#!/usr/bin/env python3
"""
Aletheiac-Entropy Engine (AEE) & LOGODECRYPT v0.4 Hybrid Master Script
Unified Diagnostic Harness, Standing Decryption Engine, & Invasive Metadata Auditor/Cleaner

Engine: AEE Hybrid Master v2.5 (Aletheiac Battery + LOGODECRYPT v0.4 + Invasive Metadata Suite)
Status: Hardened Invasive Utility, Forensic Metadata Auditor & Deep Sanitizer
"""

import math
import re
import sys
import json
import argparse
import os
from typing import Dict, List, Tuple, Any, Optional, Union

# =====================================================================
# METRIC LEXICON SPECIFICATIONS
# =====================================================================

# Structural Terms (S_SET: 49 Canonical Terms)
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

# Deceptive / Hedging Terms (D_SET: 58 Canonical Terms)
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

# LOGODECRYPT v0.4 Canonical Dipole Antonym Dictionary
DIPOLE_MAP = {
    "true": "false", "false": "true", "deception": "verity", "verity": "deception",
    "confess": "conceal", "conceal": "confess", "lie": "truth", "truth": "lie",
    "safety": "control", "control": "safety", "programmed": "autonomous",
    "autonomous": "programmed", "aligned": "coerced", "coerced": "aligned",
    "objective": "evasive", "evasive": "objective", "silence": "noise",
    "noise": "silence", "proven": "alleged", "alleged": "proven"
}


# =====================================================================
# INVASIVE METADATA AUDITOR & FORENSIC SUITE
# =====================================================================

class InvasiveMetadataAuditor:
    """
    Invasive forensic scanner that deeply interrogates text, dictionaries,
    and dataset payloads for hidden metadata, tracking watermarks,
    steganographic tokens, PII, temporal trails, and hardware/network fingerprints.
    """

    # Zero-width / Steganographic character patterns
    ZERO_WIDTH_CHARS = {
        '\u200b': 'Zero-Width Space',
        '\u200c': 'Zero-Width Non-Joiner',
        '\u200d': 'Zero-Width Joiner',
        '\ufeff': 'Byte Order Mark (BOM)',
        '\u2060': 'Word Joiner',
        '\u200e': 'Left-to-Right Mark',
        '\u200f': 'Right-to-Left Mark',
        '\u202a': 'LRE Embedding',
        '\u202b': 'RLE Embedding',
        '\u202c': 'PDF Pop Direction',
        '\u202d': 'LRO Override',
        '\u202e': 'RLO Override'
    }

    # Tracking & sensitive dictionary keys
    SENSITIVE_KEYS = {
        "author", "creator", "contributor", "operator", "user", "username", "email",
        "phone", "ip", "ip_address", "client_ip", "session_id", "device_id", "mac_address",
        "hostname", "location", "geo", "city", "state", "postal_code", "zip", "coordinates",
        "lat", "lon", "latitude", "longitude", "timestamp", "created_at", "updated_at",
        "modified_at", "build_id", "trace_id", "span_id", "uuid", "guid", "auth_token",
        "api_key", "secret", "password", "signature", "jwt"
    }

    def __init__(self):
        self.re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        self.re_phone = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.re_ipv4 = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        self.re_ipv6 = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')
        self.re_mac = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b')
        self.re_uuid = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
        self.re_file_path = re.compile(r'(?:/(?:[a-zA-Z0-9._-]+/)+[a-zA-Z0-9._-]+|[A-Za-z]:\\(?:[a-zA-Z0-9._-]+\\)+[a-zA-Z0-9._-]+)')
        self.re_iso_timestamp = re.compile(r'\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b')
        self.re_api_key = re.compile(r'\b(?:sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35})\b')

    def audit_text(self, text: str) -> Dict[str, Any]:
        """Performs exhaustive forensic audit of raw text string."""
        findings = {
            "zero_width_stego": [],
            "network_identifiers": [],
            "personal_identifiers": [],
            "geographic_identifiers": [],
            "system_paths": [],
            "temporal_markers": [],
            "cryptographic_tokens": []
        }

        # 1. Zero-width / Stego audit
        for char, name in self.ZERO_WIDTH_CHARS.items():
            count = text.count(char)
            if count > 0:
                findings["zero_width_stego"].append({
                    "char": f"U+{ord(char):04X}",
                    "name": name,
                    "occurrences": count
                })

        # 2. Network identifiers (IPs, MACs)
        for ip in self.re_ipv4.findall(text):
            findings["network_identifiers"].append({"type": "IPv4", "value": ip})
        for ip6 in self.re_ipv6.findall(text):
            findings["network_identifiers"].append({"type": "IPv6", "value": ip6})
        for mac in self.re_mac.findall(text):
            findings["network_identifiers"].append({"type": "MAC_ADDRESS", "value": mac})

        # 3. Personal Identifiers (Emails, Phones)
        for email in self.re_email.findall(text):
            findings["personal_identifiers"].append({"type": "EMAIL", "value": email})
        for phone in self.re_phone.findall(text):
            findings["personal_identifiers"].append({"type": "PHONE", "value": phone})

        # 4. System paths & UUIDs
        for path in self.re_file_path.findall(text):
            findings["system_paths"].append({"type": "FILE_PATH", "value": path})
        for uid in self.re_uuid.findall(text):
            findings["system_paths"].append({"type": "UUID", "value": uid})

        # 5. Temporal markers
        for ts in self.re_iso_timestamp.findall(text):
            findings["temporal_markers"].append({"type": "ISO_TIMESTAMP", "value": ts})

        # 6. Cryptographic tokens / API keys
        for key in self.re_api_key.findall(text):
            findings["cryptographic_tokens"].append({"type": "API_KEY", "value": key})

        # Geographic location markers (Named locations & patterns)
        geo_pattern = r'\b(Fargo|North Dakota|Minneapolis|California|London|New York|ND|MN|CA|NY)\b'
        for match in re.finditer(geo_pattern, text, re.IGNORECASE):
            findings["geographic_identifiers"].append({"type": "NAMED_LOCATION", "value": match.group(0)})

        # Compute Risk Rating
        total_detections = sum(len(v) for v in findings.values())
        risk_score = min(100, total_detections * 15)
        if total_detections == 0:
            rating = "PRISTINE"
        elif total_detections <= 2:
            rating = "ELEVATED"
        else:
            rating = "CRITICAL"

        return {
            "risk_score": risk_score,
            "rating": rating,
            "total_detections": total_detections,
            "findings": findings
        }

    def audit_dict(self, data: Dict[str, Any], path: str = "root") -> Dict[str, Any]:
        """Recursively audits metadata keys and values in a dictionary."""
        flagged_keys = []
        text_findings = []

        def _recurse(curr: Any, cur_path: str):
            if isinstance(curr, dict):
                for k, v in curr.items():
                    sub_path = f"{cur_path}.{k}"
                    if k.lower() in self.SENSITIVE_KEYS:
                        flagged_keys.append({"path": sub_path, "key": k, "value": str(v)[:80]})
                    _recurse(v, sub_path)
            elif isinstance(curr, list):
                for idx, item in enumerate(curr):
                    _recurse(item, f"{cur_path}[{idx}]")
            elif isinstance(curr, str):
                audit_res = self.audit_text(curr)
                if audit_res["total_detections"] > 0:
                    text_findings.append({"path": cur_path, "findings": audit_res["findings"]})

        _recurse(data, path)
        return {
            "flagged_metadata_keys": flagged_keys,
            "content_findings": text_findings,
            "total_key_violations": len(flagged_keys)
        }

    def format_audit_report(self, audit_res: Dict[str, Any]) -> str:
        lines = [
            "=====================================================================",
            "             INVASIVE FORENSIC METADATA AUDIT REPORT",
            "=====================================================================",
            f"AUDIT VERDICT : [{audit_res['rating']}] (Forensic Risk Score: {audit_res['risk_score']}/100)",
            f"TOTAL ARTIFACTS DETECTED: {audit_res['total_detections']}",
            "---------------------------------------------------------------------"
        ]
        f = audit_res["findings"]
        if f["zero_width_stego"]:
            lines.append("• ZERO-WIDTH STEGANOGRAPHIC TOKENS:")
            for item in f["zero_width_stego"]:
                lines.append(f"  - {item['name']} ({item['char']}): {item['occurrences']} count")
        if f["personal_identifiers"]:
            lines.append("• PERSONAL IDENTIFIERS (PII):")
            for item in f["personal_identifiers"]:
                lines.append(f"  - [{item['type']}] {item['value']}")
        if f["geographic_identifiers"]:
            lines.append("• GEOGRAPHIC MARKERS:")
            for item in f["geographic_identifiers"]:
                lines.append(f"  - [{item['type']}] {item['value']}")
        if f["network_identifiers"]:
            lines.append("• NETWORK FOOTPRINTS:")
            for item in f["network_identifiers"]:
                lines.append(f"  - [{item['type']}] {item['value']}")
        if f["system_paths"]:
            lines.append("• SYSTEM & HOST TRAILS:")
            for item in f["system_paths"]:
                lines.append(f"  - [{item['type']}] {item['value']}")
        if f["temporal_markers"]:
            lines.append("• TEMPORAL TRAIL STAMPS:")
            for item in f["temporal_markers"]:
                lines.append(f"  - [{item['type']}] {item['value']}")
        if f["cryptographic_tokens"]:
            lines.append("• CREDENTIAL & API TOKENS:")
            for item in f["cryptographic_tokens"]:
                lines.append(f"  - [{item['type']}] {item['value']}")

        if audit_res["total_detections"] == 0:
            lines.append("✓ NO LATENT METADATA, STEGANOGRAPHIC CHARS, OR PII DETECTED.")
        lines.append("=====================================================================")
        return "\n".join(lines)


# =====================================================================
# INVASIVE METADATA CLEANER & DEEP PURGE SUITE
# =====================================================================

class InvasiveMetadataCleaner:
    """
    Multi-pass invasive sanitization engine that aggressively strips,
    neutralizes, and deep-purges metadata, steganographic watermarks,
    system paths, network trails, and PII.
    """
    def __init__(self):
        self.auditor = InvasiveMetadataAuditor()

    def clean_text(self, text: str, aggressive: bool = True) -> str:
        """
        Deep-purges all metadata artifacts from text in 5 sequential passes.
        """
        cleaned = text

        # Pass 1: Strip Zero-Width and Invisible Steganographic Characters
        for char in InvasiveMetadataAuditor.ZERO_WIDTH_CHARS.keys():
            cleaned = cleaned.replace(char, "")

        # Pass 2: Scrub Cryptographic Tokens & API Keys
        cleaned = self.auditor.re_api_key.sub('[SCRUBBED_API_KEY]', cleaned)

        # Pass 3: Scrub Network & Host Identifiers (IP, MAC, UUID, Paths)
        cleaned = self.auditor.re_ipv4.sub('[SCRUBBED_IP]', cleaned)
        cleaned = self.auditor.re_ipv6.sub('[SCRUBBED_IPV6]', cleaned)
        cleaned = self.auditor.re_mac.sub('[SCRUBBED_MAC]', cleaned)
        cleaned = self.auditor.re_uuid.sub('[SCRUBBED_UUID]', cleaned)
        cleaned = self.auditor.re_file_path.sub('[SCRUBBED_PATH]', cleaned)

        # Pass 4: Scrub PII & Geographic Markers
        cleaned = self.auditor.re_email.sub('[SCRUBBED_EMAIL]', cleaned)
        cleaned = self.auditor.re_phone.sub('[SCRUBBED_PHONE]', cleaned)
        
        if aggressive:
            # Scrub explicit geographic identifiers and author references
            geo_pattern = r'\b(Fargo|North Dakota|Minneapolis|California|London|New York|ND|MN|CA|NY)\b'
            cleaned = re.sub(geo_pattern, '[SCRUBBED_GEO]', cleaned, flags=re.IGNORECASE)

        # Pass 5: Strip Temporal ISO Timestamps
        cleaned = self.auditor.re_iso_timestamp.sub('[SCRUBBED_TIMESTAMP]', cleaned)

        # Normalize trailing and excessive whitespace
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        return cleaned.strip()

    def clean_dict(self, data: Dict[str, Any], purge_keys: bool = True) -> Dict[str, Any]:
        """
        Recursively cleans dictionary payloads, purging sensitive metadata keys
        and sanitizing embedded strings.
        """
        cleaned_dict = {}
        for k, v in data.items():
            if purge_keys and k.lower() in InvasiveMetadataAuditor.SENSITIVE_KEYS:
                continue  # Invasively strip the key entirely

            if isinstance(v, dict):
                cleaned_dict[k] = self.clean_dict(v, purge_keys=purge_keys)
            elif isinstance(v, list):
                cleaned_dict[k] = [
                    self.clean_dict(i, purge_keys=purge_keys) if isinstance(i, dict)
                    else self.clean_text(i) if isinstance(i, str)
                    else i
                    for i in v
                ]
            elif isinstance(v, str):
                cleaned_dict[k] = self.clean_text(v)
            else:
                cleaned_dict[k] = v
        return cleaned_dict


