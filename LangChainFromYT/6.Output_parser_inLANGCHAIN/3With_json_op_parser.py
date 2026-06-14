from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

# 1. Use the chat-tuned repository ID instead
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V4-Flash",
    task="text-generation",
    temperature=0.7, # Added to give creative yet stable responses
    max_new_tokens=512 # Ensures the response doesn't cut off mid-sentence
)

model = ChatHuggingFace(llm=llm)

parser = JsonOutputParser()

template = PromptTemplate(
    template = 'Give me the name , age and city of the fictional person :  {format_instruction}',
    input_variables=[],
    partial_variables={'format_instruction' : parser.get_format_instructions()}

)
prompt = template.format()

# chain = template | model | parser  we can use the chain too 

print(prompt)
# Give me the name , age and city of the fictional person :  Return a JSON object.  this is the prompt being sent which is due to the partial_variables we used : So get_format_instructions give the instructions as this help us to use any kind of output parserr like json, string and automatically it will be sent 

result = model.invoke(prompt)
# print(result.content)
print(type(result)) 
print(type(result.content))  # as we can see  this is string which cannot be used in the system like api. database etc so parsing is neccessary  



final_result = parser.parse(result.content) # this is dict which is json of python . Which can be used as a structured op 
print(type(final_result))

print(final_result['name']) # here we can extract the required data as in formal data structures like list, dict, json objects  etc 