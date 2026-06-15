from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
# from langchain.schema.runnable  import RunnableSequence Deprecated

from langchain_core.runnables import RunnableSequence

load_dotenv()

prompt1 = PromptTemplate(
    template="Write a joke about {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template= "Explain the following joke : {text}",
    input_variables=['text']
)

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

parser = StrOutputParser()

chain = RunnableSequence(prompt1,model,parser,prompt2,model,parser)  
# this helps us to create the sequencial chain | operator can be used. 

# As this Runnable sequence is used very widely and most often so LC team create a LCEL (langchain Expression Language  ) . Which is | for the RunnableSequence pipe operator . So this is declarative syntax way to use Sequence . 


print(chain.invoke({'topic':"AI"}))