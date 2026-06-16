from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv

# https://docs.langchain.com/oss/python/integrations/document_loaders#all-document-loaders 

load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

prompt = PromptTemplate(
    template="Write a summary for the following poem : \n {poem}",
    input_variables=['poem']
)
parser = StrOutputParser()

loader = TextLoader('cricket.txt', encoding="utf-8") # this encoding is needed as there are some emojis 


docs = loader.load()

# print(docs)
print(type(docs))  #  <class 'list'> 

# this is because the langchain store the document as the list 

# acutal document is at the first index 

# print(docs[0])

print(type(docs[0]))

# so the format is document object {
# pagecontent = " ",
# metaData=" "
# }

# <class 'list'>
# page_content='Beneath the sun or floodlight's gleam,
# And cricket lives, eternally.'
#  metadata={'source': 'cricket.txt'}
# <class 'langchain_core.documents.base.Document'>   this shows the document is stored as the Documnet object of the langchain


chain = prompt | model |  parser

result = chain.invoke({'poem': docs[0].page_content})  # this is how we send the model the document loaded 
print(result)