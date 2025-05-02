import streamlit as st
import openai

# 🔐 Embed your OpenAI API key here
openai.api_key = "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"

st.set_page_config(page_title="Interprefy GPT", page_icon="💬", layout="centered")

# 🖼️ Optional: display your logo (upload or add file to root)
st.markdown(
    "<div style='text-align: center'><img src='https://www.interprefy.com/hubfs/interprefy-logo-white.svg' width='180'/></div>",
    unsafe_allow_html=True
)

st.markdown("## 💬 Interprefy GPT Assistant")
st.markdown("Ask anything. Powered by GPT-4. Branded by Interprefy.🧠🟠")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    role = "🧑‍💼 You" if msg["role"] == "user" else "🤖 GPT"
    st.markdown(f"**{role}**\n\n{msg['content']}\n")

# User input
user_input = st.text_area("Type your message:", height=100, placeholder="How can I help you today?")
send = st.button("Send")

# Chat logic
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        with st.spinner("GPT is thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful, clear, and professional assistant."}
                ] + st.session_state.messages
            )
            reply = response.choices[0].message["content"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.experimental_rerun()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
