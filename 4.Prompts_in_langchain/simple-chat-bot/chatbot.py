from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate,load_prompt

load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 100)

# while True:
#     user_input = input('You: ')
#     if user_input == 'exit':
#         break
#     result = model.invoke(user_input)
#     print("AI: ",result.content[0]['text'])


# You: tell me which one is bigger 2 or 9
# AI:  9 is bigger than 2.
# You: multiply the bigger one with 2 
# AI:  Please provide the two numbers you would like me to compare! Once you give them to me, I will identify the bigger one and multiply it by 2 for you.
# You: 

# so as we can see the model forget the previous conversation. So it doesnot have the contextt. It doesnot have the history, memory
# So we need to create a history data 
chat_history = []
while True:
    user_input = input('You: ')
    chat_history.append(user_input)
    if user_input == 'exit':
        break
    result = model.invoke(chat_history)
    chat_history.append(result.content[0]['text'])
    print("AI: ",result.content[0]['text'])

print(chat_history)

# You: which is bigger 2 or 0
# AI:  **2** is bigger than 0.
# You: now multiply bigger one with 5
# AI:  Since 2 is the bigger number, multiplying it by 5 gives you:

# 2 × 5 = **10**
# You: exit
# ['which is bigger 2 or 0', '**2** is bigger than 0.', 'now multiply bigger one with 5', 'Since 2 is the bigger number, multiplying it by 5 gives you:\n\n2 × 5 = **10**', 'exit']

# Now this solves the lost of context problem 

