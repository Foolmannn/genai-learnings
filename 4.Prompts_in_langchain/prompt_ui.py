from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 100)


st.header("Reasearch Toool")
user_input = st.text_input("Enter your prompt")  # this ask for the new prompt everytime as it is static prompt. 
# this is not ideal as we are giving control to user more than as needed. So we use the dynamic prompt. Where we have some part of the prompt from user and other prompt is predefined by us,

# with the predefined dynamic prompt . We can create the template which will provide better and similar result to multiple user. 



if st.button('Summarize'):
    result = model.invoke(user_input)
    st.text(result.content[0]['text'])