# Short-Term Memory in LangGraph — Detailed Notes

Below is a structured set of notes based on the topics in the video, but expanded so you can understand **why memory is needed, how LangGraph implements it, how persistence works, and how to handle context-window overflow using trimming and summarization**.

---

# 1. Why Do LLMs Need Memory?

The first important concept is:

> **LLMs are fundamentally stateless.**

Suppose you have a chatbot:

```text
User: My name is Suman.
AI: Nice to meet you, Suman!

User: What is my name?
AI: I don't know.
```

Why?

Because an LLM doesn't automatically remember previous API calls.

Each invocation is conceptually independent:

```text
Request 1
    ↓
LLM
    ↓
Response 1

Request 2
    ↓
LLM
    ↓
Response 2
```

The LLM doesn't inherently know about `Request 1` when processing `Request 2`.

---

# 2. LLMs Are Stateless

Consider:

```python
response = llm.invoke("My name is Suman")
```

Later:

```python
response = llm.invoke("What is my name?")
```

The second invocation doesn't automatically contain:

```text
"My name is Suman"
```

Therefore, the model can't reliably answer.

The application needs to maintain the conversation state.

---

# 3. How Chatbots Give LLMs Memory

A common approach is to send previous messages along with the new message.

Instead of:

```text
User → "What is my name?"
```

we send:

```text
System: You are a helpful assistant.

User: My name is Suman.
AI: Nice to meet you, Suman!

User: What is my name?
```

Now the LLM can answer:

```text
Your name is Suman.
```

So the important idea is:

> **Memory in an LLM application is usually implemented by storing state and supplying relevant state back to the model.**

---

# 4. What Is Short-Term Memory?

In LangGraph, **short-term memory** refers to memory associated with a particular conversation/thread.

For example:

```text
Thread A
    ↓
User: My name is Suman.
    ↓
AI: Nice to meet you.

User: What is my name?
    ↓
AI: Your name is Suman.
```

But:

```text
Thread B
    ↓
User: What is my name?
    ↓
AI: I don't know.
```

The important concept is the **thread**.

---

# 5. Thread

A thread represents a particular conversation/session.

For example:

```text
thread_id = "user_123"
```

Conversation:

```text
Thread user_123

Message 1
Message 2
Message 3
Message 4
...
```

Another user:

```text
thread_id = "user_456"
```

has a different conversation.

Therefore:

```text
Thread A
 ├── message
 ├── message
 └── message

Thread B
 ├── message
 ├── message
 └── message
```

The memories are isolated.

---

# 6. Short-Term Memory in LangGraph

LangGraph represents application state using a **state object**.

For example:

```python
from typing import TypedDict
from langchain_core.messages import AnyMessage

class State(TypedDict):
    messages: list[AnyMessage]
```

The state might look like:

```python
{
    "messages": [
        HumanMessage("My name is Suman"),
        AIMessage("Nice to meet you"),
        HumanMessage("What is my name?")
    ]
}
```

This state can be persisted between graph executions.

---

# 7. Checkpointers

The key LangGraph concept here is the:

> **Checkpointer**

A checkpointer saves the graph's state at different execution points.

Conceptually:

```text
                 LangGraph
                     │
                     ↓
                  State
                     │
                     ↓
               Checkpointer
                     │
             ┌───────┴───────┐
             ↓               ↓
          Thread A        Thread B
             │               │
          State A          State B
```

The checkpointer allows LangGraph to retrieve previous state for a particular thread.

---

# 8. Why Is It Called a Checkpointer?

Think about a video game.

You play:

```text
Level 1
   ↓
Level 2
   ↓
Level 3
```

Then the game saves your progress.

If the game crashes, you don't start from level 1.

You load the checkpoint.

LangGraph works similarly.

```text
Graph execution
      ↓
State
      ↓
Checkpoint
```

Later:

```text
New invocation
      ↓
thread_id
      ↓
Retrieve checkpoint
      ↓
Continue with previous state
```

---

# 9. In-Memory Checkpointer

During development, you can use an in-memory checkpointer.

A commonly used implementation is:

```python
from langgraph.checkpoint.memory import InMemorySaver
```

Then:

```python
checkpointer = InMemorySaver()
```

Compile the graph:

