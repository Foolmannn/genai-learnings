 ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/overview?utm_source=chatgpt.com))

# LangGraph Core Concepts — Detailed Notes

## 1. What is LangGraph?



**LangGraph is a framework/runtime for building stateful, multi-step applications and agents using graph-based execution.**

The fundamental idea is:

> **Represent an application as a graph where nodes perform work, edges determine what happens next, and state carries information between steps.**

LangGraph is intentionally relatively low-level. It does not force you into one particular agent architecture. Its core capabilities include stateful execution, durable execution, human-in-the-loop workflows, persistence, streaming, and more. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/overview?utm_source=chatgpt.com))

Think of it like this:

```text
                  ┌─────────────┐
                  │    START    │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │    Node A   │
                  └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │    Node B   │
                  └──────┬──────┘
                         │
                    condition?
                    /       \
                  yes       no
                   │         │
                   ▼         ▼
              ┌────────┐  ┌───────┐
              │ Node C │  │  END  │
              └────┬───┘  └───────┘
                   │
                   └──────────►
```

The important concepts are:

```text
LangGraph
   │
   ├── State
   ├── Nodes
   ├── Edges
   ├── START
   ├── END
   ├── Conditional Edges
   ├── Graph
   ├── Compile
   └── Invoke
```

Once you understand these, more advanced concepts such as:

- agents
- tool calling
- loops
- memory
- persistence
- human-in-the-loop
- multi-agent systems
- RAG agents
- supervisor architectures

become much easier.

---

# 2. Why do we need LangGraph?

Before understanding LangGraph, consider a simple LLM application.

Suppose we want:

```text
User question
      ↓
LLM
      ↓
Need tool?
   /       \
 yes       no
  ↓         ↓
Tool      Response
  ↓
LLM
  ↓
Response
```

You could manually write this using Python:

```python
while True:
    response = llm.invoke(...)

    if response.tool_calls:
        result = tool.invoke(...)
        ...
    else:
        break
```

This works for simple applications.

But eventually you need:

- multiple steps
- branching
- loops
- state
- retries
- persistence
- human approval
- parallel execution
- multiple agents
- checkpoints

At that point, manually managing the control flow becomes complicated.

LangGraph provides a structured way to represent that control flow.

---

# 3. The Mental Model

The most important mental model is:

```text
                STATE
                  │
                  ▼
        ┌─────────────────┐
        │      NODE       │
        │                 │
        │ performs work   │
        └────────┬────────┘
                 │
                 ▼
               EDGE
                 │
                 ▼
        ┌─────────────────┐
        │      NODE       │
        └─────────────────┘
```

There are three fundamental pieces:

### State

What information does the workflow currently know?

### Nodes

What work should be performed?

### Edges

Where should execution go next?

This gives us:

```text
State + Nodes + Edges = Graph-based workflow
```

---

# 4. State

**State is arguably the most important concept in LangGraph.**

The state represents the data shared throughout graph execution.

For example:

```python
from typing_extensions import TypedDict

class State(TypedDict):
    question: str
    answer: str
```

Our graph now has a state containing:

```text
State
├── question
└── answer
```

Initially:

```python
{
    "question": "What is LangGraph?",
    "answer": ""
}
```

A node can read this state:

```python
def answer_question(state: State):
    question = state["question"]

    return {
        "answer": f"You asked: {question}"
    }
```

After execution:

```text
question = "What is LangGraph?"
answer   = "You asked: What is LangGraph?"
```

---

# 5. State is Shared Memory

Consider:

```text
Node A
   │
   │ updates state
   ▼
State
   │
   ▼
Node B
   │
   │ reads state
   ▼
State
   │
   ▼
Node C
```

The state allows nodes to communicate.

For example:

```python
class State(TypedDict):
    name: str
    age: int
    result: str
```

Node 1:

```python
def get_user(state):
    return {
        "name": "Suman",
        "age": 25
    }
```

Node 2:

```python
def process_user(state):
    return {
        "result": f"{state['name']} is {state['age']} years old."
    }
```

Node 2 doesn't need the result of Node 1 passed manually as a function argument.

It gets it from the **graph state**.

---

# 6. State Schema

The state needs a defined structure.

The common approach is:

```python
from typing_extensions import TypedDict

class State(TypedDict):
    question: str
    answer: str
```

Then:

```python
graph = StateGraph(State)
```

This tells LangGraph:

> "This graph operates on this state structure."

Current LangGraph also supports other state schemas such as dataclasses and Pydantic models. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/use-graph-api?utm_source=chatgpt.com))

---

# 7. Nodes

A **node represents a unit of work**.

A node is usually a Python function.

Example:

```python
def node_a(state):
    print("Running Node A")

    return {
        "result": "Hello"
    }
```

