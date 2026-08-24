# Tools in LangGraph — Detailed Guide

Tools are one of the most important concepts in **LangGraph**, because they are what allow an LLM-based application to move from **"just generating text"** to **actually doing things**.

A useful mental model is:

> **LLM = Brain**
> **Tool = Capability**
> **LangGraph = Orchestrator**

For example, an LLM may know *how* to answer:

> "What is the weather in Kathmandu?"

But it cannot inherently access live weather data. A weather API exposed as a **tool** gives it that capability.

---

# 1. What is a Tool?

A **tool** is a callable function that an LLM can request to execute.

For example:

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

This ordinary Python function becomes an LLM-callable tool.

The important part is:

```python
@tool
```

The decorator converts the function into a LangChain `Tool` object containing information such as:

* tool name
* description
* input schema
* function to execute

Conceptually:

```text
Tool
 ├── name
 ├── description
 ├── input schema
 └── function
```

---

# 2. Why Do We Need Tools?

An LLM by itself generally does something like:

```text
User
  ↓
LLM
  ↓
Text response
```

For example:

```text
User:
What is 25 × 17?

LLM:
25 × 17 = 425
```

But suppose you want the LLM to use an actual calculator:

```text
User
  ↓
LLM
  ↓
Calculator Tool
  ↓
Result
  ↓
LLM
  ↓
Final response
```

Now the application becomes an **agentic system**.

Tools allow an LLM to:

* search the web
* query databases
* call APIs
* perform calculations
* retrieve documents
* send emails
* create records
* update records
* execute business logic
* interact with external systems

---

# 3. Tool vs Normal Python Function

This distinction is important.

A normal Python function:

```python
def add(a, b):
    return a + b
```

is just a Python function.

A tool:

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

contains additional information that allows an LLM to understand how to use it.

For example:

```text
name:
add

description:
Add two numbers.

arguments:
a: integer
b: integer
```

The LLM can then decide:

> "I should call the `add` tool."

---

# 4. Creating a Tool

The modern LangChain approach is usually:

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

The **docstring is important**.

This:

```python
"""Add two numbers."""
```

helps the model understand when the tool should be used.

You should therefore write meaningful tool descriptions.

For example:

```python
@tool
def get_weather(city: str) -> str:
    """Get the current weather information for a given city."""
    ...
```

is much better than:

```python
@tool
def get_weather(city: str):
    """weather"""
    ...
```

---

# 5. Tool Input Schema

Consider:

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

The type annotations:

```python
a: int
b: int
```

help create the input schema.

Conceptually the model sees something similar to:

```json
{
  "name": "multiply",
  "description": "Multiply two numbers.",
  "parameters": {
    "a": "integer",
    "b": "integer"
  }
}
```

Therefore the LLM can generate a tool call such as:

```json
{
  "name": "multiply",
  "args": {
    "a": 10,
    "b": 20
  }
}
```

---

# 6. Binding Tools to the LLM

Creating a tool isn't enough.

You generally need to make the model aware of the available tools:

```python
tools = [add, multiply]

llm_with_tools = llm.bind_tools(tools)
```

Now the LLM knows:

```text
Available tools:
    add
    multiply
```

It can decide whether a tool is necessary.

---

# 7. Very Important: `bind_tools()` Does NOT Execute Tools

This is one of the most important concepts.

When you do:

```python
llm_with_tools = llm.bind_tools(tools)
```

you are essentially telling the model:

> "These tools are available to you."

You are **not** saying:

> "Execute these tools now."

For example:

```python
response = llm_with_tools.invoke(
    "What is 25 multiplied by 10?"
)
```

The model may return an AI message containing a tool call.

Conceptually:

```text
AIMessage
   |
   └── tool_calls
          |
          └── multiply(25, 10)
```

The tool still needs to be executed.

This is where **ToolNode** becomes important.

---

# 8. What is `ToolNode`?

