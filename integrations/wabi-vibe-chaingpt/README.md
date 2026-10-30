# Owner-triggered GitHub → Mistral Vibe → ChainGPT review (Chassis v7)

A private-repository GitHub Actions scaffold, adapted from the Drive Chassis v7 launch kit. An owner-authored issue comment (`/wabi ai <task>`) runs a real Mistral Vibe CLI request with tools disabled, optionally sends its text answer to ChainGPT's documented REST API for a second-pass review only after the owner explicitly enables that paid call, and runs the supplied Chassis v7 CLI on the request and available answers. It saves the outputs as a short-lived private-repository Actions artifact; it never posts a comment, changes issues, edits code, signs, broadcasts, trades, or touches a chain.

This is a scaffold, not a direct Wabi API integration. It uses the Mistral Vibe CLI with a Mistral API key, not the owner’s Mistral web/AI Studio profile. The launch kit’s separate managed worker/Docker path is not part of this scaffold. The workflow is installed at `.github/workflows/wabi-vibe-chaingpt.yml`; the code is under `integrations/wabi-vibe-chaingpt/`. GitHub's `issue_comment` event only runs workflow files present on the default branch.

The target repository `socio-sapien/aee-logodecrypt-tools` is public. Its provider-free CI job can run on pushes and manual dispatch, but the real-provider job intentionally requires a private repository and therefore will not run here. This prevents public issue content and model outputs from being handled as if they were private. To use the agent path, install the same files in a private repository or have the owner explicitly change this repository's visibility; this installation does not change visibility.

## What actually runs when configured

- GitHub Actions: only a newly created, top-level issue comment in a private repository, authored by `socio-sapien`, starting exactly `/wabi ai `. Pull requests and public repositories are rejected. The task is limited to 4,000 characters and obvious secret-like values are rejected.
- Mistral Vibe CLI 3.0.3: installed with the official `uv tool install` route on the ephemeral GitHub runner and run non-interactively with one turn, bounded tokens/time, isolated `VIBE_HOME` and empty working directory, `ask` agent, connectors/MCP/subagents/background activity disabled, and all tools disabled. `MISTRAL_API_KEY` comes only from a GitHub Actions secret. The output is a genuine Vibe provider response, subject to the owner's Mistral plan and billing settings.
- ChainGPT (optional, disabled by default): if the owner sets `WABI_ENABLE_CHAINGPT=true` and provides `CHAINGPT_API_KEY`, one real `POST https://api.chaingpt.org/chat/stream` uses `Authorization: Bearer`, model `general_assistant`, and `chatHistory: "off"`. The wrapper never prints the key or response error bodies. ChainGPT's published docs state 0.5 credits per no-history call. No provider call was made while preparing this package.
- Chassis v7: existing CLI audits the owner's request, Vibe text, and (only if returned) ChainGPT review, then saves a JSON report. These are heuristic lexical measures, not fact checking, semantic verification, contract-security findings, or predictive edge.
- Test suite: CI installs `pytest==8.3.5`, runs the supplied `test_thaumaturgicon_chassis_v7.py`, then runs the included standard-library scaffold regression tests. It performs no provider call during tests.

Artifacts are retained for seven days. Keep the repository private; the artifact contains the task and model outputs. No workflow step publishes an issue comment. Mistral/ChainGPT prompts and outputs are sent to those providers when an owner triggers a configured run.

## Owner setup — required before a real run

1. Use a private GitHub repository owned by `socio-sapien`. The provider job is blocked in the currently public repository; the code is already installed there for review and provider-free CI. To run the agent job, install these files in a private repository and ensure the workflow is on its default branch. GitHub Actions must be enabled.
2. In repository Settings → Secrets and variables → Actions → New repository secret, add `MISTRAL_API_KEY` with a key the owner provisions through Mistral's Code → Vibe CLI access path. Paste the value directly into GitHub's secret field; never into chat, issue text, prompts, files, or logs. This workflow uses repository Actions secrets rather than environment reviewers so it can be used on eligible private repositories without assuming a paid GitHub plan.
3. ChainGPT is disabled by default. The available read-only dashboard landing showed “0 Credits”; its authenticated API-key/balance view was not accessible until the owner connects a wallet, so actual key existence and usable balance are unverified. Only if the owner wants to enable ChainGPT: connect their own wallet to the ChainGPT account, inspect the API Dashboard for a key and credit balance, provision a key if absent, add `CHAINGPT_API_KEY` as a repository Actions secret, then add repository Actions variable `WABI_ENABLE_CHAINGPT=true`. If credits are absent, leave the variable unset; purchasing/top-up requires a separate exact purchase approval. The key and billing remain owner-gated; no key was created and no paid request was made here.
4. Confirm the Mistral account's Vibe access/plan and billing settings. Vibe uses the supported `MISTRAL_API_KEY` environment variable for CI. Mistral provider usage depends on the account plan and pay-as-you-go settings.
5. To invoke a run, create an issue in that private repository and comment `/wabi ai <specific task>`. Each eligible new comment invokes Mistral; ChainGPT is called only after its secret and enable-variable are configured. When enabled, each run consumes 0.5 ChainGPT credits according to the current docs. This manual GitHub issue-comment bridge is the only trigger in this scaffold; Wabi has no exposed public event/API endpoint here to pass its chat instructions automatically. Do not use the command for casual conversation.

## Checks and no-secret local test

With Python 3.12+ and pytest available:

```sh
python3 -m pytest -q test_thaumaturgicon_chassis_v7.py
python3 -m unittest discover -s tests -v
```

The first suite was patched per the owner's inspected run: `AuditStore.verify_chain` reconstructs writer payload fields rather than hashing SQLite-generated `id` and default `timestamp` columns; the forensic-event timestamp remains included because its writer hashes it. The PIC test now compares against the implementation's documented four-decimal rounding. The durable-path test asserts the exact HOME-relative DB path rather than contradictorily banning pytest's `/tmp` test directory.

Local test status: Python compilation passed; the scaffold unittest suite passed 6/6; a provider-free CLI smoke test passed with ChainGPT explicitly `not_run`; the patched Chassis suite passed 26/26. GitHub CI runs both suites on push/manual dispatch. No Mistral or ChainGPT credentials were loaded, no external provider request was made, and no key/credit purchase occurred.

## Official interface references (reviewed 2026-10-30)

- Mistral Vibe install/setup, `MISTRAL_API_KEY`, plan usage: https://docs.mistral.ai/vibe/code/cli/install-setup and https://docs.mistral.ai/vibe/code/cli/api-keys-profiles
- Vibe non-interactive `--prompt-file`, bounded runs, tool allow/deny flags: https://docs.mistral.ai/vibe/code/cli/work-with-cli
- Vibe config (including `VIBE_HOME`, `enable_mcp`, `enable_connectors`, `enable_auto_approve`, `enable_subagents`, `enable_background_processes`): https://docs.mistral.ai/vibe/code/cli/configuration and https://docs.mistral.ai/vibe/code/cli/configuration-reference
- Pinned Vibe release: https://github.com/mistralai/mistral-vibe/releases/tag/v3.0.3
- ChainGPT endpoint/auth/schema/credits: https://docs.chaingpt.org/dev-docs-b2b-saas-api-and-sdk/web3-ai-chatbot-and-llm-api-and-sdk/javascript/api-reference
- GitHub `issue_comment` behavior: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub Actions secret hardening: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions
