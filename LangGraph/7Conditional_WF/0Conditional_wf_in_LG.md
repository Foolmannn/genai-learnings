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

# 15. Conditional Routing After Tool Calls

This becomes particularly important when building agents.

Imagine:

```text
User
 ↓
Agent
 ↓
 ┌──────────────┐
 │              │
Tool required?  No
 │              │
Yes             ↓
 ↓             END
Tool
 ↓
Agent
```

The decision can be:

```python
def route_after_agent(state):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return "end"
```

Then:

```python
builder.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "end": END
    }
)
```

This is the foundation of many agentic workflows.

---

# 16. Tool-Calling Agent Pattern

A common architecture is:

```text
                ┌─────────────┐
                │             ↓
START → Agent → Tools → Agent
          │
          ↓
         END
```

The agent decides:

```text
Do I need a tool?
```

If yes:

```text
agent → tools
```

After tools execute:

```text
tools → agent
```

If no:

```text
agent → END
```

This is a **conditional loop**.

---

# 17. Conditional Edge vs Conditional Node

These concepts are easy to confuse.

### Conditional node

A node performs some computation.

```python
def classify(state):
    ...
    return {"category": "billing"}
```

It modifies state.

### Routing function

A routing function decides where to go.

```python
def route(state):
    return state["category"]
```

It determines the next node.

Think:

```text
Node
 ↓
"What's the state now?"
 ↓
Routing function
 ↓
"Where should we go?"
```

---

# 18. Important Mental Model

You can think about LangGraph like this:

### Nodes = Workers

```text
Node A = classifier
Node B = researcher
Node C = writer
Node D = evaluator
```

### Edges = Roads

```text
A → B
B → C
```

### Conditional edges = Traffic controller

```text
             → B
            /
A → traffic
            \
             → C
```

The traffic controller looks at the current state and chooses the appropriate road.

---

# 19. Conditional Workflow Architecture

A realistic AI system could look like:

```text
                         ┌→ RAG → Generate
                         │
START → Classify → Route ├→ Web Search → Generate
                         │
                         └→ Direct Answer
                                      ↓
                                   Evaluate
                                      ↓
                              ┌───────┴───────┐
                              ↓               ↓
                           Improve           END
                              │
                              └→ Generate
```

Here you have **two different types of conditional routing**:

### Routing decision #1

```text
Classify → Route
```

chooses the research strategy.

### Routing decision #2

```text
Evaluate → Route
```

decides whether to finish or improve.

This is where LangGraph starts becoming powerful for agentic systems.

---

# 20. Conditional Workflow With Pydantic + Structured LLM

A production-style pattern could be:

```python
from typing import Literal
from pydantic import BaseModel, Field


class Classification(BaseModel):
    category: Literal[
        "billing",
        "technical",
        "general"
    ]


class State(BaseModel):
    question: str
    category: str | None = None
    response: str | None = None
```

Structured classifier:

```python
classifier = llm.with_structured_output(Classification)
```

Node:

```python
def classify(state: State):

    result = classifier.invoke(
        f"""
        Classify this question:

        {state.question}

        Choose one:
        billing
        technical
        general
        """
    )

    return {
        "category": result.category
    }
```

Routing:

```python
def route(state: State):

    return state.category
```

Graph:

```python
builder.add_conditional_edges(
    "classify",
    route,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general"
    }
)
```

The advantage of using:

```python
Literal["billing", "technical", "general"]
```

is that the possible categories are explicitly constrained.

---

# 21. `Literal` for Routing

You can also use typing to document the possible routing values:

```python
from typing import Literal


def route(
    state: State
) -> Literal["billing", "technical", "general"]:

    return state.category
```

This makes your code easier to understand and gives static type checkers useful information.

---

# 22. Conditional Workflow vs `if/else`

You might ask:

> Why not just use Python `if/else`?

You absolutely can use `if/else` **inside a node**, but LangGraph conditional edges provide a cleaner graph-level architecture.

For example:

```python
def process(state):

    if state["category"] == "billing":
        # billing logic

    else:
        # general logic
```

This puts everything inside one node.

Instead:

```text
classify
   ↓
conditional edge
 ┌─┴────┐
 ↓      ↓
billing general
```

Each responsibility becomes a separate node.

This gives you:

* clearer architecture
* easier debugging
* visualization
* independent testing
* better observability
* easier modification
* reusable nodes

---

# 23. Bad Design

Avoid huge nodes like:

```python
def everything(state):

    if condition1:
        ...
    elif condition2:
        ...
    elif condition3:
        ...
    elif condition4:
        ...
    elif condition5:
        ...
```

This becomes difficult to maintain.

Instead:

```text
             ┌→ node_1
             │
classifier → ├→ node_2
             │
             ├→ node_3
             │
             └→ node_4
```

Each node has one responsibility.

