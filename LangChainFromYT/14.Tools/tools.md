# Tools in LangChain (Complete Guide)

Tools are one of the **most important concepts** in LangChain. They allow an LLM to interact with the outside world instead of relying only on the knowledge it learned during training.

Think of an LLM as a very intelligent person sitting in a room with no internet, calculator, or computer. It can answer many questions, but if you ask:

* "What's today's weather?"
* "Calculate 987654 × 123456."
* "Search the web for OpenAI's latest announcement."

It cannot do these reliably by itself.

**Tools solve this problem.**

---

# What is a Tool?

A **Tool** is a Python function (or API) that an AI model can call to perform a specific task.

Instead of generating an answer directly, the model decides:

> "I should use this tool."

The tool runs.

The result is returned to the model.

The model uses that result to produce the final response.

## Without Tools

```
User
 │
 ▼
LLM
 │
 ▼
Answer
```

The LLM only uses its internal knowledge.

---

## With Tools

```
User
 │
 ▼
LLM
 │
 ▼
Should I use a tool?
 │
 ├── No
 │      │
 │      ▼
 │   Final Answer
 │
 └── Yes
        │
        ▼
     Tool Executes
        │
        ▼
   Tool Output
        │
        ▼
      LLM
        │
        ▼
   Final Answer
```

---

# Why do we need Tools?

LLMs cannot reliably:

* Search the internet
* Read files
* Use databases
* Perform precise calculations
* Execute Python code
* Access company APIs
* Send emails
* Query SQL databases
* Control applications

Tools enable all of these.

---

# Examples

## Example 1: Calculator Tool

User:

```
What is 85793 × 9876?
```

Without tool:

```
LLM guesses.
```

With tool:

```
Calculator executes

85793 * 9876

↓

847092468
```

LLM responds:

```
The answer is 847,092,468.
```

---

## Example 2: Weather Tool

User

```
Weather in Kathmandu?
```

LLM

```
Uses Weather Tool
```

Weather API returns

```
24°C
Cloudy
Humidity 61%
```

LLM formats the answer nicely.

---

## Example 3: Database Tool

User

```
How many employees work in HR?
```

LLM

```
Uses SQL Tool
```

SQL

```sql
SELECT COUNT(*)
FROM employees
WHERE department='HR';
```

Returns

```
18
```

LLM

```
18 employees work in HR.
```

---

# Components of a Tool

A tool consists of

```
Name

Description

Function

Arguments

Return value
```

Example

```python
def calculator(a: int, b: int):
    return a * b
```

Name

```
calculator
```

Description

```
Multiply two numbers
```

Arguments

```
a
b
```

Return

```
product
```

---

# Creating Tools

There are three common ways.

## Method 1: @tool Decorator (Recommended)

```python
from langchain.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b
```

The docstring is important.

```
"""Multiply two integers."""
```

The LLM reads this description to decide when to use the tool.

---

## Using the Tool

```python
multiply.invoke({"a":5, "b":4})
```

Output

```
20
```

---

# Method 2: StructuredTool

Useful when your function has many parameters.

```python
from langchain.tools import StructuredTool

def add(a: int, b: int):
    return a + b

tool = StructuredTool.from_function(
    func=add,
    name="Addition",
    description="Adds two numbers"
)
```

---

# Method 3: BaseTool

Best for advanced users.

```python
from langchain.tools import BaseTool

class MultiplyTool(BaseTool):

    name = "multiply"

    description = "Multiply two integers"

    def _run(self, a: int, b: int):
        return a * b
```

Used when:

* custom validation
* authentication
* APIs
* async logic
* logging

---

# Tool Anatomy

```
@tool
def search(query: str):

    """
    Search Wikipedia
    """

    return result
```

LangChain extracts:

```
Tool Name:
search

Description:
Search Wikipedia

Input:
query

Output:
search results
```

---

# Why Description Matters

Suppose two tools exist.

Tool A

```
weather()
```

Description

```
Returns weather
```

Tool B

```
news()
```

Description

```
Returns latest news
```

User asks

```
Will it rain tomorrow?
```

The LLM reads the descriptions and chooses

```
weather()
```

---

# Input Schema

Tools often define expected inputs.

```python
from pydantic import BaseModel

class MultiplyInput(BaseModel):
    a: int
    b: int
```

Tool

```python
@tool(args_schema=MultiplyInput)
def multiply(a: int, b: int):
    """Multiply numbers"""
    return a * b
```

Now invalid inputs are caught automatically.

---

# Return Types

A tool can return

String

```python
return "Sunny"
```

Number

```python
return 42
```

Dictionary

```python
return {
    "temp":24,
    "humidity":60
}
```

List

```python
return ["AI","ML","Python"]
```

---

# Tool Calling Process

Suppose

```
User:

Multiply 25 by 18
```

