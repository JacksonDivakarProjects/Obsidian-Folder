Perfect ask, Jack — let’s make it crystal clear with **examples + explanations** for every JSON type.  
Short, direct, and visual — exactly what you need to internalize it. 👇

---

### **1️⃣ Single-line JSON**

All data in one continuous line — compact and machine-friendly.

```json
{"id":1,"name":"Jack","role":"Engineer"}
```

✅ Used for logs or network transfer where space matters.

---

### **2️⃣ Multi-line (Pretty) JSON**

Same data, but formatted neatly for humans.

```json
{
  "id": 1,
  "name": "Jack",
  "role": "Engineer"
}
```

✅ Used in configuration files, readable reports, or documentation.

---

### **3️⃣ JSON Object**

A collection of key–value pairs inside `{}`.

```json
{"city": "Chennai", "temperature": 32}
```

✅ Represents one logical record — the most common JSON structure.

---

### **4️⃣ JSON Array**

A list of items inside `[]` — can be numbers, strings, or objects.

```json
["Python", "Spark", "SQL"]
```

✅ Used when you need an ordered list of values.

---

### **5️⃣ Nested JSON**

Objects or arrays inside another object — hierarchical data.

```json
{
  "user": {
    "name": "Jack",
    "skills": ["Python", "Airflow"]
  }
}
```

✅ Common in APIs and real-world data structures.

---

### **6️⃣ Array of Objects**

Multiple records (each as an object) inside an array.

```json
[
  {"id": 1, "name": "Jack"},
  {"id": 2, "name": "Rose"}
]
```

✅ Common in APIs returning a list of users, products, etc.

---

### **7️⃣ Mixed JSON**

Combination of arrays and nested objects.

```json
{
  "status": "ok",
  "data": [{"x": 10}, {"x": 20}],
  "meta": {"count": 2}
}
```

✅ Used in complex analytical or hierarchical data outputs.

---

### **8️⃣ NDJSON (Newline Delimited JSON)**

Each line is a valid JSON object — fast for streaming large data.

```json
{"id":1,"name":"Jack"}
{"id":2,"name":"Rose"}
```

✅ Used in log files, Spark, or big data ingestion systems.

---

### **9️⃣ JSON Lines (.jsonl)**

Same as NDJSON, just the `.jsonl` extension.

```json
{"event":"login"}
{"event":"logout"}
```

✅ One JSON record per line — perfect for large sequential data.

---

### **🔟 JSON Schema**

Describes structure and rules for JSON documents.

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"}
  }
}
```

✅ Used for validating if a JSON file follows the correct format.

---

### 🧭 Quick Recap

|Type|Main Use|
|---|---|
|Single-line|Compact data transfer|
|Multi-line|Human-readable configs|
|Object|Single record|
|Array|Ordered list|
|Nested|Hierarchical data|
|Array of Objects|Collection of records|
|Mixed|Complex data|
|NDJSON / JSONL|Streaming large data|
|Schema|Validation and structure definition|

---

Would you like me to show you **how to identify each type programmatically in Python** (for example, detect whether a JSON is array-based or object-based)? It’s very useful in automation and data ingestion pipelines.

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/JSON File Format/JSON with Python|JSON with Python]]
