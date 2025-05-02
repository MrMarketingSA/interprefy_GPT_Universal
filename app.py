
import streamlit as st
import openai
from openai import OpenAI
import os
import io
from PIL import Image
import docx2txt
import PyPDF2
import base64

# Load OpenAI API key from Streamlit secrets

st.set_page_config(page_title="Interprefy GPT-4o", layout="wide")
st.write("Loaded key:", st.secrets["OPENAI_API_KEY"][:8])  # Just for debugging
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.markdown("<h1 style='text-align: center; color: #ff5d1f;'>🧠 Interprefy GPT-4o Assistant</h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center'><img src='https://www.interprefy.com/hubfs/interprefy-logo-white.svg' width='160'/></div>", unsafe_allow_html=True)
st.markdown("### Chat with GPT-4o using text, images, or document files")

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
uploaded_files = st.sidebar.file_uploader("📎 Upload a file (PDF, DOCX, TXT, or Image)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=True)

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

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Prepare messages
messages = [{"role": "system", "content": "You are a helpful, professional assistant for Interprefy."}]
messages += st.session_state.messages

# Handle multimodal
images = [Image.open(f) for f in uploaded_files if f.type.startswith("image/")]
text_files = [extract_file_text(f) for f in uploaded_files if not f.type.startswith("image/")]

# Merge into one input for GPT-4o vision
if user_input or images or any(text_files):
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if model == "gpt-4o" and images:
                    content = [{"type": "text", "text": user_input}]
                    for img in images:
                        buffered = io.BytesIO()
                        img.save(buffered, format="PNG")
                        img_b64 = base64.b64encode(buffered.getvalue()).decode()
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_b64}"
                            }
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
                st.markdown(reply)

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
