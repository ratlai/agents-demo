import streamlit as st
from agent import delegate_task
import logging
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define avatars for agents
agent_avatars = {
    "USER": "image/user.png",
    "Bujji": "image/ratl.png"
}

# Streamlit interface
st.set_page_config(page_title="Conversational App", page_icon="🤖")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    avatar = agent_avatars.get(message["agent"], "👤")
    
    with st.chat_message(message["agent"], avatar=avatar):
        if "```" in message["response"]:
            st.markdown(message["response"])  # Display as Markdown if the response contains code
        else:
            st.write(message["response"])

# User-provided prompt
if prompt := st.chat_input("Send a message to Bujji"):
    # Append user message to session state
    st.session_state.messages.append({"agent": "USER", "response": prompt})
    with st.chat_message("USER", avatar="image/user.png"):
        st.write(prompt)

    # Log user input
    logger.info(f"User input: {prompt}")

    # Generate and display response
    response = delegate_task(prompt)

    # Log API response
    logger.info(f"API response: {response}")

    # Display response from Bujji
    st.session_state.messages.append({"agent": "Bujji", "response": response})
    avatar = agent_avatars.get("Bujji", "👤")
    with st.chat_message("Bujji", avatar=avatar):
        if "```" in response:
            st.markdown(response)  # Display as Markdown if the response contains code
        else:
            st.write(response)