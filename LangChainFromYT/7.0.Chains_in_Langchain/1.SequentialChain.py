# we are creating a detailed report . topic -> llm -> report -> llm  -> summary . This is complex as we are calling two llm two times 


from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

from langchain_core.output_parsers import StrOutputParser


load_dotenv()


prompt1 = PromptTemplate(
    template='Generate a detailed report on  {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template="Generate a five pointer summary from the following text: \n {text}",
    input_variables=['text']
)


model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

parser = StrOutputParser()

# creating chain 

chain = prompt1 | model | parser | prompt2 | model | parser

result = chain.invoke({'topic': "Himalayas"})

print(result)


# for visualization 

chain.get_graph().print_ascii()