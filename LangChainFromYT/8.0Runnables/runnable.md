# Runnables in LangChain (Detailed Notes)

Starting from modern LangChain (v0.1+ and especially v0.2+), **Runnables** are the fundamental building blocks of LangChain.

Almost everything in LangChain is a Runnable:

* LLMs
* Chat Models
* Prompt Templates
* Output Parsers
* Chains
* Retrievers
* Custom Functions

They all follow a common interface, making them easy to combine.

Think of Runnables as:

> "Objects that take an input, perform some operation, and return an output."

---

# Why Runnables Were Introduced

Older LangChain relied heavily on:

```python
LLMChain
SequentialChain
SimpleSequentialChain
```

These are now largely replaced by the **LangChain Expression Language (LCEL)** and Runnable architecture.

Benefits:

✅ More flexible

✅ Easier composition

✅ Streaming support

✅ Async support

✅ Parallel execution

✅ Better debugging

✅ Less boilerplate code

---

# Runnable Interface

Every Runnable supports several methods:

| Method    | Purpose         |
| --------- | --------------- |
| invoke()  | Run once        |
| batch()   | Run many inputs |
| stream()  | Stream outputs  |
| ainvoke() | Async invoke    |
| abatch()  | Async batch     |
| astream() | Async stream    |

---

# 1. invoke()

Runs the Runnable on a single input.

Example:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI()

result = model.invoke("What is AI?")

print(result.content)
```

Input:

```python
"What is AI?"
```

Output:

```python
AI is the simulation...
```

---

# 2. batch()

Runs multiple inputs together.

Instead of:

```python
for q in questions:
    model.invoke(q)
```

Use:

```python
questions = [
    "What is AI?",
    "What is ML?",
    "What is DL?"
]

results = model.batch(questions)

for r in results:
    print(r.content)
```

Benefits:

* Faster
* More efficient

---

# 3. stream()

Returns tokens as they are generated.

```python
for chunk in model.stream("Tell me a story"):
    print(chunk.content, end="")
```

Output:

```text
Once
upon
a
time...
```

Useful for:

* Chat applications
* Real-time interfaces

---

# 4. ainvoke()

Async version of invoke.

```python
result = await model.ainvoke("Hello")
```

Useful when:

* Building APIs
* Fast concurrent execution

---

# Core Runnable Types

LangChain provides several Runnable classes.

---

## RunnableSequence

Executes steps one after another.

```text
Input
  ↓
Prompt
  ↓
Model
  ↓
Parser
  ↓
Output
```

Example:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
    "Explain {topic}"
)

model = ChatOpenAI()

parser = StrOutputParser()

chain = prompt | model | parser
```

Here:

```python
chain
```

is a RunnableSequence.

---

### Invoke Sequence

```python
result = chain.invoke({
    "topic": "Neural Networks"
})

print(result)
```

Flow:

```text
Input Dictionary
      ↓
Prompt Template
      ↓
Chat Model
      ↓
Output Parser
      ↓
String Output
```

---

# LCEL Pipe Operator (|)

Most common Runnable operation.

```python
chain = prompt | model | parser
```

Equivalent to:

```python
RunnableSequence(
    first=prompt,
    middle=[model],
    last=parser
)
```

The pipe sends output of one step to next step.

Example:

```text
Prompt → Model → Parser
```

---

# RunnableLambda

Wraps a Python function into a Runnable.

Example:

```python
from langchain_core.runnables import RunnableLambda

def double(x):
    return x * 2

runnable = RunnableLambda(double)

print(runnable.invoke(5))
```

Output:

```python
10
```

---

### Example in Chain

```python
from langchain_core.runnables import RunnableLambda

uppercase = RunnableLambda(
    lambda x: x.upper()
)

chain = uppercase

print(chain.invoke("hello"))
```

Output:

```python
HELLO
```

---

# RunnableParallel

Runs multiple branches simultaneously.

Example:

```python
from langchain_core.runnables import RunnableParallel

parallel = RunnableParallel({
    "square": RunnableLambda(lambda x: x*x),
    "cube": RunnableLambda(lambda x: x*x*x)
})

result = parallel.invoke(3)

print(result)
```

Output:

```python
{
    'square': 9,
    'cube': 27
}
```

---

## Visual Flow

```text
          Input
             |
      ----------------
      |              |
   Square         Cube
      |              |
      ----------------
             |
          Output
```

---

# RunnablePassthrough

Passes input unchanged.

Useful when you need original input later.

Example:

```python
from langchain_core.runnables import RunnablePassthrough
```

