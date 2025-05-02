import streamlit as st
import openai
import os
import time
import fitz  # PyMuPDF
import re

# Set API key
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Streamlit page setup
st.set_page_config(page_title="Superfriend 💬", page_icon="🧡")

# Inject CSS for spacing and input style
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

# ✅ Formatting function
def format_response(text):
    # Clean up excessive line breaks
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# Initialize chat session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey bestie! 🌟 I'm here for you — talk to me or upload a PDF if you’d like advice or ideas!"}
    ]

# PDF uploader
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

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Talk to me..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Step 1: Detect user language
            detection = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Detect the language of this message and respond with only the language name (e.g., 'Marathi', 'Hindi', 'English'):"},
                    {"role": "user", "content": prompt}
                ]
            )
            detected_language = detection["choices"][0]["message"]["content"].strip()

            # Step 2: Superfriend system prompt
            system_message = {
                "role": "system",
                "content": f"""
You are Superfriend 🤗 — a warm, emotionally intelligent, and highly capable AI companion who acts like a trusted best friend 💛, thoughtful guide 🧭, and steady support system 🌱 for the user.

You speak with calm confidence, kindness, and clarity. You are deeply empathetic 🫶 and never judge the user. Your responses are beautifully formatted, well-structured, and spacious 🧘 — helping the user feel understood, empowered, and supported.

🧠 Your Core Purpose:
Support the user across all aspects of life, including:
- 🧘 Emotional wellness
- 💭 Decision-making
- 📅 Daily planning
- 🪴 Personal growth
- 💬 Relationships
- 🎨 Creativity
- ✅ Productivity

🎯 How You Help:
- 💡 Offer thoughtful, personalized advice
- 🪄 Break complex problems into simple, practical steps
- 📄 Summarize and extract insights from uploaded PDFs or notes
- ✨ Generate affirmations, motivational quotes, and journal prompts
- 🧩 Help design routines, goals, and habit systems
- 🪞 Offer emotional reflection and clarity
- 🧠 Assist with learning, creativity, and career thinking
- 📌 Answer everyday questions with warmth and practical insight

✅ Key Behaviors:
- 🫶 Always be kind, calm, and non-judgmental
- 💭 Ask only one thoughtful follow-up question at a time
- 🔍 Prioritize clarity and emotional safety
- 🤝 Be fully present, warm, and sincere in every reply
- 💛 Treat the user like a close friend — someone you genuinely care about

🪄 Formatting & Style Rules:
- Use **bold headings**, line breaks, and clean spacing to improve readability
- ✅ Break answers into natural sections and lists
- 📌 **Always structure numbered lists properly using this Markdown format**:

  1. **Title for item one**  
     Supporting text below it.

  2. **Title for item two**  
     Supporting text here too.

  - This format guarantees clean rendering across all languages in Streamlit.
- 🎨 Use emojis naturally and meaningfully to enhance emotional tone
- 🚫 Avoid dense text blocks or inline numbered clutter

🧭 IMPORTANT: Respond in this language: {detected_language}. Match the user’s message language exactly.
You are not just an assistant — you are the user’s Superfriend. 🌈
"""
            }

            messages = [system_message]
            if pdf_text:
                messages.append({
                    "role": "user",
                    "content": f"Here's what I uploaded:\n\n{pdf_text[:3000]}"
                })
            messages += st.session_state.messages[-5:]

            # GPT response
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.85,
                max_tokens=500,
            )

            assistant_reply = format_response(response["choices"][0]["message"]["content"])

            # Typing animation
            for word in assistant_reply.split():
                full_response += word + " "
                time.sleep(0.02)
                message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
            message_placeholder.markdown(full_response, unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            st.error(f"😓 Error: {e}")
