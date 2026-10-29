#!/usr/bin/env python3
"""
Invasive Metadata Cleaner & Deep Purge Suite
Aggressively strips zero-width characters, tracking watermarks, PII, system paths, and API keys.
"""
import re
from typing import Dict, Any

class InvasiveMetadataCleaner:
    ZERO_WIDTH_CHARS = [
        '\u200b', '\u200c', '\u200d', '\ufeff', '\u2060', 
        '\u200e', '\u200f', '\u202a', '\u202b', '\u202c', '\u202d', '\u202e'
    ]

    def __init__(self):
        self.re_api_key = re.compile(r'\b(?:sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36}|AIza[0-9A-Za-z-_]{35})\b')
        self.re_ipv4 = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
        self.re_email = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        self.re_phone = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
        self.re_iso_timestamp = re.compile(r'\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b')

    def clean_text(self, text: str, aggressive: bool = True) -> str:
        cleaned = text
        for char in self.ZERO_WIDTH_CHARS:
            cleaned = cleaned.replace(char, '')

        cleaned = self.re_api_key.sub('[SCRUBBED_API_KEY]', cleaned)
        cleaned = self.re_ipv4.sub('[SCRUBBED_IP]', cleaned)
        cleaned = self.re_email.sub('[SCRUBBED_EMAIL]', cleaned)
        cleaned = self.re_phone.sub('[SCRUBBED_PHONE]', cleaned)
        cleaned = self.re_iso_timestamp.sub('[SCRUBBED_TIMESTAMP]', cleaned)

        if aggressive:
            geo_pattern = r'\b(Fargo|North Dakota|Minneapolis|California|London|New York|ND|MN|CA|NY)\b'
            cleaned = re.sub(geo_pattern, '[SCRUBBED_GEO]', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        return cleaned.strip()
