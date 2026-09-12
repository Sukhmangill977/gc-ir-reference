# Row-level L-DREA/ULB output not committed (size)

Same as `results/final_v4/ldrea_ulb/NOTE_row_level_csv_not_committed.md`.
This campaign's re-run of `gamma_test_runner.py` (unmodified, pinned commit
`40fa8f046ad3c6632c66df46abe5500e5dd05696`,
`github.com/AGLakhowal/Gamma-Permit-Package`) against the full 284,807-row
mapped ULB corpus produced a 128 MB row-level CSV, not committed for size.

- SHA-256 of the generated file: `f45ebb23b52be3cc982b6b691edc137f46ba662a3e5521f276148c5366f5eae4`
  — **identical** to the final_v4 campaign's row-level output. This is
  expected: the computation is fully deterministic (no randomness), so the
  same pinned code against the same pinned input reproduces byte-identical
  output regardless of when it is run.
- Regeneration instructions: see `results/final_v4/ldrea_ulb/NOTE_row_level_csv_not_committed.md`.
