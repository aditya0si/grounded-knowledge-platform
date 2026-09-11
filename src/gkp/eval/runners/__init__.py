"""Evaluation runners.

Each runner is a self-contained measurement: it builds the corpus, indexes it,
scores a configuration against the golden set, and writes a committed report.
Runners never mutate a previous report in place — a new configuration produces a
new file, so an old number is never quietly rewritten.
"""
