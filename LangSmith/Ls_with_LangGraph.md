# LangSmith with LangGraph — Detailed Guide

If you're learning **LangGraph**, then **LangSmith** is one of the most useful tools to learn alongside it.

A simple way to think about the relationship is:

> **LangGraph = builds and runs your agent/workflow**
> **LangSmith = observes, debugs, evaluates, and monitors that workflow**

They solve different problems but work extremely well together.

---

# 1. What is LangSmith?

LangSmith is a platform for developing and monitoring LLM applications.

When you build a LangGraph application, many things can happen:

```text
User
  ↓
LangGraph
  ↓
Agent Node
  ↓
LLM
  ↓
Tool
  ↓
Another Node
  ↓
LLM
  ↓
Final Answer
```

If something goes wrong, you might wonder:

* Which node caused the problem?
* What prompt was sent to the LLM?
* What did the LLM return?
* Which tools were called?
* What arguments were passed to the tool?
* How long did each step take?
* How many tokens were used?
* How much did the execution cost?
* Why did the agent take the wrong path?

Without observability, debugging this can become painful.

LangSmith gives you visibility into these executions.

---

# 2. LangGraph vs LangSmith

This distinction is extremely important.

| LangGraph               | LangSmith                  |
| ----------------------- | -------------------------- |
| Builds workflows        | Observes workflows         |
| Manages state           | Records executions         |
| Creates nodes           | Shows node executions      |
| Creates edges           | Shows execution paths      |
| Controls agent behavior | Helps debug agent behavior |
| Handles persistence     | Helps inspect runs         |
| Executes tools          | Shows tool calls           |
| Implements workflows    | Evaluates workflows        |

Think about a normal application:

```text
React
  ↓
Frontend application

Database
  ↓
Data storage

Logging/Monitoring
  ↓
Observability
```

Similarly:

```text
LangGraph
  ↓
Agent/workflow

LangSmith
  ↓
Observability/debugging/evaluation
```

---

# 3. Why LangSmith becomes especially useful with LangGraph

A simple LangChain call might look like:

```text
User → LLM → Response
```

But a LangGraph application can look like:

```text
                    ┌──────────────┐
                    │   LLM Node   │
                    └──────┬───────┘
                           ↓
                      Condition
                       /      \
                      /        \
                     ↓          ↓
               Search Tool    Calculator
                     \          /
                      \        /
                       ↓      ↓
                       └──┬───┘
                          ↓
                    Final Response
```

There may be dozens of executions.

LangSmith lets you inspect this execution as a **trace**.

---

# 4. What is tracing?

Tracing means recording what happened during an execution.

Suppose you have:

```python
graph.invoke({
    "messages": [
        ("user", "What is the weather in Kathmandu?")
    ]
})
```

Your LangGraph might execute:

```text
START
 ↓
agent
 ↓
weather_tool
 ↓
agent
 ↓
END
```

LangSmith can capture something conceptually like:

```text
Trace
│
├── agent
│   ├── input
│   ├── prompt
│   ├── LLM request
│   └── LLM response
│
├── weather_tool
│   ├── input
│   └── output
│
└── agent
    ├── input
    ├── LLM request
    └── final response
```

This is incredibly useful when debugging.

---

# 5. Important LangSmith concepts

You should understand these terms:

### 1. Traces

A trace represents an entire execution.

Example:

```text
User asks:
"What is the weather in Kathmandu?"
```

One complete execution can be represented as a trace.

---

### 2. Runs

A trace contains individual runs.

For example:

```text
Trace
│
├── LLM run
├── Tool run
├── LLM run
└── Graph run
```

A run represents an individual operation.

---

### 3. Projects

Projects allow you to organize runs.

For example:

```text
LangSmith
│
├── development
├── production
└── testing
```

You might have:

```text
Project: mero-agent-dev
```

for development executions.

---

### 4. Datasets

Datasets contain examples used for testing/evaluation.

For example:

```text
Input                          Expected Output
------------------------------------------------
"2 + 2"                         "4"
"Weather in Kathmandu?"         correct weather response
"Who is Einstein?"              correct explanation
```

