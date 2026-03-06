from pathlib import Path
import tempfile

from hampuz.generator import Point, build_puzzle, current_unix_millis, default_output_path, render_html


def test_build_puzzle_has_full_path_and_requested_checkpoints() -> None:
    puzzle = build_puzzle(seed=7, width=6, height=6, checkpoint_count=10, mode="path")

    assert puzzle.width == 6
    assert puzzle.height == 6
    assert puzzle.mode == "path"
    assert len(puzzle.solution_path) == 36
    assert len(set(puzzle.solution_path)) == 36
    assert len(puzzle.checkpoints) == 10
    assert _is_hamiltonian_grid_walk(puzzle.solution_path)
    assert not _is_cycle_closed(puzzle.solution_path)


def test_different_seeds_produce_distinct_paths() -> None:
    first = build_puzzle(seed=7, width=6, height=6, checkpoint_count=10, mode="path")
    second = build_puzzle(seed=8, width=6, height=6, checkpoint_count=10, mode="path")

    assert first.solution_path != second.solution_path


def test_rectangular_board_is_supported() -> None:
    puzzle = build_puzzle(seed=21, width=5, height=6, checkpoint_count=8, mode="path")

    assert puzzle.width == 5
    assert puzzle.height == 6
    assert len(puzzle.solution_path) == 30
    assert len(set(puzzle.solution_path)) == 30
    assert _is_hamiltonian_grid_walk(puzzle.solution_path)


def test_circuit_mode_closes_the_loop() -> None:
    puzzle = build_puzzle(seed=22, width=6, height=6, checkpoint_count=10, mode="circuit")

    assert puzzle.mode == "circuit"
    assert len(puzzle.solution_path) == 36
    assert len(set(puzzle.solution_path)) == 36
    assert _is_hamiltonian_grid_walk(puzzle.solution_path)
    assert _is_cycle_closed(puzzle.solution_path)


def test_render_html_contains_teacher_solution_page() -> None:
    puzzle = build_puzzle(seed=11, width=5, height=6, checkpoint_count=8, mode="path")
    html = render_html(puzzle, include_solution=True)

    assert "Teacher Copy" in html
    assert "Checkpoint Trail" in html
    assert "Board: 5 x 6." in html


def test_render_html_describes_circuit_mode() -> None:
    puzzle = build_puzzle(seed=12, width=6, height=6, checkpoint_count=10, mode="circuit")
    html = render_html(puzzle, include_solution=True)

    assert "closed circuit" in html
    assert "Checkpoint 1 and checkpoint 10 sit next to each other" in html


def test_default_output_path_uses_tempdir() -> None:
    output_path = default_output_path(seed=99)
    expected_root = Path(tempfile.gettempdir()) / "hampuz"

    assert output_path.parent == expected_root
    assert output_path.name == "hampuz-99.html"


def test_current_unix_millis_is_positive_int() -> None:
    seed = current_unix_millis()

    assert isinstance(seed, int)
    assert seed > 0


def _is_hamiltonian_grid_walk(path: tuple[Point, ...]) -> bool:
    for current, nxt in zip(path, path[1:]):
        manhattan_distance = abs(current.row - nxt.row) + abs(current.col - nxt.col)
        if manhattan_distance != 1:
            return False
    return True


def _is_cycle_closed(path: tuple[Point, ...]) -> bool:
    start = path[0]
    end = path[-1]
    return abs(start.row - end.row) + abs(start.col - end.col) == 1
