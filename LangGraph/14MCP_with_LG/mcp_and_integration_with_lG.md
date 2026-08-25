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

# 12. LangGraph State + MCP

This is where MCP becomes particularly interesting.

Suppose your state is:

```python
from typing import TypedDict

class State(TypedDict):
    messages: list
```

The graph might look like:

```text
START
  │
  ▼
Agent
  │
  ├──── no tool ────► END
  │
  ▼
MCP Tool
  │
  ▼
Agent
  │
  ▼
END
```

This is essentially the same tool-calling loop you learned with LangGraph.

The difference is that the tools are coming from MCP.

---

# 13. MCP Tool Calling Loop

A typical agent loop is:

```text
                 ┌──────────────┐
                 │     User     │
                 └──────┬───────┘
                        ▼
                 ┌──────────────┐
                 │     LLM      │
                 └──────┬───────┘
                        │
                 Tool required?
                   /          \
                 No            Yes
                 │              │
                 ▼              ▼
                END        MCP Tool
                                │
                                ▼
                           MCP Server
                                │
                                ▼
                             Result
                                │
                                ▼
                               LLM
```

This is very similar to the tool-calling architectures you've already studied in LangGraph.

---

# 14. MCP Transport

MCP servers can communicate with clients using different transports.

One common local setup is **stdio**.

```text
LangGraph Process
      │
      │ stdin/stdout
      ▼
MCP Server Process
```

This is useful when the MCP server runs locally.

For remote servers, network-based transports can be used.

Conceptually:

```text
Local:

LangGraph ──stdio──► MCP Server


Remote:

LangGraph ──network──► MCP Server
```

---

# 15. Example MCP Server Concept

Imagine you create a simple MCP server providing a calculator.

Conceptually:

```python
@mcp.tool()
def multiply(a: int, b: int) -> int:
    return a * b
```

The MCP server exposes:

```text
multiply
```

Your LangGraph application connects to the server and discovers:

```text
multiply(a, b)
```

Then the LLM can decide:

```text
User:
"Calculate 25 * 40"

LLM:
I should use multiply.

MCP:
multiply(25, 40)

Result:
1000
```

---

# 16. MCP Resources

MCP isn't only about tools.

It can also expose **resources**.

Think of resources as data that the AI application can access.

For example:

```text
MCP Server
   │
   ├── Tools
   │     ├── search()
   │     └── update()
   │
   └── Resources
         ├── documentation
         ├── files
         └── database information
```

Tools generally represent **actions**.

Resources generally represent **information/data**.

For example:

```text
Tool:
create_issue()

Resource:
github://repo/issues/123
```

---

# 17. MCP Prompts

MCP can also expose reusable prompts.

For example:

```text
review_code
summarize_repository
analyze_issue
```

The application can discover these prompts from the server.

So MCP provides a broader protocol for exposing:

```text
Tools
Resources
Prompts
```

---

# 18. MCP vs API

You might wonder:

> Why don't I just call the API directly?

You absolutely can.

Without MCP:

```text
LangGraph
    │
    ▼
GitHub Python SDK
    │
    ▼
GitHub API
```

With MCP:

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

The advantage is **standardization and interoperability**.

Your agent doesn't need to understand every service's custom integration.

---

# 19. MCP's Biggest Advantage

Imagine you build:

```text
Agent A
Agent B
Agent C
Agent D
```

And they all need GitHub.

Without MCP:

```text
Agent A ── GitHub SDK
Agent B ── GitHub SDK
Agent C ── GitHub SDK
Agent D ── GitHub SDK
```

With MCP:

```text
              ┌── Agent A
              │
              ├── Agent B
              │
              ├── Agent C
              │
              ▼
          MCP Server
              │
              ▼
          GitHub API
```

The integration becomes reusable.

---

# 20. Multiple MCP Servers in LangGraph

This is where things become powerful.

You could have:

```text
                    LangGraph Agent
                          │
                    MCP Client(s)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   GitHub MCP       PostgreSQL MCP      Filesystem MCP
        │                 │                 │
        ▼                 ▼                 ▼
     GitHub              DB               Files
```

