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

# 9. What does the application receive?

The application can inspect the interrupted state.

A useful way is:

```python
state = graph.get_state(config)

print(state)
```

You can inspect the interrupts:

```python
print(state.interrupts)
```

Conceptually you'll get information similar to:

```text
Interrupt(
    value={
        "question": "Should we continue for Suman?"
    }
)
```

Your frontend can then display:

```text
┌─────────────────────────────────┐
│ Human Approval Required         │
│                                 │
│ Should we continue for Suman?   │
│                                 │
│ [ Approve ]      [ Reject ]     │
└─────────────────────────────────┘
```

---

# 10. Resuming the graph

Suppose the human clicks:

```text
Approve
```

The application resumes the graph using:

```python
graph.invoke(
    Command(resume=True),
    config
)
```

The value:

```python
True
```

is returned from:

```python
interrupt(...)
```

Therefore:

```python
decision = interrupt(...)
```

becomes:

```python
decision = True
```

and the node returns:

```python
{
    "approved": True
}
```

---

# 11. Rejecting

If the human clicks Reject:

```python
graph.invoke(
    Command(resume=False),
    config
)
```

Then:

```python
decision = False
```

and:

```python
{
    "approved": False
}
```

---

# 12. Very important concept: `interrupt()` is not normal input()

This distinction is extremely important.

You might initially think:

```python
interrupt()
```

is equivalent to:

```python
input()
```

It isn't.

### Python `input()`

```python
name = input("Enter your name:")
```

blocks the Python process.

The process waits.

---

### LangGraph `interrupt()`

```python
name = interrupt("Enter your name")
```

pauses the **graph execution** and allows the application to handle the interruption.

This is much more suitable for:

* Web applications
* APIs
* Streamlit
* React frontends
* Long-running agents
* Distributed systems

---

# 13. HITL with conditional routing

Now let's build something more realistic.

Suppose our agent decides whether an action is dangerous.

```text
START
  ↓
Analyze
  ↓
Dangerous?
 ↙       ↘
No       Yes
 ↓        ↓
Execute  Human Approval
          ↓
       Approved?
        ↙    ↘
      Yes     No
       ↓       ↓
    Execute   Reject
```

State:

```python
class State(TypedDict):
    action: str
    requires_approval: bool
    approved: bool
```

Analysis node:

```python
def analyze(state):

    dangerous_actions = [
        "delete_database",
        "send_money",
        "delete_user"
    ]

    return {
        "requires_approval":
            state["action"] in dangerous_actions
    }
```

---

# 14. Human approval node

```python
def human_approval(state):

    decision = interrupt(
        {
            "type": "approval",
            "action": state["action"],
            "message": "Do you approve this action?"
        }
    )

    return {
        "approved": decision
    }
```

---

# 15. Routing function

```python
def route_after_analysis(state):

    if state["requires_approval"]:
        return "human_approval"

    return "execute"
```

And after approval:

```python
def route_after_approval(state):

    if state["approved"]:
        return "execute"

    return "reject"
```

---

# 16. Build the graph

```python
builder = StateGraph(State)

builder.add_node("analyze", analyze)
builder.add_node("human_approval", human_approval)
builder.add_node("execute", execute)
builder.add_node("reject", reject)

builder.add_edge(START, "analyze")

builder.add_conditional_edges(
    "analyze",
    route_after_analysis
)

builder.add_conditional_edges(
    "human_approval",
    route_after_approval
)

builder.add_edge("execute", END)
builder.add_edge("reject", END)
```

Compile:

```python
graph = builder.compile(
    checkpointer=InMemorySaver()
)
```

---

# 17. Why this architecture is powerful

You can now create policies like:

```text
Action                         Approval
------------------------------------------------
Read document                  ❌
Search web                    ❌
Generate summary              ❌
Send email                    ✅
Delete record                 ✅
Transfer money                ✅
Publish article               ✅
Modify production DB          ✅
```

The agent remains autonomous for low-risk operations.

Humans intervene only when necessary.

---

# 18. HITL with an AI Agent

This becomes much more interesting when an LLM is involved.

Imagine:

```text
                    User
                      ↓
                 AI Agent
                      ↓
              Decide what to do
                      ↓
              ┌──────────────┐
              │ Tool Call    │
              └──────┬───────┘
                     ↓
               Dangerous?
                ↙       ↘
              No         Yes
              ↓           ↓
          Execute      INTERRUPT
                          ↓
                       Human
                       ↙   ↘
                    Approve Reject
                      ↓      ↓
                   Execute  Stop
```

This is one of the most useful production patterns for agentic AI.

---

# 19. HITL before a tool call

Suppose we have:

```python
@tool
def delete_file(filename: str):
    ...
```

The agent wants to call:

```python
delete_file("important.pdf")
```

Instead of immediately executing the tool:

```text
Agent
 ↓
delete_file()
 ↓
DELETE
```

we can introduce:

```text
Agent
 ↓
Tool request
 ↓
Human approval
 ↓
Tool execution
```

This creates a **tool-level approval gate**.

---

# 20. Example

Conceptually:

```python
def delete_file_node(state):

    filename = state["filename"]

    approval = interrupt({
        "action": "delete_file",
        "filename": filename,
        "message": f"Delete {filename}?"
    })

    if not approval:
        return {
            "status": "cancelled"
        }

    delete_file(filename)

    return {
        "status": "deleted"
    }
```

This is safer than allowing the LLM to directly execute destructive operations.

---

# 21. Human can modify the action

HITL doesn't have to return only:

```python
True
```

You can return structured information.

For example:

```python
approval = interrupt({
    "action": "send_email",
    "to": "john@example.com",
    "subject": "Payment reminder",
    "body": "Please make your payment."
})
```

Human could respond:

```python
{
    "approved": True,
    "to": "jane@example.com"
}
```

Then:

```python
approval["to"]
```

becomes:

```text
jane@example.com
```

So the human can **correct the AI's proposed action**.

---

# 22. Approval vs correction

This gives us an important distinction.

### Approval

```text
AI:
Delete customer 123?

Human:
Yes
```

### Correction

```text
AI:
Send $1000 to Account A?

Human:
No.

Send $500 to Account B.
```

The second is more powerful because the human isn't merely a gatekeeper.

They become a **supervisor/editor**.

---

# 23. HITL for RAG

HITL can also be used in your RAG systems.

For example:

```text
User Question
      ↓
Retriever
      ↓
Retrieved Documents
      ↓
LLM
      ↓
Confidence low?
   ↙          ↘
 No           Yes
 ↓             ↓
Answer       Human Review
               ↓
            Correct answer
```

Suppose the RAG system retrieves:

```text
Document A
Document B
Document C
```

but the model isn't confident.

Instead of hallucinating:

```python
if confidence < 0.7:
    interrupt(...)
```

Human can review the retrieved context.

---

# 24. HITL for RAG feedback

A better architecture is:

```text
             User
               ↓
             RAG
               ↓
             Answer
               ↓
          Human Review
          ↙          ↘
      Correct        Wrong
        ↓              ↓
    Return answer   Modify answer
                       ↓
                   Return answer
```

The human feedback can also become training/evaluation data.

---

# 25. HITL for customer-support agents

This is a classic use case.

```text
Customer
   ↓
Support Agent
   ↓
Understand problem
   ↓
Can resolve automatically?
    ↙          ↘
   Yes          No
    ↓            ↓
Resolve       Human
                ↓
          Support Agent
                ↓
             Resolve
```

For example:

### Low risk

```text
"What are your business hours?"
```

AI answers automatically.

### High risk

```text
"I want a refund of $500."
```

Human approval may be required.

---

# 26. HITL + LangGraph persistence

This is one of the most important concepts.

Imagine:

```text
Monday 10:00 AM

Agent:
I need your approval.

Human:
```

The human doesn't respond until:

```text
Monday 3:00 PM
```

Your application shouldn't need to keep the Python function running for five hours.

Instead:

```text
10:00 AM
Agent
 ↓
interrupt()
 ↓
Checkpoint saved
 ↓
Execution ends
```

Later:

```text
3:00 PM
Human responds
 ↓
Command(resume=...)
 ↓
Checkpoint restored
 ↓
Graph continues
```

This is why **checkpointers are fundamental to practical HITL systems**.

---

# 27. Thread IDs

The `thread_id` is extremely important.

For example:

```python
config = {
    "configurable": {
        "thread_id": "conversation-123"
    }
}
```

Suppose you have:

```text
User A → thread-001
User B → thread-002
User C → thread-003
```

Each conversation has independent graph state.

```text
thread-001
   ↓
Agent state
   ↓
Human approval

thread-002
   ↓
Agent state
   ↓
Human approval
```

Without proper thread identification, you could resume the wrong workflow.

---

# 28. HITL in a web application

Suppose you're building:

```text
React / Next.js
       ↓
FastAPI
       ↓
LangGraph
       ↓
LLM
```

The workflow might be:

```text
React
 ↓
POST /chat
 ↓
LangGraph
 ↓
interrupt()
 ↓
API returns
"approval_required"
 ↓
React displays approval UI
```

For example:

```text
┌───────────────────────────────────────┐
│ AI wants to perform an action         │
│                                       │
│ Action: Delete user account           │
│ User: 12345                           │
│                                       │
│ [ Approve ]           [ Reject ]      │
└───────────────────────────────────────┘
```

When the user clicks:

```text
Approve
```

React sends:

```text
POST /resume
```

with:

```text
thread_id
decision
```

