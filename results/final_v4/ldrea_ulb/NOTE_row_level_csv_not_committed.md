# Row-level L-DREA/ULB output not committed (size)

This campaign's L-DREA/ULB step re-ran `gamma_test_runner.py` (unmodified,
pinned commit `40fa8f046ad3c6632c66df46abe5500e5dd05696`,
`github.com/AGLakhowal/Gamma-Permit-Package`) against the full 284,807-row
mapped ULB corpus. The row-level output file
(`gamma_validation_results.csv`, one row per transaction) is **128 MB** and
is not committed to this repository for size reasons.

- SHA-256 of the generated file: `f45ebb23b52be3cc982b6b691edc137f46ba662a3e5521f276148c5366f5eae4`
- Row count: 284,807 (matches `gamma_summary.json`'s `rows` field, committed
  alongside this note)
- Regenerate with:
  ```
  git clone https://github.com/AGLakhowal/Gamma-Permit-Package.git
  git -C Gamma-Permit-Package checkout 40fa8f046ad3c6632c66df46abe5500e5dd05696
  # obtain GAMMA_G0_CREDITCARD_FULL_mapped.csv (derived from the public ULB
  # "Credit Card Fraud Detection" creditcard.csv via that repository's
  # gamma_map_raw.py) and place it alongside gamma_test_runner.py
  python3 Gamma-Permit-Package/realdatatestcode/gamma_test_runner.py \
    --input GAMMA_G0_CREDITCARD_FULL_mapped.csv --no-html --no-replay-manifest
  ```

The committed `gamma_summary.json` and `gamma_lab_v1_report.json` in this
directory are the full machine-readable aggregate outputs of that run and
contain every reported metric (row/label counts, false-permit/denial
counts, decision agreement, latency, per-scenario-class breakdown). Nothing
in the row-level CSV is needed beyond what these already report.
