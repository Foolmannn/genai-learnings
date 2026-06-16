# as we can see for just 3 pdf it is taking a lot of time so for bigger document the it will be worse. And for bigger memory constraints also exists . 

# so the solution is to use the lazy loading. 

# load() function loads the everything at once  (Eager loading)
# Lazy loading lazy_load() loads the document on demand (Lazy loading) . So for the large documents this is better approach :
# It is useful wheren the large documents and we want the stream processing 

from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader



loader = DirectoryLoader(
    path="Folder",
    glob='*.pdf', # this means all the pdf files
    loader_cls=PyPDFLoader  # loader to use for each file inside the folder
)

# docs= loader.load()
# this makes us wait for the all document to load the print the metadata of all the document 

docs=loader.lazy_load()
# this doesnot make us wait but slowly shows the data of all documents by loading the document is loaded in memory then print then removing then another document. 

# print(len(docs)) avoid using this in lazyload( ) as all documents are not loader  

for document in docs:
    print(document.metadata)


