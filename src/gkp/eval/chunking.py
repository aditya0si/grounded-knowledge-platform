"""Boundary-aware chunking.

Fixed-width character chunking is the default in most RAG demos and it is the
reason tables get destroyed: a 512-character window will happily cut a markdown
row in half, leaving two fragments that each answer nothing while the gold label
says the answer was retrieved.

This chunker packs whole structural units instead — paragraphs, and table rows
carrying their header — so a boundary never falls inside a record. It is
deliberately *not* fixed-width, because the M2 ablation varies chunk size and a
chunker that ignores document structure would make that ablation measure the
chunker's damage rather than the retrieval strategy.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Chunk", "chunk_document"]

DEFAULT_TARGET_CHARS = 512
DEFAULT_OVERLAP_CHARS = 64
DEFAULT_MIN_CHARS = 120

_TABLE_HEADER_ROWS = 2  # header line + separator rule


@dataclass(frozen=True)
class Chunk:
    """A retrievable unit of a document."""

    doc_id: str
    seq: int
    text: str
    section: str
    char_start: int
    char_end: int

    @property
    def chunk_id(self) -> str:
        """Stable identifier: document plus position, so it survives re-chunking
        at a different size only insofar as ``seq`` is stable."""
        return f"{self.doc_id}#{self.seq}"


@dataclass(frozen=True)
class _Unit:
    text: str
    start: int
    end: int
    section: str
    #: Header lines to re-emit when this row starts a chunk, so a table split
    #: across chunks keeps its column meanings.
    table_header: tuple[str, str] | None = None


def _units(text: str) -> list[_Unit]:
    """Split rendered markdown into atomic units, tracking sections and tables."""
    units: list[_Unit] = []
    section = ""
    header: tuple[str, str] | None = None
    pending_table_lines: list[tuple[str, int, int]] = []
    offset = 0

    def flush_table() -> None:
        nonlocal header, pending_table_lines
        if not pending_table_lines:
            return
        if len(pending_table_lines) >= _TABLE_HEADER_ROWS:
            head, rule = pending_table_lines[0], pending_table_lines[1]
            header = (head[0], rule[0])
        else:
            header = None
        for line_text, line_start, line_end in pending_table_lines:
            units.append(
                _Unit(
                    text=line_text,
                    start=line_start,
                    end=line_end,
                    section=section,
                    table_header=header,
                )
            )
        pending_table_lines = []

    for line in text.split("\n"):
        line_start = offset
        line_end = offset + len(line)
        offset = line_end + 1  # account for the newline

        if line.startswith("## "):
            flush_table()
            section = line[3:].strip()
            continue
        if line.startswith("# "):
            flush_table()
            section = ""
            continue
        if not line.strip():
            flush_table()
            continue
        if line.startswith("|"):
            pending_table_lines.append((line, line_start, line_end))
            continue

        flush_table()
        units.append(_Unit(text=line, start=line_start, end=line_end, section=section))

    flush_table()
    return units


def _render(group: list[_Unit]) -> str:
    """Join units, re-emitting a table header when a group starts mid-table."""
    lines: list[str] = []
    for index, unit in enumerate(group):
        if unit.table_header is not None:
            head, rule = unit.table_header
            previously = group[index - 1].text if index > 0 else None
            if previously not in {head, rule}:
                lines.extend([head, rule])
        lines.append(unit.text)
    return "\n".join(lines)


def _overlap_tail(group: list[_Unit], overlap_chars: int) -> list[_Unit]:
    """Trailing units of ``group`` fitting in ``overlap_chars``, measured in whole
    units so the overlap never begins mid-record."""
    tail: list[_Unit] = []
    length = 0
    for unit in reversed(group):
        candidate = len(unit.text) + 1
        if length + candidate > overlap_chars:
            break
        tail.insert(0, unit)
        length += candidate
    return tail


def chunk_document(
    doc_id: str,
    text: str,
    *,
    target_chars: int = DEFAULT_TARGET_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
    min_chars: int = DEFAULT_MIN_CHARS,
) -> list[Chunk]:
    """Chunk a rendered document on structural boundaries.

    ``target_chars`` is a soft ceiling: a single unit longer than the target is
    emitted whole rather than truncated, because truncating a paragraph loses
    exactly the text a gold span might be anchored to.
    """
    if target_chars <= 0:
        raise ValueError("target_chars must be positive")
    if overlap_chars >= target_chars:
        raise ValueError("overlap_chars must be smaller than target_chars")

    units = _units(text)
    if not units:
        return []

    # Group units by size. Groups are kept as units, never re-parsed from
    # rendered text, so char offsets stay valid after the merge below.
    groups: list[list[_Unit]] = []
    group: list[_Unit] = []
    length = 0

    for unit in units:
        unit_len = len(unit.text) + 1
        if group and length + unit_len > target_chars:
            groups.append(group)
            group = _overlap_tail(group, overlap_chars)
            length = sum(len(u.text) + 1 for u in group)
        group.append(unit)
        length += unit_len
    if group:
        groups.append(group)

    # Fold a stub final group into its predecessor rather than emitting a chunk
    # too short to be retrieved meaningfully. Units already contributed by the
    # overlap tail are not added twice.
    if len(groups) >= 2 and len(_render(groups[-1])) < min_chars:
        stub = groups.pop()
        present = {unit.start for unit in groups[-1]}
        groups[-1].extend(unit for unit in stub if unit.start not in present)

    return [
        Chunk(
            doc_id=doc_id,
            seq=seq,
            text=_render(current),
            section=current[0].section,
            char_start=current[0].start,
            char_end=current[-1].end,
        )
        for seq, current in enumerate(groups)
    ]
