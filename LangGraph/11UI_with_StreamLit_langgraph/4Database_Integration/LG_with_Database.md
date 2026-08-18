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

# 10. Graph structure

We can create:

```python
from langgraph.graph import StateGraph, START, END
```

Then:

```python
graph = StateGraph(State)

graph.add_node("get_user", get_user)

graph.add_edge(START, "get_user")
graph.add_edge("get_user", END)
```

Compile:

```python
app = graph.compile()
```

Run:

```python
result = app.invoke({
    "user_id": 1
})
```

Result:

```python
{
    "user_id": 1,
    "user_data": {
        "id": 1,
        "name": "Suman",
        "email": "suman@example.com"
    }
}
```

---

# 11. Combining checkpointer + application database

This is where things become interesting.

You can have:

```text
                     LangGraph
                         │
              ┌──────────┴──────────┐
              │                     │
              ↓                     ↓
        Checkpointer           DB operations
              │                     │
              ↓                     ↓
        SQLite database       Application database
              │                     │
              ↓                     ↓
       conversation           users / expenses
       checkpoints            products / orders
```

For example:

```python
conn = sqlite3.connect(
    "chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)

app = graph.compile(
    checkpointer=checkpointer
)
```

And inside a node:

```python
def get_user(state):

    db = sqlite3.connect("chatbot.db")

    cursor = db.cursor()

    cursor.execute(
        "SELECT name FROM users WHERE id = ?",
        (state["user_id"],)
    )

    user = cursor.fetchone()

    db.close()

    return {
        "user_name": user[0]
    }
```

Technically this works, but for a larger application I'd recommend separating the concerns.

---

# 12. Better architecture

Instead of putting SQL directly inside every LangGraph node:

```text
LangGraph Node
      │
      ↓
SQL query
      │
      ↓
Database
```

use a repository/service layer:

```text
LangGraph Node
      │
      ↓
UserRepository
      │
      ↓
Database
```

For example:

```python
class UserRepository:

    def __init__(self, connection):
        self.connection = connection

    def get_user(self, user_id):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        )

        return cursor.fetchone()
```

Then the LangGraph node becomes:

```python
def get_user(state):

    user = user_repository.get_user(
        state["user_id"]
    )

    return {
        "user_data": user
    }
```

This is much cleaner.

---

# 13. Why this architecture is better

Imagine you have:

```text
20 LangGraph nodes
```

If every node contains:

```python
sqlite3.connect(...)
cursor.execute(...)
cursor.fetchall()
connection.close()
```

your code becomes difficult to maintain.

Instead:

```text
                    LangGraph
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
 User Node       Expense Node      Order Node
       │               │               │
       └───────────────┼───────────────┘
                       ↓
                  Repository
                       │
                       ↓
                   Database
```

This gives you separation of concerns.

---

# 14. Database + LLM

A very common LangGraph architecture is:

```text
                    User
                     │
                     ↓
                  LLM Node
                     │
             "I need database
               information"
                     │
                     ↓
                Tool / Node
                     │
                     ↓
                  Database
                     │
                     ↓
                Query result
                     │
                     ↓
                  LLM Node
                     │
                     ↓
                Final answer
```

For example:

> "How much did I spend on food this month?"

The graph might perform:

```text
START
  ↓
understand_question
  ↓
query_expenses
  ↓
calculate_total
  ↓
generate_answer
  ↓
END
```

---

# 15. Example with an expense application

This is particularly useful for a project like **MeroHisab**.

Imagine your database:

```text
users
expenses
income
borrow
lend
```

Your LangGraph could look like:

```text
                    User
                     │
                     ↓
              Intent Detection
                     │
        ┌────────────┼─────────────┐
        ↓            ↓             ↓
     Expense       Income       Borrow/Lend
       Node          Node           Node
        │            │              │
        └────────────┼──────────────┘
                     ↓
                 Database
                     │
                     ↓
                Result
                     │
                     ↓
                 LLM Node
                     │
                     ↓
                  Answer
```

For example:

```text
User:
"How much did I spend this month?"
```

Graph:

```text
START
  ↓
intent
  ↓
expense_query
  ↓
database
  ↓
calculate
  ↓
LLM
  ↓
END
```

Response:

```text
You spent Rs. 18,500 this month.

Food: Rs. 7,200
Transport: Rs. 3,800
Entertainment: Rs. 2,500
Other: Rs. 5,000
```

---

# 16. Don't store everything in LangGraph state

This is an important design principle.

You might be tempted to do:

```python
state["all_expenses"] = 50000 rows
```

Don't.

The LangGraph state should contain the information needed for the graph execution.

Instead:

```text
Database
   ↓
query
   ↓
small result
   ↓
LangGraph state
```

For example:

```python
{
    "total_expense": 18500,
    "category": "food"
}
```

rather than putting your entire database into state.

---

# 17. Checkpointer vs Database

This distinction is worth remembering:

| Feature            | Checkpointer     | Application DB         |
| ------------------ | ---------------- | ---------------------- |
| Purpose            | Save graph state | Store application data |
| Conversation state | ✅                | Possible               |
| Thread state       | ✅                | Possible               |
| Users              | ❌                | ✅                      |
| Expenses           | ❌                | ✅                      |
| Orders             | ❌                | ✅                      |
| Graph recovery     | ✅                | ❌                      |
| LangGraph-specific | ✅                | ❌                      |
| SQLite             | ✅                | ✅                      |
| PostgreSQL         | ✅                | ✅                      |

Think of it this way:

> **Checkpointer = memory of the graph execution**

> **Database = source of truth for your application**

---

# 18. SQLite vs PostgreSQL

For learning and small applications:

```text
SQLite
  ↓
Very easy
  ↓
One file
  ↓
No database server
```

Excellent for:

* learning
* prototypes
* local applications
* small Streamlit apps
* personal projects

For production applications with many concurrent users:

```text
PostgreSQL
```

is usually a better choice.

Architecture:

```text
Development:

LangGraph
   ↓
SQLite


Production:

LangGraph
   ↓
PostgreSQL
```

The LangGraph concepts remain largely the same.

---

# 19. SQLite database file

After running your application, you may see:

```text
project/
│
├── app.py
├── graph.py
├── chatbot.db
└── ...
```

You can inspect the database using tools such as:

* SQLite Browser
* VS Code SQLite extensions
* Python's `sqlite3` module
* command-line SQLite

---

# 20. A realistic LangGraph project structure

For your chatbot projects, I'd structure it approximately like this:

```text
langgraph_app/
│
├── main.py
│
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── nodes.py
│   └── graph.py
│
├── database/
│   ├── connection.py
│   ├── models.py
│   └── repository.py
│
├── persistence/
│   └── checkpointer.py
│
├── ui/
│   └── streamlit_app.py
│
├── data/
│   └── app.db
│
└── requirements.txt
```

The responsibilities become:

```text
graph/
    → LangGraph logic

database/
    → application data

persistence/
    → LangGraph checkpoints

ui/
    → Streamlit
```

That's a very scalable way to organize the project.

---

# 21. The complete mental model

The most important thing to understand is this:

```text
                         APPLICATION
                              │
                              ↓
                          LangGraph
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ↓                             ↓
          Graph State                 Application Data
               │                             │
               ↓                             ↓
         Checkpointer                  Repository
               │                             │
               ↓                             ↓
            SQLite                    SQLite/PostgreSQL
```

So when you hear:

**"LangGraph database integration"**

don't immediately think:

> "LangGraph stores everything in the database."

Instead think:

### 1. LangGraph persistence

```text
Graph → Checkpointer → Database
```

Used for:

* thread state
* conversation history
* checkpoints
* graph recovery
* human-in-the-loop workflows

### 2. Application database

```text
Graph Node → Repository → Database
```

Used for:

* users
* expenses
* products
* orders
* business data
* application-specific information

---

## What I recommend you learn next

Since you're currently working with **LangGraph + Streamlit + threaded conversations**, the most useful progression is:

```text
1. LangGraph State
       ↓
2. Checkpoints
       ↓
3. thread_id
       ↓
4. SQLite Checkpointer
       ↓
5. Retrieve conversation history
       ↓
6. SQLite application database
       ↓
7. LangGraph node → database query
       ↓
8. LLM + database
       ↓
9. PostgreSQL
       ↓
10. Production architecture
```

The **next important topic is specifically `SqliteSaver` + `thread_id` + retrieving previous checkpoints**, because that will directly connect what you've already built in your Streamlit chatbot to persistent conversations.
