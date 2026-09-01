# Long-Term Memory in LangGraph

In LangGraph, **long-term memory** means storing information about a user or application **across different conversations/threads** so that the agent can retrieve it later.

This is different from short-term memory:

| Type     | Short-term memory                | Long-term memory                |
| -------- | -------------------------------- | ------------------------------- |
| Scope    | One conversation/thread          | Across conversations            |
| Purpose  | Remember current conversation    | Remember user facts/preferences |
| Storage  | Checkpointer                     | Store                           |
| Example  | "What was my previous question?" | "User prefers dark mode"        |
| Lifetime | Thread/session                   | Persistent                      |

A useful mental model is:

```text
                 LangGraph Agent
                       │
          ┌────────────┴────────────┐
          │                         │
   Short-term memory         Long-term memory
          │                         │
     Checkpointer                  Store
          │                         │
   Thread-specific          User-specific
     messages                facts/preferences
```

---

# 1. Why do we need long-term memory?

Suppose a user talks to your AI agent today:

```text
User:
My name is Suman and I'm learning machine learning.

Agent:
Nice to meet you, Suman!
```

Tomorrow the user starts a **new conversation**:

```text
User:
What should I learn next?
```

Without long-term memory:

```text
Agent:
I don't know what you're currently learning.
```

With long-term memory:

```text
Agent:
Since you're learning machine learning,
I'd recommend moving next to...
```

The important point is that the second conversation may have a **different thread ID**.

---

# 2. Short-term vs long-term memory

This distinction is extremely important in LangGraph.

### Short-term memory

Suppose:

```text
thread_id = "conversation-123"
```

You have:

```text
User: My name is Suman.
AI: Nice to meet you.

User: What is my name?
AI: Your name is Suman.
```

The checkpointer stores the state associated with:

```text
conversation-123
```

If you create:

```text
thread_id = "conversation-456"
```

that conversation doesn't automatically have the previous conversation's state.

---

### Long-term memory

Long-term memory is organized independently of a particular conversation.

For example:

```text
namespace = ("users", "suman")
```

Inside that namespace you might store:

```json
{
    "name": "Suman",
    "learning": ["Python", "Machine Learning", "LangGraph"],
    "preferred_language": "English"
}
```

Now multiple conversations can access the same information.

```text
Conversation A
       │
       ├──────┐
Conversation B│
       │      │
Conversation C│
       │      ▼
       └──> Long-term Store
```

---

# 3. LangGraph's `Store`

LangGraph provides a **Store abstraction** for long-term memory.

Conceptually:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
```

Then you can save information:

```python
store.put(
    ("users", "suman"),
    "profile",
    {
        "name": "Suman",
        "learning": "Machine Learning"
    }
)
```

The structure is roughly:

```text
namespace
   │
   └── key
        │
        └── value
```

For example:

```text
("users", "suman")
```

is the namespace.

```text
"profile"
```

is the key.

And:

```python
{
    "name": "Suman",
    "learning": "Machine Learning"
}
```

is the value.

---

# 4. Basic example

Let's build a simple long-term memory system.

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
```

Save a memory:

```python
store.put(
    ("users", "suman"),
    "profile",
    {
        "name": "Suman",
        "occupation": "Student",
        "interest": "Machine Learning"
    }
)
```

Now retrieve it:

```python
memory = store.get(
    ("users", "suman"),
    "profile"
)

print(memory.value)
```

Output:

```python
{
    'name': 'Suman',
    'occupation': 'Student',
    'interest': 'Machine Learning'
}
```

---

# 5. Understanding namespace

Namespaces are very important.

Imagine your application has:

```text
User 1 → Suman
User 2 → Ram
User 3 → Hari
```

You don't want their memories mixed together.

So you can create separate namespaces:

```python
("users", "suman")
("users", "ram")
("users", "hari")
```

For Suman:

```python
store.put(
    ("users", "suman"),
    "profile",
    {
        "name": "Suman",
        "interest": "AI"
    }
)
```

For Ram:

```python
store.put(
    ("users", "ram"),
    "profile",
    {
        "name": "Ram",
        "interest": "Web Development"
    }
)
```

Now each user has isolated memories.

---

# 6. Long-term memory with LangGraph

Now let's connect the store to a LangGraph application.

First:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START
from langgraph.store.memory import InMemoryStore
```

Define state:

```python
class State(TypedDict):
    user_id: str
    message: str
    response: str
```

Create store:

```python
store = InMemoryStore()
```

Create a node:

```python
def chatbot(state: State, *, store):

    user_id = state["user_id"]

    namespace = ("users", user_id)

    memory = store.get(
        namespace,
        "profile"
    )

    if memory:
        profile = memory.value
    else:
        profile = {}

    name = profile.get("name", "there")

    response = f"Hello {name}! You said: {state['message']}"

    return {
        "response": response
    }
```

Build graph:

```python
builder = StateGraph(State)

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")

