# Repository Guidelines

> For global skill orchestration and main-agent decision rules, see `~/.config/opencode/AGENTS.md`.

## Project Structure & Module Organization

This repository stores source materials and generated outputs for AGENT-LAB
slides and blogs.

```text
content/<topic>/        # Markdown source, code, papers, references, assets
  src/                  # slides.md, blog.md
  code/                 # notebooks and scripts
  papers/               # PDF papers
  refs/                 # reference documents and original images
  assets/               # public images used by generated slides/blogs
slides/<topic>/         # Generated Reveal.js slide decks
blogs/<topic>/          # Generated blog pages
shared/                 # Reusable templates, CSS, JS
tools/                  # Build scripts
```

The hand-written Transformer deck lives at `slides/transformer/index.html`.
It is kept intact; new topics should be authored in Markdown under
`content/<topic>/src/` and generated with `tools/build.py`.

## Build, Test, and Development Commands

Install build dependencies:

```powershell
pip install -r requirements.txt
```

Build all topics:

```powershell
python tools/build.py
```

Build one topic:

```powershell
python tools/build.py --topic transformer
```

Serve locally:

```powershell
python -m http.server 8010
```

Open `http://127.0.0.1:8010/slides/transformer/` for the Transformer deck, or
`http://127.0.0.1:8010/blogs/transformer/` for the generated blog.

## Coding Style & Naming Conventions

- Use two-space indentation for Markdown and YAML.
- Match the existing four-space indentation style in
  `slides/transformer/index.html` when editing that file.
- Keep slide sections clearly labeled with HTML comments, for example
  `SLIDE 3.1: Fixed context vector`.
- Use descriptive CSS class names tied to the slide concept, such as
  `bottleneck-svg` or `attention-multi-svg`.
- Preserve Vietnamese teaching copy and prefer semantic HTML plus
  self-contained SVG diagrams over external diagram generators.

## Testing Guidelines

Manual visual regression is the primary test. After edits:

1. Run `python tools/build.py --topic <topic>`.
2. Serve the repo locally.
3. Check the generated slide deck and blog in desktop and narrow viewports.
4. Confirm LaTeX formulas render, code blocks highlight, and images load.
5. Verify hash navigation and vertical slide stacks for Reveal.js decks.

Keep generated browser artifacts, local logs, and temporary files out of commits.

## Commit & Pull Request Guidelines

Use short, imperative commit subjects such as `Fix clipped Seq2Seq diagram` or
`Add Transformer recap slide`. For structural changes, use subjects like
`Reorganize content into topic-based folders`.

Pull requests should describe the changed slide/blog range, list any added
assets, and include before/after screenshots for visual changes. Mention the
local verification command and browser used.

## Agent-Specific Instructions

- Keep changes narrowly scoped to the requested topic, slide, or asset.
- Do not reformat the whole deck for small content fixes.
- Author new content in Markdown under `content/<topic>/src/` when possible.
- Run `python tools/build.py --topic <topic>` after changing Markdown source.
- When changing diagrams, adjust the SVG `viewBox` and responsive CSS together
  so labels remain visible across viewports.
- Do not commit model checkpoints or other large binary artifacts.
