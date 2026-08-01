Since **LangChain v1**, the way you build ReAct agents has changed significantly.

> **Old approach (deprecated):**
>
> ```python
> from langgraph.prebuilt import create_react_agent
> ```
>
> **Modern approach (recommended):**
>
> ```python
> from langchain.agents import create_agent
> ```
>
> The new `create_agent` API is built **on top of LangGraph**, so you still get the ReAct execution loop, but with a cleaner API, middleware, better extensibility, streaming, persistence, and human-in-the-loop support. ([Docs by LangChain][1])

Let's understand the **ReAct Agent Design Pattern** from first principles and then see how it fits into the modern LangChain ecosystem.

---

# 1. What is ReAct?

ReAct stands for

> **Re**ason + **Act**

It was introduced in the paper

**ReAct: Synergizing Reasoning and Acting in Language Models**. ([arXiv][2])

Instead of asking the LLM to immediately answer,

the LLM repeatedly performs

```
Reason
↓

Choose Action

↓

Execute Tool

↓

Observe Result

↓

Reason Again

↓

Choose Next Action

↓

...

↓

Final Answer
```

Instead of

```
Question
↓

Answer
```

it becomes

```
Question

↓

Think

↓

Search

↓

Read result

↓

Think

↓

Calculator

↓

Think

↓

Final answer
```

This dramatically reduces hallucinations because the model can verify information by interacting with tools.

---

# 2. Why do we need ReAct?

Suppose the user asks

> What is the weather in Kathmandu and should I carry an umbrella?

A plain LLM might guess.

A ReAct agent instead does

```
Thought:
I need weather information.

↓

Action:
weather_tool("Kathmandu")

↓

Observation:
Rain expected.

↓

Thought:
Rain means umbrella is recommended.

↓

Final Answer:
Yes, carry an umbrella.
```

Notice the loop.

Reasoning drives tool usage.

---

# 3. The Core ReAct Loop

The heart of every ReAct agent is

```
             +--------------------+
             |    User Question   |
             +---------+----------+
                       |
                       v
             +--------------------+
             |        LLM         |
             |  Decide next step  |
             +---------+----------+
                       |
        tool call?     |      final answer?
              Yes      |          No
                       |
                       v
             +--------------------+
             |      Tool Node     |
             +---------+----------+
                       |
                 Tool Result
                       |
                       v
             +--------------------+
             |   Add Observation  |
             +---------+----------+
                       |
                       |
                 Back to LLM
```

This continues until

```
No more tool calls
```

then

```
Return Final Answer
```

---

# 4. Modern LangChain Architecture

Today, a ReAct agent is actually a **LangGraph**.

```
create_agent()

↓

Builds a LangGraph

↓

Graph executes nodes

↓

LLM Node

↓

Tool Node

↓

LLM Node

↓

Tool Node

↓

Final Response
```

So

```
LangChain
      │
      ▼
create_agent()
      │
      ▼
LangGraph Runtime
      │
      ▼
ReAct Loop
```

The user writes very little code while LangGraph handles orchestration underneath. ([Docs by LangChain][3])

---

# 5. Internal Components

A ReAct agent contains five major parts.

```
User
↓

Messages

↓

LLM

↓

Tools

↓

Memory / State
```

Let's examine each.

---

## A. User

Example

```
"What is the capital of Nepal?"
```

---

## B. Messages

The conversation history.

```
HumanMessage

↓

AIMessage

↓

ToolMessage

↓

AIMessage

↓

ToolMessage

↓

Final AIMessage
```

The entire history is sent back to the model every iteration.

---

## C. Model

The LLM decides

```
Should I answer?

OR

Should I call a tool?
```

Example

```
Need search.

Call search tool.
```

---

## D. Tool Node

If the model requests

```
search("capital of Nepal")
```

the Tool Node executes

```
Google Search

↓

Result

↓

Returns ToolMessage
```

---

## E. State

State stores

```
messages

tool outputs

metadata

context

iteration count
```

LangGraph updates this state after every step.

---

# 6. Complete Execution

Suppose

```
User:
Who won the latest FIFA World Cup?
```

The execution looks like

```
User

↓

LLM

↓

Need search

↓

Search Tool

↓

Observation

↓

LLM

↓

Need confirmation

↓

Wikipedia Tool

↓

Observation

↓

LLM

↓

Final Answer
```

---

# 7. What create_agent() Actually Builds

Internally,

```
agent = create_agent(...)
```

