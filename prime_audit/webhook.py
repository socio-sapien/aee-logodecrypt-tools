"""Loopback-only signed GitHub webhook simulation inbox; never executes queued requests."""
from .timing import monitored
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

@monitored("webhook_ingest")
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
        # GitHub signs the body, not the delivery header. Persist a fingerprint of
        # the authenticated bytes as well as the ID, atomically across concurrent
        # requests. On upgrade, backfill hashes from existing receipts.
        payload_hash = record['payload_sha256']
        fd = os.open(database, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        os.fchmod(fd, 0o600)
        os.close(fd)
        with sqlite3.connect(database) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('CREATE TABLE IF NOT EXISTS inbox (delivery TEXT PRIMARY KEY, receipt TEXT NOT NULL)')
            has_fingerprints = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='payload_fingerprints'").fetchone()
            db.execute('CREATE TABLE IF NOT EXISTS payload_fingerprints (sha256 TEXT PRIMARY KEY)')
            if not has_fingerprints:
                for (old_receipt,) in db.execute('SELECT receipt FROM inbox').fetchall():
                    old_hash = json.loads(old_receipt)['payload_sha256']
                    if not isinstance(old_hash, str) or not re.fullmatch(r'[a-f0-9]{64}', old_hash):
                        raise ValueError('invalid legacy receipt')
                    db.execute('INSERT OR IGNORE INTO payload_fingerprints VALUES (?)', (old_hash,))
            db.execute('INSERT INTO payload_fingerprints VALUES (?)', (payload_hash,))
            db.execute('INSERT INTO inbox VALUES (?,?)', (delivery, json.dumps(record)))
        return 202, {'status': 'simulation_queued', 'delivery': delivery, 'receipt_sha256': digest(record), 'executed': False}
    except sqlite3.IntegrityError:
        return 409, {'error': 'delivery or payload already recorded', 'executed': False}
    except (KeyError, TypeError, ValueError, AttributeError):
        return 400, {'error': 'invalid event envelope'}
    except (OSError, sqlite3.DatabaseError):
        return 503, {'error': 'inbox unavailable', 'executed': False}

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
