import streamlit as st
import requests

API_URL = "http://backend:8000"

if "token" not in st.session_state:
    st.session_state["token"] = None
    st.session_state["username"] = None

# If logged in: show upload UI
if st.session_state["token"]:
    st.title("Upload Your Resume Files")
    st.write("Supported formats: PDF, PNG, JPG, JPEG")

    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True
    )

    if st.button("Submit Files") and uploaded_files:
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        res = requests.post(
            f"{API_URL}/upload",
            files=files,
            headers={"X-Token": st.session_state["token"]}
        )
        if res.status_code == 200:
            st.success("Files uploaded successfully!")
        else:
            st.error("Upload failed: " + res.json().get("detail", "Unknown error"))
else:
    st.title("🔐 Simple Login System")

    option = st.sidebar.selectbox("Select action", ["Login", "Register", "Change Password"])

    if option == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            res = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
            if res.status_code == 200:
                st.success("Logged in!")
                st.session_state["token"] = res.json()["uuid"]
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error(res.json()["detail"])

    elif option == "Register":
        st.subheader("Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Register"):
            res = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            if res.status_code == 200:
                st.success("Registered!")
                st.write(res.json())
            else:
                st.error(res.json()["detail"])

    elif option == "Change Password":
        st.subheader("Change Password")
        username = st.text_input("Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        if st.button("Change Password"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                res = requests.post(
                    f"{API_URL}/change-password",
                    json={"username": username, "new_password": new_password, "confirm_password": confirm_password}
                )
                if res.status_code == 200:
                    st.success("Password changed!")
                else:
                    st.error(res.json()["detail"])

