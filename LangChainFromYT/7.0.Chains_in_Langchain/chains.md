# Chains in LangChain (Detailed Explanation)

A **Chain** in LangChain is a sequence of operations that are executed one after another to accomplish a task. It connects different components such as:

* Prompts
* LLMs
* Chat Models
* Output Parsers
* Retrievers
* Tools
* Memory

The output of one component becomes the input of the next component.

Think of a chain like a pipeline:

```text
User Input
     ↓
Prompt Template
     ↓
LLM
     ↓
Output Parser
     ↓
Final Response
```

---

# Why Chains Are Needed

Without chains:

```python
prompt = f"Explain {topic}"
response = llm.invoke(prompt)
```

This works for simple tasks.

But real applications need multiple steps:

* Retrieve data from a database
* Format prompts
* Call LLM
* Parse output
* Store conversation history

Chains automate these workflows.

---

# Evolution of Chains in LangChain

Older versions:

```python
LLMChain
SequentialChain
SimpleSequentialChain
```

These are largely considered legacy.

Modern LangChain (LCEL - LangChain Expression Language) uses:

```python
prompt | model | parser
```

This is the recommended approach.

---

# Basic Chain Structure

## Step 1: Create Prompt

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    "Explain {topic} in simple terms."
)
```

---

## Step 2: Create Model

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI()
```

---

## Step 3: Create Parser

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
```

---

## Step 4: Create Chain

```python
chain = prompt | model | parser
```

Visualization:

```text
Prompt
   ↓
Model
   ↓
Parser
```

---

## Step 5: Invoke Chain

```python
result = chain.invoke({
    "topic": "Neural Networks"
})

print(result)
```

---

# How Data Flows Through Chain

Suppose:

```python
chain.invoke({
    "topic":"Python"
})
```

### Prompt Receives

```python
{
   "topic":"Python"
}
```

Produces:

```text
Explain Python in simple terms.
```

---

### LLM Receives

```text
Explain Python in simple terms.
```

Produces:

```text
Python is a programming language...
```

---

### Parser Receives

```text
Python is a programming language...
```

Returns:

```python
"Python is a programming language..."
```

---

# Runnable Interface

Modern chains are built from **Runnables**.

Every runnable supports:

## invoke()

Single input

```python
chain.invoke({"topic":"AI"})
```

---

## batch()

Multiple inputs

```python
chain.batch([
    {"topic":"AI"},
    {"topic":"ML"},
    {"topic":"DL"}
])
```

---

## stream()

Token streaming

```python
for chunk in chain.stream(
    {"topic":"AI"}
):
    print(chunk)
```

---

## ainvoke()

Async invocation

```python
await chain.ainvoke(
    {"topic":"AI"}
)
```

---

# Types of Chains

---

# 1. Simple Chain

One prompt → one model.

```python
chain = prompt | model | parser
```

```text
Input
 ↓
Prompt
 ↓
LLM
 ↓
Output
```

---

# 2. Sequential Chain

Multiple operations executed sequentially.

Example:

```text
Topic
 ↓
Generate Summary
 ↓
Generate Quiz
 ↓
Generate Answers
```

---

Modern LCEL:

```python
summary_chain = summary_prompt | model
quiz_chain = quiz_prompt | model

full_chain = summary_chain | quiz_chain
```

---

# Example

Step 1:

```python
summary_prompt = ChatPromptTemplate.from_template(
    "Summarize {topic}"
)
```

Step 2:

```python
quiz_prompt = ChatPromptTemplate.from_template(
    """
    Create 5 quiz questions from:

    {text}
    """
)
```

Step 3:

```python
summary_chain = summary_prompt | model

full_chain = (
    summary_chain
    | quiz_prompt
    | model
    | parser
)
```

Flow:

```text
Topic
 ↓
Summary
 ↓
Quiz Prompt
 ↓
Quiz Generation
```

---

# 3. Parallel Chains

Run multiple chains simultaneously.

Example:

```text
Topic
 ├── Summary
 ├── Quiz
 └── Key Points
```

---

Using RunnableParallel:

```python
from langchain_core.runnables import RunnableParallel
```

```python
parallel_chain = RunnableParallel(
    summary=summary_chain,
    quiz=quiz_chain,
)
```

Invoke:

```python
result = parallel_chain.invoke(
    {"topic":"AI"}
)
```

Output:

```python
{
   "summary":"...",
   "quiz":"..."
}
```

---

# 4. Branching Chains

Different paths based on conditions.

```text
Input
 ↓