```python
graph = builder.compile(
    checkpointer=checkpointer
)
```

Now LangGraph can maintain state between calls.

---

# 10. Example: Chatbot with Short-Term Memory

Let's build a simple example.

### Step 1 — Define State

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage
```

State:

```python
class State(TypedDict):
    messages: list
```

---

### Step 2 — Create Node

```python
def chatbot(state: State):

    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }
```

---

### Step 3 — Build Graph

```python
builder = StateGraph(State)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
```

---

### Step 4 — Add Checkpointer

```python
checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)
```

Now the graph has memory.

---

# 11. Thread ID Is Extremely Important

When invoking the graph:

```python
config = {
    "configurable": {
        "thread_id": "user_123"
    }
}
```

Then:

```python
graph.invoke(
    {
        "messages": [
            HumanMessage(content="My name is Suman")
        ]
    },
    config=config
)
```

Later:

```python
graph.invoke(
    {
        "messages": [
            HumanMessage(content="What is my name?")
        ]
    },
    config=config
)
```

Because both calls use:

```text
thread_id = user_123
```

LangGraph knows that they belong to the same conversation.

---

# 12. What Happens Internally?

First request:

```text
thread_id = user_123

State:
messages:
    Human: My name is Suman
```

Graph executes.

Checkpoint:

```text
user_123
   ↓
checkpoint
   ↓
messages
```

Second request:

```text
thread_id = user_123
```

LangGraph retrieves:

```text
Previous state
     ↓
Human: My name is Suman
```

Then adds:

```text
Human: What is my name?
```

The model receives the relevant conversation.

---

# 13. Different Threads = Different Memories

Suppose:

### Thread A

```python
config_a = {
    "configurable": {
        "thread_id": "A"
    }
}
```

User:

```text
My favorite language is Python.
```

### Thread B

```python
config_b = {
    "configurable": {
        "thread_id": "B"
    }
}
```

User:

```text
My favorite language is C++.
```

Now:

```text
Thread A
→ Python

Thread B
→ C++
```

They don't interfere with each other.

This is extremely important for production chat applications.

---

# 14. In-Memory Storage

`InMemorySaver` stores checkpoints in the application's memory.

Conceptually:

```text
Python Process
│
├── Thread A → State
├── Thread B → State
└── Thread C → State
```

This is useful for:

* Learning
* Testing
* Prototyping
* Local development

But it has an important limitation.

---

# 15. Problem With In-Memory Memory

Suppose your application is running:

```text
Python application
     ↓
InMemorySaver
     ↓
Conversation history
```

Now the application crashes.

Or you restart it:

```text
Application stopped
      ↓
RAM cleared
      ↓
Application restarted
```

The memory is gone.

Therefore:

```text
InMemorySaver
      ↓
RAM
      ↓
Process ends
      ↓
Memory disappears
```

---

# 16. Why Production Needs Persistent Memory

A production chatbot shouldn't lose conversations every time the server restarts.

You need:

```text
Application
     ↓
Persistent database
     ↓
Checkpoints
```

Possible storage systems include:

```text
PostgreSQL
Redis
SQLite
Cloud databases
```

For production LangGraph applications, PostgreSQL is a common choice.

---

# 17. PostgreSQL Checkpointer

Instead of:

```text
InMemorySaver
```

you can use a PostgreSQL-backed checkpointer.

Conceptually:

```text
LangGraph
    ↓
PostgreSQL Checkpointer
    ↓
PostgreSQL Database
```

Now state survives application restarts.

---

# 18. PostgreSQL + Docker

A convenient way to run PostgreSQL locally is Docker.

Conceptually:

```text
Docker
│
└── PostgreSQL Container
        │
        └── Database
```

Your LangGraph application connects to PostgreSQL.

```text
Python
  │
  ↓
LangGraph
  │
  ↓
PostgreSQL Checkpointer
  │
  ↓
PostgreSQL
```

---

# 19. Why Docker Is Useful Here

Without Docker:

```text
Install PostgreSQL
Configure PostgreSQL
Create user
Create database
Configure service
```

With Docker:

```text
docker run postgres
```

You get an isolated PostgreSQL environment.

This is especially useful during development.

---

# 20. Persistent Memory

With PostgreSQL:

```text
Application starts
      ↓
