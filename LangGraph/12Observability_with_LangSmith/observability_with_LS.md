# Observability in LangGraph with LangSmith — In Detail

When you build a LangGraph application, especially an agent with multiple nodes, tools, LLM calls, retries, loops, and state transitions, simply looking at the final answer is **not enough**.

You need to know:

* Which nodes executed?
* In what order?
* What state entered each node?
* What did the LLM receive?
* What did the LLM return?
* Which tools were called?
* How long did each operation take?
* How many tokens were consumed?
* What did the user actually ask?
* Where did an error occur?
* Why did the agent choose a particular path?
* Which version of your prompt/model produced a bad result?

This is where **LangSmith Observability** becomes extremely useful.

---

# 1. What is Observability?

In simple terms:

> **Observability is the ability to understand what happened inside your application by examining its execution traces, inputs, outputs, errors, timing, and metadata.**

For a normal Python function:

```text
Input
  ↓
Function
  ↓
Output
```

You can usually debug this easily.

But a LangGraph application might look like:

```text
User
 ↓
START
 ↓
Router
 ↓
 ├── Search Node
 │      ↓
 │    Search Tool
 │      ↓
 │    LLM
 │
 └── Calculator Node
        ↓
      Calculator Tool
        ↓
        LLM
 ↓
Answer Generator
 ↓
END
```

There can be dozens or hundreds of operations in one request.

Without observability:

```text
User: "What is the weather in Kathmandu?"

Agent:
"I couldn't answer that."
```

You don't know **why**.

With observability:

```text
Trace
 ├── Agent
 │    ├── LLM call
 │    ├── Tool: weather
 │    ├── Tool response
 │    ├── LLM call
 │    └── Final response
```

Now you can inspect exactly what happened.

---

# 2. LangSmith's Role

Think of the ecosystem like this:

```text
                 Your Application
                       │
                       ▼
                  LangGraph
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Node          Node         Node
          │            │            │
        LLM           Tool         LLM
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
                  LangSmith
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Traces       Metrics       Errors
          │            │            │
          ▼            ▼            ▼
     Debugging    Monitoring    Evaluation
```

**LangGraph executes the workflow.**

**LangSmith observes the workflow.**

That's the key relationship.

---

# 3. What is a Trace?

A **trace** represents one execution of your application.

For example:

```text
User asks:

"What is the weather in Kathmandu?"
```

One trace might contain:

```text
Trace
│
├── LangGraph
│
├── Agent Node
│   └── ChatOpenAI
│
├── Tool Node
│   └── Weather API
│
├── Agent Node
│   └── ChatOpenAI
│
└── Final Response
```

Each individual operation is generally represented as a **run/span** within the overall execution.

---

# 4. Trace vs Run

This distinction is important.

Imagine:

```text
User Request
     │
     ▼
   Trace
     │
     ├── LLM Run
     │
     ├── Tool Run
     │
     ├── LLM Run
     │
     └── Node Run
```

A **trace** gives you the overall execution.

Individual **runs** represent particular operations.

For example:

```text
Trace ID:
abc123

Runs:

1. graph
2. router
3. ChatOpenAI
4. weather_tool
5. ChatOpenAI
6. final_node
```

This hierarchical structure is extremely useful when debugging agents.

---

# 5. LangGraph + LangSmith

Suppose you have:

```python
from typing import TypedDict

class State(TypedDict):
    question: str
    answer: str
```

And your graph is:

```text
START
  ↓
LLM
  ↓
END
```

Conceptually:

```python
def llm_node(state):
    response = model.invoke(state["question"])

    return {
        "answer": response.content
    }
```

When LangSmith tracing is enabled, the execution can become visible as:

```text
Graph
│
└── llm_node
      │
      └── ChatOpenAI
            │
            ├── Input
            ├── Output
            ├── Tokens
            ├── Latency
            └── Metadata
```

You don't have to manually print everything.

---

# 6. Enabling LangSmith Tracing

The common setup uses environment variables.

