"""Translation determinism experiment (manuscript Sections VI-C, XI-H).

    TD(x) = 1[ H(C(Phi_e(x))) = H(C(Phi_e'(pi(x)))) ]

for supported execution environments e, e' and any semantics-preserving input
permutation pi.  TD applies to the **canonical payload hash**; the signature
envelope is not required to be byte-identical across signing events.

Each run varies one or more meaning-preserving conditions:

  * ``key_order``      -- every JSON object in every input document has its keys
                          re-ordered (reversed, rotated, or shuffled under a
                          fixed seed)
  * ``risk_order``     -- the risk register and risk analysis rows are permuted
  * ``obligation_order``-- the obligation matrix rows are permuted
  * ``acs_order``      -- the Approved Control Specification records are permuted
  * ``catalog_order``  -- the catalog entries are permuted
  * ``numeric_form``   -- integers are re-encoded as equal-valued floats where
                          the schema admits a number (1 -> 1.0)
  * ``locale``         -- the process runs under a different LC_ALL / LANG
  * ``timezone``       -- the process runs under a different TZ
  * ``clean_process``  -- the compilation happens in a freshly spawned
                          interpreter with a different PYTHONHASHSEED

The permutations are semantics-preserving by construction: they change document
order and encoding, never content.  A failure would mean the compiler leaked an
ordering or encoding dependence into the payload.

    python -m experiments.run_determinism [--runs-per-case 30] [--final]
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import platform
import random
import subprocess
import sys

from experiments.common import (
    CASES,
    REPO_ROOT,
    add_common_args,
    phase_of,
    environment,
    read_json,
    write_csv,
    write_result,
)

LOCALES = ["C", "en_US.UTF-8", "de_DE.UTF-8", "tr_TR.UTF-8", "ja_JP.UTF-8"]
TIMEZONES = ["UTC", "America/Edmonton", "Asia/Kolkata", "Pacific/Chatham", "Europe/Berlin"]


# ---------------------------------------------------------------------------
# Semantics-preserving permutations
# ---------------------------------------------------------------------------


def permute_keys(node, rng, mode):
    """Re-order the keys of every object in the document tree.

    JSON objects are unordered, so this changes nothing about the document's
    meaning -- and RFC 8785 must therefore produce identical bytes.
    """
    if isinstance(node, dict):
        items = [(k, permute_keys(v, rng, mode)) for k, v in node.items()]
        if mode == "reverse":
            items = list(reversed(items))
        elif mode == "rotate" and items:
            cut = rng.randrange(len(items))
            items = items[cut:] + items[:cut]
        else:
            rng.shuffle(items)
        return dict(items)
    if isinstance(node, list):
        return [permute_keys(item, rng, mode) for item in node]
    return node


def widen_numbers(node):
    """Re-encode integers as equal-valued floats.

    RFC 8785 numeric serialization is by value, not by Python type: ``1`` and
    ``1.0`` are the same JSON number and must serialize identically.
    """
    if isinstance(node, dict):
        return {k: widen_numbers(v) for k, v in node.items()}
    if isinstance(node, list):
        return [widen_numbers(item) for item in node]
    if isinstance(node, bool):
        return node
    if isinstance(node, int):
        return float(node)
    return node


def apply_permutation(documents, spec, seed):
    """Return a permuted deep copy of the loaded documents."""
    rng = random.Random(seed)
    documents = copy.deepcopy(documents)

    if spec.get("risk_order"):
        rng.shuffle(documents["assessment"]["risk_register"])
        rng.shuffle(documents["assessment"]["risk_analysis"])
    if spec.get("obligation_order"):
        rng.shuffle(documents["assessment"]["obligations"])
    if spec.get("authority_order"):
        rng.shuffle(documents["assessment"]["system_profile"]["authority_matrix"])
    if spec.get("acs_order"):
        rng.shuffle(documents["approved_control_specifications"]["records"])
        rng.shuffle(documents["dispositions"]["records"])
        rng.shuffle(documents["judgment_record"]["selections"])
        rng.shuffle(documents["judgment_record"]["approvals"])
    if spec.get("catalog_order"):
        rng.shuffle(documents["control_derivation_catalog"]["entries"])
        rng.shuffle(documents["invariant_register"]["invariants"])
    if spec.get("numeric_form"):
        # Only widen inside the risk analysis; widening an identifier-bearing
        # structure would change nothing but makes the intent less clear.
        documents["assessment"]["risk_analysis"] = widen_numbers(
            documents["assessment"]["risk_analysis"]
        )
    if spec.get("key_order"):
        documents = permute_keys(documents, rng, spec["key_order"])

    return documents


# ---------------------------------------------------------------------------
# Run matrix
# ---------------------------------------------------------------------------


#: The examiner's 31-run breakdown, from the artifact-runs memo:
#:
#:     "a loop: 10 repeats, 10 row shuffles, 5 key shuffles, 3 LC_ALL, 3 TZ;
#:      record hash and fingerprint"
#:
#: 10 + 10 + 5 + 3 + 3 = 31 executions per case.  The five strata are the
#: *primary* dimension each run exercises; every run additionally records the
#: locale, time zone and process boundary it actually ran under, so the coverage
#: of the manuscript's Section VI-C list is auditable per run rather than assumed.
#:
#: "Equivalent permitted serialization" (Section VI-C: explicit numeric
#: representations) has no stratum of its own in the memo's arithmetic, so it is
#: layered onto a documented subset of the row-shuffle and key-shuffle strata and
#: recorded in its own column.  That keeps the totals at exactly 31 while still
#: exercising the dimension the manuscript requires.
STRATA = (
    ("repeat", 10),
    ("row_shuffle", 10),
    ("key_shuffle", 5),
    ("locale", 3),
    ("timezone", 3),
)

TOTAL_RUNS_PER_CASE = sum(count for _, count in STRATA)  # 31


def build_matrix(runs_per_case=None, seed=20260101):
    """The frozen 31-run matrix, identical on every execution and every platform.

    ``runs_per_case`` is accepted for backward compatibility.  When it is None or
    equal to ``TOTAL_RUNS_PER_CASE`` the full stratified matrix is returned; a
    smaller value truncates it (development smoke runs only, never the reportable
    campaign).
    """
    rng = random.Random(seed)
    matrix = []
    index = 0

    for stratum, count in STRATA:
        for position in range(count):
            spec = {}
            label = "%s_%02d" % (stratum, position + 1)

            if stratum == "repeat":
                # Clean repeat executions: identical inputs, no permutation.
                # Half run in a freshly spawned interpreter so a different
                # PYTHONHASHSEED is exercised.
                pass
            elif stratum == "row_shuffle":
                # Every semantically unordered array is permuted. Which arrays
                # are permuted is cycled so all of them are covered.
                dimensions = ["risk_order", "obligation_order", "acs_order",
                              "catalog_order", "authority_order"]
                if position < len(dimensions):
                    spec[dimensions[position]] = True          # one at a time
                else:
                    for dimension in dimensions:               # then all together
                        spec[dimension] = True
            elif stratum == "key_shuffle":
                spec["key_order"] = ["reverse", "shuffle", "rotate",
                                     "shuffle", "reverse"][position]
            elif stratum == "locale":
                # The permutation is held fixed so the locale is the only thing
                # that varies within this stratum.
                spec["risk_order"] = True
            elif stratum == "timezone":
                spec["risk_order"] = True

            # Equivalent permitted serialization: integers re-encoded as
            # equal-valued floats. Layered onto every third row-shuffle run and
            # every second key-shuffle run.
            numeric = (
                (stratum == "row_shuffle" and position % 3 == 2)
                or (stratum == "key_shuffle" and position % 2 == 1)
            )
            if numeric:
                spec["numeric_form"] = True

            if stratum == "locale":
                locale_name = LOCALES[1 + position]            # non-C locales
                timezone = "UTC"
            elif stratum == "timezone":
                locale_name = "C"
                timezone = TIMEZONES[1 + position]             # non-UTC zones
            else:
                locale_name = LOCALES[index % len(LOCALES)]
                timezone = TIMEZONES[(index * 3) % len(TIMEZONES)]

            matrix.append({
                "label": label,
                "stratum": stratum,
                "spec": spec,
                "numeric_form": numeric,
                "permutation_seed": rng.randrange(1, 2**31),
                "locale": locale_name,
                "timezone": timezone,
                "clean_process": (index % 2 == 1),
                "python_hash_seed": rng.randrange(1, 4294967295),
            })
            index += 1

    if runs_per_case is not None and runs_per_case < len(matrix):
        return matrix[:runs_per_case]
    return matrix


def stratum_breakdown(matrix):
    counts = {}
    for entry in matrix:
        counts[entry["stratum"]] = counts.get(entry["stratum"], 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

WORKER = r"""
import json, os, sys
sys.path.insert(0, os.path.join(%(root)r, "src"))
sys.path.insert(0, %(root)r)
from experiments.run_determinism import compile_permuted
spec = json.loads(sys.stdin.read())
print(compile_permuted(spec["case_id"], spec["spec"], spec["permutation_seed"]))
"""


def compile_permuted(case_id, spec, permutation_seed):
    """Load, permute, re-sign, compile, and return the canonical payload hash.

    **Why the permuted inputs are re-signed.**  A signature binds an exact
    document.  Re-ordering an *object's keys* does not change the document under
    RFC 8785, so those signatures still verify untouched.  Re-ordering an
    *array* -- the register rows, the specification records, the catalog entries
    -- does change the document, and the signature correctly stops verifying.

    That is the right behaviour for a signature, but it is not the question this
    experiment asks.  The permutation models an equally valid authoring order
    that the same governance authority would have signed: the register rows carry
    the same content in a different sequence.  So the permuted documents are
    re-signed by the *same* authority key named in ``compile_parameters``, and
    Phi then verifies them as it verifies any signed input.  Nothing about the
    signature check is bypassed; the experiment supplies a validly signed
    equivalent input rather than a tampered one.

    ``tests/adversarial`` covers the other side of this: a document edited after
    signing, and a document signed by an unauthorized key, are both rejected.
    """
    from gcir.caseio import build_compiler_inputs, load_case
    from gcir.compiler import compile_bundle
    from experiments.run_adversarial import resign_all

    case = load_case(case_id, validate=False)
    documents = apply_permutation(case.documents, spec, permutation_seed)
    resign_all(documents, case.keyring,
               documents["compile_parameters"]["signing_authorities"])
    inputs = build_compiler_inputs(documents, case.keyring)
    result = compile_bundle(inputs)
    return result.bundle.payload_hash


def run_in_subprocess(case_id, entry):
    """Run one compilation in a freshly spawned interpreter.

    A clean process gives a different ``PYTHONHASHSEED`` (so dict iteration
    order differs), a different locale and a different time zone.
    """
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = str(entry["python_hash_seed"])
    env["LC_ALL"] = entry["locale"]
    env["LANG"] = entry["locale"]
    env["TZ"] = entry["timezone"]
    env.pop("PYTHONDONTWRITEBYTECODE", None)

    script = WORKER % {"root": REPO_ROOT}
    payload = json.dumps(
        {"case_id": case_id, "spec": entry["spec"],
         "permutation_seed": entry["permutation_seed"]}
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        input=payload.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=REPO_ROOT,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "determinism worker failed for %s/%s: %s"
            % (case_id, entry["label"], completed.stderr.decode("utf-8")[-2000:])
        )
    return completed.stdout.decode("utf-8").strip()


def run_in_process(case_id, entry):
    """Run one compilation in this interpreter, with locale and TZ switched."""
    import locale as locale_mod
    import time

    previous_tz = os.environ.get("TZ")
    os.environ["TZ"] = entry["timezone"]
    if hasattr(time, "tzset"):
        time.tzset()
    previous_locale = locale_mod.setlocale(locale_mod.LC_ALL)
    locale_applied = entry["locale"]
    try:
        locale_mod.setlocale(locale_mod.LC_ALL, entry["locale"])
    except locale_mod.Error:
        locale_applied = "%s (unavailable, fell back to %s)" % (
            entry["locale"], previous_locale
        )
    try:
        digest = compile_permuted(case_id, entry["spec"], entry["permutation_seed"])
    finally:
        try:
            locale_mod.setlocale(locale_mod.LC_ALL, previous_locale)
        except locale_mod.Error:
            pass
        if previous_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = previous_tz
        if hasattr(time, "tzset"):
            time.tzset()
    return digest, locale_applied


def _environment_fingerprint(entry, execution):
    """A short, stable fingerprint of the conditions a run actually executed under.

    The memo asks the harness to "record hash and fingerprint".  The hash is the
    canonical payload hash; this is the fingerprint of the environment that
    produced it, so a row of the CSV is self-describing.
    """
    import hashlib

    material = "|".join([
        entry["stratum"], entry["label"], execution, entry["locale"],
        entry["timezone"], str(entry["python_hash_seed"]),
        str(entry["numeric_form"]), json.dumps(entry["spec"], sort_keys=True),
        platform.platform(), platform.machine(), sys.version.split()[0],
    ])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def run(runs_per_case, final):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.metrics import translation_determinism

    matrix = build_matrix(runs_per_case)
    rows = []
    per_case = {}

    for case_id in CASES:
        # The reference hash is the unpermuted compilation in this process.
        case = load_case(case_id)
        reference = compile_bundle(case.compiler_inputs()).bundle.payload_hash
        per_case[case_id] = {"reference_hash": reference, "runs": 0, "matches": 0}

        for index, entry in enumerate(matrix, start=1):
            run_id = "%s-%03d" % (case_id, index)
            if entry["clean_process"]:
                digest = run_in_subprocess(case_id, entry)
                locale_applied = entry["locale"]
                execution = "clean_process"
            else:
                digest, locale_applied = run_in_process(case_id, entry)
                execution = "in_process"

            fingerprint = _environment_fingerprint(entry, execution)
            matched = digest == reference
            per_case[case_id]["runs"] += 1
            per_case[case_id]["matches"] += 1 if matched else 0
            rows.append(
                {
                    "run_id": run_id,
                    "case": case_id,
                    "stratum": entry["stratum"],
                    "permutation": entry["label"],
                    "numeric_form": entry["numeric_form"],
                    "environment_fingerprint": fingerprint,
                    "permutation_spec": json.dumps(entry["spec"], sort_keys=True),
                    "permutation_seed": entry["permutation_seed"],
                    "environment": execution,
                    "python_hash_seed": entry["python_hash_seed"],
                    "locale": locale_applied,
                    "timezone": entry["timezone"],
                    "hash": digest,
                    "reference_hash": reference,
                    "pass": "PASS" if matched else "FAIL",
                }
            )
            print("  %s %-12s %-16s %-14s %-18s %s"
                  % (run_id, entry["stratum"], entry["label"], entry["locale"],
                     entry["timezone"], "PASS" if matched else "FAIL <<<"))

    all_hashes = [row["hash"] for row in rows]
    overall_matches = sum(1 for row in rows if row["pass"] == "PASS")
    td_by_case = {
        case_id: translation_determinism(
            [row["hash"] for row in rows if row["case"] == case_id],
            per_case[case_id]["reference_hash"],
        )["TD"]
        for case_id in CASES
    }

    summary = {
        "runs_per_case": runs_per_case,
        "frozen_runs_per_case": TOTAL_RUNS_PER_CASE,
        "stratum_breakdown": stratum_breakdown(matrix),
        "stratum_breakdown_source": (
            "artifact-runs memo: '10 repeats, 10 row shuffles, 5 key shuffles, "
            "3 LC_ALL, 3 TZ' = 31 per case"
        ),
        "runs_with_equivalent_serialization": sum(
            1 for e in matrix if e["numeric_form"]) * len(CASES),
        "clean_process_runs": sum(1 for e in matrix if e["clean_process"]) * len(CASES),
        "total_runs": len(rows),
        "matches": overall_matches,
        "TD": {
            "value": overall_matches / len(rows) if rows else None,
            "numerator": overall_matches,
            "denominator": len(rows),
            "definition": "sum_k 1[H_k = H_reference] / N over permutations, locales, "
            "time zones and clean-process executions",
            "note": "TD is a property of the canonical payload hash. The signature "
            "envelope is not required to be byte-identical across signing events.",
        },
        "per_case": {
            case_id: {
                "reference_hash": per_case[case_id]["reference_hash"],
                "runs": per_case[case_id]["runs"],
                "matches": per_case[case_id]["matches"],
                "TD": td_by_case[case_id],
            }
            for case_id in CASES
        },
        "permutation_dimensions": [
            "key_order (reverse / shuffle / rotate, applied to every object in every input)",
            "risk_order", "obligation_order", "acs_order", "catalog_order",
            "authority_order", "numeric_form (integer re-encoded as equal float)",
            "locale", "timezone", "clean_process (fresh interpreter, new PYTHONHASHSEED)",
        ],
        "locales_used": sorted({row["locale"] for row in rows}),
        "timezones_used": sorted({row["timezone"] for row in rows}),
        "failures": [row for row in rows if row["pass"] == "FAIL"],
        "environment_scope_note": (
            "This experiment measures determinism across the permutations, locales, "
            "time zones and process boundaries listed above, on ONE host operating "
            "system. Cross-platform replication is measured separately by the GitHub "
            "Actions matrix (ubuntu / windows / macOS). No claim of universal "
            "platform independence is supported by this run alone."
        ),
    }

    csv_path = write_csv(
        final,
        "determinism_runs.csv",
        [
            "run_id", "case", "stratum", "permutation", "numeric_form",
            "permutation_spec", "permutation_seed", "environment",
            "environment_fingerprint", "python_hash_seed", "locale", "timezone",
            "hash", "reference_hash", "pass",
        ],
        rows,
    )
    write_result(final, "determinism_summary", summary)
    print("\nTD = %s (%d/%d)  ->  %s"
          % (summary["TD"]["value"], overall_matches, len(rows), csv_path))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-per-case", type=int, default=TOTAL_RUNS_PER_CASE,
                        help="the frozen matrix is %d per case (62 total); a smaller "
                             "value truncates it and is for development smoke runs "
                             "only" % TOTAL_RUNS_PER_CASE)
    add_common_args(parser)
    args = parser.parse_args(argv)
    summary = run(args.runs_per_case, phase_of(args))
    return 0 if summary["TD"]["value"] == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
