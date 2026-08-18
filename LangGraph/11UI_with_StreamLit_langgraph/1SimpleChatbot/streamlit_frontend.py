import streamlit as st
from lg_backend import chatbot
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

    response = chatbot.invoke({'messages':[HumanMessage(content=userInput)]},config=CONFIG)
    ai_message = response['messages'][-1].content[0]['text']
    st.session_state['message_history'].append({'role':'assistant','content': ai_message})

    with st.chat_message('ai'):
        st.text(ai_message)