Load checkpoint from DB
      ↓
Continue conversation
```

If application restarts:

```text
Application crashes
      ↓
Restart
      ↓
Connect to PostgreSQL
      ↓
Retrieve thread state
      ↓
Continue conversation
```

So:

```text
InMemorySaver
→ temporary memory

PostgreSQL checkpointer
→ persistent memory
```

---

# 21. Short-Term Memory ≠ Infinite Memory

This is one of the most important concepts.

Even if you persist every message, you cannot necessarily send every message to the LLM forever.

Why?

Because LLMs have a:

> **Context window**

---

# 22. Context Window

An LLM processes input using tokens.

For example:

```text
System prompt
+
Conversation history
+
Current question
+
Tools
+
Retrieved documents
+
Instructions
```

All of this consumes context.

Conceptually:

```text
┌─────────────────────────────┐
│       Context Window        │
│                             │
│ System prompt               │
│ Conversation                │
│ Tool results                │
│ Current question            │
│                             │
└─────────────────────────────┘
```

The context window has a maximum capacity.

---

# 23. Context Overflow

Suppose an LLM has a context capacity of:

```text
100,000 tokens
```

Your conversation eventually becomes:

```text
120,000 tokens
```

You can't simply send everything.

```text
120K tokens
      ↓
100K limit
      ↓
Overflow
```

This creates the:

> **Context overflow problem**

---

# 24. Memory vs Context

These two concepts are easy to confuse.

### Memory

Information stored by your application.

```text
Database
   ↓
100,000 messages
```

### Context

Information currently sent to the LLM.

```text
Selected messages
      ↓
LLM
```

Therefore:

> You can have a huge amount of stored memory while only putting a small portion of it into the model's context window.

This distinction is fundamental.

---

# 25. Three Ways to Manage Long Conversations

The video focuses on two important techniques:

```text
1. Trimming
2. Summarization
```

And deletion is involved in the summarization workflow.

---

# 26. Strategy 1 — Trimming

Trimming means:

> Keep only the most relevant/recent messages and remove older messages from the context.

Suppose conversation is:

```text
M1
M2
M3
M4
M5
M6
M7
M8
M9
M10
```

Instead of sending everything:

```text
M1 → M10
```

you might send:

```text
M6
M7
M8
M9
M10
```

So:

```text
Old messages
     ↓
Discard from active context
     ↓
Recent messages
     ↓
LLM
```

---

# 27. Why Trimming Works

Recent conversations are often more relevant.

For example:

```text
User: Explain Python.
...
20 messages later...
User: Explain decorators.
```

The recent discussion about Python decorators may be more useful than an unrelated conversation from 100 messages ago.

So we can maintain a sliding window.

---

# 28. Sliding Window Concept

For example:

```text
Conversation:

[1][2][3][4][5][6][7][8][9][10]
                  ↑
              Keep recent
```

As new messages arrive:

```text
[2][3][4][5][6][7][8][9][10][11]
                     ↑
                  Window moves
```

This is essentially a sliding context window.

---

# 29. Trimming in LangGraph

LangGraph provides message-management functionality that can be used to control the number of messages passed to the model.

A common pattern is conceptually:

```python
messages = trim_messages(
    messages,
    max_tokens=4000,
    strategy="last"
)
```

The idea is:

```text
Full message history
        ↓
trim_messages()
        ↓
Token-limited history
        ↓
LLM
```

The exact trimming configuration should depend on your model and application.

---

# 30. Important Problem With Trimming

Suppose:

```text
User: My name is Suman.
```

This message gets trimmed.

Later:

```text
User: What is my name?
```

The model might no longer see:

```text
My name is Suman.
```

Therefore:

```text
Trimming
    ↓
Less context
    ↓
Lower token usage
    ↓
But potentially lost information
```

That's the main limitation.

---

# 31. Trimming Is Not Forgetting

This distinction is important.

Suppose your database still contains:

```text
My name is Suman.
```

but your active context contains:

```text
Recent messages only
```

The information hasn't necessarily been deleted from persistent storage.

It has simply been excluded from the current model context.

So:

```text
Stored memory ≠ Active context
```

---

# 32. Strategy 2 — Summarization

Summarization solves an important problem with trimming.

Instead of completely throwing away old messages:

```text
Old messages
     ↓
