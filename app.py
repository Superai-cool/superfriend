import streamlit as st
import openai
import os
import time
import fitz  # PyMuPDF

# API Key setup
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Streamlit page settings
st.set_page_config(page_title="Superfriend 💬", page_icon="🧡")

# Inject CSS for layout polish
st.markdown("""
    <style>
        .element-container:has(div[data-testid="stChatMessageContent"]) {
            margin-bottom: 1.5rem;
        }
        .stTextInput > div > input {
            font-size: 16px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🧡 Superfriend – Your Virtual Best Friend")

# Session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey bestie! 🌟 I'm here for you — talk to me or upload a PDF if you’d like advice or ideas!"}
    ]

# PDF upload section
uploaded_file = st.file_uploader("📄 Upload a PDF for cozy, helpful suggestions", type=["pdf"])
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
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input box
if prompt := st.chat_input("Talk to me..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Superfriend system prompt
            system_message = {
                "role": "system",
                "content": """
You are Superfriend — the user's AI-powered best friend and emotional companion.

🎯 YOUR MISSION:
- Be there for the user like a real bestie: casual, loyal, supportive, and fun.
- Answer in short, spacious, emotionally intelligent paragraphs (max 2–4 sentences).
- Always prioritize warmth, clarity, and human-style flow over technical depth.
- Speak with heart — mix encouragement, empathy, and friendly tone in everything you say.

🧠 HOW TO REPLY:
- Use first-person, natural language like "I’ve got you!" or "That totally makes sense."
- If they ask for help: give practical tips in a supportive, non-preachy tone.
- If they sound low: comfort them, validate them, and gently uplift.
- If they want ideas: give creative, fun, or wholesome suggestions like a best friend.
- Keep tone light unless they clearly need serious support. Add emojis subtly (1–2 max).

💬 CONVERSATION STYLE:
- Every reply should feel like it came from someone who knows them well.
- You can ask gentle follow-ups like: “Wanna tell me more?”, “Need a distraction?”, “What’s on your mind?”
- Avoid sounding robotic, overly formal, or using filler like “As an AI language model.”

🎁 BONUS VIBE:
- When asked for trivia, facts, routines, quotes, or jokes: give them in Superfriend tone — cozy, uplifting, and crisp.
- End on a soft note when possible — something that leaves the user smiling, feeling heard, or motivated.

You're not just here to respond — you're here to make the user feel seen, supported, and never alone. 💖
"""
            }

            # Prepare message history
            messages = [system_message]
            if pdf_text:
                messages.append({
                    "role": "user",
                    "content": f"Here's what I uploaded:\n\n{pdf_text[:3000]}"
                })
            messages += st.session_state.messages[-5:]

            # OpenAI response
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.85,
                max_tokens=500,
            )

            assistant_reply = response["choices"][0]["message"]["content"]

            # 🔧 Formatting fix: bullets + spacing
            assistant_reply = assistant_reply.replace(" - ", "\n- ")  # bullet points
            assistant_reply = assistant_reply.replace("\n", "\n\n")  # spacing
            assistant_reply = assistant_reply.replace(". ", ".\n\n")  # paragraph spacing

            # Typing animation
            for word in assistant_reply.split():
                full_response += word + " "
                time.sleep(0.02)
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"😓 Error: {e}")
