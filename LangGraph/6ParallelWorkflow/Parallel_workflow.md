# Parallel Workflows in LangGraph

Parallel workflows are one of the most useful patterns in **LangGraph** when multiple tasks can be executed independently and their results later combined.

For example, suppose you are building a research agent:

```text
                  ┌──→ Search Web ───────┐
User Query ───────┼──→ Analyze Data ──────┼──→ Combine Results ──→ Final Answer
                  └──→ Search Documents ─┘
```

Instead of doing:

```text
Search Web
    ↓
Analyze Data
    ↓
Search Documents
    ↓
Combine
```

you can execute the independent tasks concurrently:

```text
             ┌── Search Web ──────┐
             │                    │
Query ───────┼── Analyze Data ────┼──→ Combine
             │                    │
             └── Search Docs ────┘
```

This can significantly reduce workflow latency.

---

# 1. What is a Parallel Workflow?

A **parallel workflow** is a LangGraph workflow where one node branches into multiple nodes that can execute independently.

Consider:

```text
START
  ↓
Prepare
  ↓
 ┌─────────────┬─────────────┬─────────────┐
 ↓             ↓             ↓
Task A        Task B        Task C
 ↓             ↓             ↓
 └─────────────┴─────────────┘
                ↓
             Combine
                ↓
               END
```

The important idea is:

> **Task A, Task B, and Task C do not depend on each other's output, so they can run in parallel.**

This is different from a sequential workflow.

### Sequential

```text
A → B → C
```

### Parallel

```text
    ┌→ A ─┐
    ├→ B ─┤
START    ├→ D
    ├→ C ─┤
    └─────┘
```

---

# 2. Why Use Parallel Workflows?

Suppose you have three operations:

```text
Task A = 3 seconds
Task B = 4 seconds
Task C = 2 seconds
```

Sequential execution:

```text
3 + 4 + 2 = 9 seconds
```

Parallel execution is approximately:

```text
max(3, 4, 2) = 4 seconds
```

So instead of waiting 9 seconds, you may only need to wait around 4 seconds, ignoring orchestration and resource overhead.

This is especially useful when your nodes perform:

* LLM calls
* Web searches
* Database queries
* API requests
* Document retrieval
* Independent calculations
* Multiple classification tasks

---

# 3. Parallelism in LangGraph

The fundamental mechanism is **graph topology**.

Suppose we have:

```python
START → node_a
```

and then create:

```text
node_a
 ├──→ node_b
 ├──→ node_c
 └──→ node_d
```

LangGraph knows that `node_b`, `node_c`, and `node_d` are independent downstream tasks.

You can then connect all of them to a final node:

```text
             ┌──→ B ──┐
             │         │
A ───────────┼──→ C ───┼──→ D
             │         │
             └──→ E ──┘
```

The graph structure itself expresses the workflow.

---

# 4. Basic Example

Let's create a simple research workflow.

We want to perform three independent analyses:

1. Technical analysis
2. Business analysis
3. Market analysis

Then combine them.

## State

```python
from typing import TypedDict


class ResearchState(TypedDict):
    topic: str
    technical: str
    business: str
    market: str
    final_report: str
```

---

# 5. Create the Nodes

```python
def technical_analysis(state: ResearchState):
    topic = state["topic"]

    return {
        "technical": f"Technical analysis of {topic}"
    }


def business_analysis(state: ResearchState):
    topic = state["topic"]

    return {
        "business": f"Business analysis of {topic}"
    }


def market_analysis(state: ResearchState):
    topic = state["topic"]

    return {
        "market": f"Market analysis of {topic}"
    }
```

Each function:

* receives the current state
* performs its own task
* returns only the state updates it owns

---

# 6. Combine the Results

Now create a final node:

```python
def combine_results(state: ResearchState):

    final_report = f"""
    Topic: {state['topic']}

    Technical:
    {state['technical']}

    Business:
    {state['business']}

    Market:
    {state['market']}
    """

    return {
        "final_report": final_report
    }
```

---

# 7. Build the LangGraph

Modern LangGraph uses `StateGraph`.

```python
from langgraph.graph import StateGraph, START, END


builder = StateGraph(ResearchState)

builder.add_node("technical", technical_analysis)
builder.add_node("business", business_analysis)
builder.add_node("market", market_analysis)
builder.add_node("combine", combine_results)
```

