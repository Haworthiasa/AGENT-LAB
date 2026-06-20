---
title: "Transformer — Attention Is All You Need"
topic: transformer
type: slides
date: 2026-06-20
math: katex
highlight: monokai
---

# Transformer — Attention Is All You Need

Giới thiệu kiến trúc Transformer và cơ chế Attention.

---

## Ý tưởng chính

- Bỏ qua recurrence và convolution
- Dùng **self-attention** để tính toán song song
- Công thức attention cơ bản:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

---

## Multi-Head Attention

Chia không gian embedding thành nhiều "đầu" để học nhiều biểu diễn khác nhau.

```python
import torch.nn as nn

mha = nn.MultiheadAttention(embed_dim=512, num_heads=8)
```
