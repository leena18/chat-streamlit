import os
import requests
import streamlit as st
from streamlit_chat import message  # For chat UI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend API Base URL
API_BASE_URL = "https://e841-2405-201-300b-71c3-80a1-ae26-5f29-adda.ngrok-free.app"

st.set_page_config(
    page_title="AI Document Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Helper Functions
def api_request(endpoint, method="GET", **kwargs):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {str(e)}")
        return None

# App Sections
st.title("📄 AI Document Assistant")

# Tabs for Navigation
tab1, tab2 = st.tabs(["File Loader", "Chat Interface"])

# Tab 1: File Loader
with tab1:
    st.header("📂 Load File and Set Roles")
    uploaded_file = st.file_uploader("Upload your document:", type=["txt", "pdf", "docx"])
    roles_input = st.text_input("Enter roles (comma-separated):")
    # print(roles_input)
    if st.button("Process File"):
        if uploaded_file and roles_input:
            with st.spinner("Processing file..."):
                files = {"file": uploaded_file}
                data = {"roles": roles_input.split(",")}
                response = api_request("/load-file/", method="POST", files=files, data=data)
                if response:
                    st.success(response["message"])
        else:
            st.warning("Please upload a file and provide roles.")

# Tab 2: Chat Interface
with tab2:
    st.header("💬 Chat with AI")
    user_id = st.text_input("Enter your User ID:", key="user_id")
    user_query = st.text_area("Your Query:")
    chat_history = st.container()

    if st.button("Send Query"):
        if user_id and user_query:
            with st.spinner("Fetching response..."):
                query_model = {"query": user_query}
                roles = [roles_input]  # Replace with actual roles for the user
                payload = {"query_model": query_model, "current_user_roles": roles, "user_id": user_id}
                response = api_request("/get-response/?user_id={user_id}", method="POST", json=payload)
                if response:
                    if "response" in response:
                        st.session_state.chat_history.append({"role": "user", "content": user_query})
                        st.session_state.chat_history.append({"role": "assistant", "content": response["response"]})
        else:
            st.warning("Please provide a User ID and a query.")

    if st.button("Clear Chat History"):
        if user_id:
            with st.spinner("Clearing chat history..."):
                response = api_request("/new-chat/?user_id={user_id}", method="POST", json={"user_id": user_id})
                if response:
                    st.success(response["message"])
                    st.session_state.chat_history = []

    # Display Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with chat_history:
        for msg in st.session_state.chat_history:
            role = msg["role"]
            content = msg["content"]
            message(content, is_user=(role == "user"))