Now create the parallel branches:

```python
builder.add_edge(START, "technical")
builder.add_edge(START, "business")
builder.add_edge(START, "market")
```

Then:

```python
builder.add_edge("technical", "combine")
builder.add_edge("business", "combine")
builder.add_edge("market", "combine")

builder.add_edge("combine", END)
```

Compile:

```python
graph = builder.compile()
```

---

# 8. Visual Structure

The graph is essentially:

```text
                  ┌───────────────→ technical ──────┐
                  │                                  │
START ────────────┼───────────────→ business ────────┼──→ combine → END
                  │                                  │
                  └───────────────→ market ─────────┘
```

The three branches are independent.

---

# 9. Running the Graph

```python
result = graph.invoke({
    "topic": "Generative AI"
})

print(result["final_report"])
```

The final state will contain:

```python
{
    "topic": "Generative AI",

    "technical": "...",

    "business": "...",

    "market": "...",

    "final_report": "..."
}
```

---

# 10. The Important Concept: State Updates

This is one of the most important things to understand about parallel workflows.

Suppose the initial state is:

```python
{
    "topic": "LangGraph"
}
```

The three nodes produce:

### Technical

```python
{
    "technical": "..."
}
```

### Business

```python
{
    "business": "..."
}
```

### Market

```python
{
    "market": "..."
}
```

LangGraph combines these updates into the state:

```text
              State
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
 technical  business   market
       │        │        │
       └────────┼────────┘
                ↓
        Updated State
```

Result:

```python
{
    "topic": "LangGraph",
    "technical": "...",
    "business": "...",
    "market": "..."
}
```

Then `combine` receives the accumulated state.

---

# 11. Why Separate State Keys Matter

Consider this bad design:

```python
class State(TypedDict):
    result: str
```

And all three nodes do:

```python
return {
    "result": "technical result"
}
```

```python
return {
    "result": "business result"
}
```

```python
return {
    "result": "market result"
}
```

Now multiple parallel nodes are trying to update the same state key.

That creates a **state conflict** unless you explicitly define how those updates should be merged.

A much cleaner design is:

```python
class State(TypedDict):
    technical: str
    business: str
    market: str
```

Then each node owns its own field.

---

# 12. Parallel Workflow with an LLM

This is where parallel workflows become much more useful.

Suppose the user asks:

```text
"Analyze the future of electric vehicles."
```

You could ask an LLM to independently generate:

```text
Technical perspective
Economic perspective
Environmental perspective
```

Graph:

```text
                         ┌──→ Technical LLM ───┐
                         │                     │
User Query → Prepare ────┼──→ Economic LLM ────┼──→ Synthesize
                         │                     │
                         └──→ Environmental ───┘
```

Each LLM call can happen independently.

---

# 13. Example with LangChain

```python
from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END


llm = ChatOpenAI(
    model="gpt-4.1-mini"
)
```

State:

```python
class ResearchState(TypedDict):
    topic: str
    technical: str
    economic: str
    environmental: str
    final: str
```

Technical node:

```python
def technical_node(state: ResearchState):

    response = llm.invoke(
        f"""
        Analyze the following topic from a technical
        perspective:

        {state['topic']}
        """
    )

    return {
        "technical": response.content
    }
```

Economic node:

```python
def economic_node(state: ResearchState):

    response = llm.invoke(
        f"""
        Analyze the following topic from an economic
        perspective:

        {state['topic']}
        """
    )

    return {
        "economic": response.content
    }
```

Environmental node:

```python
def environmental_node(state: ResearchState):

    response = llm.invoke(
        f"""
        Analyze the following topic from an environmental
        perspective:

        {state['topic']}
        """
    )

    return {
        "environmental": response.content
    }
```

Synthesis:

```python
def synthesis_node(state: ResearchState):

    prompt = f"""
    Create a comprehensive analysis using these perspectives.

    Technical:
    {state['technical']}

    Economic:
    {state['economic']}

    Environmental:
    {state['environmental']}
    """

    response = llm.invoke(prompt)

    return {
        "final": response.content
    }
```

---

# 14. Build the Graph

