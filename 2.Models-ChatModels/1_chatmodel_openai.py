from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

# model = ChatOpenAI(model='gpt-4')

# result = model.invoke("What is the best time to visit Nepal ?")
model = ChatOpenAI(model='gpt-4',temperature = 0)


'''
temperature value ranges from the 0 - 2 it is a creative parameter. 

0.0 - 0.3     for the factual answers (math, code, facts )

0.5 - 0. 7     balanced response (general QA , explations)

0.9-1.2       creative writing , storytelling, jokes

1.5 +          Maximum rnadomness (wild ideas, brainstorming )
'''

result = model.invoke("What is the best time to visit Nepal ?")

print(result) # it gives not just answer content. It gives more other content information . 

print(result.content)