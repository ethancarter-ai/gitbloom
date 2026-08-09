from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List

from .scanner import find_bloom_blocks, format_blocks, prune_trailing_blocks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitbloom",
        description="Detect and prune stale comment blocks at the ends of files.",
    )
    parser.add_argument("--version", action="version", version="gitbloom 0.1.0")
    parser.add_argument("--format", choices=["text", "json"], default="text", dest="output_format")
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List trailing bloom blocks.")
    list_parser.add_argument("files", nargs="+", help="Files to inspect.")

    prune_parser = subparsers.add_parser("prune", help="Rewrite files with stale blocks removed.")
    prune_parser.add_argument("files", nargs="+", help="Files to rewrite.")
    prune_parser.add_argument("--keep", type=int, default=1, help="Number of newest blocks to keep.")
    prune_parser.add_argument(
        "--dry-run", action="store_true", help="Show diff without rewriting."
    )

    return parser


def _load_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.readlines()


def _write_lines(path: str, lines: List[str]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.writelines(lines)


def _text_summary(file: str, pruned: List[str], original_length: int) -> str:
    changed = original_length != len(pruned)
    return f"{file}: {original_length} -> {len(pruned)} lines"


def _json_summary(file: str, pruned: List[str], original_length: int) -> Dict[str, int]:
    return {
        "file": file,
        "lines_original": original_length,
        "lines_pruned": len(pruned),
    }


def _summary_output(
    file: str,
    pruned: List[str],
    original_length: int,
    output_format: str = "text",
) -> str:
    if output_format == "json":
        return json.dumps(_json_summary(file, pruned, original_length), indent=2)

    return _text_summary(file, pruned, original_length)


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(argv)

    # Handle list command
    if namespace.command == "list":
        blocks = []
        for file_path in namespace.files:
            lines = _load_lines(file_path)
            blocks.extend(find_bloom_blocks(lines))

        output = format_blocks(blocks, output_format=namespace.output_format)
        print(output, end="" if namespace.output_format == "json" else "\n")
        return 0

    # Handle prune command
    if namespace.command == "prune":
        changed = False
        for file_path in namespace.files:
            lines = _load_lines(file_path)
            try:
                pruned_lines = prune_trailing_blocks(lines, keep=namespace.keep)
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2

            file_changed = len(pruned_lines) != len(lines)
            changed = changed or file_changed

            if namespace.dry_run:
                print(
                    _summary_output(
                        file_path,
                        pruned_lines,
                        len(lines),
                        namespace.output_format,
                    )
                )
                continue

            if file_changed:
                _write_lines(file_path, pruned_lines)
                print(f"pruned {file_path}", file=sys.stderr)

        return 0 if changed else 1

    parser.print_help()
    return 2

