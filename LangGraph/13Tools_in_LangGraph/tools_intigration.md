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
