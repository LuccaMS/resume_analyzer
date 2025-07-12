from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from pydantic import BaseModel
import uuid
import json
import os
import bcrypt
from typing import List
import tempfile
#import shutil
import aiofiles
from paddleocr import PaddleOCR
from prompt_schema import ResumeData, RESUME_EXTRACTION_PROMPT

from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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
    json_results = []

    tmp_dir = "tmp"
    os.makedirs(tmp_dir, exist_ok=True)

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
    
    

    return {"json_files": json_results}