You can run your application against these examples.

---

### 5. Evaluators

Evaluators determine whether the output is good.

For example:

```text
Input:
"What is 10 + 20?"

Output:
"30"

Evaluator:
Correct → 1
```

Or:

```text
Answer relevance = 0.95
```

---

# 6. Setting up LangSmith

You generally need a LangSmith account and API key.

The usual environment variables are:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_api_key
LANGSMITH_PROJECT=my-langgraph-project
```

Depending on your setup, you may also specify the LangSmith endpoint:

```env
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

Keep the key in `.env`, not directly in your Python source.

For example:

```env
OPENAI_API_KEY=...
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=langgraph-learning
```

Then:

```python
from dotenv import load_dotenv

load_dotenv()
```

Your LangChain/LangGraph application can then send tracing information to LangSmith.

---

# 7. Basic LangGraph + LangSmith example

Suppose you have a simple LangGraph application.

```python
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def hello_node(state: State):
    return {
        "message": state["message"] + " Hello!"
    }


graph_builder = StateGraph(State)

graph_builder.add_node("hello", hello_node)

graph_builder.add_edge(START, "hello")
graph_builder.add_edge("hello", END)

graph = graph_builder.compile()
```

Now invoke:

```python
result = graph.invoke({
    "message": "Hi"
})

print(result)
```

Output:

```python
{
    "message": "Hi Hello!"
}
```

If LangSmith tracing is configured, this execution can appear in your LangSmith project.

---

# 8. LangGraph execution inside LangSmith

Imagine this graph:

```text
START
  ↓
get_user
  ↓
generate_answer
  ↓
END
```

LangSmith can show something similar to:

```text
Trace
│
├── LangGraph
│
├── get_user
│
└── generate_answer
```

You can inspect each step.

For example:

```text
get_user

Input:
{
    "user_id": 123
}

Output:
{
    "name": "Suman",
    "age": 21
}
```

Then:

```text
generate_answer

Input:
{
    "name": "Suman",
    "age": 21
}

Output:
"Hello Suman!"
```

---

# 9. Debugging LangGraph with LangSmith

This is probably the biggest reason to use it.

Suppose your graph is:

```text
START
 ↓
classifier
 ↓
 ┌───────────────┐
 │               │
 ↓               ↓
search          math
 │               │
 └───────┬───────┘
         ↓
       answer
         ↓
        END
```

The user asks:

```text
"What is 25 × 30?"
```

But your classifier incorrectly chooses:

```text
search
```

Without LangSmith:

```text
Why did my agent search the internet?
```

With LangSmith:

```text
Trace
│
├── classifier
│     Input:
│     "What is 25 × 30?"
│
│     Output:
│     "search"
│
└── search
```

Now you know the problem is the classifier.

You can inspect its prompt and output.

---

# 10. Debugging prompts

Suppose you have:

```python
prompt = """
You are an intelligent assistant.

Determine whether the user wants:
- math
- search
"""
```

The LLM might return:

```text
search
```

when you expected:

```text
math
```

LangSmith allows you to inspect the actual execution and understand what the model received and produced.

This is much better than putting:

```python
print(prompt)
print(response)
```

everywhere.

---

# 11. Debugging tool calls

Suppose your LangGraph agent has:

```python
@tool
def get_weather(city: str):
    ...
```

The user asks:

```text
What's the weather in Kathmandu?
```

The agent may call:

```text
get_weather(
    city="Kathmandu"
)
```

LangSmith can show the tool execution.

If something goes wrong:

```text
get_weather(
    city="Kathmandu Nepal"
)
```

you can see exactly what the model generated.

This is especially useful with agents.

---

# 12. LangGraph state + LangSmith

One of the most useful aspects for your current LangGraph learning is understanding **state transitions**.

Suppose:

```python
class State(TypedDict):
    messages: list
    query_type: str
    result: str
```

Your graph:

```text
START
 ↓
classify
 ↓
search
 ↓
generate
 ↓
END
```

State might evolve like this:

### Initial state

```python
{
    "messages": [...],
    "query_type": "",
    "result": ""
}
```

### After classify