`ToolNode` is a prebuilt LangGraph node designed to execute tools.

```python
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools)
```

If:

```python
tools = [add, multiply]
```

then:

```python
ToolNode(tools)
```

knows how to execute calls to those tools.

Conceptually:

```text
AIMessage
   |
   | tool_calls
   ↓
ToolNode
   |
   ├── add()
   ├── multiply()
   └── other tools
```

---

# 9. The Complete Tool-Calling Cycle

This is the most important architecture to understand.

Suppose the user asks:

> Calculate 25 × 17.

The graph can work like this:

```text
             ┌──────────────┐
             │    User      │
             └──────┬───────┘
                    ↓
             ┌──────────────┐
             │     LLM      │
             └──────┬───────┘
                    │
              Tool required?
               /          \
             Yes           No
              ↓             ↓
       ┌────────────┐   Final Answer
       │  ToolNode  │
       └──────┬─────┘
              ↓
       Tool execution
              ↓
       Tool result
              ↓
             LLM
              ↓
        Final Answer
```

For example:

```text
User:
25 × 17?

LLM:
Call multiply(25, 17)

ToolNode:
425

LLM:
25 × 17 = 425
```

---

# 10. Why LangGraph?

You could manually implement this loop:

```python
response = llm.invoke(...)

if response.tool_calls:
    execute_tools()

    response = llm.invoke(...)
```

But as applications become complicated, you might need:

* multiple tools
* multiple iterations
* conditional routing
* persistence
* human approval
* retries
* memory
* parallel execution
* error handling

This is where LangGraph becomes useful.

Instead of manually controlling everything, you model the process as a graph.

---

# 11. Basic Tool Graph

A typical graph looks like:

```text
       START
         ↓
       LLM
         ↓
   tools_condition
      /       \
   tools       END
     ↓
   LLM
```

In Python:

```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
```

Then:

```python
builder = StateGraph(MessagesState)

builder.add_node("llm", llm_node)
builder.add_node("tools", ToolNode(tools))
```

Add the conditional routing:

```python
builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "__end__",
    }
)
```

Then:

```python
builder.add_edge("tools", "llm")
```

Finally:

```python
graph = builder.compile()
```

---

# 12. What is `tools_condition`?

`tools_condition` is a prebuilt routing function.

It checks whether the latest AI message contains tool calls.

Conceptually:

```python
if last_message.tool_calls:
    return "tools"
else:
    return "__end__"
```

So:

```text
LLM
 │
 ├── tool call exists ──→ ToolNode
 │
 └── no tool call ──────→ END
```

This is why the graph can automatically determine whether it should execute tools.

---

# 13. Complete Example

Let's build a small calculator agent.

### Step 1 — Define tools

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

---

### Step 2 — Create tool list

```python
tools = [add, multiply]
```

---

### Step 3 — Bind tools to model

```python
llm_with_tools = llm.bind_tools(tools)
```

---

### Step 4 — Create LLM node

```python
from langchain_core.messages import SystemMessage

def llm_node(state):
    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }
```

---

### Step 5 — Create graph

```python
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)

builder.add_node("llm", llm_node)
builder.add_node("tools", ToolNode(tools))
```

---

### Step 6 — Add edges

```python
builder.set_entry_point("llm")

builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        "__end__": "__end__"
    }
)

builder.add_edge("tools", "llm")
```

---

### Step 7 — Compile

```python
graph = builder.compile()
```

---

### Step 8 — Invoke

```python
result = graph.invoke({
    "messages": [
        ("user", "What is 25 multiplied by 17?")
    ]
})
```

The execution becomes:

```text
User
 ↓
LLM
 ↓
multiply(25,17)
 ↓
ToolNode
 ↓
425
 ↓
LLM
 ↓
Final response
```

---

# 14. The Message Flow

Understanding messages is critical when working with tools.

Suppose the user says:

```text
What is 10 × 20?
```

The state initially contains:

