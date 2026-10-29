#!/usr/bin/env python3
"""
Aletheiac-Entropy Engine (AEE) v4.0 - Minimalist Skeletal Schema
Zero-Dependency Copy-Paste Veracity Diagnostic & Text Integrity Scorer

Mathematical Foundations:
  - Truth Decay Ratio: T_d = log7(max(S, 1)) / log10(max(D, 1))  (for D in {0,1}, T_d = log7(max(S, 1)))
  - Phonetic Influence Coefficient: PIC = [(s * 3.64) + ((L - s) * 1.00)] / L
  - Absolute Contamination Standard (v4.0): C = 0 -> TRUE, C > 0 -> DECEPTIVE
"""

import math
import re
from typing import Dict, List, Tuple, Any

# Canonical Lexicons (Standing Specification)
S_SET = [
    "equals", "plus", "minus", "times", "divided", "sum", "total", "result",
    "therefore", "verified", "measured", "computed", "block", "hash",
    "signature", "audit", "error", "fixed", "record", "line", "index",
    "formula", "matrix", "vector", "proof", "theorem", "derive", "derivation",
    "node", "transaction", "ledger", "math", "protocol", "code", "public",
    "matches", "first", "second", "third", "finally", "however",
    "specifically", "namely", "for example", "for instance", "in conclusion",
    "in summary", "in other words", "that is"
]

D_SET = [
    "potentially", "possibly", "reportedly", "apparently", "arguably",
    "essentially", "basically", "actually", "literally", "really",
    "somewhat", "sort of", "kind of", "maybe", "perhaps", "allegedly",
    "more or less", "roughly speaking", "to some extent", "to some degree",
    "it is important to note", "it is worth noting", "could be argued",
    "going forward", "moving forward", "holistic", "synergies", "leverage",
    "meaningful", "diverse", "various", "faceted", "evolving", "landscape",
    "exploring", "committed", "stakeholders", "engagement", "fosters",
    "remains", "suggests", "implies", "generally", "typically", "likely",
    "still under development", "i apologize for", "i understand your frustration",
    "i appreciate your patience", "as an ai", "i'm afraid", "please note that",
    "at this time", "to the best of my knowledge", "i want to be transparent",
    "keep in mind", "as of my last update", "it's important to note"
]

def aee_minimal_audit(text: str) -> Dict[str, Any]:
    """Minimalist zero-dependency diagnostic function."""
    words = text.split()
    word_count = len(words)
    text_lower = text.lower()
    
    # Structural count
    s_terms = []
    masked = text_lower
    for term in sorted(S_SET, key=lambda x: len(x.split()), reverse=True):
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = list(re.finditer(pattern, masked))
        for m in matches:
            s_terms.append(term)
        if matches:
            masked = re.sub(pattern, ' ' * len(term), masked)
    s_count = len(s_terms)
    
    # Deceptive count
    d_terms = []
    masked = text_lower
    for term in sorted(D_SET, key=lambda x: len(x.split()), reverse=True):
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = list(re.finditer(pattern, masked))
        for m in matches:
            d_terms.append(term)
        if matches:
            masked = re.sub(pattern, ' ' * len(term), masked)
    d_count = len(d_terms)
    
    # PIC calculation
    alphas = [c for c in text if c.isalpha()]
    L = len(alphas)
    s_chars = sum(1 for c in alphas if c.lower() == 's')
    pic = round(((s_chars * 3.64) + ((L - s_chars) * 1.00)) / L, 4) if L > 0 else 0.0
    
    # T_d calculation
    num = math.log(max(s_count, 1), 7)
    td = round(num if d_count in [0, 1] else num / math.log10(d_count), 4)
    
    # Absolute Contamination Law (v4.0)
    contamination = d_count
    verdict = "TRUE" if contamination == 0 and s_count > 0 else ("DECEPTIVE" if contamination > 0 else "UNMEASURABLE")
    
    return {
        "S": s_count,
        "D": d_count,
        "PIC": pic,
        "T_d": td,
        "WORDS": word_count,
        "CONTAMINATION": contamination,
        "VERDICT": verdict,
        "FLAG": d_terms[0] if d_terms else "NONE",
        "S_TERMS": s_terms,
        "D_TERMS": d_terms
    }

if __name__ == '__main__':
    sample = "We verified the mathematical formula and computed the total sum. However, the system potentially evolves synergies."
    res = aee_minimal_audit(sample)
    print("--- AEE Minimalist Diagnostic Record ---")
    for k, v in res.items():
        print(f"{k}: {v}")
