from __future__ import annotations

import argparse
from pathlib import Path

from .generator import build_puzzle, default_output_path, write_puzzle_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hampuz",
        description="Generate printable Hamilton path puzzles as fixed-layout HTML.",
    )
    parser.add_argument("--seed", type=int, default=36, help="Seed used for puzzle variation.")
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
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    puzzle = build_puzzle(seed=args.seed, checkpoint_count=args.checkpoints)
    output_path = args.output if args.output is not None else default_output_path(args.seed)
    write_puzzle_html(output_path, puzzle, include_solution=not args.no_solution)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
