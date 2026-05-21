# Benchmark design: do the skills improve a model's coding?

This document specifies how to measure whether agent-fusion's skills improve the output of a coding model (Claude, via Claude Code) on an independent, external benchmark. It is design only; no harness code exists yet. The point of writing it first is to fix the protocol before spending compute, since a flawed run is expensive and its number is not recoverable after the fact.

## The question, stated precisely

For a fixed model and a fixed task set, does installing agent-fusion's skills raise the model's score versus running the same model with no skills? The answer must be a number with a confidence interval, not an anecdote.

We do **not** ask "how does agent-fusion compare to the labs' published scores." That comparison is invalid (see Validity rules). The only valid comparison is skilled versus unskilled on one harness we control.

## Why an external benchmark

The internal A/B (`bench/runs/codex/REPORT.md`) scores each run against the skills' own rules. That is circular: a rule like "use structured logging" is both an instruction the skill gives and a row it is graded on, so the skilled run wins by construction. SWE-bench removes the circularity: it grades whether hidden tests pass, which the skills do not dictate. Any lift there is independent evidence.

## Benchmark choice

**SWE-bench Lite** (300 real GitHub-issue tasks from popular Python repos). Each task ships a repo snapshot, an issue, and a hidden test set; a task is *resolved* when the previously failing tests pass and the previously passing tests still pass, evaluated in the task's Docker image.

First run is a **random 30-50 task subset** with a fixed seed, not the full 300. A subset gives directional signal at a fraction of the cost; the full set follows only if the subset is promising.

## Harness shape

agent-fusion has no executor, and this design does not build one. Claude Code is already an executor (reads repos, edits files, runs tests, iterates), so it serves as the benchmark agent.

```
for task in subset:
    for condition in [skilled, unskilled]:
        for trial in 1..R:
            prepare clean repo snapshot for task
            if condition == skilled:
                export skills into ~/.claude/skills   # existing exporter
            else:
                ensure ~/.claude/skills is empty
            run Claude Code on the issue text, capture the diff
            apply diff, run the task's test set in its Docker image
            record resolved (bool) + the diff
```

The skilled and unskilled conditions differ in exactly one thing: whether the skills are present. Same model, same Claude Code version, same prompt, same task snapshot, same trial count.

## Scoring

Two axes, computed from the same runs:

1. **Resolved rate (primary, independent).** Fraction of tasks resolved, per condition. Report `lift = resolved_skilled - resolved_unskilled` with a confidence interval. This is the headline number and the one a benchmark removes circularity from.
2. **Quality rubric (secondary).** Apply the existing rule-by-rule rubric from `bench/runs/codex/REPORT.md` (pass=1, partial=0.5, fail=0) to each diff, aggregated per condition. This captures what the skills actually target -- security, typing, logging, explicit assumptions -- which the resolved rate barely measures.

Reporting both is deliberate: skills may move quality strongly while moving resolved rate only modestly, and both facts are worth stating honestly.

## Controlling nondeterminism

Models are nondeterministic. Run each (task, condition) pair `R` times (start R=3) and average. Without repeats, a one-task flip is noise, not signal. The confidence interval on the lift must account for both task count and trial count.

## Validity rules

- **Never compare to published lab numbers.** Labs use custom scaffolding; absolute numbers are not comparable. Only skilled-vs-unskilled on this harness is valid.
- **Change one variable.** If the skilled prompt also changes length, temperature, or tool permissions, the result is confounded. Hold everything but skill presence constant.
- **Pin versions.** Record model ID, Claude Code version, skill commit SHA, and benchmark commit in every report. A rerun on different versions is a different experiment.
- **Pre-register the subset.** Choose the task seed before running, not after seeing results.

## Known confounds and limits

- **Axis mismatch.** SWE-bench measures functional correctness; the skills mostly target code quality and process. A small resolved-rate lift does not mean the skills are weak -- it may mean the benchmark does not measure their value. This is why the quality rubric runs alongside.
- **Context cost.** Loading skills consumes context the model could spend on the task. On hard tasks this could *lower* the resolved rate even when the guidance is good. The benchmark will surface this if it happens; that is a real finding, not a failure of the design.
- **Test flakiness.** Some SWE-bench tasks have flaky tests. The fixed subset should exclude known-flaky instances or the trial averaging should absorb them.
- **Cost.** subset_size * 2 conditions * R trials agent rollouts, each with a Docker test run. A 40-task subset at R=3 is 240 rollouts. Budget before starting.

## Out of scope

- Building the agent executor inside agent-fusion (Claude Code is the executor here).
- Running the full 300-task SWE-bench Lite, or SWE-bench Verified (500), before a subset shows signal.
- Comparing multiple models against each other. This measures skill lift on one model, not model-vs-model.

## Open questions for review

1. Subset size and trial count for the first run -- 40 tasks at R=3, or smaller to start?
2. Which model to pin first (Opus for headroom, or a cheaper Sonnet/Haiku where guidance may matter more)?
3. Where the harness lives: a `bench/` runner in this repo, or a separate throwaway repo so benchmark infrastructure does not bloat the core.
