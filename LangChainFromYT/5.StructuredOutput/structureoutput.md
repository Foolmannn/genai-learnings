# Structured Output in LangChain (Detailed Notes)

Structured output is a technique where an LLM returns data in a predefined format (JSON, Pydantic model, TypedDict, etc.) instead of free-form text.

Instead of getting:

```text
The movie Inception was released in 2010 and directed by Christopher Nolan.
```

You get:

```json
{
  "title": "Inception",
  "year": 2010,
  "director": "Christopher Nolan"
}
```

This makes the output:

* Predictable
* Machine-readable
* Easier to validate
* Easier to store in databases
* Easier to pass to other systems

---

# Why Structured Output?

Imagine building:

* Chatbots
* Information extraction systems
* AI Agents
* Recommendation systems
* Data pipelines

Free text is difficult to process.

Example:

```python
response = "The price is $500"
```

You must parse the text manually.

With structured output:

```python
response = {
    "price": 500
}
```

No parsing needed.

---

# How LangChain Supports Structured Output

LangChain provides several approaches:

1. Pydantic Models (Recommended)
2. TypedDict
3. JSON Schema
4. Output Parsers
5. `.with_structured_output()`

The modern approach is:

```python
.with_structured_output()
```

---

# Method 1: Using Pydantic Models

Pydantic defines the structure expected from the LLM.

Install:

```bash
pip install pydantic
```

---

## Step 1: Create Schema

```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int
    city: str
```

This tells the LLM:

```python
{
    "name": str,
    "age": int,
    "city": str
}
```

---

## Step 2: Create Model

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
```

---

## Step 3: Bind Structured Output

```python
structured_llm = llm.with_structured_output(Person)
```

Now the model knows the desired schema.

---

## Step 4: Invoke

```python
result = structured_llm.invoke(
    "John is 25 years old and lives in London."
)

print(result)
```

Output:

```python
Person(
    name='John',
    age=25,
    city='London'
)
```

Notice:

* Returned object is a Pydantic object
* Fields are validated automatically

---

# Full Example

```python
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class Person(BaseModel):
    name: str
    age: int
    city: str

llm = ChatOpenAI(model="gpt-4o-mini")

structured_llm = llm.with_structured_output(Person)

result = structured_llm.invoke(
    "Alice is 30 years old and lives in Paris."
)

print(result.name)
print(result.age)
print(result.city)
```

Output:

```python
Alice
30
Paris
```

---

# Field Descriptions

Descriptions help the model understand fields.

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(
        description="Name of the product"
    )

    price: float = Field(
        description="Product price in USD"
    )

    category: str = Field(
        description="Product category"
    )
```

---

# Optional Fields

```python
from typing import Optional

class User(BaseModel):
    name: str
    email: Optional[str] = None
```

Valid outputs:

```json
{
  "name": "John",
  "email": "john@gmail.com"
}
```

or

```json
{
  "name": "John"
}
```

---

# Lists

```python
from typing import List
from pydantic import BaseModel

class Book(BaseModel):
    title: str

class Library(BaseModel):
    books: List[Book]
```

Expected output:

```json
{
  "books": [
    {"title": "Book1"},
    {"title": "Book2"}
  ]
}
```

---

# Nested Models

```python
class Address(BaseModel):
    city: str
    country: str

class Person(BaseModel):
    name: str
    address: Address
```

Output:

```json
{
  "name": "John",
  "address": {
      "city": "London",
      "country": "UK"
  }
}
```

---

# Extracting Information

One common use case.

Schema:

```python
class Job(BaseModel):
    company: str
    position: str
    salary: int
```

Invoke:

```python
result = structured_llm.invoke(
    """
    Google is hiring a software engineer
    with a salary of $120000.
    """
)
```

Output:

```python
Job(
    company="Google",
    position="Software Engineer",
    salary=120000
)
```

---

# Multiple Objects

```python
from typing import List

class Person(BaseModel):
    name: str
    age: int

class People(BaseModel):
    persons: List[Person]
```

Input:

```text
John is 20.
Alice is 25.
Bob is 30.
```

Output:

```json
{
  "persons": [
    {
      "name":"John",
      "age":20
    },
    {
      "name":"Alice",
      "age":25
    },
    {
      "name":"Bob",
      "age":30
    }
  ]
}
```

