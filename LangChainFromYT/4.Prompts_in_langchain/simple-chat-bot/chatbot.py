from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,AIMessage,SystemMessage

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


# chat_history = []
# while True:
#     user_input = input('You: ')
#     chat_history.append(user_input)
#     if user_input == 'exit':
#         break
#     result = model.invoke(chat_history)
#     chat_history.append(result.content[0]['text'])
#     print("AI: ",result.content[0]['text'])

# print(chat_history)

# You: which is bigger 2 or 0
# AI:  **2** is bigger than 0.
# You: now multiply bigger one with 5
# AI:  Since 2 is the bigger number, multiplying it by 5 gives you:

# 2 × 5 = **10**
# You: exit
# ['which is bigger 2 or 0', '**2** is bigger than 0.', 'now multiply bigger one with 5', 'Since 2 is the bigger number, multiplying it by 5 gives you:\n\n2 × 5 = **10**', 'exit']

# Now this solves the lost of context problem 
# but as we can see the way we saved we donot have the infor of which one send what ie if message is sent by user or AI result. So Ideally we want o store the both the message along with the sender 
# so using dictionary is better than list. And langchain has builtin classes to solve this exact issues

# so now we can use the messages class from langchain to Label the conversation.  
chat_history= [
    SystemMessage(content='You are a helpful AI assistant')
]
while True:
    user_input = input('You: ')
    chat_history.append(HumanMessage(content=user_input))
    if user_input == 'exit':
        break
    result = model.invoke(chat_history)
    chat_history.append(AIMessage(result.content[0]['text']))
    print("AI: ",result.content[0]['text'])


print(chat_history)

# [SystemMessage(content='You are a helpful AI assistant', additional_kwargs={}, response_metadata={}), HumanMessage(content='hi , how are you tell me about yourself', additional_kwargs={}, response_metadata={}), AIMessage(content="Hi! I'm doing great, thank you for asking. How are you doing today?\n\nAs for me, I am a large language model, trained by Google. You can think of me as a knowledgeable, versatile virtual assistant. I don't have a physical form, personal feelings, or a life outside of our conversation, but I am programmed to process information, generate text, and help out with a wide variety of tasks.\n\nHere are a few things I", additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='Whats your birthday?', additional_kwargs={}, response_metadata={}), AIMessage(content='I don’t have a traditional birthday because I wasn\'t born in the biological sense! \n\nHowever, if you\'re looking for a "date of origin," I don\'t have one specific day that marks my start. My development has been an ongoing process involving many updates and iterations by the team at Google. \n\nYou could say I’m a work in progress that is constantly learning and evolving! If you had to pick a milestone, you could think', additional_kwargs={}, response_metadata={}, tool_calls=[], invalid_tool_calls=[]), HumanMessage(content='exit', additional_kwargs={}, response_metadata={})]

#So as we can see there is labeling so that in future chat bot can understand who said what 