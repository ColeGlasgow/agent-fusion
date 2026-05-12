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
  - Use context managers / explicit resource scoping; do not rely on garbage collection.

- **Microsoft, Engineering Fundamentals Playbook** ([repo](https://github.com/microsoft/code-with-engineering-playbook))
  - [Engineering Fundamentals Checklist](https://microsoft.github.io/code-with-engineering-playbook/engineering-fundamentals-checklist/) — testing requirements, code review minimum, automated linting/formatting/security scanning, secrets handling, version control hygiene.
  - [Python Code Reviews](https://microsoft.github.io/code-with-engineering-playbook/code-reviews/recipes/python/) — universal-process / language-specific-implementation pattern.

- **OWASP Secure Coding Practices Quick Reference Guide** ([project page](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)) — input validation, output encoding, auth/session, access control, cryptography, error handling, data protection, communication, system configuration. Archived; OWASP directs developers to the active OWASP Developer Guide for current detail, but the QRG categorization is still the canonical taxonomy.

## Rule-by-rule sourcing

| Rule | Source(s) | Confidence |
|------|-----------|------------|
| 1. Verify APIs/imports/paths exist | AI-failure-mode rule; partially Google Looking For — Every Line ("you can defend") | Synthesized — universal in practice, no single canonical citation |
| 2. Minimum code; no speculation | Google Looking For — Complexity ("not the problem the developer speculates _might_ need to be solved") | High |
| 3. Match existing style | Google Looking For — Style/Consistency; Microsoft Playbook (lint enforcement) | High (cross-sourced) |
| 4. Do not enlarge scope | Google Small CLs (one self-contained change) | High |
| 5. Tests fail when change is reverted | Google Looking For — Tests; Microsoft Checklist (>90% coverage + integration) | High (cross-sourced) |
| 6. Security at every boundary | OWASP SCP; Microsoft Checklist (secrets, encryption) | High (cross-sourced) |
| 7. Names communicate intent; comments explain why; no magic literals | Google Looking For — Naming/Comments; Google Python Style Guide | High (cross-sourced within Google) |
| 8. Handle the unhappy path (narrow exceptions + resource scoping) | Google Python Style Guide (narrow `try/except`; "coupling the lifetime of the object to the state of the resource is poor practice") | Single-source |
| 9. Focused functions, ~40-line soft ceiling | Google Python Style Guide ("If a function exceeds about 40 lines, think about whether it can be broken up") | Single-source |
| 10. Surface uncertainty | AI-failure-mode rule; implicit in Google Looking For — Every Line ("write code you can defend") | Synthesized |

## Notes

- Iteration 3 set `allowed_tools: [filesystem.write]` — required per the repo's tool tier system (`docs/SKILL_AUTHORING.md`); a code-generation skill that does not declare write permission cannot do its job. `shell.exec` deliberately omitted: running tests is a composition concern, not a permission this skill should carry.
- Iteration 2 trimmed the rule list from 14 to 10. Cut Rule 12 ("no mutable global state") — Python-shaped and has known exceptions in Go and embedded contexts; belongs in language-specific skills. Merged old Rules 8+9 into a single "handle the unhappy path" rule. Merged old Rule 10 (no magic numbers) into Rule 7 as a clause. Moved old Rule 14 (update docs) into `success_criteria` and the Process step list, where it functions as a completion check rather than a generative directive.
- Anthropic's published Claude Code best-practices URL (`docs.anthropic.com/.../best-practices`) was checked and currently returns a broken redirect chain. When it is available again, add it as cross-confirmation for Rules 1, 2, 10. Do not cite content that cannot be loaded.
- Rules 1 and 10 are explicitly AI-failure-mode rules. They have weaker single-source citations because they address failure patterns the enterprise guides predate. Flagged honestly here rather than over-claimed.
- Microsoft's Engineering Fundamentals Checklist requires >90% unit test coverage. Rule 5 deliberately does not state a coverage number — coverage targets are a project decision; the universal rule is "tests must exercise the changed behavior."
