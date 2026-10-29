#!/usr/bin/env bash
# Sovereign Offline Launcher
export PYTHONUNBUFFERED=1
echo "=== Starting AEE Sovereign Unified Engine (Air-Gapped Mode) ==="
python3 oracle_sovereign_unified.py --offline --local-ledger ./oracle_chassis.db
