from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import random
import tempfile


BOARD_SIZE = 6
DEFAULT_CHECKPOINTS = 10


@dataclass(frozen=True)
class Point:
    row: int
    col: int


@dataclass(frozen=True)
class Puzzle:
    title: str
    instructions: str
    board_size: int
    checkpoints: tuple[Point, ...]
    solution_path: tuple[Point, ...]
    seed: int


def default_output_path(seed: int) -> Path:
    return Path(tempfile.gettempdir()) / "hampuz" / f"hampuz-{seed}.html"


def build_puzzle(seed: int, board_size: int = BOARD_SIZE, checkpoint_count: int = DEFAULT_CHECKPOINTS) -> Puzzle:
    if board_size != 6:
        raise ValueError("This first version supports only a 6x6 board.")
    if not 2 <= checkpoint_count <= board_size * board_size:
        raise ValueError("checkpoint_count must fit within the board.")

    rng = random.Random(seed)
    base_path = _serpentine_path(board_size)
    transformed_path = _apply_transform(base_path, board_size, rng.randrange(8))
    checkpoints = _select_checkpoints(transformed_path, checkpoint_count)

    return Puzzle(
        title="Checkpoint Trail",
        instructions=(
            "Start at 1 and draw one continuous path through every square exactly once. "
            "Follow the numbered checkpoints in order."
        ),
        board_size=board_size,
        checkpoints=tuple(checkpoints),
        solution_path=tuple(transformed_path),
        seed=seed,
    )


def render_html(puzzle: Puzzle, include_solution: bool = True) -> str:
    board_markup = _render_board(puzzle, show_solution=False)
    solution_markup = _render_board(puzzle, show_solution=True) if include_solution else ""
    solution_page = (
        f"""
        <section class="page solution-page">
          <div class="page-header">
            <div>
              <p class="eyebrow">Teacher Copy</p>
              <h2>Solution</h2>
            </div>
            <p class="seed">Seed {puzzle.seed}</p>
          </div>
          {solution_markup}
        </section>
        """
        if include_solution
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(puzzle.title)} - Seed {puzzle.seed}</title>
  <style>
    :root {{
      --paper: #fffdf7;
      --ink: #203040;
      --accent: #e85d04;
      --accent-soft: #ffd8b1;
      --grid: #4f6d7a;
      --checkpoint: #2a9d8f;
      --checkpoint-soft: #d8f3ef;
      --solution: #c1121f;
      --cell: 1.95cm;
      --board: calc(var(--cell) * 6);
      --font-title: "Trebuchet MS", "Avenir Next", sans-serif;
      --font-body: "Gill Sans", "Trebuchet MS", sans-serif;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: var(--font-body);
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff2d8 0, transparent 28%),
        linear-gradient(180deg, #fef8ec 0%, #fffdf7 36%, #fffaf0 100%);
    }}

    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto;
      padding: 16mm 15mm 14mm;
      display: grid;
      grid-template-rows: auto auto 1fr auto;
      gap: 8mm;
      page-break-after: always;
    }}

    .page:last-child {{
      page-break-after: auto;
    }}

    .page-header {{
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 8mm;
    }}

    .eyebrow {{
      margin: 0 0 2mm;
      font-size: 11pt;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--accent);
      font-weight: 700;
    }}

    h1, h2 {{
      margin: 0;
      font-family: var(--font-title);
      font-size: 24pt;
      line-height: 1.05;
    }}

    .subtitle, .seed, .note {{
      margin: 0;
      font-size: 11.5pt;
      line-height: 1.4;
    }}

    .seed {{
      padding: 3mm 4mm;
      border: 0.5mm solid var(--accent);
      border-radius: 4mm;
      background: rgba(255, 216, 177, 0.45);
      font-weight: 700;
      white-space: nowrap;
    }}

    .board-card {{
      width: fit-content;
      padding: 6mm;
      border: 0.7mm solid rgba(32, 48, 64, 0.18);
      border-radius: 6mm;
      background: rgba(255, 255, 255, 0.9);
      box-shadow: 0 2mm 8mm rgba(0, 0, 0, 0.06);
    }}

    .board {{
      position: relative;
      display: grid;
      grid-template-columns: repeat(6, var(--cell));
      grid-template-rows: repeat(6, var(--cell));
      width: var(--board);
      height: var(--board);
      border: 0.8mm solid var(--grid);
      background:
        linear-gradient(90deg, rgba(79, 109, 122, 0.12) 0, rgba(79, 109, 122, 0.12) 100%),
        #fff;
    }}

    .cell {{
      position: relative;
      border-right: 0.35mm solid rgba(79, 109, 122, 0.42);
      border-bottom: 0.35mm solid rgba(79, 109, 122, 0.42);
      display: grid;
      place-items: center;
      font-weight: 700;
      font-size: 18pt;
    }}

    .cell:nth-child(6n) {{
      border-right: none;
    }}

    .cell.bottom {{
      border-bottom: none;
    }}

    .label {{
      width: 1cm;
      height: 1cm;
      border-radius: 50%;
      display: grid;
      place-items: center;
      background: var(--checkpoint-soft);
      border: 0.45mm solid var(--checkpoint);
      color: var(--checkpoint);
      z-index: 2;
    }}

    .path-layer {{
      position: absolute;
      inset: 0;
      pointer-events: none;
    }}

    .legend {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4mm 8mm;
      align-items: start;
      max-width: 160mm;
    }}

    .legend-card {{
      padding: 4mm 4.5mm;
      border-radius: 5mm;
      border: 0.5mm solid rgba(42, 157, 143, 0.24);
      background: rgba(216, 243, 239, 0.42);
    }}

    .legend-card strong {{
      display: block;
      margin-bottom: 1.5mm;
      font-size: 11pt;
    }}

    .footer {{
      display: flex;
      justify-content: space-between;
      gap: 8mm;
      align-items: end;
    }}

    .solution-page .board-card {{
      background: #fff;
    }}

    @media print {{
      body {{
        background: none;
      }}

      .page {{
        margin: 0;
      }}
    }}
  </style>