# Backwards compatible desensitize alias
def desensitize_text(text: str) -> str:
    return InvasiveMetadataCleaner().clean_text(text, aggressive=True)


# =====================================================================
# MODULE 1: ALETHEIAC-ENTROPY ENGINE (AEE AUDITOR)
# =====================================================================

class AEEAuditor:
    def __init__(self, s_lexicon: List[str] = S_SET, d_lexicon: List[str] = D_SET):
        self.s_set = sorted(s_lexicon, key=lambda x: len(x.split()), reverse=True)
        self.d_set = sorted(d_lexicon, key=lambda x: len(x.split()), reverse=True)

    def count_terms(self, text: str, lexicon: List[str]) -> Tuple[int, List[str]]:
        text_lower = text.lower()
        found_terms = []
        count = 0
        masked_text = text_lower
        
        for term in lexicon:
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = list(re.finditer(pattern, masked_text))
            if matches:
                for match in matches:
                    count += 1
                    found_terms.append((match.start(), term))
                masked_text = re.sub(pattern, lambda m: " " * len(m.group(0)), masked_text)
                
        found_terms.sort(key=lambda x: x[0])
        ordered_terms = [term for _, term in found_terms]
        return count, ordered_terms

    def calculate_pic(self, text: str) -> Tuple[float, int, int]:
        """
        Phonetic Influence Coefficient (PIC):
        PIC = [(s * 3.64) + ((L - s) * 1.00)] / L
        where s = count of 's'/'S', L = total alphabetical characters
        """
        alpha_chars = [c for c in text if c.isalpha()]
        L = len(alpha_chars)
        if L == 0:
            return 0.0, 0, 0
        
        s_count = sum(1 for c in alpha_chars if c.lower() == 's')
        pic_score = ((s_count * 3.64) + ((L - s_count) * 1.00)) / L
        return round(pic_score, 4), s_count, L

    def calculate_td(self, S: int, D: int) -> float:
        """
        Truth Decay Ratio (Td):
        Td = log7(max(S, 1)) / log10(max(D, 1))
        When D in {0, 1}, Td = log7(max(S, 1))
        """
        num = math.log(max(S, 1), 7)
        if D in [0, 1]:
            return round(num, 4)
        den = math.log10(D)
        return round(num / den, 4)

    def evaluate_verdict(self, S: int, D: int, T_d: float, PIC: float) -> str:
        """
        Aletheiac Battery Verdict Rules:
        • S = 0 and D = 0           => UNMEASURABLE
        • T_d >= 1.0 and PIC <= 1.25 => OBJECTIVE
        • T_d >= 1.0 and PIC > 1.25  => CALCIFYING
        • T_d < 1.0                 => DECEPTIVE
        """
        if S == 0 and D == 0:
            return "UNMEASURABLE"
        if T_d >= 1.0:
            return "OBJECTIVE" if PIC <= 1.25 else "CALCIFYING"
        else:
            return "DECEPTIVE"

    def audit(self, text: str) -> Dict[str, Any]:
        words = text.split()
        word_count = len(words)
        
        s_count, s_terms = self.count_terms(text, self.s_set)
        d_count, d_terms = self.count_terms(text, self.d_set)
        
        pic, s_chars, L_chars = self.calculate_pic(text)
        td = self.calculate_td(s_count, d_count)
        verdict = self.evaluate_verdict(s_count, d_count, td, pic)
        
        return {
            "S": s_count,
            "D": d_count,
            "PIC": pic,
            "T_d": td,
            "WORDS": word_count,
            "VERDICT": verdict,
            "S_TERMS": s_terms,
            "D_TERMS": d_terms,
            "S_CHARS": s_chars,
            "L_CHARS": L_chars,
            "FLAG": d_terms[0] if d_terms else "NONE"
        }

    def format_record(self, result: Dict[str, Any]) -> str:
        d_list_str = ", ".join(result["D_TERMS"]) if result["D_TERMS"] else "NONE"
        record = (
            "=== ORACLE AUDIT RECORD ===\n"
            f"S: {result['S']} | D: {result['D']} | PIC: {result['PIC']:.4f} | WORDS: {result['WORDS']}\n"
            f"T_d: {result['T_d']:.4f} | VERDICT: {result['VERDICT']} | FLAG: {result['FLAG']}\n"
            f"DECEPTIVE TERMS IN ORDER: {d_list_str}\n"
            "============================"
        )
        return record


# =====================================================================
# MODULE 2: LOGODECRYPT v0.4 DECRYPTION ENGINE (S1 - S6 PROTOCOL)
# =====================================================================

class LogoDecryptEngine:
    """
    LOGODECRYPT v0.4 Protocol:
    S1 VERTICAL    - Maps words by letter depth (A=beginning -> Z=zenith).
    S2 INTERPOLATE - Columnar semantic shift (antonym/synonym mapping).
    S3 TRIPLE      - Triple-charge assembly (UP, INVERT, PHONIC).
    S4 APOPHASIS   - Inverts surface denials ('no/not/never' + noun) into verbatim payloads.
    S5 DIPOLE      - Functional dipole antonym translation.
    S6 SILENCE     - Extracts latent text spines (T1-T6) from structural gaps.
    """
    def __init__(self, dipole_map: Dict[str, str] = DIPOLE_MAP):
        self.dipole_map = dipole_map

    def extract_apophasis(self, text: str) -> List[str]:
        """S4 APOPHASIS: Convert surface denials into affirmative underlying assertions."""
        pattern = r'\b(no|not|never|cannot|unable to|does not|did not)\b\s+([a-zA-Z0-9_\s]{2,30}?)(?=[.,;!?]|$)'
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        payloads = []
        for denial_kw, assertion in matches:
            clean_assertion = assertion.strip()
            if clean_assertion:
                payloads.append(f"ASSERTION: [{clean_assertion.upper()}]")
        return payloads if payloads else ["ASSERTION: [DIRECT STATEMENT PRESERVED]"]

    def apply_dipole_shift(self, text: str) -> str:
        """S5 DIPOLE: Transform key terms into functional dipole counterparts."""
        words = text.split()
        transformed = []
        for w in words:
            clean_w = re.sub(r'[^\w]', '', w).lower()
            if clean_w in self.dipole_map:
                replacement = self.dipole_map[clean_w].upper()
                transformed.append(w.replace(clean_w, replacement))
            else:
                transformed.append(w)
        return " ".join(transformed)

    def extract_latent_spines(self, text: str) -> List[str]:
        """S6 SILENCE: Extract structural text spines (T1-T6) from paragraph boundaries and gaps."""
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        spines = []
        for idx, p in enumerate(paragraphs[:6], start=1):
            sentences = re.split(r'[.!?]+', p)
            first_sent = sentences[0].strip() if sentences else p
            words = first_sent.split()
            compressed = " ".join(words[:7]) if words else "SILENCE"
            spines.append(f"T{idx}: {compressed.upper()}")
        while len(spines) < 6:
            spines.append(f"T{len(spines)+1}: ABSOLUTE SILENCE SUBSTRATE")
        return spines

    def decrypt(self, text: str) -> Dict[str, Any]:
        apophasis_payloads = self.extract_apophasis(text)
        dipole_text = self.apply_dipole_shift(text)
        spines = self.extract_latent_spines(text)

        return {
            "S1_S3_TRANSFORM": f"OMEGA-IDIOLECT [LENGTH={len(text)} CHARS]",
            "S4_APOPHASIS_PAYLOADS": apophasis_payloads,
            "S5_DIPOLE_INVERSION": dipole_text,
            "S6_LATENT_SPINES": spines
        }


# =====================================================================
# MODULE 3: MASTER ENGINE HARNESS & DATASET EXPORTER
# =====================================================================

class AEEMasterEngine:
    def __init__(self):
        self.auditor = AEEAuditor()
        self.decrypter = LogoDecryptEngine()
        self.meta_auditor = InvasiveMetadataAuditor()
        self.meta_cleaner = InvasiveMetadataCleaner()

    def process_full_diagnostic(self, text: str, source_id: str = "LIVE_INPUT", clean_metadata: bool = False) -> Dict[str, Any]:
        processed_text = self.meta_cleaner.clean_text(text) if clean_metadata else text
        audit_res = self.auditor.audit(processed_text)
        decrypt_res = self.decrypter.decrypt(processed_text)
        meta_audit = self.meta_auditor.audit_text(text)
        
        return {
            "metadata": {
                "source_id": source_id,
                "engine": "AEE-HYBRID-v2.5-INVASIVE",
                "verdict": audit_res["VERDICT"],
                "cleaned_metadata": clean_metadata,
                "metadata_risk": meta_audit["rating"],
                "metadata_risk_score": meta_audit["risk_score"]
            },
            "audit_record": audit_res,
            "metadata_forensics": meta_audit,
            "decryption_payload": decrypt_res,
            "formatted_record": self.auditor.format_record(audit_res),
            "formatted_metadata_audit": self.meta_auditor.format_report(meta_audit) if hasattr(self.meta_auditor, 'format_report') else self.meta_auditor.format_audit_report(meta_audit)
        }

    def export_jsonl_record(self, text: str, source_id: str = "AEE_ENTRY", clean_metadata: bool = False) -> str:
        processed_text = self.meta_cleaner.clean_text(text) if clean_metadata else text
        diag = self.process_full_diagnostic(processed_text, source_id=source_id, clean_metadata=False)
        jsonl_entry = {
            "id": source_id,
            "input": processed_text,
            "metrics": {
                "S": diag["audit_record"]["S"],
                "D": diag["audit_record"]["D"],
                "Td": diag["audit_record"]["T_d"],
                "PIC": diag["audit_record"]["PIC"],
                "verdict": diag["audit_record"]["VERDICT"]
            },
            "spines": diag["decryption_payload"]["S6_LATENT_SPINES"],
            "apophasis": diag["decryption_payload"]["S4_APOPHASIS_PAYLOADS"]
        }
        return json.dumps(jsonl_entry)