```python
{
    "messages": [...],
    "query_type": "search",
    "result": ""
}
```

### After search

```python
{
    "messages": [...],
    "query_type": "search",
    "result": "Search results..."
}
```

### After generate

```python
{
    "messages": [...],
    "query_type": "search",
    "result": "Final answer..."
}
```

Tracing helps you understand these executions while debugging your graph.

---

# 13. LangSmith and conditional edges

Suppose:

```python
def route(state):
    if state["query_type"] == "math":
        return "math"

    return "search"
```

Graph:

```text
             classify
                ↓
             route()
            /      \
           /        \
        math       search
          \          /
           \        /
            answer
```

Suppose the wrong branch is executed.

LangSmith helps you inspect:

```text
classify
    ↓
query_type = "search"
    ↓
route
    ↓
search
```

So you can determine whether the problem was:

```text
LLM classification
        OR
routing function
        OR
state update
```

This is extremely useful in complex LangGraph applications.

---

# 14. Streaming + LangSmith

You have also been working with LangGraph streaming.

For example:

```python
for chunk in graph.stream(
    input,
    stream_mode="updates"
):
    print(chunk)
```

or:

```python
for chunk in graph.stream(
    input,
    stream_mode="messages"
):
    print(chunk)
```

LangSmith can still trace the underlying execution.

Your application might stream:

```text
Hello
```

then:

```text
How
```

then:

```text
are
```

then:

```text
you?
```

while LangSmith records the execution behind that generation.

So:

```text
Streamlit
    ↓
LangGraph
    ↓
LLM
    ↓
LangSmith
```

LangSmith isn't replacing streaming; it provides observability for the application.

---

# 15. Thread IDs and LangSmith

This is especially relevant to the LangGraph persistence work you've been doing.

Suppose you invoke:

```python
config = {
    "configurable": {
        "thread_id": "thread-123"
    }
}
```

and:

```python
graph.invoke(
    input,
    config=config
)
```

LangGraph uses the thread ID for things like:

```text
conversation 1
conversation 2
conversation 3
```

LangSmith can help you inspect executions associated with those application runs.

This becomes very useful for debugging conversational agents.

---

# 16. LangGraph persistence vs LangSmith

Don't confuse these.

### LangGraph persistence

Used to store application state.

For example:

```text
Thread 123
 ↓
Messages
 ↓
State
 ↓
Checkpoint
```

A database/checkpointer might store it.

Examples include:

```text
SQLite
PostgreSQL
Redis
```

### LangSmith

Used to observe/debug/evaluate executions.

```text
Application
   ↓
Execution
   ↓
Trace
   ↓
LangSmith
```

Therefore:

```text
SQLite
   ↓
Stores your application's state

LangSmith
   ↓
Observes your application's execution
```

They can be used together.

---

# 17. LangGraph + SQLite + LangSmith

This is a very useful architecture to understand.

```text
                  User
                   ↓
                Streamlit
                   ↓
                LangGraph
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
    SQLite                LangSmith
        ↓                     ↓
Application state       Traces / Logs
```

For example:

```text
SQLite
→ conversation checkpoints
→ thread state
→ message history
```

while LangSmith:

```text
→ prompts
→ LLM calls
→ tool calls
→ latency
→ tokens
→ errors
→ traces
→ evaluations
```

---

# 18. LangSmith for production

Once your application becomes larger:

```text
User
 ↓
Frontend
 ↓
Backend
 ↓
LangGraph
 ↓
LLM
 ↓
Tools
```

you need to know whether it works reliably.

Suppose users report:

> "The chatbot sometimes gives bad answers."

You can inspect traces.

Maybe you discover:

```text
100 requests

95 → successful
3  → tool error
2  → LLM hallucination
```

You can then investigate the problematic runs.

---

# 19. Latency monitoring

Suppose your graph:

```text
Node A → 1.2 sec
Node B → 5.8 sec
Node C → 0.7 sec
```

Total:

```text
7.7 seconds
```

LangSmith tracing helps identify where time is being spent.

Maybe:

```text
LLM call = 5.2 seconds
```

Then optimizing your Python code won't help much.

You may instead need to:

