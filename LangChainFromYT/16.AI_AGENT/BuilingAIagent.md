# Building AI Agents with LangChain (Complete Guide)

An **AI Agent** is an application that uses an LLM (Large Language Model) to **reason, make decisions, use tools, remember information, and accomplish tasks autonomously**.

Unlike a simple chatbot that only generates text, an AI agent can:

* Think about the problem
* Decide which tools are needed
* Call APIs
* Search databases
* Read files
* Execute Python code
* Browse the web
* Use memory
* Continue until the goal is completed

---

# What is LangChain?

**LangChain** is a framework that helps developers build applications powered by LLMs.

It provides components for:

* LLMs
* Prompts
* Tools
* Agents
* Memory
* Retrieval
* RAG
* Vector databases
* Workflows
* Multi-agent systems

Think of LangChain as the **operating system for LLM applications**.

---

# Traditional LLM vs AI Agent

## Traditional LLM

```
User
   │
   ▼
Prompt
   │
   ▼
LLM
   │
   ▼
Response
```

Example

```
User:
What's 12 × 19?

LLM

Answer:
228
```

Only one interaction.

---

## AI Agent

```
User
 │
 ▼
Agent
 │
 ├── Think
 ├── Choose Tool
 ├── Execute Tool
 ├── Observe Result
 ├── Think Again
 └── Return Final Answer
```

The agent loops until it solves the task.

---

# AI Agent Workflow

```
          User
            │
            ▼
      Receive Goal
            │
            ▼
      LLM Reasons
            │
            ▼
  Does it need a Tool?
       /          \
     Yes           No
      │             │
      ▼             ▼
 Execute Tool    Answer
      │
      ▼
 Observe Result
      │
      ▼
 Think Again
      │
      ▼
Repeat Until Done
      │
      ▼
 Final Answer
```

This loop is the heart of an AI agent.

---

# Core Components of a LangChain Agent

```
Agent

├── LLM
├── Prompt
├── Tools
├── Memory
├── Output Parser
├── Agent Executor
└── Callbacks
```

Let's understand each.

---

# 1. LLM

The brain.

Example:

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0
)
```

The LLM performs reasoning.

It decides

* What tool to call
* When to stop
* How to answer

---

# 2. Prompt

The instructions given to the model.

Example

```
You are a helpful AI assistant.

You have access to these tools:

Search
Calculator

Use tools whenever necessary.
```

The prompt tells the agent how to behave.

---

# 3. Tools

Tools allow the LLM to interact with the outside world.

Without tools:

```
LLM
↓

Only text generation
```

With tools:

```
LLM
↓

Search
Calculator
Database
Email
Weather
SQL
Python
Filesystem
API
```

---

## Example Tool

```python
from langchain.tools import tool

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

---

Another tool

```python
@tool
def weather(city: str):
    """Returns weather."""
    return "28°C"
```

---

The agent sees

```
Tool:
weather(city)

Description:
Returns weather.
```

It decides when to use it.

---

# 4. Memory

Allows conversations across multiple interactions.

Without memory

```
User:
My name is John.

Later

What's my name?

LLM:
I don't know.
```

With memory

```
John
↓

Stored

↓

Retrieved later

↓

Answer:
Your name is John.
```

LangChain provides memory mechanisms, though newer versions often encourage managing conversation history explicitly rather than relying on legacy memory classes.

---

# 5. Agent Executor

This is the runtime.

```
Executor

↓

Runs Agent

↓

Calls tools

↓

Repeats

↓

Returns answer
```

Without the executor, the agent cannot execute tools.

---

# 6. Output Parser

Suppose the LLM outputs

```
Action:
Calculator

Input:
12 * 18
```

Parser converts it into

```python
calculator.invoke(...)
```

The parser translates the LLM's structured output into executable actions.

---

# How Tool Calling Works

Suppose the user asks

```
What is 19 × 27?
```

Flow

```
User
 │
 ▼
LLM

↓

I should use calculator.
```

LLM outputs

```python
tool_calls = [
    {
        "name": "calculator",
        "args": {
            "a":19,
            "b":27
        }
    }
]
```

Executor executes

```
calculator(19,27)

↓

513
```

Result goes back

```
LLM

↓

Final Answer:
513
```

---

# Modern LangChain Agent Architecture

```
User

↓

Chat Model

↓

Tool Calling

↓

Tool Execution

↓

Tool Results

↓

Chat Model

↓

Final Answer
```

Notice

The LLM itself decides tool calls.

This is called **native tool calling**.

Older approaches used ReAct parsing, while current chat models often support tool/function calling directly.

---

# Creating a Tool

```python
from langchain.tools import tool

@tool
def add(a:int,b:int)->int:
    """Add two numbers."""
    return a+b
```

Another

```python
@tool
def subtract(a:int,b:int)->int:
    """Subtract numbers."""
    return a-b
```

---

# Binding Tools

