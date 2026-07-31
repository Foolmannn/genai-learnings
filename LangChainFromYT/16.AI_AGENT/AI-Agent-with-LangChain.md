
# you asked

message time: 2026-07-31 21:50:49

# Step 3: Create the ReAct agent manually with the pulled prompt
agent = create_react_agent(
    llm=llm,
    tools=[search_tool, get_weather_data],
    prompt=prompt
)  # Step 4: Wrap it with AgentExecutor
agent_executor = AgentExecutor(
    agent=agent,
    tools=[search_tool, get_weather_data],
    verbose=True
)  This code is deprecated what i s the modern way to code the agent in langchain

---

# chatgpt response

Yes. The code you're using is based on the **legacy LangChain Agent API** (`create_react_agent` + `AgentExecutor`), which is now considered **deprecated for new projects**. The LangChain team now recommends using **LangGraph** to build agents because it provides better control, persistence, streaming, checkpoints, human-in-the-loop, and multi-agent workflows.

Let's compare the old and modern approaches.

---

# Old (Deprecated) Way

```python
from langchain.agents import create_react_agent, AgentExecutor

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools
)

agent_executor.invoke({
    "input": "What's the weather in Kathmandu?"
})
```

Architecture

```
User
   │
   ▼
AgentExecutor
   │
   ▼
ReAct Agent
   │
   ▼
LLM
   │
   ▼
Tools
```

Problems:

- Difficult to customize
- Hidden execution loop
- Hard to debug
- Not suitable for production
- Limited persistence and memory

---

# Modern Way (Recommended)

LangChain agents are now built on **LangGraph**.

Instead of creating an `AgentExecutor`, you create a graph.

Install:

```bash
pip install langgraph
```

---

## Step 1: Create the LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0
)
```

---

## Step 2: Create Tools

```python
from langchain.tools import tool

@tool
def add(a: int, b: int):
    """Add two numbers."""
    return a + b


@tool
def weather(city: str):
    """Returns weather."""
    return "28°C"
```

---

## Step 3: Create the Agent

The modern API is much simpler.

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model=llm,
    tools=[add, weather]
)
```

Notice:

Old

```python
llm=
```

Modern

```python
model=
```

No prompt is required unless you want to customize the agent.

---

## Step 4: Invoke the Agent

```python
from langchain_core.messages import HumanMessage

response = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="What is 20 + 40?"
            )
        ]
    }
)

print(response)
```

No `AgentExecutor` is needed.

---

# Agent Architecture

```
User
 │
 ▼
LangGraph Agent
 │
 ▼
LLM
 │
 ▼
Tool Calls
 │
 ▼
Execute Tool
 │
 ▼
Return Result
 │
 ▼
LLM
 │
 ▼
Answer
```

The graph itself manages the execution loop.

---

# Custom System Prompt

Instead of pulling the prompt from the LangChain Hub:

```python
prompt = hub.pull("hwchase17/react")
```

use the `prompt` argument directly:

```python
agent = create_react_agent(
    model=llm,
    tools=[weather],
    prompt="You are a helpful weather assistant."
)
```

Or use a system message:

```python
from langchain_core.messages import SystemMessage

agent.invoke(
    {
        "messages": [
            SystemMessage(
                content="You are a helpful assistant."
            ),
            HumanMessage(
                content="What's the weather?"
            )
        ]
    }
)
```

---

# Streaming

One of the biggest improvements is streaming.

```python
for chunk in agent.stream(
    {
        "messages": [
            HumanMessage(
                content="What's the weather in Kathmandu?"
            )
        ]
    }
):
    print(chunk)
```

You'll see intermediate reasoning, tool calls, and final responses as they happen.

---

# Memory

Instead of `ConversationBufferMemory`, LangGraph uses **checkpointers**.

Example:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

agent = create_react_agent(
    model=llm,
    tools=[weather],
    checkpointer=memory
)
```

Invoke with a thread ID:

```python
config = {
    "configurable": {
        "thread_id": "user-1"
    }
}

agent.invoke(
    {
        "messages": [
            HumanMessage(content="Hi!")
        ]
    },
    config=config
)
```

Now the conversation persists across calls for the same thread.

---

# State

Everything is stored as state:

```python
{
    "messages": [
        HumanMessage(...),
        AIMessage(...),
        ToolMessage(...)
    ]
}
```

This state flows through the graph.

---

# Old vs Modern

| Old LangChain | Modern LangGraph |
|---------------|------------------|
| `AgentExecutor` | No executor needed |
| `create_react_agent()` from `langchain.agents` | `create_react_agent()` from `langgraph.prebuilt` |
| `llm=` | `model=` |
| Hidden execution loop | Graph-based execution |
| Legacy memory classes | Checkpointers (`MemorySaver`, database-backed savers) |
| Limited customization | Highly customizable graphs |
| Deprecated for new projects | Recommended approach |

---

# Complete Modern Example

```python
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0
)

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

agent = create_react_agent(
    model=llm,
    tools=[multiply]
)

response = agent.invoke(
    {
        "messages": [
            HumanMessage(
                content="What is 12 × 18?"
            )
        ]
    }
)

print(response["messages"][-1].content)
```

---

## Should you still learn `AgentExecutor`?

Yes, but mainly to understand older tutorials and maintain legacy code. Many blogs and YouTube videos still use it. For **new projects**, focus on:

1. Tool creation (`@tool`)
2. Tool calling (`bind_tools`, `ToolMessage`)
3. `create_react_agent` from `langgraph.prebuilt`
4. LangGraph nodes, edges, and state
5. Checkpointers and persistent memory
6. Multi-agent workflows

Since you've already been exploring **tool calling**, `bind_tools`, multiple tool calls, and `.invoke()`, the next step is to learn **LangGraph**. It is now the primary framework for building production-ready AI agents in the LangChain ecosystem.

---
Powered by [AI Exporter](https://saveai.net)