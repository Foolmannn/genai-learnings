from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
from typing import TypedDict,Annotated,Optional,Literal


load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

#schema
# class Review(TypedDict):

#     summary: str
#     sentiment:str

# this worked because llm is well trained but sometimes their might be ambiguity for that we can provide clear description using the anootated 

# class Review(TypedDict):
#     summary: Annotated[str,"A breif summary of the review"]
#     sentiment: Annotated[str,"Return the sentiment of the review either negative, positive or mixed "]

# structured_model  = model.with_structured_output(Review)

# result = structured_model.invoke(""" The hardware is great but the software feels bloated. There are too many pre-installed apps that I can't remove. Also, the UI looks outdaed compared to other brands . Hoping for a software update to fix this.
# """)

# print(result)

# #{'summary': 'The user appreciates the hardware quality but criticizes the bloated software, unremovable pre-installed apps, and outdated user interface.', 'sentiment': 'mixed'}

# print(result['summary'])
# print(result['sentiment'])


# For more complex kind of structrued output 
class Review(TypedDict):
    key_themes : Annotated[list[str], "Write down all the key themes discussed in the review in a list "]
    summary: Annotated[str,"A breif summary of the review"]
    # sentiment: Annotated[str,"Return the sentiment of the review either negative, positive or mixed "]
    sentiment: Annotated[Literal['pos','neg'],"Return the sentiment of the review either negative or positive "] # this literal just provide the options only 
    pros: Annotated[Optional[list[str]],"Write down all the pros inside a list "]
    cons: Annotated[Optional[list[str]],"Write down all the cons inside a list"] # there is optional tooo . Because cons sometime there is no cons or pros 

structured_model  = model.with_structured_output(Review)

result = structured_model.invoke("""I recently upgraded to the Samsung Galaxy S24 Ultra, and I must say, it’s an absolute powerhouse! The Snapdragon 8 Gen 3 processor makes everything lightning fast—whether I’m gaming, multitasking, or editing photos. The 5000mAh battery easily lasts a full day even with heavy use, and the 45W fast charging is a lifesaver.

The S-Pen integration is a great touch for note-taking and quick sketches, though I don't use it often. What really blew me away is the 200MP camera—the night mode is stunning, capturing crisp, vibrant images even in low light. Zooming up to 100x actually works well for distant objects, but anything beyond 30x loses quality.

However, the weight and size make it a bit uncomfortable for one-handed use. Also, Samsung’s One UI still comes with bloatware—why do I need five different Samsung apps for things Google already provides? The $1,300 price tag is also a hard pill to swallow.

Pros:
Insanely powerful processor (great for gaming and productivity)
Stunning 200MP camera with incredible zoom capabilities
Long battery life with fast charging
S-Pen support is unique and useful
                                 
Review by Nitish Singh
""")

print(result)

# {'key_themes': ['performance', 'camera capabilities', 'battery life', 'design and ergonomics', 'software bloatware', 'price'], 'summary': 'The Samsung Galaxy S24 Ultra is a top-tier powerhouse featuring an exceptional processor, impressive camera system, and reliable battery, though it is hindered by its large physical size, software bloatware, and high price point.', 'sentiment': 'positive', 'pros': ['Insanely powerful Snapdragon 8 Gen 3 processor', 'Stunning 200MP camera with excellent low-light performance', 'Long-lasting 5000mAh battery with fast charging', 'Useful S-Pen integration'], 'cons': ['Large size and weight make one-handed use difficult', 'Pre-installed Samsung bloatware', 'High price tag', 'Zoom quality degrades significantly beyond 30x']}

print(result['sentiment'])










