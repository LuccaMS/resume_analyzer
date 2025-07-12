from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends, Query
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
import uuid, re, json, os, bcrypt, tempfile, aiofiles
from typing import List
from paddleocr import PaddleOCR
from prompt_schema import ResumeData, RESUME_EXTRACTION_PROMPT, RESUME_MATCHING_AGENT_PROMPT
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langgraph.prebuilt import create_react_agent
from langchain_huggingface import HuggingFaceEmbeddings
from tinydb import TinyDB
from datetime import datetime, timezone
from tool import RetrieveResumesTool
import ast

db = TinyDB('question_logs.json')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
USE_CUDA = ast.literal_eval(os.getenv("USE_CUDA", "False"))

print("GEMINI_API_KEY: ", GEMINI_API_KEY)
print("USE_CUDA: ", USE_CUDA)

model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cuda' if USE_CUDA else 'cpu'}

encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

from aux import load_json_with_jsonloader, chunk_documents

llm  = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)

vector_store = Chroma(
    collection_name="rag_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

app = FastAPI()
USER_FILE = "users.json"

# Ensure file exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

#Função usada para verificar se existe algum usuário com o UUID.
#Ele pode ser fornecido pelo header ou pelo query param, tornando simples a integração com o swagger ui ou outras ferramentas de teste de API.
def verify_uuid(
    x_token: str = Header(default=None),
    x_token_query: str = Query(default=None, alias="user_uuid")  # optional alias
):
    token = x_token or x_token_query  # prioritize header, fallback to query param

    if token is None:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    users = load_users()
    for username, data in users.items():
        if data["uuid"] == token:
            return token

    raise HTTPException(status_code=401, detail="Invalid authentication token")

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    username: str
    new_password: str
    confirm_password: str

class QuestionRequest(BaseModel):
    query: str

class QuestionResponse(BaseModel):
    answer: str = Field(description="Your answer to the question about the best fitting resumes and justifications, markdown format")
    files: list[str] = Field(description="List of the file names that were used to answer the question")

class ResumeMetadata(BaseModel):
    filename: str
    content: dict

class ResumePage(BaseModel):
    total: int
    resumes: list[ResumeMetadata]

@app.post("/register")
def register(user: UserRegister):
    """
    Registers a new user.

    Args:
        user (UserRegister): The user registration data containing username and password.

    Raises:
        HTTPException: If the username already exists.

    Returns:
        dict: A message indicating successful registration and the user's UUID.
    """
    users = load_users()
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    users[user.username] = {
        "password": hash_password(user.password),
        "uuid": str(uuid.uuid4())
    }
    save_users(users)
    return {"msg": "User registered", "uuid": users[user.username]["uuid"]}

@app.post("/login")
def login(user: UserLogin):
    """
    Handles user login by verifying provided credentials.

    Args:
        user (UserLogin): The login credentials provided by the user.

    Returns:
        dict: A dictionary containing a success message and the user's UUID if authentication is successful.

    Raises:
        HTTPException: If the username does not exist or the password is incorrect, raises a 401 Unauthorized error.
    """
    users = load_users()
    if user.username not in users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not check_password(user.password, users[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"msg": "Login successful", "uuid": users[user.username]["uuid"]}

@app.post("/change-password")
def change_password(data: PasswordChange):
    """
    Endpoint to change a user's password.

    Args:
        data (PasswordChange): An object containing the username, new password, and password confirmation.
    Raises:
        HTTPException: 
            - 400 if the new password and confirmation do not match.
            - 404 if the specified user is not found.
    Returns:
        dict: A message indicating the password was changed successfully.
    """
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    users = load_users()
    if data.username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    users[data.username]["password"] = hash_password(data.new_password)
    save_users(users)
    return {"msg": "Password changed successfully"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), user_uuid: str = Depends(verify_uuid)):
    """
    Endpoint to upload and process resume files.
    Accepts multiple files (PDF, PNG, JPEG, JPG), performs OCR extraction, processes the extracted text with a language model to generate structured JSON outputs, and stores the results. The processed documents are also chunked and added to a vector store for further use.
    Args:
        files (List[UploadFile]): List of files to be uploaded and processed.
        user_uuid (str): User UUID, validated via dependency injection.
    Returns:
        dict: A dictionary containing the list of paths to the created JSON files.
    Raises:
        HTTPException: If an unsupported file type is uploaded.
    Workflow:
        1. Validates file types and saves them temporarily.
        2. Runs OCR on each file and saves the OCR output as JSON.
        3. Extracts recognized texts from OCR outputs.
        4. Uses a language model to generate structured resume data from OCR text.
        5. Saves structured data as JSON files with sanitized filenames.
        6. Loads each JSON, chunks the document, and adds chunks to a vector store.
        7. Returns the list of created JSON file paths.
    """
    allowed_types = ["application/pdf", "image/png", "image/jpeg", "image/jpg"]
    saved_paths = []

    tmp_dir = "tmp"
    output_dir = "resumes_processed" #folder where the resumes structured output will be saved.

    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        suffix = "." + file.filename.split(".")[-1]
        tmp_filename = next(tempfile._get_candidate_names()) + suffix
        tmp_path = os.path.join(tmp_dir, tmp_filename)

        async with aiofiles.open(tmp_path, "wb") as out_file:
            while content := await file.read(1024):  # Read in chunks
                await out_file.write(content)

        saved_paths.append(tmp_path)

    for file in saved_paths:
        result = ocr.predict(input=file)

        for res in result:
            res.save_to_json(tmp_dir)
        
        os.remove(file) #limpando o arquivo da memória após processar com OCR
    
    ocrs_to_process = os.listdir(tmp_dir)
    rec_texts = []  #este são os textos extraídos do OCR, o que vamos usar para obter o structured output

    for path in ocrs_to_process:
        file_to_open = f"{tmp_dir}/{path}"
        with open(file_to_open) as file:
            file_data = json.load(file)
            rec_texts.append(file_data.get("rec_texts"))
        
        os.remove(file_to_open) #cleaning the OCR json
    
    created_jsons = [] #list that holds the path of each json created for the execution right now
    
    for item in rec_texts:
        prompt = RESUME_EXTRACTION_PROMPT.format(ocr_data=item)

        client = genai.Client(api_key=GEMINI_API_KEY)

        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": ResumeData,
        })

        res = json.loads(response.text)

        if res["full_name"] is not None:
            # Convert to lowercase
            file_name = res["full_name"].lower()
            # Remove spaces
            file_name = file_name.replace(" ", "")
            # Remove special characters using regex (keeps only alphanumeric characters)
            file_name = re.sub(r'[^a-z0-9]', '', file_name)
        else:
            file_name = str(uuid.uuid4())

        path_file = f"{output_dir}/{file_name}.json"

        with open(path_file, "w") as json_file:
            json.dump(res,json_file,indent=4)
            created_jsons.append(path_file)
    
    for file in created_jsons:
        document = load_json_with_jsonloader(file)

        doc_chunks = chunk_documents(documents=document, chunk_size=150, chunk_overlap=25) #small docs

        uuids = [str(uuid.uuid4()) for _ in range(len(doc_chunks))]

        vector_store.add_documents(documents=doc_chunks, ids=uuids)

    return {"json_files": created_jsons}

