# LangSmith: Evaluators, Monitoring, Alerting, Prompt Experimentation & Other Features

Since you're already learning **LangGraph + LangSmith**, the most useful way to understand LangSmith is not as "just a logging dashboard", but as the **development, testing, observability, and improvement platform for LLM applications and agents**.

The overall lifecycle looks like this:

```text
                    ┌───────────────────────┐
                    │   Build Agent         │
                    │ LangChain / LangGraph │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      LangSmith        │
                    │                       │
                    │  Tracing              │
                    │  Evaluation            │
                    │  Prompt Engineering    │
                    │  Monitoring             │
                    │  Alerting               │
                    │  Feedback               │
                    │  Datasets               │
                    │  Experiments             │
                    └───────────┬───────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
       Before deployment                   After deployment
       Offline evaluation                  Online evaluation
               │                                 │
               ▼                                 ▼
        Improve model/prompt              Monitor production
               │                                 │
               └──────────────┬──────────────────┘
                              ▼
                       Better AI system
```

LangSmith officially separates evaluation into **offline evaluation** before deployment and **online evaluation** against production traffic. ([Docs by LangChain][1])

---

# 1. First: What problem does LangSmith solve?

With a normal application, you might log:

```text
Request:
"What's the weather in Kathmandu?"

Response:
"The weather is..."
```

But an AI agent can involve many operations:

```text
User
 │
 ▼
LangGraph
 │
 ├── Planner LLM
 │
 ├── Tool selection
 │      │
 │      └── Weather API
 │
 ├── Retrieved documents
 │
 ├── Another LLM
 │
 └── Final response
```

If the final answer is wrong, you need to know:

* Was the prompt bad?
* Did the LLM reason incorrectly?
* Did it select the wrong tool?
* Did the tool return bad data?
* Did retrieval return irrelevant documents?
* Did the model hallucinate?
* Did latency suddenly increase?
* Did a new prompt make the agent worse?
* Did a new model increase cost?

That's where LangSmith comes in.

---

# 2. The major LangSmith components

Think of LangSmith as having these major areas:

| Feature                | Purpose                               |
| ---------------------- | ------------------------------------- |
| **Tracing**            | See exactly what your application did |
| **Observability**      | Understand production behavior        |
| **Evaluators**         | Automatically score outputs           |
| **Datasets**           | Store test cases                      |
| **Experiments**        | Compare versions                      |
| **Prompt engineering** | Create/version/test prompts           |
| **Monitoring**         | Track production metrics              |
| **Alerting**           | Notify when something goes wrong      |
| **Feedback**           | Collect human/user judgments          |
| **Annotation queues**  | Organize human review                 |
| **Dashboards**         | Visualize application metrics         |
| **Automations**        | Trigger actions from events           |
| **Deployment**         | Deploy agent applications             |
| **CI/CD**              | Automatically test and deploy         |

LangSmith's current documentation describes observability as covering everything from individual traces to production-wide metrics, while evaluation covers datasets, evaluators, experiments, and online evaluation. ([Docs by LangChain][2])

---

# 3. Evaluators — the most important concept

An **evaluator** answers:

> "How good was this AI response?"

Suppose your chatbot generates:

```text
Question:
What is the capital of Nepal?

AI:
Kathmandu
```

An evaluator might return:

```text
score = 1
```

For:

```text
AI:
Pokhara
```

it might return:

```text
score = 0
```

But LLM applications aren't always this simple.

For example:

```text
Question:
Explain why gradient descent works.

Reference:
A mathematical explanation...

AI:
A reasonable explanation...
```

There isn't necessarily one exact string that is correct.

Therefore, LangSmith supports multiple evaluator approaches.

---

# 4. Types of Evaluators

LangSmith currently documents several evaluator styles:

```text
                    Evaluators
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Code-based       LLM-as-judge       Human
        │               │                │
        ▼               ▼                ▼
 deterministic      subjective       human judgment
```

There are also:

* Composite evaluators
* Summary evaluators
* Pairwise evaluators

([Docs by LangChain][3])

---

# 5. Code Evaluator

A **code evaluator** uses normal programming logic.

Example:

