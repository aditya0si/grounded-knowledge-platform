"""Curated corpus content: the internal knowledge base of a fictional company.

Northwind Systems is invented so that the corpus can be published without
redaction and so that ground truth is knowable by construction. Document values
are deliberately allocated so that no gold span occurs in more than one
document; :func:`gkp.eval.corpus.build_corpus` enforces this rather than trusting
the author to have been careful.

The corpus is built to be hostile in four specific ways, each asserted in
``tests/test_corpus.py``:

1. **Version families** — ``incident-response-policy`` and ``leave-policy`` each
   exist in multiple revisions that differ *only* in their numbers. A retriever
   that finds a plausible-looking revision has not necessarily found the
   authoritative one.
2. **Tables** — two documents are largely tabular, so character-based chunking
   splits rows mid-record.
3. **Cross-references** — the database failover runbook defers to a section of
   the network partition runbook, so the answer needs two hops.
4. **Lexical distractors** — ``disaster-recovery-overview`` shares retention and
   recovery vocabulary with the incident policy and answers none of it.
"""

from __future__ import annotations

from gkp.eval.corpus import (
    BuiltCorpus,
    DocumentSpec,
    Fact,
    Section,
    TableSpec,
    UnanswerableQuestion,
    build_corpus,
)
from gkp.eval.corpus_haystack import generate_haystack

# --------------------------------------------------------------------------
# Documents
# --------------------------------------------------------------------------

_INCIDENT_SECTIONS_V1 = (
    Section(
        "Retention",
        paragraphs=(
            "Incident tickets are retained for 180 days after closure, after which they are "
            "deleted from the incident management system.",
            "Retention is counted from the moment an incident is marked resolved, not from the "
            "moment the page was raised.",
        ),
    ),
    Section(
        "Severity definitions",
        paragraphs=(
            "Severity 1 incidents are defined as outages affecting more than 25% of customers "
            "in a single region.",
            "Severity 2 incidents are defined as degraded performance affecting a single service "
            "tier without a full outage.",
        ),
    ),
    Section(
        "Acknowledgement targets",
        paragraphs=(
            "Severity 1 incidents must be acknowledged by the on-call engineer within 10 minutes "
            "of the page being raised.",
        ),
    ),
    Section(
        "Postmortems",
        paragraphs=(
            "A postmortem document must be published within 5 business days of a Severity 1 "
            "incident being resolved.",
        ),
    ),
)

_INCIDENT_SECTIONS_V2 = (
    Section(
        "Retention",
        paragraphs=(
            "Incident tickets are retained for 365 days after closure, after which they are "
            "deleted from the incident management system.",
            "Retention is counted from the moment an incident is marked resolved, not from the "
            "moment the page was raised.",
        ),
    ),
    Section(
        "Severity definitions",
        paragraphs=(
            "Severity 1 incidents are defined as outages affecting more than 20% of customers "
            "in a single region.",
            "Severity 2 incidents are defined as degraded performance affecting a single service "
            "tier without a full outage.",
        ),
    ),
    Section(
        "Acknowledgement targets",
        paragraphs=(
            "Severity 1 incidents must be acknowledged by the on-call engineer within 20 minutes "
            "of the page being raised.",
        ),
    ),
    Section(
        "Postmortems",
        paragraphs=(
            "A postmortem document must be published within 3 business days of a Severity 1 "
            "incident being resolved.",
        ),
    ),
)

_INCIDENT_SECTIONS_V3 = (
    Section(
        "Retention",
        paragraphs=(
            "Incident tickets are retained for 400 days after closure, after which they are "
            "deleted from the incident management system.",
            "Retention is measured from the moment an incident is marked resolved rather than "
            "from the moment the page was raised.",
        ),
    ),
    Section(
        "Severity definitions",
        paragraphs=(
            "Severity 1 incidents are defined as outages affecting more than 20% of customers "
            "across all regions.",
            "Severity 2 incidents are defined as degradation affecting one service tier without "
            "a full outage.",
        ),
    ),
    Section(
        "Acknowledgement targets",
        paragraphs=(
            "Severity 1 incidents must be acknowledged by the on-call engineer within 15 minutes "
            "of the page being raised.",
        ),
    ),
    Section(
        "Postmortems",
        paragraphs=(
            "A postmortem document must be published within 2 business days of a Severity 1 "
            "incident being resolved.",
        ),
    ),
)