```python
llm_with_tools = llm.bind_tools([
    add,
    subtract
])
```

Now the LLM knows about these tools.

---

# Invoking

```python
from langchain_core.messages import HumanMessage

messages = [
    HumanMessage(
        "What is 10+25?"
    )
]

response = llm_with_tools.invoke(messages)
```

Possible output

```python
response.tool_calls
```

```
[
    {
        "name":"add",
        "args":{
            "a":10,
            "b":25
        }
    }
]
```

---

# Executing the Tool

```python
tool = {
    "add": add,
    "subtract": subtract
}

result = tool["add"].invoke(
    response.tool_calls[0]["args"]
)
```

Returns

```
35
```

---

# Returning Result to Model

```python
from langchain_core.messages import ToolMessage

messages.append(response)

messages.append(
    ToolMessage(
        content=str(result),
        tool_call_id=response.tool_calls[0]["id"]
    )
)

final = llm_with_tools.invoke(messages)
```

Now the LLM produces

```
The answer is 35.
```

---

# Complete Flow

```
User
 │
 ▼
HumanMessage
 │
 ▼
LLM
 │
 ▼
Tool Call
 │
 ▼
Python Tool
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
Final Answer
```

---

# Multiple Tool Calls

Example

```
Convert 10 USD to NPR.

First get exchange rate.

Then convert.
```

The LLM may generate

```python
[
    {
        "name":"get_conversion_factor"
    },
    {
        "name":"convert"
    }
]
```

However, this only happens if:

* The model supports multiple tool calls in a single response.
* The prompt encourages parallel or batched tool use.
* The second tool does not depend on the output of the first.

If `convert` needs the exchange rate returned by `get_conversion_factor`, most agents will call them **sequentially**, because the second call depends on the first result. This relates directly to the issue you encountered earlier.

---

# Agent Loop Example

User

```
What's the weather in Kathmandu?
```

Agent

```
Think

↓

Need weather tool

↓

Call weather()

↓

28°C

↓

Generate answer

↓

Done
```

---

# More Complex Example

User

```
Find the current USD→NPR exchange rate and tell me how much 250 USD is worth.
```

Agent

```
Think

↓

Search exchange rate

↓

Receive rate

↓

Calculator

↓

Generate answer

↓

Done
```

---

# LangGraph vs LangChain Agents

LangChain agents are excellent for straightforward tool-calling tasks, but as workflows become more complex, **LangGraph** provides more explicit control.

| LangChain Agent             | LangGraph                                                     |
| --------------------------- | ------------------------------------------------------------- |
| Automatic agent loop        | Explicit graph of nodes and edges                             |
| Easy to start               | More flexible and production-ready                            |
| Good for simple assistants  | Better for complex, stateful workflows                        |
| Less control over execution | Fine-grained control over branching, retries, and persistence |

A common progression is:

```
Simple chatbot
        ↓
Tool-calling LLM
        ↓
LangChain Agent
        ↓
LangGraph Workflow
        ↓
Multi-Agent System
```

---

# Best Practices

* Give every tool a clear and descriptive docstring—the model uses it to decide when to call the tool.
* Keep tools focused on a single responsibility.
* Validate tool inputs with type hints or Pydantic models when appropriate.
* Design tools to return structured, machine-readable data where possible.
* Handle errors gracefully and return informative messages.
* Use lower temperatures (e.g., `0`–`0.3`) for deterministic agent behavior.
* Prefer native tool calling with modern chat models over older text-parsing approaches.

---

# Learning Roadmap

To become proficient in building AI agents with LangChain:

1. Learn **Chat Models** (`ChatOpenAI`, message objects, prompts).
2. Learn **Prompt Templates** and message formatting.
3. Build and test **custom tools**.
4. Understand **tool calling** (`bind_tools`, `tool_calls`, `ToolMessage`).
5. Build a simple **single-agent** that can use multiple tools.
6. Learn **retrievers** and **RAG** for knowledge-grounded agents.
7. Add **memory** or conversation history management.
8. Move to **LangGraph** for multi-step, stateful workflows.
9. Explore **multi-agent systems** where specialized agents collaborate.
10. Deploy your agent with observability, logging, and evaluation.

---

## How This Relates to Your Previous LangChain Questions

Based on the questions you've asked recently, you're already working through many of the foundational concepts:

* Creating tools with `@tool`.
* Using `llm.bind_tools([...])`.
* Inspecting `response.tool_calls`.
* Invoking tools with `.invoke()`.
* Passing results back using `ToolMessage`.
* Understanding why dependent tools (like `get_conversion_factor` → `convert`) are typically executed sequentially rather than both being called immediately.

The next logical step is to build a **real AI agent** that can:

1. Reason about a user's request.
2. Call multiple tools when needed.
3. Maintain conversation history.
4. Retrieve information from documents (RAG).
5. Use LangGraph to orchestrate more complex workflows.

That progression will take you from simple tool calling to production-grade AI agents.
