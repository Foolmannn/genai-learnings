# Tool Calling in LangChain (Complete Guide)

Tool calling is one of the most important features in modern LLM applications. It allows an LLM to **use external functions, APIs, databases, calculators, search engines, or any Python function** whenever it needs information that it cannot generate by itself.

Think of it like this:

* **Without tools:** LLM can only generate text from its training.
* **With tools:** LLM can interact with the real world.

For example:

```
User
 ↓
LLM
 ↓
"I need weather information."
 ↓
Weather Tool
 ↓
Temperature = 27°C
 ↓
LLM
 ↓
"The weather is 27°C."
```

---

# Why Tool Calling?

Suppose you ask:

> What is 987654 × 876543?

An LLM may calculate incorrectly.

Instead it can use

```
Calculator Tool
```

Similarly,

If you ask

> What is today's stock price of Apple?

The LLM cannot know because its knowledge isn't always live.

Instead it can call

```
Stock API
```

---

# Real World Examples

Imagine building an AI assistant.

User asks

```
Book a flight.
```

The LLM cannot actually book flights.

Instead

```
LLM
      ↓
Flight Search Tool
      ↓
Available flights
      ↓
LLM
      ↓
Reply to user
```

---

User asks

```
Send an email.
```

LLM

↓

Email Tool

↓

Email Sent

↓

LLM

↓

Confirmation

---

# What is a Tool?

A tool is simply a Python function with

* name
* description
* input schema

For example

```python
def multiply(a: int, b: int):
    return a * b
```

This function becomes a tool.

The LLM reads the description and decides when to use it.

---

# LangChain Tool Architecture

```
               User
                 │
                 ▼
         Chat Model (LLM)
                 │
     Decides whether tool is needed
                 │
        ┌────────┴────────┐
        │                 │
      No Tool          Tool Needed
        │                 │
        ▼                 ▼
   Generate Text      Call Tool
                            │
                            ▼
                     Execute Python
                            │
                            ▼
                     Return Result
                            │
                            ▼
                       LLM Response
```

---

# Components

There are four major components.

## 1. LLM

Example

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1"
)
```

---

## 2. Tool

Example

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int):
    """Adds two integers."""
    return a + b
```

Notice

The docstring becomes the tool description.

---

## 3. Tool Executor

Responsible for actually running the function.

```
LLM says

Call add(4,5)

↓

Python executes

↓

Returns 9
```

---

## 4. Tool Message

The result is wrapped into a ToolMessage and returned to the model.

```
Tool Result

↓

ToolMessage

↓

LLM

↓

Final Answer
```

---

# Creating Your First Tool

```python
from langchain_core.tools import tool

@tool
def multiply(a: int, b: int):
    """
    Multiply two integers.
    """
    return a * b
```

Now

```python
print(multiply.name)
```

Output

```
multiply
```

Description

```python
print(multiply.description)
```

Output

```
Multiply two integers.
```

Schema

```python
print(multiply.args)
```

Output

```python
{
 'a': {'type': 'integer'},
 'b': {'type': 'integer'}
}
```

---

# Multiple Tools

```python
@tool
def add(a:int,b:int):
    """Add numbers"""
    return a+b


@tool
def subtract(a:int,b:int):
    """Subtract numbers"""
    return a-b


@tool
def multiply(a:int,b:int):
    """Multiply numbers"""
    return a*b
```

Collect them

```python
tools = [add, subtract, multiply]
```

---

# Binding Tools to LLM

Modern LangChain

```python
llm_with_tools = llm.bind_tools(tools)
```

Now the model knows

* Tool names
* Descriptions
* Arguments

---

# What Happens Internally?

Suppose

```
User:
Multiply 12 and 50
```

The prompt sent to the LLM is roughly

```
You have access to

Tool:
multiply

Arguments:
a
b

Description:
Multiply numbers.
```

The model decides

```
Call multiply
```

instead of replying directly.

---

# Invoking the Model

```python
response = llm_with_tools.invoke(
    "Multiply 12 and 50"
)
```

The output is **not**

```
600
```

Instead

```python
AIMessage(
    tool_calls=[
        {
            "name":"multiply",
            "args":{
                "a":12,
                "b":50
            }
        }
    ]
)
```

