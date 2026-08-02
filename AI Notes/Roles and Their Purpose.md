## What this structure is

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a short joke about saving RAM."},
]
```

This is a **chat format** used to structure input for instruction/chat models.

---

## How it works internally

The model does NOT understand this list directly.

It is converted into a **single prompt string** using a template:

```text
<|system|>
You are a helpful assistant.
<|user|>
Write a short joke about saving RAM.
<|assistant|>
```

Then:

```text
text → tokens → model → output tokens → text
```

---

## Roles and their purpose

### 1. `system`

- Sets behavior, rules, tone
    

Example:

```text
"You are a strict teacher"
"You answer only in JSON"
```

Effect:

- Global control over model behavior
    

---

### 2. `user`

- The actual input/question
    

Example:

```text
"Explain machine learning"
```

---

### 3. `assistant`

- Previous model responses (used in conversation history)
    

Example:

```python
{"role": "assistant", "content": "Machine learning is..."}
```

Used for:

- Multi-turn conversation
    
- Context continuity
    

---

## Full conversation example

```python
messages = [
    {"role": "system", "content": "You are a coding assistant."},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language."},
    {"role": "user", "content": "Give an example."}
]
```

Model sees:

- Entire history
    
- Generates next assistant response
    

---

## Types of roles (practical set)

|Role|Purpose|
|---|---|
|system|behavior control|
|user|input/query|
|assistant|previous outputs|

---

## Why this design exists

To simulate:

```text
Human ↔ AI conversation
```

Instead of:

- single prompt
    
- no context
    

---

## Important detail

- Order matters
    
- Model reads top → bottom
    
- Last message should be **user** before generation
    

---

## What happens during generation

```text
messages → formatted prompt → model predicts next tokens → assistant reply
```

---

## Final compression

- `messages` = structured conversation
    
- Roles define behavior and context
    
- Converted to prompt → then model generates next assistant response

## 🔗 Related Notes
- [[AI Notes/AutoModel Class|AutoModel Class]]
