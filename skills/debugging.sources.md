# debugging — sources

Audit trail for `debugging.md`. Not loaded at runtime. Update this file whenever a rule is added, changed, or removed.

## References

- **Google, Site Reliability Engineering — Chapter 12: Effective Troubleshooting** ([sre.google/sre-book/effective-troubleshooting](https://sre.google/sre-book/effective-troubleshooting/))
  - The hypothetico-deductive method: observe, hypothesize, test.
  - The structured phases: problem report → triage → examine → diagnose → test/treat → cure.
  - Warnings against four common pitfalls: misinterpreting metrics, improperly testing hypotheses, favoring improbable theories, confusing correlation with causation.
  - System inertia: "a working computer system tends to remain in motion until acted upon by an external force, such as a configuration change."
  - Diagnostic strategies: simplification, bisection, asking "what, where, why."
  - Observability as the foundation that makes effective troubleshooting possible.

- **Google, Engineering Practices** ([eng-practices](https://google.github.io/eng-practices/)) — not specifically a debugging guide, but referenced indirectly: the Rule 10 (regression tests) connection to the code-review guidance that tests must exercise the changed behavior.

## Rule-by-rule sourcing

| Rule | Source(s) | Confidence |
|------|-----------|------------|
| 1. Reproduce before fixing | Google SRE Ch. 12 (Test and Treat requires a reproducible failure); industry consensus | High |
| 2. Read the actual error and full stack trace | AI-failure-mode rule; partial Google SRE ("what, where, why") | Synthesized — universal in practice |
| 3. Symptom is not the root cause | Google SRE Ch. 12 (case study: indexing red-herring); the "Cure" phase explicitly addresses recurrence | High |
| 4. Check recent changes first | Google SRE Ch. 12 (system inertia: explicit quote) | High |
| 5. Hypothesize, then test | Google SRE Ch. 12 (hypothetico-deductive method) | High |
| 6. Change one thing at a time | Classical debugging canon; Google SRE recommends "tests with mutually exclusive outcomes" | High (cross-sourced with canon) |
| 7. Do not confuse correlation with causation | Google SRE Ch. 12 (explicit warning, plus the case study) | High |
| 8. Bisect when the search space is large | Google SRE Ch. 12 (bisection diagnostic strategy) | High |
| 9. Verify the fix actually fixed it | AI-failure-mode rule; implicit in Google SRE "Cure" phase | Synthesized |
| 10. Add a regression test that fails against the buggy code | Google SRE (preventing recurrence); pairs with `code-generation` Rule 5 | High |

## Notes

- Microsoft's Engineering Fundamentals Playbook does not have a dedicated debugging section. Its Observability content supports debugging but does not prescribe methodology. Noted here so the absence is intentional rather than an oversight.
- PR #11's audit added explicit verification output and scoped Rule 10's regression-test requirement to code root causes; operational or configuration root causes now require a written remediation note.
- Rules 2 and 9 are explicitly AI-failure-mode rules. They have weaker single-source citations because they address failure patterns the SRE canon predates (or treats as obvious enough not to belong to a separate rule). Flagged here honestly rather than over-claimed.
- David Agans's *Debugging: The 9 Indispensable Rules* is the most-cited industry book on this topic and overlaps heavily with this skill. Deliberately not cited because the rules here were derived from the publicly readable Google SRE chapter plus AI-specific failure modes; Agans is acknowledged as parallel canon rather than a source.
- `allowed_tools` declares `filesystem.write` (to apply fixes) and `shell.exec` (to actually run reproductions — Rule 1's reproduce-before-fixing requires execution, unlike `code-generation` where test execution is optional). The wider privilege footprint is intentional and earned by the workflow.
