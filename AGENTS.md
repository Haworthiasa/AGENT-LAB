# Repository Guidelines

## Project Structure & Module Organization

This repository is a static lecture deck for AGENT-LAB. The main source is
`index.html`, which contains the Reveal.js slide markup, CSS, inline diagrams,
and initialization script. Public slide images live in `img/`. Source/reference
materials live in `data/`, including PDFs and original image captures under
`data/img/`. Keep generated browser artifacts, local logs, and temporary files
out of commits.

## Build, Test, and Development Commands

There is no package manager or build step in this repo. Serve the deck from the
repository root when checking layout:

```powershell
python -m http.server 8010
```

Open `http://127.0.0.1:8010/` in a browser. Prefer a local server over
`file://` because Reveal.js, CDN assets, hash navigation, and plugin behavior
are closer to the deployed path.

## Coding Style & Naming Conventions

Use two-space indentation for new Markdown and match the existing four-space
indentation style in `index.html`. Keep slide sections clearly labeled with HTML
comments, for example `SLIDE 3.1: Fixed context vector`. Use descriptive
CSS class names tied to the slide concept, such as `bottleneck-svg` or
`attention-multi-svg`. Preserve Vietnamese teaching copy and prefer semantic
HTML plus self-contained SVG diagrams over external diagram generators.

## Testing Guidelines

Manual visual regression is the primary test. After edits, navigate to the
changed slide, check desktop and narrow viewport sizes, and confirm that text,
SVG labels, arrows, and callouts are not clipped or overlapping. For Reveal.js
navigation changes, verify hash navigation and vertical slide stacks. If using
Playwright, keep screenshots and `.playwright-mcp/` outputs out of commits.

## Commit & Pull Request Guidelines

The current git history is minimal and does not define a strict convention. Use
short, imperative commit subjects such as `Fix clipped Seq2Seq diagram` or
`Add Transformer recap slide`. Pull requests should describe the changed slide
range, list any added assets, and include before/after screenshots for visual
changes. Mention the local verification command and browser used.

## Agent-Specific Instructions

Keep changes narrowly scoped to the requested slide or asset. Do not reformat the
whole deck for small content fixes. When changing diagrams, adjust the SVG
`viewBox` and responsive CSS together so labels remain visible across viewports.
