"""montecarlo.py -- the Monte Carlo rating-robustness run.

    python tools/montecarlo.py                 # K from the frozen specification
    python tools/montecarlo.py --draws 250000

Compatibility entry point named by the artifact-runs memo ("item 4b via
tools/montecarlo.py").  It adds no analysis of its own: the authoritative
implementation is `experiments/run_monte_carlo.py` and the frozen specification
is `preregistration/monte_carlo_distributions_v1.json`.

**Provenance, restated here because it is easy to lose.** The memo describes the
distributions as awaiting "panel sign-off", and the manuscript's Section XI-G
attributes them to the independent adjudication panel.  **No panel has been
convened.**  The distributions this runs are author-specified and were frozen a
priori; they are a declared sensitivity model, not panel-adjudicated input.  The
memo's own "0.6/0.2/0.2 model" is exactly the rule frozen here.  See
`docs/FIXTURE_PROVENANCE.md` FP-020.
"""

import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from experiments.run_monte_carlo import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
