Overview note for the AI Notes area — general LLM/Transformers concepts, Hugging Face usage, and attention mechanism deep-dives.

## 🗺️ Map of Content (auto-generated)

### Working with LLMs / Hugging Face
- [[AI Notes/AutoModel Class|AutoModel Class]] — Overview of Hugging Face `AutoModel` task-specific classes and when to use each.
- [[AI Notes/Roles and Their Purpose|Roles and Their Purpose]] — How chat-format `system`/`user`/`assistant` roles are structured and converted into a model prompt.

### Attention Mechanism (Encoder-Decoder Sequential Models)
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism High Level Example|Attention Mechanism High Level Example]] — High-level, math-free intuition for why attention removes the fixed-context bottleneck.
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Implementation (Old Sequential Model)|Attention Mechanism Implementation (Old Sequential Model)]] — Worked numeric example of computing context vector `c` and decoder state `s` via attention weights.
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Part 2 Notes|Attention Mechanism Part 2 Notes]] — Maps the `c`, `h`, `s` symbols onto the Query/Key/Value attention framework.

### Transformers
- [[AI Notes/Attention/Transformers/Difference between Encoder - Decoder and Transformers|Difference between Encoder - Decoder and Transformers]] — Contrasts RNN/LSTM encoder-decoder attention with the fully parallel Transformer architecture.

### Common Questions / Training Issues
- [[AI Notes/Attention/Common Questions/Exploding Gradients|Exploding Gradients]] — Causes and fixes for exploding gradients in deep/recurrent networks.
- [[AI Notes/Attention/Common Questions/Vanishing Gradients|Vanishing Gradients]] — Causes of vanishing gradients in deep/recurrent networks and why early layers stop learning.
