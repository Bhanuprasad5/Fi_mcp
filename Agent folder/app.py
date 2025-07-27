import asyncio

import streamlit as st
from my_agent.agent import root_agent

st.set_page_config(page_title="Personal Finance Agent", layout="centered")
st.title("💸 Personal Finance Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about your money...")

if user_input:
    # Show user input
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Run agent and stream response
    async def get_agent_response(query):
        response = ""
        async for chunk in root_agent.run_async(query):
            response += chunk
        return response

    response = asyncio.run(get_agent_response(user_input))

    # Show and store agent's response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
