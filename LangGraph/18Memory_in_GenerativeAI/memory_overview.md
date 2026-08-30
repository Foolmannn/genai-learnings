
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
