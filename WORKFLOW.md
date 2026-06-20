# Workflow: Từ Markdown đến Slide / Blog

Tài liệu này mô tả cách repo biến file Markdown thành slide Reveal.js và
blog HTML, cùng các tùy chọn để "vibe code" giống như Transformer deck gốc.

## Môi trường

Tạo virtual environment và cài đặt dependencies:

```powershell
# Windows
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# macOS / Linux
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` chỉ chứa các thư viện cần thiết cho `tools/build.py`:

- `markdown==3.10.2` — parser Markdown
- `pyyaml==6.0.3` — đọc YAML frontmatter

> Nếu bạn muốn chạy notebook, cần cài thêm `jupyter`, `numpy`, `torch`,
> `matplotlib`, v.v. tùy từng notebook. Các thư viện đó không nằm trong
> `requirements.txt` vì quá nặng và phụ thuộc vào từng chủ đề.

## `build.py` tạo ra cái gì?

`tools/build.py` đọc nguồn Markdown trong `content/<topic>/src/` và sinh ra:

- `slides/<topic>/index.html` — Reveal.js slide deck
- `blogs/<topic>/index.html` — blog HTML đơn giản
- `slides/<topic>/assets/` và `blogs/<topic>/assets/` — bản sao của
  `content/<topic>/assets/`

Nội dung được giữ nguyên:

- Cấu trúc heading, list, paragraph, bảng
- Công thức toán LaTeX: `$...$` và `$$...$$`
- Code block với highlight

## Workflow cơ bản

### 1. Tạo chủ đề mới

```powershell
$topic = "bert"
New-Item -ItemType Directory -Path "content\$topic\src" -Force
New-Item -ItemType Directory -Path "content\$topic\assets" -Force
```

### 2. Viết Markdown

`content/bert/src/slides.md`:

```markdown
---
title: "BERT — Pre-training of Deep Bidirectional Transformers"
topic: bert
type: slides
date: 2026-06-20
math: katex
highlight: monokai
---

# BERT

Giới thiệu kiến trúc BERT.

---

## Masked Language Model

BERT dự đoán token bị che:

$$
P(w_i \mid w_{\text{masked}}) = \text{softmax}(W h_i)
$$

```python
from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
```
```

`content/bert/src/blog.md` có cấu trúc tương tự.

### 3. Thêm ảnh

Copy ảnh công khai vào:

```powershell
Copy-Item "path\to\image.png" "content\bert\assets\image.png"
```

Trong Markdown dùng:

```markdown
![alt](assets/image.png)
```

### 4. Build

```powershell
# Build một chủ đề
python tools/build.py --topic bert

# Build tất cả chủ đề
python tools/build.py
```

### 5. Xem kết quả

```powershell
python -m http.server 8010
```

Mở trình duyệt:

- Slide: `http://127.0.0.1:8010/slides/bert/`
- Blog: `http://127.0.0.1:8010/blogs/bert/`

> Phải dùng `http://` qua local server, không mở file trực tiếp bằng
> `file://` vì Reveal.js và CDN asset sẽ bị lỗi đường dẫn.

## Quy tắc viết Markdown

| Thành phần | Cú pháp |
|---|---|
| Slide ngang | Dùng `---` trên dòng riêng |
| Heading | `#`, `##`, `###` |
| Inline math | `$...$` |
| Display math | `$$...$$` |
| Code block | ` ```python ` hoặc ` ```bash ` |
| Hình ảnh | `![alt](assets/image.png)` |
| Bảng | Markdown table thông thường |
| Metadata | YAML frontmatter ở đầu file |

## Vibe coding: tùy chỉnh như Transformer deck gốc

`build.py` tạo ra bộ slide **chuẩn hóa**. Nếu bạn muốn tùy chỉnh sâu như
deck Transformer (custom CSS, SVG inline, animation, layout phức tạp), có 4
hướng tiếp cận:

### Cách 1: Viết HTML bằng tay (giống Transformer)

Tạo file `slides/<topic>/index.html` bằng tay. `build.py` sẽ **không ghi đè**
file này trừ khi bạn dùng `--force`.

Phù hợp khi bạn muốn toàn quyền kiểm soát từng pixel như deck Transformer.

### Cách 2: Tùy chỉnh template chung

Sửa `shared/templates/slides.html` hoặc `shared/templates/blog.html` để thay
đổi CDN, font, cấu trúc HTML toàn cục.

Sửa `shared/css/custom.css` hoặc `shared/js/custom.js` để áp dụng style/script
cho tất cả slide/blog được generate.

### Cách 3: CSS/JS riêng cho từng chủ đề

Đặt file trong `content/<topic>/`:

| File | Tác dụng |
|---|---|
| `extra.css` | CSS cho cả slide và blog |
| `extra.js` | JS cho cả slide và blog |
| `slides-extra.css` | CSS chỉ cho slide |
| `slides-extra.js` | JS chỉ cho slide |
| `blog-extra.css` | CSS chỉ cho blog |
| `blog-extra.js` | JS chỉ cho blog |

`build.py` tự động copy các file này vào output và inject vào `<head>`.

Ví dụ `content/bert/extra.css`:

```css
.reveal h1 { color: #2d5bb9; }
.blog-content h2 { border-color: #2d5bb9; }
```

### Cách 4: Hybrid — generate trước, rồi vibe code sau

1. Chạy `python tools/build.py --topic <topic>` để có bộ slide/blog cơ bản.
2. Mở `slides/<topic>/index.html` hoặc `blogs/<topic>/index.html` và sửa tay.
3. Để bảo vệ bản sửa tay, đừng chạy lại `build.py` trên topic đó, hoặc chạy
   với `--force` khi bạn thực sự muốn ghi đè.

## Lưu ý quan trọng

- `build.py` chỉ tạo slide/blog từ Markdown. Nó **không thể** tự động sinh
  ra các diagram SVG phức tạp như trong Transformer deck.
- Để có diagram phức tạp, bạn cần viết HTML/SVG trực tiếp trong Markdown
  (Markdown hỗ trợ nhúng HTML) hoặc dùng Cách 1/Cách 4.
- Mỗi output folder (`slides/<topic>/`, `blogs/<topic>/`) tự chứa assets
  riêng để dễ deploy từng bài riêng lẻ.

## Thêm chủ đề mới checklist

- [ ] Tạo `content/<topic>/src/slides.md`
- [ ] Tạo `content/<topic>/src/blog.md`
- [ ] Thêm ảnh vào `content/<topic>/assets/`
- [ ] (Tùy chọn) Thêm `extra.css`, `slides-extra.css`, `blog-extra.css`, v.v.
- [ ] Chạy `python tools/build.py --topic <topic>`
- [ ] Serve bằng `python -m http.server 8010` và kiểm tra
- [ ] Kiểm tra LaTeX render, code highlight, ảnh load đúng
