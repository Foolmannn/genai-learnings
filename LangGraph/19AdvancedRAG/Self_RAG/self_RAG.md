 **Self-RAG (Self-Reflective Retrieval-Augmented Generation)** is one of the most important RAG architectures to understand after basic RAG and CRAG. Since you're learning LangGraph, it's especially useful because Self-RAG maps naturally onto **conditional + iterative graph workflows**.

# Self-RAG in Detail

## 1. First: What problem does normal RAG have?

A standard RAG pipeline looks like:

```text
User Query
    ↓
Retriever
    ↓
Relevant Documents
    ↓
LLM
    ↓
Answer
```

For example:

> "What are the symptoms of X?"

The system blindly retrieves documents and gives them to the LLM.

The problem is that **retrieval itself can be wrong or unnecessary**.

For example:

> "What is 2 + 2?"

A normal RAG system might still:

```text
Query
 ↓
Vector DB
 ↓
Retrieve random documents
 ↓
LLM
```

There is no reason to retrieve anything.

More importantly, even if retrieval occurs:

```text
Query
 ↓
Retriever
 ↓
Bad documents
 ↓
LLM
 ↓
Hallucinated answer
```

The LLM doesn't necessarily know that the retrieved context is irrelevant.

This is where **Self-RAG** comes in.

---

# 2. What is Self-RAG?

**Self-RAG = Retrieval-Augmented Generation + Self-Reflection**

Instead of simply:

```text
Retrieve → Generate
```

Self-RAG allows the model to ask itself questions such as:

```text
Should I retrieve?
        ↓
Are these documents relevant?
        ↓
Is my answer supported by the documents?
        ↓
Is my answer useful?
```

Conceptually:

```text
                  ┌──────────────┐
                  │   Question   │
                  └──────┬───────┘
                         ↓
                Should I retrieve?
                    ↙       ↘
                  No         Yes
                  ↓           ↓
              Generate    Retrieve
                              ↓
                       Check relevance
                              ↓
                         Generate
                              ↓
                     Check grounding
                              ↓
                       Check quality
                              ↓
                           Answer
```

The key idea is:

> **The model doesn't blindly trust its own retrieval or generation. It evaluates intermediate results.**

---

# 3. Self-RAG vs Traditional RAG

| Feature               | Traditional RAG | Self-RAG    |
| --------------------- | --------------- | ----------- |
| Retrieval             | Usually always  | Conditional |
| Document evaluation   | Limited         | Yes         |
| Answer evaluation     | Usually none    | Yes         |
| Hallucination control | Moderate        | Better      |
| Iterative retrieval   | Usually no      | Yes         |
| Self-reflection       | No              | Yes         |
| Complexity            | Low             | Higher      |
| Latency               | Lower           | Higher      |
| Cost                  | Lower           | Higher      |

---

# 4. The Core Self-RAG Loop

A practical implementation can be understood as:

```text
                    ┌───────────────┐
                    │ User Question │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │ Need Retrieval?│
                    └───────┬───────┘
                            │
                    ┌───────┴────────┐
                    │                │
                   NO               YES
                    │                │
                    ↓                ↓
                 Generate       Retrieve Docs
                                      ↓
                              Grade Documents
                                      ↓
                             Relevant enough?
                               ↙          ↘
                             NO            YES
                             ↓              ↓
                       Rewrite Query    Generate
                             ↓              ↓
                          Retrieve     Grade Answer
                                            ↓
                                    Supported?
                                      ↙    ↘
                                    NO      YES
                                    ↓        ↓
                                  Retry    Answer
```

This is almost exactly the kind of workflow that **LangGraph** is designed for.

---

# 5. Important Self-RAG Concepts

There are four major decisions we need.

## Decision 1 — Should we retrieve?

Suppose the query is:

> "Explain gradient descent."

Maybe your LLM already knows enough.

But:

> "According to the documents I uploaded, what learning rate was used?"

Definitely retrieve.

So we have:

```python
should_retrieve(query)
```

which produces:

```text
retrieve
```

or

```text
generate
```

---

# 6. Decision 2 — Are retrieved documents relevant?

Suppose we retrieve:

```text
Document 1:
Gradient descent is an optimization algorithm...

Document 2:
React components are reusable UI elements...

Document 3:
Learning rate controls the step size...
```

For:

> "What is learning rate?"

Documents 1 and 3 are relevant.

Document 2 isn't.

Therefore:

```text
Retriever
    ↓
Documents
    ↓
Document Grader
    ↓
Relevant?
```

We can assign:

```text
Document 1 → YES
Document 2 → NO
Document 3 → YES
```

---

# 7. Decision 3 — Is the generated answer grounded?

Suppose our context says:

```text
Gradient descent updates parameters using:

θ = θ - η∇J(θ)
```

The LLM generates:

> "Gradient descent updates parameters using the gradient of the loss."

