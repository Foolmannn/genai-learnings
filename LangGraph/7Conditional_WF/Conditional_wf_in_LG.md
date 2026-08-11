# Conditional Workflows in LangGraph

Conditional workflows are one of the most important concepts in LangChain / LangGraph. They allow your graph to **make decisions at runtime** and choose different execution paths based on the current state.

A normal workflow looks like:

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

A conditional workflow looks like:

```text
             ┌──→ Node B ──→ Node D
             │
START → Node A
             │
             └──→ Node C ──→ Node D
```

The important idea is:

> **A conditional edge decides which node should execute next based on the current state.**

---

# 1. Why Conditional Workflows?

Suppose you are building an AI customer-support agent.

You might want:

```text
User Question
      ↓
Classify Question
      ↓
 ┌────┼─────────┐
 ↓    ↓         ↓
Billing Technical General
 ↓    ↓         ↓
     Response
        ↓
       END
```

The path isn't known when you construct the graph.

It depends on the user's input.

For example:

```text
"Why was I charged twice?"
```

should go to:

```text
classify → billing → response
```

while:

```text
"My API is returning 500"
```

should go to:

```text
classify → technical → response
```

This is exactly what conditional edges are designed for.

---

# 2. Basic LangGraph Concepts

A LangGraph workflow generally contains:

* **State**
* **Nodes**
* **Edges**
* **Conditional edges**
* **START**
* **END**

Conceptually:

```text
State
  ↓
Node
  ↓
Decision
  ↓
Conditional Edge
  ↓
Next Node
```

The state is shared between nodes.

For example:

```python
from typing import TypedDict

class State(TypedDict):
    question: str
    category: str
    response: str
```

A node can update the state:

```python
def classify(state: State):
    question = state["question"]

    if "payment" in question.lower():
        return {"category": "billing"}

    return {"category": "general"}
```

The next node can depend on:

```python
state["category"]
```

---

# 3. Normal Edge vs Conditional Edge

## Normal edge

A normal edge always follows the same path.

```python
graph.add_edge("node_a", "node_b")
```

Meaning:

```text
node_a → node_b
```

Every time `node_a` finishes, `node_b` executes.

---

## Conditional edge

A conditional edge dynamically chooses the destination.

```python
graph.add_conditional_edges(
    "node_a",
    decision_function
)
```

The decision function determines what happens next.

For example:

```python
def decide(state: State):
    if state["category"] == "billing":
        return "billing"

    return "general"
```

Then:

```python
graph.add_conditional_edges(
    "classify",
    decide
)
```

The graph becomes:

```text
                 ┌──→ billing
                 │
classify → decide
                 │
                 └──→ general
```

---

# 4. Complete Basic Example

Let's build a simple customer-support workflow.

```python
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    question: str
    category: str
    response: str
```

## Node 1 — Classification

```python
def classify(state: State):

    question = state["question"].lower()

    if "payment" in question or "charge" in question:
        category = "billing"

    elif "error" in question or "bug" in question:
        category = "technical"

    else:
        category = "general"

    return {
        "category": category
    }
```

---

## Node 2 — Billing

```python
def billing(state: State):

    return {
        "response": "Your billing issue has been forwarded to the billing team."
    }
```

---

## Node 3 — Technical

```python
def technical(state: State):

    return {
        "response": "Please provide the error message and relevant logs."
    }
```

---

## Node 4 — General

```python
def general(state: State):

    return {
        "response": "How can I help you?"
    }
```

---

# 5. Decision Function

Now create the routing function.

```python
def route_question(state: State):

    return state["category"]
```

Notice something important.

The routing function doesn't necessarily modify state.

It simply returns a **routing key**.

For example:

```text
billing
```

or:

```text
technical
```

or:

```text
general
```

---

# 6. Building the Graph

```python
builder = StateGraph(State)

builder.add_node("classify", classify)
builder.add_node("billing", billing)
builder.add_node("technical", technical)
builder.add_node("general", general)
```

Add the starting edge:

```python
builder.add_edge(START, "classify")
```

Now the important part:

```python
builder.add_conditional_edges(
    "classify",
    route_question,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general",
    }
)
```

Finally:

```python
builder.add_edge("billing", END)
builder.add_edge("technical", END)
builder.add_edge("general", END)
```

Compile:

```python
graph = builder.compile()
```

Invoke:

```python
result = graph.invoke({
    "question": "Why was I charged twice?"
})

print(result)
```

The execution will be approximately:

```text
START
  ↓
classify
  ↓
route_question
  ↓
billing
  ↓
END
```

---

# 7. Understanding `add_conditional_edges()`

This is the most important API to understand.

The general structure is:

```python
builder.add_conditional_edges(
    source_node,
    routing_function,
    routing_map
)
```

For example:

```python
builder.add_conditional_edges(
    "classify",
    route_question,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general"
    }
)
```

There are three parts.

### 1. Source node

```python
"classify"
```

This means:

> After `classify` finishes, make a routing decision.

### 2. Routing function

```python
route_question
```

This function examines the state.

### 3. Routing map

```python
{
    "billing": "billing",
    "technical": "technical",
    "general": "general"
}
```

This maps:

```text
routing result → destination node
```

For example:

```text
"billing" → billing node
"technical" → technical node
"general" → general node
```

---

# 8. Routing Function Can Return Anything

The routing function doesn't have to return the same value as the node name.

For example:

