# Retrievers in LangChain (Complete Detailed Guide)

Retrievers are one of the **most important concepts** in LangChain, especially in **RAG (Retrieval-Augmented Generation)** applications.

Whenever you build a chatbot that answers questions from documents, PDFs, websites, databases, or vector stores, you will almost always use a **Retriever**.

---

# What is a Retriever?

A **Retriever** is an object that finds the **most relevant documents** for a query.

Instead of searching manually through thousands of documents, a retriever automatically selects the most useful ones.

```
User Question
      │
      ▼
 Retriever
      │
      ▼
Relevant Documents
      │
      ▼
LLM
      │
      ▼
Final Answer
```

Example

Suppose your vector database contains

```
Doc1: LangChain supports RAG.
Doc2: PyTorch is a deep learning framework.
Doc3: CNNs are used for image classification.
Doc4: Transformers use attention mechanisms.
```

User asks

```
What is RAG?
```

Retriever returns

```
Doc1
```

instead of all documents.

The LLM only reads Doc1.

This saves

* tokens
* money
* time

and improves accuracy.

---

# Why not directly query the vector database?

You certainly can.

Example

```python
results = vectorstore.similarity_search(query)
```

But LangChain introduces Retrievers because they provide

* a common interface
* interchangeable retrieval methods
* better chaining with other components

Every retriever has the same method

```python
retriever.invoke(query)
```

instead of

```python
similarity_search()

similarity_search_with_score()

max_marginal_relevance_search()

...
```

So the LLM doesn't care where the documents came from.

---

# Retriever Interface

Every retriever implements

```python
docs = retriever.invoke("What is CNN?")
```

returns

```python
[
    Document(...),
    Document(...),
    ...
]
```

Notice

Retriever **returns Documents**, not text.

Each document contains

```python
Document(
    page_content="...",
    metadata={...}
)
```

---

# Retriever Workflow

```
                 Documents
                     │
                     ▼
             Text Splitter
                     │
                     ▼
              Embedding Model
                     │
                     ▼
               Vector Database
                     │
                     ▼
                 Retriever
                     │
             retrieves documents
                     │
                     ▼
                   LLM
                     │
                     ▼
                 Final Answer
```

---

# Types of Retrievers

LangChain supports many retrieval techniques.

The major ones are

1. Vector Store Retriever
2. Multi Query Retriever
3. Contextual Compression Retriever
4. Parent Document Retriever
5. Multi Vector Retriever
6. Ensemble Retriever
7. Self Query Retriever
8. Time Weighted Retriever
9. BM25 Retriever
10. Merger Retriever
11. Score Threshold Retriever

Let's study each.

---

# 1. Vector Store Retriever

This is the most common retriever.

Workflow

```
Question

↓

Embedding

↓

Vector Store

↓

Top K Documents
```

Example

```python
retriever = vectorstore.as_retriever()
```

or

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k":5}
)
```

Retrieve

```python
docs = retriever.invoke(
    "Explain transformers"
)
```

Internally

```
Question

↓

Embedding

↓

Cosine similarity

↓

Nearest neighbors

↓

Top K
```

Advantages

* simple
* fast
* widely used

Disadvantages

* may miss related information
* relies heavily on embeddings

---

# Search Types

The retriever supports multiple search algorithms.

---

## Similarity Search

Default.

```
Query

↓

Embedding

↓

Nearest vectors

↓

Top K
```

```python
retriever = vectorstore.as_retriever(
    search_type="similarity"
)
```

---

## MMR Search

Maximum Marginal Relevance

Goal

Return

* relevant documents
* less redundant documents

Example

Suppose

```
Doc1 CNN basics
Doc2 CNN layers
Doc3 CNN architecture
Doc4 Transformers
```

Similarity search may return

```
Doc1
Doc2
Doc3
```

All are similar.

MMR returns

```
Doc1
Doc4
Doc2
```

which increases diversity.

```python
retriever = vectorstore.as_retriever(
    search_type="mmr"
)
```

---

## Similarity Score Threshold

Only return documents above a minimum similarity.

```python
retriever = vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold":0.75
    }
)
```

---

# 2. Multi Query Retriever

Problem

A user question may have many meanings.

Example

```
How does CNN work?
```

LLM generates

```
Explain CNN