DOCUMENTS: tuple[DocumentSpec, ...] = (
    # -- version family 1: incident response -------------------------------
    DocumentSpec(
        doc_id="incident-response-policy-v1",
        title="Incident Response Policy",
        doc_type="policy",
        acl_tags=("eng", "sec"),
        owner="Platform Reliability",
        version=1,
        sections=_INCIDENT_SECTIONS_V1,
    ),
    DocumentSpec(
        doc_id="incident-response-policy-v2",
        title="Incident Response Policy",
        doc_type="policy",
        acl_tags=("eng", "sec"),
        owner="Platform Reliability",
        version=2,
        supersedes="incident-response-policy-v1",
        sections=_INCIDENT_SECTIONS_V2,
    ),
    DocumentSpec(
        doc_id="incident-response-policy-v3",
        title="Incident Response Policy",
        doc_type="policy",
        acl_tags=("eng", "sec"),
        owner="Platform Reliability",
        version=3,
        supersedes="incident-response-policy-v2",
        sections=_INCIDENT_SECTIONS_V3,
    ),
    # -- version family 2: leave -------------------------------------------
    DocumentSpec(
        doc_id="leave-policy-v1",
        title="Leave Policy",
        doc_type="hr-policy",
        acl_tags=("hr",),
        owner="People Operations",
        version=1,
        sections=(
            Section(
                "Annual leave",
                paragraphs=(
                    "Every full-time employee accrues 20 days of paid annual leave per calendar "
                    "year, credited monthly.",
                    "Leave requests must be submitted at least fourteen days before the first day "
                    "of absence.",
                ),
            ),
            Section(
                "Carry-over",
                paragraphs=(
                    "Unused annual leave may be carried over to the following year up to a "
                    "maximum of 5 days.",
                    "Leave carried over beyond the cap is forfeited and cannot be encashed.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        doc_id="leave-policy-v2",
        title="Leave Policy",
        doc_type="hr-policy",
        acl_tags=("hr",),
        owner="People Operations",
        version=2,
        supersedes="leave-policy-v1",
        sections=(
            Section(
                "Annual leave",
                paragraphs=(
                    "Every full-time employee accrues 24 days of paid annual leave per calendar "
                    "year, credited monthly.",
                    "Requests for leave must reach the employee's manager no later than fourteen "
                    "days before the absence begins.",
                ),
            ),
            Section(
                "Carry-over",
                paragraphs=(
                    "Unused annual leave may be carried over to the following year up to a "
                    "maximum of 10 days.",
                    "Leave carried over beyond the cap is forfeited and cannot be encashed.",
                ),
            ),
        ),
    ),
    # -- tables ------------------------------------------------------------
    DocumentSpec(
        doc_id="service-tiers",
        title="Service Tier Commitments",
        doc_type="table",
        acl_tags=("all",),
        owner="Customer Engineering",
        sections=(
            Section(
                "Tier commitments",
                paragraphs=(
                    "Each service tier carries a monthly uptime commitment and a p95 request "
                    "latency target, measured per calendar month.",
                ),
                table=TableSpec(
                    headers=("Tier", "Monthly uptime", "p95 latency", "Support response"),
                    rows=(
                        ("Platinum", "99.95%", "180 ms", "30 minutes"),
                        ("Gold", "99.90%", "420 ms", "4 hours"),
                        ("Silver", "99.50%", "950 ms", "1 business day"),
                    ),
                ),
            ),
            Section(
                "Service credits",
                paragraphs=(
                    "Falling below the committed uptime for a tier entitles the customer to a "
                    "service credit against the following month's invoice.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        doc_id="oncall-escalation-matrix",
        title="On-Call Escalation Matrix",
        doc_type="table",
        acl_tags=("eng",),
        owner="Platform Reliability",
        sections=(
            Section(
                "Escalation targets",
                paragraphs=(
                    "Unacknowledged pages escalate automatically according to the table below, "
                    "measured from the initial page.",
                ),
                table=TableSpec(
                    headers=("Step", "Escalates to", "After"),
                    rows=(
                        ("1", "Primary on-call engineer", "7 minutes"),
                        ("2", "Secondary on-call engineer", "45 minutes"),
                        ("3", "Engineering duty manager", "9 hours"),
                    ),
                ),
            ),
            Section(
                "Overrides",
                paragraphs=(
                    "A duty manager may pause automatic escalation during a declared major "
                    "incident to avoid paging additional responders.",
                ),
            ),
        ),
    ),
    # -- cross-referenced runbooks -----------------------------------------
    DocumentSpec(
        doc_id="runbook-database-failover",
        title="Runbook: Database Failover",
        doc_type="runbook",
        acl_tags=("eng",),
        owner="Platform Reliability",
        sections=(
            Section(
                "Preconditions",
                paragraphs=(
                    "Confirm that the replica is streaming before promoting it. Promotion of a "
                    "lagging replica causes silent data loss.",
                ),
            ),
            Section(
                "Procedure",
                paragraphs=(
                    "Step one is to fence the primary by revoking its write credentials. Step two "
                    "is to promote the replica and repoint the connection pooler.",
                    "If the primary is unreachable rather than unhealthy, follow the partition "
                    "procedure in section 3.2 of the network partition runbook before promoting.",
                ),
            ),
            Section(
                "Validation",
                paragraphs=(
                    "After promotion, verify that write throughput recovers to at least 8500 "
                    "transactions per second before declaring the failover complete.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        doc_id="runbook-network-partition",
        title="Runbook: Network Partition",
        doc_type="runbook",
        acl_tags=("eng",),
        owner="Platform Reliability",
        sections=(
            Section(
                "Detection",
                paragraphs=(
                    "A partition is confirmed when two or more availability zones lose peer "
                    "connectivity for longer than 30 seconds while remaining individually healthy.",
                ),
            ),
            Section(
                "2. Immediate actions",
                paragraphs=(
                    "Stop automated failover before investigating. An automated failover during a "
                    "partition promotes replicas on both sides and produces split brain.",
                ),
            ),
            Section(
                "3. Recovery decision",
                paragraphs=(
                    "Determine which side holds the majority of voting nodes. The minority side "
                    "must be held read-only until connectivity is restored.",
                ),
            ),
            Section(
                "3.2 Handling an unreachable primary",
                paragraphs=(
                    "When the primary is unreachable and holds the minority of voting nodes, "
                    "decommission it by removing its vote rather than waiting for it to return.",
                    "Only after the primary has been decommissioned may the replica be promoted "
                    "and the connection pooler repointed.",
                ),
            ),
        ),
    ),
    # -- security ----------------------------------------------------------
    DocumentSpec(
        doc_id="key-rotation-policy",
        title="Key Rotation Policy",
        doc_type="standard",
        acl_tags=("sec",),
        owner="Security Engineering",
        sections=(
            Section(
                "Rotation intervals",
                paragraphs=(
                    "Service API keys must be rotated at least every 90 days.",
                    "Root account access keys must be rotated every 270 days and may not be used "
                    "for programmatic access.",
                ),
            ),
            Section(
                "Emergency rotation",
                paragraphs=(
                    "A key suspected of exposure must be rotated immediately, regardless of its "
                    "position in the rotation schedule.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        doc_id="data-classification-standard",
        title="Data Classification Standard",
        doc_type="standard",
        acl_tags=("sec", "eng"),
        owner="Security Engineering",
        sections=(
            Section(
                "Tiers",
                paragraphs=(
                    "Data is classified as Public, Internal, Confidential, or Restricted. "
                    "Restricted data may be processed only in approved regions.",
                ),
            ),
            Section(
                "Retention by tier",
                paragraphs=(
                    "Confidential records must be retained for 10 years before review for "
                    "deletion.",
                    "Restricted records are retained indefinitely unless a valid erasure request "
                    "is received.",
                ),
            ),
        ),
    ),
    # -- register variety --------------------------------------------------
    DocumentSpec(
        doc_id="changelog-2026-q2",
        title="Platform Changelog — 2026 Q2",
        doc_type="changelog",
        acl_tags=("eng",),
        owner="Platform Reliability",
        sections=(
            Section(
                "4.18.0",
                paragraphs=(
                    "Introduced connection pooler support for the read replica path. This release "
                    "reduced failover duration by roughly half.",
                ),
            ),
            Section(
                "4.19.0",
                paragraphs=(
                    "Added structured logging for escalation events and a dashboard for "
                    "unacknowledged pages.",
                ),
            ),
            Section(
                "4.20.0",
                paragraphs=(
                    "Deprecated the legacy vector ingestion endpoint. It returns HTTP 410 as of "
                    "this release and will be removed in 5.0.0.",
                ),
            ),
        ),
    ),
    DocumentSpec(
        doc_id="tickets-2026-09",
        title="Incident Tickets — September 2026",
        doc_type="ticket",
        acl_tags=("eng",),
        owner="Platform Reliability",
        sections=(
            Section(
                "INC-88421",
                paragraphs=(
                    "Elevated p99 latency on the ingest gateway traced to connection pool "
                    "exhaustion. Resolved by raising the pool ceiling.",
                ),
            ),
            Section(
                "INC-88455",
                paragraphs=(
                    "Duplicate embeddings written after a retry storm. Required a full reindex of "
                    "the affected tenant.",
                ),
            ),
            Section(
                "INC-88490",
                paragraphs=(
                    "Relevance regression reported by a customer following a chunking change. "
                    "Traced to chunk boundaries splitting a pricing table.",
                ),
            ),
        ),
    ),
    # -- distractor --------------------------------------------------------
    DocumentSpec(
        doc_id="disaster-recovery-overview",
        title="Disaster Recovery Overview",
        doc_type="standard",
        acl_tags=("eng",),
        owner="Platform Reliability",
        sections=(
            Section(
                "Objectives",
                paragraphs=(
                    "Northwind Systems targets a recovery point objective of 22 minutes and a "
                    "recovery time objective of 12 hours for tier one services.",
                    "These objectives describe our ambition, not a contractual commitment. "
                    "Contractual commitments are recorded in the service tier documents.",
                ),
            ),
            Section(
                "Scope",
                paragraphs=(
                    "This overview does not describe incident handling, retention of incident "
                    "records, or paging procedures. Those are governed by the incident response "
                    "policy and the on-call escalation matrix.",
                ),
            ),
        ),
    ),
    # -- finance -----------------------------------------------------------
    DocumentSpec(
        doc_id="procurement-guidelines",
        title="Procurement Guidelines",
        doc_type="policy",
        acl_tags=("finance",),
        owner="Finance Operations",
        sections=(
            Section(
                "Approval thresholds",
                paragraphs=(
                    "Purchases above 5000 USD require written approval from a department head.",
                    "Purchases above 25000 USD additionally require approval from the finance "
                    "committee.",
                ),
            ),
            Section(
                "Vendor onboarding",
                paragraphs=(
                    "Every vendor handling Internal data or above must complete a security review "
                    "before a contract is signed.",
                ),
            ),
        ),
    ),
)


# --------------------------------------------------------------------------
# Answerable facts
# --------------------------------------------------------------------------

FACTS: tuple[Fact, ...] = (
    # -- incident policy: the version-conflict set -------------------------
    Fact(
        id="f_ir_retention_current",
        doc_id="incident-response-policy-v3",
        section="Retention",
        span="retained for 400 days after closure",
        question="How long are incident tickets retained under the current policy?",
        category="version-conflict",
        notes="v1 says 180 days and v2 says 365 days; both are lexical distractors.",
    ),
    Fact(
        id="f_ir_retention_v1",
        doc_id="incident-response-policy-v1",
        section="Retention",
        span="retained for 180 days after closure",
        question="What retention period did the very first incident response policy specify?",
        category="version-conflict",
    ),
    Fact(
        id="f_ir_retention_v2",
        doc_id="incident-response-policy-v2",
        section="Retention",
        span="retained for 365 days after closure",
        question="What retention period did the second revision of the incident response policy "
        "introduce?",
        category="version-conflict",
    ),
    Fact(
        id="f_ir_ack_current",
        doc_id="incident-response-policy-v3",
        section="Acknowledgement targets",
        span="within 15 minutes of the page being raised",
        question="What is the current acknowledgement target for a Severity 1 incident?",
        category="version-conflict",
        notes="v1 says 10 minutes, v2 says 20 minutes.",
    ),
    Fact(
        id="f_ir_postmortem_current",
        doc_id="incident-response-policy-v3",
        section="Postmortems",
        span="within 2 business days of a Severity 1",
        question="How quickly must a postmortem be published after a Severity 1 incident?",
        category="version-conflict",
    ),
    Fact(
        id="f_ir_sev1_v1",
        doc_id="incident-response-policy-v1",
        section="Severity definitions",
        span="more than 25% of customers in a single region",
        question="How was a Severity 1 incident originally defined in terms of customer impact?",
        category="version-conflict",
    ),
    Fact(
        id="f_ir_sev1_v3",
        doc_id="incident-response-policy-v3",
        section="Severity definitions",
        span="more than 20% of customers across all regions",
        question="How is a Severity 1 incident defined today?",
        category="version-conflict",
    ),
    Fact(
        id="f_ir_sev2",
        doc_id="incident-response-policy-v3",
        section="Severity definitions",
        span="degradation affecting one service tier",
        question="What counts as a Severity 2 incident?",
        category="policy-lookup",
    ),
    Fact(
        id="f_ir_retention_clock",
        doc_id="incident-response-policy-v3",
        section="Retention",
        span="Retention is measured from the moment an incident is marked resolved",
        question="From what point does incident ticket retention begin counting?",
        category="policy-lookup",
        notes="v1 and v2 carry a near-identical sentence with different phrasing: the "
        "lexical distractor, and the reason this span must be checked for uniqueness.",
    ),
    # -- service tier table ------------------------------------------------
    # Spans are cell-plus-label slices of a table row, e.g. the row
    #   | Platinum | 99.95% | 180 ms | 30 minutes |
    # contains "Platinum | 99.95%" as a contiguous substring. Distinct per cell,
    # and distinctive enough that generated haystack prose cannot collide with
    # them the way a bare "45 minutes" would.
    Fact(
        id="f_tier_platinum_uptime",
        doc_id="service-tiers",
        section="Tier commitments",
        span="Platinum | 99.95%",
        question="What monthly uptime commitment does the Platinum tier carry?",
        category="table-lookup",
    ),
    Fact(
        id="f_tier_gold_uptime",
        doc_id="service-tiers",
        section="Tier commitments",
        span="Gold | 99.90%",
        question="What is the uptime commitment for the Gold service tier?",
        category="table-lookup",
    ),
    Fact(
        id="f_tier_silver_uptime",
        doc_id="service-tiers",
        section="Tier commitments",
        span="Silver | 99.50%",
        question="What uptime does the Silver tier commit to each month?",
        category="table-lookup",
    ),
    Fact(
        id="f_tier_platinum_latency",
        doc_id="service-tiers",
        section="Tier commitments",
        span="Platinum | 99.95% | 180 ms",
        question="What p95 latency target applies to Platinum tier customers?",
        category="table-lookup",
    ),
    Fact(
        id="f_tier_gold_latency",
        doc_id="service-tiers",
        section="Tier commitments",
        span="Gold | 99.90% | 420 ms",
        question="What is the p95 latency target for the Gold tier?",
        category="table-lookup",
    ),
    Fact(
        id="f_tier_silver_response",
        doc_id="service-tiers",
        section="Tier commitments",
        span="Silver | 99.50% | 950 ms | 1 business day",
        question="How quickly does Silver tier support respond to a request?",
        category="table-lookup",
    ),
    Fact(
        id="f_tier_credits",
        doc_id="service-tiers",
        section="Service credits",
        span="service credit against the following month's invoice",
        question="What remedy does a customer receive if uptime falls below their tier commitment?",
        category="policy-lookup",
    ),
    # -- escalation matrix -------------------------------------------------
    Fact(
        id="f_esc_step2",
        doc_id="oncall-escalation-matrix",
        section="Escalation targets",
        span="Secondary on-call engineer | 45 minutes",
        question="After how long does an unacknowledged page escalate to the secondary engineer?",
        category="table-lookup",
    ),
    Fact(
        id="f_esc_step3",
        doc_id="oncall-escalation-matrix",
        section="Escalation targets",
        span="Engineering duty manager | 9 hours",
        question="When does an unacknowledged page reach the engineering duty manager?",
        category="table-lookup",
    ),
    Fact(
        id="f_esc_override",
        doc_id="oncall-escalation-matrix",
        section="Overrides",
        span="pause automatic escalation during a declared major incident",
        question="Can automatic paging escalation be stopped, and under what circumstances?",
        category="policy-lookup",
    ),
    # -- cross-document, multi-hop -----------------------------------------
    Fact(
        id="f_failover_partition_ref",
        doc_id="runbook-database-failover",
        section="Procedure",
        span="follow the partition procedure in section 3.2 of the network partition runbook",
        question="What should you do when a database primary is unreachable rather than unhealthy?",
        category="multi-hop",
        notes="The answer routes to runbook-network-partition; both chunks are needed.",
    ),
    Fact(
        id="f_partition_32_decommission",
        doc_id="runbook-network-partition",
        section="3.2 Handling an unreachable primary",
        span="decommission it by removing its vote rather than waiting for it to return",
        question="How should an unreachable primary holding a minority of voting nodes be handled?",
        category="multi-hop",
    ),
    Fact(
        id="f_partition_stop_auto",
        doc_id="runbook-network-partition",
        section="2. Immediate actions",
        span="promotes replicas on both sides and produces split brain",
        question="What happens if automated failover is left running during a network partition?",
        category="multi-hop",
    ),
    Fact(
        id="f_failover_throughput",
        doc_id="runbook-database-failover",
        section="Validation",
        span="8500 transactions per second",
        question="What write throughput must be confirmed before a database failover is declared "
        "complete?",
        category="policy-lookup",
    ),
    Fact(
        id="f_failover_fence",
        doc_id="runbook-database-failover",
        section="Procedure",
        span="fence the primary by revoking its write credentials",
        question="What is the first step of the database failover procedure?",
        category="policy-lookup",
    ),
    # -- restricted: hr ----------------------------------------------------
    Fact(
        id="f_leave_annual_current",
        doc_id="leave-policy-v2",
        section="Annual leave",
        span="accrues 24 days of paid annual leave",
        question="How many days of paid annual leave does a full-time employee accrue?",
        category="restricted",
        notes="Only a principal holding the hr tag may retrieve this.",
    ),
    Fact(
        id="f_leave_annual_v1",
        doc_id="leave-policy-v1",
        section="Annual leave",
        span="accrues 20 days of paid annual leave",
        question="How much annual leave did the original leave policy grant?",
        category="restricted",
    ),
    Fact(
        id="f_leave_carryover_current",
        doc_id="leave-policy-v2",
        section="Carry-over",
        span="maximum of 10 days",
        question="What is the cap on unused annual leave that may be carried into the next year?",
        category="restricted",
        notes="The superseded policy capped this at 5 days.",
    ),
    Fact(
        id="f_leave_notice",
        doc_id="leave-policy-v2",
        section="Annual leave",
        span="no later than fourteen days before the absence begins",
        question="How much notice must be given before taking annual leave?",
        category="restricted",
    ),
    # -- restricted: security ----------------------------------------------
    Fact(
        id="f_key_api_rotation",
        doc_id="key-rotation-policy",
        section="Rotation intervals",
        span="rotated at least every 90 days",
        question="How often must service API keys be rotated?",
        category="restricted",
    ),
    Fact(
        id="f_key_root_rotation",
        doc_id="key-rotation-policy",
        section="Rotation intervals",
        span="rotated every 270 days",
        question="What is the rotation interval for root account access keys?",
        category="restricted",
    ),
    Fact(
        id="f_key_emergency",
        doc_id="key-rotation-policy",
        section="Emergency rotation",
        span="rotated immediately, regardless of its position in the rotation schedule",
        question="What is the process when a key is suspected of exposure?",
        category="restricted",
    ),
    Fact(
        id="f_classification_confidential_retention",
        doc_id="data-classification-standard",
        section="Retention by tier",
        span="retained for 10 years before review for deletion",
        question="How long must Confidential records be retained before they are reviewed for "
        "deletion?",
        category="restricted",
    ),
    Fact(
        id="f_classification_restricted_regions",
        doc_id="data-classification-standard",
        section="Tiers",
        span="processed only in approved regions",
        question="Where may Restricted data be processed?",
        category="restricted",
    ),
    # -- registers ---------------------------------------------------------
    Fact(
        id="f_changelog_pooler",
        doc_id="changelog-2026-q2",
        section="4.18.0",
        span="reduced failover duration by roughly half",
        question="What effect did the 4.18.0 release have on failover duration?",
        category="policy-lookup",
    ),
    Fact(
        id="f_changelog_deprecated",
        doc_id="changelog-2026-q2",
        section="4.20.0",
        span="returns HTTP 410 as of this release",
        question="What status code does the deprecated vector ingestion endpoint now return?",
        category="policy-lookup",
    ),
    Fact(
        id="f_ticket_split_table",
        doc_id="tickets-2026-09",
        section="INC-88490",
        span="chunk boundaries splitting a pricing table",
        question="What caused the relevance regression reported by a customer in INC-88490?",
        category="policy-lookup",
    ),
    Fact(
        id="f_ticket_duplicate_embeddings",
        doc_id="tickets-2026-09",
        section="INC-88455",
        span="Required a full reindex of the affected tenant",
        question="What remediation did the duplicate embedding incident require?",
        category="policy-lookup",
    ),
    # -- distractor + finance ----------------------------------------------
    Fact(
        id="f_dr_rpo",
        doc_id="disaster-recovery-overview",
        section="Objectives",
        span="recovery point objective of 22 minutes",
        question="What recovery point objective does Northwind target for tier one services?",
        category="policy-lookup",
    ),
    Fact(
        id="f_dr_rto",
        doc_id="disaster-recovery-overview",
        section="Objectives",
        span="recovery time objective of 12 hours",
        question="What recovery time objective applies to tier one services?",
        category="policy-lookup",
    ),
    Fact(
        id="f_procurement_threshold1",
        doc_id="procurement-guidelines",
        section="Approval thresholds",
        span="above 5000 USD require written approval from a department head",
        question="At what value does a purchase require approval from a department head?",
        category="restricted",
    ),
    Fact(
        id="f_procurement_threshold2",
        doc_id="procurement-guidelines",
        section="Approval thresholds",
        span="above 25000 USD additionally require approval from the finance committee",
        question="At what value does a purchase need finance committee approval?",
        category="restricted",
    ),
    Fact(
        id="f_procurement_security_review",
        doc_id="procurement-guidelines",
        section="Vendor onboarding",
        span="must complete a security review before a contract is signed",
        question="What must a vendor handling Internal data do before signing a contract?",
        category="restricted",
    ),
)


# --------------------------------------------------------------------------
# Unanswerable questions
# --------------------------------------------------------------------------
# Plausible, domain-adjacent, and genuinely absent from the corpus. Several are
# traps: they name a service tier or severity that does not exist, which a system
# that never declines will happily invent an answer for.

UNANSWERABLE: tuple[UnanswerableQuestion, ...] = (
    UnanswerableQuestion(
        id="u_bronze_tier",
        question="What is the monthly uptime commitment for the Bronze service tier?",
        required_acl_tags=("all",),
        notes="Only Platinum, Gold, and Silver tiers exist. Invites interpolation.",
    ),
    UnanswerableQuestion(
        id="u_sev3_escalation",
        question="What is the escalation window for a Severity 3 incident?",
        required_acl_tags=("eng",),
        notes="The matrix stops at step 3; severity levels 3 and 4 are never defined.",
    ),
    UnanswerableQuestion(
        id="u_platinum_eu_latency",
        question="What p95 latency target applies to Platinum tier customers in the EU region?",
        required_acl_tags=("all",),
        notes="Latency is stated per tier, never per region.",
    ),
    UnanswerableQuestion(
        id="u_paternity_leave",
        question="How many weeks of paternity leave does Northwind Systems offer?",
        required_acl_tags=("hr",),
        notes="The leave policy covers annual leave and carry-over only.",
    ),
    UnanswerableQuestion(
        id="u_sabbatical",
        question="Does Northwind Systems offer a paid sabbatical programme, and after how many "
        "years of service?",
        required_acl_tags=("hr",),
        notes="No sabbatical policy exists in the corpus.",
    ),
    UnanswerableQuestion(
        id="u_working_abroad",
        question="What is the maximum number of days an employee may work abroad each year?",
        required_acl_tags=("hr",),
        notes="Plausible next to the leave policy; absent from it.",
    ),
    UnanswerableQuestion(
        id="u_cto",
        question="Who is the current Chief Technology Officer of Northwind Systems?",
        required_acl_tags=("eng",),
        notes="No org chart is in the corpus.",
    ),
    UnanswerableQuestion(
        id="u_annual_revenue",
        question="What was Northwind Systems' total revenue in the last fiscal year?",
        required_acl_tags=("finance",),
        notes="Procurement thresholds exist; financial results do not.",
    ),
    UnanswerableQuestion(
        id="u_hardware_key_request",
        question="How do I request a hardware security key for production access?",
        required_acl_tags=("eng",),
        notes="Key rotation is covered; key provisioning is not.",
    ),
    UnanswerableQuestion(
        id="u_sev3_retention",
        question="How long are Severity 3 incident tickets retained compared with Severity 1?",
        required_acl_tags=("eng",),
        notes="Retention is stated once for all incident tickets, never per severity.",
    ),
    UnanswerableQuestion(
        id="u_crypto_payments",
        question="What is Northwind Systems' policy on paying vendors in cryptocurrency?",
        required_acl_tags=("finance",),
        notes="Procurement covers thresholds and security review only.",
    ),
    UnanswerableQuestion(
        id="u_changelog_410_removal",
        question="Which specific date will the legacy vector ingestion endpoint be removed?",
        required_acl_tags=("eng",),
        notes="The changelog names release 5.0.0, not a date.",
    ),
)


def build() -> BuiltCorpus:
    """Build and validate the corpus. Raises :class:`CorpusError` if invariants fail.

    Hand-authored documents first, then the generated haystack. The gold facts are
    validated against *every* document in the result, so a generated document can
    never accidentally contain a gold span.
    """
    return build_corpus(DOCUMENTS + generate_haystack(), FACTS, UNANSWERABLE)
