JSON itself only defines six data *types* at the value level: **object**, **array**, **string**, **number**, **boolean**, and **null**. What people usually mean by "types of JSON" in practice, though, is the different **document shapes / delivery formats** built out of those values. This note catalogs the shapes you'll actually run into day to day, especially in data engineering pipelines.

---

## 1. Single-line (Minified) JSON

All data on one continuous line — compact and machine-friendly, with no extra whitespace.

```json
{"id":1,"name":"Jack","role":"Engineer"}
```

Used for logs, API payloads, or anywhere network/storage space matters.

## 2. Multi-line (Pretty-Printed) JSON

The same data, formatted with indentation for humans to read.

```json
{
  "id": 1,
  "name": "Jack",
  "role": "Engineer"
}
```

Used in configuration files, readable reports, or documentation. Produced by tools like `json.dumps(data, indent=4)`.

## 3. JSON Object

A collection of key-value pairs inside `{}`.

```json
{"city": "Chennai", "temperature": 32}
```

Represents one logical record — the most common top-level JSON structure.

## 4. JSON Array

An ordered list of values inside `[]` — items can be numbers, strings, objects, or a mix.

```json
["Python", "Spark", "SQL"]
```

Used whenever you need an ordered collection rather than a single record.

## 5. Nested JSON

Objects or arrays embedded inside another object — hierarchical data.

```json
{
  "user": {
    "name": "Jack",
    "skills": ["Python", "Airflow"]
  }
}
```

Very common in API responses and real-world data structures. This is exactly the shape `pandas.json_normalize()` is built to flatten (see [[Data Engineering Role Notes/Data Engineering Concepts/JSON File Format/JSON with Python|JSON with Python]]).

## 6. Array of Objects

Multiple records, each its own object, collected into an array.

```json
[
  {"id": 1, "name": "Jack"},
  {"id": 2, "name": "Rose"}
]
```

The typical shape of an API endpoint that returns a list of users, products, orders, etc.

## 7. Mixed JSON

A combination of nested objects and arrays at different levels of the same document.

```json
{
  "status": "ok",
  "data": [{"x": 10}, {"x": 20}],
  "meta": {"count": 2}
}
```

Common in analytical or hierarchical API outputs that bundle results together with metadata.

## 8. NDJSON (Newline-Delimited JSON)

Each line is an independent, complete JSON value (typically an object) — there's no enclosing `[ ]` array and no commas between records.

```json
{"id":1,"name":"Jack"}
{"id":2,"name":"Rose"}
```

Because each line is self-contained, NDJSON can be streamed and processed line-by-line without loading the whole file into memory first — ideal for logs, message queues, and big-data ingestion (Spark, Kafka, etc.).

## 9. JSON Lines (`.jsonl`)

The same one-record-per-line idea as NDJSON:

```json
{"event":"login"}
{"event":"logout"}
```

NDJSON and JSON Lines are near-identical in practice and often used interchangeably, but they come from two separate specs with minor differences (e.g. the [JSON Lines](https://jsonlines.org) spec requires UTF-8 encoding and disallows a leading byte-order mark, while [NDJSON](http://ndjson.org) is slightly more permissive about line endings). For day-to-day data engineering work, treat them as the same format; if you're validating strictly against one spec, check which one a tool actually implements.

## 10. JSON Schema

A JSON document that describes the *structure and rules* another JSON document must follow — field types, required fields, allowed values, etc.

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"}
  }
}
```

Used to validate that incoming JSON conforms to an expected contract — useful for catching malformed data before it enters a pipeline.

---

## Quick Recap

| Shape | Main Use |
|---|---|
| Single-line (minified) | Compact transfer/storage |
| Multi-line (pretty) | Human-readable configs |
| Object | Single record |
| Array | Ordered list of values |
| Nested | Hierarchical data |
| Array of Objects | Collection of records |
| Mixed | Complex, bundled data |
| NDJSON / JSON Lines | Streaming large datasets line-by-line |
| Schema | Validation and structure definition |

## 🔗 Related Notes
- [[Data Engineering Role Notes/Data Engineering Concepts/JSON File Format/JSON with Python|JSON with Python]]
