Yes. The problem is most likely this part:

```python
message_chunk.content[0]['text']
```

With `stream_mode="messages"`, the streamed `message_chunk.content` is **not guaranteed to always be a list whose first element is a dictionary containing `"text"`**.

Some chunks can have:

```python
message_chunk.content == ""
```

or:

```python
message_chunk.content == "some text"
```

or content blocks with a different structure. When you do:

```python
message_chunk.content[0]
```

on an empty list/string, you get:

```text
IndexError: list index out of range
```

## The easiest fix

If your model returns normal text content, use:

```python
with st.chat_message("assistant"):
    ai_message = st.write_stream(
        message_chunk.content
        for message_chunk, metadata in chatbot.stream(
            {
                "messages": [
                    HumanMessage(content=userInput)
                ]
            },
            config={
                "configurable": {
                    "thread_id": "thread-1"
                }
            },
            stream_mode="messages"
        )
        if isinstance(message_chunk.content, str) and message_chunk.content
    )

st.session_state["message_history"].append({
    "role": "assistant",
    "content": ai_message
})
```

### Why this works

Instead of assuming:

```python
message_chunk.content[0]["text"]
```

we check:

```python
isinstance(message_chunk.content, str)
```

and:

```python
message_chunk.content
```

So if the chunk is:

```python
"Hello"
```

it streams:

```text
Hello
```

If the chunk is:

```python
" world"
```

it streams:

```text
 world
```

And if LangGraph produces an empty/non-text chunk at the end, this condition:

```python
if isinstance(message_chunk.content, str) and message_chunk.content
```

filters it out.

---

# But there's an important detail

You appear to be using a model that returns content blocks like:

```python
[
    {
        "type": "text",
        "text": "Hello"
    }
]
```

That's why you originally wrote:

```python
message_chunk.content[0]["text"]
```

If that's the case, you need to handle **both string content and list content**.

I'd recommend creating a small generator:

```python
def stream_text():
    for message_chunk, metadata in chatbot.stream(
        {
            "messages": [
                HumanMessage(content=userInput)
            ]
        },
        config={
            "configurable": {
                "thread_id": "thread-1"
            }
        },
        stream_mode="messages"
    ):
        content = message_chunk.content

        if isinstance(content, str):
            if content:
                yield content

        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text")

                    if text:
                        yield text
```

Then:

```python
with st.chat_message("assistant"):
    ai_message = st.write_stream(
        stream_text()
    )

st.session_state["message_history"].append({
    "role": "assistant",
    "content": ai_message
})
```

This is much safer.

---

# Why does the error happen at the end?

This is a very important thing to understand about LangGraph streaming.

Suppose your LLM generates:

```text
Hello
 how
 are
 you
?
```

You might expect:

```python
message_chunk.content
```

to always be:

```text
"Hello"
" how"
" are"
" you"
"?"
```

But the stream can contain other message chunks/events as well.

For example, conceptually:

```text
chunk 1 → content = "Hello"
chunk 2 → content = " how"
chunk 3 → content = " are"
chunk 4 → content = " you"
chunk 5 → content = ""
chunk 6 → metadata/event
```

Your code does:

```python
content[0]
```

on the final empty content:

```python
[][0]
```

which produces:

```text
IndexError: list index out of range
```

So **the model response itself is probably fine**. Your generator is simply assuming every streamed chunk has the same content structure.

---

# One more improvement

You can also inspect exactly what LangGraph is sending:

```python
for message_chunk, metadata in chatbot.stream(
    {
        "messages": [
            HumanMessage(content=userInput)
        ]
    },
    config={
        "configurable": {
            "thread_id": "thread-1"
        }
    },
    stream_mode="messages"
):
    print("CONTENT:", repr(message_chunk.content))
    print("METADATA:", metadata)
```

You'll probably discover something like:

```text
CONTENT: [{'type': 'text', 'text': 'Hello'}]
CONTENT: [{'type': 'text', 'text': ' world'}]
CONTENT: []
```

That last:

```python
[]
```

explains your error:

```python
message_chunk.content[0]
```

because:

```python
[][0]
```

is invalid.

---

## Best version for your Streamlit chatbot

I'd use this:

```python
def stream_text():
    for message_chunk, metadata in chatbot.stream(
        {
            "messages": [
                HumanMessage(content=userInput)
            ]
        },
        config={
            "configurable": {
                "thread_id": "thread-1"
            }
        },
        stream_mode="messages"
    ):
        content = message_chunk.content

        if isinstance(content, str):
            if content:
                yield content

        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text")

                    if text:
                        yield text


with st.chat_message("assistant"):
    ai_message = st.write_stream(stream_text())

st.session_state["message_history"].append({
    "role": "assistant",
    "content": ai_message
})
```

This handles:

```text
string content
       ↓
"Hello"

list content
       ↓
[{"type": "text", "text": "Hello"}]

empty content
       ↓
[]

other blocks
       ↓
ignored safely
```

So you won't blindly access `[0]`.

**One additional point:** if you're using the newer LangChain message-content format, you should generally prefer `.content_blocks` when you specifically want normalized content blocks, rather than assuming `.content[0]["text"]` always exists.
