You're correct. In the **modern LangChain (v1.x)** ecosystem, **`hub` is no longer part of the primary workflow**. The `langchain.hub` module is deprecated, and LangChain recommends using the **LangSmith SDK** directly for prompt management. ([Docs by LangChain][1])

## Modern way: Use `langsmith.Client`

### 1. Install

```bash
pip install -U langsmith
```

### 2. Set your API key

```bash
LANGSMITH_API_KEY=lsv2_xxxxxxxxx
```

### 3. Pull a prompt

```python
from langsmith import Client

client = Client()

prompt = client.pull_prompt("owner/prompt_name")
```

Or if it's your own prompt:

```python
prompt = client.pull_prompt("my_prompt")
```

---

## Use it with an LLM

```python
from langsmith import Client
from langchain_openai import ChatOpenAI

client = Client()

prompt = client.pull_prompt("owner/my_prompt")

llm = ChatOpenAI(model="gpt-4.1-mini")

chain = prompt | llm

response = chain.invoke(
    {
        "topic": "LangChain"
    }
)

print(response.content)
```

---

# Pull the prompt **with the model**

If you saved a model configuration along with the prompt in LangSmith:

```python
from langsmith import Client

client = Client()

chain = client.pull_prompt(
    "owner/my_prompt",
    include_model=True
)

response = chain.invoke(
    {
        "topic": "Python"
    }
)
```

Now the returned object is already a runnable chain:

```text
Prompt
      │
      ▼
Model
```

No need to create `ChatOpenAI()` yourself. ([Docs by LangChain][1])

---

# What happened to `langchain.hub`?

Older tutorials use:

```python
from langchain import hub

prompt = hub.pull("hwchase17/react")
```

This still exists in some compatibility packages, but it is **deprecated**. The LangChain documentation explicitly recommends using the LangSmith SDK (`Client.pull_prompt`) for prompt management going forward. ([Docs by LangChain][1])

---

# Can I use a pulled prompt with `create_agent()`?

This is an important distinction.

```python
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are helpful."
)
```

Notice there is **no `prompt=` parameter**.

So you **cannot directly pass**:

```python
prompt = client.pull_prompt(...)
```

into `create_agent()`.

Instead:

* Use pulled prompts with **LCEL/Runnable chains** (`prompt | llm`)
* Or extract the system message from the prompt if you only need the instructions
* Or build a custom LangGraph if you need complete control over the agent's prompting

---

## Summary

| Old (Deprecated)            | Modern (Recommended)           |
| --------------------------- | ------------------------------ |
| `from langchain import hub` | `from langsmith import Client` |
| `hub.pull()`                | `client.pull_prompt()`         |
| `hub.push()`                | `client.push_prompt()`         |
| `langchainhub` package      | `langsmith` package            |

If you're following older LangChain tutorials (especially those using `hub.pull("hwchase17/react")`), I can also show you **how to migrate each old `hub` example to the new LangChain v1 + LangSmith API**, including ReAct agents, RAG prompts, and structured output.

[1]: https://docs.langchain.com/langsmith/manage-prompts-programmatically?utm_source=chatgpt.com "Manage prompts programmatically - Docs by LangChain"


LangSmith has evolved far beyond being just "the place where traces are stored." Today it is the **development platform for LLM applications**. The four biggest pillars are:

```text
                LangSmith

        ┌─────────┬──────────┬──────────┬───────────┐
        │         │          │          │
    Prompt Hub  Playground  Observability  Evaluation
        │         │          │          │
        └─────────┴──────────┴──────────┘
                     │
               Deployment Support
```

The Prompt Hub is only one part of the ecosystem. ([Docs by LangChain][1])

---

# 1. Prompt Hub

Think of Prompt Hub as GitHub for prompts.

Instead of

```python
SYSTEM_PROMPT = """
You are...
"""
```

inside your code, you store it in LangSmith.

Benefits:

* Version history
* Collaboration
* Rollback
* Production deployment
* Public sharing
* Tags
* Commit history

---

## Creating a Prompt

### UI

Go to

