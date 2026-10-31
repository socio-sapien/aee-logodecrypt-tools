# PRIME 6.7 operational protocol

## Installed entry points
- Root executable: `python3 PRIME_6_7.py --version` (6.7.0).
- Unmodified instrument: `prime_audit/vendor/prime_v6_7.py`.
- Full text battery: MCP `prime-audit/prime_full_audit`; CLI workspace config `.github/mcp.json`.
- VS Code: `.vscode/mcp.json`. No duplicate `.mcp.json` is installed.

## Mandatory sequence within supported Copilot operations
1. Preserve the actual task and original evidence. Distinguish retrospective replay from prospective detection.
2. Run the complete applicable PRIME 6.7 text battery on the complete task/plan before operations. Use `source` only for a real independent comparison source. Text lenses include logical actions, chunk-scoped per-word dynamics and timing; metadata-dependent lenses remain explicitly unset unless actual caller metadata exists. Root CLI supports bounded metadata files.
3. Simulate planned operations, inspect concrete failures, correct and rerun. Simulations execute nothing and grant no permission. Synthetic controls must be labelled.
4. Execute only authorized supported operations, then preserve their actual results and failure evidence. Never turn a simulation, tool dispatch, or test pass into a claim of live success.
5. Reconcile claims against observed outcomes and audit the final answer; list uncovered environments and failed checks. Passing PRIME cannot guarantee correctness or eliminate failure.

## Automatic host coverage
- `userPromptTransformed`: full-battery audit of the exact available prompt/event plus root instructions; hash-only receipt.
- `preToolUse`: full-battery audit and existing bounded policy simulation before every hook-invoking tool; audit/receipt failure denies the tool.
- `postToolUse` and `postToolUseFailure`: full-battery audit of the available result/error event and instructions, hash-only receipt and contextual status.
- These hooks cover events actually delivered by the host. Prompt/post hooks record measurements, not semantic approval; they do not block completion. Final-answer audit is instructed, not independently enforced by a stop hook.
- `.git` metadata holds private hash-only lifecycle receipts. No raw prompt/result/secret log is persisted by these hooks.

## Admission and scope
Copilot CLI prompt mode loads workspace MCP only when trusted/admitted. For an explicitly authorized run in this checkout, use `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true`; it admits project MCP for that invocation, not other directories. Verify with a real session, not `mcp list` alone. Cloud agents use their job checkout: an old PR branch can lack the instrument even when default contains it. Update that branch from the integrated default before retrying; do not silently substitute unrelated code. Hooks can be disabled or restricted by client/enterprise settings. This repository cannot enforce behavior in unrelated repositories, unmanaged clients, hidden reasoning, or inaccessible platforms.