Condition
 ├── Path A
 └── Path B
```

Example:

```python
if sentiment == positive:
    positive_chain
else:
    negative_chain
```

Using:

```python
RunnableBranch
```

---

# 5. Router Chains

Route requests to specialized chains.

Example:

```text
Question
   ↓
Router
 ├── Math Expert
 ├── Coding Expert
 └── History Expert
```

---

Input:

```text
Write Python code
```

Router selects:

```text
Coding Chain
```

---

# 6. Retrieval Chain (RAG)

Most important chain for AI applications.

Flow:

```text
Question
 ↓
Retriever
 ↓
Relevant Documents
 ↓
Prompt
 ↓
LLM
 ↓
Answer
```

---

Example:

```python
retrieval_chain = (
    retriever
    | prompt
    | model
)
```

Used in:

* Chatbots
* PDF QA
* Knowledge bases
* Search systems

---

# RunnablePassthrough

Pass data unchanged.

```python
from langchain_core.runnables import RunnablePassthrough
```

Example:

```python
chain = (
    {
        "question": RunnablePassthrough(),
        "context": retriever
    }
    | prompt
    | model
)
```

Input:

```python
"What is LangChain?"
```

Produces:

```python
{
   "question":"What is LangChain?",
   "context":"retrieved docs"
}
```

---

# RunnableLambda

Convert Python functions into chain components.

```python
from langchain_core.runnables import RunnableLambda
```

Example:

```python
def uppercase(text):
    return text.upper()

chain = RunnableLambda(uppercase)
```

Invoke:

```python
chain.invoke("hello")
```

Output:

```text
HELLO
```

---

# Combining RunnableLambda with LLM

```python
formatter = RunnableLambda(
    lambda x: {
        "topic": x.upper()
    }
)

chain = (
    formatter
    | prompt
    | model
    | parser
)
```

---

# Chain with Structured Output

Suppose you want JSON.

Schema:

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
```

Structured output:

```python
structured_llm = model.with_structured_output(
    Person
)
```

Chain:

```python
chain = prompt | structured_llm
```

Output:

```python
Person(
    name="John",
    age=25
)
```

---

# Chain with Memory

Traditional idea:

```text
User
 ↓
Memory
 ↓
Prompt
 ↓
Model
```

Modern LangChain typically uses message history wrappers instead of older memory classes.

Example:

```python
RunnableWithMessageHistory
```

This automatically injects conversation history into the chain.

---

# Debugging Chains

## View Chain Graph

```python
chain.get_graph()
```

or

```python
chain.get_graph().print_ascii()
```

Example:

```text
Prompt
  |
Model
  |
Parser
```

---

# Real-World Example

Document Question Answering System

```text
User Question
       ↓
Retriever
       ↓
Relevant Chunks
       ↓
Prompt Template
       ↓
LLM
       ↓
Structured Parser
       ↓
Answer
```

Code:

```python
chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | model
    | StrOutputParser()
)
```

Usage:

```python
chain.invoke(
    "What is reinforcement learning?"
)
```

---

# Legacy Chains vs Modern Chains

| Legacy                       | Modern LCEL                 |
| ---------------------------- | --------------------------- |
| LLMChain                     | prompt | model              |
| SequentialChain              | chain1 | chain2             |
| RouterChain                  | RunnableBranch              |
| SimpleSequentialChain        | LCEL composition            |
| RetrievalQA                  | create_retrieval_chain      |
| ConversationalRetrievalChain | Retrieval + Message History |

---

# Key LCEL Operators

### Pipe Operator

```python
|
```

Connects components.

```python
prompt | model
```

---

### Parallel

```python
RunnableParallel
```

Runs multiple chains together.

---

### Branch

```python
RunnableBranch
```

Conditional execution.

---

### Passthrough

```python
RunnablePassthrough
```

Forward input unchanged.

---

### Lambda

```python
RunnableLambda
```

Wrap Python functions.

---

# Interview Definition

**A LangChain Chain is a composable workflow of Runnables where the output of one component becomes the input of the next. Modern LangChain uses LCEL (LangChain Expression Language) to build chains by connecting prompts, models, retrievers, tools, parsers, and memory using the pipe (`|`) operator, enabling sequential, parallel, branching, and retrieval-based AI workflows.**
