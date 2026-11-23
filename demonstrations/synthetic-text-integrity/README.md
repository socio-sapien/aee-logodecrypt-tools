# Synthetic text-hash consistency example

This offline Python example compares each record's supplied SHA-256 against the UTF-8 encoding of its `text` field. It uses newly written synthetic examples; it contains no original benchmark specimens. Python 3.9 or later is needed; no extra packages or network connection are required.

```sh
python check_text_hashes.py synthetic_records.json
python -m unittest -v test_check_text_hashes
```

For other local input, provide a JSON array of objects with nonempty `text` strings and lowercase 64-character hexadecimal `sha256` strings. Exit status is 0 for all matches, 1 for invalid records or mismatches, and 2 for unreadable or invalid JSON. Errors identify the row number but do not print its text. An input file and its contents remain on the local machine; this tool makes no network requests.

A match establishes consistency between the supplied text and digest only. It does not authenticate authorship, chain of custody, original file bytes, factual truth, or a digest supplied by an attacker. Different Unicode normalization or line endings yield different hashes. This is an independent synthetic illustration, not the original Gate 1, a full benchmark gate, tokenizer test, security certification, or validation of other AEE tools. It is not integrated into the benchmark or CI workflow.
