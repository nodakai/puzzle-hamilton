from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
    game_index: int
    checkpoints: tuple[Point, ...]
    solution_path: tuple[Point, ...]
    seed: int

    @property
    def cell_count(self) -> int:
        return self.width * self.height


def current_unix_millis() -> int:
    import time

    return time.time_ns() // 1_000_000


def default_run_seed() -> int:
    return int(datetime.now().strftime("%y%m%d%H%M%S"))


def default_output_path(seed: int) -> Path:
    return Path(tempfile.gettempdir()) / "hampuz" / f"hampuz-{seed}.html"


def derive_game_seed(seed: int, game_index: int) -> int:
    if not 0 <= seed < 10**12:
        raise ValueError("run seed must be between 0 and 10^12 - 1.")
    if game_index < 0:
        raise ValueError("game_index must be non-negative.")
    return game_index * 10**12 + seed


def build_puzzle(
    seed: int,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    checkpoint_count: int = DEFAULT_CHECKPOINTS,
    mode: str = DEFAULT_MODE,
    game_index: int = 0,
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
        game_index=game_index,
        checkpoints=tuple(checkpoints),
        solution_path=tuple(path),
        seed=seed,
    )


def build_puzzle_pack(
    seed: int,
    games: int,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    checkpoint_count: int = DEFAULT_CHECKPOINTS,
    mode: str = DEFAULT_MODE,
) -> list[Puzzle]:
    return [
        build_puzzle(
            seed=derive_game_seed(seed, game_index),
            width=width,
            height=height,
            checkpoint_count=checkpoint_count,
            mode=mode,
            game_index=game_index,
        )
        for game_index in range(games)
    ]


def render_html(puzzle: Puzzle, include_solution: bool = True) -> str:
    return render_pack_html([puzzle], include_solution=include_solution, pack=1)


def render_pack_html(puzzles: list[Puzzle], include_solution: bool = True, pack: int = 2) -> str:
    if not puzzles:
        raise ValueError("puzzles must not be empty.")
    if pack < 1:
        raise ValueError("pack must be at least 1.")

    sample = puzzles[0]
    run_seed = sample.seed % 10**12
    puzzle_pages = _render_pages(puzzles, pack=pack, show_solution=False)
    solution_pages = _render_pages(puzzles, pack=pack, show_solution=True) if include_solution else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(sample.title)} - Seed {sample.seed}</title>
  <style>
    :root {{
      --paper: #ffffff;
      --ink: #1f1f1f;
      --accent: #1f1f1f;
      --grid: #505050;
      --checkpoint: #2f2f2f;
      --checkpoint-soft: #ffffff;
      --checkpoint-edge: #000000;
      --solution: #111111;
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
      background: #ffffff;
    }}

    .page {{
      width: 210mm;
      min-height: 297mm;
      margin: 0 auto;
      padding: 16mm 15mm 14mm;
      display: flex;
      flex-direction: column;
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

    .subtitle, .seed {{
      margin: 0;
      font-size: 11.5pt;
      line-height: 1.4;
    }}

    .seed {{
      padding: 3mm 4mm;
      border: 0.5mm solid #3a3a3a;
      border-radius: 4mm;
      font-weight: 700;
      white-space: nowrap;
    }}

    .sheet-grid {{
      display: grid;
      gap: 6mm;
      grid-template-columns: repeat(var(--grid-columns, 1), minmax(0, 1fr));
      align-content: start;
    }}

    .puzzle-card {{
      display: flex;
      flex-direction: column;
      gap: 4mm;
      min-width: 0;
      align-items: start;
    }}

    .puzzle-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 4mm;
    }}

    .puzzle-card-title {{
      margin: 0;
      font-family: var(--font-title);
      font-size: 15pt;
      line-height: 1.1;
    }}

    .board {{
      position: relative;
      display: grid;
      width: fit-content;
      border: 0.8mm solid var(--grid);
      background: #ffffff;
      overflow: hidden;
    }}

    .cell {{
      position: relative;
      display: grid;
      place-items: center;
      font-weight: 700;
      font-size: min(18pt, calc(var(--cell) * 0.48));
      background: transparent;
      z-index: 1;
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
      line-height: 1;
    }}

    .label.endpoint {{
      min-width: min(1.34cm, calc(var(--cell) * 0.76));
      width: auto;
      height: min(1.08cm, calc(var(--cell) * 0.62));
      padding: 0 0.22em;
      background: #ffffff;
      border-color: var(--checkpoint-edge);
      color: #000000;
      border-width: 0.55mm;
      border-radius: 0.42cm;
      box-shadow: 0 0 0 0.14mm #8a8a8a;
      font-size: 0.94em;
      font-weight: 700;
      letter-spacing: 0;
      line-height: 1;
      text-align: center;
      justify-content: center;
    }}

    .label.endpoint.solution-endpoint {{
      border-width: 1.05mm;
      box-shadow: none;
    }}

    .path-layer {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 3;
    }}

    .grid-layer {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 2;
    }}

    .legend {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4mm 8mm;
      align-items: start;
      max-width: 178mm;
    }}

    .legend-card {{
      padding: 4mm 4.5mm;
      border-radius: 5mm;
      border: 0.5mm solid #d8d8d8;
      background: #ffffff;
    }}

    .legend-card strong {{
      display: block;
      margin-bottom: 1.5mm;
      font-size: 11pt;
    }}

    .footer {{
      margin-top: auto;
    }}

    .page-bundle {{
      margin: auto 0 0;
      align-self: end;
      font-size: 8.5pt;
      color: #b0b0b0;
      letter-spacing: 0.03em;
    }}

    .solution-page .board-card {{
      background: #fff;
    }}

    @media print {{
      body {{
        background: none;
        color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }}

      .page {{
        margin: 0;
      }}

      .legend-card,
      .seed {{
        box-shadow: none;
      }}
    }}
  </style>