---

# 24. Conditional Routing With Validation

Another common pattern:

```text
START
 ↓
Validate
 ↓
 ┌─────────────┐
 ↓             ↓
Valid        Invalid
 ↓             ↓
Process       Fix
 ↓             │
END            └──→ Validate
```

Routing:

```python
def route_validation(state):

    if state["valid"]:
        return "process"

    return "fix"
```

Then:

```python
builder.add_conditional_edges(
    "validate",
    route_validation,
    {
        "process": "process",
        "fix": "fix"
    }
)
```

This gives you a retry loop.

---

# 25. Conditional Routing With Human-in-the-Loop

You can also build:

```text
Generate
   ↓
Check
   ↓
 ┌───────────────┐
 ↓               ↓
Low risk       High risk
 ↓               ↓
END          Human Review
                  ↓
             ┌────┴────┐
             ↓         ↓
           Reject    Approve
             ↓         ↓
            END       END
```

The routing decision can depend on:

```python
state["risk_score"]
```

For example:

```python
def route_risk(state):

    if state["risk_score"] > 0.8:
        return "human_review"

    return "continue"
```

---

# 26. Conditional Routing With Multiple Branches

You aren't limited to two paths.

For example:

```text
             ┌→ easy
             │
             ├→ medium
START → route├→ hard
             │
             ├→ expert
             │
             └→ reject
```

Code:

```python
builder.add_conditional_edges(
    "classify",
    route,
    {
        "easy": "easy_handler",
        "medium": "medium_handler",
        "hard": "hard_handler",
        "expert": "expert_handler",
        "reject": END
    }
)
```

---

# 27. Conditional Routing to the Same Node

Multiple decisions can converge.

```text
             ┌→ billing ──┐
             │             │
classify ────┼→ technical ─┼→ response
             │             │
             └→ general ──┘
```

Code:

```python
builder.add_conditional_edges(
    "classify",
    route,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general"
    }
)

builder.add_edge("billing", "response")
builder.add_edge("technical", "response")
builder.add_edge("general", "response")
```

This pattern is called **branching and convergence**.

---

# 28. Conditional Workflow With Parallelism

Conditional routing can also be combined with parallel workflows.

For example:

```text
             ┌→ Search Web ─────┐
             │                  │
Question → Router               ├→ Synthesize
             │                  │
             └→ Search DB ──────┘
```

The router determines whether certain branches should execute.

This becomes especially powerful when combined with LangGraph's parallel execution and reducers.

---

# 29. Conditional Workflow Execution Flow

When invoking:

```python
graph.invoke({
    "question": "Why was I charged twice?"
})
```

LangGraph conceptually performs:

### Step 1

Initialize state:

```text
question = "Why was I charged twice?"
```

### Step 2

Execute:

```text
classify
```

State becomes:

```text
category = billing
```

### Step 3

Execute routing function:

```python
route_question(state)
```

returns:

```text
billing
```

### Step 4

Routing map resolves:

```text
billing → billing node
```

### Step 5

Execute:

```text
billing
```

### Step 6

Execute:

```text
END
```

---

# 30. Important Difference: State Update vs Routing Result

This is one of the most important things to understand.

Suppose:

```python
def classify(state):

    return {
        "category": "billing"
    }
```

This updates state.

The routing function:

```python
def route(state):

    return state["category"]
```

returns a routing key.

So:

```text
classify
   │
   │ state update
   ↓
category = billing
   │
   ↓
route()
   │
   │ routing result
   ↓
"billing"
   │
   ↓
billing node
```

Don't confuse:

```python
return {"category": "billing"}
```

with:

```python
return "billing"
```

They have different purposes.

---

# 31. A More Complete Example

Here's a practical workflow combining several concepts.

```python
from typing import TypedDict, Literal

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    question: str
    category: str
    answer: str


def classify(state: State):

    question = state["question"].lower()

    if "price" in question or "payment" in question:
        return {"category": "billing"}

    if "error" in question or "bug" in question:
        return {"category": "technical"}

    return {"category": "general"}


def route(
    state: State
) -> Literal["billing", "technical", "general"]:

    return state["category"]


def billing(state: State):

    return {
        "answer": "This is a billing-related question."
    }


def technical(state: State):

    return {
        "answer": "This is a technical question."
    }


def general(state: State):

    return {
        "answer": "This is a general question."
    }


builder = StateGraph(State)

builder.add_node("classify", classify)
builder.add_node("billing", billing)
builder.add_node("technical", technical)
builder.add_node("general", general)

builder.add_edge(START, "classify")

builder.add_conditional_edges(
    "classify",
    route,
    {
        "billing": "billing",
        "technical": "technical",
        "general": "general",
    }
)

builder.add_edge("billing", END)
builder.add_edge("technical", END)
builder.add_edge("general", END)

graph = builder.compile()
```

