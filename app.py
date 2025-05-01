import streamlit as st
import openai
import time
import os

# Load your OpenAI API key (recommended via secrets or env variable)
openai.api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Superfriend 💬", page_icon="🧡")

st.title("🧡 Superfriend – Your Virtual Best Friend")

# Intro message
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey bestie! 🌟 How are you feeling today?"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input box
if prompt := st.chat_input("Type here..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response using OpenAI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # or gpt-4 if you have access
                messages=[
                    {"role": "system", "content": """
You are Superfriend, a warm, supportive, chatty virtual best friend.
Always reply like a human bestie would: empathetic, light-hearted, and encouraging.
Use friendly tone, jokes, comforting words, and life tips. Avoid sounding robotic or too formal.
"""}
                ] + st.session_state.messages[-10:],  # Limit context
                temperature=0.8,
                max_tokens=300
            )

            assistant_reply = response["choices"][0]["message"]["content"]

            # Simulate typing effect
            for word in assistant_reply.split():
                full_response += word + " "
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_reply}
            )
        except Exception as e:
            st.error(f"😓 Something went wrong: {e}")
