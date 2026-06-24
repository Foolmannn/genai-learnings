# Vector Stores in Detail and Using Them with LangChain

Vector stores are one of the most important concepts in modern AI applications, especially **RAG (Retrieval-Augmented Generation)** systems.

---

# 1. What is a Vector Store?

A vector store is a database designed to store and search **embeddings**.

### Traditional Database

```text
ID | Text
--------------------
1  | LangChain is a framework
2  | PyTorch is a deep learning library
```

Search:

```sql
SELECT * FROM docs
WHERE text LIKE '%LangChain%'
```

This only finds exact keywords.

---

### Vector Database

Text is converted into vectors:

```text
"LangChain is a framework"

↓ Embedding Model

[0.23, -0.51, 0.12, 0.88, ...]
```

Stored as:

```text
ID | Vector
--------------------
1  | [0.23,-0.51,...]
2  | [0.11,0.42,...]
```

Now searches are based on **meaning**, not exact words.

Example:

Query:

```text
Framework for LLM applications
```

Even if "LangChain" isn't mentioned, the vector similarity search will find:

```text
LangChain is a framework...
```

because both embeddings are semantically close.

---

# 2. Why Do We Need Vector Stores?

Suppose you have:

* PDFs
* Books
* Research papers
* Company documents
* Websites

An LLM cannot remember all this data in its context window.

Instead:

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Store
    ↓
Similarity Search
    ↓
Relevant Chunks
    ↓
LLM
```

This is the foundation of RAG.

---

# 3. Embeddings

Embeddings are numerical representations of text.

Example:

```text
Cat
```

might become:

```python
[0.12, 0.44, -0.31, ...]
```

and

```text
Kitten
```

might become:

```python
[0.11, 0.46, -0.29, ...]
```

Their vectors are close together.

---

# 4. Similarity Search

Most vector stores use:

### Cosine Similarity

```text
Similarity = cos(θ)
```

Range:

```text
1   -> Identical
0   -> Unrelated
-1  -> Opposite
```

Example:

```text
Query:
"Neural networks"

Document A:
"Deep learning"

Similarity = 0.92

Document B:
"Cooking recipe"

Similarity = 0.08
```

Document A is returned.

---

# 5. Vector Store Workflow

## Step 1: Load Documents

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("book.pdf")
docs = loader.load()
```

---

## Step 2: Split Documents

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(docs)
```

Example:

```text
Chapter 1...
```

↓

```text
Chunk 1
Chunk 2
Chunk 3
```

---

## Step 3: Generate Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
```

or

```python
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

---

## Step 4: Store in Vector Database

```python
vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)
```

---

## Step 5: Search

```python
results = vectorstore.similarity_search(
    "What is LangChain?"
)

print(results[0].page_content)
```

---

# 6. Popular Vector Stores in LangChain

| Vector Store | Persistent | Local | Cloud |
| ------------ | ---------- | ----- | ----- |
| FAISS        | No         | Yes   | No    |
| Chroma       | Yes        | Yes   | No    |
| Pinecone     | Yes        | No    | Yes   |
| Weaviate     | Yes        | Both  | Yes   |
| Qdrant       | Yes        | Both  | Yes   |
| Milvus       | Yes        | Both  | Yes   |

---

# 7. FAISS

Most commonly used for learning.

Created by Meta.

Install:

```bash
pip install faiss-cpu
```

Create:

```python
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(
    chunks,
    embeddings
)
```

Search:

```python
docs = vectorstore.similarity_search(
    "What is machine learning?",
    k=3
)
```

---

## Save FAISS

```python
vectorstore.save_local("faiss_db")
```

Load:

```python
db = FAISS.load_local(
    "faiss_db",
    embeddings,
    allow_dangerous_deserialization=True
)
```

---

# 8. Chroma

Most popular local persistent vector database.

Install:

```bash
pip install chromadb
```

Create:

```python
from langchain_chroma import Chroma

