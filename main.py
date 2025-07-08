import streamlit as st
import json
import hashlib
import uuid
from datetime import datetime
import os

# Configuration
USER_DATA_FILE = "users.json"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

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

def main_app():
    """Main application interface after login"""
    st.title("🎉 Welcome to the Application!")
    
    # Sidebar with user info
    with st.sidebar:
        st.write(f"**Logged in as:** {st.session_state.current_user['username']}")
        
        if st.session_state.current_user.get('created_at'):
            created_at = datetime.fromisoformat(st.session_state.current_user['created_at'])
            st.write(f"**Member since:** {created_at.strftime('%Y-%m-%d')}")
        
        st.markdown("---")
        if st.button("Logout"):
            logout()
            st.rerun()
    
    # Main content area
    st.write("This is your main application area.")
    st.write("You can add your POC features here.")
    
    # Example content
    st.subheader("User Information")
    user_info = {
        "Username": st.session_state.current_user['username'],
        "User ID": st.session_state.current_user['user_id'],
        "Member Since": datetime.fromisoformat(st.session_state.current_user['created_at']).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    for key, value in user_info.items():
        st.write(f"**{key}:** {value}")

def main():
    """Main application controller"""
    st.set_page_config(
        page_title="Auth System POC",
        page_icon="🔐",
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