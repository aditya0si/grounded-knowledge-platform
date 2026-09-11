#!/usr/bin/env python3
"""Build the evaluation corpus, chunk it, and write the golden set.

Writes two things that are committed to the repository:

* ``corpus/docs/*.md`` — every rendered document, so a reader can inspect the
  actual corpus without running code;
* ``eval/golden/questions.jsonl`` — the answer key, with gold chunk ids resolved
  at the chunking configuration used here.

Usage:
    python scripts/build_corpus.py [--target-chars N] [--overlap-chars N]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gkp.eval.chunking import chunk_document  # noqa: E402
from gkp.eval.corpus import corpus_manifest  # noqa: E402
from gkp.eval.corpus_data import build  # noqa: E402
from gkp.eval.golden import build_golden_set, write_golden_set  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-chars", type=int, default=512)
    parser.add_argument("--overlap-chars", type=int, default=64)
    args = parser.parse_args()

    corpus = build()
    docs_dir = ROOT / "corpus" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    for doc_id, text in corpus.rendered.items():
        (docs_dir / f"{doc_id}.md").write_text(text, encoding="utf-8")

    chunks = [
        chunk
        for doc_id in sorted(corpus.rendered)
        for chunk in chunk_document(
            doc_id,
            corpus.rendered[doc_id],
            target_chars=args.target_chars,
            overlap_chars=args.overlap_chars,
        )
    ]

    entries, report = build_golden_set(corpus, chunks)
    golden_hash = write_golden_set(entries, ROOT / "eval" / "golden" / "questions.jsonl")
    (ROOT / "corpus" / "manifest.jsonl").write_text(corpus_manifest(corpus), encoding="utf-8")

    total_chars = sum(len(text) for text in corpus.rendered.values())
    config = Counter(chunk.doc_id for chunk in chunks)
    answerable = [e for e in entries if e.answerable]

    print(f"corpus hash        : {corpus.content_hash}")
    print(f"golden set hash    : {golden_hash}")
    print(f"documents          : {len(corpus.documents)}")
    print(f"total characters   : {total_chars:,}")
    print(
        f"chunks             : {len(chunks)}"
        f"  (target={args.target_chars}c overlap={args.overlap_chars}c)"
    )
    print(f"  per-document min/max : {min(config.values())}/{max(config.values())}")
    print(
        f"gold questions     : {len(entries)}"
        f"  ({len(answerable)} answerable, {len(entries) - len(answerable)} unanswerable)"
    )
    print(f"categories         : {dict(sorted(Counter(e.category for e in entries).items()))}")

    multi = len(report.multi_chunk_spans)
    print(f"spans resolving to >1 chunk : {multi}")
    if multi:
        for span, hits in list(report.multi_chunk_spans.items())[:3]:
            print(f"  {span!r} -> {len(hits)} chunks")

    sizes = sorted(len(chunk.text) for chunk in chunks)
    print(f"chunk size min/median/max : {sizes[0]}/{sizes[len(sizes) // 2]}/{sizes[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