For example:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=my-langgraph-project
```

Depending on the LangSmith/LangChain version you're using, environment variable names and setup recommendations can evolve, so it's worth checking the current LangSmith documentation before deploying.

Then your application can run normally.

For example:

```python
graph.invoke(
    {
        "question": "What is machine learning?"
    }
)
```

The execution can be sent to LangSmith automatically.

---

# 7. Why Automatic Tracing Is Powerful

Imagine your graph has:

```text
START
 ↓
classify
 ↓
 ┌──────────────┐
 │              │
 ▼              ▼
search        calculate
 │              │
 ▼              ▼
summarize     explain
 │              │
 └──────┬───────┘
        ▼
       END
```

Without observability, debugging requires adding:

```python
print(...)
```

everywhere.

For example:

```python
print("Entering search node")
print(state)
print(response)
print("Leaving search node")
```

This becomes messy very quickly.

LangSmith gives you structured execution information instead.

---

# 8. What Can You Observe?

There are several important categories.

## 8.1 Inputs

You can inspect what entered a component.

Example:

```text
Node: search_node

Input:
{
    "question": "Who won the World Cup?"
}
```

This helps answer:

> Did my node receive the state I expected?

---

# 9. Outputs

You can inspect what came out.

```text
Output:

{
    "documents": [...],
    "answer": "..."
}
```

This helps determine whether the problem happened:

```text
before the node
       ↓
inside the node
       ↓
after the node
```

---

# 10. LLM Observability

One of the most useful parts of LangSmith is inspecting LLM calls.

Suppose:

```python
response = model.invoke(messages)
```

You can inspect things such as:

```text
Model:
GPT model

Input:
system message
+
user message

Output:
assistant response

Token usage:
input tokens
output tokens
total tokens

Latency:
1.42 seconds
```

This is extremely useful when working with agents.

---

# 11. Prompt Debugging

Suppose your chatbot suddenly starts giving poor answers.

You might think:

> The model is bad.

But the trace might reveal:

```text
System Prompt:
"You are a helpful assistant."

User:
"Explain PCA."

Previous messages:
...
```

Maybe your intended system prompt was:

```text
You are an expert machine learning tutor.
Explain concepts with mathematical intuition and examples.
```

The trace lets you inspect what was **actually sent** to the model rather than what you think your code sent.

---

# 12. Tool Observability

This becomes even more important with agents.

Suppose you have:

```python
@tool
def get_weather(city: str):
    ...
```

Your agent might produce:

```text
Agent
 ↓
Tool Call
 ↓
get_weather
 ↓
API
 ↓
Tool Result
 ↓
Agent
```

LangSmith can help you inspect:

```text
Tool:
get_weather

Input:
Kathmandu

Output:
27°C, cloudy

Latency:
0.72 sec
```

You can therefore determine whether an incorrect final answer came from:

```text
LLM reasoning
       OR
tool selection
       OR
tool implementation
       OR
tool result
```

---

# 13. LangGraph State Observability

This is especially important for LangGraph.

Suppose:

```python
class State(TypedDict):
    messages: list
    query: str
    documents: list
    answer: str
```

Your graph:

```text
START
 ↓
retrieve
 ↓
generate
 ↓
validate
 ↓
END
```

You may have:

```text
Initial State

{
    query: "...",
    documents: [],
    answer: ""
}
```

After retrieval:

```text
{
    query: "...",
    documents: ["doc1", "doc2"],
    answer: ""
}
```

After generation:

```text
{
    query: "...",
    documents: ["doc1", "doc2"],
    answer: "..."
}
```

This makes state-related bugs much easier to understand.

---

# 14. Observing Conditional Edges

LangGraph frequently uses conditional routing.

For example:

```python
def router(state):
    if state["needs_search"]:
        return "search"

    return "answer"
```

Graph:

```text
             Router
            /      \
           /        \
       Search      Answer
          \          /
           \        /
             END
```

Suppose the wrong branch executes.

Without tracing:

```text
Why did it go to Search?
```

With observability you can inspect:

```text
Router input:
needs_search = True

Decision:
search
```

You can then determine whether the problem is:

* state generation
* router logic
* classification LLM
* conditional edge configuration

---

# 15. Observing Loops

LangGraph can create iterative workflows:

```text
Generate
   ↓