</head>
<body>
  {puzzle_pages}
  {solution_pages}
</body>
</html>
"""


def write_puzzle_html(
    destination: Path,
    puzzle: Puzzle | list[Puzzle],
    include_solution: bool = True,
    pack: int = 2,
) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(puzzle, list):
        html = render_pack_html(puzzle, include_solution=include_solution, pack=pack)
    else:
        html = render_html(puzzle, include_solution=include_solution)
    destination.write_text(html, encoding="utf-8")
    return destination


def _render_pages(puzzles: list[Puzzle], pack: int, show_solution: bool) -> str:
    pages: list[str] = []
    chunks = [puzzles[index : index + pack] for index in range(0, len(puzzles), pack)]
    for page_index, chunk in enumerate(chunks):
        pages.append(_render_page(chunk, pack=pack, page_index=page_index, show_solution=show_solution))
    return "".join(pages)


def _render_page(puzzles: list[Puzzle], pack: int, page_index: int, show_solution: bool) -> str:
    sample = puzzles[0]
    bundle = sample.seed % 10**12
    columns, rows = _page_grid_dimensions(pack)
    grid_style = f"--grid-columns: {columns};"
    heading = "Solutions" if show_solution else sample.title
    subtitle = "" if show_solution else f"{sample.instructions} Board: {sample.width} x {sample.height}."
    cards = "".join(
        _render_puzzle_card(
            puzzle,
            show_solution=show_solution,
            cell_size_mm=_cell_size_mm(puzzle.width, puzzle.height, columns, rows, show_solution),
        )
        for puzzle in puzzles
    )
    return f"""
    <section class="page{' solution-page' if show_solution else ''}">
      <div class="page-header">
        <div>
          <h1>{escape(heading)}</h1>
        </div>
        <p class="seed">Pack {page_index + 1}</p>
      </div>
      {'<p class="subtitle">' + escape(subtitle) + '</p>' if subtitle else ''}
      <div class="sheet-grid" style="{grid_style}">
        {cards}
      </div>
      {'<div class="footer"><div class="legend"><div class="legend-card"><strong>How to solve</strong>Draw lines up, down, left, or right only.</div><div class="legend-card"><strong>Remember</strong>Visit all ' + str(sample.cell_count) + ' squares once and keep the checkpoints in order.</div></div></div>' if not show_solution else ''}
      <p class="page-bundle">bundle {bundle}</p>
    </section>
    """


def _render_puzzle_card(puzzle: Puzzle, show_solution: bool, cell_size_mm: float) -> str:
    return f"""
    <article class="puzzle-card">
      <div class="puzzle-card-header">
        <h2 class="puzzle-card-title">Game {puzzle.game_index + 1}</h2>
      </div>
      {_render_board(puzzle, show_solution=show_solution, cell_size_mm=cell_size_mm)}
    </article>
    """


def _validate_board_dimensions(width: int, height: int, mode: str) -> None:
    if width < 2 or height < 2:
        raise ValueError("width and height must both be at least 2.")
    if width * height > MAX_CELLS:
        raise ValueError(f"board area must be at most {MAX_CELLS} cells for this generator.")
    if mode not in {"path", "circuit"}:
        raise ValueError("mode must be 'path' or 'circuit'.")
    if mode == "circuit" and (width * height) % 2 != 0:
        raise ValueError("circuit mode requires an even number of cells on the board.")


def _cell_size_mm(width: int, height: int, columns: int, rows: int, show_solution: bool) -> float:
    page_width_mm = 180.0
    page_height_mm = 267.0
    grid_gap_mm = 6.0
    footer_mm = 22.0 if not show_solution else 0.0
    header_mm = 24.0
    subtitle_mm = 12.0
    slot_width_mm = (page_width_mm - (columns - 1) * grid_gap_mm) / columns
    slot_height_mm = (page_height_mm - header_mm - subtitle_mm - footer_mm - (rows - 1) * grid_gap_mm) / rows
    board_width_mm = slot_width_mm - 12.0
    board_height_mm = slot_height_mm - 22.0
    return max(4.8, min(27.0, board_width_mm / width, board_height_mm / height))


def _page_grid_dimensions(pack: int) -> tuple[int, int]:
    if pack <= 1:
        return 1, 1
    if pack == 2:
        return 1, 2
    return 2, (pack + 1) // 2


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


def _render_board(puzzle: Puzzle, show_solution: bool, cell_size_mm: float) -> str:
    board_style = (
        f"--cell: {cell_size_mm:.2f}mm; "
        f"grid-template-columns: repeat({puzzle.width}, {cell_size_mm:.2f}mm); "
        f"grid-template-rows: repeat({puzzle.height}, {cell_size_mm:.2f}mm); "
        f"width: fit-content;"
    )
    labels_by_point = {point: str(index) for index, point in enumerate(puzzle.checkpoints, start=1)}
    endpoint_points = {puzzle.checkpoints[0], puzzle.checkpoints[-1]}
    solution_endpoint_points = {puzzle.solution_path[0], puzzle.solution_path[-1]} if show_solution else set()
    cells: list[str] = []
    for row in range(puzzle.height):
        for col in range(puzzle.width):
            point = Point(row, col)
            label = labels_by_point.get(point, "")
            label_class = "label"
            if point in endpoint_points and label:
                label_class = "label endpoint"
                if point in solution_endpoint_points:
                    label_class += " solution-endpoint"
            label_markup = f'<span class="{label_class}">{escape(label)}</span>' if label else ""
            cells.append(
                f'<div class="cell" data-row="{row}" data-col="{col}">{label_markup}</div>'
            )

    grid_markup = _render_grid_svg(puzzle.width, puzzle.height)
    path_markup = _render_path_svg(
        puzzle.solution_path,
        puzzle.width,
        puzzle.height,
        puzzle.mode,
        puzzle.game_index,
        show_solution,
    )
    return f"""
    <div class="board" style="{board_style}">
      {grid_markup}
      {path_markup}
      {''.join(cells)}
    </div>
    """


def _render_grid_svg(width: int, height: int) -> str:
    view_box_width = width * 100
    view_box_height = height * 100
    bleed = 8
    verticals = "".join(
        f'<line x1="{col * 100}" y1="{-bleed}" x2="{col * 100}" y2="{view_box_height + bleed}" />'
        for col in range(1, width)
    )
    horizontals = "".join(
        f'<line x1="{-bleed}" y1="{row * 100}" x2="{view_box_width + bleed}" y2="{row * 100}" />'
        for row in range(1, height)
    )
    return f"""
    <svg class="grid-layer" viewBox="0 0 {view_box_width} {view_box_height}" aria-hidden="true">
      <g stroke="#6b6b6b" stroke-width="3.6" stroke-linecap="square" shape-rendering="crispEdges">
        {verticals}
        {horizontals}
      </g>
    </svg>
    """


def _render_path_svg(
    path: tuple[Point, ...],
    width: int,
    height: int,
    mode: str,
    game_index: int,
    show_solution: bool,
) -> str:
    view_box_width = width * 100
    view_box_height = height * 100
    if not show_solution:
        return (
            f'<svg class="path-layer" viewBox="0 0 {view_box_width} {view_box_height}" aria-hidden="true"></svg>'
        )

    points_list = [f"{point.col * 100 + 50},{point.row * 100 + 50}" for point in path]
    start = path[0]
    clip_id = f"board-clip-{'solution' if show_solution else 'puzzle'}-{game_index}"
    if mode == "circuit":
        points_list.append(f"{start.col * 100 + 50},{start.row * 100 + 50}")
    points = " ".join(points_list)
    return f"""
    <svg class="path-layer" viewBox="0 0 {view_box_width} {view_box_height}" aria-hidden="true">
      <defs>
        <clipPath id="{clip_id}">
          <rect x="0" y="0" width="{view_box_width}" height="{view_box_height}" />
        </clipPath>
      </defs>
      <g clip-path="url(#{clip_id})">
        <polyline
          points="{points}"
          fill="none"
          stroke="var(--solution)"
          stroke-width="10"
          stroke-linecap="round"
          stroke-linejoin="round"
          opacity="0.34"
        />
      </g>
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