```text
HumanMessage
    |
    └── "What is 10 × 20?"
```

The LLM produces:

```text
AIMessage
    |
    └── tool_call:
            name = multiply
            args = {
                a: 10,
                b: 20
            }
```

The `ToolNode` executes it.

Then the state gets:

```text
ToolMessage
    |
    └── "200"
```

The LLM sees the conversation:

```text
HumanMessage
    ↓
AIMessage(tool call)
    ↓
ToolMessage(result)
```

and generates:

```text
AIMessage
    ↓
"10 × 20 = 200"
```

So a simplified message sequence is:

```text
HumanMessage
      ↓
AIMessage(tool_call)
      ↓
ToolMessage
      ↓
AIMessage(final answer)
```

This pattern is extremely important for LangGraph.

---

# 15. Multiple Tools

You can give the LLM many tools.

```python
tools = [
    search_web,
    get_weather,
    calculate,
    get_user,
    create_order
]
```

Then:

```python
llm_with_tools = llm.bind_tools(tools)
```

The model decides which one to call based on the user's request.

For example:

```text
User:
What's the weather in Kathmandu?
```

LLM:

```text
get_weather("Kathmandu")
```

Whereas:

```text
User:
What is 123 × 456?
```

LLM:

```text
calculate(123, 456)
```

---

# 16. Multiple Tool Calls

An LLM can sometimes request multiple tools.

For example:

```text
User:
Get the weather in Kathmandu and Pokhara.
```

The model could produce:

```text
tool_calls:
    get_weather("Kathmandu")
    get_weather("Pokhara")
```

A `ToolNode` can handle tool calls from an AI message.

This becomes especially useful when tools are independent.

Conceptually:

```text
             AI
          /      \
         ↓        ↓
 Kathmandu      Pokhara
 weather        weather
     \            /
      \          /
       ToolNode
           ↓
          LLM
```

---

# 17. Tools Can Call APIs

A very common production pattern is wrapping an API inside a tool.

```python
import requests
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""

    response = requests.get(
        "https://example.com/weather",
        params={"city": city}
    )

    return response.text
```

Now the LLM doesn't need to know the API implementation.

It only knows:

```text
get_weather(city)
```

This gives you a clean separation:

```text
LLM
 ↓
Tool interface
 ↓
Python function
 ↓
REST API
 ↓
External service
```

---

# 18. Tools and Databases

Tools are particularly useful with databases.

For example:

```python
@tool
def get_user_balance(user_id: int) -> float:
    """Retrieve the current account balance for a user."""
    
    result = database.query(
        "SELECT balance FROM users WHERE id = ?",
        (user_id,)
    )

    return result[0]
```

The agent could receive:

```text
User:
What's my balance?
```

Then:

```text
LLM
 ↓
get_user_balance(...)
 ↓
Database
 ↓
ToolMessage
 ↓
LLM
 ↓
Answer
```

This pattern is very useful for applications such as:

* banking assistants
* e-commerce
* CRM systems
* expense trackers
* customer support systems

---

# 19. Tools and RAG

Tools can also be used for retrieval.

For example:

```python
@tool
def search_documents(query: str) -> str:
    """Search the knowledge base for relevant documents."""
    
    documents = retriever.invoke(query)

    return "\n".join(
        doc.page_content
        for doc in documents
    )
```

Now your LangGraph agent can decide:

```text
Question
   ↓
LLM
   ↓
Need company knowledge?
   ↓
search_documents()
   ↓
Vector DB
   ↓
Retrieved documents
   ↓
LLM
   ↓
Answer
```

This is one common way to combine **agents + RAG**.

---

# 20. Tools Are Not Only for Read Operations

A tool can also perform an action.

For example:

```python
@tool
def create_expense(
    title: str,
    amount: float
):
    """Create a new expense in the expense tracking system."""

    database.insert(
        title=title,
        amount=amount
    )

    return "Expense created successfully."
```

