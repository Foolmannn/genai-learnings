# LangGraph with Database Integration

When you integrate a database with **LangGraph**, there are actually **two different things** you might want to store:

1. **Graph state / conversation checkpoints**
2. **Application data**

These are related, but they should not be confused.

```text
                    Your Application
                          │
              ┌───────────┴───────────┐
              │                       │
          LangGraph               Database
              │                       │
       Graph State              Application Data
       Checkpoints              Users / Expenses
       Conversation             Products / Orders
       Thread State             Documents / etc.
```

For your chatbot projects, this distinction is extremely important.

---

# 1. Two types of database integration

Suppose you're building a chatbot.

A user says:

> My name is Suman and I live in Kathmandu.

You might want to store this information.

There are two possible approaches.

### Approach 1 — LangGraph checkpoint

Store the **conversation state**:

```text
thread_id
    ↓
messages
    ↓
HumanMessage
AIMessage
HumanMessage
AIMessage
```

This is handled by a **checkpointer**.

For example:

```python
SqliteSaver
```

---

### Approach 2 — Application database

Store actual application information:

```text
users
────────────────────
id
name
email
city
```

This is your normal database.

You might use:

* SQLite
* PostgreSQL
* MySQL
* MongoDB
* etc.

LangGraph nodes can interact with these databases.

---

# 2. Architecture

A typical LangGraph application might look like this:

```text
                    Streamlit
                       │
                       ↓
                  LangGraph
                       │
          ┌────────────┴────────────┐
          ↓                         ↓
    Checkpointer              Application DB
          │                         │
          ↓                         ↓
       SQLite                  PostgreSQL
          │
          ↓
   Conversation State
```

For a simple project:

```text
LangGraph
    │
    ├── SQLite Checkpointer
    │
    └── SQLite Application Database
```

You can even use the same SQLite database file, although separating responsibilities can make larger applications cleaner.

---

# 3. What is a checkpointer?

A checkpointer saves the **state of the graph at different points in execution**.

For example:

```text
START
  ↓
retrieve_user
  ↓
generate_response
  ↓
save_response
  ↓
END
```

After execution, LangGraph can save the state.

Conceptually:

```text
Checkpoint
────────────────────────
thread_id
checkpoint_id
state
messages
metadata
```

This allows LangGraph to resume a conversation.

---

# 4. SQLite Checkpointer

Install:

```bash
pip install langgraph-checkpoint-sqlite
```

Then:

```python
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
```

Create a connection:

```python
conn = sqlite3.connect(
    "chatbot.db",
    check_same_thread=False
)
```

Create the checkpointer:

```python
checkpointer = SqliteSaver(conn)
```

Then compile your graph:

```python
app = graph.compile(
    checkpointer=checkpointer
)
```

Now LangGraph can persist graph state.

---

# 5. Using thread IDs

When invoking the graph:

```python
config = {
    "configurable": {
        "thread_id": "user-123"
    }
}
```

Then:

```python
response = app.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Hello"
            }
        ]
    },
    config=config
)
```

The important relationship is:

```text
thread_id
     │
     ↓
checkpoint
     │
     ↓
conversation state
```

---

# 6. Multiple conversations

Suppose your Streamlit application has:

```text
Thread A
Thread B
Thread C
```

You can give each conversation a different ID:

```python
thread_a = {
    "configurable": {
        "thread_id": "abc123"
    }
}

thread_b = {
    "configurable": {
        "thread_id": "xyz789"
    }
}
```

Now:

```text
abc123
   ↓
Conversation A


xyz789
   ↓
Conversation B
```

They don't share the same checkpoint state.

This is exactly what you need when implementing the **ChatGPT-like conversation/thread system** you've been working on.

---

# 7. Normal database integration

Now suppose your chatbot needs to retrieve information from a database.

For example:

```text
User:
"What are my expenses this month?"
```

Your database might contain:

```text
expenses
────────────────────────────
id
user_id
amount
category
date
description
```

LangGraph can have a node that queries this database.

Architecture:

```text
User
 ↓
LangGraph
 ↓
Expense Node
 ↓
SQLite
 ↓
expenses table
 ↓
Result
 ↓
LLM
 ↓
Response
```

---

# 8. Example SQLite database

Let's create a simple database.

```python
import sqlite3

conn = sqlite3.connect("app.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT
)
""")

conn.commit()
```

Insert data:

```python
cursor.execute(
    """
    INSERT INTO users (name, email)
    VALUES (?, ?)
    """,
    ("Suman", "suman@example.com")
)

conn.commit()
```

Retrieve data:

```python
cursor.execute(
    "SELECT * FROM users"
)

users = cursor.fetchall()

print(users)
```

---

# 9. Using the database inside a LangGraph node

Suppose we have:

```python
from typing import TypedDict


class State(TypedDict):
    user_id: int
    user_data: dict
```

We can create a node:

```python
def get_user(state: State):

    user_id = state["user_id"]

    conn = sqlite3.connect("app.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    return {
        "user_data": {
            "id": user[0],
            "name": user[1],
            "email": user[2]
        }
    }
```

The LangGraph node is now interacting with the database.

---
