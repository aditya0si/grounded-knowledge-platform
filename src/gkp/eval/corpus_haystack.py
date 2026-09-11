"""Deterministic haystack generation.

The forty-odd gold-labelled facts in :mod:`gkp.eval.corpus_data` are curated by
hand. They must be embedded in a corpus much larger than the retrieved window,
because retrieval metrics measured over a corpus barely bigger than ``k`` are not
measurements at all: if the corpus holds 20 chunks and the retriever returns 20,
recall@20 is 1.0 by construction and every retrieval strategy looks identical.
That is the prototype's failure mode reproduced at a larger scale, and it is the
single easiest way to build a RAG evaluation that cannot fail.

So the haystack is generated — large, varied, and reproducible from a seed. It is
honest about what it is: templated synthetic prose, not real enterprise
documentation. Its job is to be a realistic *haystack*, which means two things:

* it must be big enough that ``k`` is a small fraction of the corpus;
* it must contain **hard negatives** — documents that share vocabulary with the
  gold questions without answering them. Tickets that discuss retention for a
  different system, escalations unrelated to the paging matrix, latency figures
  for services the tier table does not cover.

Every gold span is checked against every generated document by
:func:`gkp.eval.corpus.build_corpus`, so a haystack document can never
accidentally contain an answer.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from gkp.eval.corpus import AclTag, DocumentSpec, Section

SEED = 20260912

SERVICES = (
    "the ingest gateway",
    "the billing reconciler",
    "the notification fanout",
    "the search indexer",
    "the identity broker",
    "the metrics aggregator",
    "the export worker",
    "the session store",
    "the webhook dispatcher",
    "the recommendation service",
    "the audit log pipeline",
    "the tenant provisioning worker",
    "the document parser",
    "the embedding worker",
    "the reranker",
    "the query planner",
)

SYMPTOMS = (
    "elevated p99 latency",
    "intermittent 502 responses",
    "a growing backlog of unprocessed messages",
    "connection pool exhaustion",
    "a sharp rise in retry volume",
    "degraded throughput",
    "unbounded queue depth growth",
    "repeated leader elections",
    "disk pressure on the primary",
    "a slow memory leak in the worker pool",
    "timeouts against a downstream dependency",
    "a partial outage in one availability zone",
)

CAUSES = (
    "a configuration change that was not rolled out gradually",
    "an upstream dependency quietly raising its timeout",
    "a schema migration holding an exclusive lock",
    "an unindexed query introduced by a recent release",
    "a certificate that expired without an alert firing",
    "a bad rollout of the connection pooler",
    "a runaway batch job competing for I/O",
    "a noisy neighbour on shared hardware",
    "a retry policy with no jitter and no ceiling",
    "a cache key that collided across tenants",
    "a feature flag enabled for a larger cohort than intended",
)

RESOLUTIONS = (
    "rolling back the offending release",
    "raising the pool ceiling and restarting the workers",
    "adding the missing index concurrently",
    "rotating the certificate and adding an expiry alert",
    "splitting the batch job into smaller windows",
    "failing the workload over to the secondary region",
    "adding jitter and a retry ceiling to the client",
    "purging and rebuilding the affected cache entries",
    "disabling the flag and re-enabling it for a smaller cohort",
)

FOLLOWUPS = (
    "Added a saturation dashboard for the connection pool.",
    "Filed a follow-up to introduce a canary stage for this service.",
    "Documented the workaround in the service runbook.",
    "Reviewed the alert threshold, which was too noisy to act on.",
    "Scheduled a dependency upgrade for the next maintenance window.",
    "Added an integration test covering the failure path.",
    "Requested a capacity review for the next quarter.",
    "Added a lint rule to catch the misconfiguration at review time.",
)

TEAMS = (
    "Platform Reliability",
    "Core Services",
    "Data Platform",
    "Security Engineering",
    "Customer Engineering",
    "Developer Experience",
    "Billing Systems",
    "Identity",
)

# Vocabulary deliberately shared with the gold questions. These sentences make
# the haystack adversarial: a lexical retriever will fire on them, and only a
# system that reads them will see they answer nothing.
CONFUSERS = (
    "Related: ticket retention for this subsystem is tracked in a separate "
    "schedule and was not affected by this change.",
    "Note that the escalation path for this service differs from the standard "
    "paging route and is documented by the owning team.",
    "The uptime commitment for this component is reported monthly and excludes "
    "planned maintenance windows.",
    "This change does not alter the classification of the data the service "
    "handles, which remains Internal.",
    "A postmortem was not required for this incident because the impact fell "
    "below the documented threshold.",
    "The rotation schedule for the credentials involved was verified and found to be current.",
    "Approval for this change was obtained through the standard review process "
    "rather than a written sign-off.",
    "Latency figures quoted here are for the service only and are not comparable "
    "with the published tier commitments.",
    "Carry-over of unspent budget for this line item is not permitted under the "
    "current finance policy.",
    "Voting node membership was unchanged, so no split-brain risk was assessed for this event.",
)

BUSINESS_AREAS = (
    "ingest",
    "billing",
    "notifications",
    "search",
    "identity",
    "reporting",
    "exports",
    "tenancy",
    "audit",
    "recommendations",
)

_all_tags: tuple[AclTag, ...] = ("all", "eng", "sec", "hr", "finance")


def _tagged(rng: random.Random) -> tuple[AclTag, ...]:
    """Assign an ACL tag set to a generated document.

    Filler is spread across tags on purpose: a principal without the tag must not
    see it, so a corpus where every document is world-readable would not exercise
    the permission predicate at all.
    """
    roll = rng.random()
    if roll < 0.55:
        return ("eng",)
    if roll < 0.70:
        return ("eng", "sec")
    if roll < 0.80:
        return ("all",)
    if roll < 0.90:
        return ("hr",)
    return ("finance",)


def _month_name(month: int) -> str:
    return date(2020, month, 1).strftime("%B")


def _ticket_archives(rng: random.Random) -> list[DocumentSpec]:
    """One archive document per month. The bulk of the haystack."""
    docs: list[DocumentSpec] = []
    start = date(2025, 1, 1)
    for index in range(20):
        month_start = date(start.year, start.month, 1)
        next_month = date(
            month_start.year + (month_start.month // 12), (month_start.month % 12) + 1, 1
        )
        acl = _tagged(rng)
        sections: list[Section] = []
        for ticket in range(12):
            number = 70000 + index * 137 + ticket * 3
            raised = month_start + timedelta(
                days=rng.randrange(max(1, (next_month - month_start).days))
            )
            service = rng.choice(SERVICES)
            peak = rng.choice(("morning", "afternoon", "evening", "night"))
            paragraphs = [
                f"**Raised:** {raised.isoformat()} · **Severity:** S{rng.randrange(1, 4)} · "
                f"**Owner:** {rng.choice(TEAMS)}",
                f"{service.capitalize()} experienced {rng.choice(SYMPTOMS)} for roughly "
                f"{rng.randrange(4, 190)} minutes during the {peak} traffic peak.",
                f"Root cause was {rng.choice(CAUSES)}.",
                f"Resolved by {rng.choice(RESOLUTIONS)}.",
                rng.choice(FOLLOWUPS),
            ]
            if rng.random() < 0.30:
                paragraphs.append(rng.choice(CONFUSERS))
            sections.append(Section(heading=f"INC-{number}", paragraphs=tuple(paragraphs)))
        docs.append(
            DocumentSpec(
                doc_id=f"tickets-{month_start.year}-{month_start.month:02d}",
                title=f"Incident Tickets — {_month_name(month_start.month)} {month_start.year}",
                doc_type="ticket",
                acl_tags=acl,
                owner=rng.choice(TEAMS),
                sections=tuple(sections),
            )
        )
        start = next_month
    return docs


def _changelogs(rng: random.Random) -> list[DocumentSpec]:
    """Quarterly release notes."""
    docs: list[DocumentSpec] = []
    for year, quarter in (
        (2025, 1),
        (2025, 2),
        (2025, 3),
        (2025, 4),
        (2026, 1),
        (2026, 3),
    ):
        sections: list[Section] = []
        for patch in range(6):
            area = rng.choice(BUSINESS_AREAS)
            paragraphs = [
                f"Updated the {area} pipeline to {rng.choice(RESOLUTIONS)}.",
                f"Reduced p99 latency on the {area} path by roughly "
                f"{rng.randrange(5, 60)}% by {rng.choice(RESOLUTIONS)}.",
            ]
            if rng.random() < 0.25:
                paragraphs.append(rng.choice(CONFUSERS))
            sections.append(
                Section(
                    heading=f"{rng.randrange(3, 6)}.{rng.randrange(10, 40)}.{patch}",
                    paragraphs=tuple(paragraphs),
                )
            )
        docs.append(
            DocumentSpec(
                doc_id=f"changelog-{year}-q{quarter}",
                title=f"Platform Changelog — {year} Q{quarter}",
                doc_type="changelog",
                acl_tags=_tagged(rng),
                owner="Platform Reliability",
                sections=tuple(sections),
            )
        )
    return docs


def _runbooks(rng: random.Random) -> list[DocumentSpec]:
    """One runbook per service, each with a procedure and a rollback."""
    docs: list[DocumentSpec] = []
    for service in rng.sample(SERVICES, k=12):
        slug = service.removeprefix("the ").replace(" ", "-")
        sections = (
            Section(
                "Preconditions",
                paragraphs=(
                    f"Confirm that {service} is reporting healthy before starting. "
                    f"Check the saturation dashboard for the last {rng.randrange(2, 12)} hours.",
                ),
            ),
            Section(
                "Procedure",
                paragraphs=(
                    f"Drain traffic from the affected node by removing it from the load "
                    f"balancer, then {rng.choice(RESOLUTIONS)}.",
                    f"If the condition persists for more than {rng.randrange(3, 25)} minutes, "
                    f"escalate to {rng.choice(TEAMS)} and {rng.choice(RESOLUTIONS)}.",
                ),
            ),
            Section(
                "Rollback",
                paragraphs=(
                    f"Restore the previous configuration and verify that {service} recovers "
                    f"within {rng.randrange(5, 40)} minutes.",
                    rng.choice(CONFUSERS),
                ),
            ),
        )
        docs.append(
            DocumentSpec(
                doc_id=f"runbook-{slug}",
                title=f"Runbook: {service.removeprefix('the ').title()}",
                doc_type="runbook",
                acl_tags=_tagged(rng),
                owner=rng.choice(TEAMS),
                sections=sections,
            )
        )
    return docs


def _decision_records(rng: random.Random) -> list[DocumentSpec]:
    """Internal decision records — the most plausible-looking distractors."""
    docs: list[DocumentSpec] = []
    for index in range(14):
        topic = rng.choice(
            (
                "queue technology",
                "embedding model selection",
                "vector index type",
                "chunking strategy",
                "cache invalidation",
                "tenant isolation model",
                "ingestion concurrency",
                "backpressure",
                "distributed tracing",
                "schema versioning",
                "secret storage",
                "multi-region routing",
                "batch size",
                "retry semantics",
            )
        )
        sections = (
            Section(
                "Context",
                paragraphs=(
                    f"We evaluated options for {topic} affecting {rng.choice(SERVICES)}. "
                    f"The current approach was chosen {rng.randrange(2, 5)} years ago and has not "
                    f"been revisited since.",
                ),
            ),
            Section(
                "Decision",
                paragraphs=(
                    f"We will adopt {rng.choice(RESOLUTIONS)} for {topic}.",
                    rng.choice(CONFUSERS),
                ),
            ),
            Section(
                "Consequences",
                paragraphs=(
                    f"This adds operational surface for {rng.choice(TEAMS)} and requires "
                    f"approximately {rng.randrange(2, 30)} engineer-days.",
                ),
            ),
        )
        docs.append(
            DocumentSpec(
                doc_id=f"decision-record-{index + 1:03d}",
                title=f"Decision Record: {topic.title()}",
                doc_type="standard",
                acl_tags=_tagged(rng),
                owner=rng.choice(TEAMS),
                sections=sections,
            )
        )
    return docs


def _vendor_notes(rng: random.Random) -> list[DocumentSpec]:
    """Finance-tagged vendor records."""
    docs: list[DocumentSpec] = []
    vendors = (
        "Helio Compute",
        "Marchmont Data",
        "Kestrel Observability",
        "Brightline CDN",
        "Northgate Storage",
        "Pinewood Analytics",
        "Cobalt Identity",
        "Riverton Messaging",
    )
    for vendor in vendors:
        sections = (
            Section(
                "Summary",
                paragraphs=(
                    f"{vendor} provides {rng.choice(BUSINESS_AREAS)} capacity under a "
                    f"{rng.randrange(12, 36)} month agreement renewed annually.",
                    rng.choice(CONFUSERS),
                ),
            ),
            Section(
                "Commercial terms",
                paragraphs=(
                    f"Committed spend is reviewed each quarter by {rng.choice(TEAMS)}. "
                    f"Overages are billed in arrears at the contracted rate.",
                ),
            ),
        )
        docs.append(
            DocumentSpec(
                doc_id=f"vendor-{vendor.lower().replace(' ', '-')}",
                title=f"Vendor Record: {vendor}",
                doc_type="policy",
                acl_tags=("finance",),
                owner="Finance Operations",
                sections=sections,
            )
        )
    return docs


def _meeting_notes(rng: random.Random) -> list[DocumentSpec]:
    """Weekly notes — short, numerous, and full of shared vocabulary."""
    docs: list[DocumentSpec] = []
    start = date(2026, 3, 2)
    for index in range(14):
        when = start + timedelta(weeks=index)
        service = rng.choice(SERVICES)
        sections = (
            Section(
                "Discussion",
                paragraphs=(
                    f"Reviewed performance of {service} over the previous week. "
                    f"{rng.choice(SYMPTOMS).capitalize()} was observed during "
                    f"{rng.randrange(1, 4)} separate windows.",
                    rng.choice(CONFUSERS),
                ),
            ),
            Section(
                "Actions",
                paragraphs=(
                    f"{rng.choice(TEAMS)} to {rng.choice(RESOLUTIONS)} before the next review.",
                    rng.choice(FOLLOWUPS),
                ),
            ),
        )
        docs.append(
            DocumentSpec(
                doc_id=f"meeting-notes-{when.isoformat()}",
                title=f"Reliability Review — {when.isoformat()}",
                doc_type="policy",
                acl_tags=_tagged(rng),
                owner=rng.choice(TEAMS),
                sections=sections,
            )
        )
    return docs


def generate_haystack() -> tuple[DocumentSpec, ...]:
    """Generate the full haystack deterministically.

    Seeded, so the corpus content hash is stable across runs and a published
    result is attributable to an exact corpus revision.
    """
    rng = random.Random(SEED)  # noqa: S311 - seeded for reproducibility, not security
    docs: list[DocumentSpec] = []
    docs.extend(_ticket_archives(rng))
    docs.extend(_changelogs(rng))
    docs.extend(_runbooks(rng))
    docs.extend(_decision_records(rng))
    docs.extend(_vendor_notes(rng))
    docs.extend(_meeting_notes(rng))
    return tuple(docs)
