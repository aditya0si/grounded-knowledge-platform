"""Evaluation: corpus, golden set, metric functions, runners, reporting.

The harness is built before the improvements it measures (ADR-002), and the
retrieval metrics are pure functions over gold chunk labels so that they are
deterministic, free, and unit-testable against hand-computed values (ADR-003).
"""