vectorstore = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="./chroma_db"
)
```

Search:

```python
results = vectorstore.similarity_search(
    "Explain transformers"
)
```

Data remains on disk.

---

# 9. Pinecone

Cloud-based vector database.

Install:

```bash
pip install pinecone langchain-pinecone
```

Advantages:

* Managed service
* Scalable
* Production ready
* Millions of vectors

Used for:

* Chatbots
* Enterprise search
* RAG systems

---

# 10. Qdrant

Very popular open-source vector database.

Install:

```bash
pip install qdrant-client
```

Features:

* Metadata filtering
* Hybrid search
* Fast retrieval
* Production deployment

---

# 11. Metadata

You can store extra information with vectors.

Example:

```python
Document(
    page_content="LangChain tutorial",
    metadata={
        "source": "youtube",
        "author": "John",
        "year": 2025
    }
)
```

Stored as:

```text
Vector
Text
Metadata
```

---

## Metadata Filtering

Search only PDFs:

```python
vectorstore.similarity_search(
    "LangChain",
    filter={"source":"pdf"}
)
```

Useful for:

* Multiple document collections
* Multi-user systems
* Department-specific search

---

# 12. Retriever

LangChain typically converts vector stores into retrievers.

```python
retriever = vectorstore.as_retriever()
```

Search:

```python
docs = retriever.invoke(
    "What is LangChain?"
)
```

---

## Configure Retriever

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k":5}
)
```

Returns top 5 chunks.

---

# 13. Similarity Search vs Retriever

### Similarity Search

```python
vectorstore.similarity_search(query)
```

Returns documents directly.

---

### Retriever

```python
retriever.invoke(query)
```

Standard interface.

Works with:

* Chains
* Agents
* RAG pipelines

Most LangChain components expect retrievers.

---

# 14. Using Vector Store in a RAG Pipeline

```python
User Question
      ↓
Retriever
      ↓
Relevant Chunks
      ↓
Prompt
      ↓
LLM
      ↓
Answer
```

Code:

```python
retriever = vectorstore.as_retriever()

docs = retriever.invoke(
    "Explain attention mechanism"
)

context = "\n".join(
    doc.page_content
    for doc in docs
)

prompt = f"""
Answer using context:

{context}

Question:
Explain attention mechanism
"""
```

Send this prompt to the LLM.

---

# 15. Modern LangChain RAG Example

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

vectorstore = Chroma(
    persist_directory="./db",
    embedding_function=OpenAIEmbeddings()
)

retriever = vectorstore.as_retriever()

llm = ChatOpenAI()

docs = retriever.invoke(
    "What is LangChain?"
)

context = "\n".join(
    d.page_content for d in docs
)

response = llm.invoke(
    f"""
    Context:
    {context}

    Question:
    What is LangChain?
    """
)

print(response.content)
```

---

# 16. Advanced Retrieval Methods

### Similarity Search

```python
retriever = db.as_retriever(
    search_type="similarity"
)
```

---

### MMR (Maximum Marginal Relevance)

Avoids duplicate chunks.

```python
retriever = db.as_retriever(
    search_type="mmr"
)
```

Example:

Instead of:

```text
Chunk 1 - LangChain
Chunk 2 - LangChain
Chunk 3 - LangChain
```

You get:

```text
Chunk 1 - LangChain
Chunk 2 - Embeddings
Chunk 3 - Vector Stores
```

More diversity.

---

### Similarity Score Threshold

```python
retriever = db.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold":0.8}
)
```

Returns only highly relevant chunks.

---

# 17. LangChain Packages You Should Know

For modern LangChain development:

```bash
pip install langchain
pip install langchain-community
pip install langchain-text-splitters
pip install langchain-openai
pip install langchain-huggingface

# Vector stores
pip install chromadb
pip install faiss-cpu

# Optional
pip install qdrant-client
pip install pinecone
```

---

# Interview/Exam Definition

**Vector Store:** A specialized database that stores vector embeddings of data and performs similarity search to retrieve semantically relevant information. It is a core component of RAG systems, enabling efficient retrieval of relevant document chunks for LLMs.

**Retriever:** A LangChain abstraction that queries a vector store and returns the most relevant documents based on semantic similarity.

For your LangChain learning path, the sequence should be:

```text
Document Loaders
        ↓
Text Splitters
        ↓
Embeddings
        ↓
Vector Stores
        ↓
Retrievers
        ↓
RAG
        ↓
Agents
```

Mastering those six topics will cover roughly 80–90% of practical LangChain applications.
