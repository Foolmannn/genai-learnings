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

# 25. Prompt + Evaluation = Powerful Combination

This is where LangSmith becomes really useful.

Imagine:

```text
             Dataset
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
   Prompt v1 Prompt v2 Prompt v3
       │        │        │
       ▼        ▼        ▼
   Evaluator  Evaluator Evaluator
       │        │        │
       ▼        ▼        ▼
      81%      89%      85%
```

You immediately know:

```text
Prompt v2 is best
```

Then:

```text
Prompt v2
   ↓
Production
```

---

# 26. Human Feedback

Automated evaluators aren't perfect.

Sometimes humans need to review outputs.

For example:

```text
User
 ↓
AI response
 ↓
Human reviewer
 ↓
👍 Good
👎 Bad
```

Or:

```text
Score:
1 ───────── 5
```

This feedback becomes useful evaluation data.

LangSmith supports feedback collection and human annotation through annotation queues and inline feedback mechanisms. ([Docs by LangChain][2])

---

# 27. Annotation Queues

Imagine your application generated:

```text
10,000 responses
```

You don't want a human to manually inspect everything.

Instead:

```text
10,000 traces
       │
       ▼
Filter
       │
       ▼
Potentially problematic traces
       │
       ▼
Annotation Queue
       │
       ▼
Human reviewers
```

For example:

```text
confidence < 0.5
```

or:

```text
evaluator_score < 0.6
```

Then humans review those cases.

This creates a very useful:

```text
AI evaluator
      ↓
Find suspicious examples
      ↓
Human review
      ↓
Better evaluation dataset
```

---

# 28. Production Feedback Loop

This is one of the most important concepts to understand.

You start with:

```text
Initial dataset
      ↓
Offline evaluation
      ↓
Deploy
      ↓
Production
      ↓
Online evaluation
      ↓
Find failures
      ↓
Human review
      ↓
Add failures to dataset
      ↓
Offline evaluation
      ↓
Improve system
      ↓
Deploy again
```

So:

> Production becomes a source of new test cases.

LangSmith explicitly describes this as a production feedback loop: online evaluation surfaces real-world problems that can become new offline dataset examples. ([Docs by LangChain][3])

---

# 29. Dashboards

You don't want to inspect thousands of traces individually.

Dashboards allow you to see aggregate information.

For example:

```text
┌────────────────────────────────────┐
│       Production Overview           │
├────────────────────────────────────┤
│ Requests       125,432              │
│ Error Rate       1.2%               │
│ Avg Latency      2.4 sec             │
│ Avg Cost         $0.008              │
│ Quality          91%                 │
├────────────────────────────────────┤
│ Quality over time                   │
│                                    │
│ 95% ──────╮                         │
│           ╰────╮                    │
│                ╰──── 91%            │
└────────────────────────────────────┘
```

LangSmith supports charts and dashboards for monitoring and analysis. ([Docs by LangChain][5])

---

# 30. Cost Monitoring

LLM applications can become expensive quickly.

Suppose:

```text
100 requests/day
```

becomes:

```text
100,000 requests/day
```

You need to understand:

```text
Which model?
Which project?
Which user?
Which workflow?
Which prompt?
How many tokens?
How much money?
```

Tracing provides usage information that can be analyzed at application/project levels.

This is especially important when your LangGraph agent makes multiple LLM calls:

```text
User request
   │
   ├── Planner LLM      $0.002
   ├── Tool reasoning   $0.001
   ├── RAG generation   $0.004
   └── Final response   $0.003
                         ------
                         $0.010
```

At 100,000 requests:

```text
$0.010 × 100,000 = $1,000
```

Therefore, observability isn't only about quality.

It's also about **economics**.

---

# 31. Latency Monitoring

For agents, latency can come from many places.

```text
Total latency =

LLM latency
+
retrieval latency
+
tool latency
+
other LLM calls
+
network latency
```

Example trace:

```text
Agent                 4.8 sec
│
├── Planner LLM       1.2 sec
├── Vector Search     0.3 sec
├── Weather API       2.1 sec  ← bottleneck
└── Final LLM         1.2 sec
```

Without tracing:

```text
"Agent is slow."
```

With tracing:

```text
"Weather API is causing 44% of latency."
```

That's the difference between logging and observability.

---

# 32. Error Debugging

Suppose a LangGraph agent crashes.

Without LangSmith:

```text
500 Internal Server Error
```

Not very useful.

With tracing:

```text
Trace
 │
 ├── classify ✓
 │
 ├── retrieve ✓
 │
 ├── tool call ✓
 │
 └── generate ✗
       │
       └── Invalid structured output
```

Now you know exactly where the problem occurred.

---

# 33. Tags and Metadata

You can attach metadata to runs.

For example:

```python
config = {
    "metadata": {
        "user_type": "premium",
        "environment": "production",
        "version": "v2"
    },
    "tags": [
        "customer-support",
        "rag"
    ]
}
```

Then you can filter:

```text
environment = production
```

or:

```text
version = v2
```

or:

```text
user_type = premium
```

This becomes extremely useful when debugging large systems.

