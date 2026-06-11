# THIS IS RECOMMENDED OP PARSER . IT ALLOWS THE SCHEMA ALONG WITH THE VALIDATION . 

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V4-Flash",
    task="text-generation",
    temperature=0.7, # Added to give creative yet stable responses
    max_new_tokens=512 # Ensures the response doesn't cut off mid-sentence
)

model = ChatHuggingFace(llm=llm)

# defining the pydantic model 

class Person(BaseModel):
    name : str = Field(description="Name of the person ")
    age : int = Field(gt=18,description='Age of the person ')
    city: str = Field(description="name of the city the person belongs to")


parser = PydanticOutputParser(pydantic_object=Person)

template = PromptTemplate(
    template="Generate the name, age and city of the fictional {place} person. \n {format_instructions}",
    input_variables=['place'],
    partial_variables={'format_instructions': parser.get_format_instructions()}
)


# prompt = template.invoke({'place':"Nepali"})
# print(prompt)
# text='Generate the name, age and city of the fictional Nepali person. \n 
# The output should be formatted as a JSON instance that conforms to the JSON schema below.\n\nAs an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}\nthe object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.\n\nHere is the output schema:\n```\n{"properties": {"name": {"description": "Name of the person ", "title": "Name", "type": "string"}, "age": {"description": "Age of the person ", "exclusiveMinimum": 18, "title": "Age", "type": "integer"}, "city": {"description": "name of the city the person belongs to", "title": "City", "type": "string"}}, "required": ["name", "age", "city"]}\n```'

# here we can see the parser has given this inputs for the output to follow the schema  and validators.  

# result = model.invoke(prompt)

# final_result = parser.parse(result.content)

# print(final_result)

# name='Anita Thapa' age=29 city='Pokhara'

# using chain 

chain = template | model | parser

final_result = chain.invoke({'place':'indian '})
print(final_result)