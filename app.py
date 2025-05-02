
import streamlit as st
import openai
from openai import OpenAI
import os
import io
from PIL import Image
import docx2txt
import PyPDF2
import base64

# Load API Key securely
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Custom CSS for dark, modern theme ---
st.set_page_config(page_title="Interprefy GPT-4o", layout="wide")
st.markdown("""
    <style>
    body, .stApp {
        background-color: #0e0e0e;
        color: #f0f0f0;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #ff5d1f;
    }
    .stChatMessage {
        background-color: #1a1a1a;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .user {
        background-color: #222;
        color: #fff;
        border-left: 4px solid #ff5d1f;
    }
    .assistant {
        background-color: #1c1c1c;
        color: #eee;
        border-left: 4px solid #4c9aff;
    }
    .stButton>button {
        background-color: #ff5d1f;
        color: white;
        border-radius: 20px;
        padding: 8px 16px;
        border: none;
    }
    .stTextInput>div>div>input {
        background-color: #1e1e1e;
        color: #fff;
        border-radius: 10px;
    }
    .stFileUploader {
        color: #ddd;
    }
    footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 style='text-align: center;'>🤖 Interprefy GPT-4o Assistant</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center;'><img src='https://www.interprefy.com/hubfs/interprefy-logo-white.svg' width='160'/></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ccc;'>Chat, upload, and interact with GPT-4o in your own branded experience</p>", unsafe_allow_html=True)

# Sidebar config
st.sidebar.header("⚙️ Settings")
model = st.sidebar.selectbox("Choose a model", ["gpt-4o", "gpt-4", "gpt-3.5-turbo"])
clear_chat = st.sidebar.button("🧹 Clear chat history")

# Session memory
if clear_chat:
    st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Upload files
uploaded_files = st.sidebar.file_uploader("📎 Upload a file", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=True)

# Extract file content
def extract_file_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return docx2txt.process(file)
    elif file.type.startswith("text/"):
        return file.read().decode()
    return None

# Input
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        bubble_style = "user" if msg["role"] == "user" else "assistant"
        st.markdown(f"<div class='{bubble_style}'>{msg['content']}</div>", unsafe_allow_html=True)

# Collect context for GPT
messages = [{"role": "system", "content": "You are Interprefy's helpful and professional virtual assistant."}]
messages += st.session_state.messages

images = [Image.open(f) for f in uploaded_files if f.type.startswith("image/")]
text_files = [extract_file_text(f) for f in uploaded_files if not f.type.startswith("image/")]

# Process response
if user_input or images or any(text_files):
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if model == "gpt-4o" and images:
                    content = [{"type": "text", "text": user_input}]
                    for img in images:
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        b64 = base64.b64encode(buf.getvalue()).decode()
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        })
                    response = client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": content}]
                    )
                else:
                    text_input = user_input
                    if any(text_files):
                        text_input += "\n\n" + "\n".join(text_files)
                    messages.append({"role": "user", "content": text_input})
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages
                    )

                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(f"<div class='assistant'>{reply}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
