# now create the labeled, dynamic list of messages


from langchain_core.messages import SystemMessage,HumanMessage,AIMessage

from langchain_core.prompts import ChatPromptTemplate

chat_template = ChatPromptTemplate( # this is as same as Like PromptTemplate but it was used for the single turn messages and this ChatPromptTemplate is used for the multi turn conversations 
    # [
    #     SystemMessage(content="You are a helpful {domain} expert. "),
    #     HumanMessage(content='You are a helpful {domain} expert. ')
    # ] this doesnot work so as per doc we should pass messages like a tuple 
    [

    ('system','You are a helpful {domain} expert. '),
    ('human','You are a helpful {domain} expert.')
    ] # this works It is recent way from documentation 
)

prompt = chat_template.invoke({'domain':'cricket','topic':'Dusra'})

print(prompt)