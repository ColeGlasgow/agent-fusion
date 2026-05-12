# code-generation — sources

Audit trail for `code-generation.md`. Not loaded at runtime. Update this file whenever a rule is added, changed, or removed.

## References

- **Google, Engineering Practices — Code Review Developer Guide** ([eng-practices](https://github.com/google/eng-practices); rendered at https://google.github.io/eng-practices/review/)
  - [What to Look For](https://google.github.io/eng-practices/review/reviewer/looking-for.html) — design, functionality, complexity, tests, naming, comments, style, consistency, documentation, every-line.
  - [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) — one self-contained change per CL; ~100 lines comfortable, 1000 too large.

- **Google, Python Style Guide** ([pyguide](https://google.github.io/styleguide/pyguide.html)) — universal principles, applied here in a language-agnostic way:
  - Descriptive naming, abbreviation avoidance.
  - Exceptions for invalid input; narrow `try/except`; do not use `assert` for runtime validation.
  - Comments explain intent; never describe what the code literally does.
  - Functions stay small and focused (~40-line soft ceiling).
  - Avoid mutable global state.
  - Use context managers / explicit resource scoping; do not rely on garbage collection.

- **Microsoft, Engineering Fundamentals Playbook** ([repo](https://github.com/microsoft/code-with-engineering-playbook))
  - [Engineering Fundamentals Checklist](https://microsoft.github.io/code-with-engineering-playbook/engineering-fundamentals-checklist/) — testing requirements, code review minimum, automated linting/formatting/security scanning, secrets handling, version control hygiene.
  - [Python Code Reviews](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/recipes/python/) — universal-process / language-specific-implementation pattern.

- **OWASP Secure Coding Practices Quick Reference Guide** ([project page](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)) — input validation, output encoding, auth/session, access control, cryptography, error handling, data protection, communication, system configuration. Now archived; OWASP directs developers to the active OWASP Developer Guide for current detail, but the categorization in the QRG is still the canonical taxonomy.

## Rule-by-rule sourcing

| Rule | Source(s) | Confidence |
|------|-----------|------------|
| 1. Verify APIs/imports/paths exist | AI-failure-mode rule; partially Google Looking For — Every Line ("you can defend") | Synthesized — universal in practice, no single canonical citation |
| 2. Minimum code; no speculation | Google Looking For — Complexity ("not the problem the developer speculates _might_ need to be solved") | High |
| 3. Match existing style | Google Looking For — Style/Consistency; Microsoft Playbook (lint enforcement) | High (cross-sourced) |
| 4. Small, self-contained change | Google Small CLs | High |
| 5. Tests fail when change is reverted | Google Looking For — Tests; Microsoft Checklist (>90% coverage + integration) | High (cross-sourced) |
| 6. Security at every boundary | OWASP SCP; Microsoft Checklist (secrets, encryption) | High (cross-sourced) |
| 7. Names communicate intent; comments explain why | Google Looking For — Naming/Comments; Google Python Style Guide | High (cross-sourced within Google) |
| 8. Narrow exception handling | Google Python Style Guide ("Keep try/except blocks narrow") | Single-source |
| 9. Explicit resource management | Google Python Style Guide (context managers; "coupling the lifetime of the object to the state of the resource is poor practice") | Single-source |
| 10. No magic numbers/strings | Google Style Guides (general), industry consensus | Single-source / consensus |
| 11. Focused functions, ~40-line soft ceiling | Google Python Style Guide ("If a function exceeds about 40 lines, think about whether it can be broken up") | Single-source |
| 12. No mutable global state | Google Python Style Guide ("Avoid mutable global state") | Single-source |
| 13. Surface uncertainty | AI-failure-mode rule; implicit in Google Looking For — Every Line ("write code you can defend") | Synthesized |
| 14. Update documentation in the same commit | Google Looking For — Documentation; Microsoft Playbook (commit messages: what/why) | High (cross-sourced) |

## Notes

- Anthropic's published Claude Code best-practices URL (`docs.anthropic.com/.../best-practices`) was checked and currently returns a broken redirect chain. When it is available again, add it as cross-confirmation for Rules 1, 2, 13. Do not cite content that cannot be loaded.
- Rules 1 and 13 are explicitly AI-failure-mode rules. They have weaker single-source citations because they address failure patterns the enterprise guides predate. Flagged honestly here rather than over-claimed.
- Microsoft's Engineering Fundamentals Checklist requires >90% unit test coverage. Rule 5 deliberately does not state a coverage number — coverage targets are a project decision; the universal rule is "tests must exercise the changed behavior."
