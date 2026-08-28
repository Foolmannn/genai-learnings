# HITL (Human-in-the-Loop) with LangGraph — Detailed Guide

**HITL = Human-in-the-Loop** means designing an AI workflow where the **LLM/agent can pause and ask a human for approval, correction, clarification, or a decision before continuing**.

This is especially important for agents that can take actions such as:

* Sending emails
* Deleting data
* Making purchases
* Updating databases
* Executing code
* Calling APIs
* Publishing content
* Performing sensitive business operations

With **LangGraph**, HITL fits naturally into the graph architecture because LangGraph supports **durable execution, state, persistence, interrupts, and resuming execution**.

---

# 1. Why do we need HITL?

Consider an AI agent that manages expenses.

The user says:

> "Delete all my expenses from January."

An autonomous agent might:

```text
User
 ↓
LLM
 ↓
Delete expenses
 ↓
Done
```

That's dangerous.

A HITL workflow would be:

```text
User
   ↓
LLM Agent
   ↓
Identifies destructive operation
   ↓
PAUSE
   ↓
Human approval
   ↓
Approved?
  ↙     ↘
Yes      No
 ↓       ↓
Delete   Cancel
```

The important idea is:

> **The AI decides when human intervention is necessary, and the human makes the final decision.**

---

# 2. HITL in LangGraph

LangGraph provides a mechanism called **interrupts**.

Conceptually:

```python
interrupt(...)
```

means:

> "Stop execution here and wait for external input."

For example:

```python
from langgraph.types import interrupt
```

Then:

```python
def approval_node(state):

    response = interrupt(
        {
            "message": "Do you approve this action?"
        }
    )

    return {
        "approved": response
    }
```

The graph pauses at this point.

Later, the application resumes the graph with:

```python
Command(resume=...)
```

---

# 3. Basic HITL architecture

A simple graph can look like:

```text
             ┌───────────────┐
             │     START     │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │ Analyze Task  │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │ Need Human?   │
             └───────┬───────┘
                     ↓
              ┌─────────────┐
              │  INTERRUPT  │
              └──────┬──────┘
                     ↓
              Human Decision
                 ↙       ↘
             Approve     Reject
                ↓           ↓
             Execute       Stop
```

---

# 4. The three major HITL patterns

In LangGraph, HITL can generally be designed around three patterns.

### Pattern 1 — Approve / Reject

Human decides whether the agent can perform an action.

```text
Agent
 ↓
Proposed action
 ↓
Human
 ↓
Approve / Reject
```

Example:

> "Send this email?"

---

### Pattern 2 — Review and Edit

The human modifies the AI-generated result.

```text
Agent
 ↓
Draft
 ↓
Human edits
 ↓
Agent continues
```

Example:

AI generates:

```text
Dear John,

Your order has been cancelled.
```

Human changes it to:

```text
Dear John,

Unfortunately, your order has been cancelled.
We apologize for the inconvenience.
```

Then the workflow continues.

---

### Pattern 3 — Human provides additional information

The agent doesn't have enough information.

```text
Agent
 ↓
Missing information
 ↓
Human provides information
 ↓
Agent continues
```

Example:

```text
Agent:
Which account should I use?

Human:
Use the savings account.
```

---

# 5. Installing LangGraph

If you haven't already:

```bash
pip install -U langgraph
```

You will commonly also use LangChain:

```bash
pip install -U langchain langchain-openai
```

---

# 6. Simple interrupt example

Let's create a very small graph.

```python
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
```

Define state:

```python
class State(TypedDict):
    name: str
    approved: bool
```

Create a node:

```python
def ask_human(state: State):

    decision = interrupt(
        {
            "question": f"Should we continue for {state['name']}?"
        }
    )

    return {
        "approved": decision
    }
```

Create graph:

```python
builder = StateGraph(State)

builder.add_node("ask_human", ask_human)

builder.add_edge(START, "ask_human")
builder.add_edge("ask_human", END)

graph = builder.compile()
```

But there's an important issue.

### Persistence

For a real HITL workflow, you need a **checkpointer**.

Why?

Because when the graph pauses, LangGraph needs to preserve the execution state so that it can resume later.

---

# 7. HITL + Checkpointer

For development, we can use:

```python
from langgraph.checkpoint.memory import InMemorySaver
```

Then:

```python
checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)
```

Now provide a `thread_id`.

```python
config = {
    "configurable": {
        "thread_id": "user-123"
    }
}
```

The thread ID identifies the execution.

---

# 8. Complete basic example

```python
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


class State(TypedDict):
    name: str
    approved: bool


def ask_human(state: State):

    decision = interrupt(
        {
            "question": f"Should we continue for {state['name']}?"
        }
    )

    return {
        "approved": decision
    }


builder = StateGraph(State)

builder.add_node("ask_human", ask_human)

builder.add_edge(START, "ask_human")
builder.add_edge("ask_human", END)


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)
```

Now invoke:

```python
config = {
    "configurable": {
        "thread_id": "user-123"
    }
}

result = graph.invoke(
    {
        "name": "Suman",
        "approved": False
    },
    config
)
```

The graph reaches:

```python
interrupt(...)
```

and pauses.

---
