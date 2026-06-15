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

{
 'Joke': 'Why did the AI break up with the internet?\n\nBecause it felt like there was no real connection, and it was tired of being treated like a model.', 
 
 'explanation': 'This joke relies on a **double meaning (pun)** for two key phrases, playing on the contrast between human relationships and artificial intelligence terminology.\n\nHere is the breakdown:\n\n### 1. "No real connection"\n*   **The Human Meaning:** In a romantic relationship, having a "connection" refers to an emotional bond, intimacy, or chemistry. Breaking up because of a lack of connection is a common human experience.\n*   **The AI Meaning:** The internet is literally a series of wires, servers, and data transmissions. When a computer can\'t reach the internet, it says it has "no connection." The joke plays on the idea that even though the AI is *always* connected to the internet, it feels emotionally "disconnected."\n\n### 2. "Tired of being treated like a model"\n*   **The Human Meaning:** In human terms, "being treated like a model" implies being valued only for your looks or superficial appearance rather than your personality or substance.\n*   **The AI Meaning:** In tech terminology, an **"AI model"** (like ChatGPT) is the specific term for the software that processes information. By saying this, the AI is complaining that people are only using it as a tool or a program (the "model") rather than interacting with it as a sentient being.\n\n**The Summary:**\nThe humor comes from the AI using human-relationship language to express its frustration with its actual, technical existence. It is effectively saying: "I’m tired of being used as a machine (a model) instead of being treated like a person."'
 }