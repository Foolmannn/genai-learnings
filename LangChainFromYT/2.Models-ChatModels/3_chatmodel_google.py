from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()

model = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 20)


result = model.invoke("What is the best time to visit Nepal? ")
# print(result)
print(result.content[0]["text"])

# content=[{'type': 'text', 'text': 'The "best" time to visit Nepal depends on what you plan to do,', 'extras': {'signature': 'EjQKMgEMOdbHlrKcXB51RNOEsiP8HbOQgpodCu1P2fkskj/L3D0ByRHoaAkBcRMbKzIMCo9s'}}] 
# additional_kwargs={} 
# response_metadata={'finish_reason': 'MAX_TOKENS', 'model_name': 'gemini-3.1-flash-lite', 'safety_ratings': [], 'model_provider': 'google_genai'} id='lc_run--019e6448-f3aa-7c63-babf-492d79801ec5-0' 
# tool_calls=[] 
# invalid_tool_calls=[] 
# usage_metadata={'input_tokens': 11, 'output_tokens': 16, 'total_tokens': 27, 'input_token_details': {'cache_read': 0}}
