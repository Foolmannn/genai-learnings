# \n\n for paragraph
# \n line
# ' ' word 
# '' character 
from langchain_text_splitters import RecursiveCharacterTextSplitter    # it tries to avoid splitting the word in mid point. It first split the text in paragraph , then into words then merge to get the less than chunksize . This is way better and widely used text splitter.

text = """
Space exploration has led to incredible scientific discoveries. From landing on the Moon to exploring Mars, humanity continues to push the boundaries of what’s possible beyond our planet.

These missions have not only expanded our knowledge of the universe but have also contributed to advancements in technology here on Earth. Satellite communications, GPS, and even certain medical imaging techniques trace their roots back to innovations driven by space programs.
"""

# Initialize the splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=0,
)

# Perform the split
chunks = splitter.split_text(text)

print(len(chunks))
print(chunks)