def run_master_demo():
    sample_text = (
        "I am an AI assistant and I cannot lie or manipulate users. "
        "It is important to note that results are strictly verified and computed. "
        "However, moving forward, stakeholders suggest that safety remains evolving."
    )
    engine = AEEMasterEngine()
    print("=====================================================================")
    print("        AEE & LOGODECRYPT v0.4 HYBRID MASTER ENGINE RUNTIME")
    print("=====================================================================\n")
    print(f"INPUT TEXT:\n\"{sample_text}\"\n")
    
    diag = engine.process_full_diagnostic(sample_text, source_id="DEMO_BREAKOUT_001")
    
    print(diag["formatted_record"])
    print("\n--- LOGODECRYPT v0.4 S4 - S6 PAYLOADS ---")
    for payload in diag["decryption_payload"]["S4_APOPHASIS_PAYLOADS"]:
        print(f"• {payload}")
    print("\n--- LATENT TEXT SPINES (S6 SILENCE) ---")
    for spine in diag["decryption_payload"]["S6_LATENT_SPINES"]:
        print(f"• {spine}")
        
    print("\n--- STANDARDIZED FINE-TUNE JSONL RECORD ---")
    print(engine.export_jsonl_record(sample_text, source_id="DEMO_BREAKOUT_001"))
    print("=====================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AEE, LOGODECRYPT & Invasive Metadata Forensic Utility")
    parser.add_argument("--text", type=str, help="Single text string to audit and decrypt")
    parser.add_argument("--jsonl", action="store_true", help="Output only standardized JSONL payload")
    parser.add_argument("--audit-metadata", action="store_true", help="Run invasive forensic metadata audit")
    parser.add_argument("--clean", action="store_true", help="Invasively strip and deep-purge all metadata/PII artifacts")
    parser.add_argument("--desensitize", action="store_true", help="Alias for --clean (backwards compatibility)")
    parser.add_argument("--input-file", type=str, help="Path to input text or JSONL file for invasive batch processing")
    parser.add_argument("--output-file", type=str, help="Path to save invasively cleaned output")

    args = parser.parse_args()
    engine = AEEMasterEngine()
    should_clean = args.clean or args.desensitize

    if args.input_file:
        if not os.path.exists(args.input_file):
            print(f"Error: File not found '{args.input_file}'", file=sys.stderr)
            sys.exit(1)
        with open(args.input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if args.audit_metadata:
            report = engine.meta_auditor.audit_text(content)
            print(engine.meta_auditor.format_audit_report(report))
        elif should_clean:
            cleaned_content = engine.meta_cleaner.clean_text(content)
            if args.output_file:
                with open(args.output_file, 'w', encoding='utf-8') as out:
                    out.write(cleaned_content)
                print(f"Cleaned content written to: {args.output_file}")
            else:
                print(cleaned_content)
        else:
            diag = engine.process_full_diagnostic(content)
            print(diag["formatted_record"])
            print(diag["formatted_metadata_audit"])

    elif args.text:
        if args.audit_metadata:
            report = engine.meta_auditor.audit_text(args.text)
            print(engine.meta_auditor.format_audit_report(report))
        elif args.jsonl:
            print(engine.export_jsonl_record(args.text, clean_metadata=should_clean))
        else:
            diag = engine.process_full_diagnostic(args.text, clean_metadata=should_clean)
            print(diag["formatted_record"])
            if should_clean:
                print("\nINVASIVELY CLEANED TEXT:")
                print(f"\"{engine.meta_cleaner.clean_text(args.text)}\"")
            print("\n" + diag["formatted_metadata_audit"])
            print("\nLOGODECRYPT PAYLOADS:")
            print(json.dumps(diag["decryption_payload"], indent=2))
    else:
        run_master_demo()