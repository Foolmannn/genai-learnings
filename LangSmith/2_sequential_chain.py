from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

os.environ['LANGCHAIN_PROJECT']='Sequential LLM App'

load_dotenv()

prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)

model1 = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
model2 = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


parser = StrOutputParser()

chain = prompt1 | model1 | parser | prompt2 | model2 | parser

# in this config dictionary we can add our own attributes like the tags, metadaata 
config={
    'tags':['llm app' , 'report generation','summarization'],
    'metadata':{'model': 'google flash lite', 'parser':'Stroutputparser'}
}

result = chain.invoke({'topic': 'Unemployment in Nepal'},config=config)

print(result)
