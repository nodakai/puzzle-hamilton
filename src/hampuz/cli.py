from __future__ import annotations

import argparse
from pathlib import Path

from .generator import (
    DEFAULT_HEIGHT,
    DEFAULT_MODE,
    DEFAULT_WIDTH,
    build_puzzle_pack,
    default_run_seed,
    default_output_path,
    write_puzzle_html,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hampuz",
        description="Generate printable Hamilton path puzzles as fixed-layout HTML.",
    )
    parser.add_argument(
        "--bundle",
        type=int,
        default=None,
        help="Bundle id. Defaults to int(yyMMddHHmmss) and must be below 10^12.",
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
        "--pack",
        type=int,
        default=2,
        help="Number of games to place on each page. Defaults to 2.",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=None,
        help="Total number of games to generate. Defaults to the pack size.",
    )
    parser.add_argument(
        "--no-solution",
        action="store_true",
        help="Exclude the solution pages from the output HTML.",
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

    bundle = args.bundle if args.bundle is not None else default_run_seed()
    width = args.size if args.size is not None else (args.width if args.width is not None else DEFAULT_WIDTH)
    height = args.size if args.size is not None else (args.height if args.height is not None else DEFAULT_HEIGHT)
    mode = "circuit" if args.circuit else DEFAULT_MODE
    if args.path:
        mode = "path"
    games = args.games if args.games is not None else args.pack
    puzzles = build_puzzle_pack(
        seed=bundle,
        games=games,
        width=width,
        height=height,
        checkpoint_count=args.checkpoints,
        mode=mode,
    )
    output_path = args.output if args.output is not None else default_output_path(bundle)
    write_puzzle_html(output_path, puzzles, include_solution=not args.no_solution, pack=args.pack)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
