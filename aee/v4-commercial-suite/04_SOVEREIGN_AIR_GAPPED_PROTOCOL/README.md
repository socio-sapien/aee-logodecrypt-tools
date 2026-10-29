# AEE Sovereign Protocol & Air-Gapped Engine [Sovereign Edition]
### Subtitle: Ed25519 Cryptographic Verifier, RISE Inversion Check & Agent Bridge

## Overview
The Sovereign Protocol Edition provides a completely air-gapped, zero-network-dependency implementation of the Aletheiac-Entropy Engine. Engineered for national security, defense environments, critical infrastructure, and autonomous agent governance.

## Key Capabilities
- **Zero Network Sockets:** Pure on-premise execution with no external telemetry or outbound calls.
- **Ed25519 Cryptographic Receipts:** Generates signed, tamper-proof verification certificates carrying Key ID `c1f8f05e2cde23b9`.
- **RISE (Relational Inversion Structure Evaluation):** Rigorous ground-truth verification preventing action contradictions and entity hallucination.
- **Sovereign Autonomous Bridge (`sovereign_bridge_agent.py`):** On-premise agent supervisor ensuring models remain aligned and verified.
- **Local Immutable Ledger:** Embedded SQLite chassis (`oracle_chassis.db`) for cryptographically sealed audit records.

## Usage
```bash
./run_offline_sovereign.sh
python3 ed25519_receipt_verifier.py
```
