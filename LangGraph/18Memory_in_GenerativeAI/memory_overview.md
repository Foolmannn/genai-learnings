
# Memory in Generative AI — Detailed Notes

## 1. Introduction: Why Memory Matters in GenAI

### What is memory in an AI system?

Memory is the mechanism that allows an AI system to **retain, retrieve, and use information from previous interactions or experiences**.

A normal LLM fundamentally works like:

```text
Input
  ↓
LLM
  ↓
Output
```

If you ask:

```text
User: My name is Suman.
AI: Nice to meet you, Suman!
```

and then start a completely new request:

```text
User: What is my name?
```

The model itself doesn't inherently know that your name is Suman.

Why?

Because the model doesn't automatically maintain a personal database of your previous conversations.

So we build a memory system around the LLM:

```text
                ┌──────────────┐
User ──────────►│     LLM      │
                └──────┬───────┘
                       │
                       ▼
                  Memory System
                       │
                       ▼
                Store / Retrieve
```

The memory system gives the LLM relevant information when it needs it.

---

# 2. How LLMs Work at Inference — Stateless by Design

This is one of the most important concepts.

## 2.1 Training vs inference

During **training**, an LLM learns patterns from enormous amounts of data.

For example:

```text
Training data:

Paris is the capital of France.
Kathmandu is the capital of Nepal.
Tokyo is the capital of Japan.
```

The model learns statistical relationships between tokens.

After training, the model parameters are stored.

During inference:

```text
Prompt
  ↓
Tokenizer
  ↓
Neural Network
  ↓
Next-token probabilities
  ↓
Generated response
```

The model uses its learned parameters to generate the response.

---

# 3. Why is an LLM Stateless?

Suppose we make two independent API calls.

### Request 1

```text
User:
My name is Suman.
```

LLM receives:

```text
"My name is Suman."
```

and returns:

```text
"Nice to meet you, Suman!"
```

### Request 2

```text
User:
What is my name?
```

LLM receives only:

```text
"What is my name?"
```

It doesn't automatically receive:

```text
"My name is Suman."
```

Therefore:

```text
Request 1 ──► LLM ──► Response 1

Request 2 ──► LLM ──► Response 2
```

The second request doesn't inherently contain the first request.

### Important distinction

The model's **parameters** contain learned knowledge.

They don't normally contain:

```text
User-specific conversation history
```

in a dynamically updated way.

So:

> **An LLM can have knowledge without having conversational memory.**

---

# 4. The Core Problem: LLMs Have No Memory

Consider this conversation:

```text
User: I'm learning machine learning.

AI: Great!

User: I'm currently studying regression.

AI: Nice.

User: What should I learn next?
```

A human can naturally remember:

```text
User → learning ML
User → studying regression
```

and answer accordingly.

But an LLM needs those facts to be included in its current input somehow.

Therefore an application must maintain state.

A simplified architecture:

```text
                 ┌─────────────┐
                 │    User     │
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │ Application │
                 └──────┬──────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        Memory Store             LLM
             │                     ▲
             └──── Retrieved ──────┘
```

The application becomes responsible for remembering.

---

# 5. Building Memory Around LLMs — First Principles

The key idea is:

> **Memory is not necessarily something inside the LLM. It can be an external system that supplies relevant information to the LLM.**

Think of the LLM as the reasoning engine.

```text
LLM = Brain
Memory = External storage
Application = Coordinator
```

A typical memory workflow:

```text
User Message
     │
     ▼
Retrieve relevant memories
     │
     ▼
Combine:
- current question
- previous conversation
- relevant memories
     │
     ▼
Prompt
     │
     ▼
LLM
     │
     ▼
Response
     │
     ▼
Store useful information
```

This is the fundamental architecture behind many AI memory systems.

---

# 6. Context Window and In-Context Learning

## 6.1 What is a context window?

A context window is the amount of information the model can process as input for a particular inference call.

For example, conceptually:

```text
Context Window
┌─────────────────────────────────────┐
│ System instructions                 │
│ Previous messages                   │
│ Retrieved documents                 │
│ User question                      │
└─────────────────────────────────────┘
```

The model processes this context to generate the next response.

---

## 6.2 Context is not the same as memory

This distinction is extremely important.

Suppose we send:

```text
User:
My name is Suman.
```

and then send:

```text
Previous conversation:
My name is Suman.

Current question:
What is my name?
```

The model can answer:

```text
Your name is Suman.
```

But the model isn't necessarily **remembering** this in its parameters.

The information is simply present in the current context.

Therefore:

> **Context is information available during inference; memory is a mechanism for retaining information across interactions or over time.**

---

# 7. In-Context Learning

In-context learning means providing examples/information inside the prompt so the model can adapt its response without changing its parameters.

For example:

```text
System:
You are a Python tutor.

Example:
Question: What is a list?
Answer: A list is an ordered mutable collection.

Question:
What is a tuple?
```

The model can infer the expected style from the context.

No model retraining is required.

---

# 8. Short-Term Memory

Short-term memory is usually the easiest memory mechanism to implement.

The most common approach:

> **Store the conversation history and send relevant history back to the LLM.**

Example:

```text
Conversation:

User: My name is Suman.
AI: Nice to meet you.

User: I'm learning Python.
AI: Great!

User: What language am I learning?
```

The application sends:

```text
[
    User: My name is Suman.
    AI: Nice to meet you.
    User: I'm learning Python.
    AI: Great!
    User: What language am I learning?
]
```

The LLM can therefore answer:

```text
You are learning Python.
```

---

# 9. Short-Term Memory Using Conversation History

Conceptually:

```python
messages = [
    {"role": "user", "content": "My name is Suman."},
    {"role": "assistant", "content": "Nice to meet you."},
    {"role": "user", "content": "I am learning Python."},
]
```

When the next request arrives:

```python
messages.append({
    "role": "user",
    "content": "What am I learning?"
})
```

Then:

```python
response = llm.invoke(messages)
```

The LLM sees the entire conversation.

---

# 10. How Chatbots Implement Short-Term Memory

A chatbot usually has something similar to:

```text
                    ┌─────────────┐
                    │    User     │
                    └──────┬──────┘
                           │
                           ▼
                    New User Message
                           │
                           ▼
                 Conversation History
                           │
                           ▼
                     Build Prompt
                           │
                           ▼
                         LLM
                           │
                           ▼
                       Response
                           │
                           ▼
                 Update Conversation
                           │
                           └───────────► History
```

The application might store history in:

* memory in application process
* Redis
* PostgreSQL
* SQLite
* MongoDB
* another persistent database

---

# 11. Example of Short-Term Memory

Imagine a coding assistant.

### Message 1

```text
User:
Create a Python function to calculate factorial.
```

### Message 2

```text
User:
Make it recursive.
```

The second message is incomplete by itself.

What does "it" refer to?

The previous conversation tells us:

```text
"it" = factorial function
```

Therefore the LLM needs conversation context.

---

# 12. Short-Term Memory in LangGraph

This becomes particularly relevant to the LangGraph topics you've been studying.

LangGraph represents state explicitly.

For example:

```python
from typing import TypedDict

class State(TypedDict):
    messages: list
```

The graph state can contain conversation messages.

Conceptually:

```text
State
┌─────────────────────┐
│ messages             │
│                     │
│ HumanMessage        │
│ AIMessage           │
│ HumanMessage        │
│ AIMessage            │
└─────────────────────┘
```

LangGraph can persist this state using a **checkpointer**.

This means conversation state can survive across graph invocations.

---

# 13. Thread-Based Memory

A useful concept in conversational systems is a **thread/session**.

For example:

```text
Thread A
User → Suman
User → Learning ML
User → Studying LangGraph

Thread B
User → Another person
User → Learning Java
```

Each thread has its own conversation state.

Conceptually:

```text
             Memory
                │
       ┌────────┴────────┐
       ▼                 ▼
   Thread A           Thread B
       │                 │
   Messages          Messages
```

This prevents conversations from mixing with each other.

---

# 14. Limitations of Short-Term Memory

This is where the need for long-term memory becomes clear.

## Problem 1: Context window limitation

Suppose a conversation becomes extremely long:

```text
Message 1
Message 2
Message 3
...
Message 10,000
```

You can't indefinitely send the entire history to the model.

The context becomes:

```text
Too large
   ↓
Expensive
   ↓
Slow
   ↓
Potential context limit
```

---

# 15. Problem 2: Cost

Suppose every request sends:

```text
10,000 tokens of history
+
1,000 tokens current question
```

You're repeatedly processing a huge amount of information.

This increases token usage and therefore potentially increases cost.

---

# 16. Problem 3: Latency

More tokens generally mean more processing.

Therefore:

```text
Long history
     ↓
Large prompt
     ↓
More computation
     ↓
Higher latency
```

---

# 17. Problem 4: Irrelevant Information

Imagine:

```text
Conversation history:

User's favorite food
User's favorite movie
User's previous coding problem
User's vacation
User's programming language
User's favorite football team
...
```

Then the user asks:

```text
How do I implement a binary search?
```

Most of that information is irrelevant.

Sending everything is inefficient.

We want:

```text
Current question
      ↓
Retrieve relevant memories
      ↓
LLM
```

rather than:

```text
Current question
      +
Entire history
      ↓
LLM
```

---

# 18. Problem 5: Short-Term Memory Doesn't Truly Generalize Across Sessions

Imagine:

```text
Monday:
User: I prefer Python examples.

Conversation ends.
```

Next week:

```text
New conversation:
User: Explain decorators.
```

If the old conversation isn't available, the chatbot may not know:

```text
User prefers Python examples.
```

