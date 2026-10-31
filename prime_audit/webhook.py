"""Loopback-only signed GitHub webhook simulation inbox; never executes queued requests."""
import argparse
import hashlib
import hmac
import json
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from .engine import audit_change, digest

MAX_BODY = 65536

def ingest(raw, headers, secret, repositories, database):
    if not secret or len(raw) > MAX_BODY:
        return 401, {'error': 'missing configuration or oversized payload'}
    signature = 'sha256=' + hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, headers.get('X-Hub-Signature-256', '')):
        return 401, {'error': 'invalid signature'}
    delivery = headers.get('X-GitHub-Delivery', '')
    if not re.fullmatch(r'[A-Za-z0-9-]{1,100}', delivery):
        return 400, {'error': 'invalid delivery identifier'}
    try:
        data = json.loads(raw)
        repo = data['repository']['full_name']
        if repo not in repositories:
            return 403, {'error': 'repository not allowlisted'}
        kind = headers.get('X-GitHub-Event', '')
        if kind == 'ping':
            text = ''
        elif kind == 'pull_request' and data.get('action') in {'opened', 'synchronize', 'reopened', 'edited'}:
            pr = data['pull_request']; text = str(pr.get('title', '')) + '\n' + str(pr.get('body') or '')
        elif kind == 'issues' and data.get('action') in {'opened', 'edited', 'reopened'}:
            issue = data['issue']; text = str(issue.get('title', '')) + '\n' + str(issue.get('body') or '')
        else:
            return 202, {'status': 'ignored', 'executed': False}
        audit = audit_change([], text)
        record = {'repository': repo, 'event': kind, 'payload_sha256': hashlib.sha256(raw).hexdigest(), 'audit': audit}
        # Delivery IDs are unique for this local inbox; no caller-selected paths or code.
        fd = os.open(database, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        os.fchmod(fd, 0o600)
        os.close(fd)
        with sqlite3.connect(database) as db:
            db.execute('CREATE TABLE IF NOT EXISTS inbox (delivery TEXT PRIMARY KEY, receipt TEXT NOT NULL)')
            db.execute('INSERT INTO inbox VALUES (?,?)', (delivery, json.dumps(record)))
        os.chmod(database, 0o600)
        return 202, {'status': 'simulation_queued', 'delivery': delivery, 'receipt_sha256': digest(record), 'executed': False}
    except sqlite3.IntegrityError:
        return 409, {'error': 'delivery already recorded', 'executed': False}
    except (KeyError, TypeError, ValueError):
        return 400, {'error': 'invalid event envelope'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8081)
    parser.add_argument('--database', default='prime-inbox.sqlite3')
    args = parser.parse_args()
    secret = os.getenv('PRIME_WEBHOOK_SECRET')
    repositories = set(filter(None, os.getenv('PRIME_WEBHOOK_REPOSITORIES', '').split(',')))
    if not secret or not repositories:
        parser.error('PRIME_WEBHOOK_SECRET and PRIME_WEBHOOK_REPOSITORIES are required')
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != '/github/webhook':
                self.send_error(404); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                self.send_error(400); return
            if not 0 < length <= MAX_BODY:
                self.send_error(413); return
            self.connection.settimeout(5)
            code, body = ingest(self.rfile.read(length), self.headers, secret, repositories, args.database)
            value = json.dumps(body).encode()
            self.send_response(code); self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(value))); self.end_headers(); self.wfile.write(value)
        def log_message(self, *unused):
            pass
    HTTPServer(('127.0.0.1', args.port), Handler).serve_forever()

if __name__ == '__main__':
    main()
