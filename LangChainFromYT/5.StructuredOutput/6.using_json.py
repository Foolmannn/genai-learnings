from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

#JSON IS USED WHEN WE HAVE TO USE THE MULTIPLE LANGUAGE AS JSON IS UNIVERSAL LANGUAGE 

load_dotenv()

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

# schema
Review_json_schema = {
  "title": "Review",
  "type": "object",
  "properties": {
    "key_themes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Write down all the key themes discussed in the review in a list"
    },
    "summary": {
      "type": "string",
      "description": "A brief summary of the review"
    },
    "sentiment": {
      "type": "string",
      "enum": ["pos", "neg"],
      "description": "Return sentiment of the review either negative, positive or neutral"
    },
    "pros": {
      "type": ["array", "null"],
      "items": {
        "type": "string"
      },
      "description": "Write down all the pros inside a list"
    },
    "cons": {
      "type": ["array", "null"],
      "items": {
        "type": "string"
      },
      "description": "Write down all the cons inside a list"
    },
    "name": {
      "type": ["string", "null"],
      "description": "Write the name of the reviewer"
    }
  },
  "required": ["key_themes", "summary", "sentiment"]
}

structured_model  = model.with_structured_output(Review_json_schema)

result = structured_model.invoke("""I recently upgraded to the Samsung Galaxy S24 Ultra, and I must say, it’s an absolute powerhouse! The Snapdragon 8 Gen 3 processor makes everything lightning fast—whether I’m gaming, multitasking, or editing photos. The 5000mAh battery easily lasts a full day even with heavy use, and the 45W fast charging is a lifesaver.

The S-Pen integration is a great touch for note-taking and quick sketches, though I don't use it often. What really blew me away is the 200MP camera—the night mode is stunning, capturing crisp, vibrant images even in low light. Zooming up to 100x actually works well for distant objects, but anything beyond 30x loses quality.

However, the weight and size make it a bit uncomfortable for one-handed use. Also, Samsung’s One UI still comes with bloatware—why do I need five different Samsung apps for things Google already provides? The $1,300 price tag is also a hard pill to swallow.

Pros:
Insanely powerful processor (great for gaming and productivity)
Stunning 200MP camera with incredible zoom capabilities
Long battery life with fast charging
S-Pen support is unique and useful
                                 

""")

print(result)

# {'key_themes': ['performance', 'camera quality', 'battery life', 'ergonomics', 'software bloatware', 'price'], 'summary': 'The Samsung Galaxy S24 Ultra is a high-performance device with exceptional camera capabilities and battery life, though it suffers from issues regarding its large size, pre-installed bloatware, and high cost.', 'sentiment': 'pos', 'pros': ['Insanely powerful processor', 'Stunning 200MP camera', 'Incredible zoom capabilities', 'Long battery life', 'Fast charging', 'S-Pen support'], 'cons': ['Heavy and large for one-handed use', 'Excessive pre-installed bloatware', 'High price point', 'Loss of image quality beyond 30x zoom'], 'name': 'Nitish Singh'}

print(result['cons'])
print(result['name'])

# ['Heavy and large size makes one-handed use uncomfortable', 'Excessive pre-installed bloatware', 'High price tag']
# Nitish Singh

# So  THIS IS BETTER AND POWERFUL THAN THE TYPEDICT  AS IT ALSO PERFORM THE VALIDATAION USING THE PYDANTIC  FOR STRUCTURED OUTPUT 
