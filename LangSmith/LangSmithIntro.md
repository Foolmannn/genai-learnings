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

Imagine you modify your prompt.< >

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

# 17. Dataset

A **dataset** is a collection of test examples.

For example:

```text
Dataset: customer_support_test

Question                         Expected Answer
-----------------------------------------------------
How do I reset my password?      Reset via Settings
What is your refund policy?      30-day refund
How do I contact support?        support@example...
```

You can use the dataset repeatedly.

```text
Dataset
   ↓
Application Version 1
   ↓
Results

Dataset
   ↓
Application Version 2
   ↓
Results
```

Then compare them.

---

# 18. Evaluation types

There are several ways to evaluate an LLM application.

## A. Exact match

Useful when the answer must exactly match something.

```text
Expected: 42
Actual:   42

→ Pass
```

---

## B. String similarity

Compare expected and actual outputs.

---

## C. LLM-as-a-judge

Another LLM evaluates the answer.

For example:

```text
Question:
What is gradient descent?

Expected:
Gradient descent is an optimization algorithm...

Actual:
Gradient descent is used to minimize a loss function...

Judge:
Score = 0.9
```

You can evaluate dimensions such as:

```text
Correctness
Relevance
Faithfulness
Helpfulness
Style
```

---

# 19. RAG evaluation

For RAG systems, you may evaluate:

```text
Retrieval quality
       ↓
Did we retrieve the right documents?

Generation quality
       ↓
Did the answer use those documents correctly?
```

For example:

```text
Question
   ↓
Retriever
   ↓
Retrieved Context
   ↓
LLM
   ↓
Answer
```

Potential metrics:

```text
Context relevance
Context recall
Answer correctness
Faithfulness
```

The exact metric names and evaluation implementations depend on your evaluation setup.

---

# 20. Online vs offline evaluation

This is another important concept.

### Offline evaluation

You test before deploying.

```text
Dataset
 ↓
Your application
 ↓
Evaluation
 ↓
Score
 ↓
Improve
 ↓
Deploy
```

### Online evaluation

You evaluate real production traffic.

```text
Real users
    ↓
Production application
    ↓
LangSmith
    ↓
Traces
    ↓
Evaluation
    ↓
Monitoring
```

---

# 21. Prompt management

Another useful capability is managing prompts.

Instead of hardcoding:

```python
prompt = """
You are a helpful assistant...
"""
```

you can treat prompts as versioned assets.

Conceptually:

```text
Prompt
│
├── v1
├── v2
├── v3
└── v4
```

Then you can determine:

```text
v1 → 72%
v2 → 78%
v3 → 84%
v4 → 81%
```

Now you know which prompt performs better.

This becomes increasingly useful as your application grows.

---

# 22. Experiments

Suppose you want to compare:

```text
Model A
vs
Model B
```

on:

```text
100 questions
```

You can evaluate both.

```text
              Dataset
                 │
       ┌─────────┴─────────┐
       ↓                   ↓
    Model A             Model B
       ↓                   ↓
    Results              Results
       │                   │
       └─────────┬─────────┘
                 ↓
             Comparison
```

You can compare things such as:

```text
Accuracy
Latency
Token usage
Cost
Quality
```

This is much better than manually testing a few prompts.

---

# 23. Production monitoring

Once your application is deployed:

```text
User
 ↓
Your API
 ↓
LangGraph
 ↓
LLM
```

you need to monitor it.

Questions include:

```text
Are requests failing?

How long are requests taking?

Are token counts increasing?

Which requests fail most often?

Which model performs better?

Are users getting poor answers?

Is one particular node causing latency?
```

LangSmith can help you monitor these execution traces and identify problematic patterns.

---

# 24. Debugging latency

Imagine:

```text
Total latency = 8 seconds
```

That's too slow.

Where did the 8 seconds go?

Tracing might show:

```text
Router          0.3 sec
Retriever       0.7 sec
LLM #1          1.8 sec
Tool            3.5 sec
LLM #2          1.7 sec
----------------------
Total           8.0 sec
```