graph = builder.compile(store=store)
```

Now invoke:

```python
result = graph.invoke(
    {
        "user_id": "suman",
        "message": "Hello"
    }
)

print(result)
```

The important part is:

```python
graph = builder.compile(store=store)
```

This makes the store available to the graph.

---

# 7. Reading and writing memories inside nodes

A node can both **read** and **write** memories.

For example:

```python
def chatbot(state: State, *, store):

    user_id = state["user_id"]

    namespace = ("users", user_id)

    memory = store.get(
        namespace,
        "profile"
    )

    profile = memory.value if memory else {}

    # Update memory
    profile["name"] = "Suman"

    store.put(
        namespace,
        "profile",
        profile
    )

    return {
        "response": "Memory updated!"
    }
```

So the workflow becomes:

```text
User message
     │
     ▼
LangGraph Node
     │
     ├──── Read memory
     │
     ├──── Process request
     │
     └──── Write/update memory
              │
              ▼
        Long-term Store
```

---

# 8. Memory should not simply be the entire conversation

A common beginner mistake is:

```text
Conversation 1
      ↓
Store EVERYTHING
      ↓
Conversation 2
      ↓
Store EVERYTHING
      ↓
Conversation 100
```

This becomes inefficient.

Instead, long-term memory should usually contain **useful durable information**.

For example:

```json
{
    "name": "Suman",
    "preferred_framework": "LangGraph",
    "experience_level": "intermediate",
    "current_project": "AI chatbot"
}
```

rather than:

```text
User: Hi
AI: Hello
User: How are you?
AI: I'm good.
User: Explain LangGraph.
AI: ...
...
```

The latter belongs more naturally to conversation history/checkpointing.

---

# 9. Semantic memory

Long-term memory is often divided conceptually into different types.

One important type is **semantic memory**.

Semantic memory stores facts about the user.

For example:

```text
User prefers Python.
User is learning LangGraph.
User uses Windows.
User prefers detailed explanations.
```

You could store:

```python
store.put(
    ("users", "suman"),
    "preferences",
    {
        "language": "Python",
        "framework": "LangGraph",
        "explanation_style": "detailed"
    }
)
```

Then retrieve:

```python
memory = store.get(
    ("users", "suman"),
    "preferences"
)
```

---

# 10. Episodic memory

Another useful concept is **episodic memory**.

This stores important events or experiences.

For example:

```text
User completed Logistic Regression.
User built an expense tracker.
User deployed an AI chatbot.
```

You might store:

```python
store.put(
    ("users", "suman"),
    "episode-001",
    {
        "event": "Completed Logistic Regression",
        "date": "2026-08-30"
    }
)
```

Then:

```python
store.put(
    ("users", "suman"),
    "episode-002",
    {
        "event": "Started LangGraph",
        "date": "2026-08-31"
    }
)
```

---


# 11. Searching long-term memory

A major feature of the Store is that you can search memories.

Conceptually:

```python
results = store.search(
    ("users", "suman")
)
```

You can also use semantic search when your store/backend supports embeddings.

For example, imagine memories:

```text
Suman is learning machine learning.
Suman is interested in LangGraph.
Suman built an expense tracker.
Suman wants to deploy GenAI applications.
```

User asks:

```text
What AI projects have I worked on?
```

A semantic search can retrieve relevant memories even if the exact words don't match.

---

# 12. Semantic search architecture

This is where long-term memory becomes particularly powerful.

```text
                 User
                  │
                  ▼
              LLM Agent
                  │
           "What do I know?"
                  │
                  ▼
          Memory Retrieval
                  │
                  ▼
          ┌───────────────┐
          │ Vector Search │
          └───────────────┘
                  │
                  ▼
       Relevant memories
                  │
                  ▼
                 LLM
                  │
                  ▼
              Response
```

The memories can be embedded into vectors:

```text
Memory
  ↓
Embedding Model
  ↓
Vector
  ↓
Vector Store
```

When the user asks something:

```text
Question
   ↓
Embedding
   ↓
Similarity Search
   ↓
Relevant memories
```

---

# 13. Long-term memory + short-term memory

A production LangGraph application will often use **both**.

```text
                    LangGraph
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   Short-term memory        Long-term memory
      Checkpointer               Store
          │                         │
          ▼                         ▼
    Conversation              User facts
       history                Preferences
       Messages               Important events
       State                  Learned info
```

For example:

### Short-term

```text
User:
Explain RAG.

AI:
RAG means Retrieval Augmented Generation...

User:
What are its components?

AI:
The components are...
```

The agent needs the conversation context.

### Long-term

```text
User:
Remember that I'm building a RAG application.
```

That information should survive the conversation.

---

# 14. Using a persistent database

`InMemoryStore` is useful for learning:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
```

But there is an important limitation:

```text
Application stops
      ↓
Memory disappears
```

For production, you need a persistent store/backend.

For example:

