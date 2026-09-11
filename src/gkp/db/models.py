"""SQLAlchemy models.

Two deliberate choices worth stating, because both look like denormalisation and
are not:

* ``chunks.acl_tags`` duplicates ``documents.acl_tags``. The permission predicate
  must be satisfiable inside the same index scan that produces retrieval
  candidates, and a join back to ``documents`` on the hot path would defeat the
  point of ADR-004. A trigger keeps the copies in sync and a test asserts they
  never diverge.
* ``chunks.tsv`` is a generated column rather than a trigger-maintained one:
  ``to_tsvector(regconfig, text)`` is immutable, so Postgres can maintain it
  itself and the sparse arm cannot drift from the text it indexes.
"""

from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#: Dimension of the embedding column. Changing the embedding model requires a
#: migration and a reindex; that is a deliberate speed bump, not an oversight.
EMBEDDING_DIM = 384


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    doc_type: Mapped[str] = mapped_column(String(32), nullable=False)
    owner: Mapped[str] = mapped_column(Text, nullable=False, default="")
    #: ``text[]`` rather than ``varchar[]``: the retrieval predicate uses the
    #: array-overlap operator against a ``text[]`` parameter, and there is no
    #: ``varchar[] && text[]`` operator. Element length limits on an ACL tag
    #: would not be enforced usefully anyway.
    acl_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    superseded_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    #: sha256 of the source bytes. The idempotency key for re-ingestion (M4).
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    chunks: Mapped[list[Chunk]] = relationship(
        back_populates="document", cascade="all, delete-orphan", lazy="selectin"
    )


class Chunk(Base):
    __tablename__ = "chunks"

    #: ``{doc_id}#{seq}`` — stable, and readable in an eval dump.
    id: Mapped[str] = mapped_column(String(192), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    workspace_id: Mapped[str] = mapped_column(String(64), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[str] = mapped_column(Text, nullable=False, default="")
    char_start: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    char_end: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    #: Denormalised from the owning document. See the module docstring.
    acl_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    tsv: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    document: Mapped[Document] = relationship(back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_workspace", "workspace_id"),
        Index("ix_chunks_document", "document_id"),
        Index(
            "ix_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_chunks_tsv", "tsv", postgresql_using="gin"),
        Index("ix_chunks_acl_tags", "acl_tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<Chunk {self.id} section={self.section!r}>"
