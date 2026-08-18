import streamlit as st
import uuid

from lg_chatbot_backend_with_db import chatbot
from langchain_core.messages import HumanMessage, AIMessage


# ============================================================
# Utility Functions
# ============================================================

def generate_thread_id():
    """Generate a unique thread ID."""
    return str(uuid.uuid4())


def add_thread(thread_id):
    """Add a thread to the thread list if it doesn't already exist."""
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    """Create a new chat thread."""
    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []

    add_thread(thread_id)


def extract_text(content):
    """
    Extract plain text from LangChain message content.

    Handles:
        1. String content
        2. List of dictionaries containing {'type': 'text', 'text': '...'}
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text = ""

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    text += item.get("text", "")

        return text

    return ""


def load_conversation(thread_id):
    """
    Load messages stored in LangGraph checkpointer.
    """

    state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    messages = state.values.get("messages", [])

    temp_messages = []
    title=""

    for message in messages:

        # Human message
        if isinstance(message, HumanMessage):
            if not title:
                title=extract_text(message.content)
            temp_messages.append({
                "role": "user",
                "content": extract_text(message.content)
            })

        # AI message
        elif isinstance(message, AIMessage):

            text = extract_text(message.content)

            if text:
                temp_messages.append({
                    "role": "assistant",
                    "content": text
                })

    return [temp_messages,title]


# ============================================================
# Session State Setup
# ============================================================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()


if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []


# Make sure current thread exists
add_thread(st.session_state["thread_id"])


# ============================================================
# Sidebar UI
# ============================================================

st.sidebar.title("LangGraph Chatbot")


# New Chat button
if st.sidebar.button("New Chat"):

    reset_chat()

    # Rerun so the UI immediately switches to the new conversation
    st.rerun()


st.sidebar.header("My Conversations")


# Display existing conversations
for thread_id in st.session_state["chat_threads"]:
    
    title = load_conversation(thread_id)[1]
    if title:
        header=title
    else:
        header=thread_id
    if st.sidebar.button(
        # thread_id,
        header,
        
        key=f"thread_{thread_id}"
    ):

        st.session_state["thread_id"] = thread_id

        st.session_state["message_history"] = load_conversation(
            thread_id
        )[0]

        st.rerun()


# ============================================================
# Main UI
# ============================================================

st.title("LangGraph Chatbot")


# ------------------------------------------------------------
# Display Conversation History
# ------------------------------------------------------------

for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):

        st.write(message["content"])


# ------------------------------------------------------------
# Chat Input
# ------------------------------------------------------------

user_input = st.chat_input("Type here...")


if user_input:

    # ========================================================
    # User Message
    # ========================================================

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)


    # ========================================================
    # LangGraph Configuration
    # ========================================================

    config = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }


    # ========================================================
    # AI Streaming Response
    # ========================================================

    with st.chat_message("assistant"):

        def generate_response():

            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=config,
                stream_mode="messages"
            ):

                # Extract text from the chunk
                text = extract_text(message_chunk.content)

                if text:
                    yield text


        ai_message = st.write_stream(
            generate_response()
        )


    # ========================================================
    # Save AI Response to Streamlit History
    # ========================================================

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })