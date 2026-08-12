# Iterative Workflows in LangChain

An **iterative workflow** is a workflow where an LLM or a set of processing steps is executed **repeatedly**, with each iteration using the result of the previous iteration to improve, refine, validate, or continue the task.

A simple way to think about it:

> **Generate → Evaluate → Improve → Evaluate → Improve → ... → Stop**

This is different from a simple sequential workflow:

> **A → B → C → D**

In an iterative workflow:

> **A → B → C → if not good → A/B/C again**

Iterative workflows become especially important when building **AI agents, content refinement systems, code-generation systems, research systems, and autonomous workflows**.

---

# 1. Why do we need iterative workflows?

Suppose you ask an LLM:

> "Write a blog post about machine learning."

A single LLM call might produce a reasonable answer.

But suppose you want:

* high-quality content
* correct information
* good structure
* no unnecessary repetition
* proper examples
* appropriate length

You can ask the LLM to **evaluate its own output** and improve it.

For example:

```text
Generate Blog
     ↓
Evaluate Blog
     ↓
Is quality >= 8?
   /       \
 Yes        No
 ↓          ↓
Finish    Improve
             ↓
          Evaluate
```

This is an iterative workflow.

---

# 2. Iterative vs Sequential Workflow

### Sequential workflow

```text
Input
  ↓
Generate
  ↓
Process
  ↓
Format
  ↓
Output
```

Each node generally executes once.

### Iterative workflow

```text
             ┌──────────────┐
             ↓              │
Input → Generate → Evaluate ─┤
                  │           │
                  │ Bad       │
                  ↓           │
                Improve ──────┘
                  │
                  │ Good
                  ↓
                Output
```

The important concept is the **loop**.

---

# 3. Iterative workflows in modern LangChain ecosystem

Today, for graph-based iterative workflows, **LangGraph** is generally the appropriate tool within the LangChain ecosystem.

LangChain provides components such as:

* Chat models
* Tools
* Structured output
* Prompt templates
* Retrievers
* Document processing

LangGraph provides the orchestration primitives needed for:

* loops
* conditional routing
* state
* persistence
* human-in-the-loop
* agent workflows
* iterative execution

So conceptually:

```text
LangChain
   ↓
LLM + Tools + Structured Output
   ↓
LangGraph
   ↓
Stateful workflow
   ↓
Iteration / loops
```

---

# 4. Core components of an iterative workflow

An iterative workflow usually contains five things.

### 1. State

Stores the information shared between iterations.

Example:

```python
class BlogState(TypedDict):
    topic: str
    draft: str
    feedback: str
    score: int
    iteration: int
```

---

### 2. Generation node

Produces the initial result.

```python
def generate(state):
    ...
```

---

### 3. Evaluation node

Checks the result.

```python
def evaluate(state):
    ...
```

---

### 4. Improvement node

Uses feedback to improve the result.

```python
def improve(state):
    ...
```

---

### 5. Conditional routing

Decides whether to:

* stop
* or continue another iteration.

```python
def should_continue(state):
    if state["score"] >= 8:
        return "finish"

    return "improve"
```

This is what creates the loop.

---

# 5. Basic architecture

A typical iterative workflow looks like:

```text
             ┌─────────────────┐
             │     Generate    │
             └────────┬────────┘
                      ↓
             ┌─────────────────┐
             │     Evaluate    │
             └────────┬────────┘
                      ↓
                 Score good?
                  /       \
                Yes        No
                 ↓          ↓
              Finish      Improve
                            │
                            └──────────→ Evaluate
```

Notice that the workflow doesn't necessarily go back to the beginning.

It can loop between specific nodes.

---

# 6. Example: Blog generation and refinement

Let's build a realistic example.

Requirement:

> Generate a blog about "Machine Learning".

We want:

1. Generate draft
2. Evaluate draft
3. If quality is low, improve
4. Evaluate again
5. Stop when quality is sufficient
6. Prevent infinite loops

---

## Step 1: Install dependencies

For a modern setup:

```bash
pip install langchain langgraph langchain-openai python-dotenv
```

---

# 7. Define the state

Using `TypedDict`:

```python
from typing import TypedDict


class BlogState(TypedDict):
    topic: str
    draft: str
    feedback: str
    score: int
    iteration: int
```

