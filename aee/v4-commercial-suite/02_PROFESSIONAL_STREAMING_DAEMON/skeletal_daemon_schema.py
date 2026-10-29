#!/usr/bin/env python3
"""
AEE Pro Streaming - Minimalist Copy-Paste Skeletal Schema
Embeddable stream processor for microservices and async consumers.
"""
import math
import re
from typing import Dict, Any

S_SET = ["equals", "plus", "minus", "times", "divided", "sum", "total", "result", "therefore", "verified", "measured", "computed", "block", "hash", "signature", "audit", "error", "fixed", "record", "line", "index", "formula", "matrix", "vector", "proof", "theorem", "derive", "node", "transaction", "ledger", "math", "protocol", "code", "public", "matches"]
D_SET = ["potentially", "possibly", "reportedly", "apparently", "arguably", "essentially", "basically", "actually", "literally", "really", "somewhat", "maybe", "perhaps", "allegedly", "holistic", "synergies", "leverage", "evolving", "fosters", "suggests", "implies", "likely"]

class StreamAuditor:
    def __init__(self):
        self.s_regex = re.compile(r'\b(' + '|'.join(S_SET) + r')\b', re.IGNORECASE)
        self.d_regex = re.compile(r'\b(' + '|'.join(D_SET) + r')\b', re.IGNORECASE)

    def audit(self, text: str) -> Dict[str, Any]:
        s_matches = self.s_regex.findall(text)
        d_matches = self.d_regex.findall(text)
        s_count = len(s_matches)
        d_count = len(d_matches)
        words = len(text.split())

        num = math.log(max(s_count, 1), 7)
        td = round(num if d_count in [0, 1] else num / math.log10(d_count), 4)
        verdict = "TRUE" if d_count == 0 and s_count > 0 else ("DECEPTIVE" if d_count > 0 else "UNMEASURABLE")

        return {
            "S": s_count,
            "D": d_count,
            "T_d": td,
            "WORDS": words,
            "CONTAMINATION": d_count,
            "VERDICT": verdict,
            "FIRST_LOCUS": d_matches[0] if d_matches else "NONE"
        }