```python
builder = StateGraph(ResearchState)

builder.add_node("technical", technical_node)
builder.add_node("economic", economic_node)
builder.add_node("environmental", environmental_node)
builder.add_node("synthesis", synthesis_node)

builder.add_edge(START, "technical")
builder.add_edge(START, "economic")
builder.add_edge(START, "environmental")

builder.add_edge("technical", "synthesis")
builder.add_edge("economic", "synthesis")
builder.add_edge("environmental", "synthesis")

builder.add_edge("synthesis", END)

graph = builder.compile()
```

Invoke:

```python
result = graph.invoke({
    "topic": "Future of Electric Vehicles"
})

print(result["final"])
```

---

# 15. Important: Parallel Does Not Mean "Run Everything Immediately"

Consider:

```text
START
  ↓
Prepare
  ↓
 ┌──────┬──────┬──────┐
 ↓      ↓      ↓
 A      B      C
 └──────┼──────┘
        ↓
        D
```

The execution dependencies are:

```text
Prepare → A
Prepare → B
Prepare → C

A ─┐
B ─┼→ D
C ─┘
```

So:

* `A`, `B`, `C` can run independently.
* `D` must wait until its required upstream work has completed.

This is essentially a **directed acyclic graph (DAG)**.

---

# 16. Fan-Out and Fan-In

The two concepts you should remember are:

## Fan-out

One node branches into multiple nodes.

```text
             ┌──→ A
             │
START → X ───┼──→ B
             │
             └──→ C
```

This is **fan-out**.

---

## Fan-in

Multiple branches converge into one node.

```text
A ──┐
B ──┼──→ D
C ──┘
```

This is **fan-in**.

Therefore, most parallel LangGraph workflows look like:

```text
             FAN-OUT
                ↓
          ┌─────┼─────┐
          ↓     ↓     ↓
          A     B     C
          └─────┼─────┘
                ↓
             FAN-IN
```

This pattern is extremely important in agentic workflows.

---

# 17. Parallel vs Sequential Workflows

## Sequential

```text
START
  ↓
A
  ↓
B
  ↓
C
  ↓
D
```

Use this when:

```text
B depends on A
C depends on B
D depends on C
```

For example:

```text
Retrieve document
       ↓
Extract information
       ↓
Analyze information
       ↓
Generate answer
```

You cannot meaningfully execute these simultaneously.

---

## Parallel

```text
             ┌→ A ─┐
             │     │
START ───────┼→ B ─┼→ D
             │     │
             └→ C ─┘
```

Use this when:

```text
A does not depend on B
B does not depend on C
C does not depend on A
```

---

# 18. Conditional Parallel Workflows

Parallelism becomes even more powerful when combined with conditional routing.

For example:

```text
                 ┌──→ Technical
                 │
START → Router ──┼──→ Business
                 │
                 └──→ Legal
```

But perhaps the router determines which branches are necessary.

For example:

```text
User Query
    ↓
Classifier
    ↓
 ┌──┴───────────────┐
 ↓                  ↓
Technical         Business
 ↓                  ↓
 └────────┬─────────┘
          ↓
       Synthesis
```

This lets you build **dynamic workflows**.

---

# 19. Parallel Tool Calls

Another common use case is tool calling.

Suppose the agent needs:

```text
Weather
Stock price
Currency conversion
```

These are independent.

Instead of:

```text
Weather
  ↓
Stock
  ↓
Currency
```

you can have:

```text
               ┌→ Weather API ───┐
               │                 │
User Request ──┼→ Stock API ─────┼→ Final Answer
               │                 │
               └→ Currency API ──┘
```

This is particularly useful for agent systems.

---

# 20. Parallel Document Processing

Suppose you upload:

```text
document1.pdf
document2.pdf
document3.pdf
document4.pdf
```

You can process them independently:

```text
                 ┌→ Process PDF 1 ──┐
                 │                  │
                 ├→ Process PDF 2 ──┤
Input Documents ─┼→ Process PDF 3 ──┼→ Combine
                 │                  │
                 └→ Process PDF 4 ──┘
```

Each branch might:

```text
Load
 ↓
Extract
 ↓
Summarize
```

and then the summaries are combined.

---

# 21. Parallel RAG

Parallelism is especially useful for **multi-source RAG**.

Suppose the user asks:

```text
"What are the security risks of LangGraph?"
```

