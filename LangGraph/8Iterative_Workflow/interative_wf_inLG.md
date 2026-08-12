# Iterative Workflows in LangChain

An **iterative workflow** is a workflow where an LLM or a set of processing steps is executed **repeatedly**, with each iteration using the result of the previous iteration to improve, refine, validate, or continue the task.

A simple way to think about it:

> **Generate → Evaluate → Improve → Evaluate → Improve → ... → Stop**

This is different from a simple sequential workflow:

> **A → B → C → D**

In an iterative workflow:

> **A → B → C → if not good → A/B/C again**

Iterative workflows become especially important when building **AI agents, content refinement systems, code-generation systems, research systems, and autonomous workflows**.

---

# 1. Why do we need iterative workflows?

Suppose you ask an LLM:

> "Write a blog post about machine learning."

A single LLM call might produce a reasonable answer.

But suppose you want:

* high-quality content
* correct information
* good structure
* no unnecessary repetition
* proper examples
* appropriate length

You can ask the LLM to **evaluate its own output** and improve it.

For example:

```text
Generate Blog
     ↓
Evaluate Blog
     ↓
Is quality >= 8?
   /       \
 Yes        No
 ↓          ↓
Finish    Improve
             ↓
          Evaluate
```

This is an iterative workflow.

---

# 2. Iterative vs Sequential Workflow

### Sequential workflow

```text
Input
  ↓
Generate
  ↓
Process
  ↓
Format
  ↓
Output
```

Each node generally executes once.

### Iterative workflow

```text
             ┌──────────────┐
             ↓              │
Input → Generate → Evaluate ─┤
                  │           │
                  │ Bad       │
                  ↓           │
                Improve ──────┘
                  │
                  │ Good
                  ↓
                Output
```

The important concept is the **loop**.

---

# 3. Iterative workflows in modern LangChain ecosystem

Today, for graph-based iterative workflows, **LangGraph** is generally the appropriate tool within the LangChain ecosystem.

LangChain provides components such as:

* Chat models
* Tools
* Structured output
* Prompt templates
* Retrievers
* Document processing

LangGraph provides the orchestration primitives needed for:

* loops
* conditional routing
* state
* persistence
* human-in-the-loop
* agent workflows
* iterative execution

So conceptually:

```text
LangChain
   ↓
LLM + Tools + Structured Output
   ↓
LangGraph
   ↓
Stateful workflow
   ↓
Iteration / loops
```

---

# 4. Core components of an iterative workflow

An iterative workflow usually contains five things.

### 1. State

Stores the information shared between iterations.

Example:

```python
class BlogState(TypedDict):
    topic: str
    draft: str
    feedback: str
    score: int
    iteration: int
```

---

### 2. Generation node

Produces the initial result.

```python
def generate(state):
    ...
```

---

### 3. Evaluation node

Checks the result.

```python
def evaluate(state):
    ...
```

---

### 4. Improvement node

Uses feedback to improve the result.

```python
def improve(state):
    ...
```

---

### 5. Conditional routing

Decides whether to:

* stop
* or continue another iteration.

```python
def should_continue(state):
    if state["score"] >= 8:
        return "finish"

    return "improve"
```

This is what creates the loop.

---

# 5. Basic architecture

A typical iterative workflow looks like:

```text
             ┌─────────────────┐
             │     Generate    │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │     Evaluate    │
             └────────┬────────┘
                      ↓
                 Score good?
                  /       \
                Yes        No
                 ↓          ↓
              Finish      Improve
                            │
                            └──────────→ Evaluate
```

Notice that the workflow doesn't necessarily go back to the beginning.

It can loop between specific nodes.

---

# 6. Example: Blog generation and refinement

Let's build a realistic example.

Requirement:

> Generate a blog about "Machine Learning".

We want:

1. Generate draft
2. Evaluate draft
3. If quality is low, improve
4. Evaluate again
5. Stop when quality is sufficient
6. Prevent infinite loops

---

## Step 1: Install dependencies

For a modern setup:

```bash
pip install langchain langgraph langchain-openai python-dotenv
```

---

# 7. Define the state

Using `TypedDict`:

```python
from typing import TypedDict


class BlogState(TypedDict):
    topic: str
    draft: str
    feedback: str
    score: int
    iteration: int
```

The state represents the information flowing through the graph.

Initially:

```python
state = {
    "topic": "Machine Learning",
    "draft": "",
    "feedback": "",
    "score": 0,
    "iteration": 0
}
```

---

# 8. Create the model

For example:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7
)
```

Your exact available model can differ.

---

# 9. Generation node

```python
def generate(state: BlogState):

    prompt = f"""
    Write a high-quality blog post about:

    {state["topic"]}

    The blog should:
    - Have a clear introduction
    - Explain concepts accurately
    - Include examples
    - Have a logical structure
    - Be easy to understand
    """

    response = model.invoke(prompt)

    return {
        "draft": response.content,
        "iteration": state["iteration"] + 1
    }
```

The node receives the current state and returns updates.

---