```python
def route_question(state: State):

    category = state["category"]

    if category == "billing":
        return "B"

    if category == "technical":
        return "T"

    return "G"
```

Then:

```python
builder.add_conditional_edges(
    "classify",
    route_question,
    {
        "B": "billing",
        "T": "technical",
        "G": "general"
    }
)
```

So:

```text
routing key
     ↓
"B"
     ↓
billing node
```

---

# 9. Conditional Workflow With LLM

This becomes much more useful when the decision is made by an LLM.

For example:

```text
User
 ↓
LLM Classifier
 ↓
 ┌───────────┬────────────┐
 ↓           ↓            ↓
Billing   Technical    General
```

Suppose you're using a structured Pydantic output.

```python
from pydantic import BaseModel, Field


class Classification(BaseModel):
    category: str = Field(
        description="The category of the user's question"
    )
```

Create a structured LLM:

```python
structured_llm = llm.with_structured_output(Classification)
```

Then:

```python
def classify(state: State):

    prompt = f"""
    Classify the following customer question.

    Question:
    {state["question"]}

    Categories:
    - billing
    - technical
    - general
    """

    result = structured_llm.invoke(prompt)

    return {
        "category": result.category
    }
```

Now your graph is making an intelligent routing decision.

---

# 10. Conditional Workflow With Pydantic State

Since you've been working with Pydantic models in LangGraph, this pattern is particularly useful.

You can define:

```python
from pydantic import BaseModel


class State(BaseModel):
    question: str
    category: str | None = None
    response: str | None = None
```

Then:

```python
def classify(state: State):

    question = state.question.lower()

    if "payment" in question:
        state.category = "billing"

    elif "error" in question:
        state.category = "technical"

    else:
        state.category = "general"

    return state
```

Routing:

```python
def route_question(state: State):
    return state.category
```

And:

```python
builder.add_conditional_edges(
    "classify",
    route_question,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general"
    }
)
```

However, when designing LangGraph state, you should be deliberate about whether your state is a mutable Pydantic object or whether nodes return state updates. The latter is often easier to reason about as workflows become larger.

---

# 11. Conditional Workflow With `END`

A conditional edge can also decide whether the graph should terminate.

Consider an email-processing agent:

```text
             ┌──→ process_email
START → check
             └──→ END
```

Maybe the email doesn't require a response.

```python
def should_process(state: State):

    if state["question"] == "":
        return "stop"

    return "process"
```

Then:

```python
builder.add_conditional_edges(
    "check",
    should_process,
    {
        "process": "process_email",
        "stop": END
    }
)
```

This gives:

```text
                ┌──→ process_email → END
                │
START → check ──┤
                │
                └──→ END
```

This is extremely useful for:

* validation
* early termination
* guardrails
* human approval
* filtering
* agent loops

---

# 12. Conditional Loops

Conditional edges aren't limited to branching.

They can create **loops**.

For example:

```text
       ┌───────────────┐
       ↓               │
Generate → Evaluate ───┘
              │
              ↓
             END
```

This can implement:

> Generate → evaluate → improve → evaluate → ... → final

For example:

```python
def evaluate(state: State):

    if state["score"] >= 8:
        return "approved"

    return "improve"
```

Then:

```python
builder.add_conditional_edges(
    "evaluate",
    evaluate,
    {
        "approved": END,
        "improve": "generate"
    }
)
```

The graph becomes:

```text
START
  ↓
generate
  ↓
evaluate
  │
  ├── approved → END
  │
  └── improve ──→ generate
                    ↑
                    │
                    └── loop
```

This is one of the major reasons LangGraph is different from a simple sequential chain.

---

# 13. Example: LLM Content Generation Loop

Imagine you're building a blog generator.

```text
             ┌──────────────┐
             │              ↓
START → Generate → Evaluate
                     │
              ┌──────┴───────┐
              ↓              ↓
           Improve          END
              │
              └──────────────→ Generate
```

State:

```python
from typing import TypedDict


class BlogState(TypedDict):
    topic: str
    article: str
    score: int
```

Generation:

```python
def generate(state: BlogState):

    article = model.invoke(
        f"Write an article about {state['topic']}"
    ).content

    return {
        "article": article
    }
```

Evaluation:

```python
def evaluate(state: BlogState):

    result = model.invoke(
        f"""
        Evaluate this article from 1-10.

        Article:
        {state['article']}
        """
    )

    score = int(result.content)

    return {
        "score": score
    }
```

Routing:

```python
def route_after_evaluation(state: BlogState):

    if state["score"] >= 8:
        return "done"

    return "improve"
```

Then:

```python
builder.add_conditional_edges(
    "evaluate",
    route_after_evaluation,
    {
        "done": END,
        "improve": "generate"
    }
)
```

---

# 14. Conditional Routing Based on Multiple State Fields

You can make decisions based on multiple pieces of state.

For example:

```python
class State(TypedDict):
    question: str
    authenticated: bool
    category: str
```

Routing:

```python
def route(state: State):

    if not state["authenticated"]:
        return "login"

    if state["category"] == "billing":
        return "billing"

    return "general"
```

Graph:

```python
builder.add_conditional_edges(
    "check_user",
    route,
    {
        "login": "login",
        "billing": "billing",
        "general": "general"
    }
)
```

Now:

```text
                  ┌──→ login
                  │
check_user ───────┼──→ billing
                  │
                  └──→ general
```

---

