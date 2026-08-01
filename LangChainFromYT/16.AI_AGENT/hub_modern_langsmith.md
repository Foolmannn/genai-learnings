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