Evaluate
   ↓
Good?
 ┌─┴─┐
No  Yes
│    │
▼    ▼
Improve END
│
└──→ Generate
```

This is difficult to debug manually.

LangSmith can make the execution hierarchy visible:

```text
Graph
│
├── Generate
├── Evaluate
├── Improve
├── Generate
├── Evaluate
├── Improve
├── Generate
├── Evaluate
└── END
```

You can immediately see:

> Why did my agent loop three times?

or:

> Why did it never reach END?

---

# 16. Latency Observability

Suppose your application takes:

```text
Total: 8.5 seconds
```

That's not enough information.

LangSmith can help break it down:

```text
Total
│
├── Router LLM       1.2s
├── Search API       3.4s
├── Tool             0.8s
├── LLM              2.1s
└── Formatting       1.0s
```

Now you know where the bottleneck is.

Maybe the problem isn't the LLM.

Maybe:

```text
Search API = 3.4 seconds
```

is responsible for most of your latency.

---

# 17. Token Usage

LLM applications can become expensive.

Suppose one request produces:

```text
Input tokens: 4,000
Output tokens: 1,000
Total: 5,000
```

But your LangGraph has multiple LLM calls:

```text
Router:
2,000 tokens

Retriever:
1,000 tokens

Generator:
5,000 tokens

Evaluator:
3,000 tokens

Total:
11,000 tokens
```

Observability allows you to understand where token usage is occurring.

This is particularly useful for:

* cost optimization
* prompt optimization
* reducing unnecessary calls
* choosing models
* detecting unexpectedly large contexts

---

# 18. Error Observability

Suppose this happens:

```python
response = model.invoke(messages)
```

and the model/API throws an error.

Instead of only seeing:

```text
500 Internal Server Error
```

you want to know:

```text
Graph
 ↓
agent_node
 ↓
LLM
 ↓
ERROR

Error:
RateLimitError
```

You can then inspect:

```text
Input
Model
Node
Timestamp
Metadata
Error
Execution path
```

This makes production debugging dramatically easier.

---

# 19. Metadata

Metadata is another powerful feature.

You can associate information with traces such as:

```text
user_id
session_id
environment
model
version
feature
application version
```

For example:

```text
Trace

Project:
production

Environment:
prod

User:
123

Session:
abc

Graph version:
v2.4

Model:
...
```

Then you can investigate questions like:

> Are errors happening only in production?

or:

> Are users using version 2.4 experiencing more failures?

---

# 20. Tags

Tags help organize traces.

For example:

```text
tags:
["production", "rag", "customer-support"]
```

or:

```text
["development", "agent"]
```

You can then filter traces based on those attributes.

A useful strategy is:

```text
environment:
dev
staging
production
```

and:

```text
workflow:
rag
chatbot
research-agent
```

---

# 21. Projects

You can separate applications using projects.

For example:

```text
LangSmith
│
├── meroHisab-ai
├── research-agent
├── customer-support
└── development
```

A project can contain many traces belonging to the same application/workflow.

This becomes particularly useful when you have multiple applications.

---

# 22. Sessions / Conversations

For conversational applications, you often want to group multiple turns.

For example:

```text
Conversation
│
├── User: What is LangGraph?
│
├── Assistant: ...
│
├── User: How does persistence work?
│
└── Assistant: ...
```

The individual requests can be associated with the same conversation/thread context.

This is especially useful for LangGraph applications using:

```python
thread_id
```

because LangGraph persistence and LangSmith tracing answer somewhat different questions:

```text
LangGraph persistence
        ↓
"What state should my application remember?"

LangSmith observability
        ↓
"What happened while my application ran?"
```

That's a very important distinction.

---

# 23. Persistence vs Observability

Don't confuse them.

### Persistence

Used to preserve application state.

```text
User
 ↓
Graph
 ↓
Checkpoint
 ↓
Database
```

Example:

```text
thread_id = "123"
```

The graph can resume conversation state.

### Observability

Used to understand execution.

```text
User
 ↓
Graph
 ↓
LangSmith
 ↓
Trace
```

So:

```text
Persistence ≠ Observability
```

They complement each other.

---
