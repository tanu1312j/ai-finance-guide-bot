import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from app.agent import chat
# -----------------------------------------------------------
# Streamlit page setup
# -----------------------------------------------------------
st.set_page_config(
    page_title="AI Financial Planning Advisor",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------
# Sidebar – optional settings or info
# -----------------------------------------------------------
with st.sidebar:
    st.header(" Info")
    st.markdown("This AI advisor helps with:")
    st.markdown("1) Financial Planning Assistance\n2) Investment Guidance\n3) General Financial Education")


# -----------------------------------------------------------
# Main Title and Intro Section
# -----------------------------------------------------------
st.title("💬 AI Financial Planning Assistant")

st.markdown("""
Welcome to your **AI-powered Financial Advisor** — a smart assistant that helps you plan, save, and invest with confidence.  
You can chat naturally to explore any of the following:
""")

st.markdown("""
- 💰 **Savings Planning** – Estimate how much you can save based on your income, spending, and financial goals.  
- 🛡 **Insurance Guidance** – Understand what coverage best fits your lifestyle and risk profile.  
- 🎯 **Retirement Planning** – Project your long-term savings, income, and expenses for a comfortable retirement.  
- 📈 **Portfolio Insights** – Explore how diversified your investments are and stay updated on market conditions.  
""")

st.markdown("""
Ask me questions like:
> *"How much can I save if I invest 20% of my income?"*  
> *"What kind of insurance should I get for my family?"*  
> *"Help me plan for retirement at age 60."*  
> *"Summarize my financial profile."*
""")

st.info("💡 Tip: Type naturally — the assistant will guide you and ask for any missing details.")

# -----------------------------------------------------------
# Chat Interface
# -----------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

user_id = "user_1"

st.divider()
st.subheader("💬 Chat with Your AI Advisor")

# Display previous messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask about savings, insurance, or retirement..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat(user_id, prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