---

# Using TypedDict

Instead of Pydantic:

```python
from typing_extensions import TypedDict

class Person(TypedDict):
    name: str
    age: int
```

```python
structured_llm = llm.with_structured_output(Person)
```

Output:

```python
{
   "name": "John",
   "age": 25
}
```

Difference:

| Pydantic      | TypedDict        |
| ------------- | ---------------- |
| Validation    | No Validation    |
| Better Schema | Simpler          |
| Object Access | Dict Access      |
| Recommended   | Less Recommended |

---

# JSON Schema

You can define schema directly.

```python
schema = {
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
}
```

```python
structured_llm = llm.with_structured_output(schema)
```

---

# Old Method: Output Parsers

Before `.with_structured_output()` became common, LangChain used output parsers.

Example:

```python
from langchain.output_parsers import PydanticOutputParser
```

Parser:

```python
parser = PydanticOutputParser(
    pydantic_object=Person
)
```

Prompt:

```python
prompt = PromptTemplate(
    template="""
    {query}

    {format_instructions}
    """,
    partial_variables={
        "format_instructions":
        parser.get_format_instructions()
    }
)
```

Then:

```python
response = chain.invoke(...)
result = parser.parse(response)
```

Still useful when a model doesn't natively support structured outputs.

---

# Under the Hood

When you do:

```python
structured_llm = llm.with_structured_output(Person)
```

LangChain typically uses one of:

1. Tool Calling
2. Function Calling
3. JSON Mode
4. Schema-Constrained Generation

depending on the model.

For example, models from [OpenAI](https://openai.com?utm_source=chatgpt.com) often use function/tool calling internally.

Conceptually:

```python
User Query
      ↓
LLM
      ↓
Tool Calling
      ↓
JSON
      ↓
Pydantic Validation
      ↓
Python Object
```

---

# Error Handling

Suppose schema:

```python
class Person(BaseModel):
    age: int
```

Model returns:

```json
{
   "age":"twenty"
}
```

Pydantic validation fails:

```python
ValidationError
```

You can catch it:

```python
try:
    result = structured_llm.invoke(query)
except Exception as e:
    print(e)
```

---

# Structured Output with LCEL

LangChain Expression Language (LCEL):

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template(
    "Extract information: {text}"
)

chain = (
    prompt
    | llm.with_structured_output(Person)
)

result = chain.invoke({
    "text": "John is 25 years old"
})
```

Flow:

```text
Prompt
   ↓
LLM
   ↓
Structured Output
   ↓
Pydantic Object
```

---

# Structured Output vs Tool Calling

| Structured Output   | Tool Calling    |
| ------------------- | --------------- |
| Returns data        | Executes tools  |
| Extract information | Perform actions |
| JSON/Pydantic       | Function calls  |
| Simpler             | More powerful   |

Structured Output:

```python
{
  "name":"John",
  "age":25
}
```

Tool Calling:

```python
search_weather(city="London")
```

---

# Real-World Use Cases

### Resume Parsing

```python
class Resume(BaseModel):
    name: str
    skills: list[str]
    experience: int
```

---

### Invoice Extraction

```python
class Invoice(BaseModel):
    invoice_number: str
    amount: float
    vendor: str
```

---

### Sentiment Analysis

```python
class Sentiment(BaseModel):
    sentiment: str
    confidence: float
```

---

### Product Extraction

```python
class Product(BaseModel):
    name: str
    price: float
```

---

# Interview/Exam Summary

**Structured Output** in LangChain forces an LLM to return data in a predefined schema rather than free text.

Key points:

* `with_structured_output()` is the modern approach.
* Pydantic is the most common schema definition method.
* Supports nested objects, lists, optional fields, and validation.
* Internally uses function/tool calling or JSON mode.
* Returns Python objects directly.
* Useful for information extraction, agents, databases, APIs, and automation pipelines.

The most common pattern you'll use in modern LangChain is:

```python
class Person(BaseModel):
    name: str
    age: int

structured_llm = llm.with_structured_output(Person)

result = structured_llm.invoke(
    "John is 25 years old"
)
```

which converts unstructured text into a validated Python object automatically.
