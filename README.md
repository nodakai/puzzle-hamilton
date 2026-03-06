# hampuz

`hampuz` generates printable Hamilton puzzle sheets for primary school students. It produces tightly controlled A4 HTML layouts for square or rectangular checkpoint puzzles and writes output to the system temp directory by default.

## What it does

- Builds square or rectangular Hamilton puzzles with ordered checkpoints
- Supports non-closed path mode and closed circuit mode
- Renders a fixed-size printable HTML worksheet
- Optionally includes a second page with the solution path for teachers
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
uv run hampuz --size 10 --seed 42
uv run hampuz --width 8 --height 10 --checkpoints 12 --path --no-solution
uv run hampuz --width 6 --height 6 --seed 42 --circuit --output ./output/puzzle.html
uv run pytest
uv run python -m hampuz.cli --seed 42
```

## Notes

- If `--seed` is omitted, the CLI uses the current Unix timestamp in milliseconds.
- Python integers do not overflow at ordinary Unix millisecond values, so this seed format is safe here.
- The HTML is intentionally not fluid; it targets predictable print output on A4 paper.
- `--size 10` is shorthand for a `10 x 10` board.
- In non-closed path mode, checkpoint `1` begins the path and the last checkpoint ends it.
- In `--circuit` mode, checkpoint `1` and the last checkpoint sit next to each other because the loop closes there.
- The generator currently allows boards up to 144 cells.
- If you add dependencies, update `requirements.in` first and regenerate `requirements.txt` with `uv pip compile`.
