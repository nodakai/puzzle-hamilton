# AGENTS.md

## Project purpose

This repository contains `hampuz`, a small Python project for generating printable Hamilton path puzzles for primary school students. The current output target is controlled-layout HTML sized for A4 printing.

## Working rules

- Use Python with `uv`.
- Keep dependencies minimal. Prefer the standard library unless a dependency clearly improves puzzle generation or rendering.
- Add new runtime or dev dependencies to `requirements.in`, then regenerate `requirements.txt` with `uv pip compile requirements.in -o requirements.txt`.
- Default output should remain the system temp directory joined with `hampuz` unless the user explicitly requests something else.
- Default the seed to the current Unix millisecond unless the user provides one explicitly.
- Support both `--size N` and `--width/--height` board configuration patterns.
- Support both non-closed path mode and `--circuit` mode.
- Keep the print layout stable. Avoid fluid browser-dependent sizing for the main puzzle board.
- Keep the puzzle tone suitable for primary school students.
- Use Conventional Commit style if creating commits.

## Current implementation

- Package source lives in `src/hampuz/`.
- CLI entrypoint is `hampuz`, implemented in `src/hampuz/cli.py`.
- Puzzle generation and HTML rendering live in `src/hampuz/generator.py`.
- The current generator supports configurable rectangular boards up to 144 cells, numbered checkpoints, path/circuit modes, and an optional teacher solution page.

## Expectations for future sessions

- Verify the generated HTML locally after layout changes.
- If changing puzzle rules, update both `README.md` and CLI help text.
- Do not replace fixed print sizing with responsive-only layouts unless explicitly requested.
- Preserve deterministic generation from a seed so results are reproducible.
