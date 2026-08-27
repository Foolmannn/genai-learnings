# RAG System with LangGraph

A **RAG (Retrieval-Augmented Generation)** system with **LangGraph** combines two ideas:

* **RAG** → gives an LLM relevant information from your own documents/data.
* **LangGraph** → manages the RAG process as a **stateful workflow/graph**, allowing you to add routing, validation, retries, query rewriting, tools, memory, and other logic.

A typical architecture looks like:

```text
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Retrieve Docs   │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Grade Documents │
                    └────────┬────────┘
                             ↓
                  ┌──────────┴──────────┐
                  │                     │
             Relevant?              Not Relevant
                  │                     │
                  ↓                     ↓
          ┌──────────────┐       ┌──────────────┐
          │ Generate     │       │ Rewrite Query│
          │ Answer       │       └──────┬───────┘
          └──────┬───────┘              │
                 ↓                      │
          ┌──────────────┐              │
          │ Check Answer │←─────────────┘
          └──────┬───────┘
                 ↓
              Response
```

This is much more powerful than a simple:

```text
Question → Retriever → LLM → Answer
```

---

# 1. What is RAG?

Suppose you have a collection of PDFs containing your university course materials.

The user asks:

> "What are the objectives of the NET Centric Computing course?"

A normal LLM may not know your particular course document.

RAG solves this by retrieving relevant content first:

```text
User Question
      ↓
Search your documents
      ↓
Relevant document chunks
      ↓
LLM + retrieved context
      ↓
Answer
```

The LLM isn't expected to memorize your documents.

Instead, you provide the relevant information at inference time.

---

# 2. Traditional RAG Architecture

A standard RAG system has two major phases.

## Phase 1: Indexing

This happens before users ask questions.

```text
Documents
   ↓
Document Loader
   ↓
Text Splitter
   ↓
Chunks
   ↓
Embeddings
   ↓
Vector Database
```

For example:

```text
course.pdf
   ↓
20 pages
   ↓
500 chunks
   ↓
Embedding model
   ↓
Chroma / FAISS / Pinecone / PGVector
```

---

# 3. Retrieval Phase

When the user asks:

> "What is MVC?"

The system converts the query into an embedding:

```text
"What is MVC?"
      ↓
Embedding
      ↓
Vector similarity search
      ↓
Top K relevant chunks
```

For example:

```text
Chunk 1 → MVC architecture
Chunk 2 → Controllers
Chunk 3 → Views
Chunk 4 → Models
```

These are passed to the LLM.

---

# 4. Where LangGraph Comes In

A basic RAG chain is usually linear:

```text
retrieve → generate
```

But real-world RAG often needs decisions.

For example:

```text
retrieve
   ↓
Are retrieved documents relevant?
   ↓
   ├── YES → generate answer
   │
   └── NO  → rewrite query
                 ↓
              retrieve again
```

This is where LangGraph becomes extremely useful.

You can represent each operation as a **node** and decisions as **conditional edges**.

---

# 5. LangGraph Mental Model

Think of a LangGraph RAG system as a workflow.

```text
                 Graph
                  │
       ┌──────────┴──────────┐
       ↓                     ↓
     Node                  Node
   Retrieve               Generate
       │                     │
       └──────→ Decision ←───┘
```

The important concepts are:

### State

Contains information being passed through the graph.

```python
class RAGState(TypedDict):
    question: str
    documents: list
    answer: str
```

### Nodes

Functions that perform work.

```python
def retrieve(state):
    ...
```

```python
def generate(state):
    ...
```

### Edges

Determine what happens next.

```text
retrieve → generate
```

### Conditional edges

Allow the graph to make decisions.

```text
retrieve
   ↓
grade_documents
   ↓
 ┌─┴─┐
 ↓   ↓
yes  no
 ↓   ↓
gen rewrite
```

---

# 6. Complete RAG + LangGraph Architecture

A more production-oriented system could look like this:

```text
                        USER
                         │
                         ↓
                  ┌──────────────┐
                  │ Analyze Query│
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Retrieve     │
                  │ Documents    │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │ Grade Docs   │
                  └──────┬───────┘
                         ↓
                  ┌──────┴───────┐
                  │ Relevant?    │
                  └──────┬───────┘
                    YES  │  NO
                     ↓   │   ↓
                Generate  │ Rewrite
                     ↓   │   │
                ┌─────────┘   │
                │             ↓
                │          Retrieve
                │             │
                └──────→──────┘
                         ↓
                  ┌──────────────┐
                  │ Grade Answer │
                  └──────┬───────┘
                         ↓
                     Response
```

This pattern is often called **Corrective/Adaptive RAG**, depending on the exact implementation.

---

# 7. Installing the Required Packages

A modern Python environment could use:

```bash
pip install langgraph langchain langchain-openai langchain-community
```

For a local vector store such as Chroma:

```bash
pip install chromadb
```

For environment variables:

```bash
pip install python-dotenv
```

---

