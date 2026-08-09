from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class BloomBlock:
    start: int
    end: int
    body: str
    markers: Tuple[str, ...]


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _comment_style(value: str) -> str | None:
    for style in ("#", "//", "--"):
        if value.lstrip().startswith(style):
            return style
    return None


def _markers(body: str) -> List[str]:
    import re
    return re.findall(r"@date\s+(\d{4}-\d{2}-\d{2})", body)


def find_bloom_blocks(lines: Sequence[str]) -> List[BloomBlock]:
    lines_list = list(lines)
    blocks: List[BloomBlock] = []
    cursor = len(lines_list)
    while cursor > 0:
        block, next_cursor = _extract_block(lines_list, cursor)
        if block is None:
            break
        blocks.append(block)
        cursor = next_cursor
        while cursor > 0 and _is_blank(lines_list[cursor - 1]):
            cursor -= 1
    return blocks


def prune_trailing_blocks(lines: Sequence[str], *, keep: int = 1) -> List[str]:
    if keep < 0:
        raise ValueError("keep must be non-negative")
    blocks = find_bloom_blocks(lines)
    droppable = blocks[keep:]
    dropped = set()
    for block in droppable:
        dropped.update(range(block.start, block.end + 1))
    pruned = [line for idx, line in enumerate(lines) if idx not in dropped]
    while pruned and pruned[-1].strip() == "":
        pruned.pop()
    return pruned


def format_blocks(blocks: Sequence[BloomBlock], output_format: str = "text") -> str:
    if not blocks:
        return ""
    if output_format == "json":
        return json.dumps(
            [
                {
                    "start": block.start,
                    "end": block.end,
                    "markers": list(block.markers),
                    "body": block.body,
                }
                for block in blocks
            ]
        )
    lines: List[str] = []
    for block in blocks:
        lines.append(f"Block from line {block.start + 1}-{block.end}:")
        for line in block.body.splitlines():
            lines.append(f"  {line}")
    return "\n".join(lines) + "\n"


def _extract_block(lines: List[str], cursor: int) -> Tuple[BloomBlock | None, int]:
    while cursor > 0 and _is_blank(lines[cursor - 1]):
        cursor -= 1
    if cursor == 0:
        return None, 0
    end = cursor
    start = None
    style = _comment_style(lines[cursor - 1])
    for idx in range(cursor - 1, -1, -1):
        line = lines[idx]
        if _is_blank(line):
            start = idx + 1
            break
        current_style = _comment_style(line)
        if current_style is None or current_style != style:
            start = idx + 1
            break
        start = idx
    else:
        start = 0
    if start is None or start >= len(lines) or _comment_style(lines[start]) is None:
        return None, 0
    body = "".join(lines[start:end])
    return BloomBlock(start=start, end=end - 1, body=body, markers=tuple(_markers(body))), start
