# AGENTS.md

## Project purpose

This repository is a static GitHub Pages web app for generating printable Hamilton puzzle worksheets in the browser.

## Working rules

- The browser app is the source of truth. Edit `index.html`.
- Keep the site build-free. Do not introduce a framework or bundler unless explicitly requested.
- Prefer a single self-contained `index.html` so the app works via both GitHub Pages and direct `file:` usage.
- Preserve deterministic generation from the bundle id and game index.
- Keep the printed output tightly controlled for A4 pages. Avoid fluid print layouts.
- Keep the on-screen controls simple and the print pages uncluttered.
- Keep the GitHub Pages deployment workflow working; this repo deploys from GitHub Actions.
- Use Conventional Commit style if creating commits.
- Treat translation as product writing, not word-for-word substitution.
- Keep terminology internally consistent within each locale, especially for puzzle concepts like path, circuit, start, end, and the ordered hints on the board.
- Avoid transliteration when a native-friendly activity title or puzzle term would read better to local users.
- When a direct equivalent sounds stiff or technical, prefer child-friendly wording that still preserves the puzzle rule.
- Prefer visible, classroom-natural wording when that is what children actually see on the page; for example, a locale may work better with a term like “circled numbers” than a literal equivalent of “checkpoint”.
- A locale does not need a literal equivalent of “checkpoint” at all. It may instead frame the puzzle around numbered circles, stops, marks, clues, or simply “follow 1, 2, 3...” if that reads more naturally.
- UI labels, reminder text, and solve instructions do not have to reuse the exact same noun if native speakers would prefer a lighter or more visual phrasing in one of those contexts. Aim for coherence, not rigid one-to-one wording.

## Current implementation

- `index.html` contains the UI shell, styling, puzzle generator, URL state handling, and HTML rendering.
- `.github/workflows/deploy-pages.yml` deploys the static site to GitHub Pages.
- `.nojekyll` keeps GitHub Pages in plain static-site mode.

## Expectations for future sessions

- Verify both screen layout and print layout after visual changes.
- Keep the app deployable on GitHub Pages without a build step.
- If changing query params or UI wording, update `README.md` too.