constructs something conceptually similar to

```
START

↓

Model Node

↓

Any tool calls?

↓

Yes ------------------+
 |                    |
 |                    |
Tool Node             |
 |                    |
 +--------------------+

↓

Model Node

↓

No Tool Calls

↓

END
```

That graph is compiled and executed automatically. The older `create_react_agent` built a similar graph but is now deprecated in favor of `create_agent`. ([LangChain Reference][4])

---

# 8. Example

Imagine two tools.

```
Weather Tool

Calculator Tool
```

User asks

```
If Kathmandu is 20°C today,
what is that in Fahrenheit?
```

Execution

```
LLM

↓

Weather Tool

↓

20°C

↓

LLM

↓

Calculator Tool

↓

68°F

↓

LLM

↓

Answer
```

Multiple tool calls happen naturally as part of the ReAct loop.

---

# 9. Message Flow

```
Human:
Weather in Pokhara?

↓

AI:
tool_call(weather)

↓

Tool:
Sunny

↓

AI:
The weather is sunny.
```

Message history

```
HumanMessage

↓

AIMessage(tool_call)

↓

ToolMessage

↓

AIMessage(final)
```

This history is exactly what the model reasons over.

---

# 10. Why is LangGraph Involved?

Before LangGraph

```
LLM

↓

if tool

↓

call tool

↓

repeat
```

Developers had to manually manage the loop.

Today

```
LangGraph Runtime

↓

Runs graph

↓

Maintains state

↓

Retries

↓

Streams

↓

Checkpointing

↓

Interrupts

↓

Human approval
```

The graph runtime manages the orchestration automatically. ([Docs by LangChain][1])

---

# 11. Modern Agent Stack

```
Application

↓

create_agent()

↓

Middleware

↓

LLM

↓

Tool Node

↓

State

↓

LangGraph Runtime
```

Middleware is one of the biggest improvements in LangChain v1, replacing many older hook APIs. ([Docs by LangChain][5])

---

# 12. ReAct vs Simple Tool Calling

## Tool Calling

```
User

↓

LLM

↓

Tool

↓

Answer
```

Only one reasoning step.

---

## ReAct

```
User

↓

Reason

↓

Tool

↓

Reason

↓

Tool

↓

Reason

↓

Answer
```

The agent can continue looping until it has enough information.

---

# 13. Advantages

* Dynamic tool selection based on the task.
* Iterative reasoning, allowing the model to refine its approach.
* Reduced hallucinations by grounding answers in tool outputs.
* Support for multiple sequential or parallel tool calls when the model and runtime allow it.
* Built-in streaming, checkpoints, and human-in-the-loop through LangGraph. ([Docs by LangChain][3])

---

# 14. Limitations

* More LLM calls increase latency and cost.
* Each iteration adds tokens to the conversation history.
* Poor tool descriptions can lead to incorrect tool selection.
* Complex workflows with branching or multiple specialized agents may require building a custom LangGraph rather than relying on the default ReAct loop.

---

# 15. Modern Mental Model

Think of the modern architecture as layers:

```
                User
                  │
                  ▼
         create_agent()
                  │
                  ▼
           LangGraph Runtime
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
     Model Node         Tool Node
        ▲                   │
        └────── Messages ───┘
                  │
                  ▼
           Stop Condition?
                  │
          No ─────┴───── Yes
          │             │
          ▼             ▼
     Continue Loop   Final Answer
```

## When should you use ReAct?

Use a ReAct agent when the task requires **reasoning combined with external actions**, such as searching the web, querying databases, calling APIs, using calculators, or interacting with business systems. If your workflow is a fixed pipeline (e.g., retrieve documents → summarize → translate), an LCEL chain or a custom LangGraph is often simpler. If you need multiple collaborating agents, conditional branches, approvals, or long-running workflows, build directly with LangGraph instead of relying solely on the default ReAct pattern.

[1]: https://docs.langchain.com/oss/python/releases/langgraph-v1?utm_source=chatgpt.com "What's new in LangGraph v1 - Docs by LangChain"
[2]: https://arxiv.org/abs/2210.03629?utm_source=chatgpt.com "ReAct: Synergizing Reasoning and Acting in Language Models"
[3]: https://docs.langchain.com/oss/python/langchain/agents?utm_source=chatgpt.com "Agents - Docs by LangChain"
[4]: https://reference.langchain.com/python/langgraph.prebuilt/chat_agent_executor/create_react_agent?utm_source=chatgpt.com "create_react_agent | langgraph.prebuilt | LangChain Reference"
[5]: https://docs.langchain.com/oss/python/migrate/langchain-v1?utm_source=chatgpt.com "LangChain v1 migration guide - Docs by LangChain"


