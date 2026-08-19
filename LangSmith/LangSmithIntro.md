# LangSmith — Why, How, and More in Detail

> **LangChain/LangGraph builds your AI application; LangSmith helps you observe, debug, evaluate, test, and improve it.**

---

# 1. What is LangSmith?

**LangSmith** is an observability, debugging, evaluation, and monitoring platform for LLM applications.

When you build an application like:

```text
User
  ↓
Streamlit UI
  ↓
LangGraph
  ↓
Prompt
  ↓
LLM
  ↓
Tools / Retriever / Database
  ↓
Response
```

a lot can happen internally.

Without LangSmith, you may only see:

```text
User: What is RAG?

AI: RAG is...
```

But you don't necessarily know:

* Which prompt was actually sent?
* Which model was called?
* What was the model's response?
* How long did it take?
* How many tokens were used?
* Which LangGraph node executed?
* Which tool was called?
* What happened before an error?
* Why did the model produce a bad answer?
* Which version of your prompt produced better results?
* How does your application perform across 100 test questions?

LangSmith gives you visibility into those things.

---

# 2. Why do we need LangSmith?

Consider a simple chatbot:

```python
response = model.invoke(
    "Explain machine learning"
)

print(response.content)
```

It works.

But imagine the user says:

> "Your chatbot gave me a completely wrong answer."

Now you need to investigate.

You might ask:

### Was the prompt wrong?

```text
System prompt
     ↓
User prompt
     ↓
Final prompt
```

### Was the retrieved context wrong?

```text
Question
   ↓
Retriever
   ↓
Documents
   ↓
LLM
```

### Did the wrong LangGraph node execute?

```text
START
 ↓
classifier
 ↓
retriever
 ↓
generator
 ↓
END
```

### Did the LLM hallucinate?

### Did the model return malformed structured output?

### Did a tool fail?

### Did the database return incorrect data?

Without tracing, debugging becomes difficult.

With LangSmith:

```text
Trace
│
├── Graph
│   ├── classifier
│   ├── retriever
│   │   └── vector search
│   └── generator
│       └── LLM
│
└── Final Response
```

You can inspect the entire execution.

---

# 3. The main purposes of LangSmith

There are four major areas to understand:

```text
                 LangSmith
                    │
       ┌────────────┼────────────┐
       ↓            ↓            ↓
 Observability   Evaluation    Testing
       │            │            │
       └────────────┼────────────┘
                    ↓
               Monitoring
```

More practically:

| Feature           | Purpose                       |
| ----------------- | ----------------------------- |
| Tracing           | See what happened             |
| Debugging         | Find why it happened          |
| Evaluation        | Measure how good it is        |
| Datasets          | Create test cases             |
| Monitoring        | Watch production applications |
| Prompt management | Manage/version prompts        |
| Experiments       | Compare different approaches  |

---

# 4. LangSmith architecture

A simplified architecture looks like this:

```text
                 Your Application
                       │
            ┌──────────┴──────────┐
            │                     │
       LangChain              LangGraph
            │                     │
            └──────────┬──────────┘
                       │
                    Traces
                       │
                       ↓
                  LangSmith
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Tracing     Evaluation    Monitoring
          │            │            │
          └────────────┼────────────┘
                       ↓
                    Insights
```

Your application executes locally or on a server.

LangSmith receives telemetry about those executions.

---

# 5. What is a Trace?

This is one of the **most important concepts**.

A **trace** represents one execution of your application.

For example:

```text
User asks:
"What is gradient descent?"
```

Your application might execute:

```text
Trace
│
├── Chatbot
│
├── Prompt
│
├── OpenAI model
│
└── Response
```

For a more complicated RAG application:

```text
Trace
│
├── User Input
│
├── Query Rewriting
│
├── Retriever
│   ├── Document 1
│   ├── Document 2
│   └── Document 3
│
├── Prompt Construction
│
├── LLM
│
└── Final Answer
```

For LangGraph:

```text
Trace
│
├── START
│
├── classify_question
│
├── retrieve_documents
│
├── generate_answer
│
├── validate_answer
│
└── END
```

This is extremely useful for debugging.

---

# 6. Trace vs Run

You will often encounter these terms.

A **run** generally represents one individual execution of a component.

For example:

```text
Trace
│
├── Run: classifier
├── Run: retriever
├── Run: LLM
└── Run: validator
```

So you can think:

```text
Trace
   =
Complete execution

Run
   =
Individual execution inside it
```

---

# 7. What information can a trace contain?

Depending on your application and configuration, you can inspect things such as:

### Input

```text
What is RAG?
```

### Output

```text
RAG stands for Retrieval-Augmented Generation...
```

### Prompt

```text
You are an AI assistant...

Context:
...

Question:
...
```

### Model

```text
GPT model
```

### Token usage

```text
Input tokens
Output tokens
Total tokens
```

### Latency

```text
2.34 seconds
```

### Errors

```text
Tool execution failed
```

### Metadata

```text
model = ...
temperature = ...
environment = production
```

This makes troubleshooting much easier.