@app.get("/resumes", response_model=ResumePage)
async def list_resumes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_uuid: str = Depends(verify_uuid)
):
    """
    Endpoint to list processed resumes with pagination.

    Args:
        limit (int): Maximum number of resumes to return (default: 10, min: 1, max: 100).
        offset (int): Number of resumes to skip before starting to collect the result set (default: 0, min: 0).
        user_uuid (str): User UUID, validated by dependency injection.

    Returns:
        ResumePage: An object containing the total number of resumes and a list of ResumeMetadata objects for the current page.

    Raises:
        HTTPException: If the directory does not exist or files cannot be read.

    Notes:
        - Only files ending with ".json" in the "resumes_processed" directory are considered.
        - Pagination is applied based on the provided limit and offset.
    """
    # List files in the processed directory
    dir_path = "resumes_processed"
    all_files = sorted(f for f in os.listdir(dir_path) if f.endswith(".json"))
    total = len(all_files)

    # Apply pagination
    page_files = all_files[offset : offset + limit]

    resumes = []
    for fname in page_files:
        path = os.path.join(dir_path, fname)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        resumes.append(ResumeMetadata(filename=fname, content=data))

    return ResumePage(total=total, resumes=resumes)

@app.post("/question")
async def ask_question(
    payload: QuestionRequest,
    user_uuid: str = Depends(verify_uuid)
):
    """
    Args:
        payload (QuestionRequest): The request body containing the user's query.
        user_uuid (str): The unique identifier for the user, validated via dependency injection.
    Process:
        - Extracts the query from the payload.
        - Initializes a retriever from the vector store.
        - Sets up a retrieval tool and a reactive agent with the specified prompt and response format.
        - Invokes the agent with the user's query and obtains a structured response.
        - Logs the request and response details into TinyDB for auditing or analytics.
        - Constructs file download URLs for any files referenced in the response.
    Returns:
        dict: The structured response from the agent, including file download URLs.
    """
    query = payload.query

    retriever = vector_store.as_retriever()

    retriever_tool = RetrieveResumesTool(retriever=retriever)

    agent = create_react_agent(
        model=llm,
        tools=[retriever_tool],
        prompt=RESUME_MATCHING_AGENT_PROMPT,
        response_format= QuestionResponse
        )
    
    res = agent.invoke(
        {"messages" : [{"role": "user", "content" : query}]}
    )

    resp_struct = res["structured_response"]

    # Prepare log record
    record = {
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_uuid": user_uuid,
        "query": query,
        "response": resp_struct.model_dump()
    }

    # Insert into TinyDB
    db.insert(record)

    base_url = "http://localhost:8000"

    resp = {
    **resp_struct.model_dump(),
    "file_urls": [f"{base_url}/downloads/{f}?user_uuid={user_uuid}" for f in resp_struct.files]
    }

    return resp

@app.get("/downloads/{filename}")
async def download_file(
    filename: str,
    user_uuid: str = Depends(verify_uuid)
):
    """
    Endpoint to download a processed resume file.
    Args:
        filename (str): The name of the file to download, provided as a path parameter.
        user_uuid (str): The user's UUID, validated via dependency injection.
    Raises:
        HTTPException: If the specified file does not exist, returns a 404 error.
    Returns:
        FileResponse: The requested file as a JSON response with appropriate headers.
    """

    file_path = os.path.join("resumes_processed", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/json"
    )