# PRIME environment contract

PRIME 6.7 is installed at `prime_audit/vendor/prime_v6_7.py`; run it, do not invent findings.
All models working here should use MCP `prime-audit/prime_full_audit` on the complete task instruction before operations and on the final response, then compare actual evidence against claims. MCP configuration is in `.github/mcp.json` and `.vscode/mcp.json`.
Copilot preToolUse automatically runs the full installed text battery on its exact hook event and available repository instructions. This is a host hook, not a promise that model reasoning is audited. Other clients must implement the same hook or call the adapter; this file alone cannot enforce their behavior.
Run `python3 -m unittest discover -s prime_audit/tests -v` and `python3 prime_audit/vendor/prime_v6_7.py --self-test`. Preserve sources, report exact errors and unavailable metadata. Do not equate cue hits with proven intent or a passing audit with universal correctness. Follow the repository's existing authorization and protected-path rules.
