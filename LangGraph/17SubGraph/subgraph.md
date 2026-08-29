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

# 10. Example RAG subgraph

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class RAGState(TypedDict):
    question: str
    documents: list[str]
    context: str


def retrieve(state: RAGState):
    question = state["question"]

    documents = [
        "LangGraph is a framework for building stateful agents.",
        "LangGraph supports persistence and human-in-the-loop."
    ]

    return {
        "documents": documents
    }


def create_context(state: RAGState):

    context = "\n".join(state["documents"])

    return {
        "context": context
    }


rag_builder = StateGraph(RAGState)

rag_builder.add_node("retrieve", retrieve)
rag_builder.add_node("create_context", create_context)

rag_builder.add_edge(START, "retrieve")
rag_builder.add_edge("retrieve", "create_context")
rag_builder.add_edge("create_context", END)

rag_subgraph = rag_builder.compile()
```

Now we have:

```text
rag_subgraph

START
  ↓
retrieve
  ↓
create_context
  ↓
 END
```

---

# 11. Parent graph

Now imagine:

```python
class AgentState(TypedDict):
    question: str
    context: str
    answer: str
```

We can make a wrapper function around the subgraph:

```python
def run_rag(state: AgentState):

    result = rag_subgraph.invoke({
        "question": state["question"],
        "documents": [],
        "context": ""
    })

    return {
        "context": result["context"]
    }
```

Then:

```python
parent_builder = StateGraph(AgentState)

parent_builder.add_node("rag", run_rag)

parent_builder.add_edge(START, "rag")
parent_builder.add_edge("rag", END)

parent_graph = parent_builder.compile()
```

Architecture:

```text
                 Parent Graph
                     
                    START
                      ↓
                  ┌───────┐
                  │  RAG  │
                  └───┬───┘
                      │
            ┌─────────┴─────────┐
            │                   │
            ↓                   │
       retrieve                │
            ↓                   │
      create_context            │
            ↓                   │
            └───────────────────┘
                      ↓
                     END
```

---

# 12. Why use a wrapper function?

When schemas are different, a wrapper is useful.

For example:

```python
def run_rag(state: AgentState):

    result = rag_subgraph.invoke({
        "question": state["question"],
        "documents": [],
        "context": ""
    })

    return {
        "context": result["context"]
    }
```

This performs **state transformation**.

```text
Parent State
     │
     │ transform
     ↓
Child State
     │
     ↓
Subgraph
     │
     │ transform
     ↓
Parent State
```

This gives you strong boundaries between components.

---

# 13. Subgraphs with shared state

There is another approach where parent and child share state keys.

For example:

```python
class State(TypedDict):
    question: str
    documents: list[str]
    answer: str
```

The subgraph can directly update:

```python
documents
```

and the parent can continue using it.

Architecture:

```text
Parent State
────────────────
question
documents
answer
────────────────
       ↓
    Subgraph
       ↓
────────────────
question
documents ← updated
answer
────────────────
```

This is convenient when the parent and child naturally operate on the same state.

---

# 14. Subgraph as a reusable component

One of the biggest advantages is **reusability**.

Suppose you build:

```text
web_search_subgraph
```

You can use it in:

```text
Customer Support Agent
Research Agent
News Agent
Coding Agent
Personal Assistant
```

For example:

```text
              Web Search Subgraph
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       Agent A      Agent B     Agent C
```

Instead of implementing search logic three times.

---

# 15. Subgraphs for multi-agent systems

Subgraphs are particularly useful for multi-agent architectures.

Imagine:

```text
                    Supervisor
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
     Researcher       Coder        Reviewer
       Subgraph      Subgraph      Subgraph
```

Each agent can have its own graph.

### Researcher

```text
START
  ↓
Search
  ↓
Analyze
  ↓
Summarize
  ↓
END
```

### Coder

```text
START
  ↓
Understand Task
  ↓
Write Code
  ↓
Test
  ↓
Fix
  ↓
END
```

### Reviewer

```text
START
  ↓
Review
  ↓
Identify Problems
  ↓
Approve / Reject
  ↓
END
```

The supervisor sees these as components.

---

# 16. Subgraphs vs normal nodes

This distinction is important.

A normal node:

```python
builder.add_node("search", search_function)
```

represents one operation.

A subgraph:

```python
builder.add_node("research", research_subgraph)
```

represents an entire workflow.

So:

```text
Node

┌────────────┐
│  Search    │
└────────────┘
```

versus:

```text
Subgraph

┌────────────────────────────┐
│       Research             │
│                            │
│ Search → Analyze → Verify  │
│                            │
└────────────────────────────┘
```

A subgraph is basically a **composite node**.

---

# 17. Subgraphs vs functions

You can think of the relationship like this:

### Function

```python
result = calculate_tax(income)
```

The function hides its internal implementation.

### Subgraph

```python
result = research_subgraph.invoke(...)
```

The subgraph hides its internal workflow.

For example:

```text
research_subgraph
```

could internally contain:

```text
search
  ↓