That's supported.

But if it says:

> "Gradient descent always finds the global minimum."

That's not necessarily supported.

So we need:

```text
Generated Answer
       +
Retrieved Context
       ↓
Grounding / Hallucination Grader
       ↓
Supported?
```

---

# 8. Decision 4 — Is the answer useful?

An answer can be factually supported but still bad.

For example:

> User: "Explain logistic regression to me."

Generated:

> "Logistic regression is a classification algorithm."

Technically correct, but not useful enough.

So Self-RAG can evaluate:

```text
Is the answer:
    ✓ relevant?
    ✓ complete?
    ✓ useful?
```

---

# 9. Self-RAG Architecture

A practical architecture:

```text
                    USER QUERY
                         │
                         ▼
                ┌─────────────────┐
                │ Query Analyzer  │
                └────────┬────────┘
                         │
                  Retrieve needed?
                    /           \
                  No             Yes
                  │               │
                  │               ▼
                  │          ┌──────────┐
                  │          │ Retriever│
                  │          └────┬─────┘
                  │               │
                  │               ▼
                  │        ┌──────────────┐
                  │        │ Doc Grader   │
                  │        └──────┬───────┘
                  │               │
                  │        Relevant?
                  │          /      \
                  │        No        Yes
                  │        │          │
                  │        ▼          │
                  │    Rewrite        │
                  │      Query        │
                  │        │          │
                  │        └──────┐   │
                  │               │   │
                  │               ▼   ▼
                  │            Retrieve
                  │               │
                  └───────────────┤
                                  ▼
                            ┌────────────┐
                            │ Generate   │
                            └─────┬──────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │ Answer Grader│
                          └──────┬───────┘
                                 │
                       ┌─────────┴─────────┐
                       │                   │
                   Supported           Unsupported
                       │                   │
                       ▼                   ▼
                     FINAL             Retry/Regenerate
```

---

# 10. Why LangGraph is perfect for Self-RAG

LangGraph provides:

* Nodes
* Edges
* Conditional edges
* State
* Loops
* Persistence
* Human-in-the-loop
* Streaming

Self-RAG requires exactly these things.

For example:

```python
retrieve
   ↓
grade_documents
   ↓
 ┌───────────────┐
 │               │
relevant       irrelevant
 │               │
 ↓               ↓
generate       rewrite
                 │
                 ↓
              retrieve
```

That's a **cycle**, which is difficult to represent cleanly using a simple sequential chain.

LangGraph makes it natural.

---

# 11. Basic LangGraph Self-RAG Implementation

Let's build one.

We'll use:

```text
LangGraph
LangChain
Vector Store
LLM
Pydantic
```

---

## Step 1 — Install dependencies

For a modern LangChain setup:

```bash
pip install langgraph langchain langchain-openai langchain-community chromadb pydantic
```

---

# 12. Imports

```python
from typing import TypedDict, List

from langgraph.graph import StateGraph, START, END

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field
```

---

# 13. Define the State

The state is extremely important in LangGraph.

```python
class GraphState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
```

Our graph state contains:

```text
question
documents
generation
```

Think of it as the shared memory of the graph.

---

# 14. Create the LLM

```python
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)
```

For Self-RAG, low temperature is generally useful because grading decisions should be relatively deterministic.

---

# 15. Create a Retriever

Suppose you already have:

```python
retriever
```

For example:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)
```

Then:

```python
def retrieve(state: GraphState):

    question = state["question"]

    documents = retriever.invoke(question)

    return {
        "documents": documents
    }
```

---

# 16. Document Relevance Grader

This is one of the most important components.

Instead of asking the LLM:

> "Give me an answer."

we ask:

> "Is this document relevant to the question?"

We can use structured output.

```python
class GradeDocument(BaseModel):

    binary_score: str = Field(
        description="Return 'yes' if the document is relevant, otherwise 'no'"
    )
```

Then:

```python
structured_llm = llm.with_structured_output(
    GradeDocument
)
```

Create a grading prompt:

```python
grader_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a document relevance grader.

        Determine whether the retrieved document contains
        information relevant to the user's question.

        Return:
        yes → relevant
        no → irrelevant
        """
    ),
    (
        "human",
        """
        Question:
        {question}

        Document:
        {document}
        """
    )
])
```

Build the chain:

```python
grader_chain = grader_prompt | structured_llm
```

---

# 17. Grade Documents

```python
def grade_documents(state: GraphState):

    question = state["question"]
    documents = state["documents"]

    filtered_docs = []

    for document in documents:

        result = grader_chain.invoke({
            "question": question,
            "document": document.page_content
        })

        if result.binary_score.lower() == "yes":
            filtered_docs.append(document)

    return {
        "documents": filtered_docs
    }
```

Now:

```text
Retrieved:
    Doc A ✓
    Doc B ✗
    Doc C ✓
    Doc D ✗

After grading:
    Doc A
    Doc C
```

---

# 18. Query Rewriting

Suppose the user asks:

> "What does it say about optimization?"

The retriever may not find good documents.

We can rewrite:

```text
"What does it say about optimization?"
```

into:

```text
"What optimization algorithms are discussed in the document?"
```

Create a rewrite prompt:

```python
rewrite_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a query rewriting expert.

        Rewrite the user's question so that it is
        more suitable for semantic retrieval.

        Preserve the original intent.
        """
    ),
    (
        "human",
        """
        Original question:
        {question}
        """
    )
])
```

Then:

```python
rewrite_chain = rewrite_prompt | llm
```

---

# 19. Rewrite Node

```python
def rewrite_query(state: GraphState):

    question = state["question"]

    response = rewrite_chain.invoke({
        "question": question
    })

    return {
        "question": response.content
    }