Step 1

LLM thinks

```
Need multiplication.
```

↓

Step 2

Calls

```
multiply(25,18)
```

↓

Step 3

Tool executes

```
450
```

↓

Step 4

LLM

```
25 × 18 = 450
```

---

# Multiple Tools

You can provide many tools.

```python
tools = [
    calculator,
    search,
    weather,
    sql,
    wikipedia
]
```

The LLM decides which to use.

---

# Toolkits

Instead of individual tools, LangChain also provides **toolkits**, which are collections of related tools.

Examples include:

* SQL Toolkit
* File Management Toolkit
* Gmail Toolkit
* GitHub Toolkit

Example:

```
SQL Toolkit

├── Execute SQL
├── List Tables
├── Get Schema
└── Query Checker
```

---

# Built-in Tools

Some commonly used tools include:

## Search

```
Search the web
```

## Wikipedia

```
Look up encyclopedia information
```

## SQL Database

```
Execute SQL queries
```

## Python REPL

```
Run Python code
```

## File Management

```
Read/write/delete files
```

## Requests

```
Call REST APIs
```

---

# Custom Tool Example

Suppose we want an area calculator.

```python
from langchain.tools import tool

@tool
def rectangle_area(length: float, width: float):
    """Calculate rectangle area."""
    return length * width
```

Invoke

```python
rectangle_area.invoke({
    "length":5,
    "width":7
})
```

Output

```
35
```

---

# Tool vs Function

| Function                  | Tool                                    |
| ------------------------- | --------------------------------------- |
| Python function           | LLM-aware function                      |
| No metadata               | Has name and description                |
| Cannot be selected by LLM | LLM can decide when to use it           |
| Standard Python           | Integrated with LangChain agents/models |

---

# Tools vs Chains vs Agents

This is one of the most common points of confusion.

| Feature             | Tool                        | Chain                             | Agent                                         |
| ------------------- | --------------------------- | --------------------------------- | --------------------------------------------- |
| Purpose             | Perform one specific action | Execute a fixed sequence of steps | Decide dynamically which actions to take      |
| Decision-making     | No                          | No                                | Yes                                           |
| Calls external APIs | Yes                         | Can                               | Yes                                           |
| Uses multiple tools | No                          | Usually fixed                     | Yes, dynamically                              |
| Example             | Weather lookup              | Prompt → LLM → Output             | Search → Calculator → Database → Final answer |

Relationship:

```
           Agent
             │
      chooses tools
             │
     ┌───────┴────────┐
     ▼                ▼
 Search Tool      Calculator Tool
     ▼                ▼
 Results         Computation
      └───────┬────────┘
              ▼
             LLM
              ▼
         Final Response
```

---

# Tools in Modern LangChain (v0.2+ / v1)

Modern LangChain encourages using tools together with **LangGraph** agents. A typical workflow is:

```python
from langchain.tools import tool

@tool
def get_stock_price(symbol: str) -> str:
    """Return the latest stock price for a symbol."""
    # Call an API here
    return f"{symbol}: $123.45"
```

You then pass the tool to an agent created with LangGraph or LangChain's agent APIs. The model can inspect the tool's name, description, and input schema to decide when to call it.

---

# Best Practices

1. Write clear, specific docstrings—models rely on them to choose the correct tool.
2. Use type hints and `args_schema` (Pydantic) for reliable input validation.
3. Design each tool to do one thing well.
4. Handle exceptions and return informative error messages.
5. Avoid exposing sensitive operations (deleting files, sending emails, etc.) without appropriate safeguards.
6. Keep tools deterministic when possible so the model receives predictable outputs.

---

# Real-World Example: Travel Assistant

Imagine a travel assistant with four tools:

* `search_flights()`
* `search_hotels()`
* `get_weather()`
* `currency_converter()`

User:

> "I'm flying to Tokyo next week. Find a hotel and tell me whether I should pack an umbrella."

The agent might execute this sequence:

1. Use `search_hotels()` to find available accommodations.
2. Use `get_weather()` to retrieve the forecast.
3. Optionally use `currency_converter()` if the user asks about costs.
4. Combine the results into a single natural-language response.

The intelligence lies in the agent's ability to choose the right tools at the right time.

---

# Summary

* **Tools** let an LLM interact with external systems and perform actions beyond text generation.
* A tool is typically a Python function enriched with metadata (name, description, input schema).
* You can create tools using `@tool`, `StructuredTool`, or by subclassing `BaseTool`.
* Good descriptions and type annotations are critical because the model uses them to decide when and how to call a tool.
* Agents orchestrate tools dynamically, while chains follow predefined workflows.
* In modern LangChain, tools are most commonly used with LangGraph-based agents to build capable AI assistants that can search, calculate, query databases, call APIs, and automate tasks.
