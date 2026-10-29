# AEE v4.0 Core CLI & Minimalist Schema [Developer Edition]
### Subtitle: Zero-Dependency Copy-Paste Veracity Diagnostic & Text Integrity Scorer

## Overview
The Developer Edition of the Aletheiac-Entropy Engine (AEE) v4.0 provides a lightweight, zero-dependency implementation of the standing forensic veracity audit standard. Designed for rapid integration into Python pipelines, agentic workflows, and developer tools.

## Key Capabilities
- **Zero Dependencies:** Pure Python standard library (no pip packages required).
- **Standing Mathematical Formulations:**
  - Truth Decay: $T_d = \log_7(\max(S, 1)) / \log_{10}(\max(D, 1))$
  - Phonetic Influence Coefficient: $PIC = \frac{s \times 3.64 + (L - s) \times 1.00}{L}$
  - Absolute Contamination Standard ($v4.0$): Contamination $C = 0 \implies \text{TRUE}$; $C > 0 \implies \text{DECEPTIVE}$.
- **Canonical Lexicons:** 49-term Structural Set ($S$-Set) and 58-term Evasion/Hedge Set ($D$-Set).
- **Sub-Millisecond Execution:** High-speed audit (<0.4 ms per standard paragraph).

## Quickstart
```bash
# 1. Direct CLI audit on string
python3 aee_cli.py --text "The system potentially leverages evolving synergies. We verified the audit line."

# 2. File audit with JSON output
python3 aee_cli.py --file sample_inputs/deceptive_corporate_claim.txt --json
```

## Minimalist Copy-Paste Skeleton
See `aee_minimal_skeleton.py` for a 70-line drop-in function `aee_minimal_audit(text)` ready to paste directly into your microservice or prompt validation filter.