DELETE
```

we first compress them:

```text
Old conversation
      ↓
Summary
      ↓
Keep summary
```

For example:

### Original

```text
User: My name is Suman.
AI: Nice to meet you.

User: I'm learning Python.
AI: Great choice.

User: I'm also learning machine learning.
AI: That's useful.

User: I'm building an AI chatbot.
AI: That's a good project.
```

Could become:

```text
Summary:
The user is Suman and is learning Python and
machine learning. They are building an AI chatbot.
```

Instead of keeping 8 messages, we might keep one compact summary.

---

# 33. Summarization = Compression

Think of it as:

```text
10,000 tokens
      ↓
LLM summarization
      ↓
1,000 tokens
```

You preserve the important information while reducing context size.

Therefore:

> **Summarization is a form of semantic compression of conversation history.**

---

# 34. Why Summarization Is Better Than Simple Trimming

Consider:

```text
Message 1:
My name is Suman.

Message 2:
I'm from Nepal.

Message 3:
I'm learning Python.

...

Message 100:
Explain LangGraph memory.
```

Trimming may remove:

```text
My name is Suman.
I'm from Nepal.
```

Summarization can preserve them:

```text
Summary:
The user is Suman, from Nepal, and is learning Python.
```

Then the recent messages can remain too.

---

# 35. Typical Summarization Architecture

A useful architecture is:

```text
             Conversation
                  │
                  ↓
          Is it too long?
             /        \
           No          Yes
           │            │
           ↓            ↓
        Continue     Summarize
                        │
                        ↓
                 Delete old messages
                        │
                        ↓
                  Keep summary
                        │
                        ↓
                  Continue chat
```

---

# 36. Why Deletion Is Used

Suppose you create a summary but leave all old messages:

```text
Summary
+
M1
+
M2
+
M3
+
...
+
M100
```

You haven't solved the context problem.

You have actually increased context:

```text
Summary + old conversation
```

Therefore the summarization workflow often becomes:

```text
Old messages
      ↓
Summarize
      ↓
Store summary
      ↓
Delete old messages
      ↓
Keep recent messages
```

---

# 37. The Result

After summarization, state might look like:

```text
Summary:
User is learning Python, ML and LangGraph.
User is building an AI chatbot.

Recent messages:
M95
M96
M97
M98
M99
M100
```

Instead of:

```text
M1
M2
M3
...
M100
```

This dramatically reduces context size.

---

# 38. Summary + Recent Messages

This is one of the most useful patterns for production chatbots.

```text
┌──────────────────────────┐
│ Conversation Summary     │
│                          │
│ Important old context    │
└──────────────────────────┘

┌──────────────────────────┐
│ Recent Messages          │
│                          │
│ Latest conversation      │
└──────────────────────────┘
```

The LLM receives:

```text
Summary
+
Recent conversation
+
Current question
```

This provides both:

* Long-term conversational context
* Recent conversational details

while controlling token usage.

---

# 39. Summarization Workflow in LangGraph

A simplified architecture could look like:

```text
                 START
                   │
                   ↓
              Chat Node
                   │
                   ↓
          Check message count
              /          \
            No            Yes
            │              │
            ↓              ↓
         Continue       Summarize
                           │
                           ↓
                    Update summary
                           │
                           ↓
                    Delete old msgs
                           │
                           ↓
                       Continue
```

---

# 40. State for Summarization

You can maintain a state such as:

```python
from typing import TypedDict

class State(TypedDict):
    messages: list
    summary: str
```

Now the state contains:

```python
{
    "summary": "...",
    "messages": [...]
}
```

---

# 41. Chat Node

Conceptually:

```python
def chatbot(state):

    messages = state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }
```

But in a real summarization system, the model input would usually be constructed from:

```text
summary
+
recent messages
```

rather than blindly passing the entire historical message list.

---

# 42. Summarization Node

Conceptually:

```python
def summarize_conversation(state):

    summary = state.get("summary", "")

    messages = state["messages"]

    prompt = f"""
    Existing summary:
    {summary}

    Conversation:
    {messages}

    Create an updated concise summary.
    """

    response = llm.invoke(prompt)

    return {
        "summary": response.content
    }
