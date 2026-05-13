# frontend-react — sources

Audit trail for `frontend-react.md`. Not loaded at runtime. Update this file whenever a rule is added, changed, or removed.

`frontend-react` extends `code-generation` via `requires:`. Foundation rules (verify APIs, minimum code, match style, scope, tests-that-fail-when-reverted, boundary security, naming/comments, unhappy path, focused functions, surface uncertainty) are inherited and not re-sourced here.

## References

- **React docs — Choosing the State Structure** ([react.dev/learn/choosing-the-state-structure](https://react.dev/learn/choosing-the-state-structure)) — avoid redundant, duplicate, and contradictory state; calculate values from props or state during render when possible.

- **React docs — You Might Not Need an Effect** ([react.dev/learn/you-might-not-need-an-effect](https://react.dev/learn/you-might-not-need-an-effect)) — Effects are unnecessary for transforming render data or handling user events; derive during render or handle events directly.

- **React docs — Separating Events from Effects** ([react.dev/learn/separating-events-from-effects](https://react.dev/learn/separating-events-from-effects)) — event handlers respond to specific interactions; Effects run when synchronization is needed.

- **React API — `useEffect`** ([react.dev/reference/react/useEffect](https://react.dev/reference/react/useEffect)) — Effects synchronize with external systems, require declared reactive dependencies, and need cleanup that mirrors setup.

- **React docs — Rendering Lists** ([react.dev/learn/rendering-lists](https://react.dev/learn/rendering-lists)) — keys must be unique among siblings and stable; array indexes lead to confusing bugs when order changes.

- **React DOM — `<input>`** ([react.dev/reference/react-dom/components/input](https://react.dev/reference/react-dom/components/input)) — controlled inputs cannot switch control mode and need synchronous `onChange` handlers.

- **React DOM — Common components / `dangerouslySetInnerHTML`** ([react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html](https://react.dev/reference/react-dom/components/common#dangerously-setting-the-inner-html)) — raw HTML rendering requires extreme caution and trusted, sanitized data.

- **MDN — Cross-site scripting (XSS)** ([developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/XSS)) — background on XSS risks and browser execution of injected content.

- **OWASP Cheat Sheet — Cross Site Scripting Prevention** ([cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)) — framework auto-escaping helps, escape hatches such as React's `dangerouslySetInnerHTML` require sanitization, and DOMPurify is recommended for HTML sanitization.

- **DOMPurify** ([github.com/cure53/DOMPurify](https://github.com/cure53/DOMPurify)) — concrete sanitizer used in the HTML example; cited as a representative approved sanitizer, not as a new repository dependency.

- **React docs — Components and Hooks must be pure** ([react.dev/reference/rules/components-and-hooks-must-be-pure](https://react.dev/reference/rules/components-and-hooks-must-be-pure)) — components and hooks should keep rendering pure and predictable.

## Rule-by-rule sourcing

| Rule | Source(s) | Confidence |
|------|-----------|------------|
| 1. Derive state; do not store what can be computed | React Choosing State Structure; React You Might Not Need an Effect; AI-failure-mode synthesis | High (cross-sourced) |
| 2. `useEffect` is the last resort | React You Might Not Need an Effect; Separating Events from Effects; `useEffect` API; AI-failure-mode synthesis | High (cross-sourced) |
| 3. Stable unique list keys, never array index | React Rendering Lists | High (single authoritative source) |
| 4. Controlled inputs have one source of truth | React DOM `<input>`; AI-failure-mode synthesis | High |
| 5. Escape user content; sanitize before `dangerouslySetInnerHTML` | React DOM common components; MDN XSS; OWASP XSS Prevention; DOMPurify | High (cross-sourced) |
| 6. Small focused components | React Components and Hooks must be pure; code-generation function-focus foundation; AI-failure-mode synthesis | Medium (heuristic threshold) |

## Notes

- Six rules, deliberately. The foundation (`code-generation`) already carries verification, minimum-code, project-style, scope, tests-that-fail-when-reverted, security-at-boundaries, naming/comments, unhappy-path handling, and function-focus rules; repeating them here would burn tokens at composition time. Each rule below is something `code-generation` does not say or cannot say in React-specific form.
- Rules 1 and 2 have a synthesis component. React documents the mechanism: derived data belongs in render, Effects are for external synchronization, and event responses belong in event handlers. The rule wording targets a common AI failure mode: adding `useState` plus `useEffect` because it "feels reactive" even when no external system exists.
- Rule 4 has a synthesis component. React documents the controlled/uncontrolled constraints; the rule combines them into the operational review check agents need: a field has exactly one source of truth for its whole lifetime.
- Rule 6's numeric ceiling is a heuristic, not a React guarantee. It translates the foundation's focused-function rule into React's failure mode: large JSX bodies with many hooks hide unrelated state machines. Treat the threshold as a review trigger, not a hard lint rule.
- Process and Output format sections are deliberately omitted. They are inherited from `code-generation` through `requires:` composition. Duplicating them would burn ~30 lines at every load.
- Examples cover Rules 1, 2, 3, and 5 directly. Rule 4 is exercised through controlled input patterns in Example 1, and Rule 6 is kept in rule text only because component-size problems are project-specific and do not need a fourth example.
