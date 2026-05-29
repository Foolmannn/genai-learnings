from langchain_core.messages import SystemMessage,HumanMessage, AIMessage

from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()
model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 100)

messages = [
    SystemMessage(content='You are a helpful assistant'),
    HumanMessage(content='Tell me about langchain'),

]

result =model.invoke(messages)

messages.append(AIMessage(result.content[0]['text']))

print(messages)

# [SystemMessage(content='You are a helpful assistant', additional_kwargs={}, response_metadata={}), HumanMessage(content='Tell me about langchain', additional_kwargs={}, response_metadata={}), AIMessage(content='**LangChain** is an open-source development framework designed to simplify the creation of applications that use Large Language Models (LLMs) like GPT-4, Claude, or Llama.\n\nThink of LangChain as a "glue" layer. While LLMs are incredibly smart, they are often disconnected from your private data and struggle to perform multi-step workflows on their own. LangChain provides the tools to connect these models to external data sources and allow them to interact with', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[])]