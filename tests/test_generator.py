from pathlib import Path
import tempfile

from hampuz.generator import build_puzzle, default_output_path, render_html


def test_build_puzzle_has_full_path_and_requested_checkpoints() -> None:
    puzzle = build_puzzle(seed=7, checkpoint_count=10)

    assert puzzle.board_size == 6
    assert len(puzzle.solution_path) == 36
    assert len(set(puzzle.solution_path)) == 36
    assert len(puzzle.checkpoints) == 10


def test_render_html_contains_teacher_solution_page() -> None:
    puzzle = build_puzzle(seed=11, checkpoint_count=10)
    html = render_html(puzzle, include_solution=True)

    assert "Teacher Copy" in html
    assert "Checkpoint Trail" in html


def test_default_output_path_uses_tempdir() -> None:
    output_path = default_output_path(seed=99)
    expected_root = Path(tempfile.gettempdir()) / "hampuz"

    assert output_path.parent == expected_root
    assert output_path.name == "hampuz-99.html"
