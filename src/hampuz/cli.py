from __future__ import annotations

import argparse
from pathlib import Path

from .generator import (
    DEFAULT_HEIGHT,
    DEFAULT_MODE,
    DEFAULT_WIDTH,
    build_puzzle,
    current_unix_millis,
    default_output_path,
    write_puzzle_html,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hampuz",
        description="Generate printable Hamilton path puzzles as fixed-layout HTML.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed used for puzzle variation. Defaults to the current Unix millisecond.",
    )
    parser.add_argument("--size", type=int, default=None, help="Square board size shorthand.")
    parser.add_argument("--width", type=int, default=None, help="Board width in cells.")
    parser.add_argument("--height", type=int, default=None, help="Board height in cells.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output HTML path. Defaults to the system temp directory plus /hampuz.",
    )
    parser.add_argument(
        "--checkpoints",
        type=int,
        default=10,
        help="Number of numbered checkpoints to show on the board.",
    )
    parser.add_argument(
        "--no-solution",
        action="store_true",
        help="Exclude the teacher solution page from the output HTML.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--path",
        action="store_true",
        help="Generate a non-closed Hamilton path puzzle.",
    )
    mode_group.add_argument(
        "--circuit",
        action="store_true",
        help="Generate a closed Hamilton circuit puzzle.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else current_unix_millis()
    width = args.size if args.size is not None else (args.width if args.width is not None else DEFAULT_WIDTH)
    height = args.size if args.size is not None else (args.height if args.height is not None else DEFAULT_HEIGHT)
    mode = "circuit" if args.circuit else DEFAULT_MODE
    if args.path:
        mode = "path"
    puzzle = build_puzzle(
        seed=seed,
        width=width,
        height=height,
        checkpoint_count=args.checkpoints,
        mode=mode,
    )
    output_path = args.output if args.output is not None else default_output_path(seed)
    write_puzzle_html(output_path, puzzle, include_solution=not args.no_solution)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