filter
  ↓
rerank
  ↓
summarize
```

The parent doesn't need to care.

---

# 18. Nested subgraphs

Subgraphs can themselves contain subgraphs.

For example:

```text
Main Graph
    │
    └── Agent Subgraph
           │
           ├── RAG Subgraph
           │      ├── Retrieve
           │      └── Rerank
           │
           └── Tool Subgraph
                  ├── Search
                  └── API
```

You can therefore build a hierarchy:

```text
Application
    ↓
Agent Graph
    ↓
Specialized Subgraph
    ↓
Smaller Subgraph
```

This is similar to software architecture:

```text
Application
    ↓
Module
    ↓
Component
    ↓
Function
```

---

# 19. Subgraphs and conditional routing

Subgraphs become even more powerful when combined with conditional edges.

For example:

```text
                  START
                    ↓
                Classifier
                    ↓
          ┌─────────┼─────────┐
          ↓         ↓         ↓
        RAG       Web       Code
      Subgraph   Subgraph   Subgraph
          │         │         │
          └─────────┼─────────┘
                    ↓
                  Answer
                    ↓
                   END
```

Code conceptually:

```python
def route(state):

    if state["type"] == "rag":
        return "rag"

    elif state["type"] == "web":
        return "web"

    return "code"
```

Then:

```python
builder.add_conditional_edges(
    "classifier",
    route,
    {
        "rag": "rag",
        "web": "web",
        "code": "code"
    }
)
```

Each destination can be a subgraph.

---

# 20. Subgraphs and persistence

This is another important LangGraph feature.

LangGraph supports persistence/checkpointing, and subgraphs can participate in larger stateful workflows.

Imagine:

```text
Main Graph
     ↓
Research Subgraph
     ↓
Human Approval
     ↓
Writing Subgraph
     ↓
Review Subgraph
```

If the workflow is interrupted:

```text
Research
   ↓
Human Approval
   ↓
     X
```

the persisted graph state can allow the workflow to resume rather than starting everything from scratch.

This becomes especially useful for:

* long-running agents
* human-in-the-loop
* multi-agent systems
* workflows involving external APIs
* expensive LLM calls

---

# 21. Subgraphs and Human-in-the-Loop

For example:

```text
Main Graph
    ↓
Research Subgraph
    ↓
Draft Subgraph
    ↓
Human Approval
    ↓
Publishing Subgraph
```

The human approval can happen between subgraphs.

```text
              Research
                 ↓
              Generate
                 ↓
          ┌──────────────┐
          │ Human Review │
          └───────┬──────┘
                  ↓
              Publish
```

This makes large HITL workflows much easier to organize.

---

# 22. Subgraphs and streaming

Subgraphs can also be useful when streaming a complex workflow.

For example:

```text
Main Graph
     ↓
Research Subgraph
     ↓
Answer Generator
```

Instead of treating the entire application as one massive stream, you can conceptually track:

```text
research.retrieve
research.analyze
research.summarize
answer.generate
```

This becomes very useful for debugging and observability.

---

# 23. Subgraphs and LangSmith

Subgraphs are particularly useful for tracing complex applications.

Imagine:

```text
Main Agent
│
├── classify
│
├── RAG Subgraph
│     ├── retrieve
│     ├── rerank
│     └── summarize
│
└── final_answer
```

Your traces can show the hierarchy:

```text
Main Agent
   │
   ├── classify
   │
   ├── RAG
   │    ├── retrieve
   │    ├── rerank
   │    └── summarize
   │
   └── final_answer
```

This is much easier to understand than having 30 unrelated nodes in one huge graph.

---

# 24. A realistic architecture

For a production-grade GenAI application, you could have:

```text
                       Application
                            │
                            ↓
                     Supervisor Graph
                            │
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
         RAG Subgraph   Web Subgraph   Code Subgraph
              │             │             │
         ┌────┴────┐     ┌──┴──┐       ┌──┴──┐
         ↓         ↓     ↓     ↓       ↓     ↓
     Retrieve   Rerank Search API   Generate Test
         │         │     │     │       │     │
         └────┬────┘     └──┬──┘       └──┬──┘
              ↓             ↓             ↓
              └─────────────┼─────────────┘
                            ↓
                     Response Generator
                            ↓
                           END
```

This is much easier to maintain than:

```text
One gigantic graph
     ↓
50 nodes
     ↓
100 conditional edges
     ↓
