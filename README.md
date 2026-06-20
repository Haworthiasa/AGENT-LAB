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
slides/<topic>/         # Hand-crafted Reveal.js slide decks
blogs/<topic>/          # Hand-crafted blog pages
shared/                 # Shared CSS and reusable assets
```

## Quick start

Serve locally:

```powershell
python -m http.server 8010
```

Browse:

- Transformer slides: `http://127.0.0.1:8010/slides/transformer/`
- GPT-1 blog: `http://127.0.0.1:8010/blogs/gpt-1/`

## Adding a new topic

1. Create `content/<topic>/src/slides.md` and/or `content/<topic>/src/blog.md`.
2. Add public images to `content/<topic>/assets/`.
3. Ask the agent to hand-craft `slides/<topic>/index.html` and/or
   `blogs/<topic>/index.html` from the Markdown source and your instructions.
4. Verify the pages locally.

## Notes

- `slides/transformer/index.html` is the original hand-written Reveal.js deck.
- New topics are hand-crafted from Markdown, preserving headings, LaTeX math,
  tables, and code blocks.
- Model checkpoints and other large binary artifacts should not be committed.
- `requirements.txt` is kept for optional notebook dependencies.

For the full workflow, see `WORKFLOW.md`.
