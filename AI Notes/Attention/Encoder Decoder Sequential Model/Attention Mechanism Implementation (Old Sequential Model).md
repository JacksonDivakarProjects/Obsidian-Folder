Let me explain **c**, **s**, and how the **percentages (attention weights)** are determined, all in parallel with the actual words and the input/output flow.

---

## First, the Fixed Input (from Encoder)

The encoder reads the source sentence `"I love you"` and produces a **list of vectors** – one per source word. This list is fixed forever during translation.

| Source word | Encoder vector (meaning) |
|-------------|--------------------------|
| "I"         | `[5, 0, 0]`  (mostly "I" meaning) |
| "love"      | `[3, 8, 0]`  (strong "love" meaning) |
| "you"       | `[0, 4, 9]`  (strong "you" meaning) |

This list is **not** `s` or `c`. It's just the source representation.

---

## What is `s` (Decoder State)?

`s` is the **decoder's memory** of what it has already said.  
It is a **single vector** (not a list) that gets updated after each predicted word.

- `s0` = `[0,0,0]` → nothing said yet.
- `s1` = after predicting "Je" → contains memory of having said "Je".
- `s2` = after predicting "t'aime" → contains memory of having said "Je t'aime".

`s` helps the decoder decide **what to look for next** in the source sentence.

---

## What is `c` (Context Vector)?

`c` is a **weighted average** of the encoder's list.  
It is a **blend** of all source words, but some words contribute more (higher weight/percentage) than others.

`c` tells the decoder: *"Here is the part of the source sentence you should focus on right now, based on what you have already said (s)."*

---

## How the Percentages (Attention Weights) Are Determined

The decoder looks at its current memory `s` and asks: *"Which source word is most relevant to what I just said?"*

It does this by comparing `s` with each encoder vector using a simple **match score** (dot product). Higher score = more relevant.

### Step 1: `s0 = [0,0,0]`

- Compare with `"I"` (`[5,0,0]`): score = 0  
- Compare with `"love"` (`[3,8,0]`): score = 0  
- Compare with `"you"` (`[0,4,9]`): score = 0  
- 0 is 33 percent and it is same for all.
- c0 = **[ 33%, 33%, 33% ]**
All scores are equal → **equal percentages** (33%, 33%, 33%).  
So `c1` is an equal blend of all three source words.

```python 
c1 = 0.33*[5,0,0] + 0.33*[3,8,0] + 0.33*[0,4,9]
   = [1.65 + 0.99 + 0,      0 + 2.64 + 1.32,      0 + 0 + 2.97]
   = [2.64, 3.96, 2.97]   (rounded)
```

### Step 2: `s1 = [2.65, 3.96, 2.97]` (after predicting "Je")

- Compare with `"I"` (`[5,0,0]`): score = 2.65×5 = 13.25  
- Compare with `"love"` (`[3,8,0]`): score = 2.65×3 + 3.96×8 = 7.95 + 31.68 = 39.63  
- Compare For `"you"` (`[0,4,9]`): score = 3.96×4 + 2.97×9 = 15.84 + 26.73 = 42.57  

Now scores: 13.25, 39.63, 42.57.  
Convert to percentages (divide by total 95.45):  
- "I" → 14%  
- "love" → 41%  
- "you" → 45%  

So `c2` is mostly "love" and "you", little "I".

---

## How `c` and `s` Contribute to Word Selection

After computing `c` (the weighted blend), the decoder **adds** `c` to its current `s` to get the **new `s`**:

```
New s = Old s + c
```

Then the new `s` is passed through a simple output layer to predict the next word.  
That output layer has learned: *if `s` looks like this, the next French word is probably that.*

For example:
- `s1 = [2.65, 3.96, 2.97]` → output layer says "Je" (learned mapping).
- `s2 = [4.58, 9.04, 7.02]` → output layer says "t'aime".

So `c` provides the **source meaning**, and `s` accumulates **what has been said**. Together they determine the next word.

---

## Parallel with Words, Input, and Output

| Step | Decoder memory `s` (before predicting) | Attention weights (focus on source) | Context `c` (blended source meaning) | New `s` (after adding `c`) | Predicted output word |
|------|----------------------------------------|--------------------------------------|----------------------------------------|----------------------------|-----------------------|
| 1 | `[0,0,0]` (nothing said) | 33% "I", 33% "love", 33% "you" | Equal blend of all | `[2.65,3.96,2.97]` | "Je" |
| 2 | `[2.65,3.96,2.97]` (just said "Je") | 14% "I", 41% "love", 45% "you" | Mostly "love"+"you" | `[4.58,9.04,7.02]` | "t'aime" |

---

## Input and Output Sequences (Training vs. Inference)

**During training (teacher forcing):**  
- Decoder input sequence: `<SOS>`, `"Je"`, `"t'aime"` (true previous words)  
- Decoder output (prediction) sequence: `"Je"`, `"t'aime"`, `<EOS>`

**During inference (actual translation):**  
- Decoder input sequence: `<SOS>`, then its own previous predictions (`"Je"`, then `"t'aime"`)  
- Decoder output sequence: same as above.

The table above shows **inference** flow for one sentence.

---

## One-Line Summary of `c` and `s`

> `s` = decoder's memory of what it has said so far.  
> `c` = a weighted blend of source words, where the weights (percentages) come from comparing `s` with each source word.  
> The decoder adds `c` to `s` to get a new `s`, then uses that to predict the next word.

## 🔗 Related Notes
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism High Level Example|Attention Mechanism High Level Example]]
- [[AI Notes/Attention/Encoder Decoder Sequential Model/Attention Mechanism Part 2 Notes|Attention Mechanism Part 2 Notes]]
- [[AI Notes/Attention/Common Questions/Vanishing Gradients|Vanishing Gradients]]
- [[AI Notes/Attention/Common Questions/Exploding Gradients|Exploding Gradients]]
