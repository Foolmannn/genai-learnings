from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
# from langchain.schema.runnable  import RunnableSequence Deprecated

from langchain_core.runnables import RunnableParallel
# in this we want to create the tweet and linkedin from the single topic parallelly 

load_dotenv()

prompt1 = PromptTemplate(
    template="Generate a tweet about :  {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template= "Generate a Linked In post about: {topic}",
    input_variables=['topic']
)

model1=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 100)
model2=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 130)

# here although i have used the same model. But in real life we might use different model which are trained for the specific purpose of there own 

parser = StrOutputParser()

parallel_chain = RunnableParallel(
    {
        'tweet': prompt1 | model1 | parser,
        'linkedIn': prompt2 | model2 | parser
    }
)