Another:

```python
def node_b(state):
    print("Running Node B")

    return {
        "result": "World"
    }
```

Nodes can perform virtually any application logic:

```text
Node
 │
 ├── Call LLM
 ├── Call tool
 ├── Query database
 ├── Retrieve documents
 ├── Validate output
 ├── Call API
 ├── Ask human
 ├── Transform data
 └── Execute Python code
```

For example:

```python
def call_llm(state):
    response = llm.invoke(state["question"])

    return {
        "answer": response.content
    }
```

---

# 8. Nodes Don't Usually Return the Entire State

A very important concept:

You generally return **state updates**, not necessarily the complete state.

Suppose:

```python
class State(TypedDict):
    question: str
    answer: str
```

You can write:

```python
def node(state):
    return {
        "answer": "LangGraph is a graph-based framework."
    }
```

You don't necessarily need:

```python
return {
    "question": state["question"],
    "answer": "..."
}
```

LangGraph applies the returned update to the state.

---

# 9. Edges

Nodes define **what work happens**.

Edges define **what happens next**.

For example:

```text
START
  ↓
node_a
  ↓
node_b
  ↓
END
```

In code:

```python
graph.add_edge(START, "node_a")
graph.add_edge("node_a", "node_b")
graph.add_edge("node_b", END)
```

The official Graph API describes `START` as the special entry node and `END` as the terminal node. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/graph-api?utm_source=chatgpt.com))

---

# 10. START

`START` represents the beginning of graph execution.

```python
from langgraph.graph import START
```

Example:

```python
graph.add_edge(START, "node_a")
```

Means:

```text
START
  ↓
node_a
```

Without defining how the graph starts, LangGraph doesn't know which node should initially execute.

---

# 11. END

`END` represents termination.

```python
from langgraph.graph import END
```

Example:

```python
graph.add_edge("node_b", END)
```

Means:

```text
node_b
  ↓
 END
```

Once execution reaches `END`, the graph stops.

---

# 12. State + Node + Edge

Let's combine everything.

```python
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    name: str
    greeting: str


def greet(state: State):
    return {
        "greeting": f"Hello {state['name']}"
    }


builder = StateGraph(State)

builder.add_node("greet", greet)

builder.add_edge(START, "greet")
builder.add_edge("greet", END)

graph = builder.compile()
```

Then:

```python
result = graph.invoke({
    "name": "Suman"
})

print(result)
```

Conceptually:

```text
Input
  │
  ▼
┌─────────┐
│  State  │
│ name    │
└────┬────┘
     │
     ▼
   START
     │
     ▼
  ┌───────┐
  │ greet │
  └───┬───┘
      │
      ▼
     END
      │
      ▼
  Final State
```

---

# 13. StateGraph

`StateGraph` is the main graph-building abstraction.

```python
from langgraph.graph import StateGraph
```

You provide your state schema:

```python
builder = StateGraph(State)
```

Then define:

```text
Nodes
Edges
Conditional Edges
```

Finally:

```python
graph = builder.compile()
```

The current documentation explicitly describes `StateGraph` as the main graph class and requires compilation before the graph can be used. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/graph-api?utm_source=chatgpt.com))

---

# 14. Compile

This is an important distinction.

Building:

```python
builder = StateGraph(State)
```

doesn't mean you have an executable graph yet.

You add:

```python
builder.add_node(...)
builder.add_edge(...)
```

Then:

```python
graph = builder.compile()
```

Think:

```text
StateGraph Builder
       │
       ├── Nodes
       ├── Edges
       └── Conditions
              │
              ▼
          compile()
              │
              ▼
       Executable Graph
```

Compilation performs structural checks and is also where runtime features such as checkpointers and breakpoints can be configured. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/graph-api?utm_source=chatgpt.com))

---

# 15. Invoke

Once compiled:

```python
graph = builder.compile()
```

you can execute it:

```python
result = graph.invoke({
    "name": "Suman"
})
```

The general flow is:

```text
Input
  ↓
Graph
  ↓
START
  ↓
Nodes
  ↓
Edges
  ↓
END
  ↓
Output
```

---

# 16. Sequential Workflow

The simplest workflow is sequential.

```text
START
  ↓
Node A
  ↓
Node B
  ↓
Node C
  ↓
END
```

Example:

```python
builder.add_node("extract", extract)
builder.add_node("transform", transform)
builder.add_node("summarize", summarize)

builder.add_edge(START, "extract")
builder.add_edge("extract", "transform")
builder.add_edge("transform", "summarize")
builder.add_edge("summarize", END)
```

This is useful when every step must happen in order.

Example:

```text
User Input
    ↓
Extract information
    ↓
Process information
    ↓
Generate response
```

---

