from langchain_openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

llm = OpenAI(model = 'gpt-3.5-turbo-instruct')
result = llm.invoke("What is the best time to visit Nepal")
print(result) # this igves the simple text string output and takes the string input 

# LLMs are outdated as they are generalized . So nowadays chat models are preferred as they are trained on the conversational data 