The agent might have tools:

```text
search_github
create_issue

query_database
get_customer

read_file
search_files
```

The LLM chooses which tool to use.

---

# 21. MCP + LangGraph Conditional Routing

Since you're learning LangGraph conditional workflows, you can combine them.

For example:

```text
                    START
                      │
                      ▼
                    Agent
                      │
               ┌──────┴──────┐
               │             │
           GitHub task    Database task
               │             │
               ▼             ▼
        GitHub MCP       DB MCP
               │             │
               └──────┬──────┘
                      ▼
                    Agent
                      │
                      ▼
                     END
```

The LLM can determine which MCP tool is appropriate.

---

# 22. MCP + LangGraph Persistence

This is another important combination.

LangGraph can maintain state using persistence/checkpointing.

For example:

```text
User
 │
 ▼
LangGraph
 │
 ├── State
 │
 ├── Checkpoint
 │
 └── MCP tools
       │
       ├── GitHub
       └── Database
```

Suppose the conversation is:

```text
User:
Find my open GitHub issues.

Agent:
[uses GitHub MCP]

User:
Which one has the highest priority?

Agent:
[uses previous state + GitHub MCP]
```

LangGraph manages the conversation state.

MCP manages access to external systems.

---

# 23. MCP + LangSmith

You have also been studying LangSmith, so this combination is worth understanding.

```text
                  LangGraph
                     │
                     ▼
                   Agent
                     │
                     ▼
                  MCP Tool
                     │
                     ▼
                MCP Server
```

LangSmith can help you observe the execution:

```text
Agent invocation
      │
      ├── LLM call
      │
      ├── MCP tool call
      │
      ├── MCP result
      │
      └── final response
```

This becomes useful for debugging:

```text
Why did the agent choose this MCP tool?

What arguments did it send?

How long did the MCP call take?

What result came back?

Why did the agent make another tool call?
```

---

# 24. MCP Security

This is an important part that shouldn't be ignored.

Suppose your MCP server exposes:

```text
delete_database()
execute_sql()
send_email()
create_github_issue()
```

Giving an agent unrestricted access is dangerous.

You should consider:

### Authentication

Who can access the MCP server?

### Authorization

What operations are allowed?

### Input validation

Can the agent send arbitrary SQL?

### Tool permissions

Does the agent really need:

```text
delete_database()
```

or only:

```text
read_database()
```

### Human approval

For dangerous operations:

```text
Agent
  │
  ▼
MCP Tool
  │
  ▼
Approval Required
  │
  ▼
Human
  │
  ▼
Execute
```

This fits naturally with LangGraph's human-in-the-loop capabilities.

---

# 25. MCP + Human-in-the-Loop

Imagine:

```text
User:
Create a GitHub issue saying production is broken.
```

The agent decides:

```text
create_issue(...)
```

But before executing:

```text
             Agent
               │
               ▼
        GitHub MCP Tool
               │
               ▼
        Human approval
          /          \
       Approve       Reject
          │             │
          ▼             ▼
       Execute         END
```

LangGraph can manage this workflow while MCP provides the actual external capability.

---

# 26. MCP and Tool Discovery

One major advantage is dynamic discovery.

Instead of hardcoding every tool:

```python
tools = [
    search_github,
    create_issue,
    query_database,
]
```

your application can discover tools from MCP servers.

Conceptually:

```text
Connect to MCP server
        │
        ▼
List available tools
        │
        ▼
Convert/adapt tools
        │
        ▼
Give them to LangGraph agent
```

This makes integrations much more modular.

---

# 27. The Integration Flow You Should Remember

For your LangGraph learning, memorize this:

```text
                   USER
                     │
                     ▼
               ┌──────────┐
               │ LangGraph│
               │  Agent   │
               └────┬─────┘
                    │
                    ▼
                   LLM
                    │
             decides to use tool
                    │
                    ▼
               MCP Client
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       GitHub       DB       Files
       MCP Server  MCP       MCP
                    │
                    ▼
                External
                Services
```

---