# 8. Building the RAG System

Let's build a simplified system.

## Step 1 — Load Documents

For example, using text files:

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("data.txt")

documents = loader.load()
```

For PDFs, you can use an appropriate PDF loader.

---

# 9. Split Documents

Large documents should be divided into smaller chunks.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)
```

Why?

Instead of retrieving an entire 100-page document:

```text
100 pages → LLM
```

you retrieve only relevant sections:

```text
100 pages
   ↓
500 chunks
   ↓
Top 5 relevant chunks
   ↓
LLM
```

---

# 10. Create Embeddings

For example:

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
```

Embeddings convert text into vectors.

Conceptually:

```text
"What is MVC?"
        ↓
[0.021, -0.183, 0.442, ...]
```

Similar meanings produce vectors that are close in vector space.

---

# 11. Create a Vector Store

For example, Chroma:

```python
from langchain_chroma import Chroma

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings
)
```

Then create a retriever:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)
```

---

# 12. Define the LangGraph State

This is one of the most important parts.

```python
from typing import TypedDict
from langchain_core.documents import Document


class RAGState(TypedDict):
    question: str
    documents: list[Document]
    answer: str
```

The state moves through the graph.

Initially:

```python
{
    "question": "What is MVC?",
    "documents": [],
    "answer": ""
}
```

After retrieval:

```python
{
    "question": "What is MVC?",
    "documents": [
        Document(...),
        Document(...),
        Document(...)
    ],
    "answer": ""
}
```

After generation:

```python
{
    "question": "What is MVC?",
    "documents": [...],
    "answer": "MVC stands for..."
}
```

---

# 13. Retrieval Node

Create a node that searches the vector database.

```python
def retrieve(state: RAGState):

    question = state["question"]

    documents = retriever.invoke(question)

    return {
        "documents": documents
    }
```

This node:

```text
State
 ↓
question
 ↓
retriever
 ↓
documents
 ↓
State
```

---

# 14. Generation Node

Now create the LLM.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)
```

Create a prompt:

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant.

Answer the question using only the provided context.

If the answer cannot be found in the context,
say that you don't know.

Context:
{context}

Question:
{question}
""")
```

Then:

```python
def generate(state: RAGState):

    question = state["question"]
    documents = state["documents"]

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    messages = prompt.invoke({
        "context": context,
        "question": question
    })

    response = llm.invoke(messages)

    return {
        "answer": response.content
    }
```

---

# 15. Building the Graph

Now we connect the nodes.

```python
from langgraph.graph import StateGraph, START, END

graph_builder = StateGraph(RAGState)

graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generate", generate)

graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", END)

graph = graph_builder.compile()
```

Now the graph is:

```text
START
  ↓
retrieve
  ↓
generate
  ↓
 END
```

---

# 16. Running the Graph

```python
result = graph.invoke({
    "question": "What is MVC?",
    "documents": [],
    "answer": ""
})
```

Then:

```python
print(result["answer"])
```

The execution becomes:

```text
graph.invoke()
      ↓
retrieve()
      ↓
vector database
      ↓
documents
      ↓
generate()
      ↓
LLM
      ↓
answer
```

---

# 17. Why This Isn't Yet a Very Good RAG System

The previous example assumes retrieval always works.

But imagine:

```text
Question:
"What is the history of Microsoft?"
```

Your vector database contains only:

```text
ASP.NET documentation
C# documentation
MVC documentation
```

The retriever may still return something.

The LLM might then try to answer using irrelevant documents.

This is known as a **retrieval quality problem**.

LangGraph lets us introduce a document grading step.

---

# 18. Document Grading

We can ask an LLM:

> Is this retrieved document relevant to the question?

For example:

```text
Question:
"What is MVC?"

Document:
"MVC separates an application into Model,
View and Controller."

Result:
YES
```

But:

```text
Question:
"What is MVC?"

Document:
"Python lists are mutable collections."

Result:
NO
```

---

# 19. Structured Output for Grading

You can define:

```python
from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):

    binary_score: str = Field(
        description="yes or no"
    )
```

Then:

```python
grader = llm.with_structured_output(
    GradeDocuments
)
```

The grader prompt:

```python
grade_prompt = ChatPromptTemplate.from_template("""
You are grading whether a document is relevant
to a user question.

Question:
{question}

Document:
{document}

Return "yes" if the document is relevant.
Return "no" otherwise.
""")
```

---

# 20. Grade Documents Node

```python
def grade_documents(state: RAGState):

    question = state["question"]
    documents = state["documents"]

    filtered_documents = []

    for document in documents:

        response = grader.invoke(
            grade_prompt.invoke({
                "question": question,
                "document": document.page_content
            })
        )

        if response.binary_score.lower() == "yes":
            filtered_documents.append(document)

    return {
        "documents": filtered_documents
    }
```

Now the graph becomes:

```text
START
  ↓
retrieve
  ↓
grade_documents
  ↓
generate
  ↓
END
```

---
