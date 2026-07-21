# Retrieval-Augmented Generation (RAG) in Detail with LangChain

RAG (Retrieval-Augmented Generation) is one of the most important concepts in LLM applications. Instead of expecting an LLM to memorize everything, RAG **retrieves relevant information from external knowledge sources and provides it to the LLM before it generates an answer.**

Think of it as an **open-book exam**.

* **Without RAG:** LLM answers from its internal knowledge.
* **With RAG:** LLM first searches your documents, then answers using them.

---

# Why RAG?

Large Language Models have limitations.

## 1. Hallucinations

The model may confidently generate incorrect information.

Example:

**Question**

> What is the leave policy of my company?

The LLM doesn't know your company's HR policy.

Without RAG:

> Employees receive 20 paid leaves.

It simply invented the answer.

With RAG:

The system searches your HR PDF.

Returns:

> Employees are entitled to 12 annual paid leaves.

LLM answers based on that document.

---

## 2. Private Data

LLMs cannot know

* Company documents
* Medical records
* Research papers
* Internal manuals
* PDFs
* Word documents
* Notes

RAG allows the model to answer using these documents.

---

## 3. Up-to-date Information

Training data becomes outdated.

Example

Today's stock price

Latest news

Company policies

Legal documents

can all change.

Instead of retraining an LLM, simply update the database.

---

# Basic Architecture

```
            User Question
                   │
                   ▼
         Retrieval System
                   │
        Search Relevant Docs
                   │
                   ▼
        Retrieved Documents
                   │
                   ▼
        Prompt + User Question
                   │
                   ▼
               LLM
                   │
                   ▼
               Final Answer
```

---

# Traditional LLM

```
Question
    │
    ▼
   LLM
    │
    ▼
Answer
```

Knowledge is fixed.

---

# RAG

```
Question
      │
      ▼
Retriever
      │
      ▼
Relevant Chunks
      │
      ▼
Prompt + Context
      │
      ▼
LLM
      │
      ▼
Answer
```

---

# Components of RAG

There are **six major components**.

```
Documents
      │
Loader
      │
Splitter
      │
Embeddings
      │
Vector Database
      │
Retriever
      │
LLM
```

Let's study each.

---

# Step 1 Document Loading

Suppose we have

```
HR.pdf
```

or

```
company.txt
```

or

```
website
```

These are raw data.

LangChain loads them.

Example

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("company.pdf")

docs = loader.load()
```

Output

```
[
Document(...),
Document(...),
Document(...)
]
```

Each page becomes a Document object.

---

# Document Object

A document contains

```
Document
│
├── page_content
└── metadata
```

Example

```python
docs[0]
```

Output

```python
Document(
    page_content="Company leave policy...",
    metadata={"page":0}
)
```

---

# Step 2 Text Splitting

LLMs cannot process huge documents efficiently.

Instead,

split into chunks.

Example

Original

```
100 Pages
```

↓

```
Chunk 1

Chunk 2

Chunk 3

...

Chunk 500
```

---

Why?

Because embeddings work better on smaller text.

---

Example

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)
```

---

Meaning

```
chunk_size=500
```

Maximum characters.

```
chunk_overlap=50
```

Previous chunk shares 50 characters.

Example

Chunk1

```
ABCDEF
```

Chunk2

```
EFGHIJ
```

Overlap

```
EF
```

This preserves context.

---

# Step 3 Embeddings

Now every chunk must become numbers.

Why?

Computers compare vectors, not sentences.

Example

Sentence

```
Cats drink milk
```

↓

```
[0.12,
0.45,
0.91,
...
]
```

These are embeddings.

---

Embedding Model

Popular ones

* OpenAI
* Hugging Face
* BAAI/bge
* Nomic
* Sentence Transformers
* Google
* Cohere

Example

```python
from langchain_openai import OpenAIEmbeddings

embedding = OpenAIEmbeddings()
```

Generate vectors

```python
vectors = embedding.embed_documents(
    [chunk.page_content for chunk in chunks]
)
```

---

# What Embeddings Capture

Embeddings represent **semantic meaning**, not exact words.

Example

Sentence A

```
My car is broken.
```

Sentence B

```
My automobile needs repair.
```

Different words.

Similar meaning.

Embedding vectors are close together.

---

# Step 4 Vector Database

Now store embeddings.

Instead of SQL,

we use

Vector DB.

Popular databases

* Chroma
* FAISS
* Pinecone
* Weaviate
* Milvus
* Qdrant

---

Example

```python
from langchain_chroma import Chroma

vectorstore = Chroma.from_documents(
    chunks,
    embedding
)
```

Now every chunk is stored.

```
Chunk

↓

Embedding

↓

Vector Database
```

---

# Step 5 Retrieval

User asks

```
How many paid leaves?
```

Question is embedded.

↓

Compared against stored embeddings.

↓

Most similar chunks returned.

```
Question Vector

↓

Similarity Search

↓

Top K Chunks
```

---

Example

```python
retriever = vectorstore.as_retriever()

docs = retriever.invoke(
    "What is leave policy?"
)
```

---

Result

```
Document 1

Document 2

Document 3
```

---

# Similarity Search

Usually uses

Cosine Similarity

```
Question Vector

↓

Compare

↓

Chunk 1

Chunk 2

Chunk 3

↓

Highest similarity wins
```

---

# Step 6 Prompt

Retrieved documents become context.

Prompt

```
Context:

Document1...

Document2...

Question:

How many leaves?

Answer only using context.
```

---

# Step 7 LLM

LLM receives