Then:

```text
User:
Add Rs. 500 for groceries.
```

The LLM can produce:

```text
create_expense(
    title="groceries",
    amount=500
)
```

The tool modifies the database.

This distinction is important:

### Read tools

```text
get_balance()
search_documents()
get_weather()
get_user()
```

### Action tools

```text
create_expense()
delete_user()
send_email()
create_order()
transfer_money()
```

Action tools should generally receive more careful validation and, for consequential operations, potentially human approval.

---

# 21. Tool Validation

Suppose you have:

```python
@tool
def transfer_money(
    from_account: str,
    to_account: str,
    amount: float
):
    ...
```

You don't want:

```text
amount = -1000000
```

or invalid account IDs.

For complex tools, you can use a structured schema.

For example, with Pydantic:

```python
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool

class TransferInput(BaseModel):
    from_account: str
    to_account: str
    amount: float = Field(gt=0)
```

Then your tool can validate its arguments before execution.

This is especially important for production systems.

---

# 22. Tool Errors

Tools can fail.

For example:

```python
@tool
def get_weather(city: str):
    response = requests.get(...)
    
    if response.status_code != 200:
        raise Exception("Weather API failed")

    return response.json()
```

Possible failures:

```text
API unavailable
Invalid input
Authentication failure
Database failure
Timeout
Rate limit
```

Your LangGraph architecture should account for these.

Conceptually:

```text
LLM
 ↓
ToolNode
 ↓
Tool fails
 ↓
Error handling
 ├── Retry
 ├── Return error to LLM
 └── Stop execution
```

---

# 23. Tool Retry

Some tools can be retried when failures are temporary.

For example:

```text
API timeout
     ↓
Retry
     ↓
Success
```

But you should **not blindly retry every tool**.

Consider:

```text
send_payment()
```

If the request succeeded but your application timed out before receiving the response, blindly retrying could potentially perform the action twice.

Therefore:

> Read-only tools are generally easier to retry than side-effecting tools.

---

# 24. Human Approval for Tools

This is an important LangGraph capability.

Imagine:

```text
User:
Transfer Rs. 50,000 to account XYZ.
```

You don't necessarily want:

```text
LLM → transfer_money()
```

without approval.

Instead:

```text
LLM
 ↓
transfer_money request
 ↓
Human approval
 ├── Approve → execute
 └── Reject  → stop
```

This is one of the areas where LangGraph's graph-based architecture becomes very useful.

---

# 25. Tools and State

LangGraph is fundamentally state-based.

For example:

```python
from langgraph.graph import MessagesState
```

Your state may contain:

```text
messages
user_id
cart
order_id
authentication
retrieved_documents
```

A tool can use information from the state depending on how you structure your nodes/tools.

For example:

```text
State
 ├── user_id
 ├── messages
 └── authentication
          ↓
       Tool
          ↓
      Database
```

This allows tools to operate within the context of the current graph execution.

---

# 26. Tools vs Nodes

This is a very important distinction.

### Node

A **node** is a component in your LangGraph workflow.

```python
builder.add_node("llm", llm_node)
```

### Tool

A **tool** is a callable capability that the LLM can request.

```python
@tool
def search(query):
    ...
```

### ToolNode

A **ToolNode** is a LangGraph node that executes tool calls.

```python
ToolNode(tools)
```

So:

```text
Tool
 ↓
Callable capability

ToolNode
 ↓
LangGraph node responsible for executing tools
```

---

# 27. Node vs Tool Example

Suppose you have:

```python
def analyze_expense(state):
    ...
```

This is a **node**.

The graph decides when it executes:

```text
Graph
 ↓
analyze_expense
```

But:

```python
@tool
def get_exchange_rate(currency: str):
    ...
```

is a **tool**.

The LLM can decide:

```text
LLM
 ↓
"I need exchange rate"
 ↓
get_exchange_rate()
```

So:

