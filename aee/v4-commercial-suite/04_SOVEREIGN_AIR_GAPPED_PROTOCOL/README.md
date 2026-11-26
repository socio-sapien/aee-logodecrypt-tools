# AEE Sovereign Protocol — experimental prototype

This directory contains experimental code. Do not use it to authenticate receipts, secure custody, or make security-critical decisions.

## Receipt limitation

`ed25519_receipt_verifier.py` does not implement Ed25519 signing or signature verification. It generates a simulated SHA-512 digest and `verify_receipt` compares only a SHA-256 hash of the payload. A receipt with an absent or invalid signature can pass; a changed payload can pass if its hash is recomputed. A matching digest is not proof of authenticity or tamper resistance against an adversary.

The other components have not been independently validated as an air-gapped security system, ground-truth verifier, immutable ledger, or production agent supervisor. Their presence here is not a security certification.

Run the receipt example locally with `python3 ed25519_receipt_verifier.py`. It is a consistency demonstration only.