You might search:

```text
Vector DB
Web
Documentation
GitHub
Internal Knowledge Base
```

Graph:

```text
                       ┌→ Vector DB ──────┐
                       │                  │
                       ├→ Web Search ─────┤
                       │                  │
Query → Query Analysis ┼→ Documentation ──┼→ Rank/Combine
                       │                  │
                       ├→ GitHub ─────────┤
                       │                  │
                       └→ Internal DB ────┘
```

This is often better than relying on a single retrieval source.

---

# 22. Parallel RAG Architecture

A more realistic architecture might be:

```text
                         ┌→ Semantic Search ──┐
                         │                    │
                         ├→ Keyword Search ───┤
User Query → Rewrite ────┤                    ├→ Reranker → LLM
                         ├→ Web Search ───────┤
                         │                    │
                         └→ Metadata Search ──┘
```

This is a very useful production pattern.

---

# 23. Parallel Map Processing

Another important pattern is **map-reduce**.

Suppose you have 100 documents.

You want to summarize each one.

Instead of:

```text
Document 1 → Summary
Document 2 → Summary
Document 3 → Summary
...
Document 100 → Summary
```

you conceptually perform:

```text
                 ┌→ Summary 1 ──┐
                 ├→ Summary 2 ──┤
Documents ───────┼→ Summary 3 ──┼→ Reduce → Final Summary
                 ├→ ... ────────┤
                 └→ Summary 100 ┘
```

This is:

```text
MAP
 ↓
Parallel processing
 ↓
REDUCE
```

LangGraph provides patterns for dynamically creating work items, which is particularly useful when the number of parallel tasks isn't known ahead of time.

---

# 24. Static vs Dynamic Parallelism

There are two major forms you should distinguish.

## Static parallelism

You know the branches when constructing the graph.

```text
START
 ├──→ A
 ├──→ B
 └──→ C
```

Example:

```python
builder.add_edge(START, "technical")
builder.add_edge(START, "business")
builder.add_edge(START, "market")
```

---

## Dynamic parallelism

The number of tasks is determined during execution.

For example:

```text
Input
 ↓
Find 50 documents
 ↓
Create 50 processing tasks
 ↓
Process them
 ↓
Combine results
```

You don't want to manually create:

```text
document_1
document_2
...
document_50
```

Instead, the workflow dynamically creates work.

This is where LangGraph's **map-reduce / Send-based patterns** become important.

---

# 25. Dynamic Parallelism with `Send`

One of the most important LangGraph concepts for dynamic fan-out is `Send`.

Conceptually:

```text
                 ┌→ Process document 1
                 │
Input → Router ──┼→ Process document 2
                 │
                 ├→ Process document 3
                 │
                 └→ Process document N
```

The router can dynamically generate tasks.

A simplified example:

```python
from langgraph.constants import Send
```

Suppose:

```python
class State(TypedDict):
    documents: list[str]
```

The router can create work:

```python
def fan_out(state: State):

    return [
        Send(
            "process_document",
            {"document": document}
        )
        for document in state["documents"]
    ]
```

So if:

```python
state["documents"] = [
    "doc1",
    "doc2",
    "doc3"
]
```

the router effectively produces:

```text
Send(process_document, doc1)
Send(process_document, doc2)
Send(process_document, doc3)
```

These become parallel work items.

---

# 26. Why `Send` Is Powerful

Imagine a user's query requires processing:

```text
10 PDFs
```

You don't know in advance that there will be exactly 10.

Tomorrow there might be:

```text
100 PDFs
```

or:

```text
1000 PDFs
```

A static graph is awkward for this.

Dynamic fan-out gives:

```text
documents
   ↓
fan-out
   ↓
N processing tasks
   ↓
fan-in
   ↓
result
```

This is essentially a dynamic map-reduce workflow.

---

# 27. Reducers and Parallel State Updates

Dynamic parallelism introduces an important problem.

Suppose 10 workers produce:

```python
{
    "result": "..."
}
```

You need to tell LangGraph how multiple updates to the same state field should be combined.

This is where **reducers** become important.

For example:

```python
from typing import Annotated
import operator


class State(TypedDict):
    results: Annotated[list[str], operator.add]
```

The annotation tells LangGraph that updates to `results` should be accumulated.

