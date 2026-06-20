# AGENT-LAB

Slides, blogs, code, papers, and reference materials for lab sessions.

## Repository layout

```text
content/<topic>/        # Markdown source and reference materials
  src/                  # slides.md, blog.md
  code/                 # notebooks and scripts
  papers/               # PDF papers
  refs/                 # reference images and documents
  assets/               # public images for generated outputs
slides/<topic>/         # Generated Reveal.js slide decks
blogs/<topic>/          # Generated blog pages
shared/                 # Templates, CSS, JS used by generated pages
tools/                  # Build scripts
```

## Quick start

Install dependencies:

```powershell
pip install -r requirements.txt
```

Build all topics:

```powershell
python tools/build.py
```

Build a single topic:

```powershell
python tools/build.py --topic transformer
```

Serve locally:

```powershell
python -m http.server 8010
```

Browse:

- Transformer slides: `http://127.0.0.1:8010/slides/transformer/`
- Transformer blog: `http://127.0.0.1:8010/blogs/transformer/`

## Adding a new topic

1. Create `content/<topic>/src/slides.md` and `content/<topic>/src/blog.md`.
2. Add public images to `content/<topic>/assets/`.
3. Run `python tools/build.py --topic <topic>`.
4. Verify the generated pages under `slides/<topic>/` and `blogs/<topic>/`.

## Notes

- `slides/transformer/index.html` is the original hand-written Reveal.js deck.
- New topics are generated from Markdown, preserving headings, LaTeX math, and
  fenced code blocks.
- Model checkpoints and other large binary artifacts should not be committed.
