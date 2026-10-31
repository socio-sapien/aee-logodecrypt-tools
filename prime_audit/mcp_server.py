"""Minimal newline-delimited JSON-RPC MCP stdio server. Pure audit tools only."""
import json
import sys
from .engine import audit_text, simulate_operation, MAX_TEXT

TOOLS = [
 {'name': 'prime_audit_text', 'description': 'Inspect supplied text against optional source; no network or execution.',
  'inputSchema': {'type': 'object', 'properties': {'text': {'type': 'string', 'maxLength': MAX_TEXT}, 'source': {'type': 'string', 'maxLength': MAX_TEXT}}, 'required': ['text'], 'additionalProperties': False},
  'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}},
 {'name': 'prime_simulate_operation', 'description': 'Simulate operation policy; never execute or authorize it.',
  'inputSchema': {'type': 'object', 'properties': {'operation': {'type': 'object'}}, 'required': ['operation'], 'additionalProperties': False},
  'annotations': {'readOnlyHint': True, 'destructiveHint': False, 'openWorldHint': False}}
]

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
        out['result'] = {'protocolVersion': version, 'capabilities': {'tools': {}}, 'serverInfo': {'name': 'prime-audit', 'version': '1.0.0'}}
    elif method == 'ping':
        out['result'] = {}
    elif method == 'tools/list':
        out['result'] = {'tools': TOOLS}
    elif method == 'tools/call':
        try:
            params = msg['params']; args = params.get('arguments', {})
            if params['name'] == 'prime_audit_text' and set(args) <= {'text', 'source'}:
                result = audit_text(**args)
            elif params['name'] == 'prime_simulate_operation' and set(args) == {'operation'}:
                result = simulate_operation(args['operation'])
            else:
                raise ValueError('unknown tool or arguments')
            out['result'] = {'content': [{'type': 'text', 'text': json.dumps(result, ensure_ascii=False)}], 'isError': False}
        except (ValueError, KeyError, TypeError, AttributeError):
            out['result'] = {'content': [{'type': 'text', 'text': 'Invalid audit request; no operation executed.'}], 'isError': True}
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
