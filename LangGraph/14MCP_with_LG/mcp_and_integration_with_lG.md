# MCP and Its Integration with LangGraph

**MCP (Model Context Protocol)** is a standard that allows an AI application to connect to external **tools, data sources, APIs, files, databases, and services** in a consistent way.

Since you're learning LangGraph, the important idea is:

> **LangGraph controls the agent/workflow, while MCP provides standardized access to external tools and resources.**

A useful mental model is:

```text
                    ┌─────────────────────┐
                    │      LangGraph      │
                    │                     │
User ──────────────►│  Agent / Workflow   │
                    │        │            │
                    └────────┼────────────┘
                             │
                         MCP Client
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        MCP Server      MCP Server      MCP Server
        ──────────      ──────────      ──────────
        GitHub          Database        Files
        Tools           Tools           Tools
```

---

# 1. What problem does MCP solve?

Suppose you're building a LangGraph agent.

You want your agent to:

* search the web
* query PostgreSQL
* access GitHub
* read files
* interact with Slack
* access your company's internal APIs

Without MCP, you might write individual integrations:

```python
github_tool = ...
database_tool = ...
slack_tool = ...
search_tool = ...
```

Every application needs to understand how each integration works.

MCP introduces a **standard interface**.

```text
                 MCP
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
     GitHub      DB       Slack
     Server     Server     Server
```

Your application acts as an **MCP client**.

The external service exposes functionality through an **MCP server**.

---

# 2. MCP Architecture

There are three important components.

## MCP Host

The host is the AI application.

Examples:

* LangGraph application
* Claude Desktop
* IDE
* your own Python application

In our case:

```text
LangGraph Application
        │
        ▼
    MCP Client
```

---

## MCP Client

The client connects your application to an MCP server.

```text
LangGraph
    │
    ▼
MCP Client
    │
    ▼
MCP Server
```

The client discovers what the server provides.

For example:

```text
tools
resources
prompts
```

---

# 3. MCP Server

An MCP server exposes capabilities.

For example, imagine a GitHub MCP server.

It might expose:

```text
Tools:
    search_repositories
    get_issue
    create_issue
    create_pull_request

Resources:
    repository files
    issue information
```

Another MCP server could expose PostgreSQL:

```text
Tools:
    execute_sql
    list_tables
    describe_table
```

So your LangGraph application doesn't necessarily need to implement each API integration itself.

---

# 4. MCP Tools

This is the part you'll use most with LangGraph.

An MCP server can expose tools such as:

```text
search_web(query)
get_weather(city)
query_database(sql)
create_github_issue(...)
```

From the LangGraph agent's perspective, these become tools that the LLM can call.

Conceptually:

```text
User
 │
 ▼
LangGraph Agent
 │
 │ decides
 ▼
MCP Tool
 │
 ▼
MCP Server
 │
 ▼
External API
```

---

# 5. MCP vs LangChain Tools

This distinction is extremely important.

### LangChain tool

A tool is defined directly inside your application.

For example:

```python
from langchain_core.tools import tool

@tool
def add(a: int, b: int):
    return a + b
```

The tool lives inside your application.

```text
LangGraph Application
      │
      └── add()
```

---

### MCP tool

The tool lives on an MCP server.

```text
LangGraph Application
       │
       ▼
   MCP Client
       │
       ▼
   MCP Server
       │
       └── add()
```

The LangGraph application consumes the tool remotely through MCP.

---

# 6. Why MCP is useful with LangGraph

LangGraph is particularly good at **orchestrating agents and workflows**.

MCP is particularly good at **standardizing external integrations**.

Together:

```text
LangGraph
    │
    │ orchestration
    ▼
Agent
    │
    ├──── MCP ────► GitHub
    │
    ├──── MCP ────► PostgreSQL
    │
    ├──── MCP ────► Slack
    │
    └──── MCP ────► Internal APIs
```

This gives you a clean separation:

| Responsibility                | Technology          |
| ----------------------------- | ------------------- |
| Agent workflow                | LangGraph           |
| State                         | LangGraph           |
| Checkpointing                 | LangGraph           |
| Routing                       | LangGraph           |
| Agent reasoning               | LangChain/LangGraph |
| External tool standardization | MCP                 |
| External service              | MCP Server          |
| Tool discovery                | MCP                 |

---

# 7. Basic LangGraph without MCP

First understand the normal architecture.

You might have:

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str):
    return f"Weather for {city}"

tools = [get_weather]
```

Then:

```text
LangGraph
    │
    ▼
LLM
    │
    ▼
Tool call
    │
    ▼
get_weather()
```

The tool is implemented directly in Python.

---

# 8. LangGraph with MCP

With MCP:

```text
                 LangGraph
                     │
                     ▼
                   Agent
                     │
                     ▼
                MCP Client
                     │
              ┌──────┴──────┐
              ▼             ▼
        Weather MCP     GitHub MCP
           Server          Server
              │             │
              ▼             ▼
         Weather API      GitHub API
```

The tools are discovered from MCP servers.

---

# 9. MCP Tool Discovery

One of the powerful features of MCP is that your application can ask the server:

> "What tools do you provide?"

Conceptually:

```python
tools = await mcp_client.list_tools()
```

The response might be something like:

```text
[
    search_repository,
    get_file,
    create_issue,
    get_issue
]
```

You can then make those tools available to your LangGraph agent.

---

# 10. The Important Integration Pattern

The integration generally looks like:

```text
MCP Server
     │
     │ exposes tools
     ▼
MCP Client
     │
     │ converts/exposes tools
     ▼
LangGraph
     │
     ▼
LLM
```

The critical part is:

> **MCP tools need to become tools that the LangGraph agent can use.**

---

# 11. Example Architecture

Imagine you're creating a coding assistant.

You have:

```text
                Coding Agent
                     │
                  LangGraph
                     │
              ┌──────┼──────┐
              │      │      │
              ▼      ▼      ▼
             GitHub  DB    Files
              │      │      │
              ▼      ▼      ▼
            MCP     MCP    MCP
           Server  Server  Server
```

The agent might receive:

```text
"Find the open authentication issues
in my GitHub repository."
```

The LLM decides:

```text
I need GitHub information.
```

It selects:

```text
search_issues
```

LangGraph executes the tool through MCP:

```text
LangGraph
   │
   ▼
MCP Client
   │
   ▼
GitHub MCP Server
   │
   ▼
GitHub API
```

Result:

```text
Issue #31: Authentication timeout
Issue #42: OAuth callback failure
```

The result goes back into the LangGraph state.

---
