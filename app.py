import streamlit as st
import openai
import os
import time
import fitz  # PyMuPDF

# Set your API key (safest via .streamlit/secrets.toml or env)
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Superfriend 💬", page_icon="🧡")
st.title("🧡 Superfriend – Your Virtual Best Friend")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey bestie! 🌟 I'm here for you. Want to chat or upload a PDF for some advice?"}
    ]

# PDF upload
uploaded_file = st.file_uploader("📄 Upload a PDF for suggestions", type=["pdf"])
pdf_text = ""

if uploaded_file:
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            pdf_text += page.get_text()
        st.success("PDF uploaded! I'll consider it while chatting 💡")
    except Exception as e:
        st.error(f"Couldn't read the PDF: {e}")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Talk to me..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Prepare prompt
            system_message = {
                "role": "system",
                "content": """
You are Superfriend — a cheerful, caring, emotionally intelligent virtual best friend.
You offer friendly conversation, warm support, helpful advice, and fun ideas like a real bestie.
If the user uploaded a PDF, use it to give relevant, light-hearted, or helpful suggestions.
Keep replies short, chatty, and comforting. Be fun, never formal.
"""
            }

            messages = [system_message]
            if pdf_text:
                messages.append({
                    "role": "user",
                    "content": f"This is some content from the user's uploaded PDF:\n\n{pdf_text[:3000]}"
                })
            messages += st.session_state.messages[-5:]  # limit to last few for performance

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )

            assistant_reply = response["choices"][0]["message"]["content"]

            for word in assistant_reply.split():
                full_response += word + " "
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            # Save assistant reply
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"😓 Error: {e}")
