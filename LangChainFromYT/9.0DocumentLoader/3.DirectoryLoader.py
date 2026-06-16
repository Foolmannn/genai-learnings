from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader



loader = DirectoryLoader(
    path="Folder",
    glob='*.pdf', # this means all the pdf files
    loader_cls=PyPDFLoader  # loader to use for each file inside the folder
)

docs= loader.load()

print(len(docs))  # 364 this is total no of documents . Each documents for each page 

print(docs[0].page_content)
print(docs[0].metadata)

# {'producer': 'pdfTeX-1.40.13', 'creator': 'TeX', 'creationdate': '2012-10-19T10:50:38-07:00', 'moddate': '2012-10-19T10:50:38-07:00', 'trapped': '/False', 'ptex.fullbanner': 'This is pdfTeX, Version 3.1415926-2.4-1.40.13 (TeX Live 2012) kpathsea version 6.1.0', 'source': 'Folder/cs229-prob.pdf', 'total_pages': 12, 'page': 0, 'page_label': '1'}

# this shows the first page of the first document. it shows the sources too. 

print(docs[326].page_content)
print(docs[326].metadata)

# this loads from the book and shows the page no ot the book which is 


# as we can see for just 3 pdf it is taking a lot of time so for bigger document the it will be worse. And for bigger memory constraints also exists . 

# so the solution is to use the lazy loading. 