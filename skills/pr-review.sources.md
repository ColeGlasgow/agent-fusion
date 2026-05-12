# pr-review — sources

Audit trail for `pr-review.md`. Not loaded at runtime. Update this file whenever a rule is added, changed, or removed.

## References

- **Google, Engineering Practices — Code Review Developer Guide** ([eng-practices](https://github.com/google/eng-practices); rendered at https://google.github.io/eng-practices/review/)
  - [Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)
  - [What to Look For](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
  - [How to Write Code Review Comments](https://google.github.io/eng-practices/review/reviewer/comments.html)
  - [Speed of Code Reviews](https://google.github.io/eng-practices/review/reviewer/speed.html)
  - [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html)
  - [Writing Good CL Descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html)

- **Microsoft, Engineering Fundamentals Playbook — Code Reviews** ([repo](https://github.com/microsoft/code-with-engineering-playbook); rendered at https://microsoft.github.io/code-with-engineering-playbook/code-reviews/) — agrees with Google and cites Google as the canonical reference.

- **OWASP Top 10** — https://owasp.org/Top10/

## Rule-by-rule sourcing

| Rule | Source(s) | Confidence |
|------|-----------|------------|
| 1. Read every changed file in full | Google: Looking For — Every Line | High |
| 2. Approve when health improves | Google: Standard; Microsoft (agreement) | High (cross-sourced) |
| 3. Tag every comment with severity | Google: Comments; Microsoft (agreement) | High (cross-sourced) |
| 4. Comment on code, not author | Google: Comments; Microsoft (agreement) | High (cross-sourced) |
| 5. Explain reasoning | Google: Comments; Microsoft (agreement) | High (cross-sourced) |
| 6. Point out problems, let author choose fix | Google: Comments — "developer's responsibility to fix" | Single-source |
| 7. Ask for splits when CL is too large | Google: Small CLs | Single-source |
| 8. Tests cover changed behavior | Google: Looking For — Tests | Single-source |
| 9. Flag security with explicit severity | OWASP Top 10; Google: Looking For — Every Line | Cross-sourced |
| 10. Comments explain why, not what | Google: Looking For — Comments | Single-source |
| 11. Style guide is the style authority | Google: Standard — "style guides are absolute authority" | Single-source |
| 12. Acknowledge what was done well | Google: Looking For — Good Things | Single-source |
| 13. Verify the CL description | Google: Writing Good CL Descriptions | Single-source |
| 14. Push back on speculative complexity | Google: Looking For — Complexity | Single-source |

## Notes

- The original draft included a "respond within one business day" rule sourced to Google's *Speed of Code Reviews*. Cut from the runtime skill because an LLM responds instantly — the rule is irrelevant to the agent and was costing tokens on every load.
- Microsoft's Playbook explicitly defers to Google on most review topics. Treat Google as the canonical reference; Microsoft signal is "Google says this and a second large org agreed."
- OWASP's current rendered page (owasp.org/Top10/) redirects to the 2025 edition. The rule cites the resource, not a specific category list, so it stays stable across yearly updates.
