# for ex. in shooping platform :

# Hello i want the refund for the product . IT come broken
# Ai: Ok , yuo will be refunded within 2 3 business day.

# 2 days later

# where is my refund .

# now problem is as in new chat bot doesnot know the history of the previous converstion. done some day ago. So we need to save those in db so that it can be inserted when the same user reinitiate the converstion. 

from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

# chat template

chat_template = ChatPromptTemplate([
    ('system','YOu are a helpful customer support agent'),
    MessagesPlaceholder(variable_name='chat_history'),  # this adds the message placeholder which will be passed at the invoke time 
    ('human','{query}')
])

chat_history = []
# load chat history

# reading the history from file. Acutally the data base is used 
with open('chat_history.txt','r') as f:
    chat_history.append(f.readlines())

print(chat_history)

# create prompt 

prompt = chat_template.invoke({'chat_history':chat_history , 'query':'Where is my Refund ?'})
print(prompt)