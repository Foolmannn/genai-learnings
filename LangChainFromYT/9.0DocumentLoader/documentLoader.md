In modern **LangChain**, a **Document Loader** is a component that loads data from different sources (PDFs, text files, web pages, databases, cloud storage, etc.) and converts them into LangChain `Document` objects.

A `Document` typically looks like:

```python
Document(
    page_content="This is the text content...",
    metadata={"source": "file.pdf"}
)
```

---

# Why Document Loaders Exist

LLMs cannot directly read files.

The typical RAG pipeline is:

```text
Data Source
     ↓
Document Loader
     ↓
Documents
     ↓
Text Splitter
     ↓
Embeddings
     ↓
Vector Store
     ↓
Retriever
     ↓
LLM
```

Example:

```text
PDF File
   ↓
PyPDFLoader
   ↓
Documents
   ↓
RecursiveCharacterTextSplitter
   ↓
Chunks
   ↓
Vector DB
```

---

# Installation (Modern LangChain)

Most loaders have moved to separate packages:

```bash
pip install langchain
pip install langchain-community
```

Many loaders also require extra dependencies.

---

# 1. TextLoader

Loads plain text files.

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("notes.txt")

docs = loader.load()

print(docs[0].page_content)
print(docs[0].metadata)
```

Output:

```python
[
 Document(
   page_content="Hello World",
   metadata={"source":"notes.txt"}
 )
]
```

---

# 2. PyPDFLoader

Loads PDF files page by page.

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("book.pdf")

docs = loader.load()
```

Each page becomes a document.

```python
print(docs[0].metadata)
```

Output:

```python
{
    "source":"book.pdf",
    "page":0
}
```

---

# Load All Pages at Once

```python
for doc in docs:
    print(doc.page_content)
```

---

# Lazy Loading PDFs

Useful for large PDFs.

```python
loader = PyPDFLoader("large.pdf")

for doc in loader.lazy_load():
    print(doc.page_content)
```

Pages are loaded one by one.

Memory efficient.

---

# 3. CSVLoader

Load CSV files.

Example CSV:

```csv
name,age
Suman,20
Ram,22
```

Code:

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader("people.csv")

docs = loader.load()
```

Output:

```python
name: Suman
age: 20
```

Each row becomes a document.

---

# 4. JSONLoader

Load JSON files.

Example:

```json
{
    "name":"Suman",
    "skills":["Python","React"]
}
```

```python
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="data.json",
    jq_schema="."
)

docs = loader.load()
```

---

# 5. WebBaseLoader

Loads website content.

```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader(
    "https://python.org"
)

docs = loader.load()
```

Useful for:

* Documentation
* Blogs
* Articles

---

# Multiple URLs

```python
loader = WebBaseLoader([
    "https://python.org",
    "https://langchain.com"
])

docs = loader.load()
```

---

# 6. DirectoryLoader

Load all files from a folder.

Folder:

```text
docs/
 ├── a.txt
 ├── b.txt
 └── c.txt
```

```python
from langchain_community.document_loaders import DirectoryLoader

loader = DirectoryLoader("docs")

docs = loader.load()
```

---

# Load Only Text Files

```python
loader = DirectoryLoader(
    "docs",
    glob="*.txt"
)
```

---

# Recursive Directory Loading

```python
loader = DirectoryLoader(
    "docs",
    glob="**/*.txt"
)
```

Loads subfolders too.

---

# 7. UnstructuredFileLoader

Handles many formats:

* PDF
* DOCX
* PPTX
* HTML
* TXT

```python
from langchain_community.document_loaders import UnstructuredFileLoader

loader = UnstructuredFileLoader("report.docx")

docs = loader.load()
```

Very flexible but slower.

---

# 8. Docx2txtLoader

For Word files.

```python
from langchain_community.document_loaders import Docx2txtLoader

loader = Docx2txtLoader("resume.docx")

docs = loader.load()
```

---

# 9. NotebookLoader

Loads Jupyter notebooks.

```python
from langchain_community.document_loaders import NotebookLoader

loader = NotebookLoader(
    "tutorial.ipynb"
)

docs = loader.load()
```

Useful for AI coding assistants.

---

# 10. YoutubeLoader

Load video transcripts.

```python
from langchain_community.document_loaders import YoutubeLoader

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=xxxxx"
)

docs = loader.load()
```

Requires transcript availability.

---

# 11. SitemapLoader

Loads entire websites through sitemap.

```python
from langchain_community.document_loaders import SitemapLoader