This is where long-term memory becomes valuable.

---

# 19. Why We Need Long-Term Memory

Long-term memory allows an AI application to retain useful information **across conversations, sessions, or long periods of time**.

Example:

```text
Conversation 1:
User: I am a beginner in Python.

Conversation 2:
User: Explain decorators.

AI:
Since you're learning Python as a beginner,
let's start with the basics...
```

The information from conversation 1 can influence conversation 2.

---

# 20. Short-Term vs Long-Term Memory

| Feature         | Short-Term Memory             | Long-Term Memory                         |
| --------------- | ----------------------------- | ---------------------------------------- |
| Scope           | Current conversation          | Across conversations                     |
| Typical storage | Conversation state            | Database/vector store                    |
| Duration        | Session/thread                | Persistent                               |
| Data            | Recent messages               | Important facts/experiences              |
| Main purpose    | Maintain conversation context | Personalization & knowledge              |
| Example         | "What did I just say?"        | "What programming language do I prefer?" |

---

# 21. Types of Long-Term Memory

A particularly important classification is:

1. **Episodic memory**
2. **Semantic memory**
3. **Procedural memory**

Let's understand each carefully.

---

# 22. Episodic Memory

Episodic memory stores **events or experiences**.

Think:

> "What happened?"

Example:

```text
User discussed a machine learning project
on August 20.
```

Or:

```text
User previously asked how to deploy
a LangGraph application.
```

It represents experiences/events.

### Example

```text
Episode:
User asked about Lasso Regression.
Assistant explained sparsity.
```

Later:

```text
User:
Continue what we discussed about Lasso.
```

The system can retrieve the previous episode.

---

# 23. Semantic Memory

Semantic memory stores **facts and knowledge**.

Think:

> "What do I know?"

Example:

```text
User prefers Python.
User is learning LangGraph.
User uses React.
User is working on an expense tracker.
```

These are facts rather than complete conversations.

---

# 24. Episodic vs Semantic

### Episodic

```text
On Monday, user asked about Lasso Regression.
```

### Semantic

```text
User is learning Machine Learning.
```

The difference:

```text
Episodic → Event / experience
Semantic → Fact / knowledge
```

---

# 25. Procedural Memory

Procedural memory represents **how something should be done**.

Think:

> "How do I perform this task?"

Examples:

```text
How should the agent respond?
How should a workflow be executed?
What steps should be followed?
What tool should be used?
```

For an AI agent:

```text
When user asks for weather:
    call weather tool

When user asks about documents:
    use RAG tool
```

That behavior can be thought of as procedural knowledge.

---

# 26. The Three Types Together

```text
             Long-Term Memory
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   Episodic      Semantic     Procedural
       │            │            │
   What          What          How
   happened?     is known?     to do?
```

Example for a coding assistant:

### Episodic

```text
User previously debugged a Next.js application.
```

### Semantic

```text
User uses TypeScript.
```

### Procedural

```text
When debugging code:
1. identify error
2. inspect stack trace
3. isolate cause
4. propose fix
```

---

# 27. How Long-Term Memory Works — High-Level Architecture

A long-term memory system typically looks like:

```text
                   User
                    │
                    ▼
                 Request
                    │
                    ▼
           ┌─────────────────┐
           │ Memory Retrieval│
           └────────┬────────┘
                    │
                    ▼
             Relevant Memories
                    │
                    ▼
              ┌────────────┐
              │     LLM    │
              └─────┬──────┘
                    │
                    ▼
                 Response
                    │
                    ▼
             Memory Extraction
                    │
                    ▼
              Memory Storage
```

This is extremely important.

---

# 28. Memory Retrieval

Suppose the database contains:

```text
Memory 1:
User prefers Python.

Memory 2:
User is learning React.

Memory 3:
User likes dark themes.

Memory 4:
User is studying regression.
```

User asks:

```text
Explain decorators.
```

A retrieval mechanism might identify:

```text
User prefers Python.
```

Then the prompt becomes:

```text
Relevant memory:
User prefers Python.

Question:
Explain decorators.
```

The LLM can provide a personalized response.

---

# 29. Memory Storage

After a conversation, the system may identify important information.

Example:

```text
User:
I'm building an expense tracker using React.
```

A memory extractor might produce:

```text
{
    "type": "semantic",
    "memory": "User is building an expense tracker using React."
}
```

This can be stored.

---

# 30. Memory Extraction

Not every conversation message should become memory.

Consider:

```text
User:
Hello.

User:
How are you?

User:
What is Python?
```

These aren't necessarily useful long-term memories.

But:

```text
User:
I'm building a production application using FastAPI.
```

could be useful.

Therefore we need a memory extraction process.

Conceptually:

```text
Conversation
     │
     ▼
Memory Extraction
     │
     ├── Important?
     │      │
     │      ├── No → discard
     │      │
     │      └── Yes
     │
     ▼
Store
```

---