```text
LangSmith

↓

Prompts

↓

New Prompt
```

Add messages:

```text
System:
You are a helpful Python tutor.

User:
{question}
```

Save it as

```text
python-tutor
```

Every save creates a **new commit**. ([Docs by LangChain][2])

---

## Creating Programmatically

```python
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate

client = Client()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful Python tutor."),
        ("human", "{question}")
    ]
)

client.push_prompt(
    "python-tutor",
    object=prompt
)
```

This creates or updates a versioned prompt. ([Docs by LangChain][3])

---

# 2. Pulling Prompts

Instead of writing prompts in Python:

```python
prompt = ChatPromptTemplate(...)
```

pull them:

```python
from langsmith import Client

client = Client()

prompt = client.pull_prompt("python-tutor")
```

Now use it like any prompt:

```python
chain = prompt | llm

response = chain.invoke(
    {
        "question": "Explain generators."
    }
)
```

---

# 3. Prompt Variables

Example

```text
System:
You are a travel guide.

User:
Plan a trip to {country} for {days} days.
```

Invocation

```python
response = chain.invoke(
    {
        "country": "Japan",
        "days": 7
    }
)
```

LangSmith replaces

```text
{country}

↓

Japan
```

---

# 4. Include the Model

Normally

```python
prompt = client.pull_prompt("python-tutor")

llm = ChatOpenAI(...)

chain = prompt | llm
```

But if you saved the model together with the prompt:

```python
chain = client.pull_prompt(
    "python-tutor",
    include_model=True
)

response = chain.invoke(
    {
        "question": "Explain decorators."
    }
)
```

The returned object already includes the model configuration. ([Docs by LangChain][3])

---

# 5. Prompt Versioning

Every save creates a commit.

```text
Commit A

↓

Commit B

↓

Commit C

↓

Commit D
```

Suppose Commit C performs best.

You can load exactly that version:

```python
prompt = client.pull_prompt(
    "python-tutor:abcdef12"
)
```

or use a tag:

```python
prompt = client.pull_prompt(
    "python-tutor:production"
)
```

Tags provide stable references while allowing you to update which commit they point to. ([Docs by LangChain][4])

---

# 6. Prompt Tags

Example

```text
v1

v2

v3

Production

Staging

Experimental
```

Production code:

```python
prompt = client.pull_prompt(
    "python-tutor:production"
)
```

If you improve the prompt:

```text
Production

↓

Move tag

↓

New version
```

No code changes are required.

---

# 7. Environments

LangSmith supports deployment environments.

```text
Development

↓

Staging

↓

Production
```

Instead of hardcoding prompt versions.

Promote

```text
Commit 45

↓

Production
```

Rollback

```text
Commit 41

↓

Production
```

No redeployment is needed. ([Docs by LangChain][4])

---

# 8. Playground

This is one of the most useful features.

You can interactively test prompts.

```text
Prompt

↓

Choose Model

↓

Temperature

↓

Tools

↓

Output

↓

Compare
```

The Playground lets you iterate quickly before moving prompts into production. ([Docs by LangChain][2])

---

# 9. Public Prompt Hub

Browse prompts created by the community.

Examples include:

* Summarization
* SQL generation
* RAG
* Classification
* Extraction
* Translation

You can:

* Fork
* Edit
* Version
* Reuse

```python
prompt = client.pull_prompt(
    "author/prompt-name"
)
```

Public prompts are community-contributed, so review them before using them in production. ([Docs by LangChain][4])

---

# 10. Prompt Metadata

You can add:

```text
Description

README

Tags

Owner

Visibility
```

This makes prompts easier to discover and maintain within a team. ([Docs by LangChain][2])

---

# 11. Prompt Comparison

Suppose you have

```text
Prompt V1

↓

80%

Prompt V2

↓

90%
```

You can compare outputs side by side in the UI.

This is much easier than copying prompts into separate files.

---

# 12. Observability (Tracing)

This is LangSmith's original feature.

Every run is automatically recorded.

```text
User

↓

Prompt

↓

LLM

↓

Tool

↓

Retriever

↓

LLM

↓

Answer
```

