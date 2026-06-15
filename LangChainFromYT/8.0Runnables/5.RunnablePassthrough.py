# Runnable Passthrough is a special RUnnable primitive that simpy returns the input as output without modifying it. 

# It is useful in some scenario for ex in the runnable requence ex we have used the sequence. But as we have seen we have seen the explanation but the joke was not seen in output So we can use the Runnable PassThrough is this case 

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

from langchain_core.runnables import RunnableParallel,RunnablePassthrough,RunnableSequence

load_dotenv()

prompt1 = PromptTemplate(
    template="Write a joke about {topic}",
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template= "Explain the following joke : {text}",
    input_variables=['text']
)

model=ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')

parser = StrOutputParser()
joke_gen_chain= RunnableSequence(prompt1,model,parser)

parallel_chain = RunnableParallel(
    {
        'Joke': RunnablePassthrough(),
        'explanation': RunnableSequence(prompt2,model,parser)
    }
)

final_chain = joke_gen_chain | parallel_chain
print(final_chain.invoke({'topic':"AI"}))