```text
PostgreSQL
Redis
MongoDB
Other supported persistent backends
```

The architecture becomes:

```text
                 LangGraph
                     │
                     ▼
              Persistent Store
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      User A       User B       User C
     memories     memories     memories
```

---

# 15. Memory extraction with an LLM

A more advanced system doesn't require the user to explicitly say:

```text
Remember this.
```

The agent can determine whether something is worth remembering.

For example:

```text
User:
I'm currently learning LangGraph and I'm building a RAG chatbot.
```

The LLM can extract:

```json
{
    "should_store": true,
    "memories": [
        "User is learning LangGraph",
        "User is building a RAG chatbot"
    ]
}
```

Then your application writes those memories to the Store.

Architecture:

```text
                 User
                  │
                  ▼
              Main LLM
                  │
                  ▼
          Memory Extraction
                  │
                  ▼
          ┌───────────────┐
          │ Is this worth │
          │ remembering?  │
          └───────┬───────┘
                  │
              Yes │
                  ▼
          Long-term Store
```

---

# 16. Important design pattern

A good long-term-memory system often looks like this:

```text
                         User
                          │
                          ▼
                     LangGraph
                          │
             ┌────────────┴────────────┐
             │                         │
             ▼                         ▼
       Retrieve Memory           Current State
             │                         │
             └────────────┬────────────┘
                          ▼
                         LLM
                          │
                          ▼
                       Response
                          │
                          ▼
                  Memory Extraction
                          │
                          ▼
                   Update Store
```

So there are actually **two memory operations**:

### Before generating response

```text
Retrieve relevant memories
```

### After generating response

```text
Store/update useful memories
```

---

# 17. `user_id` vs `thread_id`

This is one of the most important concepts.

You may have:

```text
user_id = "suman"
```

and:

```text
thread_id = "conversation-123"
```

They serve different purposes.

### `thread_id`

Identifies a particular conversation.

```text
suman
 ├── thread-001
 ├── thread-002
 └── thread-003
```

### `user_id`

Identifies the person whose long-term memories should be retrieved.

```text
user: suman
     │
     ├── preferences
     ├── profile
     ├── projects
     └── important facts
```

Therefore:

```text
thread_id → short-term memory
user_id   → long-term memory
```

This distinction is extremely useful when designing production agents.

---

# 18. Example architecture for a real application

Imagine you're building a personal AI assistant.

A user says:

```text
My name is Suman.
I prefer Python.
I'm learning machine learning.
I'm currently learning LangGraph.
```

Your system might store:

```text
Namespace:
("users", "suman")

Memories:

profile:
{
    name: "Suman"
}

preferences:
{
    programming_language: "Python"
}

learning:
{
    current: ["Machine Learning", "LangGraph"]
}
```

Later:

```text
New conversation
thread_id = "xyz789"
```

User:

```text
What should I learn next?
```

Your LangGraph retrieves:

```text
Machine Learning
LangGraph
Python
```

and sends relevant information to the LLM.

The LLM can respond based on the user's historical context.

---

# 19. Production-level mental model

Think of LangGraph memory as three layers:

```text
┌───────────────────────────────────────────┐
│                 LangGraph                 │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │ Short-term memory                   │  │
│  │                                     │  │
│  │ Checkpointer                        │  │
│  │ Messages / State / Current thread   │  │
│  └─────────────────────────────────────┘  │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │ Long-term memory                    │  │
│  │                                     │  │
│  │ Store                               │  │
│  │ User facts / preferences / events   │  │
│  └─────────────────────────────────────┘  │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │ Retrieval                            │  │
│  │                                     │  │
│  │ Search relevant memories            │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

---

# 20. Key APIs to remember

For LangGraph long-term memory, focus on these concepts:

```python
InMemoryStore
```

for development/testing.

```python
store.put(...)
```

to save memory.

```python
store.get(...)
```

to retrieve a specific memory.

```python
store.search(...)
```

to search memories.

And:

```python
graph = builder.compile(store=store)
```

to make the Store available to graph nodes.

---

## Short-term vs Long-term — remember this

If you're studying LangGraph, memorize this:

```text
CHECKPOINTER
     ↓
Short-term memory
     ↓
Thread / conversation
```

while:

```text
STORE
     ↓
Long-term memory
     ↓
Across threads / conversations
```

And the overall architecture:

```text
                 ┌───────────────┐
                 │     User      │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   LangGraph   │
                 └───────┬───────┘
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      ┌─────────────┐         ┌─────────────┐
      │ Checkpointer│         │    Store    │
      │             │         │             │
      │ Short-term  │         │ Long-term   │
      │ memory      │         │ memory      │
      └─────────────┘         └──────┬──────┘
                                     │
                              User profile
                              Preferences
                              Facts
                              Experiences
```

**The key idea:** a LangGraph checkpointer remembers the **conversation state**, while a Store lets your application remember **information that should persist beyond a single conversation**.

