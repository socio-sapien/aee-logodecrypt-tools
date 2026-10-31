"""Copilot preToolUse adapter. Bounded, no network, no subprocess, no raw-argument log."""
from .timing import monitored
import json
import os
import sys
from pathlib import Path
from .engine import digest, receipt, protected, valid_path, sensitive, simulate_operation
from .timing import Timing

ROOT = Path(__file__).resolve().parent.parent
READ_TOOLS = {'view', 'read_file', 'read', 'search', 'grep', 'glob'}
EDIT_TOOLS = {'str_replace_editor', 'str_replace', 'edit', 'write_file', 'create_file', 'apply_patch'}

@monitored("pre_tool_decision")
def decision(event):
    name = event.get('toolName', event.get('tool_name', ''))
    args = event.get('toolArgs', event.get('tool_input', {}))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {}
    allow = False
    reason = 'Use PRIME read-only MCP tools or repository-local review edits; shell/network/remote mutations require an external reviewed workflow.'
    # The custom agents have no provider/network/remote-write tools. Unknown tools fail closed.
    if name in {'prime-audit-prime_audit_text', 'prime-audit-prime_simulate_operation',
                'prime-audit/prime_audit_text', 'prime-audit/prime_simulate_operation'}:
        allow = True
    elif name in READ_TOOLS | EDIT_TOOLS and isinstance(args, dict):
        path = args.get('path', args.get('file_path', args.get('filePath', '')))
        if isinstance(path, str):
            p = Path(path)
            if p.is_absolute():
                try:
                    path = str(p.relative_to(ROOT))
                except ValueError:
                    path = ''
            if path == '.' and name in {'view', 'read_file', 'read'}:
                allow = True
            elif valid_path(path):
                try:
                    resolved = (ROOT / path).resolve()
                    resolved.relative_to(ROOT)
                    allow = name in READ_TOOLS or not protected(path)
                    # Never expose a repository-local secret through read-only tools either.
                    # Check both the supplied path and its resolved target: a safe-looking
                    # symlink must not expose or edit a repository-local secret.
                    resolved_path = str(resolved.relative_to(ROOT))
                    if sensitive(path) or sensitive(resolved_path) or (name in {'grep', 'glob', 'search'} and not resolved.is_file()):
                        allow = False
                    if name in EDIT_TOOLS and protected(str(resolved.relative_to(ROOT))):
                        allow = False
                except (ValueError, OSError, RuntimeError):
                    allow = False
    simulation_receipt = None
    # Run policy simulation in the hook itself for every permitted file operation.
    # It is independent of the agent's MCP connection or instructions.
    if allow and name in READ_TOOLS | EDIT_TOOLS:
        try:
            operation = {'action': 'read' if name in READ_TOOLS else 'propose_patch',
                         'paths': [] if path == '.' else [path],
                         'expected_observation': 'bounded repository-local tool operation'}
            simulation = simulate_operation(operation)
            simulation_receipt = simulation.get('receipt', {}).get('sha256')
            unsigned = {k: v for k, v in simulation.items() if k != 'receipt'}
            if (simulation.get('decision') != 'READY_FOR_BOUNDED_REVIEW' or
                simulation.get('executed') is not False or
                not isinstance(simulation_receipt, str) or simulation_receipt != digest(unsigned)):
                allow = False
                reason = 'PRIME local simulation did not pass; operation denied.'
        except Exception:
            # Missing or broken simulation must not become an approval.
            allow = False
            reason = 'PRIME local simulation failed; operation denied.'
    return {'permissionDecision': 'allow' if allow else 'deny',
            'permissionDecisionReason': 'Repository-local bounded tool passed preflight.' if allow else reason,
            '_simulation_receipt': simulation_receipt}

@monitored("pre_tool_request")
def main():
    try:
        raw = sys.stdin.read(262145)
        if len(raw) > 262144:
            raise ValueError('oversize')
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError('object required')
        timing = Timing()
        start = timing.clock()
        result = decision(event)
        timing.mark("pre_tool_decision", start)
        # Keep receipt hashes only; don't send internal fields to Copilot.
        simulation_receipt = result.pop('_simulation_receipt', None)
        # Fixed path, no caller-provided log destination, no prompt or secret contents.
        directory = ROOT / '.git' / 'prime-audit'
        if not (ROOT / '.git').is_dir():
            raise ValueError('missing repository metadata')
        directory.mkdir(mode=0o700, exist_ok=True)
        directory.resolve().relative_to((ROOT / '.git').resolve())
        record = receipt({'event_sha256': digest(event), 'decision': result['permissionDecision'], 'tool': str(event.get('toolName', ''))[:100], 'simulation_receipt_sha256': simulation_receipt, 'timing': timing.record()})
        fd = os.open(directory / 'decisions.jsonl', os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW, 0o600)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'a', encoding='utf-8') as stream:
            stream.write(json.dumps(record) + '\n')
        print(json.dumps(result))
    except (ValueError, TypeError, OSError):
        print(json.dumps({'permissionDecision': 'deny', 'permissionDecisionReason': 'PRIME preflight could not validate or record this operation.'}))

if __name__ == '__main__':
    main()
