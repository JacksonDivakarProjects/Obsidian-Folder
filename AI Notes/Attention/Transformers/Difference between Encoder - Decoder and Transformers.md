Here's a clear distinction between the **Transformer** and the **previous encoder-decoder models** (like RNN/LSTM with attention).

## Transformer vs. Previous Encoder-Decoder (RNN/LSTM + attention)

| Feature | Previous Model (e.g., Bahdanau et al., 2015) | Transformer (Vaswani et al., 2017) |
|---------|---------------------------------------------|-------------------------------------|
| **Core building block** | RNN (LSTM/GRU) – processes tokens sequentially | Self-attention + Feed-forward – processes all tokens in parallel |
| **Sequential processing** | Yes – hidden state depends on previous time step, cannot parallelize across sequence | No – entire sequence processed as a set, fully parallelizable |
| **Long-range dependency handling** | Partial – RNNs suffer from vanishing gradients; attention helps but still sequential | Excellent – self-attention directly connects any two positions with constant path length |
| **Attention type** | Cross-attention only (decoder attends to encoder) | Cross-attention + Self-attention in both encoder and decoder |
| **Number of attention heads** | Single head (one set of Q, K, V projections) | Multi-head (multiple parallel attention layers, concatenated) |
| **Position information** | Inherent from sequential order (time steps) | No inherent order – requires explicit **positional encoding** added to embeddings |
| **Layer structure** | RNN cells stacked | Each layer: Multi-head self-attention → FFN → Add & Norm (residual + layer norm) |
| **Memory of previous outputs** | Hidden state `s_t` (vector) | KV cache from masked self-attention (stores keys/values of all previous tokens) |
| **Training speed** | Slow – sequential processing limits GPU utilization | Fast – highly parallel, scales with GPU power |
| **Performance on long sequences** | Degrades beyond ~50–100 tokens due to bottleneck and vanishing gradients | Maintains performance for thousands of tokens (though quadratic cost limits extreme length) |

## Summary of the biggest differences

1. **No recurrence** – Transformer uses only attention and feed-forward networks.
2. **Parallel processing** – All tokens processed simultaneously during training, not one by one.
3. **Self-attention** – Both encoder and decoder use self-attention to capture intra-sequence relationships (source–source and target–target).
4. **Positional encoding** – Added to embeddings because Transformer has no built-in sense of order.
5. **Multi-head attention** – Allows the model to focus on different representational subspaces.

## One-line answer

> The Transformer replaces RNNs with **self-attention** as the primary mechanism, enabling **full parallelization** during training and much better handling of long-range dependencies, while adding **multi-head attention**, **positional encodings**, and **residual connections** with layer normalization.

## 🔗 Related Notes
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism High Level Example|Attention Mechanism High Level Example]]
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Implementation (Old Sequential Model)|Attention Mechanism Implementation (Old Sequential Model)]]
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Part 2 Notes|Attention Mechanism Part 2 Notes]]
- [[AI Notes/Attention/Common Questions/Vanishing Gradients|Vanishing Gradients]]
