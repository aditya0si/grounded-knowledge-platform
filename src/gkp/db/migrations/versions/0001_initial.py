"""Initial schema: documents and chunks with pgvector and tsvector.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-12

Notes on two things a reader might expect to see done differently:

* ``chunks.tsv`` is a **generated column**. ``to_tsvector(regconfig, text)`` is
  immutable, so Postgres maintains it and it cannot drift from the text it
  indexes. A trigger would be a second moving part with no benefit.
* ``chunks.acl_tags`` is denormalised from ``documents`` and kept in sync by a
  trigger. The permission predicate has to be satisfiable in the same index scan
  that produces retrieval candidates (ADR-001, ADR-004), which rules out a join
  back to ``documents`` on the hot path.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

#: Must match ``gkp.db.models.EMBEDDING_DIM``. Changing the embedding model is a
#: migration plus a reindex by design.
EMBEDDING_DIM = 384


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "documents",
        sa.Column("id", sa.String(128), primary_key=True),
        sa.Column("workspace_id", sa.String(64), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("doc_type", sa.String(32), nullable=False),
        sa.Column("owner", sa.Text(), nullable=False, server_default=""),
        # text[] not varchar[]: the retrieval predicate applies && against a
        # text[] parameter, and no varchar[] && text[] operator exists.
        sa.Column("acl_tags", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("superseded_by", sa.String(128), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_documents_workspace", "documents", ["workspace_id"])
    op.create_index("ix_documents_checksum", "documents", ["checksum"])

    op.create_table(
        "chunks",
        sa.Column("id", sa.String(192), primary_key=True),
        sa.Column(
            "document_id",
            sa.String(128),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("workspace_id", sa.String(64), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("section", sa.Text(), nullable=False, server_default=""),
        sa.Column("char_start", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("char_end", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("acl_tags", postgresql.ARRAY(sa.Text()), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column(
            "tsv",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('english', text || ' ' || section)",
                persisted=True,
            ),
            nullable=True,
        ),
    )

    # The ACL predicate and the workspace scope are on every retrieval query, so
    # they are indexed; the hot path is a filtered ANN scan, not a full scan.
    op.create_index("ix_chunks_workspace", "chunks", ["workspace_id"])
    op.create_index("ix_chunks_document", "chunks", ["document_id"])
    op.create_index("ix_chunks_acl_tags", "chunks", ["acl_tags"], postgresql_using="gin")
    op.create_index("ix_chunks_tsv", "chunks", ["tsv"], postgresql_using="gin")
    op.execute(
        "CREATE INDEX ix_chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops)"
    )

    # Keep the denormalised ACL copy honest. Without this, a document whose tags
    # are narrowed would keep chunks readable under the old tags — a silent
    # permission expansion, which is the worst possible direction for this bug.
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_chunk_acl_tags() RETURNS trigger AS $$
        BEGIN
            IF NEW.acl_tags IS DISTINCT FROM OLD.acl_tags THEN
                UPDATE chunks SET acl_tags = NEW.acl_tags
                WHERE document_id = NEW.id;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_documents_acl_tags
        AFTER UPDATE ON documents
        FOR EACH ROW EXECUTE FUNCTION sync_chunk_acl_tags();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_documents_acl_tags ON documents")
    op.execute("DROP FUNCTION IF EXISTS sync_chunk_acl_tags()")
    op.drop_table("chunks")
    op.drop_table("documents")
