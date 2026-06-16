# It uses the request and BeautifulSoup library of python. 

# it works best for the static web pages. And for more dynamic using the SeleniumURlloader
# we need to install bs4 for the beautiful soap

from langchain_community.document_loaders import WebBaseLoader,SeleniumURLLoader

from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv

load_dotenv()

url = "https://mudita.com.np/lenovo-legion-7-16iax10-u9-275hx-rtx-5060.html"  # As we can see the document we got is not that good and nicely formated 
# url2 = ["https://en.wikipedia.org/wiki/ML","https://en.wikipedia.org/wiki/ML_(programming_language)"] # we can even send the list of urls

# loader = WebBaseLoader(url2)

# loader = WebBaseLoader(url)
# loader = SeleniumURLLoader(url)  # we need the selenium, unstructured it need more setup

urls = [
    "https://mudita.com.np/lenovo-legion-7-16iax10-u9-275hx-rtx-5060.html"
]

loader = SeleniumURLLoader(
    urls=urls,
    browser="chrome",
    headless=True
)
# this gives more better result 
docs = loader.load()

# print(len(docs))

print(docs[0].page_content)


model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

prompt = PromptTemplate(
    template="Answer the following questions : \n {questions} \n from the following test : \n {text}",
    input_variables=['text','questions']
)
parser = StrOutputParser()

chain = prompt | model | parser

# result = chain.invoke({'questions':"What are the main specifications of the prodcut ? ", 'text':docs[0].page_content})

# print(result)


