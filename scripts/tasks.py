#!/usr/bin/env python3
"""Cross-platform task runner.

``make`` is not installed on the primary development machine. Rather than keep a
Makefile and a parallel set of shell commands that inevitably drift, every task
is defined once here and the Makefile and CI both delegate to this file. There is
therefore exactly one definition of "run the tests".

Usage:
    uv run python scripts/tasks.py check
    python scripts/tasks.py test
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: Sequence[str], *, check: bool = True) -> int:
    print(f"$ {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=ROOT, check=False)  # noqa: S603 - fixed argv, no shell
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result.returncode


def _mod(*args: str) -> int:
    """Run a Python module from the active interpreter (venv-safe, PATH-free)."""
    return _run([sys.executable, *args])


# -- infrastructure ---------------------------------------------------------


def up() -> int:
    """Start Postgres + Redis + MinIO and wait for their healthchecks."""
    return _run(["docker", "compose", "up", "-d", "--wait"])


def down() -> int:
    return _run(["docker", "compose", "down"])


def nuke() -> int:
    """Stop the stack and delete its volumes. Destructive."""
    return _run(["docker", "compose", "down", "-v"])


def logs() -> int:
    return _run(["docker", "compose", "logs", "--tail", "50", "-f"], check=False)


def deps() -> int:
    """Install/refresh the locked virtual environment."""
    return _run(["uv", "sync", "--all-extras"])


def serve() -> int:
    return _mod("-m", "uvicorn", "gkp.api.main:app", "--reload", "--port", "8010")


# -- quality gates ----------------------------------------------------------


def lint() -> int:
    return _mod("-m", "ruff", "check", ".")


def fmt() -> int:
    return _mod("-m", "ruff", "format", ".")


def fmt_check() -> int:
    return _mod("-m", "ruff", "format", "--check", ".")


def typecheck() -> int:
    return _mod("-m", "mypy", ".")


def test() -> int:
    """Unit tests: no infrastructure, no provider credentials."""
    return _mod("-m", "pytest", "-m", "not integration")


def test_all() -> int:
    """Every test, including those needing live services."""
    return _mod("-m", "pytest")


def cov() -> int:
    return _mod("-m", "pytest", "-m", "not integration", "--cov", "--cov-report=term-missing")


# -- evaluation -------------------------------------------------------------


def eval_corpus() -> int:
    """Rebuild the corpus, chunk it, and regenerate the golden set."""
    return _mod("scripts/build_corpus.py")


def eval_retrieval() -> int:
    """Measure the dense-only baseline and write results/BASELINE.md."""
    return _mod("-m", "gkp.eval.runners.baseline")


def check() -> int:
    """The full local gate, in the same order CI runs it."""
    for step in (lint, fmt_check, typecheck, test):
        step()
    print("\ncheck: all gates passed")
    return 0


# -- dispatch ---------------------------------------------------------------

TASKS: dict[str, tuple[Callable[[], int], str]] = {
    "up": (up, "start the dev stack"),
    "down": (down, "stop the dev stack"),
    "nuke": (nuke, "stop the dev stack and delete volumes"),
    "logs": (logs, "follow stack logs"),
    "deps": (deps, "install/refresh dependencies"),
    "serve": (serve, "run the API with reload on :8010"),
    "lint": (lint, "ruff check"),
    "fmt": (fmt, "ruff format"),
    "fmt-check": (fmt_check, "ruff format --check"),
    "typecheck": (typecheck, "mypy --strict"),
    "test": (test, "unit tests (no infrastructure)"),
    "test-all": (test_all, "all tests"),
    "cov": (cov, "unit tests with coverage"),
    "eval-corpus": (eval_corpus, "rebuild corpus + golden set"),
    "eval-retrieval": (eval_retrieval, "measure dense-only baseline"),
    "check": (check, "lint + format + types + tests"),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tasks.py",
        description="Project task runner. Commands mirror the Makefile targets.",
        epilog="Tasks: " + ", ".join(sorted(TASKS)),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("task", nargs="?", help="task to run")
    parser.add_argument("--list", action="store_true", help="list tasks and exit")
    args = parser.parse_args()

    if args.list or not args.task:
        width = max(len(name) for name in TASKS)
        for name in sorted(TASKS):
            _, desc = TASKS[name]
            print(f"  {name.ljust(width)}  {desc}")
        return 0

    if args.task not in TASKS:
        parser.error(f"unknown task {args.task!r} (try --list)")

    return TASKS[args.task][0]()


if __name__ == "__main__":
    raise SystemExit(main())