You can inspect:

* Every prompt
* Every token
* Tool calls
* Latency
* Cost
* Errors

---

# 13. Run Tree

Example

```text
Agent

├── Search Tool

├── Weather Tool

└── Final Answer
```

Click any node to inspect:

* Input
* Output
* Runtime
* Token usage

---

# 14. Datasets

Datasets store evaluation examples.

Example

```text
Question

Expected Answer

Difficulty
```

Example rows

```text
What is Python?

↓

Programming language

--------------

Capital of Nepal?

↓

Kathmandu
```

Datasets power automated evaluation workflows.

---

# 15. Evaluation

Imagine

100 questions.

You update the prompt.

Instead of manually testing:

```text
Prompt V1

↓

100 Questions

↓

Accuracy
```

and

```text
Prompt V2

↓

100 Questions

↓

Accuracy
```

LangSmith can compare versions automatically using evaluators and datasets. This is one of its strongest capabilities for production AI systems.

---

# 16. Annotation Queues

For tasks that require humans to review outputs:

```text
LLM Output

↓

Reviewer

↓

Correct

↓

Score

↓

Feedback
```

Useful for building high-quality datasets and improving prompts over time.

---

# 17. Experiments

Compare:

```text
GPT-4.1

vs

Claude

vs

Gemini
```

or

```text
Prompt A

vs

Prompt B
```

or

```text
Temperature 0

vs

Temperature 0.7
```

using the same dataset.

---

# 18. Webhooks

Whenever a prompt changes:

```text
Prompt Updated

↓

Webhook

↓

CI/CD

↓

Deploy
```

This enables automation around prompt releases. ([Docs by LangChain][4])

---

# 19. Typical Production Workflow

```text
Developer

↓

Create Prompt

↓

Playground Testing

↓

Save

↓

Commit

↓

Tag

↓

Staging

↓

Evaluation

↓

Production

↓

Application

↓

Tracing

↓

Feedback

↓

Improve Prompt
```

---

# 20. When to Use Each Feature

| Feature           | Purpose                                           |
| ----------------- | ------------------------------------------------- |
| Prompt Hub        | Store and version prompts                         |
| Playground        | Test prompts interactively                        |
| Prompt Variables  | Reuse templates with dynamic inputs               |
| Prompt Versions   | Load specific commits                             |
| Tags              | Stable references like `production` or `staging`  |
| Environments      | Promote prompts through deployment stages         |
| Public Prompt Hub | Discover and reuse community prompts              |
| Tracing           | Debug chains and agents                           |
| Datasets          | Create benchmark examples                         |
| Evaluation        | Compare prompts, models, and application versions |
| Annotation Queues | Human review and labeling                         |
| Webhooks          | Automate workflows on prompt changes              |

## Recommended learning order

Since you're already working with modern LangChain agents, I'd learn LangSmith in this sequence:

1. **Prompt Hub** (`push_prompt`, `pull_prompt`, variables, versioning)
2. **Playground** (rapid prompt iteration)
3. **Tracing** (debugging LangChain and LangGraph applications)
4. **Datasets** (building evaluation sets)
5. **Evaluation** (automated regression testing for prompts and models)
6. **Production features** (tags, environments, webhooks, and prompt promotion)

This progression mirrors how most production AI teams adopt LangSmith, starting with prompt management and observability before moving into evaluation and deployment workflows. ([Docs by LangChain][3])

[1]: https://docs.langchain.com/langsmith/prompt-engineering?utm_source=chatgpt.com "Prompt engineering - Docs by LangChain"
[2]: https://docs.langchain.com/langsmith/create-a-prompt?utm_source=chatgpt.com "Create a prompt - Docs by LangChain"
[3]: https://docs.langchain.com/langsmith/manage-prompts-programmatically?utm_source=chatgpt.com "Manage prompts programmatically - Docs by LangChain"
[4]: https://docs.langchain.com/langsmith/manage-prompts?utm_source=chatgpt.com "Manage prompts - Docs by LangChain"
