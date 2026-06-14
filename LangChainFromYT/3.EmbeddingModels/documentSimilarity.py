from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


embedding = HuggingFaceEmbeddings(model_name ='sentence-transformers/all-MiniLM-L6-v2')

documents = [
    "Virat Kohli is an Indian cricketer known for his aggressive batting and leadership.",
    "MS Dhoni is a former Indian captain famous for his calm demeanor and finishing skills.",
    "Sachin Tendulkar, also known as the 'God of Cricket', holds many batting records.",
    "Rohit Sharma is known for his elegant batting and record-breaking double centuries.",
    "Jasprit Bumrah is an Indian fast bowler known for his unorthodox action and yorkers."
]
query="tell me about Rohit Sharma"


doc_embeddings = embedding.embed_documents(documents)
query_embedding = embedding.embed_query(query)


# print(cosine_similarity([query_embedding],doc_embeddings)) # we have to pass both value as the 2D arrays as queryembedding is not a 2d we converted it and doc_embedding is already in 2d array
# [[0.46542253 0.35921699 0.44355194 0.72734208 0.47194653]]
# as it is 2d array we grab the first elements

scores = cosine_similarity([query_embedding],doc_embeddings)[0]

# print(list(enumerate(scores)))

# [(0, np.float64(0.465422534977158)), (1, np.float64(0.3592169882073831)), (2, np.float64(0.44355193726644815)), (3, np.float64(0.7273420779214999)), (4, np.float64(0.47194652616362154))]
# print(sorted(list(enumerate(scores)),key=lambda x:x[1])) # now sorting 

# [(1, np.float64(0.3592169882073831)), (2, np.float64(0.44355193726644815)), (0, np.float64(0.465422534977158)), (4, np.float64(0.47194652616362154)), (3, np.float64(0.7273420779214999))]

# as we need the largest similarity one : that is at the end 

index,score = sorted(list(enumerate(scores)),key=lambda x:x[1])[-1]

print(query)

print(f"Response:{documents[index]}")

print("Similarity score is: ",score)
