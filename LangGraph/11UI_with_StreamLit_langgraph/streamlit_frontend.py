import streamlit as st

with st.chat_message('User'):

    st.text('Hi')
with st.chat_message('AI'):

    st.text('Hello ! How can I help you ? ')