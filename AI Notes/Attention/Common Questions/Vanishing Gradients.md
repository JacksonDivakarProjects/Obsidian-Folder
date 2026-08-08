The vanishing gradient problem occurs during backpropagation in deep neural networks, particularly when:

- **Using activation functions with small derivatives** like sigmoid or tanh, whose gradients are ≤ 0.25 (and near zero for saturated units).
- **Networks have many layers** – gradients get multiplied repeatedly, shrinking exponentially as they propagate backward.
- **Initializing weights poorly** (e.g., too small) can exacerbate the effect.
- **Training recurrent neural networks (RNNs)** on long sequences, where gradients vanish over many time steps.

In essence, it happens when the gradient becomes so tiny that earlier layers learn extremely slowly or stop learning altogether.

## 🔗 Related Notes
- [[AI Notes/Attention/Common Questions/Exploding Gradients|Exploding Gradients]]
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Implementation (Old Sequential Model)|Attention Mechanism Implementation (Old Sequential Model)]]
- [[AI Notes/Attention/Transformers/Difference between Encoder - Decoder and Transformers|Difference between Encoder - Decoder and Transformers]]