```python
def evaluate_output(run, example):
    answer = run.outputs["answer"]

    if "Kathmandu" in answer:
        return {"key": "correct", "score": 1}

    return {"key": "correct", "score": 0}
```

Conceptually:

```text
LLM output
    │
    ▼
Python function
    │
    ├── condition true  → 1
    │
    └── condition false → 0
```

### Best for

Deterministic requirements:

```text
JSON is valid?
Required field exists?
Output length < 500?
Expected tool called?
SQL generated?
Code compiles?
Response contains required information?
```

For example:

```python
def evaluate_json(run, example):
    try:
        json.loads(run.outputs["answer"])
        return {"key": "valid_json", "score": 1}
    except:
        return {"key": "valid_json", "score": 0}
```

Code evaluators are particularly useful when you need deterministic checks. ([Docs by LangChain][3])

---

# 6. LLM-as-a-Judge

This is extremely important for GenAI.

Instead of:

```text
Python:
Is answer == reference?
```

you ask another LLM:

```text
Evaluate the quality of this answer.

Question:
{question}

Reference:
{reference}

Answer:
{answer}

Score from 1 to 5.
Explain your reasoning.
```

The judge might return:

```text
Score: 4

Reason:
The answer is mostly correct but misses one important detail.
```

This is called:

> **LLM-as-a-judge**

It works well for subjective properties such as:

* correctness
* relevance
* helpfulness
* tone
* clarity
* factuality
* safety
* hallucination
* adherence to instructions

LangSmith supports LLM-as-a-judge evaluators for both offline and online evaluation. ([Docs by LangChain][3])

---

# 7. Example: RAG evaluator

Suppose you're building a RAG chatbot.

```text
User question
      │
      ▼
Retriever
      │
      ▼
Documents
      │
      ▼
LLM
      │
      ▼
Answer
```

You could evaluate:

### 1. Retrieval quality

Did we retrieve useful documents?

```text
retrieval_score = 0.85
```

### 2. Answer relevance

Does the answer actually answer the question?

```text
relevance = 0.92
```

### 3. Faithfulness

Did the model stay within the retrieved context?

```text
faithfulness = 0.88
```

### 4. Correctness

Is the final answer correct?

```text
correctness = 0.90
```

Then your experiment could look like:

| Metric       | Score |
| ------------ | ----: |
| Retrieval    |  0.85 |
| Relevance    |  0.92 |
| Faithfulness |  0.88 |
| Correctness  |  0.90 |

This is far more useful than simply asking:

> "Does my chatbot work?"

---

# 8. Composite Evaluators

Sometimes one evaluator isn't enough.

Suppose:

```text
Correctness       = 0.90
Relevance         = 0.95
Faithfulness      = 0.80
```

You could create a combined metric:

```text
overall =
    0.5 * correctness
  + 0.3 * relevance
  + 0.2 * faithfulness
```

This gives:

```text
overall = 0.895
```

LangSmith supports composite evaluators that combine multiple evaluator scores, including weighted combinations. ([Docs by LangChain][4])

This becomes useful when you want a single:

```text
AI QUALITY SCORE
```

while still preserving individual metrics.

---

# 9. Pairwise Evaluation

Another interesting technique is:

```text
Prompt
  │
  ├──── Model A ────> Answer A
  │
  └──── Model B ────> Answer B
```

Instead of asking:

```text
Score A = ?
Score B = ?
```

ask:

```text
Which answer is better?
```

Example:

```text
Answer A:
Gradient descent minimizes the loss by moving...

Answer B:
Gradient descent is an algorithm...

Judge:
A is better because it provides a more complete explanation.
```

This is called **pairwise evaluation**.

It's especially useful when comparing:

```text
GPT model A vs GPT model B
Prompt A vs Prompt B
Agent v1 vs Agent v2
RAG strategy A vs RAG strategy B
```

LangSmith specifically identifies pairwise comparison as useful when relative preference is easier to judge than absolute scoring. ([Docs by LangChain][3])

---

# 10. Summary Evaluators

Most evaluators operate at:

```text
one input
    ↓
one output
    ↓
one score
```

A summary evaluator instead looks at an entire experiment.