```

This produces a compressed representation.

---

# 43. Updating an Existing Summary

This is better than starting from scratch every time.

Suppose:

```text
Existing summary:
User is learning Python.
```

New messages:

```text
User is learning LangGraph.
User is building a chatbot.
```

Updated summary:

```text
User is learning Python and LangGraph
and is building a chatbot.
```

Conceptually:

```text
Old Summary
     +
New Messages
     ↓
LLM
     ↓
New Summary
```

This allows the summary to evolve.

---

# 44. Deleting Old Messages

After generating the summary, old messages can be removed from the active message state.

Conceptually:

```text
Before:

Summary: ""
M1
M2
M3
M4
M5
M6
M7
M8
```

After:

```text
Summary:
User is learning Python...

M6
M7
M8
```

The older information has been compressed into the summary.

---

# 45. Conditional Routing

LangGraph is particularly useful here because we can use conditional edges.

For example:

```text
                chatbot
                   │
                   ↓
             should_summarize?
              /            \
            No              Yes
            │                │
            ↓                ↓
           END          summarize
                              │
                              ↓
                          continue
```

The decision can be based on:

```python
len(messages)
```

or preferably some token-aware measurement.

---

# 46. Message Count vs Token Count

A subtle but important point:

Don't assume:

```python
len(messages) > 20
```

always means the context is too large.

Why?

Because messages have different lengths.

For example:

```text
Message A:
"Hi"

Message B:
[10,000-word document]
```

Both count as one message.

But their token usage is radically different.

Therefore, production systems should consider:

> **Token count rather than only message count.**

---

# 47. Token Budget

A useful mental model is:

```text
Model Context Window
        │
        ├── System instructions
        ├── Summary
        ├── Recent messages
        ├── Tool results
        └── Current user message
```

You need to reserve enough space for the model's output as well.

For example:

```text
Context limit = 32K

Input budget:
    System       = 2K
    Summary      = 3K
    Messages     = 20K
    User query   = 1K

Output reserve:
                 = 6K
```

Total:

```text
32K
```

This is why simply filling the entire context window with history isn't ideal.

---

# 48. Short-Term Memory Lifecycle

A good mental model:

```text
User message
      ↓
Graph receives message
      ↓
Thread ID identifies conversation
      ↓
Checkpointer loads state
      ↓
Graph executes
      ↓
State updated
      ↓
Checkpointer saves checkpoint
      ↓
Next request
      ↓
Retrieve state
```

Then when history becomes large:

```text
Large history
      ↓
Trim OR summarize
      ↓
Smaller active context
      ↓
Continue
```

---

# 49. Complete Architecture

Putting everything together:

```text
                     USER
                       │
                       ↓
                 New Message
                       │
                       ↓
                 thread_id
                       │
                       ↓
              ┌────────────────┐
              │   Checkpointer │
              └────────────────┘
                       │
                       ↓
                Retrieve State
                       │
                       ↓
              ┌─────────────────┐
              │  Memory Manager │
              └─────────────────┘
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
        Small history       Large history
             │                   │
             │              Summarization
             │                   │
             │              Delete old msgs
             │                   │
             └─────────┬─────────┘
                       ↓
               Summary + Recent
                       │
                       ↓
                      LLM
                       │
                       ↓
                    Response
                       │
                       ↓
                  Save State
                       │
                       ↓
                  Checkpointer
```

---

# 50. In-Memory vs Persistent Memory

| Feature                        | InMemorySaver      | PostgreSQL Checkpointer |
| ------------------------------ | ------------------ | ----------------------- |
| Storage                        | RAM                | Database                |
| Restart survives?              | ❌                  | ✅                       |
| Development                    | Excellent          | Good                    |
| Production                     | Usually unsuitable | Suitable                |
| Persistence                    | ❌                  | ✅                       |
| Multiple application instances | Limited            | Much better             |
| Database required              | ❌                  | ✅                       |
| Good for prototypes            | ✅                  | ✅                       |
| Good for production            | ❌                  | ✅                       |

---

# 51. Trimming vs Summarization

| Feature                   | Trimming             | Summarization              |
| ------------------------- | -------------------- | -------------------------- |
| Basic idea                | Remove old messages  | Compress old messages      |
| Token reduction           | High                 | High                       |
| Preserves old information | ❌                    | ✅ approximately            |
| Complexity                | Low                  | Higher                     |
| Cost                      | Low                  | Requires LLM call          |
| Risk of information loss  | High                 | Lower, but possible        |
| Good for                  | Simple conversations | Long-running conversations |

---

# 52. Trimming vs Deletion vs Summarization

These terms should not be mixed up.

### Trimming

Reduce the messages supplied to the model.

```text
History
 ↓
