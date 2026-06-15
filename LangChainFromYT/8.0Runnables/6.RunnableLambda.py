# Using Lambda we can add the extra workflow like preprocessing And we can connect to langchain flow by converting it to runnable. 

# For ex: we are asking joke . Then we will create our own functioni to count the no of word in the joke. We will not want to ask llm to count the words. 

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableSequence,RunnableLambda

load_dotenv()



prompt1 = PromptTemplate(
    template="Write a one joke about {topic}",
    input_variables=['topic']
)


model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

parser = StrOutputParser()
joke_gen_chain= RunnableSequence(prompt1,model,parser)

# custom function to count the no. of words

def word_counter(text):
    return len(text.split())

# conversion to he Runnable 
runnable_word_counter = RunnableLambda(word_counter)
# print(runnable_word_counter.invoke("Here is five no words.")) 


parallel_chain = RunnableParallel(
    {
        'Joke': joke_gen_chain,
        'count': runnable_word_counter,
        # 'word_count':RunnableLambda(word_counter) Another method
        
        "word_counts": RunnableLambda(lambda x : len(x.split())) # another method 
    }
)

final_chain = joke_gen_chain | parallel_chain
print(final_chain.invoke({'topic':"AI"}))

{
'Joke': 'Why did the AI go to therapy?\n\nBecause it had too many unresolved cache issues.',  
 'count': 15
 }