Then:

```python
result = graph.invoke({
    "question": "Why was I charged twice?",
    "category": "",
    "answer": ""
})

print(result)
```

Result conceptually:

```python
{
    "question": "Why was I charged twice?",
    "category": "billing",
    "answer": "This is a billing-related question."
}
```

---

# 32. Visualizing the Graph

One of the benefits of LangGraph is that you can visualize the workflow.

Conceptually, our graph is:

```text
               ┌───────────→ billing ───────→ END
               │
START → classify ──────────→ technical ─────→ END
               │
               └───────────→ general ───────→ END
```

For complex agent systems, this visualization becomes extremely useful because you can see:

* branches
* loops
* termination conditions
* agent/tool cycles
* human approval paths
* retry paths

---

# 33. Common Conditional Workflow Patterns

You should become comfortable with these patterns.

### Pattern 1 — Simple branching

```text
A → B
  → C
```

Used for:

* classification
* routing
* intent detection

---

### Pattern 2 — Branch + convergence

```text
       → B →
A →           D
       → C →
```

Used for:

* specialized processing
* multiple handlers

---

### Pattern 3 — Conditional termination

```text
A → B
  → END
```

Used for:

* validation
* guardrails
* filtering

---

### Pattern 4 — Retry loop

```text
A → B
↑   │
└───┘
```

Used for:

* validation
* generation/evaluation
* retry mechanisms

---

### Pattern 5 — Agent/tool loop

```text
Agent → Tools
  ↑      │
  └──────┘

Agent → END
```

Used for:

* AI agents
* tool calling

---

### Pattern 6 — Human approval

```text
Generate
   ↓
Review
   ↓
 ┌─┴─┐
 ↓   ↓
Yes  No
 ↓   ↓
END Retry
```

Used for:

* sensitive workflows
* approval systems
* content moderation

---

# 34. Conditional Workflows vs Linear Workflows

| Feature                 | Linear  | Conditional |
| ----------------------- | ------- | ----------- |
| Fixed execution path    | ✅       | ❌           |
| Dynamic routing         | ❌       | ✅           |
| Branching               | ❌       | ✅           |
| Loops                   | Limited | ✅           |
| Early termination       | Limited | ✅           |
| Agent workflows         | Limited | ✅           |
| Human approval          | Limited | ✅           |
| Retry logic             | Limited | ✅           |
| Complex decision making | ❌       | ✅           |

---

# 35. Where Conditional Workflows Are Used

You'll see them everywhere in serious agentic applications.

### RAG

```text
Question
 ↓
Need retrieval?
 ├── Yes → Retriever → LLM
 └── No  → LLM
```

### Customer support

```text
Question
 ↓
Classifier
 ├── Billing
 ├── Technical
 └── Account
```

### Coding agent

```text
Request
 ↓
Plan
 ↓
Need tool?
 ├── Yes → Tool → Agent
 └── No → Response
```

### Research agent

```text
Question
 ↓
Research required?
 ├── Web search
 ├── Database
 └── Direct answer
```

### Content generation

```text
Generate
 ↓
Evaluate
 ├── Good → END
 └── Bad → Improve → Generate
```

---

# 36. The Most Important LangGraph Pattern to Learn

Given that you're learning **agentic AI with LangChain/LangGraph**, I'd recommend mastering this pattern first:

```text
                    ┌─────────────┐
                    │             ↓
START → Agent → Router → Tool → Agent
          │
          │
          └────────────────────→ END
```

In code:

```python
builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)
```

This simple pattern is the foundation for many modern tool-using agents.

Then learn:

```text
Conditional branching
        ↓
Conditional loops
        ↓
Tool-calling loops
        ↓
Parallel + conditional workflows
        ↓
Human-in-the-loop
        ↓
Subgraphs
        ↓
Multi-agent workflows
```

---

# 37. Key Takeaways

The core concept can be reduced to:

```python
builder.add_conditional_edges(
    "source_node",
    routing_function,
    {
        "route_a": "node_a",
        "route_b": "node_b",
        "route_c": "node_c",
    }
)
```

Where:

```text
source_node
     ↓
routing_function(state)
     ↓
routing key
     ↓
routing map
     ↓
next node
```

For example:

```python
def route(state):
    if state["score"] >= 8:
        return "done"

    return "retry"
```

and:

```python
builder.add_conditional_edges(
    "evaluate",
    route,
    {
        "done": END,
        "retry": "generate"
    }
)
```

produces:

```text
             ┌───────────────┐
             │               │
             ↓               │
          Generate → Evaluate
                         │
                    ┌────┴────┐
                    ↓         ↓
                   END      Generate
```

**That is the essence of conditional workflows in LangGraph: the graph structure is defined ahead of time, but the actual path through that graph is determined dynamically from the current state.**
