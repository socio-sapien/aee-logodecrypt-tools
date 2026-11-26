# AEE Sovereign Protocol — experimental prototype

This directory contains experimental code. Do not use it to authenticate receipts, secure custody, or make security-critical decisions.

## Receipt limitation

`ed25519_receipt_verifier.py` does not implement Ed25519 signing or verification. Both legacy methods now raise `NotImplementedError` rather than claiming a simulated digest is a signature or accepting a checksum as authentication. Older simulated receipts cannot be authenticated by this module. This is a breaking change for callers; no signed-byte format, trusted-key contract, or audited signing implementation has been established.

The other components have not been independently validated as an air-gapped security system, ground-truth verifier, immutable ledger, or production agent supervisor. Their presence here is not a security certification.

Running `python3 ed25519_receipt_verifier.py` reports the unsupported operation and exits nonzero.
