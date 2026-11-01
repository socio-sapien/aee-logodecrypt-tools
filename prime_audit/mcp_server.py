"""Minimal newline-delimited JSON-RPC MCP stdio server. Pure audit tools only."""
from .timing import monitored
import json
import sys
from .engine import audit_text, simulate_operation, MAX_TEXT
from .timing import Timing
from .full import audit_full
from .evidence_case import audit_evidence_case
from .harness import run as harness_run

TOOLS = [
 {'name': 'prime_evidence_case', 'description': 'Compare supplied prompt, output, and caller-provided tool receipts using exhaustive surface mapping and separately labeled evidence, deductions, inductions, abductive hypotheses and unknowns. No execution, hidden reasoning access or source authentication.', 'inputSchema': {'type': 'object', 'properties': {'prompt': {'type': 'string', 'maxLength': MAX_TEXT}, 'output': {'type': 'string', 'maxLength': MAX_TEXT}, 'tool_receipts': {'type': 'array', 'maxItems': 256}, 'requirements': {'type': 'array', 'items': {'type': 'string', 'maxLength': 512}, 'maxItems': 64}}, 'required': ['prompt', 'output'], 'additionalProperties': False}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
 {'name': 'prime_full_audit', 'description': 'Run the installed PRIME 6.7 full text battery, logical actions and bounded per-word dynamics on complete inputs. Metadata-only lenses remain unset without metadata.', 'inputSchema': {'type': 'object', 'properties': {'text': {'type': 'string', 'maxLength': MAX_TEXT}, 'source': {'type': 'string', 'maxLength': MAX_TEXT}}, 'required': ['text'], 'additionalProperties': False}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
 {'name': 'prime_investigate', 'description': 'Assess an operation and caller-supplied evidence matrix. No execution or authorization.', 'inputSchema': {'type': 'object', 'properties': {'operation': {'type': 'object'}, 'observations': {'type': 'array', 'maxItems': 16}}, 'required': ['operation'], 'additionalProperties': False}, 'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
 {'name': 'prime_audit_text', 'description': 'Run PRIME 6.7 full text battery (compatibility name); no network or execution.',
  'inputSchema': {'type': 'object', 'properties': {'text': {'type': 'string', 'maxLength': MAX_TEXT}, 'source': {'type': 'string', 'maxLength': MAX_TEXT}}, 'required': ['text'], 'additionalProperties': False},
  'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
 {'name': 'prime_simulate_operation', 'description': 'Simulate operation policy; never execute or authorize it.',
  'inputSchema': {'type': 'object', 'properties': {'operation': {'type': 'object'}}, 'required': ['operation'], 'additionalProperties': False},
  'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}}
]

@monitored("mcp_dispatch")
def dispatch(msg):
    if not isinstance(msg, dict) or not isinstance(msg.get('params', {}), dict):
        raise ValueError('object params required')
    method = msg.get('method')
    if 'id' not in msg:
        return None
    out = {'jsonrpc': '2.0', 'id': msg['id']}
    if method == 'initialize':
        requested = msg.get('params', {}).get('protocolVersion')
        version = requested if isinstance(requested, str) and requested in {'2024-11-05', '2025-03-26', '2025-06-18'} else '2024-11-05'
        out['result'] = {'protocolVersion': version, 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'prime-audit', 'version': '6.7.0'}}
    elif method == 'ping':
        out['result'] = {}
    elif method == 'tools/list':
        out['result'] = {'tools': TOOLS}
    elif method == 'tools/call':
        timing = Timing(); started = timing.clock()
        try:
            params = msg['params']; args = params.get('arguments', {})
            if params['name'] == 'prime_evidence_case' and set(args) <= {'prompt', 'output', 'tool_receipts', 'requirements'} and {'prompt', 'output'} <= set(args):
                result = audit_evidence_case(**args)
            elif params['name'] == 'prime_full_audit' and set(args) <= {'text', 'source'}:
                result = audit_full(**args)
            elif params['name'] == 'prime_audit_text' and set(args) <= {'text', 'source'}:
                result = audit_full(**args)
            elif params['name'] == 'prime_investigate' and set(args) <= {'operation', 'observations'} and 'operation' in args:
                result = harness_run(**args)
            elif params['name'] == 'prime_simulate_operation' and set(args) == {'operation'}:
                result = simulate_operation(args['operation'])
            else:
                raise ValueError('unknown tool or arguments')
            timing.mark('mcp_tool', started)
            out['result'] = {'content': [{'type': 'text', 'text': json.dumps(result, ensure_ascii=False)}], 'isError': False, '_meta': {'prime_timing': timing.record()}}
        except (ValueError, KeyError, TypeError, AttributeError):
            timing.mark('mcp_tool', started)
            out['result'] = {'content': [{'type': 'text', 'text': 'Invalid audit request; no operation executed.'}], 'isError': True, '_meta': {'prime_timing': timing.record()}}
    else:
        out['error'] = {'code': -32601, 'message': 'Method not found'}
    return out

def main():
    while True:
        line = sys.stdin.buffer.readline(262145)
        if not line:
            return
        try:
            if len(line) > 262144 or not line.endswith(b'\n'):
                raise ValueError('message too large')
            msg = json.loads(line)
            if not isinstance(msg, dict):
                raise ValueError('object required')
            result = dispatch(msg)
        except (ValueError, TypeError):
            result = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'Invalid JSON-RPC message'}}
        if result is not None:
            print(json.dumps(result, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