Now you immediately know:

```text
Tool = bottleneck
```

Without tracing, you'd just know:

```text
The application is slow.
```

---

# 25. Debugging token usage

Suppose one request consumes:

```text
Input: 8,000 tokens
Output: 500 tokens
```

You might discover:

```text
Conversation history
+
Huge retrieved documents
+
Large system prompt
```

are being sent to the model.

Tracing helps you identify this.

Then you can optimize:

```text
Before:
8,500 tokens

After:
3,000 tokens
```

That can improve both latency and cost.

---

# 26. Metadata and tags

You can attach information to executions.

For example:

```text
environment = production
user_type = premium
application = chatbot
version = v2
```

You can then filter traces.

Conceptually:

```text
All traces
    │
    ├── production
    ├── development
    ├── v1
    └── v2
```

This becomes particularly useful when debugging production applications.

---

# 27. Sessions / conversations

For chat applications, a user may have:

```text
Conversation
│
├── Message 1
├── Message 2
├── Message 3
├── Message 4
└── Message 5
```

You can associate executions with a conversation/session identifier so that related interactions can be analyzed together.

This is especially useful for:

```text
Chatbots
Customer support
AI assistants
Agent applications
```

---

# 28. LangSmith + Streamlit

Since you've been building LangGraph applications with Streamlit, the architecture could be:

```text
             Streamlit
                 │
                 ↓
            LangGraph
                 │
        ┌────────┼────────┐
        ↓        ↓        ↓
       LLM      Tools    DB
        │        │        │
        └────────┼────────┘
                 ↓
             LangSmith
```

Your user sees:

```text
Streamlit UI
```

You see:

```text
LangSmith
```

for debugging and monitoring.

So LangSmith isn't really a replacement for Streamlit.

They solve completely different problems.

---

# 29. Streamlit vs LangSmith

| Streamlit               | LangSmith               |
| ----------------------- | ----------------------- |
| Builds UI               | Observes AI application |
| User-facing             | Developer-facing        |
| Chat interface          | Tracing                 |
| Forms                   | Debugging               |
| Dashboards              | Evaluation              |
| Visualization           | Monitoring              |
| Application interaction | Application analysis    |

You might use both:

```text
                User
                 ↓
             Streamlit
                 ↓
             LangGraph
                 ↓
          ┌──────┴──────┐
          ↓             ↓
         LLM           Tools
          │             │
          └──────┬──────┘
                 ↓
             LangSmith
```

---

# 30. LangSmith + LangGraph + SQLite

Since you've been learning LangGraph persistence with SQLite, there is an important distinction.

SQLite:

```text
Stores application state
```

LangSmith:

```text
Observes application execution
```

For example:

```text
              LangGraph
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
     SQLite             LangSmith
        │                   │
        ↓                   ↓
Conversation          Traces/debugging
state/history        evaluation/monitoring
```

They are **not competitors**.

You can use both.

---

# 31. SQLite vs LangSmith

Suppose your chatbot has:

```python
thread_id = "thread-123"
```

SQLite might store:

```text
thread_id
messages
state
checkpoint
```

LangSmith might record:

```text
thread_id
node execution
LLM calls
prompts
outputs
latency
metadata
errors
```

So:

```text
SQLite
→ Application persistence

LangSmith
→ Observability/evaluation
```

---

# 32. LangSmith in a real production architecture

A more realistic architecture might look like:

```text
                       User
                         │
                         ↓
                  React / Streamlit
                         │
                         ↓
                       API
                         │
                         ↓
                    LangGraph
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
       LLM           Retriever          Tools
         │               │               │
         ↓               ↓               ↓
    OpenAI/etc.       Vector DB       External APIs
                         │
                         │
                         ↓
                      Database
                         
                         │
                         ↓
                    LangSmith
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     Tracing         Evaluation       Monitoring
```

This is a very common mental model for LLM application development.

---

# 33. LangSmith development lifecycle

