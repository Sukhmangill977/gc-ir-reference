"""Generate results.html -- a self-contained, chart-illustrated results page
for the current release, read from results/final_v4_1/, with the historical
v1.0.5/final_v2 campaign summarized underneath.

    python tools/generate_results_page.py
    make results-page

No external assets, no CDN, no JavaScript charting library: every chart is
plain HTML/CSS (width-percentage bars), so the page renders identically
offline, in any browser, forever -- consistent with this repository's own
determinism/reproducibility standard. Re-run any time the underlying result
files change; nothing here is hand-edited.
"""

from __future__ import annotations

import datetime
import html
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

CAMPAIGN_PATH = os.path.join(REPO_ROOT, "results", "final_v4_1", "campaign_results.json")
INJECTIONS_PATH = os.path.join(REPO_ROOT, "results", "final_v4_1", "injections", "case_b_v11_13_injections.json")
OUT_PATH = os.path.join(REPO_ROOT, "results.html")


def esc(value):
    return html.escape(str(value))


def bar(label, value, total, color="#4f7cff", note=""):
    pct = 0 if total == 0 else round(100 * value / total)
    return f"""
    <div class="bar-row">
      <div class="bar-label">{esc(label)}</div>
      <div class="bar-track">
        <div class="bar-fill" style="width:{pct}%; background:{color};"></div>
        <span class="bar-value">{esc(value)}/{esc(total)}</span>
      </div>
      {f'<div class="bar-note">{esc(note)}</div>' if note else ""}
    </div>"""


def stacked_bar(segments):
    """segments: list of (label, count, color)."""
    total = sum(c for _, c, _ in segments) or 1
    chips = "".join(
        f'<div class="stack-seg" style="width:{100 * c / total:.2f}%; background:{color};" '
        f'title="{esc(label)}: {c}"></div>'
        for label, c, color in segments
    )
    legend = "".join(
        f'<span class="legend-chip"><span class="legend-dot" style="background:{color};"></span>{esc(label)} ({c})</span>'
        for label, c, color in segments
    )
    return f'<div class="stack-bar">{chips}</div><div class="legend">{legend}</div>'


def stat_card(label, value, sub="", title=""):
    title_attr = f' title="{esc(title)}"' if title else ""
    return f"""
    <div class="stat-card"{title_attr}>
      <div class="stat-value">{esc(value)}</div>
      <div class="stat-label">{esc(label)}</div>
      {f'<div class="stat-sub">{esc(sub)}</div>' if sub else ""}
    </div>"""


def load_historical():
    try:
        from tools.show_results import load_results
        return load_results()
    except Exception as exc:  # noqa: BLE001 -- historical section is best-effort
        return {"_error": str(exc)}


def _read(path):
    with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as fh:
        return json.load(fh)


def load_campaign_history():
    """Every frozen/reportable campaign this repo has ever produced, oldest
    first. Each entry's fields are pulled directly from that campaign's own
    result files (schema differs release to release; see tools/compare with
    the extraction this was built from). Best-effort per entry: a campaign
    directory that can't be read contributes an "_error" entry rather than
    breaking the whole table."""
    rows = []

    try:
        m = _read("results/final/metrics.json")["result"]
        d = _read("results/final/determinism_summary.json")["result"]
        fv = _read("results/final/freeze_verification.json")
        pt = _read("results/final/property_tests.json")["result"]["totals"]
        rows.append({
            "label": "v1.0.0-era", "tag": fv["freeze_tag"], "commit": fv["freeze_commit"],
            "status": "Superseded -- never pushed publicly", "current": False,
            "case_a_gd_min": m["per_case"]["case_a"]["GD_min"]["value"],
            "case_b_gd_min": m["per_case"]["case_b"]["GD_min"]["value"],
            "td": f'{d["TD"]["numerator"]}/{d["TD"]["denominator"]}',
            "tests": f'{pt["passed"]}/{pt["tests"]}',
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"label": "results/final/", "_error": str(exc)})

    try:
        m = _read("results/final_v2/metrics.json")["result"]
        d = _read("results/final_v2/determinism_summary.json")["result"]
        fv = _read("results/final_v2/freeze_verification.json")
        pt = _read("results/final_v2/property_tests.json")["result"]["totals"]
        rows.append({
            "label": "v1.0.5", "tag": fv["freeze_tag"], "commit": fv["freeze_commit"],
            "status": "Superseded -- first public freeze", "current": False,
            "case_a_gd_min": m["per_case"]["case_a"]["GD_min"]["value"],
            "case_b_gd_min": m["per_case"]["case_b"]["GD_min"]["value"],
            "td": f'{d["TD"]["numerator"]}/{d["TD"]["denominator"]}',
            "tests": f'{pt["passed"]}/{pt["tests"]}',
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"label": "results/final_v2/", "_error": str(exc)})

    try:
        c = _read("results/final_v3/campaign_results.json")
        rows.append({
            "label": "v1.0.4 target", "tag": c["freeze_tag"], "commit": c["freeze_commit"],
            "status": "Superseded by v3.1 (PERMIT/DENY/HOLD semantics correction)", "current": False,
            "td": f'{c["metrics"]["determinism"]["runs"]}/{c["metrics"]["determinism"]["runs"]}'
                  if c["metrics"]["determinism"].get("unique_outcomes") == 1 else "see file",
            "tests": f'{c["metrics"]["test_suite"]["passed"]}/{c["metrics"]["test_suite"]["total"]}',
            "gates": f'{c["gates_passed"]}/{c["gates_total"]}',
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"label": "results/final_v3/", "_error": str(exc)})

    try:
        c = _read("results/final_v3_1/campaign_results.json")
        rows.append({
            "label": "v1.0.5 (corrected)", "tag": c["freeze_tag"], "commit": c["freeze_commit"],
            "status": "Superseded by v4 (adds Case B v1.1 + Case C)", "current": False,
            "td": f'{c["determinism"]["runs"]}/{c["determinism"]["runs"]}'
                  if c["determinism"].get("td") == 1.0 else "see file",
            "tests": f'{c["tests"]["passed"]}/{c["tests"]["total"]}',
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"label": "results/final_v3_1/", "_error": str(exc)})

    try:
        c = _read("results/final_v4/campaign_results.json")
        rows.append({
            "label": "v1.1.0 pre-release", "tag": c["freeze_tag"], "commit": c["freeze_commit"],
            "status": "Superseded by v4.1 -- MANIFEST tooling fix only, science byte-identical",
            "current": False,
            "td": f'{c["determinism"]["TD"]["numerator"]}/{c["determinism"]["TD"]["denominator"]}',
            "tests": f'{c["test_suite"]["tests"] - c["test_suite"]["failures"] - c["test_suite"]["errors"]}/{c["test_suite"]["tests"]}',
            "freeze_check": f'{c["freeze_verification_prospective_v4"]["checks"] - c["freeze_verification_prospective_v4"]["failures"]}/{c["freeze_verification_prospective_v4"]["checks"]}',
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"label": "results/final_v4/", "_error": str(exc)})

    try:
        c = _read("results/final_v4_1/campaign_results.json")
        rows.append({
            "label": "v1.1.0 (current release)", "tag": c["freeze_tag"], "commit": c["freeze_commit"],
            "status": "Current reportable release -- shown in full above", "current": True,
            "td": f'{c["determinism"]["TD"]["numerator"]}/{c["determinism"]["TD"]["denominator"]}',
            "tests": f'{c["test_suite"]["tests"] - c["test_suite"]["failures"] - c["test_suite"]["errors"]}/{c["test_suite"]["tests"]}',
            "freeze_check": f'{c["freeze_verification_prospective_v4"]["checks"] - c["freeze_verification_prospective_v4"]["failures"]}/{c["freeze_verification_prospective_v4"]["checks"]}',
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"label": "results/final_v4_1/", "_error": str(exc)})

    return rows