---

# 34. Automations

Instead of manually responding to every event:

```text
Trace
  ↓
Rule
  ↓
Action
```

For example:

```text
IF
    evaluator score < 0.5

THEN
    send webhook
```

or:

```text
IF
    specific failure occurs

THEN
    add to annotation queue
```

or:

```text
IF
    performance degrades

THEN
    trigger CI/CD workflow
```

LangSmith supports automations using rules, webhooks, and online evaluations. ([Docs by LangChain][2])

---

# 35. LangSmith + LangGraph

Since you're learning LangGraph, this is the combination I recommend focusing on.

Imagine:

```text
                 LangGraph
                     │
                     ▼
              ┌─────────────┐
              │    Agent    │
              └──────┬──────┘
                     │
             LangSmith tracing
                     │
                     ▼
             ┌─────────────┐
             │   Traces    │
             └──────┬──────┘
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   Evaluation   Monitoring   Debugging
       │            │            │
       ▼            ▼            ▼
   Experiments   Alerts       Trace UI
       │
       ▼
   Better Agent
```

---

# 36. A Real LangGraph Example

Suppose you're building:

```text
Customer Support Agent
```

with:

```text
START
 │
 ▼
Classify Question
 │
 ├── Billing ──────┐
 │                 │
 ├── Technical ────┤
 │                 ▼
 └── General ───> Retrieve
                    │
                    ▼
                   LLM
                    │
                    ▼
                  END
```

You can use LangSmith at every level.

### Tracing

See:

```text
classification
retrieval
LLM
tool calls
final response
```

### Evaluation

Measure:

```text
classification accuracy
retrieval quality
answer correctness
faithfulness
```

### Prompt experimentation

Compare:

```text
classifier prompt v1
classifier prompt v2
```

### Monitoring

Watch:

```text
latency
errors
quality
cost
```

### Alerting

```text
IF correctness < 80%
    → alert
```

### Human feedback

```text
User says:
"This answer was incorrect."

→ feedback
→ review
→ dataset
```

---

# 37. Offline vs Online Evaluation

This distinction is **very important for interviews and real projects**.

|                   | Offline           | Online                   |
| ----------------- | ----------------- | ------------------------ |
| When?             | Before deployment | Production               |
| Data              | Dataset           | Real user traces         |
| Purpose           | Test              | Monitor                  |
| Reference answers | Often available   | Usually unavailable      |
| Main concern      | Regression        | Production quality       |
| Example           | Prompt comparison | Hallucination monitoring |
| Human feedback    | Possible          | Very useful              |
| Automation        | CI/CD             | Alerts/webhooks          |

LangSmith explicitly categorizes evaluation this way. ([Docs by LangChain][1])

---

# 38. The Complete LangSmith Development Loop

This is the mental model I recommend remembering:

```text
                  ┌───────────────┐
                  │ Build Agent   │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Create Dataset│
                  └───────┬───────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Create Evaluator│
                 └────────┬────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Run Experiment│
                  └───────┬───────┘
                          │
                          ▼
                    Score Results
                          │
              ┌───────────┴───────────┐
              │                       │
           Good                     Bad
              │                       │
              ▼                       ▼
          Deploy                  Improve
                                      │
                    ┌─────────────────┼──────────────┐
                    │                 │              │
                    ▼                 ▼              ▼
                  Prompt            Model          Agent
                  change            change        logic
                    │                 │              │
                    └─────────────────┼──────────────┘
                                      │
                                      ▼
                              Run Experiment
                                      │
                                      ▼
                                   Deploy
                                      │
                                      ▼
                              Production Traces
                                      │
                 ┌────────────────────┼──────────────────┐
                 │                    │                  │
                 ▼                    ▼                  ▼
             Monitoring           Online Eval        Feedback
                 │                    │                  │
                 └────────────────────┼──────────────────┘
                                      │
                                      ▼
                                   Alerts
                                      │
                                      ▼
                              Find Production
                                  Failures
                                      │
                                      ▼
                              Add to Dataset
                                      │
                                      └──────► Repeat
```

That loop is arguably the most important thing to understand about LangSmith.

---

# 39. LangSmith in a production architecture

A realistic architecture could look like:

```text
                    User
                     │
                     ▼
               Next.js / API
                     │
                     ▼
              LangGraph Agent
                     │
         ┌───────────┼─────────────┐
         │           │             │
         ▼           ▼             ▼
       LLM        Retriever       Tools
         │           │             │
         └───────────┼─────────────┘
                     │
                     ▼
                LangSmith
                     │
      ┌──────────────┼────────────────┐
      │              │                │
      ▼              ▼                ▼
   Tracing       Evaluation       Monitoring
      │              │                │
      │              ▼                ▼
      │          Experiments       Alerts
      │              │
      │              ▼
      │          Prompt testing
      │
      ▼
   Debugging
```

---

# 40. Other Important LangSmith Features

Beyond the features you specifically asked about, you should know these:

### Datasets

Your AI test suite.

### Experiments

Compare different versions.

### Feedback

Capture user/human judgments.

### Annotation queues

Send selected examples to humans.

