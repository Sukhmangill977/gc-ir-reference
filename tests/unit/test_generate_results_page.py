"""results.html is generated from results/final_v4_1/ evidence, not
hand-edited; this proves the generator runs cleanly and the output actually
reflects the current release's real numbers."""

from __future__ import annotations

import os

from tools.generate_results_page import main as generate

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_PATH = os.path.join(REPO_ROOT, "results.html")


def test_generate_results_page_runs_and_contains_current_release_evidence():
    assert generate() == 0
    assert os.path.exists(OUT_PATH)
    with open(OUT_PATH, encoding="utf-8") as fh:
        text = fh.read()

    assert "0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1" in text
    assert "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536" in text
    assert "preregister-tier0-v4.1" in text
    assert "446 passed" in text
    assert text.count("<div") == text.count("</div>")
    assert text.count("<section") == text.count("</section>")
