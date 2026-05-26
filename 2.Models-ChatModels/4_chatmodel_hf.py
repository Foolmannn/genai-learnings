from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv

load_dotenv()

# 1. Use the chat-tuned repository ID instead
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1-0528",
    task="text-generation",
    temperature=0.7, # Added to give creative yet stable responses
    max_new_tokens=512 # Ensures the response doesn't cut off mid-sentence
)

# 2. Wrap it with ChatHuggingFace safely
model = ChatHuggingFace(llm=llm)

# 3. Invoke the model
result = model.invoke("What is best time to visit Nepal?")

print(result.content)