Impossible to understand
```

---

# 25. When should you use a subgraph?

Use a subgraph when a group of nodes represents a **logical unit**.

Good candidates:

### RAG

```text
retrieve
→ rerank
→ format_context
```

### Research

```text
search
→ collect
→ analyze
→ summarize
```

### Coding

```text
generate
→ execute
→ test
→ fix
```

### Authentication

```text
validate
→ authenticate
→ authorize
```

### Document processing

```text
load
→ split
→ embed
→ store
```

### Multi-agent

```text
Researcher
Coder
Reviewer
```

---

# 26. When NOT to use a subgraph

Don't create a subgraph for every two-node operation.

For example:

```text
START
 ↓
A
 ↓
B
 ↓
END
```

doesn't necessarily need a subgraph.

If the workflow is tiny and tightly coupled, keeping it in the parent graph is simpler.

Use subgraphs when they provide a meaningful **boundary**.

A good rule:

> **If you can give a group of nodes a meaningful name, it may deserve to become a subgraph.**

For example:

```text
retrieve → rerank → summarize
```

can become:

```text
ResearchSubgraph
```

---

# 27. Important concept: state boundary

Think of a subgraph as having an API.

For example:

```text
                 Research Subgraph

Input
────────────────────
question
────────────────────
          ↓
     [internal]
          ↓
retrieve
          ↓
rerank
          ↓
summarize
          ↓
Output
────────────────────
summary
────────────────────
```

The parent shouldn't necessarily care about:

```text
documents
scores
retrieval metadata
reranking information
```

It might only need:

```text
summary
```

This is **encapsulation**.

---

# 28. Subgraph design principle

A good subgraph should ideally have:

### 1. Clear responsibility

```text
RAGSubgraph
```

should do RAG-related work.

Not:

```text
RAG + payments + authentication
```

### 2. Clear input

```text
question
```

### 3. Clear output

```text
context
```

### 4. Internal implementation

```text
retrieve
rerank
summarize
```

can remain internal.

---

# 29. A complete mental model

Think of LangGraph like this:

```text
                    LangGraph Application
                            │
                            ↓
                       Main Graph
                            │
             ┌──────────────┼──────────────┐
             ↓              ↓              ↓
          Node          Subgraph         Node
                           │
                  ┌────────┼────────┐
                  ↓        ↓        ↓
                Node     Node     Node
                           │
                           ↓
                       Subgraph
                           │
                       ┌───┴───┐
                       ↓       ↓
                     Node    Node
```

So there are different abstraction levels:

```text
Node
  ↓
Subgraph
  ↓
Larger Subgraph
  ↓
Application
```

---

# 30. Subgraphs vs parallel workflows

Don't confuse these concepts.

### Subgraph

Concerned with **organization/composition**:

```text
Parent
  ↓
Subgraph
   ↓
 A → B → C
```

### Parallel workflow

Concerned with **execution**:

```text
       ┌── A ──┐
START ─┤       ├─→ D
       └── B ──┘
```

You can combine them:

```text
Main Graph
    ↓
Research Subgraph
    ↓
    ┌─────────┬─────────┐
    ↓         ↓         ↓
 Search      News      Docs
    └─────────┴─────────┘
              ↓
          Summarize
              ↓
             END
```

---

# 31. Subgraphs vs agents

These are also different.

An **agent** is generally an LLM-driven decision-maker.

A **subgraph** is an architectural composition mechanism.

You could have:

```text
Agent
  ↓
Subgraph
  ↓
Tools
```

or:

```text
Subgraph
   ↓
Agent
   ↓
Tools
```

For example:

```text
Research Subgraph

START
 ↓
Research Agent
 ↓
Search Tool
 ↓
Research Agent
 ↓
Summarize
 ↓
END
```

So a subgraph doesn't necessarily mean "agent."

---

# 32. The most important takeaway

If you're building increasingly complex LangGraph applications, think about your architecture like this:

```text
                  MAIN GRAPH
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
   RAG GRAPH      RESEARCH GRAPH   CODE GRAPH
       │              │              │
    retrieve        search         generate
       ↓              ↓              ↓
     rerank         analyze         execute
       ↓              ↓              ↓
   summarize       summarize         test
       │              │              │
       └──────────────┼──────────────┘
                      ↓
                FINAL RESPONSE
```

**Subgraphs give you modularity, encapsulation, reuse, independent state management, and a clean architecture for large LangGraph applications.**

For the kind of **RAG + tools + HITL + multi-agent** systems you're learning, subgraphs are especially important because they let you turn something like a 30–50 node application into several understandable components:

```text
                    Supervisor
                        │
        ┌───────────────┼────────────────┐
        ↓               ↓                ↓
   RAG Subgraph    Tool Subgraph    HITL Subgraph
        │               │                │
   retrieve          search           approval
   rerank            API calls        validation
   generate          tools            correction
        │               │                │
        └───────────────┼────────────────┘
                        ↓
                   Final Answer
```

### The key sentence to remember

> **A LangGraph subgraph is a compiled graph that can be composed into another graph, allowing a complex workflow to be divided into modular, reusable, and independently managed workflows.**
