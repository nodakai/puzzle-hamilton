from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import random
import tempfile


DEFAULT_WIDTH = 6
DEFAULT_HEIGHT = 6
DEFAULT_CHECKPOINTS = 10
MAX_CELLS = 144
DEFAULT_MODE = "path"


@dataclass(frozen=True)
class Point:
    row: int
    col: int


@dataclass(frozen=True)
class Puzzle:
    title: str
    instructions: str
    width: int
    height: int
    mode: str
    checkpoints: tuple[Point, ...]
    solution_path: tuple[Point, ...]
    seed: int

    @property
    def cell_count(self) -> int:
        return self.width * self.height


def current_unix_millis() -> int:
    import time

    return time.time_ns() // 1_000_000


def default_output_path(seed: int) -> Path:
    return Path(tempfile.gettempdir()) / "hampuz" / f"hampuz-{seed}.html"


def build_puzzle(
    seed: int,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    checkpoint_count: int = DEFAULT_CHECKPOINTS,
    mode: str = DEFAULT_MODE,
) -> Puzzle:
    _validate_board_dimensions(width, height, mode)
    if not 2 <= checkpoint_count <= width * height:
        raise ValueError("checkpoint_count must fit within the board.")

    rng = random.Random(seed)
    path = _generate_hamiltonian_path(width, height, mode, rng)
    checkpoints = _select_checkpoints(path, checkpoint_count)

    return Puzzle(
        title="Checkpoint Trail",
        instructions=_instructions_for_mode(mode, checkpoint_count),
        width=width,
        height=height,
        mode=mode,
        checkpoints=tuple(checkpoints),
        solution_path=tuple(path),
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
    cell_size_mm = _cell_size_mm(puzzle.width, puzzle.height)
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
      --cell: {cell_size_mm:.2f}mm;
      --board-width: calc(var(--cell) * {puzzle.width});
      --board-height: calc(var(--cell) * {puzzle.height});
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
      grid-template-columns: repeat({puzzle.width}, var(--cell));
      grid-template-rows: repeat({puzzle.height}, var(--cell));
      width: var(--board-width);
      height: var(--board-height);
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
      font-size: min(18pt, calc(var(--cell) * 0.48));
    }}

    .cell.last-col {{
      border-right: none;
    }}

    .cell.last-row {{
      border-bottom: none;
    }}

    .label {{
      width: min(1cm, calc(var(--cell) * 0.56));
      height: min(1cm, calc(var(--cell) * 0.56));
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
    <p class="subtitle">{escape(puzzle.instructions)} Board: {puzzle.width} x {puzzle.height}.</p>
    {board_markup}
    <div class="footer">
      <div class="legend">
        <div class="legend-card">
          <strong>How to solve</strong>
          Draw lines up, down, left, or right only.
        </div>
        <div class="legend-card">
          <strong>Remember</strong>
          Visit all {puzzle.cell_count} squares once and keep the checkpoints in order.
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


def _validate_board_dimensions(width: int, height: int, mode: str) -> None:
    if width < 2 or height < 2:
        raise ValueError("width and height must both be at least 2.")
    if width * height > MAX_CELLS:
        raise ValueError(f"board area must be at most {MAX_CELLS} cells for this generator.")
    if mode not in {"path", "circuit"}:
        raise ValueError("mode must be 'path' or 'circuit'.")
    if mode == "circuit" and (width * height) % 2 != 0:
        raise ValueError("circuit mode requires an even number of cells on the board.")


def _cell_size_mm(width: int, height: int) -> float:
    usable_width_mm = 148.0
    usable_height_mm = 165.0
    return min(27.0, usable_width_mm / width, usable_height_mm / height)


def _generate_hamiltonian_path(width: int, height: int, mode: str, rng: random.Random) -> list[Point]:
    path = _serpentine_path(width, height)
    best_path = path.copy()
    best_score = _mode_score(best_path, mode)
    attempts = 12
    iterations = max(300, width * height * 40)

    for _ in range(attempts):
        candidate = path.copy()
        _randomize_path(candidate, width, height, rng, iterations)
        score = _mode_score(candidate, mode)
        if score > best_score:
            best_path = candidate.copy()
            best_score = score
        if _matches_mode(candidate, mode) and _path_score(candidate) >= max(10, (width * height) // 3):
            best_path = candidate.copy()
            break

    if not _matches_mode(best_path, mode):
        best_path = _force_mode_match(best_path, width, height, mode, rng)
    return best_path


def _serpentine_path(width: int, height: int) -> list[Point]:
    path: list[Point] = []
    for row in range(height):
        columns = range(width) if row % 2 == 0 else range(width - 1, -1, -1)
        for col in columns:
            path.append(Point(row, col))
    return path


def _randomize_path(path: list[Point], width: int, height: int, rng: random.Random, iterations: int) -> None:
    for _ in range(iterations):
        if not _backbite_step(path, width, height, rng):
            continue


def _backbite_step(path: list[Point], width: int, height: int, rng: random.Random) -> bool:
    from_start = rng.choice([True, False])
    endpoint_index = 0 if from_start else len(path) - 1
    blocked_neighbor_index = 1 if from_start else len(path) - 2
    endpoint = path[endpoint_index]
    blocked_neighbor = path[blocked_neighbor_index]
    neighbors = _neighbors(endpoint, width, height)
    candidates = [point for point in neighbors if point != blocked_neighbor]
    rng.shuffle(candidates)
    positions = {point: index for index, point in enumerate(path)}

    for candidate in candidates:
        cut_index = positions[candidate]
        if from_start:
            if cut_index <= 1:
                continue
            path[:] = list(reversed(path[:cut_index])) + path[cut_index:]
            return True
        if cut_index >= len(path) - 2:
            continue
        path[:] = path[: cut_index + 1] + list(reversed(path[cut_index + 1 :]))
        return True
    return False


def _matches_mode(path: list[Point], mode: str) -> bool:
    endpoints_adjacent = _points_are_adjacent(path[0], path[-1])
    if mode == "circuit":
        return endpoints_adjacent
    return not endpoints_adjacent


def _force_mode_match(path: list[Point], width: int, height: int, mode: str, rng: random.Random) -> list[Point]:
    candidate = path.copy()
    for _ in range(max(500, width * height * 80)):
        _backbite_step(candidate, width, height, rng)
        if _matches_mode(candidate, mode):
            return candidate
    raise RuntimeError(f"Unable to generate a {mode} puzzle for this board and seed.")


def _mode_score(path: list[Point], mode: str) -> int:
    score = _path_score(path)
    endpoints_adjacent = _points_are_adjacent(path[0], path[-1])
    if mode == "circuit":
        return score + (1000 if endpoints_adjacent else 0)
    return score + (1000 if not endpoints_adjacent else -1000)


def _neighbors(point: Point, width: int, height: int) -> list[Point]:
    neighbors: list[Point] = []
    if point.row > 0:
        neighbors.append(Point(point.row - 1, point.col))
    if point.row + 1 < height:
        neighbors.append(Point(point.row + 1, point.col))
    if point.col > 0:
        neighbors.append(Point(point.row, point.col - 1))
    if point.col + 1 < width:
        neighbors.append(Point(point.row, point.col + 1))
    return neighbors


def _points_are_adjacent(first: Point, second: Point) -> bool:
    return abs(first.row - second.row) + abs(first.col - second.col) == 1


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
    for row in range(puzzle.height):
        for col in range(puzzle.width):
            point = Point(row, col)
            label = labels_by_point.get(point, "")
            row_class = " last-row" if row == puzzle.height - 1 else ""
            col_class = " last-col" if col == puzzle.width - 1 else ""
            label_markup = f'<span class="label">{escape(label)}</span>' if label else ""
            cells.append(
                f'<div class="cell{row_class}{col_class}" data-row="{row}" data-col="{col}">{label_markup}</div>'
            )

    path_markup = _render_path_svg(
        puzzle.solution_path,
        puzzle.width,
        puzzle.height,
        puzzle.mode,
        show_solution,
    )
    return f"""
    <div class="board-card">
      <div class="board">
        {path_markup}
        {''.join(cells)}
      </div>
    </div>
    """


def _render_path_svg(
    path: tuple[Point, ...],
    width: int,
    height: int,
    mode: str,
    show_solution: bool,
) -> str:
    view_box_width = width * 100
    view_box_height = height * 100
    if not show_solution:
        return (
            f'<svg class="path-layer" viewBox="0 0 {view_box_width} {view_box_height}" aria-hidden="true"></svg>'
        )

    points = " ".join(f"{point.col * 100 + 50},{point.row * 100 + 50}" for point in path)
    start = path[0]
    end = path[-1]
    closing_segment = ""
    if mode == "circuit":
        closing_segment = (
            f'<line x1="{end.col * 100 + 50}" y1="{end.row * 100 + 50}" '
            f'x2="{start.col * 100 + 50}" y2="{start.row * 100 + 50}" '
            'stroke="var(--solution)" stroke-width="16" stroke-linecap="round" opacity="0.82" />'
        )
    return f"""
    <svg class="path-layer" viewBox="0 0 {view_box_width} {view_box_height}" aria-hidden="true">
      <polyline
        points="{points}"
        fill="none"
        stroke="var(--solution)"
        stroke-width="16"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.82"
      />
      {closing_segment}
      <circle cx="{start.col * 100 + 50}" cy="{start.row * 100 + 50}" r="22" fill="#ffb703" />
      <circle cx="{end.col * 100 + 50}" cy="{end.row * 100 + 50}" r="22" fill="#8ecae6" />
    </svg>
    """


def _path_score(path: list[Point]) -> int:
    turns = 0
    for previous, current, nxt in zip(path, path[1:], path[2:]):
        first_direction = (current.row - previous.row, current.col - previous.col)
        second_direction = (nxt.row - current.row, nxt.col - current.col)
        if first_direction != second_direction:
            turns += 1
    return turns


def _instructions_for_mode(mode: str, checkpoint_count: int) -> str:
    if mode == "circuit":
        return (
            "Draw one closed circuit through every square exactly once. "
            f"Follow checkpoints 1 to {checkpoint_count} in order. "
            f"Checkpoint 1 and checkpoint {checkpoint_count} sit next to each other because the circuit closes there."
        )
    return (
        "Draw one non-closed path through every square exactly once. "
        f"Follow checkpoints 1 to {checkpoint_count} in order. "
        f"Checkpoint 1 begins the path and checkpoint {checkpoint_count} ends it."
    )