### Dashboards

Visualize production behavior.

### Automations

React automatically to events.

### Webhooks

Connect LangSmith to external systems.

### Prompt management

Store/version prompts.

### Deployment

Deploy agent applications.

### CI/CD

Quality-gate deployments using tests and evaluations.

LangSmith's official CI/CD example combines unit/integration/end-to-end tests with offline evaluations, deployment gates, continuous monitoring, and alerting. ([Docs by LangChain][6])

---

# 41. How all the features relate

A useful way to categorize everything is:

```text
             LANGSMITH
                 │
     ┌───────────┼────────────┐
     │           │            │
     ▼           ▼            ▼
 DEVELOPMENT   TESTING     PRODUCTION
     │           │            │
     ▼           ▼            ▼
   Prompts     Datasets     Tracing
   Playground  Evaluators   Monitoring
               Experiments  Alerts
               Regression   Feedback
               Backtesting  Automations
```

Or even simpler:

```text
PROMPT
   ↓
EXPERIMENT
   ↓
EVALUATION
   ↓
DEPLOY
   ↓
TRACE
   ↓
MONITOR
   ↓
ALERT
   ↓
FEEDBACK
   ↓
DATASET
   ↓
EXPERIMENT
   ↓
...
```

---

# 42. What you should learn first

Since you're currently learning **LangGraph**, I wouldn't try to learn every LangSmith feature simultaneously.

Follow this order:

### Level 1 — Observability

Learn:

```text
Tracing
Runs
Projects
Threads
Metadata
Tags
```

Goal:

> "I can inspect exactly what my LangGraph agent did."

---

### Level 2 — Datasets

Learn:

```text
Datasets
Examples
Reference outputs
Production traces → datasets
```

Goal:

> "I have a reliable test set for my agent."

---

### Level 3 — Evaluators

Learn:

```text
Code evaluator
LLM-as-judge
Pairwise evaluator
Composite evaluator
```

Goal:

> "I can automatically measure agent quality."

---

### Level 4 — Experiments

Learn:

```text
Experiment
Baseline
Comparison
Regression
Backtesting
```

Goal:

> "I can prove whether my new agent is better."

---

### Level 5 — Prompt Engineering

Learn:

```text
Prompt versions
Prompt testing
Prompt → Dataset → Evaluation
```

Goal:

> "I can systematically improve prompts."

---

### Level 6 — Production Monitoring

Learn:

```text
Online evaluators
Dashboards
Latency
Errors
Costs
Quality metrics
```

Goal:

> "I know what my production agent is doing."

---

### Level 7 — Alerting + Automation

Learn:

```text
Rules
Alerts
Webhooks
Automations
Annotation queues
```

Goal:

> "My system can detect and react to failures automatically."

---

# 43. The most important distinction

Don't think:

> **LangSmith = place where LangGraph logs are displayed.**

Think:

> **LangSmith = lifecycle platform for developing, evaluating, debugging, deploying, and continuously improving AI applications.**

The progression is:

```text
                Build
                  ↓
               Trace
                  ↓
               Inspect
                  ↓
              Evaluate
                  ↓
             Experiment
                  ↓
              Improve
                  ↓
               Deploy
                  ↓
              Monitor
                  ↓
               Alert
                  ↓
              Feedback
                  ↓
               Dataset
                  ↓
              Evaluate
                  ↓
               Improve
```

That's the core philosophy behind LangSmith.

And importantly, LangSmith is not limited to LangGraph/LangChain; its observability and evaluation tooling supports multiple frameworks and model providers. ([Docs by LangChain][2])

### For your LangGraph learning

The next practical step I'd recommend is building **one small LangGraph agent and adding LangSmith progressively**:

```text
1. LangGraph agent
       ↓
2. LangSmith tracing
       ↓
3. Dataset with 20–50 questions
       ↓
4. Code evaluator
       ↓
5. LLM-as-judge evaluator
       ↓
6. Experiment: Agent v1 vs v2
       ↓
7. Online evaluator
       ↓
8. Dashboard
       ↓
9. Alert when quality drops
       ↓
10. Human feedback → dataset
```

That project will teach you far more than learning LangSmith's UI feature-by-feature.

[1]: https://docs.langchain.com/langsmith/evaluation?utm_source=chatgpt.com "LangSmith Evaluation - Docs by LangChain"
[2]: https://docs.langchain.com/langsmith/observability?utm_source=chatgpt.com "LangSmith Observability - Docs by LangChain"
[3]: https://docs.langchain.com/langsmith/evaluation-types?utm_source=chatgpt.com "Evaluation types - Docs by LangChain"
[4]: https://docs.langchain.com/langsmith/changelog?utm_source=chatgpt.com "LangSmith Cloud changelog - Docs by LangChain"
[5]: https://docs.langchain.com/langsmith/organization-workspace-operations?utm_source=chatgpt.com "Organization and workspace operations reference - LangChain Docs"
[6]: https://docs.langchain.com/langsmith/cicd-pipeline-example?utm_source=chatgpt.com "Implement a CI/CD pipeline using LangSmith Deployment and ..."
