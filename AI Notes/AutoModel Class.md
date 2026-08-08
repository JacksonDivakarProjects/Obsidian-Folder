Hugging Face provides several `AutoModel` classes, each tailored to a specific machine learning task. By choosing the right one, you ensure the model is loaded with the correct "head" (the final layers) needed to perform that task. [1, 2, 3]

## Common NLP AutoModel Classes

|AutoModel Class [2, 3, 4, 5]|Typical Task|Input $\rightarrow$ Output|
|---|---|---|
|`AutoModel`|Semantic search, embeddings|Text $\rightarrow$ Raw hidden states (vectors)|
|`AutoModelForSequenceClassification`|Sentiment analysis, spam detection|Text $\rightarrow$ A single label for the whole sentence|
|`AutoModelForTokenClassification`|Named Entity Recognition (NER), POS tagging|Text $\rightarrow$ A label for every word|
|`AutoModelForQuestionAnswering`|Extracting answers from a document|Question + Context $\rightarrow$ Start/end positions of the answer|
|`AutoModelForSeq2SeqLM`|Translation, Summarization|Text $\rightarrow$ New transformed text (e.g., T5, BART)|
|`AutoModelForMaskedLM`|Fill-in-the-blanks, pretraining|Text with `[MASK]` $\rightarrow$ The missing word (e.g., BERT, RoBERTa)|

## Beyond Text (Vision and Audio)

The "Auto" philosophy also extends to other data types through the [Hugging Face Transformers library](https://huggingface.co/docs/transformers/models): [6]

- Vision: `AutoModelForImageClassification` for identifying objects in photos or `AutoModelForObjectDetection` for finding and bounding multiple items in one image.
- Audio: `AutoModelForAudioClassification` (e.g., keyword spotting) or `AutoModelForSpeechSeq2Seq` (e.g., Speech-to-Text).
- Multimodal: Models that process both images and text simultaneously (e.g., `AutoModelForVision2Seq`). [6, 7]

## Further Exploration

- Check out the [Guide to Hugging Face AutoModel Classes](https://pub.towardsai.net/guide-to-hugging-face-automodelfor-classes-and-tokenizers-05d2a5b85210) for a detailed comparison and code examples for each NLP task.
- See the official [Auto Classes documentation](https://huggingface.co/docs/transformers/model_doc/auto) on Hugging Face for the full, technical list of all supported task wrappers.
- Explore [Vision and Audio AutoModels](https://pub.towardsai.net/part2-guide-to-huggingface-automodels-for-vision-and-audio-4b0c90f2255c) to see how these abstractions work for non-text data like pixels and sound waves. [6]

Do you have a specific task in mind, like sentiment analysis or translation, that you're trying to build?

  

[1] [https://stackoverflow.com](https://stackoverflow.com/questions/69907682/what-are-differences-between-automodelforsequenceclassification-vs-automodel)

[2] [https://pub.towardsai.net](https://pub.towardsai.net/guide-to-hugging-face-automodelfor-classes-and-tokenizers-05d2a5b85210)

[3] [https://machinelearningmastery.com](https://machinelearningmastery.com/using-auto-classes-in-the-transformers-library/)

[4] [https://pub.towardsai.net](https://pub.towardsai.net/guide-to-hugging-face-automodelfor-classes-and-tokenizers-05d2a5b85210)

[5] [https://pub.towardsai.net](https://pub.towardsai.net/guide-to-hugging-face-automodelfor-classes-and-tokenizers-05d2a5b85210)

[6] [https://pub.towardsai.net](https://pub.towardsai.net/part2-guide-to-huggingface-automodels-for-vision-and-audio-4b0c90f2255c)

[7] [https://huggingface.co](https://huggingface.co/docs/transformers/model_doc/auto#:~:text=cohere2%20%E2%80%94%20Cohere2Config%20%28Cohere2%20model%29%20cohere2_vision%20%E2%80%94,%28ColModernVBert%20model%29%20colpali%20%E2%80%94%20ColPaliConfig%20%28ColPali%20model%29)

## 🔗 Related Notes
- [[AI Notes/Roles and Their Purpose|Roles and Their Purpose]]
