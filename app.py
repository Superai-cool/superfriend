import streamlit as st
import openai
import fitz  # PyMuPDF
import time
import os

# Load API key
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Superfriend", page_icon="💬", layout="centered")

# --- Custom CSS for ChatGPT-style look ---
st.markdown("""
    <style>
    .block-container {
        padding: 2rem 2rem 5rem;
        max-width: 700px;
        margin: auto;
    }
    .chat-bubble {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 1rem;
        line-height: 1.6;
        max-width: 100%;
        word-wrap: break-word;
    }
    .user-bubble {
        background-color: #DCF8C6;
        text-align: right;
        align-self: flex-end;
    }
    .bot-bubble {
        background-color: #F1F0F0;
        align-self: flex-start;
    }
    .chat-wrapper {
        display: flex;
        flex-direction: column;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center;'>🧡 Superfriend – Your AI Bestie</h1>", unsafe_allow_html=True)

# --- Init session ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey bestie! 🌸 I’m here for anything you need. Just start typing or upload a PDF!"}
    ]

# --- PDF Upload ---
uploaded_file = st.file_uploader("📄 Upload a PDF for personal suggestions", type=["pdf"])
pdf_text = ""
if uploaded_file:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            pdf_text += page.get_text()
        st.success("PDF uploaded successfully! 🎉")
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

# --- Display chat history ---
for msg in st.session_state.messages:
    bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
    st.markdown(f"""
    <div class="chat-wrapper">
        <div class="chat-bubble {bubble_class}">{msg["content"]}</div>
    </div>
    """, unsafe_allow_html=True)

# --- User input ---
if prompt := st.chat_input("Talk to your Superfriend..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Typing animation container
    response_placeholder = st.empty()

    try:
        # SYSTEM MESSAGE for tone
        system_message = {
            "role": "system",
            "content": """
You are Superfriend — a warm, kind, encouraging AI best friend.
Speak casually, like a real bestie: short, cozy, clear replies.
If user uploaded a PDF, use it to offer thoughtful suggestions.
Always reply in a conversational, personal tone — emotionally intelligent, and a little playful.
""",
        }

        # Prepare message history
        messages = [system_message]
        if pdf_text:
            messages.append({"role": "user", "content": f"Here’s the uploaded PDF:\n{pdf_text[:3000]}"})
        messages += st.session_state.messages[-5:]

        # Get assistant response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=400,
        )

        reply = response["choices"][0]["message"]["content"]

        # Simulated typing animation
        full_response = ""
        for word in reply.split():
            full_response += word + " "
            response_placeholder.markdown(f"""
            <div class="chat-wrapper">
                <div class="chat-bubble bot-bubble">{full_response}▌</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.03)

        # Final message
        response_placeholder.markdown(f"""
        <div class="chat-wrapper">
            <div class="chat-bubble bot-bubble">{full_response}</div>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"Error: {e}")

