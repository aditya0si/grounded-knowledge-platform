"""Dense (vector) retrieval arm.

Both the workspace scope and the ACL predicate are part of the ``WHERE`` clause,
not applied to the results afterwards. That is the whole point of ADR-001 and
ADR-004: the candidate set is authorised by construction, so no code path can
retrieve rows the principal may not see and then forget to remove them.

Embeddings are passed as a vector literal rather than via an asyncpg codec
registration. That keeps the query portable across drivers and means the SQL in
this file is the SQL you can paste into ``psql`` to debug it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ["DenseHit", "dense_search", "vector_literal"]

DENSE_SQL = text(
    """
    SELECT
        c.id            AS chunk_id,
        c.document_id   AS document_id,
        c.seq           AS seq,
        c.section       AS section,
        c.text          AS text,
        1 - (c.embedding <=> CAST(:embedding AS vector)) AS score
    FROM chunks c
    WHERE c.workspace_id = :workspace_id
      AND c.acl_tags && CAST(:acl_tags AS text[])
    ORDER BY c.embedding <=> CAST(:embedding AS vector)
    LIMIT :limit
    """
)


@dataclass(frozen=True)
class DenseHit:
    chunk_id: str
    document_id: str
    seq: int
    section: str
    text: str
    score: float


def vector_literal(vector: np.ndarray) -> str:
    """Render an embedding as a pgvector literal: ``[0.1,0.2,...]``."""
    values = np.asarray(vector, dtype=np.float32).ravel()
    return "[" + ",".join(f"{float(v):.6f}" for v in values) + "]"


async def dense_search(
    session: AsyncSession,
    *,
    embedding: np.ndarray,
    workspace_id: str,
    acl_tags: tuple[str, ...] | list[str],
    limit: int,
) -> list[DenseHit]:
    """Return the top ``limit`` chunks visible to a principal holding ``acl_tags``.

    An empty ``acl_tags`` yields no rows by construction: ``&&`` against an empty
    array is false, so a principal with no grants sees nothing rather than
    everything. That direction of failure is chosen deliberately.
    """
    if limit <= 0:
        return []

    result = await session.execute(
        DENSE_SQL,
        {
            "embedding": vector_literal(embedding),
            "workspace_id": workspace_id,
            "acl_tags": list(acl_tags),
            "limit": limit,
        },
    )
    return [
        DenseHit(
            chunk_id=row.chunk_id,
            document_id=row.document_id,
            seq=row.seq,
            section=row.section,
            text=row.text,
            score=float(row.score),
        )
        for row in result
    ]
