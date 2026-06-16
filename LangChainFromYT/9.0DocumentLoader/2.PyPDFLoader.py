# this works well for the normal pdf with textual data not well for the pdf made by scanning the pictures or other 

from langchain_community.document_loaders import PyPDFLoader # it uses the pypdf module in python

# for other types of pdf refer to the note pdf 

loader = PyPDFLoader('pdfTest.pdf')

docs = loader.load()

# print(docs)

print(len(docs))  # 12 as we have 12 pages so it loads the document for each page 

print(docs[0].page_content)
print(docs[1].metadata)
# this is meta data it shows the page no total pages, producer etc
# {'producer': 'pdfTeX-1.40.13', 'creator': 'TeX', 'creationdate': '2012-10-19T10:50:38-07:00', 'moddate': '2012-10-19T10:50:38-07:00', 'trapped': '/False', 'ptex.fullbanner': 'This is pdfTeX, Version 3.1415926-2.4-1.40.13 (TeX Live 2012) kpathsea version 6.1.0', 'source': 'pdfTest.pdf', 'total_pages': 12, 'page': 1, 'page_label': '2'}