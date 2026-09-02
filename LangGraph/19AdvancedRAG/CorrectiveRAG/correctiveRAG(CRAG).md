# CRAG — Corrective Retrieval-Augmented Generation

**CRAG (Corrective RAG)** is an advanced form of RAG where the system **doesn't blindly trust the retrieved documents**.

Normal RAG does:

> Query → Retrieve → Generate

CRAG does:

> Query → Retrieve → **Evaluate retrieval quality** → Correct if necessary → Generate

The key idea from the original CRAG paper is to use a retrieval evaluator and trigger different actions depending on whether the retrieved knowledge is **relevant, ambiguous, or incorrect**. It can also supplement the local retrieval with web search and refine retrieved knowledge before generation. ([arXiv][1])

---

# 1. Why do we need CRAG?

Suppose you have a PDF containing information about **LangGraph**.

User asks:

> "What is a checkpointer in LangGraph?"

Your vector database retrieves:

```text
Document 1 → Checkpointing in LangGraph
Document 2 → LangGraph persistence
Document 3 → LangChain memory
Document 4 → Vector databases
```

Normal RAG might simply give all four documents to the LLM:

```text
Question
   ↓
Retriever
   ↓
4 documents
   ↓
LLM
   ↓
Answer
```

The problem is that some retrieved documents may be:

* irrelevant
* partially relevant
* misleading
* outdated
* insufficient to answer the question

The LLM may then generate an answer based on bad context.

CRAG adds a **retrieval evaluation stage**.

```text
                     ┌───────────────┐
                     │   Retriever   │
                     └───────┬───────┘
                             ↓
                       Retrieved Docs
                             ↓
                    ┌─────────────────┐
                    │ Retrieval Grader│
                    └────────┬────────┘
                             ↓
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
          Relevant        Ambiguous      Irrelevant
              ↓              ↓              ↓
          Refine          Search          Rewrite
              ↓              ↓              ↓
              └──────────────┼──────────────┘
                             ↓
                         Generate
```

That conditional behavior is exactly where **LangGraph becomes very useful**. LangGraph allows you to model the RAG pipeline as nodes plus conditional edges and loops. ([LangChain][2])

---

# 2. RAG vs CRAG

## Traditional RAG

```text
User Query
    ↓
Retriever
    ↓
Documents
    ↓
LLM
    ↓
Answer
```

## CRAG

```text
User Query
    ↓
Retriever
    ↓
Retrieved Documents
    ↓
Document Grader
    ↓
   ┌───────────────┐
   │ Is retrieval  │
   │ good enough?  │
   └───────┬───────┘
           │
      ┌────┴────┐
      ↓         ↓
    YES         NO
      ↓         ↓
 Refine       Rewrite
      ↓         ↓
      │      Web Search
      │         ↓
      └────┬────┘
           ↓
        Generate
           ↓
         Answer
```

So the fundamental difference is:

> **RAG assumes retrieval is useful. CRAG verifies retrieval before generation.**

---

# 3. Core components of CRAG

The important components are:

1. Retriever
2. Retrieval evaluator
3. Decision mechanism
4. Knowledge refinement
5. Query rewriting
6. External/web search
7. Generator

Let's understand each.

---

# 4. Retriever

This is the same basic retriever used in normal RAG.

For example:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)
```

User asks:

```text
"What is short-term memory in LangGraph?"
```

Retriever returns:

```python
documents = retriever.invoke(question)
```

Example:

```text
Document 1:
LangGraph uses checkpointers to persist graph state...

Document 2:
Short-term memory allows a conversation to maintain state...

Document 3:
Long-term memory stores information across sessions...

Document 4:
Vector stores are used for semantic search...
```

But we don't immediately send them to the LLM.

---

# 5. Retrieval Grader

This is the most important part of CRAG.

The grader asks:

> "Is this document relevant to the question?"

For example:

```text
Question:
"What is short-term memory in LangGraph?"

Document:
"Long-term memory stores information across sessions."
```

The grader should return:

```text
NO
```

Whereas:

```text
Document:
"Short-term memory allows a LangGraph thread to maintain state..."
```

should return:

```text
YES
```

LangChain's CRAG example uses this relevance-grading idea before deciding whether to generate directly or perform additional retrieval. ([LangChain][3])

---

# 6. Why use structured output for the grader?

You don't want this:

```text
I think the document is probably relevant because...
```

You want deterministic output such as:

```python
{
    "relevant": "yes"
}
```

So we can define:

```python
from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):
    binary_score: str = Field(
        description="Is the document relevant to the question? yes or no"
    )
```

Then:

```python
grader = llm.with_structured_output(GradeDocuments)
```

Now:

```python
result = grader.invoke(...)
```

might produce:

```python
GradeDocuments(binary_score="yes")
```

This is particularly useful for LangGraph conditional routing.

---

# 7. CRAG's decision logic

After grading documents, we need to decide what to do.

A simplified version:

```text
             Retrieved docs
                    ↓
             Grade documents
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
Relevant docs             No useful docs
        ↓                       ↓
 Knowledge refinement      Rewrite query
        ↓                       ↓
     Generate              Web search
                                ↓
                             Generate
```

The original CRAG approach is somewhat richer: the evaluator can distinguish retrieval quality and trigger different retrieval actions, while knowledge refinement filters information into useful pieces. ([arXiv][1])

---

# 8. Knowledge refinement

This is an important CRAG concept.

Suppose the retriever returns:

```text
Document:

LangGraph is a framework for building stateful agents.

It supports persistence.

Checkpointers save graph state.

LangGraph can use PostgreSQL.

LangChain provides many integrations.

Vector databases are used for semantic retrieval.

LangGraph supports human-in-the-loop workflows.
```

The question is:

> "What is a checkpointer?"

We don't need the entire document.

We only need:

```text
Checkpointers save graph state.
```

CRAG's original formulation calls this **knowledge refinement** and describes breaking retrieved documents into smaller "knowledge strips", evaluating them, and filtering irrelevant pieces. ([blog.langchain.dev][4])

Conceptually:

```text
Document
   ↓
Split into knowledge strips
   ↓
┌──────────────┐
│ Strip 1      │ → relevant
│ Strip 2      │ → irrelevant
│ Strip 3      │ → relevant
│ Strip 4      │ → irrelevant
└──────────────┘
   ↓
Relevant strips
   ↓
Generator
```

This can reduce noise significantly.

---

# 9. What happens when retrieval fails?

Suppose your knowledge base contains only:

```text
LangGraph documentation
LangChain documentation
```

User asks:

> "Who won the 2026 FIFA World Cup?"

Your vector database might return something because semantic search always returns its top `k` documents.

But those documents aren't actually useful.

A normal RAG system might answer incorrectly.

CRAG says:

```text
Retrieved documents
       ↓
     Grader
       ↓
   irrelevant
       ↓
Rewrite query
       ↓
External search
       ↓
Useful information
       ↓
Generate
```

This is one of CRAG's major advantages.

---
