#!/usr/bin/env python3
"""
AEE v4.0 Pro Daemon - Professional Edition
Continuous High-Throughput Streaming Audit & Metadata Sanitization Worker
"""
import os
import sys
import time
import json
import threading
from typing import Dict, Any

from aee_sanitizer import InvasiveMetadataCleaner
from skeletal_daemon_schema import StreamAuditor

class AEEDaemon:
    def __init__(self, watch_dir: str = "./watch_incoming", out_dir: str = "./watch_processed", log_dir: str = "./audit_logs"):
        self.watch_dir = watch_dir
        self.out_dir = out_dir
        self.log_dir = log_dir
        self.auditor = StreamAuditor()
        self.cleaner = InvasiveMetadataCleaner()
        self.running = False
        # Successful versions are skipped only for the lifetime of this process.
        self._processed = {}
        
        watch = os.path.realpath(self.watch_dir)
        for output_dir in (self.out_dir, self.log_dir):
            if os.path.commonpath((watch, os.path.realpath(output_dir))) == watch:
                raise ValueError("output and audit directories must be outside watch_dir")

        for d in [self.watch_dir, self.out_dir, self.log_dir]:
            os.makedirs(d, exist_ok=True)

    def process_file(self, filepath: str):
        try:
            filename = os.path.basename(filepath)
            # Capture the opened file identity, not a possibly replaced pathname.
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                st = os.fstat(f.fileno())
                fingerprint = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
                if self._processed.get(os.path.abspath(filepath)) == fingerprint:
                    return False
                content = f.read()
                after = os.fstat(f.fileno())
                if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != fingerprint:
                    raise RuntimeError("input changed during reading")

            # 1. Run Invasive Sanitization
            cleaned_text = self.cleaner.clean_text(content, aggressive=True)

            # 2. Run High-Throughput Veracity Audit
            audit_res = self.auditor.audit(cleaned_text)
            audit_res["source_file"] = filename
            audit_res["timestamp"] = time.time()

            # Exclusive creation refuses existing destinations. A failure may leave
            # a partial pair; do not delete anything automatically on failure.
            out_path = os.path.join(self.out_dir, f"sanitized_{filename}")
            log_path = os.path.join(self.log_dir, f"audit_{filename}.json")
            with open(out_path, "x", encoding="utf-8") as out:
                with open(log_path, "x", encoding="utf-8") as log:
                    out.write(cleaned_text)
                    json.dump(audit_res, log, indent=2)

            self._processed[os.path.abspath(filepath)] = fingerprint
            print(f"[AEE-DAEMON] Processed: {filename} -> Verdict: {audit_res['VERDICT']} (Td={audit_res['T_d']})")
            return True
        except Exception as e:
            print(f"[AEE-DAEMON] Error processing {filepath}: {e}")
            return False

    def run_poll(self, interval: float = 1.0, max_iterations: int = None):
        self.running = True
        iterations = 0
        print(f"[AEE-DAEMON] Watching directory: {self.watch_dir}")
        while self.running:
            files = [os.path.join(self.watch_dir, f) for f in os.listdir(self.watch_dir) if os.path.isfile(os.path.join(self.watch_dir, f))]
            for f in files:
                self.process_file(f)
            iterations += 1
            if max_iterations and iterations >= max_iterations:
                break
            time.sleep(interval)

if __name__ == "__main__":
    daemon = AEEDaemon()
    daemon.run_poll()
