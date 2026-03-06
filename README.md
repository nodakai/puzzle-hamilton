# hampuz

`hampuz` generates printable Hamilton puzzle sheets for primary school students. It produces tightly controlled A4 HTML layouts for square or rectangular checkpoint puzzles and writes output to the system temp directory by default.

## What it does

- Builds square or rectangular Hamilton puzzles with ordered checkpoints
- Supports non-closed path mode and closed circuit mode
- Packs multiple games into each printed page
- Renders a fixed-size printable HTML worksheet
- Optionally includes solution pages
- Uses only the Python standard library at runtime

## Quick start

```bash
uv venv
source .venv/bin/activate
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt
uv pip install -e .
uv run hampuz
```

The command prints the output path, which defaults to:

```text
$(python -c 'import tempfile; print(tempfile.gettempdir())')/hampuz/
```

## Useful commands

```bash
uv run hampuz --size 10 --bundle 42 --pack 2
uv run hampuz --width 8 --height 10 --checkpoints 12 --path --pack 4 --games 8 --no-solution
uv run hampuz --width 6 --height 6 --bundle 42 --circuit --pack 2 --output ./output/puzzle.html
uv run pytest
uv run python -m hampuz.cli --bundle 42
```

## Notes

- If `--bundle` is omitted, the CLI uses `int(yyMMddHHmmss)`.
- `--pack 2` is the default and places two games on each page.
- If `--games` is omitted, the CLI generates as many games as the pack size.
- Each game is still derived deterministically from the bundle id and game index, but only the bundle id is shown in the output.
- The HTML is intentionally not fluid; it targets predictable print output on A4 paper.
- `--size 10` is shorthand for a `10 x 10` board.
- In non-closed path mode, checkpoint `1` begins the path and the last checkpoint ends it.
- In `--circuit` mode, checkpoint `1` and the last checkpoint sit next to each other because the loop closes there.
- The generator currently allows boards up to 144 cells.
- If you add dependencies, update `requirements.in` first and regenerate `requirements.txt` with `uv pip compile`.