Keep recent messages
```

### Deletion

Actually remove messages from the graph's message state.

```text
M1 M2 M3 M4 M5
 ↓
Delete M1 M2 M3
```

### Summarization

Compress old messages before deleting them.

```text
M1 M2 M3 M4
      ↓
  Summary
      ↓
Delete M1-M4
```

---

# 53. Short-Term Memory vs Long-Term Memory

This is another important distinction.

### Short-Term Memory

Associated with a conversation/thread.

```text
Thread A
 ├── messages
 ├── state
 └── checkpoint
```

Useful for:

* Current conversation
* Current task
* Previous messages
* Tool state
* Workflow state

### Long-Term Memory

Information that should survive across conversations.

For example:

```text
User preferences
User profile
Persistent facts
Past experiences
```

Conceptually:

```text
Thread A ──┐
Thread B ──┼──→ Long-term memory
Thread C ──┘
```

Short-term memory is primarily about **the current thread's state**.

---

# 54. Important Mental Model

Think about ChatGPT-like applications as having several layers:

```text
                 AI Application
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   Short-term      Long-term       External
     memory         memory          knowledge
        │              │              │
    Thread state    User facts       RAG
    Checkpoints     Preferences      Documents
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                  Context Builder
                       ↓
                       LLM
```

The LLM itself isn't necessarily storing all this information.

The **application architecture** manages it.

---

# 55. Why LangGraph Is Good for Memory

LangGraph is particularly suitable because it models an application as:

```text
State
+
Nodes
+
Edges
+
Persistence
```

Memory naturally fits into this architecture.

You can have:

```text
State
  ↓
Checkpoint
  ↓
Thread
  ↓
Persistence
```

and then build more sophisticated workflows:

```text
Chat
 ↓
Check context
 ↓
Trim
 ↓
Summarize
 ↓
Delete
 ↓
Continue
```

---

# 56. Production Considerations

When implementing short-term memory in a real application, consider:

### 1. Thread identity

Every conversation needs a stable identifier.

```text
thread_id
```

---

### 2. Persistent storage

Don't depend solely on RAM.

```text
PostgreSQL
```

is a strong option.

---

### 3. Context limits

Always account for the model's context window.

---

### 4. Token-aware management

Prefer token-based limits over simply counting messages.

---

### 5. Summarization

Use summarization when conversations become long.

---

### 6. Recent-message preservation

Don't summarize everything blindly.

Keep recent messages because they contain the immediate conversational context.

---

### 7. Summary quality

A bad summary can lose important information.

Therefore summaries should ideally preserve:

```text
User goals
Important facts
Decisions
Preferences
Constraints
Important previous conclusions
Current task status
```

---

# 57. A Practical Memory Strategy

For a real chatbot, a good architecture could be:

```text
                  Incoming message
                         │
                         ↓
                  Load thread state
                         │
                         ↓
               Is context within budget?
                    /          \
                  Yes           No
                   │             │
                   │       Create summary
                   │             │
                   │       Remove old msgs
                   │             │
                   └──────┬──────┘
                          ↓
                  Summary + recent msgs
                          ↓
                         LLM
                          ↓
                      New response
                          ↓
                  Save checkpoint
                          ↓
                     PostgreSQL
```

This is a very practical production pattern.

---

# 58. Example End-to-End Concept

Imagine a user has a conversation:

```text
User:
I'm building a RAG chatbot.

AI:
Great. You can use embeddings...

User:
I'm using PostgreSQL.

AI:
You can use pgvector...

User:
I want to add LangGraph.

AI:
You can create a retrieval node...

