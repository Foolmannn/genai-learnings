from langchain_openai import OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv()

embedding = OpenAIEmbeddings(model='text-embedding-3-large',dimensions=32)


result = embedding.embed_query("Nepal is a breathtaking destination that offers a perfect blend of ancient history, lush greenery, and stunning landscapes. While there are many popular spots, the **best places** to visit depend on your interests (e.g., history, nature, culture, or adventure).")


print(str(result))