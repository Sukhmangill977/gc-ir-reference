# GC-IR Reference Implementation
#
# The entry point a reviewer needs is `make reproduce`.

PYTHON ?= python3
VENV   := .venv
PY     := $(VENV)/bin/python

.PHONY: help venv install test reproduce reproduce-final verify-hashes cases \
        manifest clean docker-build docker-reproduce freeze-manifest lint-secrets

help:
	@echo "GC-IR Reference Implementation"
	@echo ""
	@echo "  make install           create .venv and install the pinned dependencies"
	@echo "  make test              run all four pytest suites"
	@echo "  make reproduce         run every non-CI experiment (development phase)"
	@echo "  make reproduce-final   run the frozen reportable campaign -> results/final/"
	@echo "  make verify-hashes     recompile both cases and check the reference hashes"
	@echo "  make cases             regenerate the committed case artifacts"
	@echo "  make manifest          regenerate MANIFEST.sha256 from the files on disk"
	@echo "  make freeze-manifest   regenerate the preregistration freeze manifest"
	@echo "  make docker-build      build the pinned container image"
	@echo "  make docker-reproduce  run the full reproduction inside the container"
	@echo ""
	@echo "  Five-minute verification: make install && make test && make verify-hashes"

$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --quiet --upgrade pip setuptools wheel

venv: $(VENV)

install: venv
	$(PY) -m pip install --quiet -r requirements.lock

test:
	$(PY) -m pytest -q

reproduce:
	$(PY) -m experiments.reproduce_all

reproduce-final:
	$(PY) -m experiments.reproduce_all --final --runs-per-case 30

verify-hashes:
	$(PY) -m experiments.verify_hashes

cases:
	$(PY) -m tools.build_cases
	$(PY) -m tools.build_lifecycle

manifest:
	$(PY) -m experiments.make_manifest

freeze-manifest:
	$(PY) -m experiments.make_freeze_manifest

docker-build:
	docker build -t gcir .

docker-reproduce: docker-build
	docker run --rm gcir make reproduce

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .hypothesis
