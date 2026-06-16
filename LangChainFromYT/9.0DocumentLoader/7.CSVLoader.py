from langchain_community.document_loaders import CSVLoader

loader  = CSVLoader(file_path='Social_Network_Ads.csv')

docs = loader.load()

print(len(docs)) # this gives one document for the each row of data 

print(docs[0])
print(docs[2].metadata)

# 400
# page_content='User ID: 15624510
# Gender: Male
# Age: 19
# EstimatedSalary: 19000
# Purchased: 0' metadata={'source': 'Social_Network_Ads.csv', 'row': 0}
# {'source': 'Social_Network_Ads.csv', 'row': 2}