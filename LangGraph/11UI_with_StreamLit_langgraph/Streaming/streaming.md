# Streaming in LangGraph — Detailed Explanation

**Streaming** in LangGraph means receiving the execution results of a graph **incrementally as the graph runs**, instead of waiting for the entire graph to finish.

This is especially important for **LLM applications and agentic AI**, because an LLM may take several seconds to generate a response. Streaming lets you show the user what is happening in real time.

For example, instead of:

```text
User → Agent starts → Agent thinks → Tool executes → LLM responds → Final answer
                                                     ↓
                                          Everything returned at once
```

you can stream:

```text
User
 ↓
Node starts
 ↓
"Searching..."
 ↓
Tool result
 ↓
"Based on the results..."
 ↓
"Here is the answer..."
```

---

# 1. Why Streaming Is Important

Suppose you have a LangGraph agent:

```text
START
  ↓
Planner
  ↓
Researcher
  ↓
Writer
  ↓
END
```

Without streaming:

```python
result = graph.invoke({
    "topic": "Artificial Intelligence"
})

print(result)
```

The user waits until:

```text
Planner       ✓
Researcher    ✓
Writer        ✓
END           ✓
```

Only then does the application receive the result.

With streaming:

```text
Planner started...
Planner finished...

Researcher started...
Researcher finished...

Writer started...
Writer: Artificial
Writer: Intelligence
Writer: is
Writer: transforming
...
```

This creates a much better user experience.

---

# 2. LangGraph Streaming Architecture

A useful mental model is:

```text
                    LangGraph
                       │
                       ▼
                 ┌───────────┐
                 │   START   │
                 └─────┬─────┘
                       │
                       ▼
                 ┌───────────┐
                 │ Planner   │
                 └─────┬─────┘
                       │
                 stream update
                       │
                       ▼
                 ┌───────────┐
                 │ Research  │
                 └─────┬─────┘
                       │
                 stream update
                       │
                       ▼
                 ┌───────────┐
                 │  Writer   │
                 └─────┬─────┘
                       │
                 token stream
                       │
                       ▼
                      END
```

LangGraph provides several streaming modes because you may want to stream **different kinds of information**.

The important ones to understand are:

1. `updates`
2. `values`
3. `messages`
4. `custom`
5. `debug`

---

# 3. Basic `stream()` API

The simplest way to stream a graph is:

```python
for chunk in graph.stream(input):
    print(chunk)
```

For example:

```python
for chunk in graph.stream(
    {"topic": "Machine Learning"}
):
    print(chunk)
```

Instead of returning one final result, LangGraph yields intermediate information as the graph executes.

Conceptually:

```text
chunk 1
chunk 2
chunk 3
chunk 4
...
```

---

# 4. `stream_mode="updates"`

This is one of the most useful modes.

`updates` streams **state updates produced by individual graph nodes**.

Consider:

```python
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    topic: str
    outline: str
    article: str


def create_outline(state: State):
    return {
        "outline": f"Outline for {state['topic']}"
    }


def write_article(state: State):
    return {
        "article": f"Article based on {state['outline']}"
    }


builder = StateGraph(State)

builder.add_node("outline", create_outline)
builder.add_node("writer", write_article)

builder.add_edge(START, "outline")
builder.add_edge("outline", "writer")
builder.add_edge("writer", END)

graph = builder.compile()
```

Now:

```python
for chunk in graph.stream(
    {"topic": "Machine Learning"},
    stream_mode="updates"
):
    print(chunk)
```

You might conceptually receive:

```python
{"outline": {"outline": "Outline for Machine Learning"}}

{"writer": {"article": "Article based on Outline for Machine Learning"}}
```

The important idea is that the update is associated with the node.

Depending on the LangGraph version/configuration, the streamed update can include the node name as part of the emitted structure.

---