```python
chain = RunnablePassthrough()

chain.invoke("hello")
```

Output:

```python
"hello"
```

---

## Practical Example

Input:

```python
{
  "question": "What is AI?"
}
```

Keep original question while generating answer.

```python
chain = RunnableParallel(
    question=RunnablePassthrough(),
    answer=model
)
```

Output:

```python
{
  "question": "...",
  "answer": "..."
}
```

---

# RunnableAssign

Adds new fields to dictionary output.

Example:

```python
from langchain_core.runnables import RunnablePassthrough

chain = RunnablePassthrough.assign(
    length=lambda x: len(x["text"])
)
```

Input:

```python
{
  "text": "hello"
}
```

Output:

```python
{
  "text": "hello",
  "length": 5
}
```

---

# RunnableMap

Applies multiple Runnables to same input.

Example:

```python
runnable = {
    "summary": summary_chain,
    "sentiment": sentiment_chain
}
```

This dictionary automatically becomes a RunnableMap.

```python
result = runnable.invoke(text)
```

Output:

```python
{
  "summary": "...",
  "sentiment": "positive"
}
```

---

# RunnableBranch

Conditional execution.

Like:

```python
if condition:
    do A
else:
    do B
```

Example:

```python
from langchain_core.runnables import RunnableBranch
```

```python
branch = RunnableBranch(
    (
        lambda x: x > 0,
        RunnableLambda(lambda x: "Positive")
    ),
    RunnableLambda(lambda x: "Negative")
)
```

```python
branch.invoke(5)
```

Output:

```python
Positive
```

---

# Binding Parameters

You can preconfigure a Runnable.

Example:

```python
model = ChatOpenAI()

creative_model = model.bind(
    temperature=1.0
)
```

Now:

```python
creative_model.invoke("Write a poem")
```

uses temperature = 1.

---

# Configuring Runtime Behavior

```python
chain.invoke(
    input,
    config={
        "tags":["test"],
        "metadata":{"user":"abc"}
    }
)
```

Useful for:

* LangSmith tracing
* Monitoring
* Logging

---

# Streaming Through Chains

Entire chains can stream.

```python
chain = prompt | model | parser
```

```python
for chunk in chain.stream(
    {"topic":"AI"}
):
    print(chunk, end="")
```

The stream flows through all components.

---

# Batch Processing Through Chains

```python
chain.batch([
    {"topic":"AI"},
    {"topic":"ML"},
    {"topic":"DL"}
])
```

Produces:

```python
[
    "...",
    "...",
    "..."
]
```

---

# Custom Runnable Class

You can create your own Runnable.

```python
from langchain_core.runnables import Runnable

class AddOneRunnable(Runnable):

    def invoke(self, input, config=None):
        return input + 1
```

Usage:

```python
r = AddOneRunnable()

print(r.invoke(5))
```

Output:

```python
6
```

---

# Real-World RAG Runnable Flow

A Retrieval-Augmented Generation pipeline often looks like:

```text
User Question
       |
       v
Retriever
       |
       v
Retrieved Documents
       |
       v
Prompt Template
       |
       v
LLM
       |
       v
Parser
       |
       v
Final Answer
```

LCEL version:

```python
chain = (
    retriever
    | prompt
    | model
    | StrOutputParser()
)
```

Everything in the pipeline is a Runnable.

---

# Modern LangChain Philosophy

Instead of old chains:

```python
LLMChain
SequentialChain
SimpleSequentialChain
```

Modern LangChain prefers:

```python
prompt | model | parser
```

because every component implements the Runnable interface.

---

# Summary

| Runnable Type       | Purpose                          |
| ------------------- | -------------------------------- |
| invoke()            | Single execution                 |
| batch()             | Multiple inputs                  |
| stream()            | Token streaming                  |
| RunnableSequence    | Sequential execution             |
| RunnableLambda      | Wrap Python functions            |
| RunnableParallel    | Parallel execution               |
| RunnablePassthrough | Forward input unchanged          |
| RunnableAssign      | Add new fields                   |
| RunnableMap         | Multiple outputs from same input |
| RunnableBranch      | Conditional routing              |
| bind()              | Preconfigure runnable            |
| Custom Runnable     | Create your own runnable         |

### Most frequently used in real projects

```python
prompt | model | parser
```

```python
RunnableParallel(...)
```

```python
RunnablePassthrough()
```

```python
RunnableLambda(...)
```

These four cover the majority of modern LangChain applications, including chatbots, RAG systems, agents, and structured-output pipelines.