loader = SitemapLoader(
    "https://example.com/sitemap.xml"
)

docs = loader.load()
```

Great for building website chatbots.

---

# Modern LangChain Example (RAG)

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

loader = PyPDFLoader("book.pdf")

documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(len(chunks))
```

Pipeline:

```text
PDF
 ↓
PyPDFLoader
 ↓
Documents
 ↓
Text Splitter
 ↓
Chunks
 ↓
Embeddings
 ↓
Vector Store
 ↓
Retriever
 ↓
LLM
```

---

# New Loader API in LangChain

Many loaders support:

### `load()`

Loads everything immediately.

```python
docs = loader.load()
```

### `lazy_load()`

Loads documents one at a time.

```python
for doc in loader.lazy_load():
    print(doc.page_content)
```

### `aload()`

Async loading.

```python
docs = await loader.aload()
```

### `alazy_load()`

Async lazy loading.

```python
async for doc in loader.alazy_load():
    print(doc)
```

---

# Most Commonly Used Loaders in Real Projects

| Loader                   | Use Case              |
| ------------------------ | --------------------- |
| `PyPDFLoader`            | PDF chatbot           |
| `TextLoader`             | TXT files             |
| `CSVLoader`              | Structured data       |
| `JSONLoader`             | JSON datasets         |
| `WebBaseLoader`          | Website scraping      |
| `DirectoryLoader`        | Bulk document loading |
| `Docx2txtLoader`         | Word documents        |
| `YoutubeLoader`          | Video transcript RAG  |
| `SitemapLoader`          | Documentation chatbot |
| `UnstructuredFileLoader` | Mixed file formats    |

For someone building modern RAG applications in 2026, focus first on:

1. `PyPDFLoader`
2. `WebBaseLoader`
3. `DirectoryLoader`
4. `CSVLoader`
5. `RecursiveCharacterTextSplitter`

These five cover most interview questions and real-world LangChain projects.


Good catch. What you're seeing is the difference between **LangChain's modern documentation structure** and the **actual implementation packages**.

The page you linked:

[LangChain Document Loader Integrations Docs](https://docs.langchain.com/oss/python/integrations/document_loaders?utm_source=chatgpt.com)

does **not** show import statements anymore. It shows integrations by category (PDFs, Webpages, Cloud Providers, etc.) and intentionally hides many implementation details. ([LangChain Docs][1])

For example, the docs now list:

* PyPDF
* Docling
* Firecrawl
* Sitemap
* CSV
* JSON
* GitHub
* Notion

instead of showing:

```python
from langchain_community.document_loaders import PyPDFLoader
```

directly. ([LangChain Docs][1])

### What's happening behind the scenes?

LangChain v1 has moved toward:

```text
langchain-core      ← interfaces
langchain           ← high-level framework
langchain-community ← community integrations
partner packages    ← vendor-specific integrations
```

Many loaders are still implemented in `langchain-community`, but the official docs now describe them as **integrations** rather than teaching the import paths. ([LangChain Docs][1])

For example, the "PyPDF" integration corresponds to:

```python
from langchain_community.document_loaders import PyPDFLoader
```

while "CSV" corresponds to:

```python
from langchain_community.document_loaders import CSVLoader
```

The docs are becoming more integration-centric and less package-centric. ([LangChain Docs][1])

### Modern RAG trend (2025–2026)

If you're starting fresh today, many engineers are moving away from classic loaders like:

```python
PyPDFLoader
PDFMinerLoader
PyMuPDFLoader
```

and instead using document intelligence tools such as:

* Docling
* Firecrawl
* Unstructured
* Kreuzberg

because they preserve tables, layouts, headers, and metadata much better than traditional PDF-to-text extraction. ([LangChain Docs][1])

### What I would learn today

For a modern LangChain + RAG stack:

```text
1. DoclingLoader
2. FirecrawlLoader
3. WebBaseLoader
4. CSVLoader
5. JSONLoader
```

and understand the common loader API:

```python
loader.load()
loader.lazy_load()
```

which is still the core abstraction used by LangChain loaders. ([LangChain Docs][1])

If you're following a specific tutorial, paste the import statement that's failing and I'll show you the exact 2026 equivalent. Often the code changed from:

```python
from langchain.document_loaders import PyPDFLoader
```

to

```python
from langchain_community.document_loaders import PyPDFLoader
```

or to a completely different integration package depending on the loader.

[1]: https://docs.langchain.com/oss/python/integrations/document_loaders?utm_source=chatgpt.com "Document loader integrations - Docs by LangChain"