...
```

After 100 messages, instead of sending everything:

```text
M1 + M2 + ... + M100
```

we can maintain:

```text
Summary:

The user is building a RAG chatbot using PostgreSQL
and wants to integrate LangGraph. The system uses
retrieval and vector search. The user is currently
working on conversation memory.
```

Plus:

```text
Recent messages:

M96
M97
M98
M99
M100
```

The LLM receives:

```text
Summary
+
Recent conversation
+
Current query
```

This gives the model a compressed understanding of the conversation.

---

# 59. Key Code Concepts to Remember

### Checkpointer

```python
checkpointer = InMemorySaver()
```

or a persistent checkpointer such as PostgreSQL-backed storage.

---

### Compile with checkpointer

```python
graph = builder.compile(
    checkpointer=checkpointer
)
```

---

### Thread ID

```python
config = {
    "configurable": {
        "thread_id": "conversation-123"
    }
}
```

---

### Invoke

```python
graph.invoke(
    {
        "messages": [
            HumanMessage(content="Hello")
        ]
    },
    config=config
)
```

The same `thread_id` allows LangGraph to associate subsequent invocations with the same conversation.

---

# 60. The Most Important Concept

Don't think:

> "LangGraph gives the LLM memory."

Instead think:

> **LangGraph provides mechanisms for maintaining, checkpointing, retrieving, and managing application state so that the relevant state can be supplied to the LLM.**

This is a much more accurate mental model.

---

# 61. Final Mental Diagram

Memorize this:

```text
                LLM
                 ↑
                 │
          Relevant Context
                 ↑
                 │
      ┌─────────────────────┐
      │  Memory Management  │
      │                     │
      │ Summary             │
      │ Recent Messages     │
      │ Current State       │
      └──────────┬──────────┘
                 ↑
                 │
          LangGraph State
                 ↑
                 │
            Checkpointer
                 ↑
        ┌────────┴────────┐
        │                 │
   In-Memory          PostgreSQL
   (temporary)        (persistent)
        │                 │
        └────────┬────────┘
                 │
              Thread
                 │
                 ↓
          Conversation
```

---

# 62. Quick Revision

### LLMs

```text
LLM = Stateless
```

They don't automatically remember previous API calls.

### Short-term memory

```text
Conversation-specific state
```

### Thread

```text
thread_id → identifies conversation
```

### Checkpointer

```text
Saves and retrieves graph state
```

### InMemorySaver

```text
Fast
Simple
Temporary
```

### PostgreSQL checkpointer

```text
Persistent
Survives restart
Better for production
```

### Context window

```text
Maximum amount of information
the model can process in one call
```

### Context overflow

```text
Conversation becomes too large
```

### Trimming

```text
Keep only relevant/recent messages
```

### Summarization

```text
Compress old conversation into a summary
```

### Deletion

```text
Remove old messages after their information
has been compressed/preserved elsewhere
```

### Best long-conversation pattern

```text
Summary
+
Recent Messages
+
Current User Query
       ↓
      LLM
```

---

## ⭐ Exam/Interview-Level Takeaway

If you're asked **"How does short-term memory work in LangGraph?"**, a strong answer is:

> **LangGraph maintains short-term memory as graph state associated with a conversation thread. A checkpointer persists checkpoints of that state, allowing subsequent invocations with the same `thread_id` to recover the previous conversation state. During development, an in-memory checkpointer can be used, while production systems generally use persistent storage such as PostgreSQL. Because storing the entire conversation indefinitely can exceed the LLM's context window, memory must also be managed. Trimming can remove older messages from the active context, while summarization compresses older conversation into a concise summary and allows the original messages to be removed. A practical long-conversation architecture therefore combines a persistent checkpointer with a summary and recent messages.**

The **core progression to remember** is:

```text
LLM is stateless
       ↓
Need application state
       ↓
LangGraph State
       ↓
Thread
       ↓
Checkpointer
       ↓
InMemorySaver / PostgreSQL
       ↓
Conversation grows
       ↓
Context overflow
       ↓
Trimming OR Summarization
       ↓
Summary + Recent Messages
       ↓
LLM
```

This is the foundation you'll need before moving into **LangGraph long-term memory, stores, user-level memory, semantic memory, and memory + RAG architectures**.