The LLM is **requesting** that the tool be executed—it does not execute it itself.

---

# Executing the Tool

```python
tool_call = response.tool_calls[0]

result = multiply.invoke(tool_call["args"])

print(result)
```

Output

```
600
```

---

# Returning Result to LLM

Now create a ToolMessage.

```python
from langchain_core.messages import ToolMessage

tool_message = ToolMessage(
    content=str(result),
    tool_call_id=tool_call["id"]
)
```

Then

```python
final = llm.invoke([
    response,
    tool_message
])
```

Output

```
The answer is 600.
```

---

# Complete Flow

```
User
 │
 ▼
LLM
 │
 ▼
Needs Tool?
 │
 ├──No────────►Answer
 │
 │
 Yes
 │
 ▼
Generate Tool Call
 │
 ▼
Python Executes Tool
 │
 ▼
Tool Result
 │
 ▼
ToolMessage
 │
 ▼
LLM
 │
 ▼
Final Response
```

---

# Using `tool.invoke()`

You asked previously if tools behave like normal functions.

Suppose

```python
tool.invoke({"a":10,"b":20})
```

works.

Can you do

```python
tool.invoke(10,20)
```

**No.**

`invoke()` expects a **single input object**, usually a dictionary matching the tool's schema.

If you want to call it like a regular Python function, use the underlying function:

```python
multiply.func(10, 20)
```

or simply call the original function before decorating (if you still have a reference to it).

With the `@tool` decorator, the recommended interface inside LangChain is:

```python
multiply.invoke({"a": 10, "b": 20})
```

because it supports validation, serialization, and integration with agents.

---

# Structured Tools

Instead of simple arguments

```python
@tool
def weather(city:str):
    """Get weather."""
```

you can define a schema using Pydantic.

```python
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    city: str = Field(description="City name")

@tool(args_schema=WeatherInput)
def weather(city:str):
    return "28°C"
```

Benefits:

* Better validation
* Better descriptions
* Required fields
* Optional fields
* Type checking

---

# Toolkits

LangChain also provides **toolkits**, which are collections of related tools. For example:

```python
from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()
```

You explored something similar with `MathToolkit`:

```python
toolkit = MathToolkit()
tools = toolkit.get_tools()

for tool in tools:
    print(tool.name)
    print(tool.description)
```

Each returned tool is still a standard LangChain tool and can be bound to an LLM with `bind_tools()`.

---

# Tool Calling vs Agent

| Tool Calling                                        | Agent                                         |
| --------------------------------------------------- | --------------------------------------------- |
| One tool call (or a fixed sequence you orchestrate) | Can plan and call multiple tools autonomously |
| You control the execution loop                      | The agent manages the loop                    |
| Easier to debug                                     | More flexible but more complex                |
| Best for deterministic workflows                    | Best for open-ended tasks                     |

Example:

**Tool Calling**

```
User
↓

LLM
↓

Calculator

↓

Answer
```

**Agent**

```
User

↓

Search

↓

Calculator

↓

Database

↓

Email

↓

Final Answer
```

An agent repeatedly reasons about whether another tool is needed until it decides it has enough information.

---

# Best Practices

* Write clear, specific docstrings—LLMs rely heavily on them to decide when to use a tool.
* Use precise type hints and, for complex inputs, Pydantic schemas.
* Keep each tool focused on a single responsibility.
* Validate inputs and handle exceptions gracefully.
* Return structured data (e.g., dictionaries) when appropriate, rather than long formatted strings.
* Prefer explicit tool calling for predictable workflows and agents for tasks that require planning across multiple tools.

## Summary

Tool calling in LangChain follows a simple lifecycle:

1. Define one or more tools (Python functions decorated with `@tool`).
2. Bind them to a chat model using `llm.bind_tools(tools)`.
3. Invoke the model with a user query.
4. If the model returns `tool_calls`, execute the requested tool(s).
5. Send the tool result back to the model as a `ToolMessage`.
6. The model generates the final natural-language response.

Understanding this flow is fundamental to building AI assistants that can search the web, query databases, perform calculations, call APIs, or interact with external systems. Once you're comfortable with tool calling, the next natural step is learning **LangGraph**, which builds on the same concepts to orchestrate complex, multi-step AI workflows.
