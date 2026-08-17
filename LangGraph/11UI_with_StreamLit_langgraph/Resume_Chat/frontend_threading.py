import streamlit as st
from lg_backend_Threading import chatbot
from langchain_core.messages import HumanMessage
import uuid 

#********************************************* Utitlity Functions *************************************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id':thread_id}}).values['messages']

  
# st.session_state - > dict : this streamlit dictionary retains the state until manually tab is refresshed 


#******************************************** Session setup **************************************************
if 'message_history' not in st.session_state:
    st.session_state['message_history']= []


if 'thread_id' not in st.session_state:

    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]

add_thread(st.session_state['thread_id'])



#******************************************** Sidebar UI **************************************************

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

for thread_id in st.session_state['chat_threads']:

    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for message in messages:
            if isinstance(message,HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content':message.content})
        st.session_state['message_history'] = temp_messages

#******************************************** Main UI **************************************************


# loading the converstion history 

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


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