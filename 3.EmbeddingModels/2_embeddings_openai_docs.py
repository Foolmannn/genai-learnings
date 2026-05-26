from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv()

embedding = OpenAIEmbeddings(model='text-embedding-3-large',dimensions=32)

documents=[
    "Nepal is a beautiful country to visit",
    "Best time to visit nepal is on spring ",
    "Mountaineering season is from March-April "
]



result = embedding.embed_documents(documents)


print(str(result))