A good workflow is:

```text
1. Build
   ↓
2. Trace
   ↓
3. Debug
   ↓
4. Create dataset
   ↓
5. Evaluate
   ↓
6. Improve
   ↓
7. Deploy
   ↓
8. Monitor
   ↓
9. Collect failures
   ↓
10. Add failures to dataset
   ↓
11. Evaluate again
```

This creates a continuous improvement loop.

---

# 34. The most important concept: traces + datasets

If you're learning LangSmith seriously, focus first on these two concepts.

### Traces answer:

> **What happened?**

### Datasets/evaluations answer:

> **How good was it?**

Together:

```text
Trace
 ↓
Understand failure
 ↓
Create test case
 ↓
Dataset
 ↓
Evaluate improvement
 ↓
Deploy
```

---

# 35. Example: debugging your LangGraph chatbot

Imagine you have:

```python
def chatbot(state):
    response = model.invoke(state["messages"])

    return {
        "messages": [response]
    }
```

User asks:

```text
"What is LangGraph?"
```

The model responds incorrectly.

You inspect LangSmith:

```text
TRACE
│
├── chatbot
│
├── Input
│   └── What is LangGraph?
│
├── Messages
│   ├── system message
│   └── user message
│
├── LLM
│   ├── input
│   ├── output
│   ├── latency
│   └── tokens
│
└── Final output
```

You discover:

```text
System prompt accidentally says:
"Answer questions about LangChain only."
```

Problem found.

That's the value of observability.

---

# 36. Example: debugging an agent

Consider an agent:

```text
User
 ↓
Agent
 ↓
Reason
 ↓
Tool selection
 ↓
Search
 ↓
Tool result
 ↓
Reason
 ↓
Final answer
```

A trace could conceptually look like:

```text
Agent
│
├── User input
│
├── LLM
│
├── Tool call
│   └── Search
│
├── Tool result
│
├── LLM
│
└── Final answer
```

If the agent repeatedly calls a tool:

```text
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
...
```

you can identify the problem much more easily.

---

# 37. LangSmith is not just "logging"

This distinction is important.

Traditional logging:

```python
print("Calling model")
print(response)
```

gives you basic information.

LangSmith provides a much richer model:

```text
Tracing
+
Nested execution
+
Metadata
+
Inputs/outputs
+
Evaluation
+
Datasets
+
Experiments
+
Monitoring
```

So you should think of LangSmith as an **LLM application observability and evaluation platform**, rather than simply a logging library.

---

# 38. What you should learn first

Since you're already working with LangGraph, I recommend this order:

### Level 1 — Basics

Learn:

```text
What is LangSmith?
What is a project?
What is a trace?
What is a run?
```

### Level 2 — LangGraph integration

Learn:

```text
LangGraph → LangSmith
Node tracing
LLM tracing
Tool tracing
Metadata
Tags
```

### Level 3 — Debugging

Learn:

```text
Trace inspection
Errors
Latency
Token usage
Input/output inspection
```

### Level 4 — Evaluation

Learn:

```text
Datasets
Examples
Evaluators
LLM-as-judge
Experiments
Comparisons
```

### Level 5 — Production

Learn:

```text
Production tracing
Monitoring
Feedback
Online evaluation
Failure analysis
```

---

# 39. A complete mental model

Keep this picture in your head:

```text
                  LLM APPLICATION
                        │
        ┌───────────────┼────────────────┐
        │               │                │
     LangChain       LangGraph          Tools
        │               │                │
        └───────────────┼────────────────┘
                        │
                        ↓
                    LangSmith
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ↓               ↓                ↓
     Observe          Evaluate         Improve
        │               │                │
        ↓               ↓                ↓
     Traces          Datasets        Experiments
        │               │                │
        └───────────────┼────────────────┘
                        ↓
                   Better AI App
```

The simplest summary is:

> **LangChain/LangGraph tells your application what to do. LangSmith lets you see what it did, determine whether it did it well, and systematically improve it.**

