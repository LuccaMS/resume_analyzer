from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import json
import os
import bcrypt

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