Convolutional Neural Networks

Image classification using CNN

Deep learning CNN architecture
```

Each query searches separately.

Results merged.

Pipeline

```
Question

↓

LLM

↓

Multiple Queries

↓

Retriever

↓

Merge

↓

LLM
```

Example

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectorstore.as_retriever(),
    llm=llm
)
```

Advantages

* higher recall
* fewer missed documents

Disadvantages

* more LLM calls
* slower

---

# 3. Contextual Compression Retriever

Problem

Retrieved documents are often large.

Example

1000-word document

Only 20 words matter.

Instead of sending

```
1000 words
```

Send

```
20 relevant words
```

Pipeline

```
Retriever

↓

LLM Compressor

↓

Smaller Documents

↓

LLM
```

Example

```python
from langchain.retrievers import ContextualCompressionRetriever
```

Advantages

* saves tokens
* faster inference
* lower cost

---

# 4. Parent Document Retriever

Problem

Small chunks retrieve well.

Large chunks preserve context.

Why not use both?

Idea

Split

```
Large Document

↓

Parent

↓

Small Chunks

↓

Embedding
```

Retriever finds

```
small chunk
```

then returns

```
entire parent document
```

Example

```
Book

↓

Pages

↓

Paragraphs

↓

Embeddings

↓

Retriever

↓

Whole Page
```

Useful for

* books
* research papers
* PDFs

---

# 5. Multi Vector Retriever

A document can have multiple embeddings.

Example

One document

```
Image Caption

Summary

Keywords

Original Text
```

Each gets its own embedding.

Query compares against all embeddings.

Improves retrieval quality.

---

# 6. Ensemble Retriever

Combines multiple retrievers.

Example

```
BM25

+

Vector Search

+

Keyword Search
```

Pipeline

```
Question

↓

Retriever A

Retriever B

Retriever C

↓

Combine Scores

↓

Final Documents
```

Advantages

* more robust
* better accuracy

---

# 7. Self Query Retriever

Very powerful.

The LLM understands

* filters
* metadata
* query

Suppose documents contain

```python
metadata={
    "year":2024,
    "author":"John",
    "topic":"AI"
}
```

User asks

```
Show AI papers after 2023
```

Retriever automatically generates

```
topic="AI"

year>2023
```

Then searches.

Example

```python
SelfQueryRetriever
```

Excellent for

* metadata filtering
* databases
* enterprise search

---

# 8. Time Weighted Retriever

Useful for chatbots.

Recent conversations get higher priority.

Example

```
Yesterday
↓

High weight

One year ago

↓

Low weight
```

Perfect for

* memory
* conversations

---

# 9. BM25 Retriever

Traditional keyword search.

No embeddings.

Example

```
Question

↓

TF-IDF / BM25

↓

Keyword Ranking
```

Advantages

Works better when

```
Error code

Variable names

Exact words

IDs
```

Embedding models sometimes fail here.

---

# 10. Merger Retriever

Runs multiple retrievers.

Simply merges results.

Unlike Ensemble Retriever

* no score fusion
* simple merge

---

# 11. Score Threshold Retriever

Instead of fixed Top-K

```
Top 5
```

It returns

```
all documents

whose score > threshold
```

Example

```
Doc1 0.95

Doc2 0.91

Doc3 0.83

Doc4 0.50
```

Threshold

```
0.80
```

Returns

```
Doc1

Doc2

Doc3
```

---

# Retriever vs Vector Store

| Feature             | Vector Store | Retriever           |
| ------------------- | ------------ | ------------------- |
| Stores embeddings   | ✅            | ❌                   |
| Performs search     | ✅            | ✅ (through backend) |
| Common interface    | ❌            | ✅                   |
| Can combine methods | ❌            | ✅                   |
| Used in chains      | Limited      | Yes                 |
| Returns Documents   | ✅            | ✅                   |