Backend:

```python
graph.invoke(
    Command(resume=True),
    config
)
```

---

# 29. HITL with Streamlit

Since Streamlit is useful for quickly prototyping AI systems, HITL works nicely conceptually there.

You can have:

```python
if approval_required:

    st.warning("Human approval required")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve"):
            # resume graph
            ...

    with col2:
        if st.button("Reject"):
            # resume graph
            ...
```

The important part is that the graph state is persisted using a checkpointer.

---

# 30. HITL with multiple humans

You can even design:

```text
Agent
 ↓
Manager approval
 ↓
Security approval
 ↓
Finance approval
 ↓
Execute
```

For example:

```text
Transfer $100,000
       ↓
Finance Manager
       ↓
Security Officer
       ↓
CEO
       ↓
Execute
```

LangGraph's graph structure makes this possible.

---

# 31. Multi-level approval

You can implement rules like:

```text
Amount < $100
    → Automatic

$100 - $1,000
    → Manager

$1,000 - $10,000
    → Finance

> $10,000
    → CEO
```

Graph:

```text
                   Transaction
                       ↓
                    Analyze
                       ↓
             ┌─────────┴─────────┐
             ↓                   ↓
          < $100              >= $100
             ↓                   ↓
          Execute          Determine level
                                ↓
                   ┌────────────┼────────────┐
                   ↓            ↓            ↓
                Manager       Finance        CEO
                   ↓            ↓            ↓
                   └────────────┼────────────┘
                                ↓
                             Execute
```

---

# 32. HITL and Agent Safety

HITL is particularly valuable for **high-impact actions**.

You can divide tools into categories:

### Read-only

```text
search()
retrieve()
get_weather()
get_user()
```

Usually safe.

### Write operations

```text
update_user()
create_invoice()
send_email()
```

Potentially require approval.

### Destructive operations

```text
delete_user()
delete_database()
transfer_money()
```

Strongly consider mandatory approval.

---

# 33. A useful production pattern

A strong architecture is:

```text
                     Agent
                       ↓
                  Tool request
                       ↓
                Risk assessment
                       ↓
            ┌──────────┴──────────┐
            ↓                     ↓
        Low Risk              High Risk
            ↓                     ↓
      Execute directly        INTERRUPT
                                  ↓
                              Human
                             ↙      ↘
                        Approve      Reject
                           ↓            ↓
                       Execute         Stop
```

This gives you:

**Autonomy + Safety**

rather than:

**Full autonomy** or **fully manual workflow**.

---

# 34. `interrupt()` and state updates

A subtle but important concept is that you should think carefully about **where the interrupt occurs**.

For example:

```python
def node(state):

    result = expensive_operation()

    approval = interrupt(...)

    return {
        "result": result
    }
```

When the graph resumes, the node execution semantics matter: the interrupted node is re-entered from the beginning rather than simply continuing from the exact Python line like a debugger breakpoint.

Therefore, avoid putting non-idempotent side effects before an interrupt unless they are designed safely.

For example, be careful with:

```python
def node(state):

    send_money()        # dangerous side effect

    approval = interrupt(...)
```

A safer design is:

```python
def node(state):

    approval = interrupt(...)

    if approval:
        send_money()

    return {}
```

This is a **very important LangGraph HITL design principle**.

---

# 35. Idempotency

Suppose:

```python
def execute_payment():
    payment_api.charge(...)
```

If a node can be re-entered after an interrupt or retry, you don't want:

```text
$100 charged
$100 charged again
```

Instead use an idempotency key:

```python
payment_id = state["payment_id"]

charge(
    amount=100,
    idempotency_key=payment_id
)
```

Then repeated execution can safely result in the same logical operation.

---

# 36. HITL is not just an approval button

This is worth remembering.

HITL can mean:

```text
Human approval
Human rejection
Human correction
Human input
Human selection
Human editing
Human escalation
Human verification
Human feedback
```

For example:

```python
interrupt({
    "type": "review",
    "draft": generated_text,
    "instructions": "Edit the draft if necessary."
})
```

The human can return:

```python
{
    "approved": True,
    "edited_text": "..."
}
```

---

# 37. HITL vs Human-in-the-Loop vs Human-on-the-Loop

These concepts are related but different.

### Human-in-the-loop

Human participates directly in the workflow.

```text
AI → Human → AI
```

Example:

> Approve this transaction.

---

### Human-on-the-loop

AI operates autonomously, while humans monitor it.

```text
AI
 ↓
AI
 ↓
AI
 ↓
Human monitors
```

Human intervention occurs only when necessary.

---

### Human-out-of-the-loop

Fully autonomous.

```text
AI → Action
```

No human intervention.

---

# 38. HITL vs traditional workflow

Traditional workflow:

```text
User
 ↓
Form
 ↓
Human
 ↓
Database
```