# 28. MCP vs LangGraph vs LangChain vs LangSmith

These technologies solve different problems.

| Technology    | Main responsibility                                               |
| ------------- | ----------------------------------------------------------------- |
| **LangChain** | Components, models, tools, retrievers, agents                     |
| **LangGraph** | Stateful agent/workflow orchestration                             |
| **MCP**       | Standard protocol for connecting AI apps to external capabilities |
| **LangSmith** | Tracing, evaluation, monitoring, debugging                        |

A modern architecture could therefore be:

```text
                         LangSmith
                       Observability
                            │
                            ▼
User ───────────────► LangGraph
                         │
                         ▼
                       Agent
                         │
                  ┌──────┴──────┐
                  ▼             ▼
             LangChain       MCP Client
             Components          │
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
                 GitHub         DB          Slack
                 MCP Server     MCP         MCP
```

---

# 29. When Should You Use MCP?

MCP is especially useful when:

### You have multiple AI applications

```text
Agent A ─┐
Agent B ─┼──► MCP Server ──► Service
Agent C ─┘
```

### You want reusable integrations

Build the integration once as an MCP server.

### You want standardized tool discovery

The client can discover available capabilities.

### You are connecting many external systems

For example:

```text
GitHub
PostgreSQL
Slack
Google Drive
Notion
Internal APIs
```

### You want your tools separated from your agent

This creates a cleaner architecture.

---

# 30. When MCP May Be Overkill

For a small application:

```python
@tool
def add(a, b):
    return a + b
```

There may be little reason to create an MCP server.

You could simply use:

```text
LangGraph
   │
   └── Python Tool
```

MCP becomes more attractive when you have:

```text
many applications
       +
many external integrations
       +
reusable tools
       +
standardized access
```

---

# 31. The Key Difference in One Example

### Without MCP

```text
LangGraph
    │
    ├── GitHub Python SDK
    ├── Slack SDK
    ├── PostgreSQL driver
    └── Google API client
```

Your application directly manages everything.

### With MCP

```text
LangGraph
    │
    └── MCP Client
           │
           ├── GitHub MCP
           ├── Slack MCP
           ├── PostgreSQL MCP
           └── Google MCP
```

The integration layer becomes standardized.

---

# 32. How You Should Learn MCP for LangGraph

Given the LangGraph topics you've been studying, I'd learn it in this order:

```text
1. MCP fundamentals
       ↓
2. MCP architecture
       ↓
3. MCP server
       ↓
4. MCP client
       ↓
5. MCP tools
       ↓
6. MCP resources
       ↓
7. MCP transports
       ↓
8. Connect MCP to LangChain
       ↓
9. Connect MCP tools to LangGraph
       ↓
10. MCP + LangGraph agent
       ↓
11. MCP + persistence
       ↓
12. MCP + human-in-the-loop
       ↓
13. MCP + LangSmith
       ↓
14. Build a real project
```

## The most important concept

Don't think of MCP as another agent framework.

Think of it like this:

> **LangGraph = the brain's workflow/orchestration system.**
> **MCP = a standardized communication layer for giving that brain access to external capabilities.**

So when you eventually build a serious LangGraph application, the architecture can look like:

```text
                         ┌───────────────┐
                         │   LangSmith   │
                         │ Observability │
                         └───────┬───────┘
                                 │
                                 ▼
┌─────────┐               ┌──────────────┐
│  User   │──────────────►│  LangGraph   │
└─────────┘               │    Agent     │
                          └──────┬───────┘
                                 │
                       ┌─────────┴─────────┐
                       │                   │
                       ▼                   ▼
                    LangChain          MCP Client
                    Components              │
                                           │
                         ┌─────────────────┼─────────────────┐
                         ▼                 ▼                 ▼
                    GitHub MCP        Database MCP       Slack MCP
                         │                 │                 │
                         ▼                 ▼                 ▼
                      GitHub             DB                 Slack
```

That separation—**orchestration in LangGraph, capabilities through MCP, and observability through LangSmith**—is the core architecture you should understand before moving into the actual MCP + LangGraph implementation.
