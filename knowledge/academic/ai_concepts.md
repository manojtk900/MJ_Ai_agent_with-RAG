# MJ AI Assistant — AI Concepts & Knowledge

## 1. Transformer Architecture
Transformers rely on the self-attention mechanism:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
This allows the model to capture long-range contextual relationships across tokens in parallel, replacing sequential recurrent neural networks (RNNs).

## 2. Parameter-Efficient Fine-Tuning (PEFT) & LoRA
Low-Rank Adaptation (LoRA) freezes the pretrained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture.
Given a weight matrix $W_0 \in \mathbb{R}^{d \times k}$, the update is constrained by representing $\Delta W = B \cdot A$, where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$ with rank $r \ll \min(d, k)$.
This drastically reduces memory footprint during fine-tuning.

## 3. Retrieval-Augmented Generation (RAG)
RAG optimizes the output of large language models by referencing an authoritative knowledge base outside of its training data sources before generating a response.
Workflow:
1. Document Ingestion & Chunking
2. Dense Vector Embedding (`all-MiniLM-L6-v2`)
3. Cosine Similarity Vector Retrieval
4. Context Grounding & Source Citation
