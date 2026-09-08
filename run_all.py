#!/usr/bin/env python3
"""run_all.py -- one-command reproduction, at the repository root.

    python run_all.py                 # development phase
    python run_all.py --final-v2      # the frozen reportable v2 campaign

The artifact-runs memo assumes a reviewer will "run run_all.py", so this exists
at the path a reviewer will look for.  It adds nothing: the authoritative driver
is `experiments/reproduce_all.py`, and `make reproduce` calls the same thing.

Every experiment, in order, with each step's status reported and a non-zero exit
if any step fails.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from experiments.reproduce_all import main  # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--final-v2" in argv:
        argv = ["--final-v2" if a == "--final-v2" else a for a in argv]
    raise SystemExit(main(argv))
