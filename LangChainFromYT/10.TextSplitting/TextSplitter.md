# Text Splitters in LangChain (Detailed Notes)

## 1. What is a Text Splitter?

A **Text Splitter** is a component that divides large documents into smaller chunks before they are processed by LLMs, embeddings models, or vector databases.

### Why do we need text splitting?

Large Language Models have context window limits.

For example:

```
Document = 100 pages
Embedding Model Limit = 8000 tokens
```

You cannot directly send the entire document to the model.

Instead:

```
Document
   ↓
Text Splitter
   ↓
Chunk 1
Chunk 2
Chunk 3
...
```

Each chunk is then:

* Embedded
* Stored in Vector DB
* Retrieved during RAG

---

# 2. Text Splitting in a RAG Pipeline

```
PDF
 ↓
Document Loader
 ↓
Text Splitter
 ↓
Chunks
 ↓
Embedding Model
 ↓
Vector Database
 ↓
Retriever
 ↓
LLM
```

Without proper chunking:

* Retrieval quality decreases
* Context is lost
* Hallucinations increase

---

# 3. Installation

Modern LangChain uses a separate package.

```bash
pip install langchain-text-splitters
```

Import:

```python
from langchain_text_splitters import *
```

---

# 4. Important Parameters

Almost every splitter uses:

## chunk_size

Maximum size of a chunk.

```python
chunk_size=1000
```

Example:

```
Text Length = 3000 chars

Chunk 1 = 1000
Chunk 2 = 1000
Chunk 3 = 1000
```

---

## chunk_overlap

How much content is repeated between chunks.

```python
chunk_overlap=200
```

Example:

```
Chunk 1:
Python is a programming language....

Chunk 2:
...programming language used for AI...
```

Overlap prevents context loss.

---

### Why overlap is important?

Without overlap:

```
Chunk 1:
John went to

Chunk 2:
the market yesterday
```

Meaning gets broken.

With overlap:

```
Chunk 1:
John went to the market

Chunk 2:
to the market yesterday
```

Context preserved.

---

# 5. CharacterTextSplitter

Simplest splitter.

Splits text after fixed character counts.

```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=100
)
```

Example:

```
AAAAAAAAAAAAAA....
```

Split every 1000 characters.

---

### Pros

* Easy
* Fast

### Cons

* Can break sentences
* Can break words

Not ideal for RAG.

---

# 6. RecursiveCharacterTextSplitter (Most Important)

This is the most commonly used splitter.

### Why "Recursive"?

It tries multiple separators.

Order:

```python
[
    "\n\n",
    "\n",
    " ",
    ""
]
```

Meaning:

1. Split by paragraph
2. If too large → split by line
3. If too large → split by space
4. If too large → split by character

---

## Example

Input:

```
Paragraph 1

Paragraph 2

Paragraph 3
```

Output:

```
Chunk 1:
Paragraph 1

Chunk 2:
Paragraph 2

Chunk 3:
Paragraph 3
```

---

### Code

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_text(text)
```

---

### For Documents

```python
docs = splitter.create_documents([text])

for doc in docs:
    print(doc.page_content)
```

---

### Why it is preferred?

Because it preserves:

* Paragraphs
* Sentences
* Context

Hence:

✅ Best for RAG

---

# 7. TokenTextSplitter

Instead of characters, splits based on tokens.

Useful because LLMs think in tokens.

```python
from langchain_text_splitters import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
```

---

## Character vs Token

Text:

```
I love machine learning.
```

Characters:

```
24 characters
```

Tokens:

```
≈ 5 tokens
```

LLM limits are token-based.

Therefore token splitting is often more accurate.

---

# 8. Sentence-Based Splitting

Goal:

```
Never break a sentence.
```

Example:

```
Sentence 1.
Sentence 2.
Sentence 3.
```

Output:

```
Chunk 1:
Sentence 1.
Sentence 2.

Chunk 2:
Sentence 3.
```

Useful for:

* Question answering
* Academic documents

---

# 9. MarkdownTextSplitter

Used for Markdown files.

Input:

```markdown
# Introduction

Some text

# Methods

Some text
```

Output:

```
Chunk 1:
# Introduction

Chunk 2:
# Methods
```

---

### Code

```python
from langchain_text_splitters import MarkdownTextSplitter

splitter = MarkdownTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)
```

Useful for:

* Documentation
* README files
* Wikis

---

# 10. HTMLTextSplitter

Used for HTML pages.

Input:

```html
<h1>Introduction</h1>

<p>Text...</p>
```

Keeps HTML structure intact.

```python
from langchain_text_splitters import HTMLHeaderTextSplitter
```

Useful for:

* Web scraping
* Website RAG systems

---

# 11. JSON Splitter

For JSON documents.

Example:

```json
{
  "user": {
    "name": "John",
    "age": 25
  }
}
```

Keeps JSON hierarchy intact.

Useful for:

* APIs
* Configuration files
* Structured data

---

# 12. Python Code Splitter

For source code.

Instead of random chunking:

```python
def train():
    pass

def test():
    pass
```

Chunks become:

```
Function 1
Function 2
```

rather than arbitrary character blocks.

Useful for:

* Code assistants
* Repository Q&A
* GitHub RAG

---

# 13. Language-Specific Splitters

LangChain supports code-aware splitting for:

* Python
* Java
* JavaScript
* C++
* Go
* Rust
* PHP
* Kotlin
* TypeScript

Example:

```python
from langchain_text_splitters import Language
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=1000,
    chunk_overlap=100
)
```

---

# 14. Semantic Chunking (Advanced)

Traditional chunking:

```
1000 chars
1000 chars
1000 chars
```

Problem:

Meaning can be broken.

---

Semantic Chunking groups related content.

Example:

```
Machine Learning
Neural Networks
Deep Learning
```

remain together.

Even if character count differs.

---

Used with embeddings:

```
Sentence
   ↓
Embedding
   ↓
Similarity Check
   ↓
Semantic Chunks
```

Benefits:

* Better retrieval
* Better RAG answers
* Less hallucination

---

# 15. How to Choose Chunk Size?

Common settings:

| Use Case        | Chunk Size | Overlap |
| --------------- | ---------- | ------- |
| Small Docs      | 500        | 50      |
| PDFs            | 1000       | 100     |
| RAG Systems     | 1000-1500  | 100-200 |
| Research Papers | 1500-2000  | 200     |
| Source Code     | 500-1000   | 50-100  |

---

# 16. Best Practices for RAG

### PDFs

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

### Research Papers

```python
chunk_size=1500
chunk_overlap=300
```

### Code Repositories

```python
RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=800,
    chunk_overlap=100
)
```

### Documentation Websites

```python
MarkdownTextSplitter
```

or

```python
HTMLHeaderTextSplitter
```

---

# Interview Questions

### Q1. Why is chunk overlap used?

To preserve context between adjacent chunks and improve retrieval quality.

---

### Q2. Which splitter is most commonly used?

`RecursiveCharacterTextSplitter`

---

### Q3. Why not use CharacterTextSplitter for RAG?

It may split sentences and paragraphs arbitrarily, reducing retrieval quality.

---

### Q4. Character-based vs Token-based splitting?

| Character                | Token              |
| ------------------------ | ------------------ |
| Counts characters        | Counts tokens      |
| Simpler                  | More accurate      |
| Doesn't match LLM limits | Matches LLM limits |

---

### Q5. Which splitter should be used for most RAG projects?

`RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`

This is the default starting point for most production RAG systems unless you have a structured format (Markdown, HTML, code, JSON) where a specialized splitter works better.