Agentic HITL:

```text
User
 ↓
AI Agent
 ↓
Reasoning
 ↓
Tool selection
 ↓
Human approval
 ↓
Tool execution
 ↓
Result
```

The difference is that AI can perform the **planning and reasoning**, while humans retain control over important decisions.

---

# 39. HITL with LangGraph + LangSmith

For production systems, it is useful to observe:

```text
User request
     ↓
Agent
     ↓
Tool selection
     ↓
Human approval
     ↓
Tool execution
```

You want visibility into:

* Which node ran
* Why an interrupt happened
* What the agent proposed
* What the human approved
* What the human rejected
* What tools were executed
* How long the workflow paused
* Whether the agent made repeated attempts

This is where **LangSmith observability/tracing** becomes valuable alongside LangGraph.

---

# 40. HITL mental model

The easiest way to remember it is:

```text
             ┌───────────────┐
             │     User      │
             └───────┬───────┘
                     ↓
             ┌───────────────┐
             │   LangGraph   │
             │     Agent     │
             └───────┬───────┘
                     ↓
                Make decision
                     ↓
             ┌───────────────┐
             │ Risk / Policy │
             └───────┬───────┘
                     ↓
             ┌───────┴───────┐
             ↓               ↓
          Safe            Sensitive
           ↓                 ↓
        Execute          INTERRUPT
                             ↓
                          Human
                         ↙     ↘
                    Approve    Reject
                       ↓          ↓
                    Execute     Stop
```

---

# 41. How HITL fits into what you're learning

Given the LangGraph concepts you've been working through, I'd place HITL here:

```text
LangChain
   │
   ├── Models
   ├── Prompts
   ├── Tools
   ├── Structured Output
   │
   ↓
LangGraph
   │
   ├── State
   ├── Nodes
   ├── Edges
   ├── Conditional Edges
   ├── Parallel Workflows
   ├── Iterative Workflows
   ├── Persistence
   ├── Checkpointing
   ├── Interrupts / HITL       ← YOU ARE HERE
   ├── Tool Calling
   ├── Subgraphs
   └── MCP
   │
   ↓
LangSmith
   ├── Tracing
   ├── Evaluation
   ├── Monitoring
   └── Debugging
```

The key relationship is:

> **Persistence + Checkpointing + Interrupts = practical HITL workflows in LangGraph.**

---

# 42. A project you should build

For your AI/ML portfolio, I'd recommend building an:

## **AI Financial Action Agent with Human Approval**

Architecture:

```text
                 User
                  ↓
              React UI
                  ↓
               FastAPI
                  ↓
             LangGraph
                  ↓
              AI Agent
                  ↓
        ┌─────────┼──────────┐
        ↓         ↓          ↓
      Search    Database   Calculator
                             
                  ↓
             Risk Checker
                  ↓
       ┌──────────┴──────────┐
       ↓                     ↓
   Safe action          Dangerous action
       ↓                     ↓
    Execute              INTERRUPT
                              ↓
                         User Approval
                         ↙          ↘
                     Approve       Reject
                        ↓             ↓
                     Execute        Stop
```

Example:

> "Transfer ₹50,000 to Ram."

Agent:

```text
Action detected:
Transfer ₹50,000

Risk: HIGH

Human approval required.
```

UI:

```text
┌────────────────────────────────────────┐
│       ⚠️ Approval Required             │
│                                        │
│ Action: Transfer Money                 │
│ Amount: ₹50,000                        │
│ Recipient: Ram                         │
│                                        │
│       [ Approve ]   [ Reject ]         │
└────────────────────────────────────────┘
```

Then the LangGraph resumes using:

```python
Command(resume=True)
```

This single project can demonstrate:

**LangGraph + Agents + Tool Calling + Persistence + HITL + FastAPI + React + LangSmith**

which is considerably stronger for a portfolio than a simple chatbot.

---

## The 6 things you should remember

If you're studying HITL for LangGraph, remember these six concepts:

1. **`interrupt()`** → pauses graph execution and requests external input.
2. **`Command(resume=...)`** → resumes an interrupted graph.
3. **Checkpointer** → persists graph state across the pause/resume lifecycle.
4. **`thread_id`** → identifies the specific workflow/conversation being resumed.
5. **Human input can be more than True/False** → humans can edit, correct, or provide data.
6. **Place interrupts before side effects** → design nodes carefully because interrupted nodes can be re-entered when resumed.

The core pattern is simply:

```python
def human_review(state):

    decision = interrupt({
        "message": "Approve this action?"
    })

    if decision:
        return {"approved": True}

    return {"approved": False}
```

followed by:

```python
graph.invoke(
    Command(resume=True),
    config
)
```

That is the fundamental building block from which you can construct much more sophisticated **human-supervised AI agents**.
