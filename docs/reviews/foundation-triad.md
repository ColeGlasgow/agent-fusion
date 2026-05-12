# Foundation triad audit

## skills/pr-review.md

### Summary

`skills/pr-review.md` defines a language-agnostic PR review skill with strong review hygiene, but I would request changes before treating it as a stable foundation skill. The main issue is that its broad "pull request, code diff, or proposed change" scope conflicts with CL-only required checks, and its output format can force fabricated positives when none are present.

### Blockers

- `skills/pr-review.md:13` — **blocker:** The success criteria require "The CL description has been verified for clarity," but the skill's trigger includes any "code diff, or proposed change" at `skills/pr-review.md:27`. A standalone diff may not have a CL description, so the agent cannot honestly answer every success criterion with "yes" as required by `skills/pr-review.md:67`.
- `skills/pr-review.md:88` — **blocker:** The output format requires "one or two specific positives," and `skills/pr-review.md:92` says to always include `Things done well`. That can force the reviewer to invent praise when no specific positive is present, which conflicts with the repository hard rule against fabrication.

### Suggestions

- `skills/pr-review.md:55` — **suggestion:** The CL-description rule says the first line must be imperative and stand-alone, but this skill is language-agnostic and repository-agnostic. Treating that convention as universal can produce false negatives in repositories that use issue templates or structured PR forms instead of a one-line CL summary.
- `skills/pr-review.md:74` — **suggestion:** The summary placeholder asks for "what the CL does," but the skill also applies to proposed changes that may not be a CL. Consider using the broader "change" wording throughout so the process and output format match the trigger.

### Nits

- `skills/pr-review.md:55` — **nit:** The skill switches between "PR," "code diff," "proposed change," and "CL" without defining CL. That is small, but it makes the rulebook less direct for agents outside Google-style terminology.

### FYI

- `skills/pr-review.md:23` — **fyi:** The file says citations live in `pr-review.sources.md`, and that adjacent source file exists. I did not treat the plain code-form path as a problem because repository docs already use local path references heavily.

### Things done well

- `skills/pr-review.md:35` — **fyi:** The severity vocabulary is explicit and operational, which makes author actionability much clearer.
- `skills/pr-review.md:127` — **fyi:** The examples show concrete bad and corrected review comments, which gives the model a usable pattern instead of only abstract rules.

## skills/code-generation.md

### Summary

`skills/code-generation.md` covers the core failure modes of generated code well, especially hallucinated APIs, speculative scope, and behavior-focused tests. I would request changes because the security boundary rule allows unresolved TODOs for sensitive areas, and the tool/output contract leaves verification weaker than the success criteria imply.

### Blockers

- `skills/code-generation.md:45` — **blocker:** Rule 6 allows auth, crypto, deserialization, file paths, and similar boundaries to receive "an explicit `TODO` flag." That does not satisfy the success criterion at `skills/code-generation.md:14` that security-sensitive boundaries are "handled explicitly"; it permits generated code to leave high-risk behavior unresolved while still claiming completion.

### Suggestions

- `skills/code-generation.md:7` — **suggestion:** The skill grants only `filesystem.write`, but the process requires verifying every success criterion at `skills/code-generation.md:64`, and the output requires a non-empty `Tests` section at `skills/code-generation.md:86`. If test execution is intentionally outside this skill, the rulebook should say that directly; otherwise add the tool permission needed to run the verification the skill asks for.
- `skills/code-generation.md:18` — **suggestion:** The success criteria require invalidated documentation to be updated "in the same commit," but the skill does not grant `git.commit` and many agent tasks produce a working-tree change rather than a commit. Rephrase this as same change or same PR unless the skill is expected to own commits.
- `skills/code-generation.md:86` — **suggestion:** The note says "Omit `Assumptions`" even though the output section is named `Assumptions and uncertainty` at `skills/code-generation.md:79`. That mismatch is easy for an agent to pattern-match incorrectly.

### Nits

- `skills/code-generation.md:51` — **nit:** The 40-line function ceiling is useful but Python-shaped. Since this is the language-agnostic foundation, it would be clearer as an example heuristic rather than a cross-language rule.

### FYI

- `skills/code-generation.md:203` — **fyi:** The OpenAI SDK example tells the agent to check installed package docs before calling an API. That is useful, but it also means the skill's practical workflow depends on local dependency inspection even though the formal process does not name that as a verification step.

### Things done well

- `skills/code-generation.md:35` — **fyi:** The first rule directly targets hallucinated APIs, imports, and paths, which is one of the highest-value constraints for generated code.
- `skills/code-generation.md:231` — **fyi:** The retry-test example demonstrates the "would this fail if reverted?" standard with a concrete mock setup and assertions.

## skills/debugging.md

### Summary

`skills/debugging.md` gives a strong root-cause workflow and correctly centers reproduction before repair. I would request changes because the output format does not require the final verification evidence that the rules and success criteria demand, and the incident-level trigger conflicts with a mandatory regression-test requirement.

### Blockers

- `skills/debugging.md:70` — **blocker:** The output format has no required section for the verification rerun, even though the success criteria require "The fix has been verified by re-running the reproduction" at `skills/debugging.md:16`, Rule 9 requires the exact reproduction to be re-run at `skills/debugging.md:51`, and the process repeats that at `skills/debugging.md:66`. The final artifact can therefore omit the key evidence that the bug is fixed.
- `skills/debugging.md:31` — **blocker:** The trigger includes incidents and any "this isn't working" report, but the success criteria require a regression test at `skills/debugging.md:17` and Rule 10 says the fix is incomplete until that test exists at `skills/debugging.md:53`. Operational incidents, configuration failures, and third-party regressions may not have a meaningful code-level regression test, so the skill can force fake or irrelevant tests.

### Suggestions

- `skills/debugging.md:14` — **suggestion:** The success criteria require recent changes to be checked, and the process names git log, deploys, and config at `skills/debugging.md:60`, but the output format has no place to record what was checked. Add a required recent-changes line or section so the audit trail preserves that step.
- `skills/debugging.md:60` — **suggestion:** "Recent deploys" may require external release-system access that the agent often will not have. The rule should say to record unavailable evidence explicitly instead of letting the agent imply the check was completed.

### Nits

- `skills/debugging.md:49` — **nit:** Rule 8 says to use `git bisect` when the search space is large. Since `git bisect` changes repository state while it runs, the process should remind agents to clean up the bisect session before finishing.

### FYI

- `skills/debugging.md:37` — **fyi:** Requiring the agent to quote relevant error lines is a good guard against pattern-matching, but it can expose secrets if stack traces include credentials. The rule should preserve the intent while telling agents to redact sensitive values.

### Things done well

- `skills/debugging.md:35` — **fyi:** The reproduce-before-fixing rule is crisp, testable, and placed first, which anchors the whole workflow.
- `skills/debugging.md:43` — **fyi:** The hypothesis-and-prediction rule gives agents a concrete alternative to random trial-and-error debugging.
