---
title: "Transformer — Attention Is All You Need"
topic: transformer
type: blog
date: 2026-06-20
math: katex
highlight: github
---

# Transformer — Attention Is All You Need

Bài viết này giải thích kiến trúc Transformer một cách trực quan.

## Self-Attention

Self-attention cho phép mô hình nhìn vào tất cả các token cùng lúc và tính trọng số quan hệ giữa chúng.

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

Trong đó $Q$, $K$, $V$ lần lượt là query, key và value.

## Code minh họa

```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    weights = F.softmax(scores, dim=-1)
    return torch.matmul(weights, V)
```
