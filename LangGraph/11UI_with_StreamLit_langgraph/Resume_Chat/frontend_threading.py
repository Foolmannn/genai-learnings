import streamlit as st
from lg_backend_Threading import chatbot
from langchain_core.messages import HumanMessage
import uuid 

#********************************************* Utitlity Functions *************************************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id



  
# st.session_state - > dict : this streamlit dictionary retains the state until manually tab is refresshed 


#******************************************** Session setup **************************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history']= []


if 'thread_id' not in st.session_state:

    st.session_state['thread_id'] = generate_thread_id()

#******************************************** Sidebar UI **************************************************

st.sidebar.title('LangGraph Chatbot')

st.sidebar.button('New Chat')

st.sidebar.header('My Conversations')

st.sidebar.text(st.session_state['thread_id'])

#******************************************** Main UI **************************************************


# loading the converstion history 

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

CONFIG = {'configurable': {'thread_id':'thread-1'}}   
userInput = st.chat_input('Type Here')

if userInput:

    # first add the message to the history
    st.session_state['message_history'].append({'role':'user','content': userInput})
    with st.chat_message('user'):
        st.text(userInput)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}   
    


    # first add the ai message to the history



    with st.chat_message("assistant"):
        ai_message = st.write_stream(
            message_chunk.content[0]['text']
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=userInput)]},
                config=CONFIG ,
                stream_mode="messages"
            )
            if  message_chunk.content
        )

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })