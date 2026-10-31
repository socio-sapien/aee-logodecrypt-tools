# PRIME GitHub audit boundary

The original PRIME instrument is included byte-for-byte from `prime/aee_logodecrypt_prime.py`
in `socio-sapien/aee-logodecrypt-tools`. The bridge carries this exact snapshot with its source
commit/hash in `provenance.json`. It remains a deterministic text-pattern instrument, not a
semantic security oracle. This layer adds explicit operation contracts and GitHub adapters.

## Installed behavior

- `.github/copilot-instructions.md`: repository task/evidence contract.
- `.github/agents/prime-auditor.agent.md`: read-only reviewer, with its own two-tool MCP server.
- `.github/agents/prime-implementer.agent.md`: bounded source-proposal specialist, with the same MCP.
- `.github/hooks/prime-audit.json`: supported Copilot `preToolUse` hook, repository-local read/edit
  allowlist and default denial of shell, network, provider and remote-mutating tool calls. The hook
  protects its own control plane and records hashes/decisions in `.git/prime-audit/decisions.jsonl`.
- `PRIME repository audit` workflow: runs on pull requests and main pushes; tests the instrument,
  simulates `.prime/operations.json`, fails on review-required operation plans, and uploads a seven-day changed-file receipt.
- `copilot-setup-steps.yml`: prepares Python and validates the secret-free audit tools.
- `.vscode/mcp.json`: local IDE server configuration. The cloud agent profiles embed supported
  `mcp-servers`; the optional repository-wide settings payload is
  `.github/copilot/prime-mcp-settings.json`. That JSON file alone is not a GitHub setting.

No API key is needed for these audit tools. A plan never launches a shell, model, deployment,
transaction, GitHub write or hidden operator. `ghost operator` is implemented here as a dry-run
webhook inbox/broker, not impersonation or covert execution.

## Copilot tasking

When the account/repository has Copilot cloud agent enabled, select PRIME auditor for evidence
review, then PRIME implementer for a scoped source proposal. Agent profiles in the default branch
are discoverable by GitHub; this is not proof that a paid agent session has been activated.
Only the account's current Copilot UI/policy and observed session can establish availability.
A GitHub assignee lookup during this installation returned only the owner, not a Copilot assignee.
Do not infer that this is a permanent lack of entitlement. No paid session was started.

Suggested bounded task: "Use PRIME auditor to inspect the operation manifest, simulate a source
change and review its evidence. Then use PRIME implementer for one regression fix outside the
control-plane directories. Open a reviewable PR, wait for PRIME repository audit, and report actual
checks separately from assumptions. Do not call providers or deploy."

## Direct tools

```
python3 -m prime_audit.mcp_server
python3 -m unittest discover -s prime_audit/tests -v
python3 -m prime_audit.ci --base "$(git rev-parse HEAD^)" --head "$(git rev-parse HEAD)"
```

MCP tools accept supplied strings/objects only: `prime_audit_text(text, source?)` and
`prime_simulate_operation(operation)`. There are no execution or filesystem-reading MCP tools.
The operation simulation distinguishes read/propose_patch/test from network/deploy/secret/
delete/push/merge. A caller-provided `approved: true` never grants execution authority.
The CI operation gate rejects review-required manifests; change-text cues remain advisory.
The example operation manifest is labelled sample content; replace it with the exact task plan.

## Signed webhook inbox / agent warehouse

Run locally only after provisioning a webhook secret outside source control:

```
# Set PRIME_WEBHOOK_SECRET securely and PRIME_WEBHOOK_REPOSITORIES=owner/repository.
python3 -m prime_audit.webhook --port 8081 --database /private/path/prime-inbox.sqlite3
```

The listener binds to 127.0.0.1 only. It verifies HMAC-SHA256 over exact bytes, repository allowlist,
event type and body size; it atomically rejects duplicate delivery IDs and exact authenticated payload bytes in SQLite, including on a changed delivery ID. Identical legitimate event bodies are also rejected. GitHub signs the body, not the event or delivery headers, so this is duplicate suppression, not a general replay-proof or header-authentication protocol.
It queues only simulation receipts and hashes, not prompt text or executable commands.
It does not fetch URLs, call providers, post comments or execute queue entries. A separately
approved TLS deployment and actual GitHub webhook registration are still required for live events;
this installation did not expose a public endpoint or create a secret. Provider work stays in the
existing guarded bridge pipeline and needs its separate credentials/financial authorization.

