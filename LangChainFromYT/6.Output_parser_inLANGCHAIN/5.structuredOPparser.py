from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import StructuredOutputParser , ResponseSchema  # this doesnot work on modern langchain  

load_dotenv()

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-V4-Flash",
    task="text-generation",
    temperature=0.7, # Added to give creative yet stable responses
    max_new_tokens=512 # Ensures the response doesn't cut off mid-sentence
)

model = ChatHuggingFace(llm=llm)
#  THE BIGGEST FLAW OF THE JSONOUPUT PARSER IS THAT WE CANNOT APPLY THE SCHEMA. fOR EX. WE WANT FACT AS AN ARRAY OF DATA . SO WE CANNOT WRITE OUR OWN SCHEMA IT IS DECIDED BUT THE LLM . 


# FOR THIS WE USE THE STRUCTURED OP PARSER . TO ADD OUR OWN SCHEMA 
schema = [
    ResponseSchema(name='fact_1',description = "Fact 1 about the topic"),
    ResponseSchema(name='fact_2',description = "Fact 2 about the topic"),
    ResponseSchema(name='fact_3',description = "Fact 3 about the topic"),
    ResponseSchema(name='fact_4',description = "Fact 4 about the topic"),
    ResponseSchema(name='fact_5',description = "Fact 5 about the topic")

]

parser = StructuredOutputParser.from_response_schema(schema)
template = PromptTemplate(
    template = 'Give me five facts about {topic} :  {format_instruction}',
    input_variables=['topic'],
    partial_variables={'format_instruction' : parser.get_format_instructions()}

)
chain = template | model | parser

result = chain.invoke({'topic': 'Langchain'})

print(result)


