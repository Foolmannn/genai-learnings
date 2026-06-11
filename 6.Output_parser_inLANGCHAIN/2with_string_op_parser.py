from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. Use the chat-tuned repository ID instead
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V4-Flash",
    task="text-generation",
    temperature=0.7, # Added to give creative yet stable responses
    max_new_tokens=512 # Ensures the response doesn't cut off mid-sentence
)

model = ChatHuggingFace(llm=llm)


# 1st prompt -> detailed report
template1 = PromptTemplate(
    template = 'Write a detailed report on {topic}',
    input_variables=['topic']
)

#2 nd prompt  -> summary 

template2 = PromptTemplate(
    template = "Write a 5 line summary on the following text. /n {text}",
    input_variables=['text']
)

parser = StrOutputParser()

chain = template1 | model | parser | template2 | model | parser 
# this is chain . What happens is first the template1 is used then 

result = chain.invoke({'topic':"Black Hole"})

# prompt1 = template1.invoke({'topic':'black hole'})
# result1 = model.invoke(prompt1)

# prompt2 = template2.invoke({'text':result1.content})
# result2 = model.invoke(prompt2)

print(result)
