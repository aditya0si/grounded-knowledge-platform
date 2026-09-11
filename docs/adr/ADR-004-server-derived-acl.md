# ADR-004 — ACL filtering is server-derived and applied inside the retrieval predicate

- **Status:** Accepted
- **Date:** 2026-09-12

## Context

Multi-tenant RAG systems typically isolate data with a filter of some kind —
`user_id`, `workspace_id`, a namespace, or an ACL list. The common failure is not
the *existence* of the filter but its **provenance** and its **position** in the
pipeline.

Two anti-patterns recur:

- **Client-supplied scope.** The request carries `workspace_id` or a document
  filter, the server passes it through, and authorisation becomes a UI feature.
  The system is only secure for clients that choose to behave.
- **Post-retrieval filtering.** Candidates are fetched by similarity and filtered
  afterwards. Beyond the recall problem described in ADR-001, this means every
  code path that retrieves must remember to filter, and one forgotten path is a
  cross-tenant leak.

The predecessor project had neither a workspace boundary nor a persistent store —
its documents were scoped to an in-process session dict — so the concept does not
exist there at all.

## Decision

1. **Scope is derived server-side from the authenticated principal.** The
   workspace ID and the principal's permission groups come from the verified
   token. A workspace identifier in a request body is ignored, and a test asserts
   that supplying a foreign one changes nothing.
2. **Authorisation is a predicate, not a filter.** `workspace_id = $1 AND
   acl_tags && $2` is part of the `WHERE` clause of both retrieval arms, so the
   candidate set is authorised by construction. There is no path that retrieves
   unauthorised rows and then removes them.
3. **Repositories require a scope to be constructed.** A repository that can be
   instantiated without a workspace is a repository that will eventually be used
   without one. Making the scope a constructor argument turns a forgotten
   authorisation check into a type error rather than a code-review catch.
4. **Routes are authenticated by an explicit allow-list.** A test enumerates the
   application's routes and fails if any route is neither on the public list nor
   behind an auth dependency — so an endpoint added in six months fails the build
   rather than shipping open.

## Consequences

**Positive**

- Cross-tenant leakage becomes a single invariant to test: *for every golden
  question, re-running retrieval as a principal lacking the required tag returns
  the empty set.* This is asserted per question, not sampled, and the CI gate
  requires a leak count of exactly zero.
- The security property survives refactoring of the retrieval strategy, because
  it lives in the predicate rather than in the calling code.
- Permission behaviour is demonstrable rather than asserted: switching the demo
  principal (M8) changes the result set for the same query.

**Negative**

- Every retrieval query must carry the predicate, which slightly couples the
  retrieval layer to the authorisation model.
- Denormalising `acl_tags` onto `chunks` introduces a synchronisation obligation
  between `chunks` and `documents`. Mitigated with a database trigger and a test
  that asserts the two never diverge.
- `acl_tags && $2` with a GIN index is fast at this scale but is not a
  row-level-security audit. This is application-enforced authorisation, not
  defence in depth at the database level. Postgres RLS is a natural hardening
  step and is noted as future work rather than claimed as present.

## Alternatives considered

| Option | Why not |
|---|---|
| **Post-retrieval filtering** | The recall problem from ADR-001, plus one forgotten call site equals a leak. |
| **Vector-store namespaces per tenant** | Workable for tenant isolation, but cannot express *within-workspace* ACLs (a runbook visible to `eng` and not to `hr`), which is the interesting case here. It also reintroduces the fetch-then-filter problem for the inner ACL. |
| **Postgres row-level security only** | Genuinely stronger, and the right eventual answer — it enforces at the database so a bug in application code cannot bypass it. Deferred because it requires session-variable plumbing through the connection pool, and because the application-level invariant is the one this milestone can test exhaustively. |
| **Separate index per tenant** | Operationally heavy, and does not solve the intra-workspace ACL requirement. |
