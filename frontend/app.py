import streamlit as st
import requests
import json
import os
from typing import List, Optional
import time

# Configuration
API_BASE_URL = "http://backend:8000"


# Initialize session state
if "user_uuid" not in st.session_state:
    st.session_state.user_uuid = None
if "username" not in st.session_state:
    st.session_state.username = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, files: dict = None, params: dict = None) -> dict:
    """Make API request with proper error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if st.session_state.user_uuid:
        headers["X-Token"] = st.session_state.user_uuid
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, files=files, data=data)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": response.json().get("detail", "Unknown error")}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Connection error: {str(e)}"}

def login_page():
    """Login/Registration page"""
    st.title("🔐 Resume Processing System")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Change Password"])
    
    with tab1:
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    result = make_api_request("/login", "POST", {
                        "username": username,
                        "password": password
                    })
                    
                    if result["success"]:
                        st.session_state.user_uuid = result["data"]["uuid"]
                        st.session_state.username = username
                        st.session_state.authenticated = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.header("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            submit = st.form_submit_button("Register")
            
            if submit:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        result = make_api_request("/register", "POST", {
                            "username": new_username,
                            "password": new_password
                        })
                        
                        if result["success"]:
                            st.success("Registration successful! Please login.")
                            st.info(f"Your UUID: {result['data']['uuid']}")
                        else:
                            st.error(f"Registration failed: {result['error']}")
                else:
                    st.error("Please fill in all fields")
    
    with tab3:
        st.header("Change Password")
        with st.form("change_password_form"):
            username = st.text_input("Username", key="change_username")
            new_password = st.text_input("New Password", type="password", key="change_new_password")
            confirm_password = st.text_input("Confirm New Password", type="password", key="change_confirm")
            submit = st.form_submit_button("Change Password")
            
            if submit:
                if username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        result = make_api_request("/change-password", "POST", {
                            "username": username,
                            "new_password": new_password,
                            "confirm_password": confirm_password
                        })
                        
                        if result["success"]:
                            st.success("Password changed successfully!")
                        else:
                            st.error(f"Password change failed: {result['error']}")
                else:
                    st.error("Please fill in all fields")

def upload_page():
    """File upload page"""
    st.header("📁 Upload Resume Files")
    
    st.info("Upload PDF, PNG, JPEG, or JPG files containing resumes. The system will process them using OCR and extract structured information.")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True,
        type=['pdf', 'png', 'jpg', 'jpeg']
    )
    
    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s):")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size} bytes)")
        
        if st.button("Upload and Process"):
            files = []
            for uploaded_file in uploaded_files:
                files.append(("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)))
            
            with st.spinner("Processing files... This may take a few minutes."):
                result = make_api_request("/upload", "POST", files=dict(files))
                
                if result["success"]:
                    st.success("Files uploaded and processed successfully!")
                    #st.json(result["data"])
                    
                    # Show processed files
                    if "json_files" in result["data"]:
                        st.subheader("Processed Files:")
                        for json_file in result["data"]["json_files"]:
                            st.write(f"✅ {json_file}")
                else:
                    st.error(f"Upload failed: {result['error']}")

def resumes_page():
    """Browse resumes page"""
    st.header("📋 Browse Processed Resumes")
    
    # Pagination controls
    col1, col2, col3 = st.columns(3)
    with col1:
        limit = st.number_input("Items per page", min_value=1, max_value=100, value=10)
    with col2:
        offset = st.number_input("Page offset", min_value=0, value=0)
    with col3:
        if st.button("Refresh"):
            st.rerun()
    
    # Fetch resumes
    result = make_api_request("/resumes", "GET", params={"limit": limit, "offset": offset})
    
    if result["success"]:
        data = result["data"]
        st.write(f"Total resumes: {data['total']}")
        st.write(f"Showing {len(data['resumes'])} resume(s)")
        
        # Display resumes
        for i, resume in enumerate(data["resumes"]):
            with st.expander(f"📄 {resume['filename']} - {resume['content'].get('full_name', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Basic Information")
                    st.write(f"**Name:** {resume['content'].get('full_name', 'N/A')}")
                    st.write(f"**Email:** {resume['content'].get('email', 'N/A')}")
                    st.write(f"**Phone:** {resume['content'].get('phone', 'N/A')}")
                    st.write(f"**Location:** {resume['content'].get('location', 'N/A')}")
                    
                    if resume['content'].get('linkedin'):
                        st.write(f"**LinkedIn:** {resume['content']['linkedin']}")
                    
                    if resume['content'].get('github'):
                        st.write(f"**GitHub:** {resume['content']['github']}")
                
                with col2:
                    st.subheader("Professional Summary")
                    st.write(resume['content'].get('professional_summary', 'N/A'))
                
                # Skills
                if resume['content'].get('skills'):
                    st.subheader("Skills")
                    skills = resume['content']['skills']
                    if isinstance(skills, list):
                        st.write(", ".join(skills))
                    else:
                        st.write(skills)
                
                # Experience
                if resume['content'].get('experience'):
                    st.subheader("Experience")
                    experience = resume['content']['experience']
                    if isinstance(experience, list):
                        for exp in experience:
                            if isinstance(exp, dict):
                                st.write(f"**{exp.get('position', 'N/A')}** at {exp.get('company', 'N/A')}")
                                st.write(f"Duration: {exp.get('duration', 'N/A')}")
                                if exp.get('description'):
                                    st.write(f"Description: {exp['description']}")
                            else:
                                st.write(f"- {exp}")
                    else:
                        st.write(experience)
                
                # Education
                if resume['content'].get('education'):
                    st.subheader("Education")
                    education = resume['content']['education']
                    if isinstance(education, list):
                        for edu in education:
                            if isinstance(edu, dict):
                                st.write(f"**{edu.get('degree', 'N/A')}** from {edu.get('institution', 'N/A')}")
                                if edu.get('year'):
                                    st.write(f"Year: {edu['year']}")
                            else:
                                st.write(f"- {edu}")
                    else:
                        st.write(education)
                
                base_download_url = "http://localhost:8000"
                # Download button
                download_url = f"{base_download_url}/downloads/{resume['filename']}?user_uuid={st.session_state.user_uuid}"
                st.markdown(f"[📥 Download JSON]({download_url})")
    else:
        st.error(f"Failed to load resumes: {result['error']}")

def question_page():
    """Ask questions about resumes"""
    st.header("❓ Ask Questions About Resumes")
    
    st.info("Ask questions about the processed resumes. The system will search through the resume database and provide relevant answers with references to specific files.")
    
    # Question input
    question = st.text_area(
        "Enter your question:",
        placeholder="e.g., 'Find candidates with Python experience', 'Who has worked in fintech?', 'Show me senior developers with 5+ years experience'",
        height=100
    )
    
    if st.button("Ask Question") and question:
        with st.spinner("Searching resumes and generating answer..."):
            result = make_api_request("/question", "POST", {"query": question})
            
            if result["success"]:
                data = result["data"]
                
                # Display answer
                st.subheader("Answer")
                st.markdown(data.get("answer", "No answer provided"))
                
                # Display referenced files
                if data.get("files"):
                    st.subheader("Referenced Files")
                    for file in data["files"]:
                        st.write(f"📄 {file}")
                
                # Download links
                if data.get("file_urls"):
                    st.subheader("Download Files")
                    for url in data["file_urls"]:
                        filename = url.split("/")[-1].split("?")[0]
                        st.markdown(f"[📥 Download {filename}]({url})")
                
            else:
                st.error(f"Failed to get answer: {result['error']}")

def main():
    """Main application"""
    st.set_page_config(
        page_title="Resume Processing System",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        
        if st.session_state.authenticated:
            st.success(f"Welcome, {st.session_state.username}!")
            st.write(f"UUID: {st.session_state.user_uuid[:8]}...")
            
            if st.button("Logout"):
                st.session_state.user_uuid = None
                st.session_state.username = None
                st.session_state.authenticated = False
                st.rerun()
        
    # Main content
    if not st.session_state.authenticated:
        login_page()
    else:
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📁 Upload", "📋 Browse Resumes", "❓ Ask Questions", "ℹ️ About"])
        
        with tab1:
            upload_page()
        
        with tab2:
            resumes_page()
        
        with tab3:
            question_page()
        
        with tab4:
            st.header("About Resume Processing System")
            st.markdown("""
            This system allows you to:
            
            1. **Upload Resume Files**: Upload PDF, PNG, JPEG, or JPG files containing resumes
            2. **OCR Processing**: Automatically extract text from uploaded files using OCR
            3. **Structured Data Extraction**: Convert raw text into structured JSON format
            4. **Browse Resumes**: View all processed resumes with pagination
            5. **Ask Questions**: Query the resume database using natural language
            6. **Download Results**: Download processed JSON files
            
            ### Features:
            - **Multi-format Support**: PDF and image files
            - **OCR Technology**: Powered by PaddleOCR
            - **AI Processing**: Uses Google Gemini for text extraction and matching
            - **Vector Search**: Efficient resume matching using embeddings
            - **Secure**: User authentication and UUID-based access control
            
            ### Technology Stack:
            - **Backend**: FastAPI with Python
            - **Frontend**: Streamlit
            - **OCR**: PaddleOCR
            - **AI**: Google Gemini and LangChain
            - **Vector Store**: Chroma
            - **Database**: TinyDB for logging
            """)

if __name__ == "__main__":
    main()