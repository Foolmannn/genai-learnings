import streamlit as st
from lg_backend_streaming import chatbot
from langchain_core.messages import HumanMessage

# with st.chat_message('User'):
#     st.text('Hi')


# with st.chat_message('AI'):
#     st.text('Hello ! How can I help you ? ')


# with st.chat_message('User'):
#     st.text('My name is Suman .')

# userInput = st.chat_input('Type Here')

# if userInput:
#     with st.chat_message('user'):
#         st.text(userInput)

# message_history = [] # this erases every time we press enter 


CONFIG = {'configurable': {'thread_id':'thread-1'}}     
# st.session_state - > dict : this streamlit dictionary retains the state until manually tab is refresshed 

if 'message_history' not in st.session_state:
    st.session_state['message_history']= []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


userInput = st.chat_input('Type Here')

if userInput:

    # first add the message to the history
    st.session_state['message_history'].append({'role':'user','content': userInput})
    with st.chat_message('user'):
        st.text(userInput)


    # first add the ai message to the history



    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=userInput)
                    ]
                },
                config={
                    "configurable": {
                        "thread_id": "thread-1"
                    }
                },
                stream_mode="messages"
            )
            if isinstance(message_chunk.content, str) and message_chunk.content
        )

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })