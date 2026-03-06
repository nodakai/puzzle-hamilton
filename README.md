# hampuz

`hampuz` is a static GitHub Pages app for generating printable Hamilton path and circuit worksheets directly in the browser.

## Current structure

- `index.html`: the entire app, including markup, styles, puzzle generation, UI state, and print rendering
- `.github/workflows/deploy-pages.yml`: GitHub Pages deployment workflow
- `.nojekyll`: disables Jekyll processing so the static site is served as-is

## Local use

Open the app directly:

```text
file:///.../index.html
```

No local server or build step is required.

## GitHub Pages

This repository is ready for GitHub Pages through GitHub Actions.

1. Push to `main`
2. In repository settings, configure Pages to use `GitHub Actions`
3. The included workflow deploys the repository root as the site

## App behavior

- `bundle` defaults to `int(yyMMddHHmmss)`
- Each game is derived deterministically from the bundle and its game index
- Puzzle sheets and solution sheets are both generated
- Output is tuned for controlled A4 printing