The state represents the information flowing through the graph.

Initially:

```python
state = {
    "topic": "Machine Learning",
    "draft": "",
    "feedback": "",
    "score": 0,
    "iteration": 0
}
```

---

# 8. Create the model

For example:

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.7
)
```

Your exact available model can differ.

---

# 9. Generation node

```python
def generate(state: BlogState):

    prompt = f"""
    Write a high-quality blog post about:

    {state["topic"]}

    The blog should:
    - Have a clear introduction
    - Explain concepts accurately
    - Include examples
    - Have a logical structure
    - Be easy to understand
    """

    response = model.invoke(prompt)

    return {
        "draft": response.content,
        "iteration": state["iteration"] + 1
    }
```

The node receives the current state and returns updates.

---

# 10. Evaluation node

Now we ask another LLM call to evaluate the generated blog.

A structured output is preferable here because we don't want to parse arbitrary text.

```python
from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    score: int = Field(
        description="Quality score from 1 to 10"
    )

    feedback: str = Field(
        description="Specific improvements required"
    )
```

Create a structured evaluator:

```python
evaluator = model.with_structured_output(Evaluation)
```

Now:

```python
def evaluate(state: BlogState):

    prompt = f"""
    Evaluate the following blog post.

    Blog:
    {state["draft"]}

    Give a score from 1 to 10.

    Consider:
    - Accuracy
    - Structure
    - Clarity
    - Examples
    - Completeness
    - Readability

    Provide specific feedback for improvement.
    """

    result = evaluator.invoke(prompt)

    return {
        "score": result.score,
        "feedback": result.feedback
    }
```

Now the state might become:

```python
{
    "topic": "Machine Learning",

    "draft": "...generated blog...",

    "feedback": "The explanation of overfitting needs more examples.",

    "score": 6,

    "iteration": 1
}
```

---

# 11. Improvement node

Now use the evaluation feedback.

```python
def improve(state: BlogState):

    prompt = f"""
    Improve the following blog post.

    Current blog:
    {state["draft"]}

    Evaluation feedback:
    {state["feedback"]}

    Improve the blog while preserving good parts.

    Return only the improved blog.
    """

    response = model.invoke(prompt)

    return {
        "draft": response.content,
        "iteration": state["iteration"] + 1
    }
```

Now we have:

```text
Generate
   ↓
Evaluate
   ↓
Improve
   ↓
Evaluate
   ↓
Improve
   ↓
Evaluate
```

---

# 12. Conditional routing

We need a function that decides whether to continue.

```python
def should_continue(state: BlogState):

    if state["score"] >= 8:
        return "finish"

    if state["iteration"] >= 5:
        return "finish"

    return "improve"
```

This is extremely important.

Without a maximum iteration count, an LLM-based loop could theoretically continue indefinitely.

So a robust workflow should usually have:

```text
Quality threshold
+
Maximum iterations
```

---

# 13. Build the LangGraph

```python
from langgraph.graph import StateGraph, START, END
```

Create graph:

```python
graph = StateGraph(BlogState)
```

Add nodes:

```python
graph.add_node("generate", generate)
graph.add_node("evaluate", evaluate)
graph.add_node("improve", improve)
```

Add edges:

```python
graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
```

Now conditional routing:

```python
graph.add_conditional_edges(
    "evaluate",
    should_continue,
    {
        "improve": "improve",
        "finish": END
    }
)
```

Finally:

```python
graph.add_edge("improve", "evaluate")
```

Compile:

```python
workflow = graph.compile()
```

---

# 14. Complete flow

The resulting graph is:

```text
START
  │
  ▼
Generate
  │
  ▼
Evaluate
  │
  ├──── score >= 8 ─────→ END
  │
  └──── score < 8
            │
            ▼
         Improve
            │
            ▼
         Evaluate
            │
            └───────────────┐
                            │
                            ▼
                         Evaluate
```

Technically the loop is:

```text
evaluate
   ↓
improve
   ↓
evaluate
```

---

# 15. Running the workflow

```python
initial_state = {
    "topic": "Machine Learning",
    "draft": "",
    "feedback": "",
    "score": 0,
    "iteration": 0
}