* use a faster model
* reduce prompt size
* reduce unnecessary LLM calls
* parallelize independent work
* cache results

---

# 20. Token usage

LLM applications cost money.

Suppose one graph execution does:

```text
LLM #1
   ↓
2,000 tokens

LLM #2
   ↓
3,000 tokens

LLM #3
   ↓
2,500 tokens
```

Total:

```text
7,500 tokens
```

With many users:

```text
7,500 × 10,000 requests
```

can become expensive.

Tracing helps you understand where token consumption is happening.

---

# 21. Errors and exceptions

Suppose:

```python
@tool
def search_database(query):
    ...
```

throws:

```text
DatabaseConnectionError
```

Your graph may terminate unexpectedly.

Instead of guessing what happened, you can inspect the execution:

```text
Trace
│
├── agent
│
├── search_database
│     └── ERROR
│
└── graph
      └── FAILED
```

This makes debugging much easier.

---

# 22. Evaluation

This is where LangSmith becomes more than a logging system.

Suppose you're building a RAG application.

You have:

```text
Question
 ↓
Retriever
 ↓
Documents
 ↓
LLM
 ↓
Answer
```

You might have 100 test questions:

```text
Question 1
Question 2
Question 3
...
Question 100
```

You want to know:

> Is my application actually getting better?

You can create a dataset and evaluate different versions.

For example:

```text
                  Accuracy
Version A          72%
Version B          81%
Version C          87%
```

Now you have evidence that your changes improved the application.

---

# 23. Dataset

Imagine you're building a chatbot.

Create test examples:

```text
Input:
"What is LangGraph?"

Expected:
"LangGraph is a framework for building stateful..."

Input:
"What is LangSmith?"

Expected:
"LangSmith is used for..."

Input:
"What is a LangGraph node?"

Expected:
"A node represents..."
```

This becomes your evaluation dataset.

Then you can test your application against those examples.

---

# 24. Why evaluation matters

Imagine you modify your prompt.

Before:

```text
Accuracy = 87%
```

After:

```text
Accuracy = 82%
```

Your prompt looked better, but performance actually got worse.

Without evaluation, you may deploy it.

With evaluation:

```text
Old prompt → 87%
New prompt → 82%
```

You know to reject the change.

---

# 25. LLM-as-a-judge

For many LLM applications, exact string comparison isn't enough.

For example:

Expected:

```text
Paris is the capital of France.
```

Actual:

```text
The capital city of France is Paris.
```

These are different strings but essentially the same answer.

An LLM evaluator can judge:

```text
Correctness:
0.98
```

or:

```text
Relevant: YES
```

This is called **LLM-as-a-judge**.

---

# 26. LangSmith and RAG

LangSmith becomes particularly useful with RAG.

Typical architecture:

```text
User question
      ↓
Retriever
      ↓
Documents
      ↓
Prompt
      ↓
LLM
      ↓
Answer
```

Suppose the answer is wrong.

There are many possible causes:

```text
Wrong query
    ↓
Wrong documents
    ↓
Bad chunking
    ↓
Bad prompt
    ↓
LLM failure
```

LangSmith tracing helps you inspect the whole chain.

You can see:

```text
Question
   ↓
Retriever
   ↓
Retrieved documents
   ↓
Prompt
   ↓
LLM
   ↓
Answer
```

This is much easier than debugging blindly.

---

# 27. LangSmith and agents

This is perhaps the most powerful combination.

Suppose your LangGraph agent has:

```text
          User
            ↓
          Agent
         /  |  \
        /   |   \
       ↓    ↓    ↓
   Search  Math  Weather
       \    |    /
        \   |   /
          Agent
            ↓
          Answer
```

The agent might make multiple decisions:

```text
Thought/decision
 ↓
Tool call
 ↓
Tool result
 ↓
Decision
 ↓
Tool call
 ↓
Final answer
```

LangSmith allows you to inspect this execution.

---

# 28. A practical project architecture

Since you're learning LangGraph + Streamlit, a good architecture would be:

