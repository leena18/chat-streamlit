import streamlit as st
import requests
from streamlit_chat import message as st_message  # Rename to avoid conflict with 'message'

# Backend URL
BASE_URL = "https://e841-2405-201-300b-71c3-80a1-ae26-5f29-adda.ngrok-free.app"  # Replace with your FastAPI backend URL if different

# Constants
ROLE = "HR"
USER_ID = "1"

def get_ai_response(user_query):
    """
    Sends a user query to the backend and fetches the AI's response.
    """
    query_model = {"query": user_query}

    try:
        response = requests.post(
            f"{BASE_URL}/get-response/?user_id={USER_ID}",
            json={
                "query_model": query_model,
                "current_user_roles": [ROLE],
                "user_id": USER_ID,
            },
        )
        response_data = response.json()
        return response_data.get("response", "No response from the server.")
    except Exception as e:
        return f"Error communicating with the server: {e}"

def clear_chat_history():
    """
    Sends a request to clear chat history for the user.
    """
    try:
        response = requests.post(f"{BASE_URL}/new-chat/?user_id={USER_ID}", json={"user_id": USER_ID})
        response_data = response.json()
        st.session_state.chat_history = []
        return response_data.get("message", "Error clearing history.")
    except Exception as e:
        return f"Error communicating with the server: {e}"

import uuid

# Display Chat History
def display_chat():
    """
    Displays the chat history dynamically in the app.
    """
    chat_placeholder.empty()  # Clear the placeholder
    with chat_placeholder.container():
        for idx, chat in enumerate(st.session_state.chat_history):
            # Use role, idx, and a UUID for a unique key
            unique_key = f"{chat['role']}_{idx}_{uuid.uuid4()}"
            
            # Display user message
            if chat["role"] == "user":
                st_message(chat["content"], is_user=True, key=unique_key)
            # Display assistant message
            else:
                st_message(chat["content"], is_user=False, key=unique_key)


# Streamlit UI setup
st.set_page_config(page_title="Chat Assistant")
st.markdown("<h1 style='text-align: center;'>HR Chat Assistant</h1>", unsafe_allow_html=True)

# Sidebar for options
with st.sidebar:
    st.header("Options")
    if st.button("Clear Chat History"):
        clear_message = clear_chat_history()
        st.success(clear_message)

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Placeholder for chat interface
chat_placeholder = st.empty()

# Display chat messages
display_chat()

# Divider to separate chat interface and input field
st.divider()

# Chat Input and Send Button
with st.container():
    user_input = st.text_input("Type your message here:", key="user_input", placeholder="Ask anything...")
    send_clicked = st.button("Send", key="send_button")

# Process the message when the "Send" button is clicked
if send_clicked and user_input.strip():
    # Add user input to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get AI response
    ai_response = get_ai_response(user_input)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

    # Refresh chat interface
    display_chat()