---

# Retriever vs Loader vs Splitter

| Component       | Purpose                      |
| --------------- | ---------------------------- |
| Document Loader | Loads documents              |
| Text Splitter   | Splits documents into chunks |
| Embedding Model | Converts text into vectors   |
| Vector Store    | Stores vectors               |
| Retriever       | Finds relevant documents     |
| LLM             | Generates the answer         |

Pipeline

```
PDF

↓

Loader

↓

Documents

↓

Splitter

↓

Chunks

↓

Embedding

↓

Vector Store

↓

Retriever

↓

LLM
```

---

# Retriever Search Parameters

Most vector store retrievers expose these options through `search_kwargs`:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 5,                  # Number of documents
        "fetch_k": 20,           # Candidates to fetch (used by MMR)
        "lambda_mult": 0.5,      # Diversity vs. relevance (MMR)
        "score_threshold": 0.8   # Minimum similarity score
    }
)
```

* **`k`**: Final number of documents returned.
* **`fetch_k`**: Number of candidate documents retrieved before reranking (primarily for MMR).
* **`lambda_mult`**: Controls the balance between relevance and diversity in MMR. Lower values favor diversity; higher values favor relevance.
* **`score_threshold`**: Filters out documents below the specified similarity score (when using threshold-based search).

---

# Which Retriever Should You Use?

| Retriever                        | Best Use Case                                                     |
| -------------------------------- | ----------------------------------------------------------------- |
| Vector Store Retriever           | General RAG, semantic search                                      |
| Similarity Search                | Fast semantic retrieval                                           |
| MMR Search                       | Diverse results with less redundancy                              |
| Similarity Score Threshold       | Return only highly relevant documents                             |
| Multi Query Retriever            | Improve recall for ambiguous questions                            |
| Contextual Compression Retriever | Reduce token usage before sending to the LLM                      |
| Parent Document Retriever        | Preserve broader context while retrieving fine-grained chunks     |
| Multi Vector Retriever           | Documents represented by summaries, keywords, or multiple views   |
| Ensemble Retriever               | Combine semantic and keyword search for higher accuracy           |
| Self Query Retriever             | Natural language queries with metadata filters                    |
| Time Weighted Retriever          | Conversational memory where recent information matters most       |
| BM25 Retriever                   | Keyword-heavy content such as code, logs, IDs, and error messages |
| Merger Retriever                 | Aggregate results from multiple retrievers without reranking      |

---

# Complete RAG Pipeline with a Retriever

```text
                  Raw Documents
                        │
                        ▼
              Document Loader
                        │
                        ▼
               Text Splitter
                        │
                        ▼
              Embedding Model
                        │
                        ▼
                 Vector Store
                        │
            vectorstore.as_retriever()
                        │
                        ▼
        User Question → Retriever
                        │
            Top Relevant Documents
                        │
                        ▼
                 Prompt Template
                        │
                        ▼
                      LLM
                        │
                        ▼
                 Generated Answer
```

## Key Takeaways

* A **Retriever** is responsible for **finding relevant documents**, not generating answers.
* Most RAG systems convert a vector store into a retriever using `vectorstore.as_retriever()`.
* Retrievers provide a **standard interface** (`invoke()`) regardless of the underlying retrieval strategy.
* Advanced retrievers like **Multi Query**, **Contextual Compression**, **Self Query**, and **Ensemble** can significantly improve answer quality in complex applications.
* Choosing the right retriever depends on your data and use case:

  * Use **Vector Store Retriever** for most semantic search tasks.
  * Add **MMR** when you want diverse results.
  * Use **Self Query Retriever** for metadata-aware searches.
  * Combine approaches with **Ensemble Retriever** for production-grade RAG systems.
  * Use **Contextual Compression Retriever** to reduce token costs while preserving relevant information.

Mastering retrievers is one of the biggest steps toward building effective LangChain RAG applications, since retrieval quality directly influences the quality of the LLM's final answer.
