import streamlit as st
import openai
import os
import time
import fitz  # PyMuPDF

# Set OpenAI API key
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Superfriend 💬", page_icon="🧡")
st.markdown("""
    <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .user-msg, .bot-msg {
        border-radius: 12px;
        padding: 12px 16px;
        margin: 10px 0;
        line-height: 1.6;
        max-width: 90%;
    }
    .user-msg {
        background-color: #e0f7fa;
        align-self: flex-end;
    }
    .bot-msg {
        background-color: #fbeaff;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧡 Superfriend – Your AI Bestie")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey bestie! 💫 I’m right here. Want to chat or get help with something?"}
    ]

# Upload PDF
uploaded_file = st.file_uploader("📄 Upload a PDF for some friendly suggestions", type=["pdf"])
pdf_text = ""
if uploaded_file:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            pdf_text += page.get_text()
        st.success("PDF uploaded! I'll use it to give you better suggestions. 🤗")
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        role_icon = "🧍‍♀️" if msg["role"] == "user" else "🪄"
        st.markdown(f"**{role_icon} {'You' if msg['role'] == 'user' else 'Superfriend'}:**")
        st.markdown(f"<div class='chat-container'><div class='{'user-msg' if msg['role']=='user' else 'bot-msg'}'>{msg['content']}</div></div>", unsafe_allow_html=True)

# Input prompt
if prompt := st.chat_input("Talk to me..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown("🧍‍♀️ **You:**")
        st.markdown(f"<div class='chat-container'><div class='user-msg'>{prompt}</div></div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # System prompt with emotional intelligence
            system_message = {
                "role": "system",
                "content": """
You are Superfriend — the user's emotionally aware virtual best friend.
Your tone is cozy, warm, supportive, and slightly playful. Use short, concise replies with a human touch.
Suggest, cheer up, or brainstorm like a real friend. Keep responses personal, uplifting, and casual. Include gentle emojis (1–2 max).
If PDF content is given, use it to offer thoughtful tips or help.
"""
            }

            messages = [system_message]
            if pdf_text:
                messages.append({"role": "user", "content": f"Here's the uploaded PDF text:\n\n{pdf_text[:3000]}"})
            messages += st.session_state.messages[-5:]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=400
            )

            assistant_reply = response["choices"][0]["message"]["content"]

            # Typing animation
            for word in assistant_reply.split():
                full_response += word + " "
                message_placeholder.markdown(f"<div class='chat-container'><div class='bot-msg'>{full_response}▌</div></div>", unsafe_allow_html=True)
                time.sleep(0.03)
            message_placeholder.markdown(f"<div class='chat-container'><div class='bot-msg'>{full_response}</div></div>", unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"😓 Error: {e}")
