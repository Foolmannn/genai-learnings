# Semantic Splitting (Semantic Chunking) in Detail

Semantic splitting is an advanced chunking technique where text is divided based on **meaning** rather than fixed character counts, tokens, or paragraphs.

The main idea is:

> "Keep semantically related information together, even if the chunk sizes are uneven."

---

# Why Traditional Chunking Fails

Suppose we have a document:

```text
Machine Learning is a subset of AI.

Neural Networks are inspired by the human brain.

Deep Learning uses multiple neural network layers.

The weather in Kathmandu is pleasant today.

Tourists often visit Pashupatinath Temple.
```

## Recursive Character Splitter Output

```text
Chunk 1:
Machine Learning is a subset of AI.
Neural Networks are inspired by the human brain.

Chunk 2:
Deep Learning uses multiple neural network layers.
The weather in Kathmandu is pleasant today.

Chunk 3:
Tourists often visit Pashupatinath Temple.
```

Notice the problem:

```text
Deep Learning
Weather
```

are completely unrelated topics.

This creates poor retrieval.

---

# Semantic Splitting Solution

A semantic splitter identifies topic changes.

Output:

```text
Chunk 1:
Machine Learning is a subset of AI.
Neural Networks are inspired by the human brain.
Deep Learning uses multiple neural network layers.

Chunk 2:
The weather in Kathmandu is pleasant today.
Tourists often visit Pashupatinath Temple.
```

Now each chunk contains one coherent idea.

---

# How Semantic Chunking Works

## Step 1: Break into Sentences

Input:

```text
Sentence 1
Sentence 2
Sentence 3
Sentence 4
Sentence 5
```

↓

```python
[
  s1,
  s2,
  s3,
  s4,
  s5
]
```

---

## Step 2: Create Embeddings

Each sentence is converted into a vector.

```python
Embedding(s1)
Embedding(s2)
Embedding(s3)
Embedding(s4)
Embedding(s5)
```

Example:

```text
s1 → [0.12, 0.44, ...]
s2 → [0.11, 0.47, ...]
s3 → [0.13, 0.45, ...]
```

The embedding captures semantic meaning.

---

## Step 3: Calculate Similarity

Usually cosine similarity.

```text
Similarity(s1,s2) = 0.92
Similarity(s2,s3) = 0.89
Similarity(s3,s4) = 0.21
Similarity(s4,s5) = 0.87
```

Notice:

```text
s3 → s4
```

has a large drop.

That indicates a topic change.

---

## Step 4: Create Boundaries

```text
s1
s2
s3
--------
s4
s5
```

Chunk boundary inserted where similarity drops significantly.

---

# Visual Representation

```text
Sentence Embeddings

S1 -----
         \
S2 ------- High Similarity
           \
S3 ---------

S4 ---------------- New Topic

S5 ---------------- Similar Topic
```

↓

```text
Chunk A = S1+S2+S3
Chunk B = S4+S5
```

---

# Why Semantic Chunking Improves RAG

Imagine a user asks:

```text
What is Deep Learning?
```

Traditional chunk:

```text
Deep Learning...
Weather...
Tourism...
```

Embedding contains mixed meanings.

Retrieval quality decreases.

---

Semantic chunk:

```text
Machine Learning
Neural Networks
Deep Learning
```

Embedding represents one topic.

Retrieval quality increases significantly.

---

# LangChain Semantic Chunking

Modern LangChain provides semantic chunking through embedding-based methods.

Example:

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

splitter = SemanticChunker(embeddings)

docs = splitter.create_documents([text])
```

Pipeline:

```text
Text
 ↓
Sentence Split
 ↓
Embeddings
 ↓
Similarity Analysis
 ↓
Semantic Chunks
```

---

# Different Breakpoint Strategies

Semantic chunkers need a rule to decide:

> "When should a new chunk begin?"

---

## 1. Percentile Strategy

Most common.

```python
splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile"
)
```

Process:

```text
All similarities computed

Lowest 5%
Lowest 10%
Lowest 20%
```

become chunk boundaries.

---

Example:

```text
0.91
0.93
0.88
0.20 ← boundary
0.90
0.92
```

---

## 2. Standard Deviation Strategy

Boundary occurs when similarity drops far below average.

```python
breakpoint_threshold_type="standard_deviation"
```

Uses:

```text
mean similarity
standard deviation
```

to detect topic shifts.

---

## 3. Interquartile Strategy

More robust to outliers.

```python
breakpoint_threshold_type="interquartile"
```

Uses statistical quartiles.

Useful for large noisy documents.

---

# Example

Document:

```text
Python Basics

Variables store values.

Functions organize code.

Loops repeat instructions.

Machine Learning

Models learn patterns.

Neural networks mimic neurons.

Deep learning uses many layers.
```

Traditional chunking:

```text
Chunk 1:
Python Basics
Variables
Functions
Loops
Machine Learning

Chunk 2:
Models
Neural Networks
Deep Learning
```

Machine Learning section gets split.

---

Semantic chunking:

```text
Chunk 1:
Python Basics
Variables
Functions
Loops

Chunk 2:
Machine Learning
Models
Neural Networks
Deep Learning
```

Much better.

---

# Advantages

## 1. Better Retrieval

Most important benefit.

Chunks represent a single topic.

---

## 2. Better Embeddings

Embedding quality improves because:

```text
One Chunk
=
One Idea
```

instead of:

```text
One Chunk
=
Five Different Ideas
```

---

## 3. Better Context

LLM receives coherent information.

---

## 4. Less Hallucination

Cleaner retrieval means fewer irrelevant chunks.

---

## 5. Better Question Answering

Especially for:

* Research papers
* Books
* Documentation
* Knowledge bases

---

# Disadvantages

## 1. Expensive

Recursive splitter:

```text
No embeddings needed
```

Semantic splitter:

```text
Embeddings for every sentence
```

Cost increases significantly.

---

## 2. Slower

Must compute:

```text
Sentence embeddings
+
Similarity matrix
+
Boundary detection
```

before indexing.

---

## 3. Uneven Chunk Sizes

Example:

```text
Chunk 1 = 200 words
Chunk 2 = 900 words
Chunk 3 = 350 words
```

This may not fit strict token limits.

---

# Semantic Chunking vs Recursive Character Splitting

| Feature           | Recursive   | Semantic         |
| ----------------- | ----------- | ---------------- |
| Speed             | Fast        | Slow             |
| Cost              | Cheap       | Expensive        |
| Topic Awareness   | No          | Yes              |
| Embeddings Needed | No          | Yes              |
| RAG Quality       | Good        | Excellent        |
| Production Use    | Very Common | Advanced Systems |

---

# What is Used in Production?

Most production RAG systems use a hybrid approach:

```text
Document
 ↓
Recursive Character Splitter
 ↓
1000-1500 token chunks
 ↓
(Optional)
Semantic Refinement
 ↓
Vector DB
```

Why?

Pure semantic chunking can be expensive for millions of documents.

So companies often use:

1. Structure-aware splitting (Markdown/HTML/code)
2. Recursive chunking
3. Semantic retrieval/reranking

This gives most of the benefit of semantic chunking while keeping costs manageable.

For interviews and practical RAG projects, remember this progression:

```text
Character Splitter
      ↓
Recursive Character Splitter
      ↓
Token Splitter
      ↓
Semantic Chunker
```

where **Semantic Chunking is the most intelligent but also the most computationally expensive approach.**
