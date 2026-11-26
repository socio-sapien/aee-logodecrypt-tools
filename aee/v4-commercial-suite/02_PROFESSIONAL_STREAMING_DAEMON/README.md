> Safety note (2026-11-26): This is a prototype, not a comprehensive privacy or secret-redaction tool. Its pattern-based cleaner can leave names, IPv6 addresses and credentials in the output. The daemon now preserves its input and refuses to overwrite existing output or audit files. This changes the prior delete-after-processing behavior. A write failure, destination collision, or process crash can leave incomplete outputs, which must be inspected before retrying. Retained inputs are skipped only during the current process; a restart encounters existing output names and refuses to overwrite them. Do not rely on output being safe to share. The latency and production-readiness claims below have not been established by this test.

# AEE v4.0 Pro Daemon & Streaming Pipeline [Professional Edition]
### Subtitle: Automated High-Throughput Ingestion & Metadata Sanitization Harness

## Overview
The Professional Edition provides an automated, continuous background daemon and file-watcher pipeline designed for enterprise streaming architectures, ingestion queues, and automated data cleaning.

## Key Capabilities
- **Continuous Watcher Daemon:** Automated polling and processing of streaming directories.
- **5-Pass Invasive Metadata Cleaner:** Neutralizes steganographic zero-width characters, scrubbed credentials/API keys, network footprints, and PII.
- **Sub-Millisecond Pipeline Latency:** Processes streaming text payloads in <0.5 ms.
- **Production Systemd Service:** Complete system service descriptor for Linux enterprise servers.
- **Clean Skeletal Schema:** Embeddable `StreamAuditor` for custom microservices.

## Running the Daemon
```bash
python3 aee_daemon.py
```
Drop any `.txt` or `.json` file into `watch_incoming/` and inspect results in `watch_processed/` and `audit_logs/`.

## File handling and compatibility
Output and audit directories must be outside the watched directory. Inputs are retained, not removed; successful unchanged files are skipped while the same daemon process runs. Existing `sanitized_<filename>` or `audit_<filename>.json` paths cause processing to fail without overwriting either file. A changed input with the same name also needs a new destination or manual handling. After a restart, existing output files prevent reprocessing; move or rename outputs deliberately before retrying. Failed or interrupted processing can leave empty or partial outputs; nothing is automatically deleted. This is not a concurrency, filesystem security or durable queue guarantee. `process_file` returns `True` on success and `False` on skip or failure. The cleaner remains pattern-based and incomplete: treat all output as potentially sensitive.

### Inspecting a blocked retry

Before handling real files, stop the daemon and ensure no other process is writing to these directories. For the affected input `NAME`, inspect both `sanitized_NAME` in the output directory and `audit_NAME.json` in the audit directory. A failed attempt may leave either file empty or incomplete. In a synthetic test, an existing audit file caused a new empty output to be left behind; moving only the audit file still left the retry blocked by that output. A JSON write error also left both paths blocking the next attempt.

If reprocessing is appropriate, preserve any existing output and audit files in a separate, access-controlled location before retrying, and keep the input. Both original destination names must be free; an existing path is never overwritten. Examine the files and decide which results to keep before moving them. Repeated polling can log the same collision on every pass. These observations are from isolated synthetic tests, not a crash-recovery or concurrent-filesystem guarantee. Outputs and audit files can contain sensitive data; the cleaner is not comprehensive.