## Trust and enforcement limits

- This covers the installed workflow, MCP tools and supported Copilot hooks, not every operation
  by every external agent or GitHub administrator. It is not branch protection or a universal sandbox.
- Hook timeouts may fail open in Copilot; hook files can be changed by an authorized repo writer.
  No claim of tamper-proof enforcement is made. Do not rely on the hook to protect host secrets.
- Copilot tool aliases/arguments can vary; unknown tool calls fail closed. Use actual runtime tool
  evidence to extend an allowlist, never broad wildcards. The cloud hook requires Python on Linux.
- Source edits are proposals. GitHub CI executes tests in a separate runner without provider
  credentials and with read-only repo permissions; the diff itself is never executed by the auditor.
- Review-required findings are recorded for the owner; a green CI means checks ran, not automatic
  authorization to merge. A required status-check ruleset is a separate repository setting.
- Integrity hashes are unsigned, local evidence records, not independent attestations.

References: GitHub's `hooks-reference`, `custom-agents-configuration`, and `configure-mcp-servers`
documentation. No unsupported API endpoint is used to "recruit" or silently enable an agent.

## Seven-role audit simulations
Seven read-only Copilot profiles cover evidence, perception wording, path boundaries,
recording integrity, MCP, webhook ingress and verification. Their action/contrast tables
are in `role_lexicons.py`; the changed-diff receipt records literal cue counts, not semantic
claims. Perception labels refer to words, not actual audio or image analysis. The sequence
prepares triage and review rather than granting operation authority.

Run `python3 -m prime_audit.seven_roles` to generate an unsigned fixture receipt: seven
finite checks cover missing observation, negation cue, traversal, logging failure, denied
MCP deployment, duplicate signed payload, and control-plane review. No real user operation
or agent session is run. A passing fixture does not establish complete safety or prevent
all failure. Existing hook, environment and webhook limitations still apply. Identical
legitimate webhook bodies can be suppressed, and this is not general replay protection.

## Temporal proximity
The local CI comparison, audit and operation preflight, seven offline scenarios,
Copilot pre-tool decision, and MCP tool calls record monotonic elapsed time in
nanoseconds with an advisory 7 ms target. A target breach is evidence to investigate;
it does not bypass validation, deny a safe operation, cancel work, or prove completion.
Hook timing excludes durable log I/O; CI excludes checkout, setup and artifact upload;
MCP timing excludes transport. Provider calls, GitHub queues, human approvals, webhooks
and other operations are outside this measurement; no end-to-end deadline is guaranteed.
Receipts can vary with load and hardware. No prompts or secrets are recorded in timing data.

### Live timing signals
Best-effort in-process watchdogs emit a 7 ms overrun signal to stderr while a monitored
operation is still running, then emit completion with measured elapsed time. Wrapped paths
include CI audit, seven-scenario run, change audit, simulation triage, pre-tool decision,
MCP dispatch, webhook inbox,
and available local bridge entry points for Workspace, Gemini, ChainGPT and chassis audit.
Signals contain stage names and timing only, not inputs or secrets. Thread scheduling and
stderr delivery can be delayed; these signals are not hard real-time interrupts and never
cancel or authorize an operation. Provider execution and end-to-end coverage remain dependent
on separate integration and authorization. Only paths invoking these wrappers are covered.

### Additional local checkpoint boundaries
`pre_tool_request` includes hook input parsing and receipt I/O, including rejected input;
`webhook_request` covers the loopback HTTP handler including body reads; `audit_text`
times direct text audits. Failed MCP tool calls include local elapsed timing metadata.
These signals remain best-effort observations, not guaranteed deadlines or proof of
a completed simulation. Hook policy and model instructions are separate: a permitted
read is not proof that a preceding simulation completed. No external provider or network
response timing is controlled by these checkpoints.
