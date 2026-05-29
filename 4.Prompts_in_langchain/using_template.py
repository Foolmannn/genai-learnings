
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import streamlit as st
from langchain_core.prompts import load_prompt
load_dotenv()
model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')


st.header('Reasearch Tool')

paper_input = st.selectbox( "Select Research Paper Name", ["Attention Is All You Need", "BERT: Pre-training of Deep Bidirectional Transformers", "GPT-3: Language Models are Few-Shot Learners", "Diffusion Models Beat GANs on Image Synthesis"] )

style_input = st.selectbox( "Select Explanation Style", ["Beginner-Friendly", "Technical", "Code-Oriented", "Mathematical"] ) 

length_input = st.selectbox( "Select Explanation Length", ["Short (1-2 paragraphs)", "Medium (3-5 paragraphs)", "Long (detailed explanation)"] )

#Template
template = load_prompt('template.json') # now we can use the json file created and use it easily. So in langchain prompt template can be very useful 
# it is tighly coupled with the chains 



# prompt = template.invoke({
#     'paper_input':paper_input,
#     'style_input': style_input,
#     'length_input': length_input
# })

# if st.button("Summarize"):
#     result= model.invoke(prompt)
#     st.text(result.content[0]['text'])



# we can use invoke one time using the chain 
if st.button("Summarize"):
    chain = template | model
    result= chain.invoke({
        'paper_input':paper_input,
        'style_input': style_input,
        'length_input': length_input
    })
    st.text(result.content[0]['text'])