For example:

```text
100 test cases
      │
      ▼
Experiment
      │
      ▼
Calculate:
accuracy
precision
recall
F1
average latency
average cost
```

This gives you experiment-level metrics.

LangSmith documents summary evaluators as dataset/experiment-level evaluators rather than per-example evaluators. ([Docs by LangChain][3])

---

# 11. Datasets

Evaluators need something to test.

That's where **datasets** come in.

Imagine you create:

```text
Dataset: customer_support_v1
```

with:

```text
Input                              Expected output

"How do I reset password?"        "Go to Settings..."

"Can I get a refund?"             "Refunds are..."

"How do I change email?"          "Navigate to..."
```

This becomes your test suite.

Think of it as:

```text
LangSmith Dataset
        =
AI application's test cases
```

---

# 12. Why datasets are extremely important

Without a dataset:

```text
Change prompt
     ↓
Looks better
     ↓
Deploy
```

You don't know whether you broke something.

With a dataset:

```text
Dataset
   │
   ├── 100 examples
   │
   ▼
Prompt v1 ──> Evaluation ──> 87%
Prompt v2 ──> Evaluation ──> 91%
Prompt v3 ──> Evaluation ──> 84%
```

Now you have evidence.

---

# 13. Experiments

An **experiment** is essentially:

> Run an application/version against a dataset and measure the results.

For example:

```text
Dataset:
customer_support_v1

                    Accuracy   Relevance
Prompt v1             87%        90%
Prompt v2             91%        93%
Prompt v3             84%        89%
```

Now you know:

```text
Prompt v2 > Prompt v1 > Prompt v3
```

LangSmith's evaluation workflow explicitly uses datasets → evaluators → experiments → analysis. ([Docs by LangChain][1])

---

# 14. Offline Evaluation

Offline evaluation means:

> Test your application **before sending it to users**.

Example:

```text
                 Dataset
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Agent v1    Agent v2    Agent v3
        │           │           │
        ▼           ▼           ▼
     Evaluate    Evaluate    Evaluate
        │           │           │
        └───────────┼───────────┘
                    ▼
               Comparison
```

Useful for:

### Benchmarking

Which version performs best?

### Unit testing

Does this component work correctly?

### Regression testing

Did the latest change make performance worse?

### Backtesting

Would a new version have worked well on historical production requests?

### Pairwise comparison

Which version is better?

These are all documented offline evaluation patterns in LangSmith. ([Docs by LangChain][3])

---

# 15. Regression Testing

This is one of the most useful features for real projects.

Suppose:

```text
Version 1:
Accuracy = 92%
```

You modify your system.

```text
Version 2:
Accuracy = 84%
```

Your application might still appear to work.

But LangSmith can expose:

```text
REGRESSION

Correctness:
92% → 84%

-8%
```

This is extremely valuable for agent development because changing one prompt can unexpectedly affect many behaviors.

---

# 16. Backtesting

Suppose your production chatbot has processed:

```text
50,000 conversations
```

You want to replace:

```text
Model A
```

with:

```text
Model B
```

Instead of immediately deploying B:

```text
Historical production traces
             │
             ▼
          Dataset
             │
       ┌─────┴─────┐
       ▼           ▼
    Model A      Model B
       │           │
       ▼           ▼
   Evaluate     Evaluate
       │           │
       └─────┬─────┘
             ▼
          Compare
```

This is **backtesting**.

LangSmith specifically supports using historical production data as evaluation datasets. ([Docs by LangChain][3])

---

# 17. Tracing

Now let's move from testing to production.

Suppose your LangGraph agent is:

```text
START
 │
 ▼
classify
 │
 ▼
retrieve
 │
 ▼
generate
 │
 ▼
END
```

LangSmith can trace the execution.

Conceptually:

```text
Trace
│
├── classify
│    └── LLM call
│
├── retrieve
│    ├── embedding
│    └── vector search
│
└── generate
     └── LLM call
```

You can inspect things such as:

```text
Input
Output
Latency
Tokens
Model
Prompt
Tool calls
Errors
Metadata
Feedback
```

This is the foundation of LangSmith observability. ([Docs by LangChain][2])

