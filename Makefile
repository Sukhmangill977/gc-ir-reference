# GC-IR Reference Implementation
#
# The entry point a reviewer needs is `make reproduce`.

PYTHON ?= python3
VENV   := .venv
PY     := $(VENV)/bin/python

.PHONY: help venv install test reproduce reproduce-final reproduce-final-v2 \
        verify-hashes verify-results verify-manifest result-map ieee-check cases \
        manifest clean docker-build docker-reproduce freeze-manifest lint-secrets

help:
	@echo "GC-IR Reference Implementation"
	@echo ""
	@echo "  make install           create .venv and install the pinned dependencies"
	@echo "  make test              run all four pytest suites"
	@echo "  make ieee-check        THE REVIEWER CHECK: everything below, in order (~20 s)"
	@echo "  make verify-results    check every paper-facing number against results/final_v2/"
	@echo "  make verify-manifest   check MANIFEST.sha256 is current (the check CI runs)"
	@echo "  make reproduce         run every non-CI experiment (development phase)"
	@echo "  make reproduce-final-v2  re-run the REPORTABLE campaign -> results/final_v2/"
	@echo "  make reproduce-final   re-run the SUPERSEDED v1 campaign -> results/final/"
	@echo "  make verify-hashes     recompile both cases and check the reference hashes"
	@echo "  make cases             regenerate the committed case artifacts"
	@echo "  make manifest          regenerate MANIFEST.sha256 from the files on disk"
	@echo "  make freeze-manifest   regenerate the preregistration freeze manifest"
	@echo "  make docker-build      build the pinned container image"
	@echo "  make docker-reproduce  run the full reproduction inside the container"
	@echo ""
	@echo "  Five-minute verification: make install && make test && make verify-hashes"
	@echo "  IEEE artifact review:     make install && make ieee-check"

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

# The SUPERSEDED v1 campaign. Kept so the historical campaign remains executable;
# results/final/ is NOT reportable -- see README, "Reproducibility and the
# two-phase workflow".
reproduce-final:
	$(PY) -m experiments.reproduce_all --final --runs-per-case 30

# The reportable campaign. This OVERWRITES results/final_v2/. A reviewer checking
# the published numbers wants `make verify-results`, which writes nothing.
reproduce-final-v2:
	$(PY) -m experiments.reproduce_all --final-v2 --runs-per-case 31

verify-hashes:
	$(PY) -m experiments.verify_hashes

cases:
	$(PY) -m tools.build_cases
	$(PY) -m tools.build_lifecycle

manifest:
	$(PY) -m experiments.make_manifest

# Exactly the check the reproducibility workflow runs. Two rows are excluded
# because they necessarily change: results/development/ is rewritten by
# `make reproduce`, and MANIFEST.json embeds every hash including its own from
# the previous generation, so it never reaches a fixpoint. Every other row must
# match the committed manifest exactly. The regenerated files are restored
# afterwards, so this check leaves the working tree exactly as it found it.
verify-manifest:
	@cp MANIFEST.sha256 /tmp/gcir_manifest_saved.sha256
	@cp MANIFEST.json /tmp/gcir_manifest_saved.json
	@git show HEAD:MANIFEST.sha256 \
	  | grep -vE '  development_result |  MANIFEST\.json$$' > /tmp/gcir_manifest_before.txt
	@$(PY) -m experiments.make_manifest > /dev/null
	@grep -vE '  development_result |  MANIFEST\.json$$' MANIFEST.sha256 \
	  > /tmp/gcir_manifest_after.txt
	@cp /tmp/gcir_manifest_saved.sha256 MANIFEST.sha256
	@cp /tmp/gcir_manifest_saved.json MANIFEST.json
	@diff /tmp/gcir_manifest_before.txt /tmp/gcir_manifest_after.txt \
	  && echo "manifest is current for every released path ($$(wc -l < /tmp/gcir_manifest_after.txt) rows checked)"

# Every paper-facing number, checked against results/final_v2/. Writes nothing.
verify-results:
	$(PY) tools/verify_reported_results.py

# Regenerate the paper-to-artifact result map from results/final_v2/.
result-map:
	$(PY) -m tools.build_paper_result_map

freeze-manifest:
	$(PY) -m experiments.make_freeze_manifest

docker-build:
	docker build -t gcir .

docker-reproduce: docker-build
	docker run --rm gcir make reproduce

# ---------------------------------------------------------------------------
# The one command an IEEE artifact reviewer runs.
#
# Ordered so that a failure stops at the earliest meaningful point: environment,
# then tests, then the compiled artifacts, then the frozen evidence, then the
# published numbers, then the repository inventory. Any failure returns non-zero
# because each recipe line is a separate shell and make stops on the first error.
#
# Nothing here writes into results/final_v2/. Measured runtime ~15 s on a warm
# .venv (macOS/arm64, CPython 3.11); add ~30 s if `make install` has not run.
ieee-check:
	@echo "== 1/8  environment =="
	@$(PY) -c "import sys, jsonschema, referencing, cryptography, numpy, pytest, hypothesis; \
	  print('python', sys.version.split()[0]); \
	  print('jsonschema', jsonschema.__version__, '| cryptography', cryptography.__version__, \
	        '| numpy', numpy.__version__)"
	@echo "\n== 2/8  test suites =="
	$(PY) -m pytest -q
	@echo "\n== 3/8  recompile Case A and Case B =="
	$(PY) -m experiments.run_case --case case_a
	$(PY) -m experiments.run_case --case case_b
	@echo "\n== 4/8  committed reference payload hashes =="
	$(PY) -m experiments.verify_hashes
	@echo "\n== 5/8  freeze verification (public tag, ancestry, frozen files) =="
	$(PY) tools/freeze_check.py --final-v2
	@echo "\n== 6/8  paper-facing results vs results/final_v2/ =="
	$(PY) tools/verify_reported_results.py
	@echo "\n== 7/8  traceability audit queries and negative controls =="
	$(PY) -m experiments.run_traceability
	@echo "\n== 8/8  manifest currency =="
	@$(MAKE) --no-print-directory verify-manifest
	@echo "\n=============================================================="
	@echo "IEEE ARTIFACT CHECK PASSED -- all 8 stages"
	@echo "=============================================================="

clean:
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .hypothesis
