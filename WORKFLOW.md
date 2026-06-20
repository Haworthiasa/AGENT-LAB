# Workflow: Từ Markdown đến Slide / Blog

Tài liệu này mô tả workflow thủ công: bạn viết Markdown + chỉ dẫn, agent đọc
và viết tay HTML cho slide/blog.

> Không còn `build.py` hay script tự động nào. Mọi output đều được viết tay.

## Môi trường

Không cần cài đặt gì để xem slide/blog. Chỉ cần Python để chạy local server:

```powershell
python -m http.server 8010
```

Nếu sau này bạn muốn chạy notebook, có thể cài các thư viện trong
`requirements.txt`:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Workflow thủ công

```
Bạn
├── Viết content/<topic>/src/slides.md
├── Viết content/<topic>/src/blog.md
├── Đặt ảnh vào content/<topic>/assets/
└── Gửi chỉ dẫn cho agent (trực tiếp trong message)

Agent
├── Đọc Markdown nguồn
├── Viết tay slides/<topic>/index.html
├── Viết tay blogs/<topic>/index.html
├── Copy ảnh sang output folders
└── Serve + kiểm tra visual
```

## Cách yêu cầu agent

Gửi message theo mẫu:

```text
Tạo blog [tên-chủ-đề] theo phong cách [tên-phong-cách].
Nội dung từ content/[tên-chủ-đề]/src/blog.md.
Yêu cầu thêm: ...
```

Ví dụ:

```text
Tạo blog gpt-1 theo phong cách Anthropic Blog.
Nội dung từ content/gpt-1/src/blog.md.
Giữ nguyên công thức toán và bảng kết quả.
```

## Quy tắc viết Markdown nguồn

| Thành phần | Cú pháp |
|---|---|
| Heading | `#`, `##`, `###` |
| Inline math | `$...$` |
| Display math | `$$...$$` |
| Code block | ` ```python ` hoặc ` ```bash ` |
| Hình ảnh | `![alt](assets/image.png)` |
| Bảng | Markdown table thông thường |
| Metadata | YAML frontmatter ở đầu file |

## Phong cách có sẵn

### Anthropic Blog

Tối giản, sang trọng như tờ báo in cao cấp:

- Nền: màu kem/giấy cũ `#F9F6F0`
- Chữ: màu than chì sẫm `#2D2D2D`
- Điểm nhấn: màu đỏ gạch `#A94442`
- Heading: serif (Newsreader/Georgia)
- Body: sans-serif (Inter/Arial)
- Layout: đơn cột, max-width 700px, nhiều khoảng trắng
- Bảng: chỉ đường kẻ ngang mảnh
- Code block: nền tối
- Ảnh: flat, không shadow/3D

CSS dùng chung: `shared/css/blog-anthropic.css`

## Vibe coding

Vì output là HTML viết tay, bạn có thể tùy chỉnh sâu:

1. **Viết HTML bằng tay** trong `slides/<topic>/index.html` hoặc
   `blogs/<topic>/index.html`.
2. **Dùng shared CSS** cho phong cách nhất quán (vd `blog-anthropic.css`).
3. **Thêm CSS/JS riêng cho từng topic** trong folder output nếu cần.

## Thêm chủ đề mới checklist

- [ ] Tạo `content/<topic>/src/slides.md` và/hoặc `content/<topic>/src/blog.md`
- [ ] Thêm ảnh vào `content/<topic>/assets/`
- [ ] Gửi chỉ dẫn cho agent để viết tay output
- [ ] Kiểm tra output bằng `python -m http.server 8010`
- [ ] Xác nhận LaTeX render, code highlight, ảnh load đúng
