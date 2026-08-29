# Subgraphs in LangGraph

A **subgraph** in LangGraph is a graph that is used as a **node inside another graph**.

The main idea is:

> **Build a complex workflow by breaking it into smaller, reusable graphs.**

This is similar to how functions work in programming:

```text
Main Graph
   │
   ├── Node A
   │
   ├── Subgraph
   │      ├── Node 1
   │      ├── Node 2
   │      └── Node 3
   │
   ├── Node B
   │
   └── Node C
```

Instead of putting every node into one huge graph, you can create smaller graphs and compose them.

---

# 1. Why do we need subgraphs?

Imagine you're building an AI customer-support system.

The complete workflow might be:

```text
                    ┌──────────────────┐
                    │ Receive Question │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Classify Query   │
                    └────────┬─────────┘
                             ↓
             ┌───────────────┴───────────────┐
             ↓                               ↓
       Technical Query                 Billing Query
             ↓                               ↓
      ┌───────────────┐               ┌───────────────┐
      │ Technical     │               │ Billing       │
      │ Subgraph      │               │ Subgraph      │
      └───────┬───────┘               └───────┬───────┘
              ↓                               ↓
              └───────────────┬───────────────┘
                              ↓
                       Final Response
```

The technical workflow itself might contain:

```text
Retrieve Documentation
        ↓
Analyze Error
        ↓
Generate Solution
        ↓
Verify Solution
```

Instead of adding all these nodes to the parent graph, we can create:

```text
technical_subgraph
```

and use it as a single component.

---

# 2. Subgraph = Graph inside a Graph

Suppose our parent graph is:

```text
START
  ↓
classify
  ↓
research_subgraph
  ↓
generate_answer
  ↓
END
```

The `research_subgraph` itself can be:

```text
START
  ↓
search
  ↓
analyze
  ↓
summarize
  ↓
END
```

So conceptually:

```text
Parent Graph

START
  ↓
classify
  ↓
┌─────────────────────────────┐
│       Research Subgraph     │
│                             │
│   search → analyze →        │
│              summarize      │
└──────────────┬──────────────┘
               ↓
        generate_answer
               ↓
              END
```

The parent graph doesn't necessarily need to know all the internal details.

This gives you **modularity**.

---

# 3. Basic graph without a subgraph

First, consider a normal LangGraph:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def node_a(state: State):
    return {
        "message": state["message"] + " → A"
    }


def node_b(state: State):
    return {
        "message": state["message"] + " → B"
    }


builder = StateGraph(State)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile()
```

Workflow:

```text
START
  ↓
node_a
  ↓
node_b
  ↓
 END
```

---

# 4. Turning part of it into a subgraph

Suppose these two nodes represent a separate process:

```text
node_a → node_b
```

We can create another graph:

```python
def node_a(state: State):
    return {
        "message": state["message"] + " → A"
    }


def node_b(state: State):
    return {
        "message": state["message"] + " → B"
    }


subgraph_builder = StateGraph(State)

subgraph_builder.add_node("node_a", node_a)
subgraph_builder.add_node("node_b", node_b)

subgraph_builder.add_edge(START, "node_a")
subgraph_builder.add_edge("node_a", "node_b")
subgraph_builder.add_edge("node_b", END)

subgraph = subgraph_builder.compile()
```

Now:

```text
subgraph

START
  ↓
node_a
  ↓
node_b
  ↓
 END
```

---

# 5. Using the subgraph in the parent graph

Now we can use:

```python
subgraph
```

as a node in another graph.

For example:

```python
def start_node(state: State):
    return {
        "message": state["message"] + " → START"
    }


def final_node(state: State):
    return {
        "message": state["message"] + " → FINAL"
    }


parent_builder = StateGraph(State)

parent_builder.add_node("start", start_node)
parent_builder.add_node("research", subgraph)
parent_builder.add_node("final", final_node)

parent_builder.add_edge(START, "start")
parent_builder.add_edge("start", "research")
parent_builder.add_edge("research", "final")
parent_builder.add_edge("final", END)

parent_graph = parent_builder.compile()
```

Now the complete architecture is:

```text
                 Parent Graph

START
  ↓
start
  ↓
┌───────────────────────────┐
│       research            │
│                           │
│   ┌──────┐    ┌──────┐    │
│   │  A   │ →  │  B   │    │
│   └──────┘    └──────┘    │
│                           │
└────────────┬──────────────┘
             ↓
           final
             ↓
            END
```

The important thing is that:

```python
parent_builder.add_node("research", subgraph)
```

treats the compiled graph as a node.

---

# 6. The two main ways subgraphs communicate state

This is one of the **most important concepts**.

There are two common patterns:

### Pattern 1

Parent and child use the **same state schema**.

### Pattern 2

Parent and child use **different state schemas**.

Let's understand both.

---

# 7. Same state schema

Suppose the parent graph has:

```python
class State(TypedDict):
    question: str
    answer: str
```

And the subgraph uses exactly the same state:

```python
class State(TypedDict):
    question: str
    answer: str
```

Then communication is straightforward.

Example:

```python
def search_node(state: State):
    return {
        "answer": f"Searching for: {state['question']}"
    }
```

Subgraph:

```python
sub_builder = StateGraph(State)

sub_builder.add_node("search", search_node)

sub_builder.add_edge(START, "search")
sub_builder.add_edge("search", END)

subgraph = sub_builder.compile()
```

Parent:

```python
parent_builder = StateGraph(State)

parent_builder.add_node("research", subgraph)
```

The parent passes state into the subgraph.

Conceptually:

```text
Parent State
     │
     │
     ↓
┌──────────────┐
│  Subgraph    │
│              │
│ question     │
│ answer       │
└──────┬───────┘
       │
       ↓
Updated State
```

This is the simplest form.

---

# 8. Different state schemas

This becomes more interesting when the parent and child have different responsibilities.

For example:

### Parent

```python
class ParentState(TypedDict):
    question: str
    final_answer: str
```

### Child

```python
class ResearchState(TypedDict):
    question: str
    documents: list[str]
    summary: str
```

Now:

```text
Parent
────────────────────────────

question
final_answer


            ↓


Research Subgraph
────────────────────────────

question
documents
summary
```

The child has internal state that the parent doesn't need.

This is extremely useful for modular systems.

---

# 9. Example: RAG subgraph

Since you're learning LangGraph + RAG, this is a very useful example.

Suppose we have:

```text
Main Agent
     ↓
Should we search documents?
     ↓
RAG Subgraph
     ↓
Generate final answer
```

The RAG subgraph:

```text
                 RAG Subgraph

                  START
                    ↓
              Retrieve Documents
                    ↓
              Rerank Documents
                    ↓
             Generate Context
                    ↓
                   END
```

The parent agent doesn't need to know how retrieval works internally.

---

## Parent state

```python
class AgentState(TypedDict):
    question: str
    answer: str
```

## RAG state

```python
class RAGState(TypedDict):
    question: str
    documents: list
    context: str
```

The RAG graph can independently manage:

```python
documents
context
```

The parent only cares about:

```python
question
answer
```

This separation is a major advantage of subgraphs.

---