> **Nodes are controlled by the graph.**
> **Tools are typically requested by the LLM and executed by the graph.**

---

# 28. Tools vs Functions

Another useful distinction:

```text
Python Function
      ↓
Developer calls it
```

Whereas:

```text
Tool
      ↓
LLM can request it
```

For example:

```python
def calculate_tax(amount):
    ...
```

You call:

```python
calculate_tax(1000)
```

But with:

```python
@tool
def calculate_tax(amount: float):
    """Calculate tax for a given amount."""
    ...
```

the LLM can decide:

```text
Call calculate_tax
with amount=1000
```

---

# 29. Tool Calling vs Agent

These terms are related but not identical.

### Tool calling

The model produces a structured request:

```text
Call:
get_weather("Kathmandu")
```

### Agent

An agent can repeatedly reason and act:

```text
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
LLM
 ↓
Tool
 ↓
Final answer
```

LangGraph is especially useful for building these multi-step agentic workflows.

---

# 30. ReAct and Tools

A classic ReAct-style architecture looks like:

```text
Reason
  ↓
Action
  ↓
Observation
  ↓
Reason
  ↓
Action
  ↓
Observation
  ↓
Final Answer
```

In LangGraph:

```text
             ┌───────────────┐
             │      LLM      │
             └───────┬───────┘
                     ↓
                Tool call?
                /       \
              Yes        No
               ↓          ↓
          ┌─────────┐    END
          │ ToolNode│
          └────┬────┘
               ↓
          Tool result
               ↓
              LLM
```

The loop:

```text
LLM → ToolNode → LLM
```

is the key mechanism.

---

# 31. Example: Web Search Agent

Imagine:

```python
@tool
def search_web(query: str) -> str:
    """Search the internet for current information."""
    ...
```

Then:

```python
tools = [search_web]

llm_with_tools = llm.bind_tools(tools)
```

User:

```text
What are the latest developments in LangGraph?
```

The model may decide:

```text
search_web(
    "latest developments in LangGraph"
)
```

The ToolNode executes the search.

Then:

```text
Search result
 ↓
LLM
 ↓
Summary
```

This is a basic research agent.

---

# 32. Example: Expense Tracker Agent

This is particularly useful for understanding real-world tool architecture.

Suppose your application has:

```python
@tool
def add_expense(
    category: str,
    amount: float,
    description: str
):
    """Add an expense to the user's expense tracker."""
    ...


@tool
def get_expenses():
    """Retrieve the user's recent expenses."""
    ...


@tool
def get_monthly_summary():
    """Return the current month's expense summary."""
    ...
```

Now the user could say:

```text
I spent Rs. 800 on dinner.
```

LLM:

```text
add_expense(
    category="Food",
    amount=800,
    description="Dinner"
)
```

Or:

```text
How much have I spent this month?
```

LLM:

```text
get_monthly_summary()
```

This is a very realistic architecture for an AI-powered expense tracker.

---

# 33. Tool Description Matters a Lot

Consider:

```python
@tool
def search(query: str):
    """Search the web."""
```

versus:

```python
@tool
def search(query: str):
    """
    Search the internet for current information.

    Use this tool when the user asks for:
    - recent events
    - current information
    - information that may have changed
    """
```

The second description gives the model much better guidance.

Tool descriptions effectively become part of the model's decision-making context.

---

# 34. Tool Naming Matters

Prefer:

```python
get_weather
search_documents
create_expense
get_user_balance
delete_expense
```

instead of:

```python
tool1
tool2
function_a
function_b
```

Good names help the LLM choose the correct tool.

---

# 35. Tool Granularity

Don't make one enormous tool:

```python
@tool
def do_everything(...):
    ...
```

Instead, use focused tools:

```text
get_user()
get_expenses()
create_expense()
update_expense()
delete_expense()
```

This gives the model clearer choices.

However, don't split functionality unnecessarily either.