result = workflow.invoke(initial_state)
```

Then:

```python
print(result["draft"])
print(result["score"])
print(result["iteration"])
```

You might get:

```text
Score: 9
Iterations: 3
```

Meaning:

```text
Iteration 1
Generate → Evaluate → 6

Iteration 2
Improve → Evaluate → 7

Iteration 3
Improve → Evaluate → 9

STOP
```

---

# 16. The most important concept: State

Iteration becomes much easier to understand when you understand **state**.

Imagine the first iteration:

```python
{
    "topic": "Machine Learning",
    "draft": "Draft v1",
    "feedback": "",
    "score": 0,
    "iteration": 1
}
```

After evaluation:

```python
{
    "topic": "Machine Learning",
    "draft": "Draft v1",
    "feedback": "Needs better examples",
    "score": 6,
    "iteration": 1
}
```

After improvement:

```python
{
    "topic": "Machine Learning",
    "draft": "Draft v2",
    "feedback": "Needs better examples",
    "score": 7,
    "iteration": 2
}
```

After another improvement:

```python
{
    "topic": "Machine Learning",
    "draft": "Draft v3",
    "feedback": "Looks good",
    "score": 9,
    "iteration": 3
}
```

The **state survives the transitions**.

That is one of the fundamental reasons LangGraph is useful for iterative workflows.

---

# 17. Iterative workflow isn't necessarily self-reflection

These concepts are related but not identical.

### Iteration

Means:

> Execute some part of the workflow repeatedly.

### Reflection

Means:

> Evaluate the result and use that evaluation to improve it.

Therefore:

```text
Iteration
    ↓
Repeat something
```

while:

```text
Reflection
    ↓
Evaluate
    ↓
Improve
```

A reflection workflow is usually iterative.

But an iterative workflow doesn't necessarily require reflection.

---

# 18. Example without reflection

Imagine processing documents in batches.

```text
Load batch 1
    ↓
Process
    ↓
Load batch 2
    ↓
Process
    ↓
Load batch 3
    ↓
Process
```

That's iterative processing.

There isn't necessarily an evaluator.

---

# 19. Example with reflection

```text
Generate answer
      ↓
Critique answer
      ↓
Improve answer
      ↓
Critique answer
      ↓
Improve answer
      ↓
Final answer
```

This is an **iterative reflection workflow**.

---

# 20. Iterative workflows with tools

Iterations become even more interesting when tools are involved.

For example, suppose an AI research system needs to answer:

> "What are the latest developments in LangGraph?"

The workflow might be:

```text
Question
   ↓
Search
   ↓
Analyze results
   ↓
Enough information?
   │
   ├── No → Search again
   │
   └── Yes
          ↓
       Generate
          ↓
        Finish
```

The loop might be:

```text
Search
  ↓
Analyze
  ↓
Need more information?
  ↓
Search
```

This is an iterative research workflow.

---

# 21. Iterative workflows with an LLM agent

An agent itself can be thought of as an iterative workflow:

```text
User request
     ↓
LLM decides
     ↓
Tool call
     ↓
Tool result
     ↓
LLM decides again
     ↓
Another tool
     ↓
Tool result
     ↓
LLM decides
     ↓
Final answer
```

For example:

```text
User:
"What is the weather in Kathmandu and convert
the temperature to Fahrenheit?"
```

The agent could:

```text
LLM
 ↓
weather_tool
 ↓
result
 ↓
LLM
 ↓
conversion_tool
 ↓
result
 ↓
LLM
 ↓
final answer
```

The repeated LLM → tool → LLM cycle is iterative.

---

# 22. Iterative workflows vs Agent loops

This distinction is important.

### Fixed iterative workflow

You know the workflow beforehand:

```text
Generate
 ↓
Evaluate
 ↓
Improve
 ↓
Evaluate
```

### Agentic loop

The LLM determines what to do next:

```text
LLM
 ↓
Choose action
 ↓
Tool
 ↓
Observe result
 ↓
LLM
 ↓
Choose next action
 ↓
