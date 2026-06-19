# https://chunkviz.up.railway.app/
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# text = """
# One of the most important things I didn't understand about the world when I was a child is the degree to which the returns for performance are superlinear.

# Teachers and coaches implicitly told us the returns were linear. "You get out," I heard a thousand times, "what you put in." They meant well, but this is rarely true. If your product is only half as good as your competitor's, you don't get half as many customers. You get no customers, and you go out of business.
# """
loader = PyPDFLoader('pdfTest.pdf')

docs = loader.load()

splitter = CharacterTextSplitter(
    chunk_size=100,  # no of characters for the chunk_size
    chunk_overlap=0,  # this means how much overlap there is between the chunks 
    separator=''

)
# the benefit of using the chunk_overlap is that while using the Charactoer Text splitter the text can abruptly broken. There might loss the context. So by this it helps to preserve the context. and pass context to another chunk. So overlap is balanced if more the chunk no will be very more and if less then context loss is very high.
# # it is considered 10-20 percent of the overlap is best for the RAG based application  

# result = splitter.split_text(text)

result = splitter.split_documents(docs)

print(result[1])

print(result[1].page_content)




