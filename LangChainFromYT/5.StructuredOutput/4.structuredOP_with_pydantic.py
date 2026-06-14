from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
from typing import TypedDict,Annotated,Optional,Literal
from pydantic import BaseModel,Field


load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')


class Review(BaseModel):
    key_themes : list[str] = Field(description="Write down all the key themes discussed in the review in a list ")
    summary : str= Field(description="A breif summary of the review")
    sentiment: Literal['pos','neg'] = Field(description="Return the sentiment of the review either negative or positive ")
    pros: Optional[list[str]] =Field(description="Write down all the pros inside a list ")
    cons: Optional[list[str]] = Field(description="Write down all the cons inside a list")
    name: Optional[str]=Field(description="Write the name of the reviewer")

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

print(result.name)

# key_themes=['Performance', 'Camera quality', 'Battery life', 'Ergonomics', 'Software bloatware', 'Price'] summary='The Samsung Galaxy S24 Ultra is a top-tier powerhouse with exceptional performance, camera capabilities, and battery life, though it is held back by its large size, pre-installed bloatware, and high price.' sentiment='pos' pros=['Snapdragon 8 Gen 3 processor', '200MP camera', 'Stunning night mode photography', 'Functional 100x zoom', 'Long battery life', 'Fast 45W charging', 'Useful S-Pen integration'] cons=['Heavy and large size', 'Difficult for one-handed use', 'Excessive bloatware', 'High price point', 'Image quality loss beyond 30x zoom'] name='Nitish Singh'
# Nitish Singh


# So  THIS IS BETTER AND POWERFUL THAN THE TYPEDICT  AS IT ALSO PERFORM THE VALIDATAION USING THE PYDANTIC  FOR STRUCTURED OUTPUT 
