#!/usr/bin/env python3
"""
Build Markdown source into Reveal.js slides and blog HTML.

Usage:
    python tools/build.py
    python tools/build.py --topic transformer
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

try:
    import markdown
    import yaml
except ImportError as exc:  # pragma: no cover
    print("Missing dependencies. Run: pip install -r requirements.txt")
    raise SystemExit(1) from exc

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
SLIDES_DIR = ROOT / "slides"
BLOGS_DIR = ROOT / "blogs"
SHARED_DIR = ROOT / "shared"
TEMPLATES_DIR = SHARED_DIR / "templates"


def parse_frontmatter(text: str):
    """Return (metadata_dict, body) from a Markdown file with YAML frontmatter."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            return meta, parts[2].strip()
    return {}, text


def md_to_html(body: str) -> str:
    """Convert Markdown body to HTML while preserving LaTeX math delimiters."""
    display_math = []
    inline_math = []

    def capture_display(m):
        display_math.append(m.group(1))
        return f"<!--MATH_DISPLAY_{len(display_math) - 1}-->"

    def capture_inline(m):
        inline_math.append(m.group(1))
        return f"<!--MATH_INLINE_{len(inline_math) - 1}-->"

    text = re.sub(r"\$\$(.+?)\$\$", capture_display, body, flags=re.DOTALL)
    text = re.sub(r"\$(.+?)\$", capture_inline, text)

    md = markdown.Markdown(extensions=["fenced_code", "tables", "toc"])
    html = md.convert(text)

    for i, eq in enumerate(display_math):
        html = html.replace(
            f"<!--MATH_DISPLAY_{i}-->", f"$${eq}$$"
        )
    for i, eq in enumerate(inline_math):
        html = html.replace(
            f"<!--MATH_INLINE_{i}-->", f"${eq}$"
        )
    return html


def split_slides(html: str) -> str:
    """Split Markdown-generated HTML into Reveal.js <section> slides."""
    if "<hr />" in html:
        parts = [p.strip() for p in html.split("<hr />")]
    else:
        parts = re.split(r"(?=<h1)", html)
        parts = [p.strip() for p in parts if p.strip()]

    sections = []
    for part in parts:
        if part:
            sections.append(f"<section>\n{part}\n</section>")
    return "\n".join(sections)


def build_topic(topic: str, force: bool = False) -> bool:
    """Build slides and blog for a single topic."""
    topic_dir = CONTENT_DIR / topic
    if not topic_dir.exists():
        print(f"Topic not found: {topic}")
        return False

    src_dir = topic_dir / "src"
    assets_dir = topic_dir / "assets"

    slides_md = src_dir / "slides.md"
    slides_out = SLIDES_DIR / topic
    slides_out.mkdir(parents=True, exist_ok=True)
    slides_html_path = slides_out / "index.html"
    if slides_md.exists():
        if slides_html_path.exists() and not force:
            print(
                f"  Skipping slides/{topic}/index.html (already exists; use --force to overwrite)"
            )
        else:
            meta, body = parse_frontmatter(slides_md.read_text(encoding="utf-8"))
            slides_html = split_slides(md_to_html(body))
            template = (TEMPLATES_DIR / "slides.html").read_text(encoding="utf-8")
            title = meta.get("title", topic)
            final = template.replace("{{title}}", title).replace("{{content}}", slides_html)
            slides_html_path.write_text(final, encoding="utf-8")
            print(f"  Built slides/{topic}/index.html")
    else:
        print(f"  No slides.md for {topic}")

    blog_md = src_dir / "blog.md"
    blog_out = BLOGS_DIR / topic
    blog_out.mkdir(parents=True, exist_ok=True)
    blog_html_path = blog_out / "index.html"
    if blog_md.exists():
        if blog_html_path.exists() and not force:
            print(
                f"  Skipping blogs/{topic}/index.html (already exists; use --force to overwrite)"
            )
        else:
            meta, body = parse_frontmatter(blog_md.read_text(encoding="utf-8"))
            blog_html = md_to_html(body)
            template = (TEMPLATES_DIR / "blog.html").read_text(encoding="utf-8")
            title = meta.get("title", topic)
            final = template.replace("{{title}}", title).replace("{{content}}", blog_html)
            blog_html_path.write_text(final, encoding="utf-8")
            print(f"  Built blogs/{topic}/index.html")
    else:
        print(f"  No blog.md for {topic}")

    if assets_dir.exists():
        for target in (slides_out, blog_out):
            dst = target / "assets"
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(assets_dir, dst)
        print(f"  Copied assets for {topic}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Build Markdown content into Reveal.js slides and blog pages."
    )
    parser.add_argument("--topic", help="Build only the specified topic")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing generated HTML files",
    )
    args = parser.parse_args()

    if args.topic:
        ok = build_topic(args.topic, force=args.force)
        sys.exit(0 if ok else 1)

    built = 0
    for topic_dir in sorted(CONTENT_DIR.iterdir()):
        if topic_dir.is_dir():
            print(f"Building topic: {topic_dir.name}")
            if build_topic(topic_dir.name, force=args.force):
                built += 1
    print(f"\nBuilt {built} topic(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
