In modern LangChain (especially v0.3+ and v1.x), `StructuredOutputParser` is no longer the recommended way to get structured outputs from LLMs.

The older pattern was:

```python
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

response_schemas = [
    ResponseSchema(name="name", description="person name"),
    ResponseSchema(name="age", description="person age")
]

parser = StructuredOutputParser.from_response_schemas(response_schemas)
```

This still exists in some versions for backward compatibility, but LangChain now strongly prefers **Pydantic models** and the model's **structured output** capabilities.

---

# Recommended Approach: Pydantic + with_structured_output()

## Step 1: Define a Pydantic Schema

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="Name of the person")
    age: int = Field(description="Age of the person")
```

---

## Step 2: Create LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)
```

---

## Step 3: Attach Structured Output

```python
structured_llm = llm.with_structured_output(Person)
```

---

## Step 4: Invoke

```python
result = structured_llm.invoke(
    "John is 25 years old."
)

print(result)
```

Output:

```python
Person(
    name='John',
    age=25
)
```

Notice that you get a **Pydantic object directly**, not raw text.

---

# Multiple Fields Example

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Product price")
    category: str = Field(description="Product category")
```

```python
structured_llm = llm.with_structured_output(Product)

result = structured_llm.invoke(
    "The iPhone 17 costs $999 and belongs to smartphones."
)

print(result)
```

Output:

```python
Product(
    name='iPhone 17',
    price=999.0,
    category='smartphones'
)
```

---

# Using TypedDict Instead of Pydantic

You can also use:

```python
from typing_extensions import TypedDict

class Person(TypedDict):
    name: str
    age: int

structured_llm = llm.with_structured_output(Person)
```

This returns a dictionary.

---

# If You Need Parsing Without Native Structured Output

For models that don't support tool/function calling, use:

```python
from langchain_core.output_parsers import JsonOutputParser
```

Example:

```python
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

parser = JsonOutputParser(pydantic_object=Person)
```

Then:

```python
chain = prompt | llm | parser
```

---

# Current LangChain Recommendation

For new projects:

```python
from pydantic import BaseModel
```

↓

```python
llm.with_structured_output(MySchema)
```

This is the approach used throughout the current LangChain documentation and works much better than the old `StructuredOutputParser + ResponseSchema` pattern because:

* Less prompt engineering
* Automatic validation
* Type safety
* Works with tool calling/function calling models
* Cleaner LCEL pipelines

So if you're learning LangChain in 2026, focus primarily on **Pydantic schemas + `with_structured_output()`**, and treat `StructuredOutputParser` as a legacy API.