...
```

So:

| Workflow    | Decision maker                        |
| ----------- | ------------------------------------- |
| Sequential  | Developer                             |
| Conditional | Developer-defined condition           |
| Iterative   | Developer-defined loop                |
| Agentic     | LLM/agent dynamically chooses actions |

---

# 23. Maximum iteration is extremely important

Never create an unrestricted loop like:

```python
def should_continue(state):
    return "improve"
```

because your workflow could keep running.

Instead:

```python
def should_continue(state):

    if state["score"] >= 8:
        return "finish"

    if state["iteration"] >= 5:
        return "finish"

    return "improve"
```

Now you have two stopping conditions.

### Condition 1

Quality is sufficient:

```text
score >= 8
```

### Condition 2

Maximum iterations reached:

```text
iteration >= 5
```

This is a common pattern in production workflows.

---

# 24. Better stopping conditions

Instead of only checking score, you can check multiple conditions.

For example:

```python
def should_continue(state):

    if state["score"] >= 9:
        return "finish"

    if state["iteration"] >= 5:
        return "finish"

    if state["score"] == 10:
        return "finish"

    return "improve"
```

Or:

```python
def should_continue(state):

    quality_good = state["score"] >= 8
    max_iterations = state["iteration"] >= 5

    if quality_good or max_iterations:
        return "finish"

    return "improve"
```

---

# 25. Avoiding useless iterations

There's another important issue.

Suppose:

```text
Iteration 1 → score 6
Iteration 2 → score 6
Iteration 3 → score 6
Iteration 4 → score 6
```

The model isn't improving.

We can detect this.

Add:

```python
previous_score: int
```

to state.

Then:

```python
def should_continue(state):

    if state["score"] >= 8:
        return "finish"

    if state["iteration"] >= 5:
        return "finish"

    if state["score"] <= state["previous_score"]:
        return "finish"

    return "improve"
```

However, you'd want to carefully initialize and update `previous_score`; otherwise the first iteration can be misleading.

A better production design could track:

```python
score_history: list[int]
```

For example:

```python
[6, 7, 7, 7]
```

Then stop when improvement stalls.

---

# 26. Score history

State:

```python
class BlogState(TypedDict):
    topic: str
    draft: str
    feedback: str
    score: int
    score_history: list[int]
    iteration: int
```

Evaluation:

```python
def evaluate(state):

    result = evaluator.invoke(...)

    history = state["score_history"] + [result.score]

    return {
        "score": result.score,
        "feedback": result.feedback,
        "score_history": history
    }
```

Then you can inspect:

```python
[5, 6, 7, 8]
```

This is useful for debugging and observability.

---

# 27. Iterative workflow with structured output

For production applications, I strongly recommend structured output for evaluators.

Instead of:

```text
Score: 8
Feedback: Improve examples
```

use:

```python
class Evaluation(BaseModel):
    score: int
    feedback: str
```

Then:

```python
evaluator = model.with_structured_output(Evaluation)
```

This gives you predictable data:

```python
result.score
result.feedback
```

instead of manually parsing LLM text.

---

# 28. Pydantic state

Since you've been working with Pydantic models in your LangGraph workflows, you can also model your state with a Pydantic schema where appropriate.

For example:

```python
from pydantic import BaseModel, Field


class BlogState(BaseModel):
    topic: str
    draft: str = ""
    feedback: str = ""
    score: int = 0
    iteration: int = 0
```

Then your nodes can work around that structured state representation.

However, when working with LangGraph, pay attention to the specific state schema/update semantics of the LangGraph version you're using. In many examples, `TypedDict` remains the simplest choice for graph state, while Pydantic is particularly useful for **LLM structured outputs**.

---

# 29. A more production-like architecture

A robust iterative workflow might look like:

```text
                    ┌──────────────┐
                    │    START     │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Generate   │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Validate   │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │   Evaluate   │
                    └──────┬───────┘
                           ↓
                ┌─────────────────────┐
                │ Quality acceptable? │
                └──────────┬──────────┘
                     Yes /     \ No
                       /         \
                      ↓           ↓
                   Finish      Improve
                                  │
                                  ↓
                              Validate
                                  │
                                  ↓
                              Evaluate
                                  │
                                  └────────┐
                                           │
                                           ↓
                                      Quality check
```

Notice the additional **validation** stage.

That's often preferable to blindly asking the LLM to improve itself.

---

# 30. Real-world applications

Iterative workflows are useful in many applications.

### 1. Content generation

```text
Generate
 ↓
