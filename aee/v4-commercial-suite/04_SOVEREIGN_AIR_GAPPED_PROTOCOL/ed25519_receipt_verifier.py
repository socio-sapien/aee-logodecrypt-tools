#!/usr/bin/env python3
"""Legacy receipt example: cryptographic signing/verification is unavailable.

Both legacy APIs fail closed. Existing simulated receipts are not signatures.
No trusted key, signature encoding, or signed-byte protocol has been established;
implementing cryptography without those contracts would give false assurance.
"""
from typing import Any, Dict


class Ed25519ReceiptVerifier:
    DEFAULT_KEY_ID = "c1f8f05e2cde23b9"

    @staticmethod
    def generate_signed_receipt(audit_payload: Dict[str, Any], key_id: str = DEFAULT_KEY_ID) -> Dict[str, Any]:
        raise NotImplementedError("Ed25519 signing is not implemented; no receipt was signed")

    @staticmethod
    def verify_receipt(receipt: Dict[str, Any]) -> bool:
        raise NotImplementedError("Ed25519 verification is not implemented; receipt is unverified")


if __name__ == "__main__":
    import sys
    print("Ed25519 verification is not implemented; receipts cannot be authenticated.", file=sys.stderr)
    sys.exit(1)
