from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(model_name ='sentence-transformers/all-MiniLM-L6-v2')

text= "Nepal is one of the best place for the Mountaineering"

documents=[
    "Nepal is a beautiful country to visit",
    "Best time to visit nepal is on spring ",
    "Mountaineering season is from March-April "
]
# vector = embedding.embed_query(text)  # we can do it for documents tooo

vector = embedding.embed_documents(documents)

print(str(vector))