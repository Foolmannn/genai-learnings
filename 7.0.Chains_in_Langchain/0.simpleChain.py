from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser


load_dotenv()


prompt = PromptTemplate(
    template='Generate 5 interesting facts about {topic}',
    input_variables=['topic']
)
# model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1",
    task="text-generation",
    temperature=0.7, 
    max_new_tokens=512 
)

model = ChatHuggingFace(llm=llm)

parser = StrOutputParser()

# creating chain 

chain = prompt | model | parser

result = chain.invoke({'topic': "Himalayas"})

print(result)


# for visualization 

chain.get_graph().print_ascii()