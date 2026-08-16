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

# 5. Why `updates` Is Useful

Imagine:

```text
START
 ↓
classifier
 ↓
researcher
 ↓
writer
 ↓
END
```

You can observe:

```text
classifier → state update
researcher → state update
writer     → state update
```

This is useful for:

* displaying agent progress
* debugging
* monitoring workflows
* building UI progress indicators
* observing tool execution
* tracking state changes

For example, your frontend could display:

```text
✓ Understanding question
✓ Searching documents
⏳ Generating answer
```

---

# 6. `stream_mode="values"`

`values` is different from `updates`.

Instead of giving you only the **new update**, it gives you the **full state after each step**.

Example:

```python
for chunk in graph.stream(
    {"topic": "Machine Learning"},
    stream_mode="values"
):
    print(chunk)
```

Conceptually:

### After outline node

```python
{
    "topic": "Machine Learning",
    "outline": "Outline for Machine Learning",
    "article": ""
}
```

### After writer node

```python
{
    "topic": "Machine Learning",
    "outline": "Outline for Machine Learning",
    "article": "Article based on Outline for Machine Learning"
}
```

So:

```text
updates
   ↓
What changed?

values
   ↓
What is the complete state now?
```

---

# 7. `updates` vs `values`

This distinction is extremely important.

Suppose your state is:

```python
{
    "name": "Suman",
    "topic": "LangGraph",
    "answer": "..."
}
```

A node changes:

```python
answer
```

### `updates`

You are interested in:

```python
{
    "answer": "..."
}
```

### `values`

You receive:

```python
{
    "name": "Suman",
    "topic": "LangGraph",
    "answer": "..."
}
```

Therefore:

| Mode      | What it streams |
| --------- | --------------- |
| `updates` | State changes   |
| `values`  | Full state      |

---

# 8. Streaming LLM Tokens with `messages`

This is probably the **most important streaming mode for chatbot applications**.

Suppose your LangGraph node calls an LLM:

```python
def chatbot(state):
    response = model.invoke(state["messages"])

    return {
        "messages": [response]
    }
```

If you use:

```python
graph.stream(...)
```

with only normal state streaming, you might get the completed LLM response.

But for a chatbot, you usually want:

```text
Hello
Hello, how
Hello, how can
Hello, how can I
Hello, how can I help
...
```

This is where:

```python
stream_mode="messages"
```

becomes useful.

---

# 9. Example of LLM Token Streaming

Suppose:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="your-model",
    streaming=True
)
```

Then your LangGraph node:

```python
def chatbot(state):
    response = model.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }
```

You can stream:

```python
for message_chunk, metadata in graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "Explain LangGraph"
            }
        ]
    },
    stream_mode="messages"
):
    print(message_chunk.content, end="")
```

The application can receive chunks such as:

```text
LangGraph
is
a
framework
for
building
stateful
agentic
applications...
```

and render them immediately.

---

# 10. Why `messages` Is Different

Think about the difference:

```text
updates
   ↓
Node-level state changes
```

while:

```text
messages
   ↓
LLM message/token chunks
```

For an AI chatbot:

```text
User
 ↓
LangGraph
 ↓
LLM
 ↓
Token
 ↓
Token
 ↓
Token
 ↓
Token
 ↓
Final response
```

`messages` lets you expose that token-level generation.

---

# 11. `messages` Gives You Metadata Too

A streamed message chunk is generally accompanied by metadata.

Conceptually:

```python
chunk, metadata
```

The metadata can contain information useful for identifying where the message came from, such as:

```python
{
    "langgraph_node": "chatbot",
    ...
}
```

This becomes extremely useful when you have multiple LLM nodes.

Imagine:

```text
Supervisor
    ↓
Research Agent
    ↓
Writer Agent
```

All three may call an LLM.

Metadata allows your UI to distinguish:

```text
Research Agent:
Searching for information...

Writer Agent:
Writing final response...
```

rather than treating all tokens as one stream.

---

# 12. `stream_mode="custom"`

Sometimes you want to stream **your own custom information**.

For example:

```text
Searching database...
Found 10 documents.
Processing document 1...
Processing document 2...
Generating answer...
```

These messages aren't necessarily LLM tokens or state updates.

That's where custom streaming is useful.

The concept is:

```text
Your node
   │
   ├── update state
   │
   └── emit custom event
```

A node can emit custom data while executing.

For example, conceptually:

```python
def research(state, config):
    writer = get_stream_writer()

    writer("Starting research...")
    
    # research logic

    writer("Research completed.")

    return {
        "documents": [...]
    }
```

Then:

```python
for chunk in graph.stream(
    input,
    stream_mode="custom"
):
    print(chunk)
```

You can receive:

```text
Starting research...
Research completed.
```

---

# 13. Why Custom Streaming Is Powerful

Suppose you are building a RAG application.

Your graph:

```text
START
 ↓
Query Rewrite
 ↓
Retriever
 ↓
Reranker
 ↓
LLM
 ↓
END
```

You could stream custom progress:

```text
Rewriting query...
Searching vector database...
Retrieved 20 documents...
Reranking documents...
Generating answer...
```

This is much better UX than showing a generic:

```text
Loading...
```

for 10 seconds.

---

# 14. `stream_mode="debug"`

`debug` is useful when you want detailed information about graph execution.

It can expose things such as:

```text
Node started
Node finished
State changes
Tasks
LLM events
Execution information
```

This is especially useful while developing and debugging complex graphs.

For production UI, you normally don't want to expose every debug event to the user.

---

# 15. Debug vs Updates

Think of it like this:

```text
updates
   ↓
"What state did this node update?"

debug
   ↓
"What exactly is happening inside the graph?"
```

For development:

```python
for chunk in graph.stream(
    input,
    stream_mode="debug"
):
    print(chunk)
```

can be very useful.

---

# 16. Multiple Streaming Modes

You don't have to choose only one mode.

You can request multiple modes.

Conceptually:

```python
for chunk in graph.stream(
    input,
    stream_mode=["updates", "messages"]
):
    print(chunk)
```

Now you can receive different event types.

For example:

```text
updates
   ↓
Node state changed

messages
   ↓
LLM generated token
```

This is extremely useful for agentic applications.

---

# 17. Example: Agentic AI Application

Consider:

```text
                    User
                      │
                      ▼
                ┌───────────┐
                │ Supervisor│
                └─────┬─────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Research Agent          Calculator
          │                       │
          └───────────┬───────────┘
                      ▼
                 Final Writer
                      │
                      ▼
                     END
```

You might want to stream:

### Updates

```text
Supervisor updated state
Research Agent updated state
Calculator updated state
Final Writer updated state
```

### Messages

```text
Research Agent:
Let me search for...

Final Writer:
Based on the information...
```

### Custom

```text
Searching web...
Found 5 sources...
Calculating result...
```

### Debug

```text
Task started
Task completed
State changed
...
```

This is why LangGraph's streaming system is more powerful than simply streaming an LLM response.

---

# 18. Streaming and LangGraph State

One important concept:

**Streaming does not mean that the graph state itself is continuously changing token by token.**

For example:

```python
def node(state):
    response = model.invoke(...)
    
    return {
        "answer": response.content
    }
```

The LLM may generate:

```text
Hello
Hello world
Hello world this
Hello world this is
...
```

But your graph state may only be updated with:

```python
{
    "answer": "Hello world this is ..."
}
```

after the node finishes.

The `messages` stream allows you to observe the LLM generation **while it happens**.

This distinction is important:

```text
LLM token stream
        ≠
Graph state update
```

---

# 19. Streaming a Complete LangGraph Application

Let's build a simplified example.

## State

```python
from typing import TypedDict


class BlogState(TypedDict):
    topic: str
    outline: str
    article: str
```

## Nodes

```python
def create_outline(state: BlogState):

    print("Creating outline...")

    return {
        "outline": f"""
        1. Introduction
        2. Core concepts
        3. Examples
        4. Conclusion

        Topic: {state['topic']}
        """
    }


def create_article(state: BlogState):

    return {
        "article": f"""
        Article about {state['topic']}

        {state['outline']}
        """
    }
```

## Graph

```python
from langgraph.graph import StateGraph, START, END


builder = StateGraph(BlogState)

builder.add_node(
    "outline",
    create_outline
)

builder.add_node(
    "article",
    create_article
)

builder.add_edge(
    START,
    "outline"
)

builder.add_edge(
    "outline",
    "article"
)

builder.add_edge(
    "article",
    END
)

graph = builder.compile()
```

---

# 20. Streaming Updates

```python
for chunk in graph.stream(
    {
        "topic": "Machine Learning"
    },
    stream_mode="updates"
):
    print(chunk)
```

Conceptually:

```text
{
    "outline": {
        "outline": "..."
    }
}
```

then:

```text
{
    "article": {
        "article": "..."
    }
}
```

---

# 21. Streaming Full State

```python
for state in graph.stream(
    {
        "topic": "Machine Learning"
    },
    stream_mode="values"
):
    print(state)
```

You might see:

```python
{
    "topic": "Machine Learning",
    "outline": "...",
    "article": ""
}
```

then:

```python
{
    "topic": "Machine Learning",
    "outline": "...",
    "article": "..."
}
```

---
