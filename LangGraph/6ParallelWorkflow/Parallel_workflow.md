# Parallel Workflows in LangGraph

Parallel workflows are one of the most useful patterns in **LangGraph** when multiple tasks can be executed independently and their results later combined.

For example, suppose you are building a research agent:

```text
                  ┌──→ Search Web ───────┐
User Query ───────┼──→ Analyze Data ──────┼──→ Combine Results ──→ Final Answer
                  └──→ Search Documents ─┘
```

Instead of doing:

```text
Search Web
    ↓
Analyze Data
    ↓
Search Documents
    ↓
Combine
```

you can execute the independent tasks concurrently:

```text
             ┌── Search Web ──────┐
             │                    │
Query ───────┼── Analyze Data ────┼──→ Combine
             │                    │
             └── Search Docs ────┘
```

This can significantly reduce workflow latency.

---

# 1. What is a Parallel Workflow?

A **parallel workflow** is a LangGraph workflow where one node branches into multiple nodes that can execute independently.

Consider:

```text
START
  ↓
Prepare
  ↓
 ┌─────────────┬─────────────┬─────────────┐
 ↓             ↓             ↓
Task A        Task B        Task C
 ↓             ↓             ↓
 └─────────────┴─────────────┘
                ↓
             Combine
                ↓
               END
```

The important idea is:

> **Task A, Task B, and Task C do not depend on each other's output, so they can run in parallel.**

This is different from a sequential workflow.

### Sequential

```text
A → B → C
```

### Parallel

```text
    ┌→ A ─┐
    ├→ B ─┤
START    ├→ D
    ├→ C ─┤
    └─────┘
```

---

# 2. Why Use Parallel Workflows?

Suppose you have three operations:

```text
Task A = 3 seconds
Task B = 4 seconds
Task C = 2 seconds
```

Sequential execution:

```text
3 + 4 + 2 = 9 seconds
```

Parallel execution is approximately:

```text
max(3, 4, 2) = 4 seconds
```

So instead of waiting 9 seconds, you may only need to wait around 4 seconds, ignoring orchestration and resource overhead.

This is especially useful when your nodes perform:

* LLM calls
* Web searches
* Database queries
* API requests
* Document retrieval
* Independent calculations
* Multiple classification tasks

---

# 3. Parallelism in LangGraph

The fundamental mechanism is **graph topology**.

Suppose we have:

```python
START → node_a
```

and then create:

```text
node_a
 ├──→ node_b
 ├──→ node_c
 └──→ node_d
```

LangGraph knows that `node_b`, `node_c`, and `node_d` are independent downstream tasks.

You can then connect all of them to a final node:

```text
             ┌──→ B ──┐
             │         │
A ───────────┼──→ C ───┼──→ D
             │         │
             └──→ E ──┘
```

The graph structure itself expresses the workflow.

---

# 4. Basic Example

Let's create a simple research workflow.

We want to perform three independent analyses:

1. Technical analysis
2. Business analysis
3. Market analysis

Then combine them.

## State

```python
from typing import TypedDict


class ResearchState(TypedDict):
    topic: str
    technical: str
    business: str
    market: str
    final_report: str
```

---

# 5. Create the Nodes

```python
def technical_analysis(state: ResearchState):
    topic = state["topic"]

    return {
        "technical": f"Technical analysis of {topic}"
    }


def business_analysis(state: ResearchState):
    topic = state["topic"]

    return {
        "business": f"Business analysis of {topic}"
    }


def market_analysis(state: ResearchState):
    topic = state["topic"]

    return {
        "market": f"Market analysis of {topic}"
    }
```

Each function:

* receives the current state
* performs its own task
* returns only the state updates it owns

---

# 6. Combine the Results

Now create a final node:

```python
def combine_results(state: ResearchState):

    final_report = f"""
    Topic: {state['topic']}

    Technical:
    {state['technical']}

    Business:
    {state['business']}

    Market:
    {state['market']}
    """

    return {
        "final_report": final_report
    }
```

---

# 7. Build the LangGraph

Modern LangGraph uses `StateGraph`.

```python
from langgraph.graph import StateGraph, START, END


builder = StateGraph(ResearchState)

builder.add_node("technical", technical_analysis)
builder.add_node("business", business_analysis)
builder.add_node("market", market_analysis)
builder.add_node("combine", combine_results)
```

Now create the parallel branches:

```python
builder.add_edge(START, "technical")
builder.add_edge(START, "business")
builder.add_edge(START, "market")
```

Then:

```python
builder.add_edge("technical", "combine")
builder.add_edge("business", "combine")
builder.add_edge("market", "combine")

builder.add_edge("combine", END)
```

Compile:

```python
graph = builder.compile()
```

---

# 8. Visual Structure

The graph is essentially:

```text
                  ┌───────────────→ technical ──────┐
                  │                                  │
START ────────────┼───────────────→ business ────────┼──→ combine → END
                  │                                  │
                  └───────────────→ market ─────────┘
```

The three branches are independent.

---

# 9. Running the Graph

```python
result = graph.invoke({
    "topic": "Generative AI"
})

print(result["final_report"])
```

The final state will contain:

```python
{
    "topic": "Generative AI",

    "technical": "...",

    "business": "...",

    "market": "...",

    "final_report": "..."
}
```

---

# 10. The Important Concept: State Updates

This is one of the most important things to understand about parallel workflows.

Suppose the initial state is:

```python
{
    "topic": "LangGraph"
}
```

The three nodes produce:

### Technical

```python
{
    "technical": "..."
}
```

### Business

```python
{
    "business": "..."
}
```

### Market

```python
{
    "market": "..."
}
```

LangGraph combines these updates into the state:

```text
              State
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
 technical  business   market
       │        │        │
       └────────┼────────┘
                ↓
        Updated State
```

Result:

```python
{
    "topic": "LangGraph",
    "technical": "...",
    "business": "...",
    "market": "..."
}
```

Then `combine` receives the accumulated state.

---

# 11. Why Separate State Keys Matter

Consider this bad design:

```python
class State(TypedDict):
    result: str
```

And all three nodes do:

```python
return {
    "result": "technical result"
}
```

```python
return {
    "result": "business result"
}
```

```python
return {
    "result": "market result"
}
```

Now multiple parallel nodes are trying to update the same state key.

That creates a **state conflict** unless you explicitly define how those updates should be merged.

A much cleaner design is:

```python
class State(TypedDict):
    technical: str
    business: str
    market: str
```

Then each node owns its own field.

---

# 12. Parallel Workflow with an LLM

This is where parallel workflows become much more useful.

Suppose the user asks:

```text
"Analyze the future of electric vehicles."
```

You could ask an LLM to independently generate:

```text
Technical perspective
Economic perspective
Environmental perspective
```

Graph:

```text
                         ┌──→ Technical LLM ───┐
                         │                     │
User Query → Prepare ────┼──→ Economic LLM ────┼──→ Synthesize
                         │                     │
                         └──→ Environmental ───┘
```

Each LLM call can happen independently.

---

# 13. Example with LangChain

```python
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


llm = ChatOpenAI(
    model="gpt-4.1-mini"
)
```

State:

```python
class ResearchState(TypedDict):
    topic: str
    technical: str
    economic: str
    environmental: str
    final: str
```

Technical node:

```python
def technical_node(state: ResearchState):

    response = llm.invoke(
        f"""
        Analyze the following topic from a technical
        perspective:

        {state['topic']}
        """
    )

    return {
        "technical": response.content
    }
```

Economic node:

```python
def economic_node(state: ResearchState):

    response = llm.invoke(
        f"""
        Analyze the following topic from an economic
        perspective:

        {state['topic']}
        """
    )

    return {
        "economic": response.content
    }
```

Environmental node:

```python
def environmental_node(state: ResearchState):

    response = llm.invoke(
        f"""
        Analyze the following topic from an environmental
        perspective:

        {state['topic']}
        """
    )

    return {
        "environmental": response.content
    }
```

Synthesis:

```python
def synthesis_node(state: ResearchState):

    prompt = f"""
    Create a comprehensive analysis using these perspectives.

    Technical:
    {state['technical']}

    Economic:
    {state['economic']}

    Environmental:
    {state['environmental']}
    """

    response = llm.invoke(prompt)

    return {
        "final": response.content
    }
```

---

# 14. Build the Graph

```python
builder = StateGraph(ResearchState)

builder.add_node("technical", technical_node)
builder.add_node("economic", economic_node)
builder.add_node("environmental", environmental_node)
builder.add_node("synthesis", synthesis_node)

builder.add_edge(START, "technical")
builder.add_edge(START, "economic")
builder.add_edge(START, "environmental")

builder.add_edge("technical", "synthesis")
builder.add_edge("economic", "synthesis")
builder.add_edge("environmental", "synthesis")

builder.add_edge("synthesis", END)

graph = builder.compile()
```

Invoke:

```python
result = graph.invoke({
    "topic": "Future of Electric Vehicles"
})

print(result["final"])
```

---

# 15. Important: Parallel Does Not Mean "Run Everything Immediately"

Consider:

```text
START
  ↓
Prepare
  ↓
 ┌──────┬──────┬──────┐
 ↓      ↓      ↓
 A      B      C
 └──────┼──────┘
        ↓
        D
```

The execution dependencies are:

```text
Prepare → A
Prepare → B
Prepare → C

A ─┐
B ─┼→ D
C ─┘
```

So:

* `A`, `B`, `C` can run independently.
* `D` must wait until its required upstream work has completed.

This is essentially a **directed acyclic graph (DAG)**.

---

# 16. Fan-Out and Fan-In

The two concepts you should remember are:

## Fan-out

One node branches into multiple nodes.

```text
             ┌──→ A
             │
START → X ───┼──→ B
             │
             └──→ C
```

This is **fan-out**.

---

## Fan-in

Multiple branches converge into one node.

```text
A ──┐
B ──┼──→ D
C ──┘
```

This is **fan-in**.

Therefore, most parallel LangGraph workflows look like:

```text
             FAN-OUT
                ↓
          ┌─────┼─────┐
          ↓     ↓     ↓
          A     B     C
          └─────┼─────┘
                ↓
             FAN-IN
```

This pattern is extremely important in agentic workflows.

---