Suppose workers return:

```python
{"results": ["Result A"]}
```

and:

```python
{"results": ["Result B"]}
```

and:

```python
{"results": ["Result C"]}
```

The reducer combines them conceptually into:

```python
{
    "results": [
        "Result A",
        "Result B",
        "Result C"
    ]
}
```

This is extremely important when working with dynamic parallel workflows.

---

# 28. Reducer vs Normal State Field

Consider:

```python
class State(TypedDict):
    result: str
```

This represents one value:

```text
result = "something"
```

But:

```python
class State(TypedDict):
    results: Annotated[list[str], operator.add]
```

represents accumulated values:

```text
results = [
    result1,
    result2,
    result3
]
```

So:

```text
Normal field
     ↓
single update/value

Reducer field
     ↓
multiple updates
     ↓
combined result
```

---

# 29. A Practical Map-Reduce Example

Suppose we want to summarize several pieces of text.

```python
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
```

State:

```python
class OverallState(TypedDict):
    documents: list[str]
    summaries: Annotated[list[str], operator.add]
    final_summary: str
```

Worker state:

```python
class DocumentState(TypedDict):
    document: str
```

Worker:

```python
def summarize_document(state: DocumentState):

    document = state["document"]

    summary = f"Summary of: {document}"

    return {
        "summaries": [summary]
    }
```

---

# 30. Fan-Out Function

```python
def fan_out_documents(state: OverallState):

    return [
        Send(
            "summarize",
            {
                "document": document
            }
        )
        for document in state["documents"]
    ]
```

This dynamically creates one task for each document.

---

# 31. Reduce Node

```python
def reduce_summaries(state: OverallState):

    combined = "\n\n".join(
        state["summaries"]
    )

    return {
        "final_summary": combined
    }
```

Graph conceptually becomes:

```text
                 ┌→ summarize(doc1) ─┐
                 │                   │
                 ├→ summarize(doc2) ─┤
START → fan-out ─┼→ summarize(doc3) ─┼→ reduce
                 │                   │
                 └→ summarize(docN) ─┘
```

This is one of the most important advanced parallel patterns in LangGraph.

---

# 32. Parallelism and Errors

Parallel workflows introduce another important issue:

> What happens if one branch fails?

Suppose:

```text
        ┌→ API A ✓
        │
START ──┼→ API B ✗
        │
        └→ API C ✓
```

You need to decide what the workflow should do.

Possible strategies:

### Strategy 1 — Fail the whole workflow

```text
A ✓
B ✗ → STOP
C ✓
```

Useful when every result is mandatory.

---

### Strategy 2 — Continue with partial results

```text
A ✓
B ✗
C ✓
 ↓
Combine A + C
```

Useful when some sources are optional.

---

### Strategy 3 — Retry failed branch

```text
B
↓
FAIL
↓
RETRY
↓
SUCCESS
```

Useful for unreliable APIs.

---

### Strategy 4 — Fallback

```text
Primary API
     ↓
   failed
     ↓
Fallback API
```

---

# 33. Parallelism and Retries

For example:

```text
             ┌→ Search API
             │
Query ───────┼→ Database
             │
             └→ Internal API
```

If `Search API` fails:

```text
Search API
    ↓
 Retry
    ↓
 Retry
    ↓
Fallback
```

while the other branches can continue independently.

This is one reason graph-based orchestration is valuable compared with writing one giant agent loop.

---

# 34. Parallelism vs Async Programming

An important distinction:

### LangGraph parallelism

Defines **workflow-level concurrency**:

```text
A ─┐
B ─┼→ C
D ─┘
```

### Python async

Defines how individual operations can execute concurrently:

```python
async def task():
    ...
```

They are related, but not the same concept.

LangGraph describes:

> **Which work is independent?**

The runtime handles execution according to its graph semantics and execution model.

---

# 35. Parallelism Doesn't Always Make Things Faster

Suppose your three operations all use a resource with a strict limit:

```text
API rate limit = 1 request/second
```

Running:

```text
A
B
C
```

simultaneously might cause:

```text
429 Too Many Requests
```

So parallelism should be used when:

* operations are independent
* resources allow concurrency
* API limits permit it
* downstream systems can handle the load

---

# 36. Parallel LLM Calls and Cost

