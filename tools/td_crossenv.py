"""td_crossenv.py -- cross-environment determinism.

    python tools/td_crossenv.py              # this environment
    python tools/td_crossenv.py --collect downloaded/   # compare CI legs

Compatibility entry point named by the artifact-runs memo ("2-3 hours across
three machines with td_crossenv.py ... flips \\crossenvtrue").  It adds no logic:
`experiments/run_determinism.py` runs the frozen 31-per-case matrix in the
current environment, and `experiments/check_ci_agreement.py` compares the result
files that several environments produced.

**What flipping the flag requires.** Agreement of the committed reference
canonical payload hashes across environments that were *independently installed*.
Running this twice on one machine does not qualify. The measured environments are
recorded in `results/*/CI_STATUS.md`, and the supportable wording never exceeds
"deterministic across the tested supported environments".
"""

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collect", metavar="DIR", default=None,
                        help="compare determinism summaries downloaded from several "
                             "environments instead of running one here")
    parser.add_argument("--out", default=None, help="write a CI_STATUS.md here")
    parser.add_argument("--final", action="store_true")
    args, rest = parser.parse_known_args(argv)

    if args.collect:
        from experiments.check_ci_agreement import main as collect
        argv2 = [args.collect]
        if args.out:
            argv2 += ["--out", args.out]
        return collect(argv2)

    from experiments.run_determinism import main as determinism
    argv2 = list(rest)
    if args.final:
        argv2.append("--final")
    return determinism(argv2)


if __name__ == "__main__":
    raise SystemExit(main())
