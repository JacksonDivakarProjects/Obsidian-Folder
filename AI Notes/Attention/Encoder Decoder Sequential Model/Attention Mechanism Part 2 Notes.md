Great question. Let's map the symbols `c`, `h`, `s` to the **Query, Key, Value** framework clearly.

## The Standard Mapping (in basic attention)

| Symbol | Meaning | Role in Attention |
|--------|---------|-------------------|
| **h** (or `h_1...h_n`) | Encoder hidden states – one vector per source word | **Keys** and **Values** (both are the same `h` in basic attention) |
| **s** (or `s_t`) | Decoder hidden state at current time step `t` | **Query** |
| **c** (or `c_t`) | Context vector – the weighted sum produced by attention | **Output of attention** (not Q/K/V) |

## How they connect

At decoding step `t`:

1. **Query = `s_t`** (decoder's current state – "what I need right now")
2. **Keys = `h_1, h_2, ..., h_n`** (encoder states – "what each source word offers")
3. **Scores = Query · Key** = `s_t · h_i` for each `i`
4. **Weights = softmax(scores)**
5. **Values = same as Keys** = `h_1, h_2, ..., h_n` (the actual information to average)
6. **Context vector `c_t` = Σ (weight_i × Value_i)** = weighted average of all `h_i`

So:
- `s_t` (query) is used to compute attention weights over `h` (keys).
- Then `c_t` is computed using the same `h` (values).
- Finally, `c_t` is combined with `s_t` to predict the next word.

## Diagram (simplified)

```
Encoder:  h1   h2   h3   ...   hn
           ↑    ↑    ↑         ↑
        (keys/values - fixed)

Decoder:   s_t  ──┬─→ compute scores → softmax → weights
                 │
                 └───────────────────→ weighted sum → c_t
```

## One-line summary

> **`h`** = keys and values, **`s`** = query, **`c`** = the weighted sum (output of attention).

If you're using multi-head or cross-attention in Transformers, the roles are similar but with learned weight matrices for Q, K, V. Want that level next?


---

### Pareto Level (Optimal trade‑off of clarity & depth)

Now let's go one level deeper — the level where you understand **how** it works without drowning in linear algebra.

#### The problem it solves (recap)
Basic encoder‑decoder: one fixed context vector for the whole sentence → long sentences lose early information.

#### The core idea of Attention
Instead of a single vector, the encoder gives the decoder **a list of all its hidden states** — one vector per source word (or subword).  
At each decoding step, the decoder computes **a score** for each source word, indicating *how useful that word is for predicting the next target word*. Those scores are turned into **weights** (probabilities that sum to 1). Then the decoder takes a **weighted sum** of the encoder's hidden states. That weighted sum is the **context vector for this specific decoding step** — a fresh, custom‑made context that focuses on the relevant part of the source.

#### The three players: Query, Key, Value (simplified)
- **Query (Q)**: The decoder's current state (what it needs right now).  
- **Keys (K)**: Each encoder hidden state (what each source word "offers").  
- **Values (V)**: The same encoder hidden states (the actual information to be summed).

The decoder computes:  
`Score = Q · K` (dot product) for each source word → softmax → weights → `Context = sum(weights * V)`.

#### Why this is a Pareto‑level explanation
- You know the **intuition** (spotlight).
- You know the **components** (Q, K, V, weighted sum).
- You know **why** it fixes the bottleneck (dynamic context per step, no compression into one vector).
- You don't need the full matrix formulas or backprop details unless you implement it.

#### Real effect on translation
With attention, translating `"The cat, which was sleeping on the windowsill, woke up"`:
- When generating `"Le chat"` (The cat), attention focuses heavily on `"The cat"`.
- When generating `"s'est réveillé"` (woke up), attention focuses on `"woke up"` and also on `"sleeping"` (because contrast matters).
- The model keeps the whole sentence accessible at all times.

#### One‑line summary (Pareto level)
> Attention gives the decoder a **dynamic, weighted view** of the entire source sentence at every generation step, using the decoder's current state (query) to retrieve relevant source words (keys) and sum their information (values).

If you want the next level (full scaled dot‑product attention with matrices, masking, multi‑head), just ask. But this is the optimal trade‑off between simplicity and working knowledge.

## 🔗 Related Notes
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism High Level Example|Attention Mechanism High Level Example]]
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Implementation (Old Sequential Model)|Attention Mechanism Implementation (Old Sequential Model)]]
- [[AI Notes/Attention/Transformers/Difference between Encoder - Decoder and Transformers|Difference between Encoder - Decoder and Transformers]]
