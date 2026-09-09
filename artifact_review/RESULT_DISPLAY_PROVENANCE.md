# Result display provenance

Generated from `tools.show_results.load_results()` provenance records.
Empirical evidence is read from final_v2. Editorial labels and packaging metadata
are identified separately. Arithmetic in field descriptions only aggregates recorded counts.
The viewer verifies final_v2 inventory hashes against MANIFEST.json and runs the
existing paper-result map verifier and independent cross-checks before rendering.
A missing local freeze tag is skipped by that verifier; recorded freeze evidence remains checked.
No machine-readable ieee-check outcome is present in final_v2, so none is claimed.

| Displayed result | Source file | JSON/CSV field | Terminal | README |
|---|---|---|---|---|
| freeze tag | `results/final_v2/PROVENANCE.json` | `freeze_verification.freeze_tag` | yes | yes |
| freeze commit | `results/final_v2/PROVENANCE.json` | `freeze_verification.freeze_commit` | yes | yes |
| public commitment discharged | `results/final_v2/PROVENANCE.json` | `freeze_verification.public_commitment_discharged` | yes | no |
| frozen file count | `results/final_v2/PROVENANCE.json` | `freeze_verification.frozen_file_count` | yes | no |
| execution commit | `results/final_v2/determinism_summary.json` | `environment.git_commit` | yes | no |
| Case A bundle SHA-256 | `results/final_v2/case_a/compilation.json` | `result.payload_hash` | yes | yes |
| Case A risk count | `results/final_v2/case_a/compilation.json` | `result.statistics.risk_count` | yes | no |
| Case A predicate count | `results/final_v2/case_a/compilation.json` | `result.statistics.predicate_count` | yes | no |
| Case A disposition counts | `results/final_v2/metrics.json` | `result.per_case.case_a.disposition_counts` | yes | no |
| Case A class | `results/final_v2/case_a/compilation.json` | `result.case_class` | yes | no |
| Case B bundle SHA-256 | `results/final_v2/case_b/compilation.json` | `result.payload_hash` | yes | yes |
| Case B risk count | `results/final_v2/case_b/compilation.json` | `result.statistics.risk_count` | yes | no |
| Case B predicate count | `results/final_v2/case_b/compilation.json` | `result.statistics.predicate_count` | yes | no |
| Case B disposition counts | `results/final_v2/metrics.json` | `result.per_case.case_b.disposition_counts` | yes | no |
| Case B class | `results/final_v2/case_b/compilation.json` | `result.case_class` | yes | no |
| DC (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.DC.value` | yes | yes |
| RCY (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.RCY.value` | yes | yes |
| NDR (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.NDR.value` | yes | yes |
| OPR (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.OPR.value` | yes | yes |
| ODC (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.ODC.value` | yes | yes |
| PTC (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.PTC.value` | yes | yes |
| CV (Case A) | `results/final_v2/metrics.json` | `result.per_case.case_a.CV.value` | yes | yes |
| GD(T_H) (Case A) | `results/final_v2/gate_divergence.json` | `result.per_case.case_a.GD_at_declared_threshold` | yes | yes |
| GD_min (Case A) | `results/final_v2/gate_divergence.json` | `result.per_case.case_a.GD_min` | yes | yes |
| DC (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.DC.value` | yes | yes |
| RCY (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.RCY.value` | yes | yes |
| NDR (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.NDR.value` | yes | yes |
| OPR (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.OPR.value` | yes | yes |
| ODC (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.ODC.value` | yes | yes |
| PTC (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.PTC.value` | yes | yes |
| CV (Case B) | `results/final_v2/metrics.json` | `result.per_case.case_b.CV.value` | yes | yes |
| GD(T_H) (Case B) | `results/final_v2/gate_divergence.json` | `result.per_case.case_b.GD_at_declared_threshold` | yes | yes |
| GD_min (Case B) | `results/final_v2/gate_divergence.json` | `result.per_case.case_b.GD_min` | yes | yes |
| GD_min fixture-rating range | `results/final_v2/gate_divergence.json` | `result.case_a_fixture_rating_sensitivity.GD_min_range` | yes | no |
| TD | `results/final_v2/determinism_summary.json` | `result.TD.value` | yes | yes |
| TD passed / total | `results/final_v2/determinism_summary.json` | `result.TD.numerator, result.TD.denominator` | yes | yes |
| determinism runs per case | `results/final_v2/determinism_summary.json` | `result.runs_per_case` | yes | yes |
| determinism strata | `results/final_v2/determinism_summary.json` | `result.stratum_breakdown` | yes | no |
| cross-platform determinism-macos-latest-py3.11 | `results/final_v2/cross_environment/ci/determinism-macos-latest-py3.11/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform determinism-macos-latest-py3.12 | `results/final_v2/cross_environment/ci/determinism-macos-latest-py3.12/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform determinism-ubuntu-latest-py3.11 | `results/final_v2/cross_environment/ci/determinism-ubuntu-latest-py3.11/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform determinism-ubuntu-latest-py3.12 | `results/final_v2/cross_environment/ci/determinism-ubuntu-latest-py3.12/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform determinism-windows-latest-py3.11 | `results/final_v2/cross_environment/ci/determinism-windows-latest-py3.11/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform determinism-windows-latest-py3.12 | `results/final_v2/cross_environment/ci/determinism-windows-latest-py3.12/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform pinned container | `results/final_v2/cross_environment/determinism_summary_container_linux.json` | `environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash` | yes | yes |
| cross-platform local host | `results/final_v2/determinism_summary.json` | `environment.{platform,machine,python_version}; result.TD.value` | yes | yes |
| cross-platform environments | `results/final_v2/cross_environment/**/determinism_summary.json` | `environment.platform, .machine, .python_version; result.TD.value` | yes | yes |
| Monte Carlo K (Case A) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.draws_K` | yes | yes |
| max FP_heat (Case A) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.max_FP_heat.value` | yes | yes |
| max FP_C* (Case A) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.max_FP_cstar` | yes | yes |
| Monte Carlo K (Case B) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.draws_K` | yes | yes |
| max FP_heat (Case B) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.max_FP_heat.value` | yes | no |
| max FP_C* (Case B) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.max_FP_cstar` | yes | yes |
| Monte Carlo MCSE (Case A) | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.max_FP_heat.mcse` | yes | yes |
| C* membership changes observed | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.cstar_membership_changes_observed` | yes | yes |
| test count | `results/final_v2/property_tests.json` | `result.totals.tests` | yes | yes |
| adversarial corpus | `results/final_v2/adversarial.json` | `result.corpus.passed / .total` | yes | yes |
| structural checks | `results/final_v2/adversarial.json` | `result.structural_checks.passed / .total` | yes | yes |
| validation seeds | `results/final_v2/adversarial.json` | `result.validation_seeds.passed / .total` | yes | no |
| Case B injection scenarios | `results/final_v2/adversarial.json` | `result.case_b_injection_scenarios.passed / .scenario_count` | yes | no |
| property count | `results/final_v2/property_tests.json` | `result.property_based.property_count` | yes | yes |
| generated examples | `results/final_v2/property_tests.json` | `result.property_based.total_generated_examples` | yes | yes |
| clean traceability queries | `results/final_v2/traceability_queries.json` | `result.clean.<case>.Q1..Q6.empty` | yes | yes |
| negative controls | `results/final_v2/traceability_queries.json` | `result.negative_controls.<case>[].detected` | yes | yes |
| paper-facing results verified | `artifact_review/PAPER_RESULT_MAP.json` | `entry_count` | yes | no |
| artifact release | `CITATION.cff` | `version` | yes | yes |
| result directory | `artifact_review/PAPER_RESULT_MAP.json` | `results_dir` | yes | yes |
| freeze verification | `results/final_v2/freeze_verification.json` | `verified, findings, frozen_files_changed_since_freeze` | yes | no |
| case_a obligation_count | `results/final_v2/case_a/compilation.json` | `result.statistics.obligation_count` | yes | no |
| case_a risk_derived_predicate_count | `results/final_v2/case_a/compilation.json` | `result.statistics.risk_derived_predicate_count` | yes | no |
| case_a compiler_invariant_predicate_count | `results/final_v2/case_a/compilation.json` | `result.statistics.compiler_invariant_predicate_count` | yes | no |
| case_a cstar_risk_count | `results/final_v2/case_a/compilation.json` | `result.statistics.cstar_risk_count` | yes | no |
| case_a name | `tools/show_results.py` | `CASE_NAMES (editorial label, not an empirical result)` | yes | no |
| case_a GD threshold | `results/final_v2/gate_divergence.json` | `result.per_case.case_a.declared_threshold` | yes | yes |
| case_a DC fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.DC.{numerator,denominator}` | yes | no |
| case_a RCY fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.RCY.{numerator,denominator}` | yes | no |
| case_a NDR fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.NDR.{numerator,denominator}` | yes | no |
| case_a OPR fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.OPR.{numerator,denominator}` | yes | no |
| case_a ODC fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.ODC.{numerator,denominator}` | yes | no |
| case_a PTC fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.PTC.{numerator,denominator}` | yes | no |
| case_a CV fraction | `results/final_v2/metrics.json` | `result.per_case.case_a.CV.{numerator,denominator}` | yes | no |
| case_a MC rng_seed | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.rng_seed` | yes | no |
| case_a MC max_FP_heat.risk_id | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.max_FP_heat.risk_id` | yes | no |
| case_a MC max_FP_heat.mcse | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.max_FP_heat.mcse` | yes | no |
| case_a MC cstar_probe_draws | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.cstar_probe_draws` | yes | no |
| case_a MC cstar_membership_changes_observed | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_a.cstar_membership_changes_observed` | yes | no |
| case_a determinism counts | `results/final_v2/determinism_summary.json` | `result.per_case.case_a.{matches,runs}` | yes | no |
| case_b obligation_count | `results/final_v2/case_b/compilation.json` | `result.statistics.obligation_count` | yes | no |
| case_b risk_derived_predicate_count | `results/final_v2/case_b/compilation.json` | `result.statistics.risk_derived_predicate_count` | yes | no |
| case_b compiler_invariant_predicate_count | `results/final_v2/case_b/compilation.json` | `result.statistics.compiler_invariant_predicate_count` | yes | no |
| case_b cstar_risk_count | `results/final_v2/case_b/compilation.json` | `result.statistics.cstar_risk_count` | yes | no |
| case_b name | `tools/show_results.py` | `CASE_NAMES (editorial label, not an empirical result)` | yes | no |
| case_b GD threshold | `results/final_v2/gate_divergence.json` | `result.per_case.case_b.declared_threshold` | yes | yes |
| case_b DC fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.DC.{numerator,denominator}` | yes | no |
| case_b RCY fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.RCY.{numerator,denominator}` | yes | no |
| case_b NDR fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.NDR.{numerator,denominator}` | yes | no |
| case_b OPR fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.OPR.{numerator,denominator}` | yes | no |
| case_b ODC fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.ODC.{numerator,denominator}` | yes | no |
| case_b PTC fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.PTC.{numerator,denominator}` | yes | no |
| case_b CV fraction | `results/final_v2/metrics.json` | `result.per_case.case_b.CV.{numerator,denominator}` | yes | no |
| case_b MC rng_seed | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.rng_seed` | yes | no |
| case_b MC max_FP_heat.risk_id | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.max_FP_heat.risk_id` | yes | no |
| case_b MC max_FP_heat.mcse | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.max_FP_heat.mcse` | yes | no |
| case_b MC cstar_probe_draws | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.cstar_probe_draws` | yes | no |
| case_b MC cstar_membership_changes_observed | `results/final_v2/monte_carlo_summary.json` | `result.per_case.case_b.cstar_membership_changes_observed` | yes | no |
| case_b determinism counts | `results/final_v2/determinism_summary.json` | `result.per_case.case_b.{matches,runs}` | yes | no |
| TD failed | `results/final_v2/determinism_summary.json` | `result.TD.denominator - result.TD.numerator` | yes | no |
| tests passed | `results/final_v2/property_tests.json` | `result.totals.passed` | yes | yes |
| adversarial composition | `results/final_v2/adversarial.json` | `result.corpus.{negative_cases,positive_controls,code_mismatch}` | yes | no |