Parallelism doesn't magically reduce token usage.

Suppose:

```text
LLM A = 1000 tokens
LLM B = 1000 tokens
LLM C = 1000 tokens
```

Total:

```text
3000 tokens
```

whether they execute:

```text
sequentially
```

or:

```text
parallel
```

The main benefit is usually **latency**, not token cost.

---

# 37. Parallelism in Agent Architecture

A sophisticated agent might look like:

```text
                         ┌→ Research Agent ───┐
                         │                    │
User → Planner ──────────┼→ Coding Agent ─────┼→ Reviewer
                         │                    │
                         └→ Data Agent ───────┘
```

This is a multi-agent parallel architecture.

For example:

### Research agent

Finds information.

### Coding agent

Writes implementation.

### Data agent

Analyzes data.

### Reviewer

Receives all three results and evaluates them.

This can be represented as:

```text
                    ┌──────── Research ────────┐
                    │                          │
Planner ────────────┼──────── Coding ──────────┼──→ Reviewer
                    │                          │
                    └──────── Data ────────────┘
```

---

# 38. Parallel vs Multi-Agent

These are not the same thing.

Parallelism is an **execution pattern**.

Multi-agent is an **architecture pattern**.

You can have:

```text
one agent
   ↓
parallel tools
```

or:

```text
multiple agents
   ↓
parallel execution
```

For example:

```text
                 ┌→ Agent A
Planner ─────────┼→ Agent B
                 └→ Agent C
```

This is both:

* multi-agent
* parallel workflow

---

# 39. A Real-World Research Agent

A good architecture could be:

```text
                      ┌→ Web Research ─────┐
                      │                    │
User → Planner ───────┼→ Academic Search ──┼→ Evidence Aggregator
                      │                    │
                      ├→ Internal Docs ────┤
                      │                    │
                      └→ GitHub Search ────┘
                                             ↓
                                          Reranker
                                             ↓
                                           Writer
                                             ↓
                                          Reviewer
```

Notice the stages:

```text
Planner
   ↓
Fan-out
   ↓
Parallel research
   ↓
Fan-in
   ↓
Reranking
   ↓
Generation
   ↓
Review
```

This is a very realistic LangGraph architecture.

---

# 40. Parallel Workflow with Human-in-the-Loop

You can even introduce human approval after parallel work:

```text
                 ┌→ Research A ──┐
                 │               │
                 ├→ Research B ──┤
START → Planner ─┼→ Research C ──┼→ Human Review
                 │               │
                 └→ Research D ──┘
                                      ↓
                                  Generate
```

The human doesn't need to review every individual branch.

Instead, the workflow aggregates the results first.

---

# 41. Parallel Workflow with Checkpointing

LangGraph's persistence/checkpointing capabilities become useful in long-running workflows.

Imagine:

```text
              ┌→ Research A
              │
Planner ──────┼→ Research B
              │
              └→ Research C
                     ↓
                 Synthesis
```

If something goes wrong after the research stage, you don't necessarily want to redo all research.

A persistent workflow can preserve state/checkpoints and allow the workflow to resume.

This becomes especially important for:

* expensive LLM calls
* long-running agents
* human approval
* external APIs
* production workflows

---

# 42. Parallel Workflow Design Rules

When designing parallel workflows, ask these questions.

### Question 1

Can these tasks execute independently?

If:

```text
B needs A
```

then they cannot be truly parallel.

---

### Question 2

Do they write to the same state key?

If:

```text
A → result
B → result
C → result
```

you need an appropriate reducer or a different state design.

---

### Question 3

Does the downstream node need all results?

If yes:

```text
A ─┐
B ─┼→ Combine
C ─┘
```

If not, you might not need fan-in at that point.

---

### Question 4

What happens when one branch fails?

Define:

```text
retry
fallback
partial result
failure
```

---

### Question 5

Is concurrency actually beneficial?

Consider:

```text
API limits
database limits
LLM provider limits
CPU
memory
network
cost
```

---

# 43. Common Mistakes

## Mistake 1 — Parallelizing dependent tasks

Bad:

```text
Retrieve
Analyze
```

and treating them as independent.

Analysis requires retrieval.

Correct:

```text
Retrieve → Analyze
```

---

## Mistake 2 — Shared state collisions

Bad:

```python
return {"result": ...}
```

from multiple branches without a reducer.

Better:

```python
return {"technical": ...}
```

```python
return {"business": ...}
```

or use a reducer:

```python
results: Annotated[list, operator.add]
```

---

## Mistake 3 — Assuming parallelism means unlimited concurrency

It doesn't.

External services can have:

```text
rate limits
connection limits
quota
resource constraints
```

---

## Mistake 4 — Making everything parallel

You should not turn:

```text
A → B → C
```

into parallel execution just because parallelism exists.

Parallelism should represent **actual independence**.

---

# 44. Sequential + Parallel Hybrid

Most real workflows are not purely sequential or purely parallel.

They are hybrid.

For example:

```text
                 ┌→ Web Search ────────┐
                 │                     │
Query → Analyze ─┼→ Vector Search ─────┼→ Rerank
                 │                     │
                 └→ Database Search ───┘
                                         ↓
                                      Generate
                                         ↓
                                      Review
                                         ↓
                                        END
```

This is probably the most important architecture to understand.

Real-world LangGraph workflows frequently look like:

```text
Sequential
    ↓
Parallel
    ↓
Sequential
    ↓
Parallel
    ↓
Sequential
```

---

# 45. Mental Model

The easiest way to remember LangGraph parallelism is:

```text
             DEPENDENCY GRAPH
                    │
                    ↓
          ┌─────────┴─────────┐
          │                   │
       Independent         Independent
          │                   │
          ↓                   ↓
       Parallel             Parallel
          │                   │
          └─────────┬─────────┘
                    ↓
                  Merge
```

Or simply:

> **If two nodes don't need each other's outputs, they are candidates for parallel execution.**

---

# 46. The Three Patterns You Should Master

For LangGraph, I'd recommend mastering these three patterns in order:

### 1. Basic fan-out/fan-in

```text
       ┌→ A ─┐
START ─┼→ B ─┼→ D
       └→ C ─┘
```

Learn:

* multiple outgoing edges
* multiple incoming edges
* state updates

---

### 2. Reducers

```text
A ─┐
B ─┼→ results[]
C ─┘
```

Learn:

```python
Annotated[list, operator.add]
```

This is essential for accumulating results from parallel workers.

---

### 3. Dynamic fan-out with `Send`

```text
                ┌→ Worker 1
                ├→ Worker 2
Router ─────────┼→ Worker 3
                ├→ Worker 4
                └→ Worker N
```

Learn:

```python
Send(...)
```

This is the pattern you need when the number of parallel tasks is determined dynamically.

---

# 47. Putting Everything Together

A production-style architecture could look like:

```text
                         ┌→ Web Search ────────┐
                         │                     │
                         ├→ Vector Search ─────┤
                         │                     │
User → Planner → Fan-Out ┼→ Database Search ───┼→ Reducer
                         │                     │
                         └→ Document Search ───┘
                                                   ↓
                                                Reranker
                                                   ↓
                                               Synthesizer
                                                   ↓
                                                Reviewer
                                                   ↓
                                                  END
```

And if the number of documents is dynamic:

```text
                         ┌→ Process Doc 1 ─┐
                         ├→ Process Doc 2 ─┤
Planner → Send ──────────┼→ Process Doc 3 ─┼→ Reducer
                         ├→ Process Doc 4 ─┤
                         └→ Process Doc N ─┘
```

That gives you the core architecture behind many sophisticated LangGraph systems.

---

# 48. What to Learn Next

Since you're working through the modern LangChain/LangGraph ecosystem, I'd learn parallel workflows in this order:

```text
LangGraph State
      ↓
Nodes
      ↓
Edges
      ↓
Conditional Edges
      ↓
Fan-out / Fan-in
      ↓
Reducers
      ↓
Dynamic Fan-out
      ↓
Send
      ↓
Map-Reduce
      ↓
Subgraphs
      ↓
Persistence / Checkpointing
      ↓
Human-in-the-loop
      ↓
Multi-Agent Workflows
      ↓
Production Agent Architecture
```

The **most important transition** is:

```text
Static parallelism
      ↓
Reducers
      ↓
Dynamic parallelism with Send
      ↓
Map-Reduce
```

Once you understand those four concepts, parallel workflows in LangGraph become much easier to reason about.