</head>
<body>
  <section class="page">
    <div class="page-header">
      <div>
        <p class="eyebrow">Printable Puzzle</p>
        <h1>{escape(puzzle.title)}</h1>
      </div>
      <p class="seed">Seed {puzzle.seed}</p>
    </div>
    <p class="subtitle">{escape(puzzle.instructions)}</p>
    {board_markup}
    <div class="footer">
      <div class="legend">
        <div class="legend-card">
          <strong>How to solve</strong>
          Draw lines up, down, left, or right only.
        </div>
        <div class="legend-card">
          <strong>Remember</strong>
          Visit all 36 squares once and keep the checkpoints in order.
        </div>
      </div>
      <p class="note">Tip: print the first page for pupils and keep the second page for checking.</p>
    </div>
  </section>
  {solution_page}
</body>
</html>
"""


def write_puzzle_html(destination: Path, puzzle: Puzzle, include_solution: bool = True) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_html(puzzle, include_solution=include_solution), encoding="utf-8")
    return destination


def _serpentine_path(board_size: int) -> list[Point]:
    path: list[Point] = []
    for row in range(board_size):
        columns = range(board_size) if row % 2 == 0 else range(board_size - 1, -1, -1)
        for col in columns:
            path.append(Point(row, col))
    return path


def _apply_transform(path: list[Point], board_size: int, transform_index: int) -> list[Point]:
    transforms = [
        lambda p: Point(p.row, p.col),
        lambda p: Point(p.col, board_size - 1 - p.row),
        lambda p: Point(board_size - 1 - p.row, board_size - 1 - p.col),
        lambda p: Point(board_size - 1 - p.col, p.row),
        lambda p: Point(p.row, board_size - 1 - p.col),
        lambda p: Point(board_size - 1 - p.row, p.col),
        lambda p: Point(p.col, p.row),
        lambda p: Point(board_size - 1 - p.col, board_size - 1 - p.row),
    ]
    transform = transforms[transform_index]
    return [transform(point) for point in path]


def _select_checkpoints(path: list[Point], checkpoint_count: int) -> list[Point]:
    last_index = len(path) - 1
    checkpoints: list[Point] = []
    for position in range(checkpoint_count):
        index = round(position * last_index / (checkpoint_count - 1))
        checkpoints.append(path[index])
    return checkpoints


def _render_board(puzzle: Puzzle, show_solution: bool) -> str:
    labels_by_point = {point: str(index) for index, point in enumerate(puzzle.checkpoints, start=1)}
    cells: list[str] = []
    for row in range(puzzle.board_size):
        for col in range(puzzle.board_size):
            point = Point(row, col)
            label = labels_by_point.get(point, "")
            is_bottom = row == puzzle.board_size - 1
            bottom_class = " bottom" if is_bottom else ""
            label_markup = f'<span class="label">{escape(label)}</span>' if label else ""
            cells.append(
                f'<div class="cell{bottom_class}" data-row="{row}" data-col="{col}">{label_markup}</div>'
            )

    path_markup = _render_path_svg(puzzle.solution_path, show_solution)
    return f"""
    <div class="board-card">
      <div class="board">
        {path_markup}
        {''.join(cells)}
      </div>
    </div>
    """


def _render_path_svg(path: tuple[Point, ...], show_solution: bool) -> str:
    if not show_solution:
        return '<svg class="path-layer" viewBox="0 0 600 600" aria-hidden="true"></svg>'

    points = " ".join(f"{point.col * 100 + 50},{point.row * 100 + 50}" for point in path)
    start = path[0]
    end = path[-1]
    return f"""
    <svg class="path-layer" viewBox="0 0 600 600" aria-hidden="true">
      <polyline
        points="{points}"
        fill="none"
        stroke="var(--solution)"
        stroke-width="16"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.82"
      />
      <circle cx="{start.col * 100 + 50}" cy="{start.row * 100 + 50}" r="22" fill="#ffb703" />
      <circle cx="{end.col * 100 + 50}" cy="{end.row * 100 + 50}" r="22" fill="#8ecae6" />
    </svg>
    """
