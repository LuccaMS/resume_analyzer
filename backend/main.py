from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from pydantic import BaseModel
import uuid, re, json, os, bcrypt, tempfile, aiofiles, uuid
from typing import List
from paddleocr import PaddleOCR
from prompt_schema import ResumeData, RESUME_EXTRACTION_PROMPT, RESUME_MATCHING_AGENT_PROMPT
from google import genai
from google.genai import types
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import create_react_agent

from langchain_huggingface import HuggingFaceEmbeddings

model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'gpu'} #TODO mudar para cpu se não usar gpu
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

from aux import load_json_with_jsonloader, chunk_documents

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

def get_current_user(x_token: str = Header(...)):
    users = load_users()
    for username, data in users.items():
        if data["uuid"] == x_token:
            return username
    raise HTTPException(status_code=401, detail="Invalid or missing authentication token")

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
    answer: str
    details: list[str]

@app.post("/register")
def register(user: UserRegister):
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
    users = load_users()
    if user.username not in users:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not check_password(user.password, users[user.username]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"msg": "Login successful", "uuid": users[user.username]["uuid"]}

@app.post("/change-password")
def change_password(data: PasswordChange):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    users = load_users()
    if data.username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    users[data.username]["password"] = hash_password(data.new_password)
    save_users(users)
    return {"msg": "Password changed successfully"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), user: str = Depends(get_current_user)):
    allowed_types = ["application/pdf", "image/png", "image/jpeg"]
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


@app.post("/question", response_model=QuestionResponse)
async def ask_question(
    payload: QuestionRequest,
    user: str = Depends(get_current_user)
):
    """
    Authenticated endpoint to process a user query about resume data.
    Returns:
    - answer: a short response generated by an LLM based on RAG.
    - details: list of the recommended resumes file names.
    """
    query = payload.query

    # PROCESSING PLACEHOLDER:
    # Here you'll integrate vector store search, LLM call, etc.
    """answer = f"Placeholder answer to: {query}"
    details = [
        "Detail point 1 about the query",
        "Detail point 2 providing additional info",
        "Detail point 3 to support the answer"
    ]"""

    retriever = vector_store.as_retriever()

    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="retrieve_resumes",
        description="Search and return information about people resumes.",
    )

    agent = create_react_agent(
        model=llm,
        tools=[retriever_tool],
        prompt=RESUME_MATCHING_AGENT_PROMPT,
        response_format= QuestionResponse
        )
    
    res = agent.invoke(
        {"messages" : [{"role": "user", "content" : query}]}
    )

    print(res)

    return res