# 17. Conditional Edges

This is where LangGraph becomes much more interesting.

Suppose:

```text
          START
            │
            ▼
        classify
         /     \
      math     general
       │         │
       ▼         ▼
 math_agent  general_agent
       │         │
       └────┬────┘
            ▼
           END
```

The next node depends on the current state.

Example:

```python
def route(state):

    if state["question_type"] == "math":
        return "math"

    return "general"
```

Then:

```python
builder.add_conditional_edges(
    "classify",
    route,
    {
        "math": "math_agent",
        "general": "general_agent"
    }
)
```

This creates dynamic routing.

The Graph API supports conditional edges for routing based on custom logic. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/graph-api?utm_source=chatgpt.com))

---

# 18. Why Conditional Routing Matters for Agents

Imagine a customer support agent:

```text
                 User
                  │
                  ▼
             Classifier
             /    |    \
            /     |     \
         billing tech  general
           │       │       │
           ▼       ▼       ▼
        Billing  Tech   General
         Agent    Agent    Agent
            \      |      /
             \     |     /
                  ▼
                END
```

The LLM or routing function determines which path should be executed.

This is one of the fundamental patterns behind agentic systems.

---

# 19. Loops

One of the biggest advantages of graph-based workflows is that edges don't have to move only forward.

You can create:

```text
      ┌──────────┐
      │          ▼
START → Agent → Evaluate
          ▲       │
          │       │
          └──retry┘
                  │
                  ▼
                 END
```

For example:

```text
Generate answer
      ↓
Evaluate answer
      ↓
Good?
 /    \
No    Yes
 |      |
 ▼      ▼
Improve END
 |
 └──────► Generate answer
```

This creates an iterative workflow.

---

# 20. Agent Loop

A typical tool-using agent looks like:

```text
             START
               │
               ▼
            LLM Node
               │
        Does it need tool?
           /          \
         yes           no
          │             │
          ▼             ▼
      Tool Node        END
          │
          ▼
        LLM Node
          │
          └───────────┐
                      │
                      ▼
               decide again
```

The current LangGraph quickstart demonstrates essentially this pattern: an LLM node, a tool node, conditional routing based on whether a tool call was produced, and a loop back to the LLM. ([Docs by LangChain](https://docs.langchain.com/oss/python/langgraph/quickstart?utm_source=chatgpt.com))

---

# 21. The Most Important Agent Pattern

Remember this:

```text
LLM
 │
 ├── no tool call ──────► END
 │
 └── tool call
        │
        ▼
      TOOL
        │
        ▼
       LLM
        │
        └──────────────►
```

This is the basic foundation of a tool-using agent.

---

# 22. Reducers

This is a more subtle but extremely important LangGraph concept.

Suppose multiple nodes update the same state key.

For example:

```text
             START
             /   \
            /     \
       Node A     Node B
            \     /
             \   /
              ▼
            State
```

Both Node A and Node B might produce:

```python
{
    "results": [...]
}
```

How should LangGraph combine those updates?

This is where **reducers** become important.

A reducer specifies how updates to a state key should be combined.

For example:

```python
import operator
from typing import Annotated
from typing_extensions import TypedDict

class State(TypedDict):
    results: Annotated[list, operator.add]
```

Conceptually:

```text
Node A → ["A"]
Node B → ["B"]

       ↓

Reducer

       ↓

["A", "B"]
```

Without an appropriate reducer, concurrent updates can conflict.

---

# 23. MessagesState

When building chatbots and agents, you frequently work with messages.

LangGraph provides:

```python
MessagesState
```

Example:

```python
from langgraph.graph import MessagesState
```

Instead of defining:

```python
class State(TypedDict):
    messages: list
```

you can use:

```python
class State(MessagesState):
    pass
```

Or simply use:

```python
MessagesState
```

This is especially useful for conversational applications.

---

# 24. Message-Based Agent Architecture

A typical chatbot can have:

```text
State
│
└── messages
      │
      ├── HumanMessage
      ├── AIMessage
      ├── ToolMessage
      ├── HumanMessage
      └── AIMessage
```

The graph operates over that evolving conversation.

Example:

```text
User
 ↓
HumanMessage
 ↓
LLM
 ↓
AIMessage
 ↓
ToolMessage
 ↓
LLM
 ↓
AIMessage
```

---

# 25. Tool Calling

LangGraph becomes particularly powerful when combined with LangChain tools.

Suppose we have:

```python
@tool
def calculator(a: int, b: int):
    return a + b
```

The LLM may produce:

```text
AIMessage
    │
    └── tool_call
          │
          ▼
       calculator
          │
          ▼
      ToolMessage
          │
          ▼
         LLM
```

LangGraph can explicitly represent this process.

---