---

# 8. Setting up LangSmith

First, create a LangSmith account and create an API key/project through the LangSmith interface.

Then configure your application with environment variables.

A typical setup looks like:

```text
LANGSMITH_API_KEY=your_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=my-project
```

Depending on the SDK/version you're using, the exact environment variable names and configuration options can evolve, so check the current LangSmith documentation when setting up a new project.

---

# 9. Installing LangSmith

For Python:

```bash
pip install -U langsmith
```

If you're already working with LangChain/LangGraph, you may already have much of the required integration dependencies.

For example:

```bash
pip install -U langchain langgraph langsmith
```

---

# 10. Basic LangChain example

Suppose you have:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="..."
)

response = model.invoke(
    "Explain gradient descent"
)

print(response.content)
```

After configuring LangSmith tracing, the execution can appear in LangSmith roughly as:

```text
my-project
│
└── ChatOpenAI
      │
      ├── Input
      ├── Prompt
      ├── Model
      ├── Output
      ├── Tokens
      └── Latency
```

You don't normally have to manually write logging code around every LangChain operation.

That is one of the major advantages of the integration.

---

# 11. LangSmith with LangGraph

This is particularly important for what you've been learning.

Suppose you have:

```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(State)

graph.add_node("classifier", classifier)
graph.add_node("retriever", retriever)
graph.add_node("generator", generator)

graph.add_edge(START, "classifier")
graph.add_edge("classifier", "retriever")
graph.add_edge("retriever", "generator")
graph.add_edge("generator", END)

app = graph.compile()
```

When you execute:

```python
result = app.invoke({
    "messages": [...]
})
```

LangSmith can give you visibility into the execution.

Conceptually:

```text
                    Trace
                      │
                    Graph
                      │
              ┌───────┴────────┐
              ↓                ↓
         classifier        metadata
              │
              ↓
          retriever
              │
              ↓
          generator
              │
              ↓
             END
```

And inside `generator`:

```text
generator
    │
    └── LLM call
          │
          ├── input
          ├── output
          ├── latency
          └── token usage
```

This is extremely valuable when your LangGraph becomes complicated.

---

# 12. Why LangSmith is especially useful with LangGraph

Imagine your graph:

```text
START
  ↓
router
  ↓
 ┌───────────────┐
 │               │
 ↓               ↓
RAG             SQL
 │               │
 ↓               ↓
validator     validator
 │               │
 └───────┬───────┘
         ↓
       answer
         ↓
        END
```

Suppose the chatbot gives a bad SQL answer.

You can inspect:

```text
Trace
│
├── router
│    └── selected: SQL
│
├── SQL node
│    └── generated query
│
├── database
│    └── returned rows
│
├── validator
│    └── rejected/accepted
│
└── answer
```

Now you can determine exactly where the problem occurred.

---

# 13. LangSmith for debugging

Consider:

```python
def generate_answer(state):
    response = model.invoke(state["messages"])

    state["answer"] = response.content

    return state
```

Suppose the output is incorrect.

Without tracing:

```text
Something is wrong with the model.
```

With tracing:

```text
Input
 ↓
System prompt
 ↓
Conversation history
 ↓
Retrieved documents
 ↓
Final prompt
 ↓
Model
 ↓
Output
```

You might discover:

```text
Problem:
Retriever returned irrelevant documents.
```

So the problem wasn't the LLM.

It was retrieval.

This distinction is extremely important when building production RAG systems.

---

# 14. Debugging RAG applications

RAG is one of the best examples.

Your architecture:

```text
Question
   ↓
Embedding
   ↓
Vector DB
   ↓
Top K documents
   ↓
Prompt
   ↓
LLM
   ↓
Answer
```

Suppose:

> User: "What is the refund policy?"

AI:

> "Refunds are available for 90 days."

But your actual policy says 30 days.

You need to investigate.

LangSmith can help you inspect:

```text
Question
   ↓
Retriever
   ↓
Document 1
Document 2
Document 3
   ↓
Prompt
   ↓
LLM
   ↓
Wrong Answer
```

You might discover:

```text
Retriever problem
```

because it retrieved an outdated document.

Or:

```text
Prompt problem
```

because the prompt didn't tell the model to prioritize the supplied context.

Or:

```text
Generation problem
```

because the correct context was retrieved but the model still produced an incorrect answer.

---

# 15. Evaluation

Tracing answers:

> **What happened?**

Evaluation answers:

> **Was it good?**

This distinction is fundamental.

Suppose you have:

```text
100 questions
```

Your chatbot generates:

```text
100 answers
```

You want to know:

```text
How good are those answers?
```

LangSmith provides evaluation workflows for this.

---

# 16. Why evaluation is necessary

Imagine you modify your prompt.

### Version 1

```text
Answer the question.
```

Accuracy:

```text
78%
```

Then you improve it:

```text
Answer only using the supplied context.
If the context doesn't contain the answer, say you don't know.
```

Accuracy:

```text
86%
```

You want to know whether the change actually improved the system.

That's where evaluation becomes important.

---