Critique
 ↓
Improve
 ↓
Final
```

### 2. Code generation

```text
Generate code
 ↓
Run tests
 ↓
Tests pass?
 ↓
No → Fix code
 ↓
Run tests again
```

This is particularly powerful.

```text
             ┌──────────────┐
             ↓              │
Generate → Test → Failed → Fix
             │
             └── Passed → END
```

---

### 3. SQL generation

```text
Generate SQL
    ↓
Execute SQL
    ↓
Error?
  /    \
Yes     No
 ↓       ↓
Fix    Return
 ↓
Execute again
```

---

### 4. RAG

A RAG system can iteratively retrieve information:

```text
Question
 ↓
Retrieve
 ↓
Evaluate retrieved documents
 ↓
Enough?
 ├── Yes → Generate answer
 └── No → Rewrite query
             ↓
          Retrieve again
```

This is often called **iterative retrieval** or query refinement.

---

### 5. Research agent

```text
Question
 ↓
Search
 ↓
Analyze
 ↓
Missing information?
 ├── Yes → Search again
 └── No → Synthesize
```

---

### 6. Data extraction

```text
Extract
 ↓
Validate
 ↓
Invalid?
 ↓
Re-extract
 ↓
Validate
 ↓
Valid → END
```

---

# 31. Iterative workflow vs recursion

They can look similar, but conceptually:

### Recursion

A function calls itself:

```python
def process():
    ...
    process()
```

### Workflow iteration

A graph transitions back to a previous node:

```text
A → B → C
    ↑   |
    └───┘
```

LangGraph is designed around graph transitions rather than requiring you to manually implement recursion.

This makes workflow state, routing, persistence, visualization, and debugging much easier to manage.

---

# 32. Common pattern: Generate → Critique → Refine

This is one of the most useful iterative patterns.

```text
           ┌─────────────┐
           │   Generate  │
           └──────┬──────┘
                  ↓
           ┌─────────────┐
           │   Critique  │
           └──────┬──────┘
                  ↓
           ┌─────────────┐
           │   Refine    │
           └──────┬──────┘
                  │
                  └─────────────→ Critique
```

For example:

```text
Generate answer
     ↓
Critic LLM
     ↓
"Answer lacks examples"
     ↓
Generator LLM
     ↓
Improved answer
     ↓
Critic LLM
     ↓
"Good"
     ↓
END
```

---

# 33. Generator and critic can be different models

You don't necessarily need the same model.

For example:

```text
Generator
   ↓
GPT model
   ↓
Critic
   ↓
Another model
```

You could use:

```python
generator = ChatOpenAI(
    model="..."
)

critic = ChatOpenAI(
    model="..."
)
```

This can be useful because the critic has a different role.

---

# 34. Important problem: LLM self-evaluation isn't perfect

A major limitation of:

```text
LLM generates
     ↓
same LLM evaluates
     ↓
same LLM improves
```

is that the model can reinforce its own mistakes.

For example:

```text
Generate incorrect information
        ↓
LLM evaluates it
        ↓
"Looks good"
        ↓
Final answer still incorrect
```

Therefore, whenever possible, use **external validation**.

For example:

```text
Generate code
 ↓
Run unit tests
 ↓
Result
```

or:

```text
Generate SQL
 ↓
Database executes SQL
 ↓
Actual error/result
```

or:

```text
Generate answer
 ↓
Retrieve authoritative documents
 ↓
Verify claims
```

This is usually stronger than pure self-reflection.

---

# 35. Three levels of iterative workflows

You can think about iterative workflows at three levels.

### Level 1 — Simple iteration

```text
A → B → A → B
```

Example:

```text
Process → Check → Process → Check
```

---

### Level 2 — Reflection loop

```text
Generate
 ↓
Evaluate
 ↓
Improve
 ↓
Evaluate
```

---

### Level 3 — Agentic loop

```text
           ┌─────────────┐
           │     LLM     │
           └──────┬──────┘
                  ↓
             Choose action
                  ↓
                Tool
                  ↓
               Result
                  ↓
                 LLM
                  ↓
                ...
```

The third level is much more dynamic.

---