A good tool should represent a meaningful operation.

---

# 36. Tool Security

This is extremely important.

Never assume:

```text
LLM-generated tool call = trusted input
```

It isn't.

For example:

```python
@tool
def delete_user(user_id: str):
    ...
```

should not blindly trust the model.

You should validate:

```text
Is user_id valid?
        ↓
Does current user own this resource?
        ↓
Is the operation allowed?
        ↓
Does the user need confirmation?
        ↓
Execute
```

The LLM should decide **what it wants to do**, but your application should enforce **what it is actually allowed to do**.

---

# 37. Read Tools vs Write Tools

A useful production classification is:

### Read-only

```text
search()
get_user()
get_balance()
get_weather()
query_database()
```

Generally lower risk.

### Write/action

```text
create_order()
delete_file()
send_email()
transfer_money()
delete_user()
```

Potentially high risk.

For action tools, consider:

* validation
* authorization
* confirmation
* idempotency
* audit logs
* rate limiting

---

# 38. Tool Architecture in Production

A production LangGraph agent might look like:

```text
                     User
                       ↓
                  LangGraph
                       ↓
                  ┌────────┐
                  │   LLM  │
                  └───┬────┘
                      ↓
              Tool decision
                      ↓
              ┌───────┴────────┐
              ↓                ↓
         Search Tool       DB Tool
              ↓                ↓
          Search API       PostgreSQL
              ↓                ↓
              └───────┬────────┘
                      ↓
                     LLM
                      ↓
                 Final Answer
```

And around this you can add:

```text
Persistence
   ↓
Checkpointing

Observability
   ↓
LangSmith

Security
   ↓
Authorization

Human approval
   ↓
Interrupts

Error handling
   ↓
Retries
```

---

# 39. Tools + LangSmith

Since you've been studying **LangSmith + LangGraph**, tools are especially important for observability.

A LangSmith trace can show:

```text
LangGraph Run
│
├── LLM
│    └── tool_call: search_web
│
├── ToolNode
│    └── search_web
│
├── LLM
│
└── Final Response
```

This allows you to investigate:

* Which tool was called?
* Why was it called?
* What arguments were passed?
* How long did the tool take?
* Did the tool fail?
* What did the tool return?
* How many tools were called?
* How many tokens were used around the calls?

This is extremely useful when debugging agents.

---

# 40. The Most Important Concepts to Remember

If you're learning LangGraph, I recommend remembering this chain:

```text
@tool
   ↓
Create tool
   ↓
bind_tools()
   ↓
LLM knows about tools
   ↓
LLM generates tool_call
   ↓
ToolNode
   ↓
Tool executes
   ↓
ToolMessage
   ↓
LLM receives result
   ↓
Final answer
```

And the graph:

```text
                 ┌─────────────┐
                 │     LLM     │
                 └──────┬──────┘
                        ↓
                 ┌──────────────┐
                 │ Tool needed? │
                 └──────┬───────┘
                    Yes │ No
                        │  └────────→ END
                        ↓
                 ┌────────────┐
                 │  ToolNode  │
                 └──────┬─────┘
                        ↓
                   Tool result
                        ↓
                       LLM
                        │
                        └─────────→ ...
```

### The four things you should clearly distinguish

| Concept           | Purpose                                            |
| ----------------- | -------------------------------------------------- |
| `@tool`           | Converts a function into an LLM-callable tool      |
| `bind_tools()`    | Makes the LLM aware of available tools             |
| `ToolNode`        | Executes tool calls inside the LangGraph           |
| `tools_condition` | Routes the graph based on whether tool calls exist |

Once these four concepts are clear, **tool-calling agents in LangGraph become much easier to understand**.

A natural next step is to study **`ToolNode` in depth**, including its execution behavior, multiple tool calls, tool errors, custom tool nodes, state injection, runtime/context access, and how tools interact with LangGraph's `Command` and `interrupt()` mechanisms.
