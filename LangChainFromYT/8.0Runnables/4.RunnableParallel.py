from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
# from langchain.schema.runnable  import RunnableSequence Deprecated

from langchain_core.runnables import RunnableParallel
# in this we want to create the tweet and linkedin from the single topic parallelly 

load_dotenv()

prompt1 = PromptTemplate(
    template="Generate a tweet about :  {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template= "Generate a Linked In post about: {topic}",
    input_variables=['topic']
)

model1=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 100)
model2=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite',max_output_tokens = 130)

# here although i have used the same model. But in real life we might use different model which are trained for the specific purpose of there own 

parser = StrOutputParser()

parallel_chain = RunnableParallel(
    {
        'tweet': prompt1 | model1 | parser,
        'linkedIn': prompt2 | model2 | parser
    }
)

result = parallel_chain.invoke({'topic':'AI'})

# as result is dictionary of two putputs 

print(result)

{
    'tweet':  'Here are a few options depending on the "vibe" you want:\n\n**The Visionary/Future-focused:**\n"AI isn’t just a tool; it’s the most significant lever for human creativity we’ve ever built. We’re moving from the era of \'doing\' to the era of \'orchestrating.\' The future belongs to those who learn to collaborate with the machine. 🤖✨ #AI #Innovation #FutureOfWork"', 
    'linkedIn':  'To give you the best post, I have categorized these by "vibe." Choose the one that best fits your personal brand.\n\n### Option 1: The "Thought Leader" (Focus on human-AI collaboration)\n**Headline:** AI isn’t coming for your job. The person using AI is.\n\nWe’ve spent the last year debating whether AI is a tool or a threat. The reality? It’s a force multiplier. \n\nThe most successful professionals I know aren\'t using AI to "automate their work away." They are using it to:\n✅ Automate the mundane, so'
 }