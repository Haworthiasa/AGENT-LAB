<div align="center">

# AGENT-LAB

Slides, blogs, code và reference materials cho Agent LAB's seminars

[Website](https://haworthiasa.github.io/AGENT-LAB/) |
[Workflow](WORKFLOW.md) |
[Issues](https://github.com/haworthiasa/AGENT-LAB/issues)

</div>

## Giới Thiệu

AGENT-LAB lưu trữ source materials (Markdown, code, papers, reference documents) và hand-crafted outputs (Reveal.js slide decks, blog HTML) phục vụ các lab sessions. Output được viết tay từ Markdown source.

## Repository Layout

```text
content/<topic>/        # Markdown source, code, papers, refs, assets
  src/                  # slides.md, blog.md
  code/                 # notebooks and scripts
  papers/               # PDF papers
  refs/                 # reference images and documents
  assets/               # public images used by slides/blogs
slides/<topic>/         # Hand-crafted Reveal.js slide decks
blogs/<topic>/          # Hand-crafted blog pages
shared/                 # Shared CSS và reusable assets
```

## Hướng Dẫn Sử Dụng

### Xem Slide và Blog

Hai cách xem nội dung đã publish:

- **GitHub Pages**: mở [webpage](https://haworthiasa.github.io/AGENT-LAB/) trên trình duyệt.
- **Local server** (recommended cho development):

```powershell
python -m http.server 8010
```

Mở trong trình duyệt:

- Transformer slides: `http://127.0.0.1:8010/slides/transformer/`
- GPT-1 blog: `http://127.0.0.1:8010/blogs/gpt-1/`

Dùng local server thay vì `file://` giúp Reveal.js, CDN assets, hash navigation và plugin behavior hoạt động ổn định hơn.

### Tìm Nội Dung

| Loại | Đường dẫn |
|---|---|
| Slide | `slides/<topic>/index.html` |
| Blog | `blogs/<topic>/index.html` |
| Source Markdown | `content/<topic>/src/slides.md` hoặc `blog.md` |
| Assets | `content/<topic>/assets/` |

## Thêm Chủ Đề Mới

1. Tạo `content/<topic>/src/slides.md` và/hoặc `content/<topic>/src/blog.md`.

2. Thêm ảnh vào `content/<topic>/assets/`.
3. Nhờ agent hand-craft `slides/<topic>/index.html` và/hoặc `blogs/<topic>/index.html` từ Markdown source và hướng dẫn.
4. Verify output local bằng local server.

## Workflow Với Agent

Gửi prompt theo mẫu:

```text
Tạo blog [topic] theo phong cách [style].
Nội dung từ content/[topic]/src/blog.md.
Yêu cầu thêm: giữ nguyên công thức toán, bảng kết quả.
```

Ví dụ:

```text
Tạo blog gpt-1 theo phong cách Anthropic Blog.
Nội dung từ content/gpt-1/src/blog.md.
```

Xem `WORKFLOW.md` để biết workflow chi tiết và quy tắc viết Markdown nguồn.

## Quy Ước

- Output là hand-crafted HTML, giữ nguyên headings, LaTeX math, tables và code blocks từ Markdown source.
- Dùng shared CSS (`shared/css/`) cho style nhất quán giữa các topic.
- Thêm CSS/JS riêng cho từng topic trong folder output nếu cần.
- Giữ changes narrowly scoped — không reformat toàn bộ deck cho small content fixes.
- Khi thay đổi diagrams, adjust SVG `viewBox` và responsive CSS để labels visible trên mọi viewport.