```

Now the graph can do:

```text
Poor retrieval
     ↓
Rewrite query
     ↓
Retrieve again
```

This is where Self-RAG becomes **iterative**.

---

# 20. Generation

Now we generate an answer using only relevant documents.

```python
generation_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a helpful question answering assistant.

        Answer the question using ONLY the provided context.

        If the context does not contain enough information,
        say that you don't have enough information.

        Do not invent facts.
        """
    ),
    (
        "human",
        """
        Question:
        {question}

        Context:
        {context}
        """
    )
])
```

Create chain:

```python
generation_chain = generation_prompt | llm
```

---

# 21. Generate Node

```python
def generate(state: GraphState):

    question = state["question"]
    documents = state["documents"]

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    response = generation_chain.invoke({
        "question": question,
        "context": context
    })

    return {
        "generation": response.content
    }
```

---

# 22. Answer Grading

Now comes the most important Self-RAG idea:

> **Don't automatically trust the generated answer.**

We evaluate whether the answer is supported by the retrieved documents.

Define:

```python
class GradeHallucination(BaseModel):

    binary_score: str = Field(
        description="yes if the answer is grounded in the documents, no otherwise"
    )
```

Create structured LLM:

```python
hallucination_llm = llm.with_structured_output(
    GradeHallucination
)
```

Prompt:

```python
hallucination_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a hallucination grader.

        Determine whether the generated answer is supported
        by the provided documents.

        Return:
        yes → fully supported
        no → unsupported or hallucinated
        """
    ),
    (
        "human",
        """
        Documents:
        {documents}

        Answer:
        {generation}
        """
    )
])
```

Chain:

```python
hallucination_chain = (
    hallucination_prompt |
    hallucination_llm
)
```

---

# 23. Grade Generation

```python
def grade_generation(state: GraphState):

    documents = state["documents"]
    generation = state["generation"]

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    result = hallucination_chain.invoke({
        "documents": context,
        "generation": generation
    })

    return result.binary_score
```

Notice something important.

This function doesn't necessarily need to modify state.

It can instead be used to determine the next edge.

---

# 24. Build the LangGraph

Now connect everything.

```python
workflow = StateGraph(GraphState)
```

Add nodes:

```python
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("rewrite_query", rewrite_query)
workflow.add_node("generate", generate)
```

---

# 25. Add Edges

Start:

```python
workflow.add_edge(
    START,
    "retrieve"
)
```

Then:

```text
retrieve
   ↓
grade_documents
```

```python
workflow.add_edge(
    "retrieve",
    "grade_documents"
)
```

---

# 26. Conditional Document Routing

We need to determine whether relevant documents exist.

```python
def decide_to_generate(state: GraphState):

    documents = state["documents"]

    if not documents:
        return "rewrite_query"

    return "generate"
```

Then:

```python
workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "rewrite_query": "rewrite_query",
        "generate": "generate"
    }
)
```

Now:

```text
grade_documents
       │
       ├── relevant → generate
       │
       └── irrelevant → rewrite_query
```

---

# 27. Create the Retrieval Loop

After rewriting:

```python
workflow.add_edge(
    "rewrite_query",
    "retrieve"
)
```

So:

```text
retrieve
   ↓
grade
   ↓
bad
   ↓
rewrite
   ↓
retrieve
```

This creates the loop.

---

# 28. Finish Generation

For the simple version:

```python
workflow.add_edge(
    "generate",
    END
)
```

Compile:

```python
app = workflow.compile()
```

Run:

```python
result = app.invoke({
    "question": "What is gradient descent?",
    "documents": [],
    "generation": ""
})
```

---

# 29. But This Isn't Full Self-RAG Yet

Important distinction.

The graph above has:

```text
Retrieval
↓
Document grading
↓
Query rewriting
↓
Generation
```

That's already a **self-reflective/agentic RAG workflow**, but a stronger Self-RAG architecture also evaluates the generated answer.

We want:

```text
Generate
   ↓
Grounding check
   ↓
Answer quality check
```

---
