# PRIME 6.7 environment integration

## Files that actually execute
- `prime_audit/vendor/prime_v6_7.py`: unchanged standalone PRIME 6.7 instrument.
- `prime_audit/full.py`: bounded adapter calling its full base text analysis and logical-action lens. The 128-token dynamics lens is chunked for longer text, with local indices explicitly marked; metadata-dependent lenses remain unset.
- `prime_audit/mcp_server.py`: exposes `prime_full_audit` plus text, simulation and investigation tools over stdio.
- `.github/mcp.json`: workspace discovery for Copilot CLI. `.vscode/mcp.json` is VS Code discovery.
- `.github/hooks/prime-audit.json`: Copilot preToolUse executes `python3 -m prime_audit.hook` automatically. It audits the exact event and available AGENTS/Copilot instructions with 6.7 before the existing operation/scope gate. An audit error denies the tool call. Hash-only receipts live under the repository Git directory at `prime-audit/decisions.jsonl`.
- `AGENTS.md`, `.github/copilot-instructions.md`, `.github/agents/*.agent.md`: instructions for all participating models to audit their complete task and final answer. Instructions are not host enforcement.
- `.github/workflows/copilot-setup-steps.yml`: verifies installed instrument during cloud environment setup. `prime-audit.yml` repeats verification in CI and uploads the environment receipt.

## Verify locally
```sh
python3 prime_audit/vendor/prime_v6_7.py --self-test
python3 -m unittest discover -s prime_audit/tests -v
python3 -m prime_audit.environment --output prime-environment.json
copilot --trust-folder
```
Open the repository folder, not `/root`, to discover its files and workspace configuration.

## Cloud and other hosts
GitHub cloud agent MCP settings are repository Settings > Copilot > MCP servers; the file `.github/copilot/prime-mcp-settings.json` supplies the compatible JSON. Repository files alone do not change that setting. The setup workflow and pre-tool hook are repository-scoped. Models/clients that do not support these hooks must explicitly invoke the MCP adapter or implement equivalent enforcement. These files cannot modify hidden reasoning or globally force every model/service to use PRIME.

## Measurements and coverage
The pre-tool audit sees the host event and checked-in instructions, not undisclosed system prompts or the full chat unless supplied through MCP. Its source is preserved; report hashes are integrity records, not external attestation. Input is limited to 65,536 characters per MCP audit; oversize input is rejected rather than silently truncated. Metadata-based sensory, custom-domain and permutation profiles require actual supplied metadata. The existing simulation and investigation tools remain separate: empty observations are an unpopulated investigation, not completed evidence collection. Full text analysis is not a guarantee that all defects are eliminated.
