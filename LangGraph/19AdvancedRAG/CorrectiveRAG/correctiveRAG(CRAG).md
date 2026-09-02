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

# 10. Query rewriting

Instead of sending the original question directly to web search:

```text
Who won the World Cup?
```

the system can transform it into something more retrieval-friendly:

```text
2026 FIFA World Cup winner
```

or:

```text
2026 FIFA World Cup final winner
```

A query rewriting node can be:

```python
def rewrite_query(state):
    question = state["question"]

    prompt = f"""
    Rewrite the following question into a better search query.

    Question:
    {question}

    Return only the rewritten query.
    """

    response = llm.invoke(prompt)

    return {
        "question": response.content
    }
```

---

# 11. External search

After rewriting:

```text
Question
   ↓
Query Rewriter
   ↓
Better Search Query
   ↓
Web Search
```

For example, with Tavily:

```python
from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=3
)
```

Then:

```python
results = web_search.invoke(query)
```

The LangChain CRAG example uses web search as the supplementary datasource when vector retrieval is insufficient. ([LangChain][3])

---

# 12. CRAG in LangGraph

Now let's build the architecture.

Our graph will look like:

```text
                         START
                           │
                           ▼
                       RETRIEVE
                           │
                           ▼
                    GRADE DOCUMENTS
                           │
                 ┌─────────┴──────────┐
                 │                    │
            Relevant?             Not useful
                 │                    │
                 ▼                    ▼
          REFINE KNOWLEDGE      REWRITE QUERY
                 │                    │
                 │                    ▼
                 │               WEB SEARCH
                 │                    │
                 └──────────┬─────────┘
                            ▼
                         GENERATE
                            │
                            ▼
                           END
```

This is essentially the structure demonstrated by LangChain's CRAG/LangGraph examples, although their introductory implementation simplifies or omits some of the original knowledge-refinement machinery. ([LangChain][3])

---

# 13. Installing dependencies

For a Python implementation:

```bash
pip install langgraph langchain langchain-openai langchain-community
pip install langchain-tavily
pip install chromadb
```

You'll need:

```env
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
```

---

# 14. Define the graph state

Start with:

```python
from typing import TypedDict, List
from langchain_core.documents import Document


class CRAGState(TypedDict):
    question: str
    documents: List[Document]
    generation: str
    web_search: bool
```

Think of this as the shared memory of the graph.

At the beginning:

```python
{
    "question": "What is short-term memory in LangGraph?",
    "documents": [],
    "generation": "",
    "web_search": False
}
```

---

# 15. Create the LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)
```

For grading, `temperature=0` is useful because we want consistent decisions.

---

# 16. Retriever

Assume you've already created:

```python
vectorstore
```

Then:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)
```

Create the retrieval node:

```python
def retrieve(state: CRAGState):

    question = state["question"]

    documents = retriever.invoke(question)

    return {
        "documents": documents
    }
```

---

# 17. Document grader

Create the schema:

```python
from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):

    binary_score: str = Field(
        description="Is the document relevant to the question? yes or no"
    )
```

Create the grader:

```python
grader = llm.with_structured_output(GradeDocuments)
```

Now create the node:

```python
def grade_documents(state: CRAGState):

    question = state["question"]
    documents = state["documents"]

    filtered_documents = []
    relevant_count = 0

    for document in documents:

        prompt = f"""
        You are a document relevance grader.

        Question:
        {question}

        Document:
        {document.page_content}

        Determine whether the document contains information
        useful for answering the question.

        Return yes if relevant.
        Return no if irrelevant.
        """

        result = grader.invoke(prompt)

        if result.binary_score.lower() == "yes":
            filtered_documents.append(document)
            relevant_count += 1

    web_search = relevant_count == 0

    return {
        "documents": filtered_documents,
        "web_search": web_search
    }
```

This is a simplified but very practical CRAG implementation.

---

# 18. Conditional routing

Now we need to tell LangGraph:

```text
If documents are good
       ↓
    generate

Otherwise
       ↓
  rewrite query
```

Create:

```python
def decide_next(state: CRAGState):

    if state["web_search"]:
        return "rewrite_query"

    return "generate"
```

This function becomes a conditional edge.

---

# 19. Query rewriting node

```python
def rewrite_query(state: CRAGState):

    question = state["question"]

    prompt = f"""
    Rewrite this question into a better search query.

    Original question:
    {question}

    Produce a concise search query.
    """

    response = llm.invoke(prompt)

    return {
        "question": response.content
    }
```

Example:

```text
Original:

"What happened with the 2026 World Cup?"

↓

Rewritten:

"2026 FIFA World Cup winner final"
```

---

# 20. Web search node

```python
from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=3
)
```

Node:

```python
def web_search_node(state: CRAGState):

    question = state["question"]

    results = web_search.invoke(question)

    documents = []

    for result in results["results"]:

        documents.append(
            Document(
                page_content=result["content"],
                metadata={
                    "source": result["url"]
                }
            )
        )

    return {
        "documents": documents
    }
```

Now the graph has an external retrieval path.

---

# 21. Generation node

The generator is basically standard RAG.

```python
def generate(state: CRAGState):

    question = state["question"]
    documents = state["documents"]

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = f"""
    Answer the question using the provided context.

    Question:
    {question}

    Context:
    {context}

    If the context does not contain enough information,
    say that you don't have enough information.

    Answer clearly and accurately.
    """

    response = llm.invoke(prompt)

    return {
        "generation": response.content
    }
```

---

# 22. Build the LangGraph

Now the interesting part.

```python
from langgraph.graph import StateGraph, START, END


workflow = StateGraph(CRAGState)
```

Add nodes:

```python
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("rewrite_query", rewrite_query)
workflow.add_node("web_search", web_search_node)
workflow.add_node("generate", generate)
```

Connect:

```python
workflow.add_edge(
    START,
    "retrieve"
)

workflow.add_edge(
    "retrieve",
    "grade_documents"
)
```

Conditional edge:

```python
workflow.add_conditional_edges(
    "grade_documents",
    decide_next,
    {
        "generate": "generate",
        "rewrite_query": "rewrite_query"
    }
)
```

Then:

```python
workflow.add_edge(
    "rewrite_query",
    "web_search"
)

workflow.add_edge(
    "web_search",
    "generate"
)

workflow.add_edge(
    "generate",
    END
)
```

Compile:

```python
app = workflow.compile()
```

---

# 23. Complete graph

The resulting graph is:

```text
                  ┌───────────┐
                  │   START   │
                  └─────┬─────┘
                        │
                        ▼
                  ┌───────────┐
                  │  RETRIEVE │
                  └─────┬─────┘
                        │
                        ▼
              ┌──────────────────┐
              │ GRADE DOCUMENTS  │
              └────────┬─────────┘
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       relevant              irrelevant
             │                   │
             │                   ▼
             │            ┌──────────────┐
             │            │ REWRITE QUERY│
             │            └──────┬───────┘
             │                   │
             │                   ▼
             │            ┌──────────────┐
             │            │ WEB SEARCH   │
             │            └──────┬───────┘
             │                   │
             └──────────┬────────┘
                        ▼
                  ┌───────────┐
                  │  GENERATE │
                  └─────┬─────┘
                        │
                        ▼
                     ┌─────┐
                     │ END │
                     └─────┘
```

---

# 24. Invoke the graph

```python
result = app.invoke({
    "question": "What is short-term memory in LangGraph?",
    "documents": [],
    "generation": "",
    "web_search": False
})
```

Then:

```python
print(result["generation"])
```

---

# 25. But there's an important problem with this implementation

The implementation above is a **simplified CRAG**.

The original CRAG paper does more than:

```text
relevant → generate
irrelevant → web search
```

It also introduces:

### Retrieval evaluation

```text
How good is the retrieved knowledge?
```

### Knowledge refinement

```text
Break retrieved documents into knowledge strips
↓
Evaluate strips
↓
Keep useful information
```

### Web augmentation

```text
If local retrieval is insufficient
↓
External search
↓
Supplement knowledge
```

The original paper describes the evaluator as a lightweight component that returns a confidence degree and uses that to select retrieval actions. ([arXiv][1])

---