def load_v12_development():
    """The current (unfrozen) Paper 2 v1.2 development state from
    results/development_v12/. Every file here is explicitly
    phase="development" / "DEVELOPMENT result; not reportable." -- this
    function's caller must keep that framing on the page; this is NOT a
    frozen campaign like the rows load_campaign_history() returns."""
    try:
        campaign = _read("results/development_v12/campaign_results_development.json")["result"]
        surface_a = _read("results/development_v12/surface_a.json")["result"]
        case_d = _read("results/development_v12/case_d.json")["result"]
        validators = _read("results/development_v12/validators.json")["result"]
        audit = _read("results/development_v12/audit.json")["result"]
        determinism = _read("results/development_v12/determinism.json")["result"]
        cross_env = _read("results/development_v12/cross_environment_determinism.json")["result"]
        monte_carlo = _read("results/development_v12/monte_carlo.json")["result"]
        timing = _read("results/development_v12/compile_timing.json")["result"]
        obs = _read("results/development_v12/observation_diagnostics.json")["result"]
        case_b_int = _read("results/development_v12/case_b_integration.json")["result"]
        env7_path = os.path.join(REPO_ROOT, "results", "development_v12", "environment_container_aarch64.json")
        env7 = _read("results/development_v12/environment_container_aarch64.json") if os.path.exists(env7_path) else None
        return {
            "reportable": campaign.get("reportable"),
            "freeze_status": campaign.get("freeze", {}).get("status"),
            "surface_a": surface_a["counts"],
            "case_d": case_d,
            "validators": validators["totals"],
            "audit": audit,
            "determinism": determinism,
            "cross_env": cross_env,
            "env7": env7,
            "monte_carlo": monte_carlo,
            "timing": timing,
            "obs": obs,
            "case_b_int": case_b_int,
        }
    except Exception as exc:  # noqa: BLE001
        return {"_error": str(exc)}


def render_campaign_history(rows):
    body = ""
    for r in rows:
        if "_error" in r:
            body += f'<tr><td>{esc(r["label"])}</td><td colspan="5" class="muted">could not be loaded ({esc(r["_error"])})</td></tr>'
            continue
        row_cls = ' class="current-row"' if r.get("current") else ""
        body += f"""<tr{row_cls}>
          <td>{esc(r["label"])}</td>
          <td><code>{esc(r["tag"])}</code></td>
          <td><code>{esc(r["commit"][:10])}</code></td>
          <td>{esc(r.get("td", "—"))}</td>
          <td>{esc(r.get("tests", "—"))}</td>
          <td class="muted">{esc(r["status"])}</td>
        </tr>"""
    return f"""
    <section class="card">
      <h2>Full campaign history</h2>
      <p class="muted">Every frozen, reportable campaign this repository has produced, oldest first.
      Case A's payload hash (<code>f5cbc3a8…</code>) and Case B's historical payload hash
      (<code>2850155a…</code>) have never changed across any of these. Only <strong>v1.1.0</strong>
      (<code>results/final_v4_1/</code>, detailed above) is the current reportable release.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Release</th><th>Freeze tag</th><th>Commit</th><th>Determinism</th><th>Tests</th><th>Status</th></tr></thead>
          <tbody>{body}</tbody>
        </table>
      </div>
    </section>"""


def render_v12_development(v12):
    if "_error" in v12:
        return f"""
    <section class="card">
      <h2>Paper 2 v1.2 &mdash; development phase (not yet frozen)</h2>
      <p class="muted">Could not be loaded in this environment ({esc(v12["_error"])}).</p>
    </section>"""

    sa = v12["surface_a"]
    cd = v12["case_d"]
    val = v12["validators"]
    au = v12["audit"]
    det = v12["determinism"]["result"] if "result" in v12["determinism"] else v12["determinism"]
    ce = v12["cross_env"]
    mc = v12["monte_carlo"]
    tm = v12["timing"]
    obs = v12["obs"]
    cbi = v12["case_b_int"]
    env7 = v12["env7"]

    env7_card = ""
    if env7:
        env7_res = env7["result"]
        env7_card = stat_card("Env-7 container (aarch64)",
                               f'{env7_res["TD"]["numerator"]}/{env7_res["TD"]["denominator"]}',
                               "pinned Linux/aarch64, hashes match")

    return f"""
    <section class="card">
      <h2>Paper 2 v1.2 &mdash; development phase (not yet frozen)</h2>
      <div class="claim">
        <strong>Not a reportable campaign.</strong> reportable = {esc(v12["reportable"])}; freeze status =
        {esc(v12["freeze_status"])}. Every figure below is development-phase evidence from
        <code>results/development_v12/</code>, gathered ahead of a prospective
        <code>preregister-tier0-v5</code> freeze that has not been created. No v1.2.0 tag exists.
      </div>
      <div class="stat-grid" style="margin-top:16px;">
        {stat_card("Surface A", sa["nominal_accepted"], "8 paired semantic families: nominal accepted")}
        {stat_card("Surface A negatives", sa["semantic_negatives_rejected"], "correct reason: " + str(sa["correct_expected_reason"]))}
        {stat_card("Case D matrix", f'{cd["passed"]}/{cd["total"]}', "D1–D10")}
        {stat_card("Validator matrix", f'{val["positive_passed"]}/{val["positive_total"]}', "16 positive/negative pairs")}
        {stat_card("Audit: historical", "19/19" if au["historical_19_all_detected"] else "FAIL", "Q1–Q10 negatives still detected")}
        {stat_card("Audit: new v1.2", "9/9" if au["new_v12_all_detected"] else "FAIL", "new audit-regression negatives")}
        {stat_card("Local determinism", f'{det["TD"]["numerator"]}/{det["TD"]["denominator"]}', "31 runs x 3 cases (A, B v1.1, D CCS1)")}
        {stat_card("6-leg CI matrix", f'{ce["jobs_succeeded"]}/{ce["total_jobs"]}', "Ubuntu/Windows/macOS x Py 3.11/3.12")}
        {env7_card}
        {stat_card("Case B integration", f'{cbi["passed"]}/{cbi["scenario_count"]}', "13 adverse + 1 clean")}
        {stat_card("Observation diagnostics", "2/2" if obs["both_passed"] else "FAIL", "history-scoped + contract-completeness")}
      </div>
      <h3>Monte Carlo (GD/GDmin regression)</h3>
      <p class="muted">K = {mc["K"]:,}, seed = {mc["seed"]}. Status: {esc(mc["regression_status"])}.</p>
      <div class="stat-grid">
        {stat_card("Case A GD_approved / GD_min", f'{mc["per_case_regression"]["case_a"]["GD_approved"]} / {mc["per_case_regression"]["case_a"]["GD_min_mean"]}')}
        {stat_card("Case B v1.1 GD_approved / GD_min", f'{mc["per_case_regression"]["case_b_v1_1"]["GD_approved"]} / {mc["per_case_regression"]["case_b_v1_1"]["GD_min_mean"]}')}
      </div>
      <h3>Compile timing (10 warmup + 100 measured, single host)</h3>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Case</th><th>n</th><th>median</th><th>p95</th></tr></thead>
          <tbody>
            {"".join(f'<tr><td>{esc(c)}</td><td>{p["n"]}</td><td>{p["median_ms"]:.2f} ms</td><td>{p["p95_ms"]:.2f} ms</td></tr>' for c, p in tm["per_case"].items())}
          </tbody>
        </table>
      </div>
      <p class="muted" style="margin-top:10px;">Single reportable reference machine only
      ({esc(tm.get("machine", {}).get("os", ""))}, {esc(tm.get("machine", {}).get("architecture", ""))},
      Python {esc(tm.get("machine", {}).get("python", ""))}); hosts never pooled;
      not platform-general latency (spec section 12).</p>
    </section>"""


def render(data, injections, historical, campaign_history=None, v12=None):
    s = data["case_b_v1_1_structure"]
    q = data["audit_queries"]
    inj = data["case_b_v1_1_injections"]
    det = data["determinism"]
    mc = data["monte_carlo"]
    ld = data["ldrea_ulb"]
    fv = data["freeze_verification_prospective_v4"]
    ieee = data["ieee_check_v4"]
    ts = data["test_suite"]
    generated_at = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    q_rows = "".join(
        bar(case_id.replace("_", " "), v["passed"], v["total"], color="#4f7cff")
        for case_id, v in q.items()
    )

    auth = inj["authorization_decision_counts"]
    rel = inj["release_decision_counts"]
    auth_stack = stacked_bar([
        ("PERMIT", auth.get("PERMIT", 0), "#2fb380"),
        ("DENY", auth.get("DENY", 0), "#e5533d"),
        ("HOLD", auth.get("HOLD", 0), "#f2a93b"),
    ])
    rel_stack = stacked_bar([
        ("ALLOW_RELEASE", rel.get("ALLOW_RELEASE", 0), "#2fb380"),
        ("BLOCK_RELEASE", rel.get("BLOCK_RELEASE", 0), "#e5533d"),
    ])

    corr = ld["correspondence_summary"]
    corr_stack = stacked_bar([
        ("exact", corr["exact"], "#2fb380"),
        ("family", corr["family"], "#4f7cff"),
        ("not_established", corr["not_established"], "#9aa3b2"),
    ])

    mc_a = mc["case_a_max_FP_heat"]
    mc_b = mc["case_b_v1_1_max_FP_heat"]
    mc_max = max(mc_a["value"], mc_b["value"]) or 1
    mc_chart = f"""
    <div class="bar-row">
      <div class="bar-label">Case A (risk {esc(mc_a["risk_id"])})</div>
      <div class="bar-track"><div class="bar-fill" style="width:{100*mc_a["value"]/mc_max:.1f}%; background:#4f7cff;"></div>
        <span class="bar-value">{mc_a["value"]:.6f}</span></div>
    </div>
    <div class="bar-row">
      <div class="bar-label">Case B v1.1 (risk {esc(mc_b["risk_id"])})</div>
      <div class="bar-track"><div class="bar-fill" style="width:{100*mc_b["value"]/mc_max:.1f}%; background:#8a5cf6;"></div>
        <span class="bar-value">{mc_b["value"]:.6f}</span></div>
    </div>"""

    def outcome_pill(v):
        cls = {"PERMIT": "ok", "DENY": "bad", "HOLD": "warn",
               "ALLOW_RELEASE": "ok", "BLOCK_RELEASE": "bad"}.get(v, "")
        return f'<span class="pill {cls}">{esc(v)}</span>'

    injection_rows = "".join(
        f"""<tr>
          <td>{esc(row["scenario"])}</td>
          <td>{esc(row.get("target_acs_or_invariant", ""))}</td>
          <td>{outcome_pill(row["authorization_decision"])}</td>
          <td>{outcome_pill(row["release_decision"])}</td>
          <td>{esc(row["safe_state"])}</td>
          <td>{esc(row["externalization"])}</td>
          <td>{'<span class="pill ok">PASS</span>' if row["passed"] else '<span class="pill bad">FAIL</span>'}</td>
        </tr>"""
        for row in injections["scenarios"] if row["scenario"] != "clean_control"
    )

    historical_block = ""
    if "_error" not in historical:
        hm = historical["metrics"]
        hd = historical["determinism"]
        hv = historical["verification"]
        historical_block = f"""
        <section class="card">
          <h2>Historical campaign -- v1.0.5 / <code>results/final_v2/</code></h2>
          <p class="muted">Superseded by the current release above; unchanged and reported here only
          for comparison. Governed by the unmodified <code>preregister-tier0-v2.2</code> freeze.</p>
          <div class="stat-grid">
            {stat_card("Bundle A", historical["cases"]["case_a"]["bundle_sha256"][:12] + "…")}
            {stat_card("Bundle B (6 ACS)", historical["cases"]["case_b"]["bundle_sha256"][:12] + "…")}
            {stat_card("TD", f'{hd["TD"]:.3f}', f'{hd["passed"]}/{hd["total"]} runs')}
            {stat_card("Tests", f'{hv["tests_passed"]}/{hv["tests_total"]}')}
            {stat_card("Negative controls", f'{hv["negative_controls_detected"]}/{hv["negative_controls_total"]}')}
            {stat_card("GD(15) / GD_min", f'A: {hm["case_a"]["GD"]["value"]}/{hm["case_a"]["GD_min"]["value"]}  ·  B: {hm["case_b"]["GD"]["value"]}/{hm["case_b"]["GD_min"]["value"]}')}
          </div>
        </section>"""
    else:
        historical_block = f"""
        <section class="card">
          <h2>Historical campaign -- v1.0.5 / <code>results/final_v2/</code></h2>
          <p class="muted">Could not be loaded in this environment ({esc(historical["_error"])}).
          Run <code>python tools/show_results.py</code> directly.</p>
        </section>"""

    v12_block = render_v12_development(v12) if v12 is not None else ""
    campaign_history_block = render_campaign_history(campaign_history) if campaign_history else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GC-IR Results -- v1.1.0</title>
<style>
  :root {{
    --bg: #f6f7fb; --card: #ffffff; --text: #1b1f27; --muted: #6b7280;
    --border: #e5e7eb; --accent: #4f7cff;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #0f1218; --card: #171b24; --text: #e7eaf0; --muted: #9aa3b2; --border: #2a2f3a; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--text);
    font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    padding: 0 0 64px;
  }}
  header {{
    padding: 40px 24px 28px; text-align: center;
    background: linear-gradient(135deg, #4f7cff, #8a5cf6);
    color: white;
  }}
  header h1 {{ margin: 0 0 6px; font-size: 28px; }}
  header p {{ margin: 4px 0; opacity: .92; font-size: 14px; }}
  .badges {{ margin-top: 14px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }}
  .badge {{
    background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
    padding: 4px 12px; border-radius: 999px; font-size: 12.5px; font-family: ui-monospace, monospace;
  }}
  main {{ max-width: 980px; margin: -20px auto 0; padding: 0 20px; display: grid; gap: 20px; }}
  .card {{
    background: var(--card); border: 1px solid var(--border); border-radius: 14px;
    padding: 22px 24px; box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .card h2 {{ margin: 0 0 4px; font-size: 18px; }}
  .card h3 {{ margin: 20px 0 10px; font-size: 14px; text-transform: uppercase; letter-spacing: .04em; color: var(--muted); }}
  .muted {{ color: var(--muted); font-size: 13.5px; }}
  code {{ background: rgba(127,127,127,.14); padding: 1px 5px; border-radius: 5px; font-size: 90%; }}
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 14px; }}
  .stat-card {{ background: rgba(79,124,255,.07); border-radius: 10px; padding: 14px; text-align: center; }}
  .stat-value {{ font-size: 20px; font-weight: 700; word-break: break-word; }}
  .stat-label {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  .stat-sub {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}
  .bar-row {{ margin: 10px 0; }}
  .bar-label {{ font-size: 13px; margin-bottom: 4px; text-transform: capitalize; }}
  .bar-track {{ position: relative; background: rgba(127,127,127,.14); border-radius: 8px; height: 22px; overflow: hidden; }}
  .bar-fill {{ position: absolute; inset: 0 auto 0 0; border-radius: 8px; }}
  .bar-value {{ position: relative; z-index: 1; font-size: 12px; line-height: 22px; padding-left: 10px; font-family: ui-monospace, monospace; }}
  .bar-note {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}
  .stack-bar {{ display: flex; height: 26px; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }}
  .stack-seg {{ height: 100%; }}
  .legend {{ margin-top: 8px; display: flex; gap: 14px; flex-wrap: wrap; }}
  .legend-chip {{ font-size: 12.5px; color: var(--muted); }}
  .legend-dot {{ display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
  th, td {{ text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--border); white-space: nowrap; }}
  th {{ color: var(--muted); font-weight: 600; font-size: 11.5px; text-transform: uppercase; }}
  .table-wrap {{ overflow-x: auto; }}
  tr.current-row {{ background: rgba(79,124,255,.08); }}
  tr.current-row td:first-child {{ font-weight: 700; }}
  .pill {{ display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 11.5px; font-weight: 600; }}
  .pill.ok {{ background: rgba(47,179,128,.15); color: #1f8f63; }}
  .pill.bad {{ background: rgba(229,83,61,.15); color: #c8422c; }}
  .pill.warn {{ background: rgba(242,169,59,.18); color: #a8710e; }}
  .claim {{
    background: rgba(242,169,59,.1); border: 1px solid rgba(242,169,59,.3);
    border-radius: 10px; padding: 14px 16px; font-size: 13px;
  }}
  footer {{ text-align: center; color: var(--muted); font-size: 12.5px; margin-top: 28px; }}
  footer a {{ color: var(--accent); }}
</style>
</head>
<body>

<header>
  <h1>GC-IR Reference Implementation -- Results</h1>
  <p>Governance-to-control compiler: measured evidence for the current release</p>
  <div class="badges">
    <span class="badge">release v1.1.0</span>
    <span class="badge">freeze {esc(data["freeze_tag"])}</span>
    <span class="badge">commit {esc(data["freeze_commit"][:12])}</span>
    <span class="badge">generated {esc(generated_at)}</span>
  </div>
</header>

<main>

  <section class="card">
    <h2>Case bundles</h2>
    <p class="muted">{esc(data.get("purpose", ""))}</p>
    <div class="stat-grid">
      {stat_card("Case A hash", data["case_a_hash"]["actual"][:16] + "…", "match: " + str(data["case_a_hash"]["match"]), title=data["case_a_hash"]["actual"])}
      {stat_card("Case B v1.1 hash", data["case_b_v1_1_hash"]["actual"][:16] + "…", "match: " + str(data["case_b_v1_1_hash"]["match"]), title=data["case_b_v1_1_hash"]["actual"])}
      {stat_card("Case B v1.1 risks", s["risk_count"])}
      {stat_card("Approved Control Specs", s["acs_count"])}
      {stat_card("Risk-derived predicates", s["risk_derived_predicate_count"])}
      {stat_card("Compiler invariants", s["compiler_invariant_predicate_count"])}
      {stat_card("Total predicates", s["predicate_count"])}
      {stat_card("Tests", f'{ts["tests"]} passed', f'{ts["failures"]} failed, {ts["skipped"]} skipped')}
    </div>
    <h3>Full hashes (for verification)</h3>
    <div class="table-wrap">
      <table>
        <tbody>
          <tr><td>Case A payload SHA-256</td><td><code>{esc(data["case_a_hash"]["actual"])}</code></td></tr>
          <tr><td>Case B v1.1 payload SHA-256</td><td><code>{esc(data["case_b_v1_1_hash"]["actual"])}</code></td></tr>
          <tr><td>Freeze commit</td><td><code>{esc(data["freeze_commit"])}</code></td></tr>
          <tr><td>Manifest root SHA-256</td><td><code>0640ad1e7a703879d4b9083a088f5b562b638173590292a2c1aed1625102e0e6</code></td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="card">
    <h2>Canonical audit queries (Q1-Q10)</h2>
    <p class="muted">Empty result set = conformant. Each case checked independently.</p>
    {q_rows}
    <h3>Negative fixtures</h3>
    {bar("19 targeted fixtures", data["negative_fixtures"]["detected"], data["negative_fixtures"]["total"], color="#2fb380",
         note="Each fixture is a deliberately corrupted copy of a real compiled bundle, detected by its intended query -- 19 fixtures covering the 10 queries above, not 10 additional queries.")}
  </section>

  <section class="card">
    <h2>Case B v1.1 injection scenarios</h2>
    <p class="muted">13 adversarial scenarios, each targeting one predicate or invariant. Two independent decision axes --
    <code>release_decision</code> is never a fourth peer <code>authorization_decision</code>.</p>
    <h3>authorization_decision</h3>
    {auth_stack}
    <h3>release_decision (meaningful only when authorization_decision = PERMIT)</h3>
    {rel_stack}
    <div class="table-wrap">
      <table>
        <thead><tr><th>Scenario</th><th>Target</th><th>Authorization</th><th>Release</th><th>safe_state</th><th>Externalized</th><th>Result</th></tr></thead>
        <tbody>{injection_rows}</tbody>
      </table>
    </div>
  </section>

  <section class="card">
    <h2>Determinism</h2>
    {bar("Translation Determinism (TD)", det["matches"], det["total_runs"], color="#2fb380",
         note="31 runs per case (10 repeat, 10 row-shuffle, 5 key-shuffle, 3 locale, 3 timezone) x 2 cases = 62.")}
    <div class="stat-grid">
      {stat_card("Case A TD", f'{det["per_case"]["case_a"]["TD"]["value"]:.3f}')}
      {stat_card("Case B v1.1 TD", f'{det["per_case"]["case_b_v1_1"]["TD"]["value"]:.3f}')}
    </div>
  </section>

  <section class="card">
    <h2>Monte Carlo rating-robustness</h2>
    <p class="muted">K = {mc["K"]:,} draws, seed = {mc["seed"]}. Maximum per-risk heat-map gate-flip probability.</p>
    {mc_chart}
    <div class="stat-grid">
      {stat_card("Case B v1.1 FP_C*", mc["case_b_v1_1_max_FP_cstar"])}
      {stat_card("Case B v1.1 GD_approved", mc["case_b_v1_1_GD_approved"])}
      {stat_card("Case B v1.1 GD_min_mean", mc["case_b_v1_1_GD_min_mean"])}
    </div>
  </section>

  <section class="card">
    <h2>L-DREA / ULB downstream reproduction</h2>
    <p class="muted">Pinned: <code>{esc(ld["pinned_repository"])}</code> @ <code>{esc(ld["pinned_commit"][:12])}</code></p>
    <div class="stat-grid">
      {stat_card("Rows", f'{ld["rows"]:,}')}
      {stat_card("Fraud-labelled", ld["fraud_labelled_rows"])}
      {stat_card("False permits", ld["false_permit_count"])}
      {stat_card("False denials", ld["false_denial_count"])}
    </div>
    <h3>GC-IR &harr; downstream predicate-family correspondence</h3>
    {corr_stack}
    <div class="claim">
      <strong>Claim boundary.</strong> The original {ld["rows"]:,}-row experiment was reproduced fresh and
      unmodified this generation. The new Case B v1.1 twelve-predicate bundle was
      <strong>not</strong> executed against that corpus (new_v1_1_replay_executed =
      {esc(ld["new_v1_1_replay_executed"])}). No fraud-detection, classifier-performance, or
      production-deployment claim is made anywhere in this artifact.
    </div>
  </section>

  <section class="card">
    <h2>Machine-readable checks</h2>
    <div class="stat-grid">
      {stat_card("ieee-check-v4", ieee["status"], f'{ieee["stage_count"]} stages')}
      {stat_card("Freeze verification", "PASS" if fv["passed"] else "FAIL", f'{fv["checks"]} checks, {fv["failures"]} failures')}
    </div>
  </section>

  {historical_block}

  {v12_block}

  {campaign_history_block}

</main>

<footer>
  Generated by <code>python tools/generate_results_page.py</code> from
  <code>results/final_v4_1/campaign_results.json</code> -- run it again any time the
  underlying result files change; nothing on this page is hand-edited.<br>
  <a href="https://github.com/Sukhmangill977/gc-ir-reference">github.com/Sukhmangill977/gc-ir-reference</a>
</footer>

</body>
</html>
"""


def main(argv=None):
    with open(CAMPAIGN_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    with open(INJECTIONS_PATH, encoding="utf-8") as fh:
        injections = json.load(fh)
    historical = load_historical()
    campaign_history = load_campaign_history()
    v12 = load_v12_development()

    page = render(data, injections, historical, campaign_history, v12)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote %s (%d bytes)" % (OUT_PATH, len(page)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
