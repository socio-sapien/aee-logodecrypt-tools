# PRIME customer evaluation pilot

A draft protocol for evaluating a source-to-summary review workflow with one consenting team. This is a proposal, not evidence of customer demand, efficacy, deployment readiness, or a commercial commitment.

## Question

Does a frozen PRIME build help human reviewers notice and investigate discrepancies between an authorized source trace and a candidate summary, without encouraging them to treat a cue or receipt as a verdict?

## Bounded scope

- Select one workflow with a clear source record, candidate summary, and human review point. Suitable starting examples include agent execution status or protocol-oracle freshness; this public demo uses synthetic inputs only.
- Use only records the participating organization is authorized to provide. Remove credentials, personal data, wallet secrets, and unrelated customer content before any evaluation.
- Freeze the PRIME version, configuration, source/candidate pair, and review instructions before scoring. Keep the source and candidate distinct.
- Do not connect a live wallet, broadcast transactions, trigger production actions, or use the output as a financial, legal, security, or release decision.

## Evaluation design

1. Build a small representative set of authorized traces, including unchanged controls and deliberately seeded discrepancies. Keep a holdout set that the builder does not tune against.
2. Have two reviewers independently label each trace against the source records: discrepancy category, affected field, correct status/count, whether evidence is sufficient, and unresolved questions. Reconcile disagreements before calculating results.
3. Run the same frozen inputs through PRIME and through a baseline review process. Keep raw inputs, version identifiers, output receipts, labels, and reviewer notes together under the organization's retention rules.
4. Review every mismatch and every missed discrepancy manually. Separate exact string/cue behavior from semantic interpretation, authorship, truth, or actual downstream effect.

## Measures to report

- Cue-level precision and recall against the adjudicated labels, reported per category with denominators and examples.
- Known misses, false-positive review prompts, and cases where the source or labels were insufficient.
- Reproducibility on identical inputs and configuration; record the tool version and hashes, while noting that an unsigned hash is integrity metadata, not provenance authentication.
- Reviewer time and escalation rate, comparing matched tasks and reporting sample size and study conditions. Do not treat a small pilot as proof of general performance.
- Whether reviewers understood that PRIME supplies bounded cues rather than a verdict.

## Decision gates

Continue only if independent review shows useful, reproducible cues on the holdout set, known misses remain visible, and reviewers do not over-rely on the output. If those conditions are not met, document the failure modes and revise before considering another test. Any future production integration requires separate security, privacy, reliability, and customer approvals.

## What this pilot cannot establish

A small evaluation cannot establish broad efficacy, legal compliance, security certification, market uniqueness, demand, revenue, or causal industry impact. The demo's impact paths are hypotheses; validate a real downstream chain only with authorized, time-linked source and decision records.
