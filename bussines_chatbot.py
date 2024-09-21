import streamlit as st
import requests
import time
import hashlib
import logging

# ==========================
# Logging Configuration
# ==========================
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# ==========================
# User Authentication Setup
# ==========================

users = {
    "Moin": hashlib.sha256("user1".encode()).hexdigest(),
    "user2": hashlib.sha256("password2".encode()).hexdigest(),
    # Add more users as needed
}

def verify_password(username, password):
    """Verify a user's password."""
    if username in users:
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        return users[username] == hashed_input
    return False

# ==========================
# BusinessChatbot Class
# ==========================

class BusinessChatbot:
    def __init__(self):
        # Retrieve the API key from Streamlit Secrets
        try:
            self.api_key = st.secrets["NVIDIA_API_KEY"]
        except KeyError:
            logger.error("NVIDIA_API_KEY not found in Streamlit secrets.")
            st.error("Server configuration error. Please contact the administrator.")
            st.stop()
        
        self.base_url = "https://integrate.api.nvidia.com/v1"

    def get_response(self, prompt, max_tokens=200):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "nvidia/mistral-nemo-minitron-8b-base",
            "prompt": prompt,
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": max_tokens,
            "stream": False
        }
        try:
            response = requests.post(f"{self.base_url}/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return "An error occurred while processing your request. Please try again later."

    def answer_business_question(self, question):
        prompt = f"""You are a professional business assistant. Please provide a helpful and insightful answer to the following business-related question:

Question: {question}

Answer:"""
        return self.get_response(prompt, max_tokens=300)

    def brainstorm_ideas(self, topic):
        prompt = f"""You are a creative business strategist. Please brainstorm innovative ideas related to the following business topic:

Topic: {topic}

Ideas:"""
        return self.get_response(prompt, max_tokens=400)

# ==========================
# UI Styling
# ==========================

def set_dark_mode_style():
    st.markdown("""
    <style>
    /* Dark mode theme */
    body {
        color: #E0E0E0;
        background-color: #1E1E1E;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    .css-1d391kg {
        background-color: #2D2D2D;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .stTextInput>div>div>input {
        background-color: #3D3D3D;
        color: #E0E0E0;
        border: 1px solid #555;
        border-radius: 5px;
    }
    .stTextArea>div>div>textarea {
        background-color: #3D3D3D;
        color: #E0E0E0;
        border: 1px solid #555;
        border-radius: 5px;
    }
    .stTab {
        background-color: #2D2D2D;
        color: #E0E0E0;
    }
    .stTab[aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .stMarkdown {
        color: #E0E0E0;
    }
    .st-emotion-cache-16fyc3s {
        background-color: #2D2D2D;
    }
    .st-emotion-cache-16fyc3s p {
        color: #E0E0E0;
    }
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-track {
        background: #1E1E1E;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================
# Main Application
# ==========================

def main():
    st.set_page_config(page_title="Business AI Assistant", layout="wide")
    set_dark_mode_style()
    
    st.title("💼 Professional Business AI Assistant")

    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # ==========================
    # Login Form
    # ==========================
    if not st.session_state.logged_in:
        st.header("🔒 Please Log In")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
        
        if submit:
            if verify_password(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                # Optionally, clear the login form
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    else:
        # ==========================
        # Logout Button
        # ==========================
        st.sidebar.header(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            # Clear session state
            st.session_state.logged_in = False
            st.session_state.username = ''
            st.session_state.chat_history = []
            st.experimental_rerun()
        
        # ==========================
        # Initialize the Chatbot
        # ==========================
        chatbot = BusinessChatbot()
        
        # ==========================
        # Chatbot Tabs
        # ==========================
        tab1, tab2 = st.tabs(["💬 Business Q&A", "💡 Idea Brainstorming"])
        
        with tab1:
            st.header("Ask a Business Question")
            question = st.text_area("Enter your business-related question:", height=150)
            get_answer = st.button("Get Answer")
            if get_answer:
                if question.strip() == "":
                    st.error("Please enter a valid question.")
                else:
                    with st.spinner("Thinking..."):
                        answer = chatbot.answer_business_question(question)
                        st.success("Here's your answer:")
                        st.write(answer)
        
        with tab2:
            st.header("Business Idea Brainstorming")
            topic = st.text_input("Enter a business topic for brainstorming:")
            generate_ideas = st.button("Generate Ideas")
            if generate_ideas:
                if topic.strip() == "":
                    st.error("Please enter a valid topic.")
                else:
                    with st.spinner("Brainstorming..."):
                        ideas = chatbot.brainstorm_ideas(topic)
                        st.success("Here are some innovative ideas:")
                        st.write(ideas)
        
        # ==========================
        # Chat Interface
        # ==========================
        st.header("💬 Chat with Business AI")
        
        for i, (role, content) in enumerate(st.session_state.chat_history):
            with st.chat_message(role):
                st.write(content)
        
        user_input = st.chat_input("Ask me anything about business:")
        if user_input:
            st.session_state.chat_history.append(("user", user_input))
            with st.chat_message("user"):
                st.write(user_input)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chatbot.answer_business_question(user_input)
                    st.write(response)
            st.session_state.chat_history.append(("assistant", response))

# ==========================
# Run the App
# ==========================

if __name__ == "__main__":
    main()