With **LangChain v1+**, the recommended way to build an agent is with `create_agent()`. This is the modern replacement for the older `create_react_agent()` API. Under the hood, it creates a LangGraph-powered ReAct agent.

Let's build one step by step.

---

# Project Structure

```
project/
│
├── .env
├── app.py
└── requirements.txt
```

---

## Install Dependencies

```bash
pip install -U langchain langchain-openai python-dotenv
```

If you want search capabilities:

```bash
pip install langchain-tavily
```

---

## Step 1: Create `.env`

```text
OPENAI_API_KEY=your_openai_key

# Optional
TAVILY_API_KEY=your_tavily_key
```

---

# Step 2: Load Environment Variables

```python
from dotenv import load_dotenv

load_dotenv()
```

No need to manually access the API key because `ChatOpenAI` reads it automatically from the environment.

---

# Step 3: Create the LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)
```

---

# Step 4: Create Tools

A tool is simply a Python function decorated with `@tool`.

Example:

```python
from langchain.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""

    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""

    return a + b
```

Notice the **docstring**.

The LLM reads the docstring to decide **when** to use the tool.

---

# Step 5: Build the Agent

This is the modern API.

```python
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[add, multiply],
    system_prompt="You are a helpful math assistant."
)
```

That's it.

No `AgentExecutor`.

No prompts to pull.

No manual ReAct prompt.

No output parser.

---

# Step 6: Invoke the Agent

```python
response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is 15 times 8?"
            }
        ]
    }
)

print(response)
```

The output is a state dictionary similar to:

```python
{
    "messages": [
        HumanMessage(...),
        AIMessage(
            tool_calls=[
                {
                    "name": "multiply",
                    "args": {
                        "a": 15,
                        "b": 8
                    }
                }
            ]
        ),
        ToolMessage(...),
        AIMessage(content="15 × 8 = 120")
    ]
}
```

---

# Complete Example

```python
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()


llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b


agent = create_agent(
    model=llm,
    tools=[add, multiply],
    system_prompt="You are a helpful assistant."
)


response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is 45 + 19?"
            }
        ]
    }
)

print(response["messages"][-1].content)
```

Output:

```
64
```

---

# Example with a Search Tool

Suppose you have a search tool:

```python
from langchain_tavily import TavilySearch

search = TavilySearch(max_results=3)
```

Now create the agent:

```python
agent = create_agent(
    model=llm,
    tools=[search],
    system_prompt="You are an AI research assistant."
)
```

Ask:

```python
response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Who won the FIFA World Cup in 2022?"
            }
        ]
    }
)

print(response["messages"][-1].content)
```

The agent will:

```
User
   │
   ▼
LLM
   │
   ▼
Search Tool
   │
   ▼
Search Results
   │
   ▼
LLM
   │
   ▼
Final Answer
```

You don't need to manually orchestrate the loop—the agent handles it.

---

# Streaming Responses

Instead of `invoke()`, you can stream the execution:

```python
for chunk in agent.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is 25 * 16?"
            }
        ]
    },
    stream_mode="values"
):
    print(chunk)
```

This lets you observe intermediate messages, including tool calls and results, as they happen.

---

# How `create_agent()` Works Internally

When you write:

```python
agent = create_agent(
    model=llm,
    tools=[add, multiply]
)
```

LangChain constructs a LangGraph similar to:

```
START
   │
   ▼
Model Node
   │
   ▼
Tool Calls?
 ┌──┴──┐
 │     │
Yes    No
 │      │
 ▼      ▼
Tool   END
 │
 ▼
Model
```

The loop continues until the model produces an AI message with **no tool calls**, at which point the graph ends and returns the final state.

---

## Why this is better than the old API

Old (deprecated):

```python
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(
    llm,
    tools,
    prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools
)
```

Modern:

```python
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant."
)
```

The modern API is:

* Simpler (fewer moving parts)
* Built on LangGraph
* Supports streaming and checkpoints
* Easier to extend with middleware
* The recommended approach for new LangChain applications

As you learn further, the next logical step is to understand **how to customize this default agent** with middleware, memory, structured output, and eventually build custom LangGraph workflows when the default ReAct loop isn't enough.