---

# 18. Trace vs Run

This distinction is important.

A **run** is an individual operation.

For example:

```text
LLM call
Retriever call
Tool call
Chain
Node
```

A **trace** represents the broader execution.

For a LangGraph agent:

```text
Trace
│
├── Node: planner
│     └── LLM run
│
├── Node: tool
│     └── API run
│
└── Node: response
      └── LLM run
```

Therefore, when debugging an agent:

> Don't only inspect the final answer. Inspect the complete trace.

---

# 19. Monitoring

Monitoring asks:

> "What is happening to my application in production?"

Imagine:

```text
Your chatbot
     │
     ▼
100,000 requests
     │
     ▼
LangSmith
     │
     ├── Latency
     ├── Errors
     ├── Token usage
     ├── Cost
     ├── Quality
     ├── User feedback
     └── Evaluator scores
```

You can then monitor trends.

For example:

```text
Average latency

10 AM     1.2 sec
11 AM     1.3 sec
12 PM     1.4 sec
1 PM      4.8 sec  ← Problem
```

Or:

```text
Correctness

92%
91%
90%
89%
72%  ← Problem
```

LangSmith observability includes production-wide performance monitoring, dashboards, alerts, and online evaluations. ([Docs by LangChain][2])

---

# 20. Online Evaluation

This is different from offline evaluation.

### Offline

```text
Before deployment

Dataset
   ↓
Agent
   ↓
Evaluator
   ↓
Score
```

### Online

```text
Real user
    ↓
Production agent
    ↓
Response
    ↓
Online evaluator
    ↓
Score
```

For example:

```text
User asks question
       ↓
Agent answers
       ↓
LLM judge
       ↓
Faithfulness = 0.32
       ↓
Potential hallucination
```

Now you can investigate the actual production trace.

LangSmith supports online evaluators specifically for monitoring live production behavior and anomaly detection. ([Docs by LangChain][3])

---

# 21. Alerting

Monitoring tells you:

> Something is wrong.

Alerting tells someone:

> Something is wrong **right now**.

For example:

```text
IF
    error_rate > 5%
THEN
    send alert
```

Or:

```text
IF
    average_latency > 5 seconds
THEN
    alert
```

Or:

```text
IF
    evaluator score < 0.7
THEN
    alert
```

Conceptually:

```text
Production traces
       │
       ▼
    Rule
       │
       ├── condition false → nothing
       │
       └── condition true
                │
                ▼
             Alert
```

LangSmith has dedicated alert/rule capabilities for monitoring and automated reactions. ([Docs by LangChain][5])

---

# 22. Monitoring + Alerting Example

Imagine your RAG application normally has:

```text
Faithfulness = 92%
```

Suddenly:

```text
Faithfulness = 65%
```

You could configure:

```text
IF faithfulness < 80%
        ↓
Trigger alert
        ↓
Slack / webhook / automation
        ↓
Developer investigates
```

This is much more powerful than manually checking the LangSmith dashboard.

---

# 23. Prompt Experimentation

This is another major LangSmith capability.

Suppose your prompt is:

```text
You are a helpful AI assistant.
Answer the user's question.
```

You create:

```text
Prompt v1
```

Then:

```text
Prompt v2
```

with additional instructions:

```text
You are a helpful AI assistant.

Always:
1. Be concise.
2. Give examples.
3. Do not invent information.
```

Now test both.

```text
Dataset
   │
   ├──── Prompt v1 ────> 82%
   │
   └──── Prompt v2 ────> 91%
```

Now you have evidence that v2 performs better.

---

# 24. Prompt Versioning

Instead of keeping prompts scattered inside Python:

```python
prompt = """
You are an AI assistant...
"""
```

you can manage prompts centrally.

Conceptually:

```text
Prompt
 │
 ├── Version 1
 ├── Version 2
 ├── Version 3
 └── Version 4
```

This is useful because prompts become a **versioned engineering artifact**.

You can track:

```text
Who changed it?
What changed?
When?
Which version performed better?
```

LangSmith's current platform includes prompt resources as part of workspace development/configuration. ([Docs by LangChain][5])

---
