## Attention Mechanism: High Level → Pareto Level (Optimal Trade-off)

You asked for two levels: a **high-level** intuition, then the **"Pareto level"** — by which I assume you mean the sweet spot: detailed enough to be useful, but not buried in every mathematical derivative. Let's go.

---

### High Level (One paragraph, no math)

Imagine you are translating a long sentence from English to French. You don't just memorize the whole sentence and then start speaking. Instead, you **look back at the original sentence** while you speak. When you say the first French word, you glance at the first few English words. When you say a later word, you look at the corresponding part of the English sentence. **Attention** does exactly that: at each step of generating the translation, the decoder looks back at **all** the encoder's hidden states and decides which source words are most relevant *right now*. It then creates a **weighted focus** (a spotlight) on those words. This completely removes the fixed‑vector bottleneck.

---


## 🔗 Related Notes
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Implementation (Old Sequential Model)|Attention Mechanism Implementation (Old Sequential Model)]]
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Part 2 Notes|Attention Mechanism Part 2 Notes]]
- [[AI Notes/Attention/Transformers/Difference between Encoder - Decoder and Transformers|Difference between Encoder - Decoder and Transformers]]