```
Question

+

Retrieved Context
```

Now answer becomes grounded.

---

# Complete RAG Pipeline

```
PDF
 │
 ▼
Loader
 │
 ▼
Documents
 │
 ▼
Splitter
 │
 ▼
Chunks
 │
 ▼
Embeddings
 │
 ▼
Vector DB
 │
 ▼
Retriever
 │
 ▼
Relevant Chunks
 │
 ▼
Prompt
 │
 ▼
LLM
 │
 ▼
Answer
```

---

# LangChain Implementation

## Step 1 Load PDF

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("book.pdf")
docs = loader.load()
```

---

## Step 2 Split

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(docs)
```

---

## Step 3 Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embedding = OpenAIEmbeddings()
```

---

## Step 4 Vector Store

```python
from langchain_chroma import Chroma

db = Chroma.from_documents(
    chunks,
    embedding
)
```

---

## Step 5 Retriever

```python
retriever = db.as_retriever(
    search_kwargs={"k": 3}
)
```

This retrieves the top **3** most similar chunks.

---

## Step 6 LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4.1-mini")
```

---

## Step 7 Prompt Template

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
Answer the question using only the context below.

Context:
{context}

Question:
{question}
""")
```

---

## Step 8 Create the Chain

A modern LangChain pipeline uses LCEL (LangChain Expression Language):

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

Invoke it:

```python
response = chain.invoke("What is the leave policy?")
print(response)
```

---

# Types of Retrieval

### 1. Similarity Search

Returns the closest chunks by vector similarity.

```python
retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)
```

---

### 2. Maximum Marginal Relevance (MMR)

Balances **relevance** and **diversity**, reducing duplicate chunks.

```python
retriever = db.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 20}
)
```

* `fetch_k`: candidates to consider.
* `k`: final chunks returned.

---

### 3. Similarity Score Threshold

Only returns chunks above a minimum similarity score.

```python
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.8,
        "k": 5
    }
)
```

---

# Advanced RAG Techniques

As your document collection grows, you can improve retrieval quality:

* **Metadata filtering:** Search only documents with matching metadata (e.g., `department="HR"`).
* **Hybrid search:** Combine keyword search (BM25) with vector search.
* **Multi-query retrieval:** Generate multiple versions of the user's question.
* **Contextual compression:** Retrieve more chunks, then compress them before sending to the LLM.
* **Reranking:** Use a cross-encoder model to reorder retrieved chunks for higher relevance.
* **Parent-document retrieval:** Retrieve a small chunk but return the larger parent section for better context.
* **Self-RAG / Agentic RAG:** Let the model decide whether to retrieve more information, refine the query, or answer directly.

---

# Common Problems in RAG

| Problem                  | Cause                    | Solution                            |
| ------------------------ | ------------------------ | ----------------------------------- |
| Wrong answer             | Poor retrieval           | Better embeddings or reranking      |
| Missing context          | Chunk too small          | Increase `chunk_size`               |
| Too much irrelevant text | Chunk too large          | Reduce `chunk_size`                 |
| Broken sentences         | No overlap               | Increase `chunk_overlap`            |
| Slow retrieval           | Large vector database    | Use ANN indexes (FAISS, HNSW, etc.) |
| Duplicate information    | Similar chunks retrieved | Use MMR or deduplicate results      |

---

# Choosing Chunk Size

There is no universal best value.

| Use case        | Recommended chunk size                            |
| --------------- | ------------------------------------------------- |
| FAQs            | 200–400 characters/tokens (depending on splitter) |
| PDFs            | 500–1000                                          |
| Research papers | 800–1500                                          |
| Code            | Split by functions/classes rather than fixed size |
| Books           | 1000–2000                                         |

A good starting point is:

```python
RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)
```

Then evaluate retrieval quality and adjust.

---

# Modern LangChain RAG Ecosystem

Typical packages you'll use are:

```text
langchain
langchain-core
langchain-community
langchain-text-splitters
langchain-openai      # or langchain-google-genai, langchain-cohere, etc.
langchain-chroma      # or FAISS, Pinecone, Qdrant integrations
chromadb              # if using Chroma
```

---

# Complete Flow Diagram

```text
                  ┌──────────────┐
                  │ PDF / DOCX / │
                  │ Website / DB │
                  └──────┬───────┘
                         │
                         ▼
                Document Loader
                         │
                         ▼
                  LangChain Documents
                         │
                         ▼
              Text Splitter (Chunks)
                         │
                         ▼
                 Embedding Model
                         │
                         ▼
                 Vector Database
                         │
                  (Offline indexing)
────────────────────────────────────────────────────
                         │
                  User Question
                         │
                         ▼
          Embed Question + Retrieve Top-k
                         │
                         ▼
                Relevant Document Chunks
                         │
                         ▼
                  Prompt Template
                         │
                         ▼
                    Chat Model (LLM)
                         │
                         ▼
                    Final Answer
```

## Learning Path

Since you've already studied **document loaders**, **text splitters**, and **vector stores**, the next topics to master are:

1. Embedding models (how they work and how to choose one).
2. Vector databases in depth (FAISS, Chroma, Pinecone, Qdrant).
3. Retriever types (similarity, MMR, score threshold, metadata filtering).
4. LCEL (LangChain Expression Language) for composing RAG pipelines.
5. Advanced RAG patterns (reranking, contextual compression, parent-document retrieval, hybrid search, and agentic RAG).

Once you're comfortable with these, you'll be able to build production-quality chatbots that answer questions over PDFs, websites, databases, or any custom knowledge base.
