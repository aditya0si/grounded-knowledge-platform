# Thin delegation layer.
#
# The canonical task definitions live in scripts/tasks.py so that Windows (which
# has no `make`), Linux, and CI all execute byte-identical commands. Add tasks
# there, not here.

PY ?= python

.PHONY: help up down nuke logs deps serve lint fmt fmt-check typecheck test test-all cov check

help:
	@$(PY) scripts/tasks.py --list

up:          ; $(PY) scripts/tasks.py up
down:        ; $(PY) scripts/tasks.py down
nuke:        ; $(PY) scripts/tasks.py nuke
logs:        ; $(PY) scripts/tasks.py logs
deps:        ; $(PY) scripts/tasks.py deps
serve:       ; $(PY) scripts/tasks.py serve
lint:        ; $(PY) scripts/tasks.py lint
fmt:         ; $(PY) scripts/tasks.py fmt
fmt-check:   ; $(PY) scripts/tasks.py fmt-check
typecheck:   ; $(PY) scripts/tasks.py typecheck
test:        ; $(PY) scripts/tasks.py test
test-all:    ; $(PY) scripts/tasks.py test-all
cov:         ; $(PY) scripts/tasks.py cov
check:       ; $(PY) scripts/tasks.py check
