import streamlit as st
import json
import hashlib
import uuid
from datetime import datetime
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import time

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
USER_DATA_FILE = "users.json"
UPLOADS_DIR = "uploads"
RESULTS_DIR = "results"
DOLPHIN_MODEL_PATH = "./hf_model"
DOLPHIN_SCRIPT = "./Dolphin/demo_page_hf.py"

# Initialize directories
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'ocr_results' not in st.session_state:
    st.session_state.ocr_results = []

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_user_id():
    """Generate unique user ID"""
    return str(uuid.uuid4())

def get_user_dirs(user_id):
    """Get user-specific directories"""
    user_upload_dir = os.path.join(UPLOADS_DIR, user_id)
    user_results_dir = os.path.join(RESULTS_DIR, user_id)
    os.makedirs(user_upload_dir, exist_ok=True)
    os.makedirs(user_results_dir, exist_ok=True)
    return user_upload_dir, user_results_dir

def register_user(username, password):
    """Register a new user"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    user_id = generate_user_id()
    users[username] = {
        'user_id': user_id,
        'password': hash_password(password),
        'created_at': datetime.now().isoformat(),
        'last_login': None
    }
    
    save_users(users)
    # Create user directories
    get_user_dirs(user_id)
    return True, "User registered successfully"

def authenticate_user(username, password):
    """Authenticate user login"""
    users = load_users()
    
    if username not in users:
        return False, "Username not found"
    
    if users[username]['password'] != hash_password(password):
        return False, "Invalid password"
    
    # Update last login
    users[username]['last_login'] = datetime.now().isoformat()
    save_users(users)
    
    # Add username to the returned user data
    user_data = users[username].copy()
    user_data['username'] = username
    
    return True, user_data

def reset_password(username, new_password):
    """Reset user password"""
    users = load_users()
    
    if username not in users:
        return False, "Username not found"
    
    users[username]['password'] = hash_password(new_password)
    users[username]['password_reset_at'] = datetime.now().isoformat()
    save_users(users)
    
    return True, "Password reset successfully"

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = 'login'
    st.session_state.ocr_results = []

def check_dolphin_setup():
    """Check if Dolphin model is properly set up"""
    return (os.path.exists(DOLPHIN_MODEL_PATH) and 
            os.path.exists(DOLPHIN_SCRIPT) and
            os.path.exists("./Dolphin"))

def run_ocr_processing(input_dir, output_dir):
    """Run Dolphin OCR processing"""
    try:
        cmd = [
            "python", DOLPHIN_SCRIPT,
            "--model_path", DOLPHIN_MODEL_PATH,
            "--input_path", input_dir,
            "--save_dir", output_dir
        ]

        logger.info(f"Command {cmd}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)

        logger.info(f"Result {result}")
        
        if result.returncode == 0:
            return True, "OCR processing completed successfully"
        else:
            return False, f"OCR processing failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "OCR processing timed out"
    except Exception as e:
        return False, f"Error running OCR: {str(e)}"

def load_ocr_results(results_dir):
    """Load OCR results from directory"""
    results = []
    if os.path.exists(results_dir):
        for file in os.listdir(results_dir):
            if file.endswith('.txt'):
                file_path = os.path.join(results_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        results.append({
                            'filename': file,
                            'content': content,
                            'timestamp': datetime.fromtimestamp(os.path.getmtime(file_path))
                        })
                except Exception as e:
                    st.error(f"Error reading {file}: {str(e)}")
    return results

def login_page():
    """Login page interface"""
    st.title("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if username and password:
                success, result = authenticate_user(username, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.current_user = result
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result)
            else:
                st.error("Please enter both username and password")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Create New Account"):
            st.session_state.page = 'register'
            st.rerun()
    
    with col2:
        if st.button("Forgot Password"):
            st.session_state.page = 'reset_password'
            st.rerun()

def register_page():
    """Registration page interface"""
    st.title("📝 Create New Account")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        register_button = st.form_submit_button("Register")
        
        if register_button:
            if not username or not password or not confirm_password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords do not match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                success, message = register_user(username, password)
                if success:
                    st.success(message)
                    st.info("You can now login with your new account")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    if st.button("← Back to Login"):
        st.session_state.page = 'login'
        st.rerun()

def reset_password_page():
    """Password reset page interface"""
    st.title("🔑 Reset Password")
    
    with st.form("reset_form"):
        username = st.text_input("Username")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        reset_button = st.form_submit_button("Reset Password")
        
        if reset_button:
            if not username or not new_password or not confirm_new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_new_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                success, message = reset_password(username, new_password)
                if success:
                    st.success(message)
                    st.info("You can now login with your new password")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    
    st.markdown("---")
    if st.button("← Back to Login"):
        st.session_state.page = 'login'
        st.rerun()

def ocr_processing_page():
    """OCR processing interface"""
    st.title("📄 Document OCR Processing")
    
    user_id = st.session_state.current_user['user_id']
    user_upload_dir, user_results_dir = get_user_dirs(user_id)
    
    # Check if Dolphin is set up
    if not check_dolphin_setup():
        st.error("❌ Dolphin OCR model is not properly set up!")
        st.info("Please ensure that:")
        st.write("1. Dolphin repository is cloned")
        st.write("2. Model weights are downloaded")
        st.write("3. Requirements are installed")
        return
    
    st.success("✅ Dolphin OCR model is ready!")
    
    # File upload section
    st.subheader("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose image files (PNG, JPG, JPEG)",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"📋 {len(uploaded_files)} files uploaded")
        
        # Save uploaded files
        saved_files = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(user_upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(file_path)
            
        st.success(f"✅ Files saved successfully!")
        
        # Process OCR button
        if st.button("🔍 Process OCR", type="primary"):
            with st.spinner("Processing OCR... This may take a few minutes..."):
                success, message = run_ocr_processing(user_upload_dir, user_results_dir)
                
                if success:
                    st.success(message)
                    st.session_state.ocr_results = load_ocr_results(user_results_dir)
                    st.rerun()
                else:
                    st.error(message)
    
    # Display results
    st.subheader("📊 OCR Results")
    results = load_ocr_results(user_results_dir)
    
    if results:
        for idx, result in enumerate(results):
            with st.expander(f"📄 {result['filename']} (Processed: {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')})"):
                st.text_area(
                    "Extracted Text:",
                    result['content'],
                    height=200,
                    key=f"result_{idx}"
                )
                
                # Download button for individual results
                st.download_button(
                    label="💾 Download Text",
                    data=result['content'],
                    file_name=f"{result['filename']}.txt",
                    mime="text/plain"
                )
    else:
        st.info("No OCR results yet. Upload some documents and process them!")

def main_app():
    """Main application interface after login"""
    st.title("🎉 OCR Document Processor")
    
    # Sidebar with user info and navigation
    with st.sidebar:
        st.write(f"**Logged in as:** {st.session_state.current_user['username']}")
        
        if st.session_state.current_user.get('created_at'):
            created_at = datetime.fromisoformat(st.session_state.current_user['created_at'])
            st.write(f"**Member since:** {created_at.strftime('%Y-%m-%d')}")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("📋 Navigation")
        if st.button("📄 OCR Processing"):
            st.session_state.app_page = 'ocr'
            st.rerun()
            
        if st.button("👤 Profile"):
            st.session_state.app_page = 'profile'
            st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            logout()
            st.rerun()
    
    # Main content based on selected page
    if 'app_page' not in st.session_state:
        st.session_state.app_page = 'ocr'
    
    if st.session_state.app_page == 'ocr':
        ocr_processing_page()
    elif st.session_state.app_page == 'profile':
        profile_page()

def profile_page():
    """User profile page"""
    st.title("👤 User Profile")
    
    user_info = {
        "Username": st.session_state.current_user['username'],
        "User ID": st.session_state.current_user['user_id'],
        "Member Since": datetime.fromisoformat(st.session_state.current_user['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    for key, value in user_info.items():
        st.write(f"**{key}:** {value}")
    
    st.subheader("📈 Usage Statistics")
    user_id = st.session_state.current_user['user_id']
    user_upload_dir, user_results_dir = get_user_dirs(user_id)
    
    # Count files
    uploaded_files = len([f for f in os.listdir(user_upload_dir) if os.path.isfile(os.path.join(user_upload_dir, f))])
    processed_files = len([f for f in os.listdir(user_results_dir) if f.endswith('.txt')])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📁 Uploaded Files", uploaded_files)
    with col2:
        st.metric("✅ Processed Files", processed_files)

def main():
    """Main application controller"""
    st.set_page_config(
        page_title="OCR Document Processor",
        page_icon="📄",
        layout="wide"
    )
    
    # Check if user is logged in
    if st.session_state.logged_in:
        main_app()
    else:
        # Show appropriate page based on session state
        if st.session_state.page == 'login':
            login_page()
        elif st.session_state.page == 'register':
            register_page()
        elif st.session_state.page == 'reset_password':
            reset_password_page()

if __name__ == "__main__":
    main()