```text
project/
│
├── app.py
│
├── graph/
│   ├── state.py
│   ├── nodes.py
│   ├── edges.py
│   └── graph.py
│
├── tools/
│   ├── search.py
│   └── weather.py
│
├── database/
│   └── sqlite.py
│
├── .env
│
└── requirements.txt
```

`.env`:

```env
OPENAI_API_KEY=...
LANGSMITH_API_KEY=...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=my-langgraph-agent
```

Architecture:

```text
                 Streamlit
                     ↓
                  graph
                     ↓
        ┌────────────┼────────────┐
        ↓            ↓            ↓
      Agent        Tools       Database
        ↓            ↓            ↓
       LLM         APIs         SQLite
        │
        └──────────────┐
                       ↓
                   LangSmith
```

---

# 29. Development workflow I recommend

When building a LangGraph application, use this workflow:

### Step 1 — Build the graph

```text
START
 ↓
node1
 ↓
node2
 ↓
END
```

Don't worry about optimization initially.

---

### Step 2 — Add LangSmith tracing

Configure:

```env
LANGSMITH_TRACING=true
```

and your API key/project.

---

### Step 3 — Run the graph

```python
graph.invoke(...)
```

---

### Step 4 — Inspect the trace

Look at:

```text
Input
 ↓
Node
 ↓
LLM
 ↓
Tool
 ↓
Node
 ↓
Output
```

---

### Step 5 — Find problems

For example:

```text
❌ Wrong routing
❌ Too many LLM calls
❌ Huge prompt
❌ Wrong tool arguments
❌ Slow tool
❌ Poor retrieved documents
```

---

### Step 6 — Fix the graph

Modify:

```text
Prompt
Node
Edge
Tool
Model
Retriever
```

---

### Step 7 — Evaluate

Create test cases:

```text
Input → Expected behavior
```

Then compare versions.

---

### Step 8 — Deploy

Once you're confident:

```text
Development
     ↓
Evaluation
     ↓
Production
     ↓
Monitoring
```

LangSmith continues being useful in production.

---

# 30. The mental model you should remember

The easiest way to remember everything is:

```text
                 LANGGRAPH
                     │
                     │ builds
                     ↓
              LLM APPLICATION
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
        Nodes       Tools      State
          │          │          │
          └──────────┼──────────┘
                     │
                     ↓
                 EXECUTION
                     │
                     │ traced by
                     ↓
                LANGSMITH
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
    Debugging    Evaluation    Monitoring
       │             │             │
       ↓             ↓             ↓
    Errors       Accuracy       Latency
    Prompts      Quality        Tokens
    Tool calls   Regression     Cost
    State        Datasets       Production
```

---

# 31. LangSmith is not a replacement for LangGraph

This is a common misunderstanding.

You **don't** use LangSmith to create your graph.

You use LangGraph to create:

```python
graph = builder.compile()
```

and LangSmith observes what happens when that graph runs.

So:

```python
graph.invoke(...)
```

is the application execution.

LangSmith provides visibility into that execution.

---

# 32. How this fits into your current learning path

Given the LangGraph topics you've been learning, I'd learn them in roughly this order:

```text
LangGraph Basics
      ↓
State
      ↓
Nodes
      ↓
Edges
      ↓
Conditional Edges
      ↓
Messages
      ↓
Tool Calling
      ↓
Agents
      ↓
Streaming
      ↓
Persistence
      ↓
SQLite
      ↓
LangSmith  ← YOU ARE HERE
      ↓
Tracing
      ↓
Debugging
      ↓
Evaluation
      ↓
Production Monitoring
```

Then move into:

```text
RAG
 ↓
Agentic RAG
 ↓
Multi-agent systems
 ↓
Human-in-the-loop
 ↓
Production deployment
```

### The key takeaway

If **LangGraph answers "How does my agent work?"**, LangSmith answers **"What exactly happened when my agent ran, and was it good?"**

For serious LangGraph applications, I would consider **LangSmith + LangGraph** almost like:

```text
LangGraph = Engine
LangSmith = Dashboard + Debugger + Evaluation system
```

That combination becomes especially valuable once your graph has **multiple nodes, conditional routing, tools, memory/persistence, streaming, or RAG**.
