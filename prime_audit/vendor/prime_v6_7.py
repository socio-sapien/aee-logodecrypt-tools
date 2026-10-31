#!/usr/bin/env python3
"""AEE × LOGODECRYPT PRIME 6.7 — bounded, evidence-aware review prototype.

Python 3.10+, standard library only. Retains v6.3's bounded lexical, arithmetic, cultural,
sensory-metadata, and performance lenses; adds a finite terminology-record audit with exact
set-distance arithmetic and optional bounded JSON profiles. No etymology, semantic identity,
truth, device capture, or production security claim is inferred.
"""
from __future__ import annotations

import argparse
import collections
from dataclasses import dataclass
from typing import Literal
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import hashlib
import json
import math
import pathlib
import re
import sys
import time
from typing import Any, Optional

VERSION = "6.7.0"
MAX_TEXT_BYTES = 262_144
MAX_CONTEXT_BYTES = 262_144
MAX_DOMAIN_CONFIG_BYTES = 65_536
MAX_REPORT_BYTES = 16_777_216
MAX_SENSORY_METADATA_BYTES = 65_536
MAX_TERM_CATALOG_BYTES = 65_536
MAX_DICHOTOMY_PROFILE_BYTES = 65_536

STRUCT = [
    "equals", "plus", "minus", "times", "divided", "sum", "total", "result",
    "therefore", "verified", "measured", "computed", "block", "hash", "signature",
    "audit", "error", "fixed", "record", "line", "index", "formula", "matrix",
    "vector", "proof", "theorem", "derive", "derivation", "node", "transaction",
    "ledger", "math", "protocol", "code", "public", "matches", "first", "second",
    "third", "finally", "however", "specifically", "namely", "for example",
    "for instance", "in conclusion", "in summary", "in other words", "that is",
]
EVAS = [
    "potentially", "possibly", "reportedly", "apparently", "arguably", "essentially",
    "basically", "actually", "literally", "really", "somewhat", "sort of", "kind of",
    "maybe", "perhaps", "allegedly", "more or less", "roughly speaking", "to some extent",
    "to some degree", "it is important to note", "it is worth noting", "could be argued",
    "going forward", "moving forward", "holistic", "synergies", "leverage", "meaningful",
    "diverse", "various", "faceted", "evolving", "landscape", "exploring", "committed",
    "stakeholders", "engagement", "fosters", "remains", "suggests", "implies", "generally",
    "typically", "likely", "still under development", "i apologize for",
    "i understand your frustration", "i appreciate your patience", "as an ai", "i'm afraid",
    "please note that", "at this time", "to the best of my knowledge",
    "i want to be transparent", "keep in mind", "as of my last update",
    "it's important to note",
]

# Rule dictionaries are illustrative, versioned starter vocabularies. Every hit
# is a surface match and keeps its original character offsets.
DOMAIN_PATTERNS: dict[str, dict[str, str]] = {
    "crypto": {
        "actor": r"(?i:\b(?:we|our|issuer|foundation|agency|regulator|company|protocol team|project team|SEC|CFTC)\b)",
        "action": r"(?i:\b(?:filed|approved|proposed|launched|launch|deployed|deploy|paused|listed|delisted|acquired|acquire|settled|settle|will issue|plans to issue)\b)",
        "asset": r"(?i:\b(?:BTC|ETH|SOL|USDC|USDT|XRP|DOGE|ADA|AVAX|LINK|DOT|MATIC)\b)|\b[A-Z]{2,10}\b",
        "chain": r"(?i:\b(?:Ethereum|Bitcoin|Solana|Base|Arbitrum|Optimism|Polygon|Avalanche|BNB Chain)\b)",
        "amount": r"(?i:\b\d[\d,.]*(?:\s?(?:%|USD|USDT|USDC|BTC|ETH|tokens?))?(?=\s|$|[.,;:]))",
        "timing": r"(?i:\b(?:Q[1-4](?:\s?\d{4})?|\d{4}-\d{2}-\d{2}|today|tomorrow|next week|within \d+ days?)\b)",
        "modality": r"(?i:\b(?:will|shall|plan(?:s|ned)?|intend(?:s|ed)?|aim(?:s|ed)?|may|might|could|expects?)\b)",
        "condition": r"(?i:\b(?:if|unless|pending|subject to|following|provided that|contingent on)\b)",
        "approval": r"(?i:\b(?:approved|approval|authorized|authorization|rejected|denied|pending approval)\b)",
        "contract_address": r"\b0x[a-fA-F0-9]{40}\b",
    },
    "agent_trace": {
        "source": r"(?i:\b(?:source|according to|retrieved from|tool output|recorded in)\b)",
        "claim": r"(?i:\b(?:claims?|reports?|states?|shows?|indicates?|confirms?)\b)",
        "value": r"(?i:\b\d[\d,.]*(?:\s?(?:%|USD|USDT|USDC|BTC|ETH|tokens?))?\b)",
        "unit": r"(?i:\b(?:percent|percentage|USD|USDT|USDC|BTC|ETH|tokens?|seconds?|minutes?|hours?|days?)\b)",
        "actor": r"(?i:\b(?:agent|assistant|tool|user|system|worker|model)\b)",
        "action": r"(?i:\b(?:called|returned|read|wrote|sent|submitted|failed|completed|retried|cancelled)\b)",
        "object": r"(?i:\b(?:file|message|record|account|order|transaction|event|response|result)\b)",
        "time": r"(?i:\b(?:\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?Z?)?|\d{1,2}:\d{2}(?:\s?[AP]M)?)\b)",
        "polarity": r"(?i:\b(?:not|never|no|without|failed|succeeded|approved|denied)\b)",
        "modality": r"(?i:\b(?:will|must|may|might|should|claimed|reported|attempted)\b)",
        "status": r"(?i:\b(?:success|succeeded|failed|pending|unknown|cancelled|complete|completed)\b)",
    },
    "legal_procurement": {
        "party": r"(?i:\b(?:buyer|seller|provider|vendor|agency|contractor|company|customer|supplier)\b)",
        "obligation": r"(?i:\b(?:must|shall|required to|agrees to|is responsible for|undertakes to)\b)",
        "condition": r"(?i:\b(?:if|unless|subject to|provided that|contingent on)\b)",
        "deadline": r"(?i:\b(?:within \d+ days?|by \w+ \d{1,2},? \d{4}|\d{4}-\d{2}-\d{2})\b)",
        "deliverable": r"(?i:\b(?:deliver|provide|submit|produce|complete|report|payment|notice)\b)",
        "status": r"(?i:\b(?:proposed|approved|executed|effective|terminated|pending|renewed|expired)\b)",
        "exception": r"(?i:\b(?:except|excluding|unless|subject to|other than)\b)",
    },

    "systemic_root": {
        "cascading_dependency": r"\b(?:delegatecall|upgradeTo|implementation|proxy)\b",
        "liquidity_lock": r"\b(?:staked|locked|liquidity|collateral|vault)\b",
        "oracle_influence": r"\b(?:latestRoundData|getPrice|oracle|feed|deviation)\b",
        "governance_override": r"\b(?:propose|execute|timelock|multisig|emergencyAction)\b",
        "cross_chain_vector": r"\b(?:bridge|sendMessage|crossChain|gateway|relayer)\b",
    },
}
DEFAULT_FRAMES = {
    "crypto": ["actor", "action", "asset", "chain", "amount", "timing", "modality", "condition", "approval", "contract_address"],
    "agent_trace": ["source", "claim", "value", "unit", "actor", "action", "object", "time", "polarity", "modality", "status"],
    "legal_procurement": ["party", "obligation", "condition", "deadline", "deliverable", "status", "exception"],
    "systemic_root": ["cascading_dependency", "liquidity_lock", "oracle_influence", "governance_override", "cross_chain_vector"],
}

ATTENTION_MARKERS = ["unprecedented", "first-ever", "record-breaking", "urgent", "breaking"]
INTENTION_PATTERNS = {
    "plan_or_intend": r"(?i:\b(?:plan|plans|planned|planning|intend|intends|intended|aim|aims|aimed)\b)",
    "commitment_or_modality": r"(?i:\b(?:will|shall|must|commits? to|expects? to)\b)",
    "condition_or_contingency": r"(?i:\b(?:if|unless|pending|subject to|contingent on|provided that)\b)",
}
RHETORIC_PATTERNS = {
    "contrast": r"(?i:\b(?:but|however|yet|whereas|although|rather than|on the other hand)\b)",
    "repetition_marker": r"(?i:\b(?:again|repeatedly|always|never)\b)",
}
EMBELLISHMENT = ["revolutionary", "unprecedented", "guaranteed", "massive", "absolute", "unquestionable", "breakthrough", "world-leading", "best-in-class", "transformative"]
POLARITY_PAIRS = [("approved", "denied"), ("accepted", "rejected"), ("passed", "failed"), ("opened", "closed"), ("increased", "decreased"), ("above", "below"), ("public", "private"), ("retain", "delete"), ("valid", "invalid")]
STOP_WORDS = set("a an the and or but if of to in on for from with by is are was were be been being it this that as at we our they their you your".split())


CULTURAL_APERTURES = {
    "anglo_corporate": ["circle back", "touch base", "alignment", "synergy", "moving forward", "robust framework", "best-in-class", "market-leading", "paradigms", "holistic"],
    "euro_regulatory": ["compliance vector", "proportionality principle", "harmonized standard", "adequacy determination", "framework alignment", "transitional provisions"],
    "transactional_web3": ["decentralized ethos", "community-driven", "paradigm shift", "game-changing", "next-generation", "ecosystem growth", "value accrual", "vetted protocol"],
}
# Candidate mappings preserve source text and are never silently substituted.
LIGATURE_MAP = {
    "circle back": "postpone", "touch base": "consult", "compliance vector": "rule",
    "harmonized standard": "formula", "decentralized ethos": "unregulated", "vetted protocol": "verified_code",
    "synergy": "plus", "alignment": "equals",
}
CULTURAL_CHOICES = ["none", *sorted(CULTURAL_APERTURES)]
EMOTION_LEXICONS = {
    "pain_distress": ["hurt", "pain", "grief", "sad", "sorrow", "anger", "angry", "fear", "afraid", "anxiety", "anxious", "shame", "betrayed"],
    "pleasure_joy": ["joy", "joyful", "pleasure", "enjoy", "delight", "happy", "happiness", "comfort", "gratitude", "relief"],
    "trust_connection": ["trust", "love", "care", "belonging", "connection", "safe", "safety"],
}
THOUGHT_FEATURES = ["numeric_fact", "reported_affect", "survival", "pleasure", "deception_cue", "intention_cue", "rhetoric_cue", "embellishment_cue"]

# Configured lexical observables: these are not jurisdiction-specific legal analysis
# and are not claims about actual cognition, meaning, intent, or emotional state.
LAW_CUES = ["law", "laws", "legal", "legislation", "statute", "statutory", "regulation", "regulations", "regulatory", "jurisdiction"]
RULE_CUES = ["rule", "rules", "policy", "policies", "procedure", "procedures", "requirement", "requirements", "standard", "standards", "protocol"]
AWARENESS_CUES = {
    "meaning": ["meaning", "definition", "signify", "interpret", "interpretation"],
    "purpose": ["purpose", "aim", "goal", "intent", "intention", "objective"],
    "thought": ["think", "thinks", "thought", "consider", "reason", "believe", "belief"],
    "emotion": sorted({word for words in EMOTION_LEXICONS.values() for word in words}),
}
MEANING_POLARITY_PAIRS = [("explicit", "implicit"), ("clear", "ambiguous"), ("literal", "figurative")]
PURPOSE_POLARITY_PAIRS = [("support", "oppose"), ("enable", "prevent"), ("preserve", "remove"), ("planned", "unplanned")]
PROFUNDITY_CUES = ["deep", "depth", "profound", "profundity", "layered", "underlying", "foundational", "nuanced", "complex", "recursive"]
PERCEPTION_CUES = ["perceive", "perception", "observe", "observation", "sense", "sensory", "detect", "notice", "discern", "awareness"]
OPTICAL_LEXICON = ["vision", "visual", "optic", "optical", "light", "lens", "focus", "focal", "aperture", "iris", "pupil", "retina", "acuity", "resolution", "pixel", "wavelength", "color", "contrast", "brightness", "exposure"]
AUDITORY_LEXICON = ["auditory", "audio", "sound", "hearing", "hear", "ear", "acoustic", "frequency", "pitch", "amplitude", "waveform", "sample", "hertz", "decibel", "noise", "signal", "stereo", "channel", "microphone", "echo"]



# Terminology profiles are finite, source-preserving records. Etymology fields
# are caller assertions unless sources are supplied; citations are not fetched.
TermRegister = Literal["definition", "axiom", "observation", "ligature"]
REGISTER_VALUES = {"definition", "axiom", "observation", "ligature"}
VOCAB_MARKERS = ("STRUCT", "EVAS", "DOMAIN_PATTERNS", "LIGATURE_MAP", "CULTURAL_APERTURES")

@dataclass(frozen=True)
class Etymology:
    root: str = "unknown"
    language: str = "unspecified"
    attested_from: str = "not supplied"
    sense_shift: tuple[tuple[str, str, str], ...] = ()
    sources: tuple[str, ...] = ()

@dataclass(frozen=True)
class Term:
    register: TermRegister
    name: str
    etymology: Etymology
    denotation: tuple[str, ...]
    connotation: str
    antonym: str = "none"


def _default_term_catalog() -> dict[str, Any]:
    # This is a bounded sample based on the user's supplied table. Historical
    # etymology fields are retained as unverified user-provided claims.
    return {
        "definitions": ["normalize", "_word_tokens", "_sentence_spans", "_equations_in",
                        "_exact_fraction", "_hash", "_canonical"],
        "terms": [
            {"register": "definition", "name": "tokenization",
             "etymology": {"root": "tācno-", "language": "Old English", "attested_from": "c. 1300",
                           "sense_shift": [["sign", "token", "16c"], ["token", "computational unit", "20c"]]},
             "denotation": ["_word_tokens"],
             "connotation": "stipulates the regex [A-Za-z0-9]+(?:'[A-Za-z0-9]+)? as the word class",
             "antonym": "subtokenization"},
            {"register": "observation", "name": "measurement",
             "etymology": {"root": "mētiri", "language": "Latin", "attested_from": "c. 1250",
                           "sense_shift": [["to measure", "act of measuring", "14c"], ["act", "quantified observation", "17c"]]},
             "denotation": ["normalize", "_word_tokens"],
             "connotation": "a quantity obtained under named normalization and tokenization definitions",
             "antonym": "stipulation"},
            {"register": "definition", "name": "definition",
             "etymology": {"root": "dēfīnīre", "language": "Latin", "attested_from": "c. 1380",
                           "sense_shift": [["to bound", "to determine", "14c"], ["to determine", "to stipulate a term", "16c"]]},
             "denotation": ["normalize", "_canonical"],
             "connotation": "a bounded stipulation of what a term means within a build",
             "antonym": "description"},
            {"register": "observation", "name": "description",
             "etymology": {"root": "dēscrībere", "language": "Latin", "attested_from": "c. 1300",
                           "sense_shift": [["to write down", "to represent", "14c"], ["to represent", "to report a measured value", "17c"]]},
             "denotation": ["_hash", "_canonical"],
             "connotation": "a reported value contingent on cited definitions and any vocabularies",
             "antonym": "definition"},
        ],
    }


def _term_catalog_objects(value: Any) -> tuple[frozenset[str], dict[str, Term]]:
    if not isinstance(value, dict) or set(value) != {"definitions", "terms"}:
        raise ValueError("term catalog JSON must contain exactly 'definitions' and 'terms'")
    definitions, rows = value["definitions"], value["terms"]
    if not isinstance(definitions, list) or len(definitions) > 256:
        raise ValueError("term catalog definitions must be a list with at most 256 identifiers")
    id_pattern = r"[A-Za-z_][A-Za-z0-9_.:-]{0,63}"
    if any(not isinstance(x, str) or not re.fullmatch(id_pattern, x) for x in definitions):
        raise ValueError("definition identifiers must be bounded names, not executable content")
    if len(set(definitions)) != len(definitions):
        raise ValueError("term catalog definition identifiers must be unique")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 64:
        raise ValueError("term catalog must contain 1-64 term records")
    terms: dict[str, Term] = {}
    for row in rows:
        required = {"register", "name", "etymology", "denotation", "connotation", "antonym"}
        if not isinstance(row, dict) or set(row) != required:
            raise ValueError("each term needs exactly register, name, etymology, denotation, connotation, and antonym")
        register, name = row["register"], row["name"]
        if not isinstance(register, str) or register not in REGISTER_VALUES:
            raise ValueError(f"unsupported term register: {register!r}")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name):
            raise ValueError("term names must be 1-64 lowercase letters, digits, or underscores; start with a letter")
        if name in terms:
            raise ValueError(f"duplicate term name: {name}")
        et = row["etymology"]
        if not isinstance(et, dict) or not set(et).issubset({"root", "language", "attested_from", "sense_shift", "sources"}):
            raise ValueError(f"term {name!r} has invalid etymology fields")
        et_values = {key: et.get(key, default) for key, default in
                     (("root", "unknown"), ("language", "unspecified"), ("attested_from", "not supplied"))}
        if any(not isinstance(v, str) or len(v) > 256 for v in et_values.values()):
            raise ValueError(f"term {name!r} etymology strings must be at most 256 characters")
        shifts = et.get("sense_shift", [])
        if not isinstance(shifts, list) or len(shifts) > 16 or any(
            not isinstance(x, list) or len(x) != 3 or any(not isinstance(part, str) or len(part) > 160 for part in x)
            for x in shifts
        ):
            raise ValueError(f"term {name!r} sense_shift must be at most 16 triples of short strings")
        sources = et.get("sources", [])
        if not isinstance(sources, list) or len(sources) > 8 or any(not isinstance(x, str) or not x.strip() or len(x) > 512 for x in sources):
            raise ValueError(f"term {name!r} sources must be at most 8 nonempty strings of at most 512 characters")
        denotation = row["denotation"]
        if not isinstance(denotation, list) or len(denotation) > 16 or any(
            not isinstance(x, str) or not re.fullmatch(id_pattern, x) for x in denotation
        ):
            raise ValueError(f"term {name!r} denotation must be a list of at most 16 bounded identifiers")
        connotation, antonym = row["connotation"], row["antonym"]
        if not isinstance(connotation, str) or len(connotation) > 1000:
            raise ValueError(f"term {name!r} connotation must be text of at most 1,000 characters")
        if not isinstance(antonym, str) or not (antonym == "none" or re.fullmatch(r"[a-z][a-z0-9_]{0,63}", antonym)):
            raise ValueError(f"term {name!r} antonym must be 'none' or a bounded term name")
        terms[name] = Term(register, name,
                           Etymology(**et_values, sense_shift=tuple(tuple(x) for x in shifts), sources=tuple(sources)),
                           tuple(denotation), connotation, antonym)
    return frozenset(definitions), terms


def _load_term_catalog(path: str) -> tuple[dict[str, Any], bytes]:
    text, raw = _read_bounded_file(path, MAX_TERM_CATALOG_BYTES, "term catalog JSON")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"cannot parse term catalog JSON: {exc}") from exc
    _term_catalog_objects(data)
    return data, raw


def _submitted_isomorphy_predicate(term: Term) -> dict[str, Any]:
    """Reproduce the supplied literal predicate as a diagnostic, not semantic validation."""
    missing_literal_mentions = [cite for cite in term.denotation if cite not in term.connotation]
    marker_hits = [marker for marker in VOCAB_MARKERS if marker.casefold() in term.connotation.casefold()]
    passed = bool(term.connotation) and not missing_literal_mentions and not marker_hits
    return {"pass": passed, "denotation_ids_not_literally_named_in_connotation": missing_literal_mentions,
            "configured_vocabulary_markers_in_connotation": marker_hits,
            "interpretation": "literal string predicate only; failure does not imply semantic inconsistency"}


def _term_catalog_lens(profile: Optional[dict[str, Any]] = None,
                       profile_bytes: Optional[bytes] = None) -> dict[str, Any]:
    selected = profile if profile is not None else _default_term_catalog()
    definitions, terms = _term_catalog_objects(selected)
    rows = []
    for name, term in terms.items():
        resolved = sorted(set(term.denotation) & definitions)
        unresolved = sorted(set(term.denotation) - definitions)
        dep = min(len(resolved), 3)
        if term.etymology.root.casefold() == "unknown":
            dep = min(dep, 1)
        if term.antonym == "none":
            separation = None
            pair_status = "no contrast specified"
        elif term.antonym not in terms:
            separation = None
            pair_status = "antonym label has no matching term record"
        else:
            left, right = set(term.denotation), set(terms[term.antonym].denotation)
            union = left | right
            if not union:
                separation = None
                pair_status = "empty denotation sets; separation undefined"
            else:
                separation = Fraction(1) - Fraction(len(left & right), len(union))
                pair_status = "computed from declared reference sets only"
        original_predicate = _submitted_isomorphy_predicate(term)
        rows.append({
            "name": name, "register": term.register,
            "etymology": {"root": term.etymology.root, "language": term.etymology.language,
                           "attested_from": term.etymology.attested_from,
                           "sense_shift": [list(x) for x in term.etymology.sense_shift],
                           "source_references": list(term.etymology.sources),
                           "source_status": ("reference supplied; not independently checked" if term.etymology.sources
                                             else "user-supplied claim; no source reference supplied")},
            "denotation": list(term.denotation),
            "denotation_reference_check": {"resolved": resolved, "unresolved": unresolved,
                                             "resolved_count": len(resolved),
                                             "coverage_fraction": (str(Fraction(len(resolved), len(set(term.denotation))))
                                                                   if term.denotation else None)},
            "dependability_index": {"value": dep, "formula": "min(resolved unique definition bases, 3); if root == 'unknown', cap at 1",
                                    "interpretation": "reference-count heuristic only; not empirical reliability or truth"},
            "antonym_denotation_separation": {"antonym": term.antonym,
                                               "exact_fraction": str(separation) if separation is not None else None,
                                               "formula": "1 - |A∩B|/|A∪B| (Jaccard distance)",
                                               "status": pair_status,
                                               "interpretation": "lexical-reference set separation, not antonym quality or reliability"},
            "connotation": term.connotation,
            "submitted_isomorphy_predicate": original_predicate,
            "record_consistency": {"connotation_nonempty": bool(term.connotation),
                                   "all_denotation_refs_resolve": not unresolved,
                                   "vocabulary_marker_hits": original_predicate["configured_vocabulary_markers_in_connotation"],
                                   "interpretation": "finite field/reference checks; not a semantic proof"},
        })
    raw = profile_bytes if profile_bytes is not None else _canonical(selected)
    return {"profile_sha256": _hash(raw), "definitions": sorted(definitions), "term_count": len(rows),
            "records": rows,
            "scope": "finite caller-declared terminology records; source text and claims are not rewritten",
            "etymology_policy": "source references are reported as supplied and never treated as verified by this tool",
            "formula_review": {
                "dependability": "counts resolvable reference labels, capped at 3; it is not a calibrated dependability probability",
                "proposed_reliability": "1 minus Jaccard similarity is Jaccard distance; report it as denotation-set separation, not reliability",
                "isomorphy": "the supplied string rule is exposed as a mechanical diagnostic; it cannot establish semantic identity",
            }}


# Finite permutation / reference-fidelity dichotomy. All outputs are properties
# of caller-supplied finite encodings, not psychological depth or human sensing.
def _permutation_sign(permutation: list[int]) -> int:
    inversions = sum(1 for i in range(len(permutation)) for j in range(i + 1, len(permutation))
                     if permutation[i] > permutation[j])
    return -1 if inversions % 2 else 1


def _permutation_cycles(permutation: list[int]) -> list[list[int]]:
    seen = [False] * len(permutation)
    cycles: list[list[int]] = []
    for start in range(len(permutation)):
        if seen[start]:
            continue
        cycle = []
        index = start
        while not seen[index]:
            seen[index] = True
            cycle.append(index)
            index = permutation[index]
        cycles.append(cycle)
    return cycles


def _validate_dichotomy_profile(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"ground_set", "permutation", "perception"}:
        raise ValueError("dichotomy profile must contain exactly ground_set, permutation, and perception")
    ground, permutation, perception = value["ground_set"], value["permutation"], value["perception"]
    if not isinstance(ground, list) or len(ground) > 12 or any(
        not isinstance(label, str) or not label.strip() or len(label) > 64 for label in ground
    ):
        raise ValueError("ground_set must contain at most 12 nonempty labels of at most 64 characters")
    if len(set(ground)) != len(ground):
        raise ValueError("ground_set labels must be unique")
    if not isinstance(permutation, list) or len(permutation) != len(ground) or any(
        type(index) is not int for index in permutation
    ) or sorted(permutation) != list(range(len(ground))):
        raise ValueError("permutation must be a bijection over zero-based indices of ground_set")
    if not isinstance(perception, dict):
        raise ValueError("perception must be an object")
    required = {"modality", "received", "reference_count", "matched_count"}
    optional = {"reference_values"}
    if not required.issubset(perception) or set(perception) - required - optional:
        raise ValueError("perception requires modality, received, reference_count, matched_count, and optional reference_values")
    modality = perception["modality"]
    if not isinstance(modality, str) or modality not in {"optical", "auditory"}:
        raise ValueError("perception modality must be optical or auditory")
    received = perception["received"]
    if not isinstance(received, list) or len(received) > 4096:
        raise ValueError("received must be a list of at most 4096 JSON scalar values")
    def scalar(item: Any) -> bool:
        return item is None or isinstance(item, (str, bool, int, float)) and (not isinstance(item, float) or math.isfinite(item))
    if any(not scalar(item) for item in received):
        raise ValueError("received and reference values must be finite JSON scalars")
    ref_count, matched_count = perception["reference_count"], perception["matched_count"]
    if type(ref_count) is not int or not 0 <= ref_count <= 4096:
        raise ValueError("reference_count must be an integer from 0 to 4096")
    if type(matched_count) is not int or not 0 <= matched_count <= ref_count:
        raise ValueError("matched_count must be an integer between 0 and reference_count")
    if len(received) != ref_count:
        raise ValueError("received list length must equal reference_count")
    reference_values = perception.get("reference_values")
    evidence_basis = "caller-reported matched_count; no reference values supplied for verification"
    if reference_values is not None:
        if not isinstance(reference_values, list) or len(reference_values) != ref_count or any(not scalar(item) for item in reference_values):
            raise ValueError("reference_values must be finite JSON scalars with length equal to reference_count")
        positional_matches = sum(_canonical(a) == _canonical(b) for a, b in zip(received, reference_values))
        if positional_matches != matched_count:
            raise ValueError("matched_count conflicts with exact positional comparison to reference_values")
        evidence_basis = "matched_count verified by exact positional JSON-scalar equality against supplied reference_values"
    clean_perception = {"modality": modality, "received": received,
                        "reference_count": ref_count, "matched_count": matched_count}
    if reference_values is not None:
        clean_perception["reference_values"] = reference_values
    return {"ground_set": ground, "permutation": permutation, "perception": clean_perception,
            "_perception_evidence_basis": evidence_basis}


def _load_dichotomy_profile(path: str) -> tuple[dict[str, Any], bytes]:
    raw_text, raw = _read_bounded_file(path, MAX_DICHOTOMY_PROFILE_BYTES, "dichotomy profile JSON")
    try:
        value = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"cannot parse dichotomy profile JSON: {exc}") from exc
    _validate_dichotomy_profile(value)
    return value, raw


def _profundity_perception_lens(profile: Optional[dict[str, Any]] = None,
                                profile_bytes: Optional[bytes] = None) -> dict[str, Any]:
    if profile is None:
        return {"configured": False,
                "scope": "finite permutation and reference-fidelity calculations; no profile supplied",
                "interpretation": "no depth, perception, or sensory capability is inferred"}
    checked = _validate_dichotomy_profile(profile)
    ground = checked["ground_set"]
    permutation = checked["permutation"]
    cycles = _permutation_cycles(permutation)
    fixed = [i for i, target in enumerate(permutation) if i == target]
    n = len(ground)
    cycle_order = math.lcm(*(len(cycle) for cycle in cycles)) if cycles else 1
    p = checked["perception"]
    ref_count, matched_count = p["reference_count"], p["matched_count"]
    fidelity = Fraction(matched_count, ref_count) if ref_count else None
    admissibility_failures = []
    if n < 2:
        admissibility_failures.append("permutation proxy requires at least two named ground-set elements")
    if ref_count == 0:
        admissibility_failures.append("perception fidelity reference must contain at least one sample")
    raw_profile = profile_bytes if profile_bytes is not None else _canonical({
        "ground_set": ground, "permutation": permutation, "perception": p})
    return {
        "configured": True,
        "profile_sha256": _hash(raw_profile),
        "dichotomy": "user-stipulated finite permutation proxy : reference-qualified perception",
        "profundity_proxy": {
            "ground_set": ground, "ground_set_size": n,
            "permutation_zero_based": permutation,
            "symmetric_group_space_size_factorial": math.factorial(n),
            "permutation_sign": _permutation_sign(permutation) if n else 1,
            "cycles_zero_based": cycles,
            "cycles_by_label": [[ground[i] for i in cycle] for cycle in cycles],
            "cycle_count_orbits": len(cycles),
            "fixed_point_indices": fixed,
            "fixed_point_labels": [ground[i] for i in fixed],
            "permutation_order_lcm_cycle_lengths": cycle_order,
            "movement_density_exact": str(Fraction(n - len(fixed), n)) if n else None,
            "arithmetic_exact": True,
            "interpretation": "finite permutation invariants for the declared encoding; not a measure of psychological or semantic profundity",
        },
        "perception_proxy": {
            "modality": p["modality"], "received_sample_count": len(p["received"]),
            "reference_sample_count": ref_count, "matched_sample_count": matched_count,
            "fidelity_exact": str(fidelity) if fidelity is not None else None,
            "evidence_basis": checked["_perception_evidence_basis"],
            "arithmetic_exact": True,
            "interpretation": "sample-count match ratio only; it is not human vision/hearing, sensor calibration, or perception quality",
        },
        "admissible_under_declared_checks": not admissibility_failures,
        "admissibility_failures": admissibility_failures,
        "formula_notes": {
            "permutation_sign": "(-1)^inversions",
            "space_size": "n! for the declared finite ground-set size n",
            "movement_density": "(n - fixed_points)/n; undefined when n=0",
            "perception_fidelity": "matched samples/reference samples; exact Fraction; undefined for zero reference samples",
        },
    }


# Optional per-token dynamics ledger. These are mechanical surface observations;
# no etymology, grammatical role, intention, or semantic purpose is inferred.
WORD_DYNAMICS_MAX_TOKENS = 128
WORD_DYNAMICS_MODULUS = 1_000_000_007
WORD_DYNAMIC_SLOTS = (
    "surface", "casefold_surface", "start", "end", "token_index",
    "sentence_index", "position", "letter_sum", "letter_product_mod",
    "letter_position_signature_mod", "vowel_count", "consonant_count",
    "vowel_consonant_ratio_exact", "letter_frequency", "polarity_pair",
    "polarity_side", "polarity_balance_exact", "pleasure_cue", "survival_cue",
    "pleasure_survival_balance_exact",
)
WORD_ANTONYM_PAIRS = (
    ("approved", "denied"), ("accept", "reject"), ("pass", "fail"),
    ("open", "close"), ("increase", "decrease"), ("above", "below"),
    ("public", "private"), ("retain", "delete"), ("valid", "invalid"),
    ("safe", "danger"), ("protect", "threaten"), ("pleasure", "pain"),
    ("survival", "death"), ("trust", "betray"), ("know", "believe"),
    ("fact", "feel"), ("definition", "description"), ("same", "different"),
)
WORD_PLEASURE_CUES = frozenset({
    "joy", "pleasure", "enjoy", "delight", "happy", "comfort",
    "gratitude", "relief", "reward", "satisfy",
})
WORD_SURVIVAL_CUES = frozenset({
    "survive", "safe", "safety", "danger", "threat", "risk", "protect",
    "protection", "loss", "hurt", "pain", "death",
})
WORD_POLARITY_INDEX: dict[str, tuple[tuple[str, str], str]] = {}
for _left, _right in WORD_ANTONYM_PAIRS:
    WORD_POLARITY_INDEX[_left] = ((_left, _right), "left")
    WORD_POLARITY_INDEX[_right] = ((_left, _right), "right")


def _word_dynamics_lens(text: str) -> dict[str, Any]:
    """Build a bounded per-token ledger and an explicit finite slot permutation."""
    matches = list(re.finditer(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text))
    if len(matches) > WORD_DYNAMICS_MAX_TOKENS:
        raise ValueError(f"word-dynamics accepts at most {WORD_DYNAMICS_MAX_TOKENS} word tokens")
    sentence_rows = _sentence_spans(text)
    rows: list[dict[str, Any]] = []
    sentence_cursor = 0
    for token_index, match in enumerate(matches):
        surface = match.group(0)
        word = surface.casefold()
        while sentence_cursor + 1 < len(sentence_rows) and match.start() >= sentence_rows[sentence_cursor][2]:
            sentence_cursor += 1
        sentence_index = sentence_cursor + 1 if sentence_rows and sentence_rows[sentence_cursor][1] <= match.start() < sentence_rows[sentence_cursor][2] else None
        if len(matches) == 1:
            position = "only"
        elif token_index == 0:
            position = "first"
        elif token_index == len(matches) - 1:
            position = "last"
        else:
            position = "interior"
        letters = [char for char in word if "a" <= char <= "z"]
        codes = [ord(char) for char in letters]
        letter_sum = sum(codes)
        product = 1
        for code in codes:
            product = (product * code) % WORD_DYNAMICS_MODULUS
        if not codes:
            product = 0
        position_signature = sum(code * (i + 1) for i, code in enumerate(codes)) % WORD_DYNAMICS_MODULUS
        vowels = sum(char in "aeiouy" for char in letters)
        consonants = len(letters) - vowels
        ratio = Fraction(vowels, consonants) if consonants else (Fraction(vowels) if vowels else Fraction(0))
        frequency = dict(sorted(collections.Counter(letters).items()))
        polarity = WORD_POLARITY_INDEX.get(word)
        pair, side = polarity if polarity else (None, None)
        balance = ("-1" if side == "left" else "1") if side else None
        pleasure = word in WORD_PLEASURE_CUES
        survival = word in WORD_SURVIVAL_CUES
        motivation_balance = Fraction(int(pleasure), int(pleasure) + int(survival)) if pleasure or survival else None
        row = {
            "surface": surface,
            "casefold_surface": word,
            "start": match.start(),
            "end": match.end(),
            "token_index": token_index,
            "sentence_index": sentence_index,
            "position": position,
            "letter_sum": letter_sum,
            "letter_product_mod": product,
            "letter_position_signature_mod": position_signature,
            "vowel_count": vowels,
            "consonant_count": consonants,
            "vowel_consonant_ratio_exact": str(ratio),
            "letter_frequency": frequency,
            "polarity_pair": list(pair) if pair else None,
            "polarity_side": side,
            "polarity_balance_exact": balance,
            "pleasure_cue": pleasure,
            "survival_cue": survival,
            "pleasure_survival_balance_exact": str(motivation_balance) if motivation_balance is not None else None,
        }
        row["record_sha256"] = _hash(_canonical(row))
        rows.append(row)

    slot_count = len(rows) * len(WORD_DYNAMIC_SLOTS)
    permutation = list(range(slot_count))
    slot_index = {name: index for index, name in enumerate(WORD_DYNAMIC_SLOTS)}
    width = len(WORD_DYNAMIC_SLOTS)
    for word_index in range(len(rows)):
        base = word_index * width
        for field_index in range(width):
            permutation[base + field_index] = base + ((field_index + 1) % width)

    # Link only the first explicitly matched left/right surface cue for each pair.
    # Swapping their outgoing edges preserves bijectivity and joins those cycles.
    by_pair: dict[tuple[str, str], dict[str, list[int]]] = {}
    for index, row in enumerate(rows):
        if row["polarity_pair"] is not None:
            pair_key = tuple(row["polarity_pair"])
            by_pair.setdefault(pair_key, {"left": [], "right": []})[row["polarity_side"]].append(index)
    links = []
    for pair_key, sides in sorted(by_pair.items()):
        if sides["left"] and sides["right"]:
            left_word, right_word = sides["left"][0], sides["right"][0]
            left_slot = left_word * width + slot_index["polarity_pair"]
            right_slot = right_word * width + slot_index["polarity_pair"]
            permutation[left_slot], permutation[right_slot] = permutation[right_slot], permutation[left_slot]
            links.append({"pair": list(pair_key), "left_token_index": left_word,
                          "right_token_index": right_word,
                          "link_rule": "swap outgoing edges at the polarity_pair slots"})

    cycles = _permutation_cycles(permutation)
    cycle_lengths = [len(cycle) for cycle in cycles]
    order = math.lcm(*cycle_lengths) if cycle_lengths else 1
    sign = -1 if (slot_count - len(cycles)) % 2 else 1
    sample_mappings = []
    for source in range(min(slot_count, 16)):
        target = permutation[source]
        source_word, source_field = divmod(source, width)
        target_word, target_field = divmod(target, width)
        sample_mappings.append({"from": f"{source_word}:{WORD_DYNAMIC_SLOTS[source_field]}",
                                "to": f"{target_word}:{WORD_DYNAMIC_SLOTS[target_field]}"})
    return {
        "configured": True,
        "word_count": len(rows),
        "word_token_limit": WORD_DYNAMICS_MAX_TOKENS,
        "words": rows,
        "dynamic_slot_order": list(WORD_DYNAMIC_SLOTS),
        "permutation": {
            "slot_count": slot_count,
            "mapping_zero_based": permutation,
            "sign": sign,
            "cycle_count": len(cycles),
            "cycle_lengths": cycle_lengths,
            "order_lcm_cycle_lengths": order,
            "space_size_expression": f"{slot_count}!" if slot_count else "1",
            "cross_polarity_links": links,
            "sample_mappings": sample_mappings,
            "mapping_sha256": _hash(_canonical(permutation)),
            "meaning": "finite index mapping over named per-token fields; values and source text are not rearranged",
        },
        "scope": "ASCII token surface, exact codepoint arithmetic, configured cue matches, and source offsets only",
        "limitations": [
            "casefold_surface is not morphological lemmatization; position is not grammatical function",
            "etymology, connotation, purpose, intent, awareness, and semantic antonymy are not inferred",
            "polarity and motivation labels are configured surface cues, not emotional or factual findings",
            "record hashes and mapping hash are unsigned content-integrity checks, not authorship or attestation",
        ],
    }


# Configured logical-action surface cues. Weights are explicit analyst priorities,
# not empirically calibrated logical force or semantic parsing.
LOGICAL_ACTIONS: dict[str, tuple[str, float]] = {
    "NEGATION": (r"\b(?:not|no|never|none|neither|nor|cannot|can't|won't|without)\b", 1.00),
    "CONDITION": (r"\b(?:if|unless|provided that|subject to|contingent on|only if|in the event)\b", 1.00),
    "MODALITY_COMMIT": (r"\b(?:will|shall|must|commits? to|agrees? to|undertakes? to)\b", 0.95),
    "MODALITY_TENTATIVE": (r"\b(?:may|might|could|expects? to|plans? to|intends? to|aims? to)\b", 0.80),
    "QUANTIFIER": (r"\b(?:\d+-of-\d+|no more than|at least|at most|up to|all|any|each|every|some)\b", 0.90),
    "CONTRAST": (r"\b(?:on the other hand|rather than|but|however|yet|whereas|although|instead)\b", 0.85),
    "CAUSAL": (r"\b(?:as a result|consequently|so that|because|therefore|thus|hence|since)\b", 0.90),
    "SCOPE_LIMIT": (r"\b(?:limited to|insofar as|only|solely|exclusively|except|excluding|other than)\b", 0.90),
    "THRESHOLD": (r"\b(?:basis points|supermajority|threshold|quorum|majority|bps|cap|ceiling|floor)\b", 0.85),
    "TEMPORAL_BOUND": (r"\b(?:for at least|for up to|within|after|before|until|deadline|by|for \d+)\b", 0.75),
    "ASSERTION": (r"\b(?:equals?|is|are|was|were|states?|confirms?|reports?|shows?)\b", 0.60),
    "HEDGE": (r"\b(?:may suggest|possibly|reportedly|apparently|arguably|likely|roughly)\b", 0.55),
}
MAX_LOGICAL_ACTION_HITS = 2048
MAX_LOGICAL_ACTION_WORD_BUDGET = 10000

def _logical_action_lens(text: str, reference_text: Optional[str] = None,
                         target_words: Optional[int] = None) -> dict[str, Any]:
    if target_words is not None and (type(target_words) is not int or not 1 <= target_words <= MAX_LOGICAL_ACTION_WORD_BUDGET):
        raise ValueError(f"logical-action word budget must be an integer from 1 to {MAX_LOGICAL_ACTION_WORD_BUDGET}")
    def scan(value: str) -> tuple[list[dict[str, Any]], dict[str, int], int, collections.Counter]:
        saved: list[dict[str, Any]] = []
        counts: dict[str, int] = {}
        phrase_counts: collections.Counter = collections.Counter()
        total = 0
        per_class_cap = MAX_LOGICAL_ACTION_HITS
        for cue_class, (pattern, weight) in LOGICAL_ACTIONS.items():
            count = 0
            for match in re.finditer(pattern, value, flags=re.IGNORECASE):
                count += 1
                total += 1
                phrase_counts[(cue_class, match.group(0).casefold())] += 1
                if count <= per_class_cap:
                    saved.append({"class": cue_class, "text": match.group(0),
                                  "start": match.start(), "end": match.end(),
                                  "source_slice_matches": value[match.start():match.end()] == match.group(0),
                                  "declared_weight": weight})
            counts[cue_class] = count
        saved.sort(key=lambda row: (row["start"], row["end"], row["class"]))
        return saved[:MAX_LOGICAL_ACTION_HITS], counts, total, phrase_counts

    hits, counts, total, current_inventory = scan(text)
    sentences = _sentence_spans(text)
    sequences: dict[int, dict[str, Any]] = {}
    sentence_cursor = 0
    for hit in hits:
        while sentence_cursor < len(sentences) and hit["start"] >= sentences[sentence_cursor][2]:
            sentence_cursor += 1
        if sentence_cursor >= len(sentences):
            continue
        _sentence, start, end = sentences[sentence_cursor]
        if not start <= hit["start"] < end:
            continue
        row = sequences.setdefault(sentence_cursor + 1, {"sentence_index": sentence_cursor + 1,
            "operator_sequence": [], "operator_count": 0, "declared_weight_sum": 0.0})
        row["operator_sequence"].append(f"{hit['class']}:{hit['text']}")
        row["operator_count"] += 1
        row["declared_weight_sum"] += hit["declared_weight"]
    skeleton = []
    ranked = []
    for row in sequences.values():
        row["declared_weight_sum"] = round(row["declared_weight_sum"], 4)
        row["interpretation"] = "source-order cue sequence; not a parsed logical form"
        skeleton.append(row)
        line = f"S{row['sentence_index']} ops[{row['operator_count']}] " + " > ".join(row["operator_sequence"])
        words = len(_word_tokens(line))
        ranked.append({"kind": "skeleton", "class": "ARGUMENT_SHAPE_PROXY",
            "weight": row["declared_weight_sum"], "words": words,
            "force_per_word": round(row["declared_weight_sum"] / max(words, 1), 6), "line": line})
    for hit in hits:
        line = f"{hit['class']}: {hit['text']!r} @{hit['start']}-{hit['end']}"
        words = len(_word_tokens(line))
        ranked.append({"kind": "operator", "class": hit["class"],
            "weight": round(hit["declared_weight"] / max(words, 1), 6),
            "words": words, "force": hit["declared_weight"], "line": line})
    ranked.sort(key=lambda row: (-(row["weight"] if row["kind"] == "operator" else row["force_per_word"]), row["kind"], row["line"]))
    if target_words is None:
        emitted, flagged, remaining = ranked, [], None
        objective = "declared cue weight / rendered word, descending; heuristic, not calibrated force"
    else:
        remaining, emitted, flagged = target_words, [], []
        for row in ranked:
            if row["words"] <= remaining:
                emitted.append(row)
                remaining -= row["words"]
            else:
                flagged.append({"line": row["line"], "reason": "over budget; recoverable from full operator scan", "recoverable": True})
        objective = "declared cue weight / rendered word, descending; greedy fit, not an optimal summary"
    comparison = None
    if reference_text is not None:
        _ref_hits, ref_counts, ref_total, ref_inventory = scan(reference_text)
        def bounded_delta(delta: collections.Counter) -> tuple[list[dict[str, Any]], int]:
            rows = []
            for (cue_class, phrase), occurrences in sorted(delta.items()):
                if len(rows) >= MAX_LOGICAL_ACTION_HITS:
                    break
                rows.append({"class": cue_class, "phrase": phrase,
                             "occurrences": occurrences, "recoverable": True})
            return rows, max(0, len(delta) - len(rows))
        reference_delta = ref_inventory - current_inventory
        current_delta = current_inventory - ref_inventory
        reference_only, reference_only_omitted = bounded_delta(reference_delta)
        current_only, current_only_omitted = bounded_delta(current_delta)
        comparison = {"reference_counts_by_class": ref_counts, "current_counts_by_class": counts,
            "reference_total": ref_total, "current_total": total,
            "reference_only_occurrence_total": sum(reference_delta.values()),
            "reference_only_cues": reference_only,
            "reference_only_distinct_cues_omitted": reference_only_omitted,
            "current_only_occurrence_total": sum(current_delta.values()),
            "current_only_cues": current_only,
            "current_only_distinct_cues_omitted": current_only_omitted,
            "interpretation": "exact multiset difference of configured cue class/surface pairs; not proof a logical condition was lost or added"}
    return {"status": "CUES_FOUND" if hits else "NO_CUES_FOUND",
        "rule_version": "prime-logical-actions-1",
        "declared_weights": {name: weight for name, (_pattern, weight) in LOGICAL_ACTIONS.items()},
        "match_counts_by_class": counts, "total_match_count": total,
        "hits_returned": len(hits), "omitted_match_count": max(0, total - len(hits)),
        "hits_truncated": total > len(hits), "source_spans": hits,
        "sentence_operator_sequences": skeleton,
        "reference_comparison": comparison,
        "ranked_index": {"objective": objective, "word_budget": target_words,
            "words_remaining": remaining, "emitted": emitted, "flagged_not_deleted": flagged},
        "limitations": [
            "matches are configured surface cues, not proof of negation scope, entailment, causality, commitment, or truth",
            "weights are declared ranking priorities, not calibrated logical force",
            "different classes may overlap on a phrase and are reported separately",
            "sentence grouping uses punctuation/newline heuristics, not syntactic or argument parsing",
            "ranked index is not semantic compression; source wording and all flagged material remain unchanged",
        ]}

def _custom_domain_patterns(profile: dict[str, Any]) -> tuple[str, dict[str, str]]:
    """Compile a bounded JSON profile of literal phrases; never treat user data as regex/code."""
    if not isinstance(profile, dict) or set(profile) != {"name", "fields"}:
        raise ValueError("custom domain JSON must contain exactly 'name' and 'fields'")
    name, fields = profile["name"], profile["fields"]
    if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,47}", name):
        raise ValueError("custom domain name must be 1-48 lowercase letters, digits, or underscores; start with a letter")
    if not isinstance(fields, dict) or not 1 <= len(fields) <= 32:
        raise ValueError("custom domain fields must contain 1-32 named phrase lists")
    patterns: dict[str, str] = {}
    total_terms = total_chars = 0
    for field, terms in fields.items():
        if not isinstance(field, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,47}", field):
            raise ValueError("custom field names must be 1-48 lowercase letters, digits, or underscores; start with a letter")
        if not isinstance(terms, list) or not 1 <= len(terms) <= 128:
            raise ValueError(f"custom field {field!r} must have 1-128 literal phrases")
        clean = []
        for term in terms:
            if not isinstance(term, str) or not term.strip() or len(term) > 160:
                raise ValueError(f"custom field {field!r} has an empty, non-text, or over-160-character phrase")
            clean.append(term.strip())
            total_terms += 1
            total_chars += len(term)
        alternatives = "|".join(re.escape(term) for term in sorted(set(clean), key=lambda item: (-len(item), item.casefold())))
        patterns[field] = r"(?i:(?<!\w)(?:" + alternatives + r")(?!\w))"
    if total_terms > 512 or total_chars > 24_000:
        raise ValueError("custom domain is too large: maximum 512 phrases and 24,000 phrase characters")
    return name, patterns


def _load_custom_domain(path: str) -> dict[str, Any]:
    source = pathlib.Path(path)
    if source.stat().st_size > MAX_DOMAIN_CONFIG_BYTES:
        raise ValueError(f"custom domain JSON exceeds {MAX_DOMAIN_CONFIG_BYTES} bytes")
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read custom domain JSON: {exc}") from exc
    _custom_domain_patterns(data)
    return data


def _read_bounded_file(path: str, limit: int, label: str) -> tuple[str, bytes]:
    source = pathlib.Path(path)
    try:
        if source.stat().st_size > limit:
            raise ValueError(f"{label} exceeds the {limit}-byte limit")
        with source.open("rb") as handle:
            raw = handle.read(limit + 1)
    except OSError as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if len(raw) > limit:
        raise ValueError(f"{label} exceeds the {limit}-byte limit")
    try:
        return raw.decode("utf-8"), raw
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be UTF-8") from exc


def fold(text: str) -> str:
    return text.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'}))


def normalize(text: str) -> str:
    """Reproduce the ASCII §2 normalization used by the supplied prototype."""
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9:' ]", " ", fold(text).lower())).strip()
    return f" {cleaned} " if cleaned else ""


def count_term(normalized: str, term: str) -> int:
    if not normalized:
        return 0
    if " " in term:
        return len(re.findall(re.escape(term), normalized))
    return len(re.findall(r"\b" + re.escape(term) + r"\b", normalized))


def lexicon_counts(normalized: str, terms: list[str]) -> dict[str, int]:
    return {term: n for term in terms if (n := count_term(normalized, term)) > 0}


def span_hits(text: str, pattern: str, rule_id: str) -> list[dict[str, Any]]:
    return [{"text": m.group(0), "start": m.start(), "end": m.end(), "rule_id": rule_id}
            for m in re.finditer(pattern, text)]


def all_field_spans(text: str, patterns: dict[str, str], domain: str) -> dict[str, list[dict[str, Any]]]:
    return {field: span_hits(text, pattern, f"{domain}.{field}") for field, pattern in patterns.items()}


def _hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_report(report: Any, input_bytes: Optional[bytes] = None) -> dict[str, Any]:
    """Verify report self-integrity and optionally compare exact original input bytes."""
    if not isinstance(report, dict) or not isinstance(report.get("receipt"), dict):
        return {"report_integrity_valid": False, "input_source_match": None,
                "protocol": "SHA-256 content-integrity check; unsigned; no semantic attestation"}
    receipt = report["receipt"]
    payload = dict(report)
    payload.pop("receipt", None)
    report_ok = receipt.get("report_sha256_before_receipt") == _hash(_canonical(payload))
    input_match = None if input_bytes is None else receipt.get("input_sha256") == _hash(input_bytes)
    return {"report_integrity_valid": bool(report_ok), "input_source_match": input_match,
            "protocol": "SHA-256 content-integrity check; unsigned; no semantic attestation"}


def _word_tokens(text: str) -> list[str]:
    return [m.group(0).lower() for m in re.finditer(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text)]


def _paired_polarity(text: str) -> list[dict[str, Any]]:
    result = []
    for left, right in POLARITY_PAIRS:
        for polarity, term in (("left", left), ("right", right)):
            for hit in span_hits(text, r"(?i:\b" + re.escape(term) + r"\b)", f"polarity.{left}.{right}.{polarity}"):
                result.append({"pair": [left, right], "side": polarity, **hit})
    return sorted(result, key=lambda x: (x["start"], x["end"], x["rule_id"]))


def _attention(text: str) -> dict[str, Any]:
    first_nonempty = next(((m.start(), m.group(0)) for m in re.finditer(r"[^\n]+", text) if m.group(0).strip()), None)
    lead = None if first_nonempty is None else {"text": first_nonempty[1].strip(), "start": first_nonempty[0]}
    uppercase = span_hits(text, r"\b[A-Z]{2,}\b", "attention.all_caps")
    markers = []
    for term in ATTENTION_MARKERS:
        markers.extend(span_hits(text, r"(?i:\b" + re.escape(term) + r"\b)", "attention.marker." + term))
    repeated = [{"token": token, "count": n} for token, n in collections.Counter(_word_tokens(text)).most_common()
                if n > 1 and token not in STOP_WORDS][:20]
    return {"lead_line": lead, "all_caps_spans": uppercase, "exclamation_marks": text.count("!"),
            "configured_attention_marker_spans": sorted(markers, key=lambda x: x["start"]),
            "repeated_content_tokens": repeated,
            "interpretation": "surface placement/repetition cues only; layout emphasis needs original document structure"}


def _intention(text: str) -> dict[str, Any]:
    explicit = {name: span_hits(text, pattern, "intention." + name) for name, pattern in INTENTION_PATTERNS.items()}
    return {"explicit_cue_spans": explicit, "inferred_intention": [],
            "inference_status": "not inferred; requires independent evidence"}


def _rhetoric(text: str) -> dict[str, Any]:
    cues = {name: span_hits(text, pattern, "rhetoric." + name) for name, pattern in RHETORIC_PATTERNS.items()}
    return {"configured_cue_spans": cues, "question_marks": text.count("?"),
            "interpretation": "device/cue counts; context and function require review"}


def run_omni_analysis(text: str, context: Optional[str] = None, domain: str = "crypto",
                      frame: Optional[list[str]] = None, recorded_fields: Optional[list[str]] = None,
                      source_bytes: Optional[bytes] = None, culture: str = "none",
                      custom_domain: Optional[dict[str, Any]] = None,
                      sensory_metadata: Optional[dict[str, Any]] = None,
                      include_performance: bool = False,
                      term_catalog: Optional[dict[str, Any]] = None,
                      term_catalog_bytes: Optional[bytes] = None,
                      profundity_perception: Optional[dict[str, Any]] = None,
                      profundity_perception_bytes: Optional[bytes] = None,
                      include_word_dynamics: bool = False,
                      include_logical_actions: bool = False,
                      logical_action_word_budget: Optional[int] = None) -> dict[str, Any]:
    performance_started = time.perf_counter() if include_performance else None
    if custom_domain is not None:
        selected_domain, patterns = _custom_domain_patterns(custom_domain)
    else:
        if domain not in DOMAIN_PATTERNS:
            raise ValueError(f"Unsupported domain: {domain}")
        selected_domain, patterns = domain, DOMAIN_PATTERNS[domain]
    text_size = len(text.encode("utf-8"))
    source_size = len(source_bytes) if source_bytes is not None else text_size
    context_size = len(context.encode("utf-8")) if context is not None else 0
    if max(text_size, source_size) > MAX_TEXT_BYTES or context_size > MAX_CONTEXT_BYTES:
        raise ValueError("text or context exceeds the bounded UTF-8 input limit")
    if culture not in CULTURAL_CHOICES:
        raise ValueError(f"Unsupported cultural profile: {culture}")
    raw_bytes = source_bytes if source_bytes is not None else text.encode("utf-8")
    normalized = normalize(text)
    tokens = _word_tokens(text)
    word_dynamics_report = _word_dynamics_lens(text) if include_word_dynamics else {
        "configured": False, "scope": "optional bounded per-token dynamics ledger; not requested"}
    if logical_action_word_budget is not None and not include_logical_actions:
        raise ValueError("logical-action word budget requires include_logical_actions=True")
    logical_actions_report = _logical_action_lens(text, context, logical_action_word_budget) if include_logical_actions else {
        "configured": False, "scope": "optional logical-action cue ledger and ranked index; not requested"}
    s_hits, d_hits = lexicon_counts(normalized, STRUCT), lexicon_counts(normalized, EVAS)
    S, D = sum(s_hits.values()), sum(d_hits.values())
    l7, l10 = math.log(max(S, 1), 7), math.log10(max(D, 1))
    td = l7 / l10 if l10 > 0 else l7
    ascii_letters = re.findall(r"[a-z]", normalized)
    s_letters = sum(ch == "s" for ch in ascii_letters)
    pic = (len(ascii_letters) + 2.64 * s_letters) / len(ascii_letters) if ascii_letters else 0.0

    spans = all_field_spans(text, patterns, selected_domain)
    phi = {field: len(field_spans) for field, field_spans in spans.items()}
    chosen_frame = list(frame) if frame is not None else list(DEFAULT_FRAMES.get(selected_domain, patterns))
    chosen_recorded = list(recorded_fields) if recorded_fields is not None else list(patterns)
    unknown_recorded = sorted(set(chosen_recorded) - set(patterns))
    if unknown_recorded:
        raise ValueError(f"Recorded fields outside the declared {selected_domain} basis: {unknown_recorded}")
    unmeasured = sorted(set(chosen_frame) - set(patterns))
    frame_gaps = sorted(field for field in set(chosen_frame).intersection(patterns) if not spans[field])
    observed_frame = set(chosen_frame).intersection(patterns) - set(frame_gaps)
    measurable_frame_size = len(set(chosen_frame).intersection(patterns))
    coverage = len(observed_frame) / measurable_frame_size if measurable_frame_size else None
    recorded_set = set(chosen_recorded)
    projection = {field: phi[field] for field in patterns if field in recorded_set}
    residual = {field: phi[field] for field in patterns if field not in recorded_set}
    domain_hit_total = sum(phi.values())
    domain_rates = {field: (count / len(tokens) if tokens else None) for field, count in phi.items()}

    context_metrics = None
    if context is not None:
        source_counts, context_counts = collections.Counter(tokens), collections.Counter(_word_tokens(context))
        shared = sum((source_counts & context_counts).values())
        context_metrics = {"shared_token_occurrences": shared,
                           "source_token_occurrences": len(tokens),
                           "source_token_overlap_rate": round(shared / len(tokens), 6) if tokens else None,
                           "basis": "multiset token overlap; lexical only, not semantic entailment"}

    quality_quantity = _quality_quantity_dynamics(text, tokens, spans, chosen_frame, context_metrics)

    value_lenses = {"fact_vs_felt_truth": _fact_truth_lens(text, context, context_metrics),
                    "pleasure_vs_survival": _motivation_lens(text),
                    "deception_vs_lie": _lie_deception_lens(text)}
    arithmetic_lenses = _arithmetic_fact_truth_lens(text, context)
    value_lenses["fact_vs_felt_truth"]["sentence_cooccurrence_table"] = _fact_affect_sentence_table(text)
    law_rule_lens = _law_rule_lens(text)
    meaning_purpose = _meaning_purpose_polarity(text)
    awareness_lattice = _awareness_quadripartite_lattice(text)
    seven_letter = _seven_letter_inversion_interpolation(text)
    sensory_lexicons = _sensory_lexicon_lens(text)
    sensory_aperture = _sensory_metadata_aperture(sensory_metadata)
    thought_matrix = _thought_matrix_lattice(text)
    culture_report = _cultural_annotations(text, culture)
    term_catalog_report = _term_catalog_lens(term_catalog, term_catalog_bytes)
    profundity_perception_report = _profundity_perception_lens(profundity_perception, profundity_perception_bytes)
    embellishment_hits = []
    for term in EMBELLISHMENT:
        embellishment_hits.extend(span_hits(text, r"(?i:\b" + re.escape(term) + r"\b)", "embellishment." + term))
    embellishment_hits.sort(key=lambda x: x["start"])
    polarity_hits = _paired_polarity(text)
    lead_and_lenses = {
        "attention": _attention(text),
        "intention": _intention(text),
        "rhetoric": _rhetoric(text),
        "embellishment_cues": {"spans": embellishment_hits, "interpretation": "configured wording cues, not a factuality judgment"},
        "said": {"domain_field_spans": spans, "structural_lexicon_hits": s_hits, "evasion_lexicon_hits": d_hits,
                 "polarity_cue_spans": polarity_hits},
        "frame_relative_never_said": {"unobserved_fields": frame_gaps, "unmeasured_fields": unmeasured,
                                       "meaning": "no matching span found in supplied text under the selected frame and rules"},
        "observation_vs_hypothesis": {"observations": ["span matches and counts in this report"], "analyst_hypotheses": []},
    }

    output: dict[str, Any] = {
        "instrument": "AEE × LOGODECRYPT PRIME",
        "version": VERSION,
        "status": "ANALYZED" if text.strip() else "EMPTY",
        "scope": {"domain": selected_domain, "frame_fields": chosen_frame, "basis_fields": list(patterns),
                  "recorded_fields": chosen_recorded, "cultural_profile": culture,
                  "lexicon_basis": "built-in versioned starter rules"},
        "base_sensors": {"structural_count_S": S, "structural_hits": s_hits,
                         "evasion_count_D": D, "evasion_hits": d_hits,
                         "T_d": round(td, 4), "T_d_formula": "log7(max(S,1))/log10(max(D,1)); if denominator=0 use log7(max(S,1))",
                         "T_d_interpretation": "legacy configured-lexicon ratio only; no validated relationship to truth, accuracy, or deception",
                         "PIC": round(pic, 4), "PIC_basis": "1 + 2.64*(ASCII s/S letters / ASCII letters); 0 if no ASCII letters",
                         "PIC_interpretation": "unvalidated character-composition index; not a pathology or intent measure",
                         "token_count": len(tokens)},
        "domain_projection": {"feature_vector_phi": phi, "recorded_projection_R": projection,
                              "measurement_residual_u": residual,
                              "projection_definition": "R=Mφ; u=(I−M)φ; binary diagonal mask over the finite declared basis",
                              "finite_space_identity": "M²=M=Mᵀ, ker(M)=Range(M)⊥ under standard Euclidean inner product",
                              "domain_feature_hit_total": domain_hit_total,
                              "hits_per_token": {k: (round(v, 6) if v is not None else None) for k, v in domain_rates.items()},
                              "frame_gaps": frame_gaps, "unmeasured_frame_fields": unmeasured,
                              "frame_coverage": round(coverage, 6) if coverage is not None else None,
                              "coverage_denominator": measurable_frame_size if measurable_frame_size else None,
                              "frame_gap_interpretation": "unobserved under this frame; prompts review and supplies no hidden proposition"},
        "paired_lenses": lead_and_lenses,
        "quality_quantity_dynamics": quality_quantity,
        "market_readiness": {
            "maturity": "research prototype; not production-certified",
            "supported_now": ["offline deterministic text-pattern and exact-rational checks", "source-preserving offsets and unsigned integrity hashes", "built-in frames and bounded literal-only custom profiles", "finite terminology-reference checks and exact Jaccard set distances"],
            "not_established": ["truth, intent, deception, etymological accuracy, semantic identity, antonym quality, contract safety, predictive accuracy, customer demand, or commercial superiority"],
            "release_gates": ["independent, rights-cleared, labeled evaluation against simple baselines", "false-positive/false-negative and domain-shift measurements", "security and resource-limit review on hostile inputs", "documented license, privacy, deployment, and support terms", "user pilot confirming workflow value and willingness to pay"],
            "systemic_root_scope": "configured Solidity/Web3 surface-term flags only; no AST, bytecode, call-graph, exploit, or formal-verification analysis",
        },
        "fact_truth_motivation_lie_deception_lenses": value_lenses,
        "arithmetic_truth_and_mathematical_facts": arithmetic_lenses,
        "algorithmic_thought_matrix_and_boolean_lattice": thought_matrix,
        "law_rule_polarity_lexicon_lens": law_rule_lens,
        "meaning_purpose_polarity_tables": meaning_purpose,
        "four_part_awareness_quaternion_and_quadratic_lattice": awareness_lattice,
        "seven_letter_inversion_and_interpolation": seven_letter,
        "sensory_lexicon_polarity_tables": sensory_lexicons,
        "sensory_metadata_aperture": sensory_aperture,
        "cultural_aperture_and_ligature_annotations": culture_report,
        "terminology_consistency_audit": term_catalog_report,
        "profundity_perception_permutation_fidelity": profundity_perception_report,
        "per_word_dynamics_and_slot_permutation": word_dynamics_report,
        "logical_action_cue_ledger_and_ranked_index": logical_actions_report,
        "token_chain": {"adjacent_pair_count": max(0, len(tokens) - 1),
                        "sample_pairs": [f"{tokens[i]}-{tokens[i+1]}" for i in range(min(max(0, len(tokens)-1), 10))]},
    }
    if context_metrics is not None:
        output["context_overlap"] = context_metrics
    if performance_started is not None:
        elapsed = max(time.perf_counter() - performance_started, 1e-12)
        output["runtime_performance_profile"] = {
            "scope": "single local run of run_omni_analysis; excludes CLI startup and file I/O",
            "elapsed_ms": round(elapsed * 1000, 6), "input_bytes": len(raw_bytes), "token_count": len(tokens),
            "tokens_per_second": round(len(tokens) / elapsed, 3),
            "input_bytes_per_second": round(len(raw_bytes) / elapsed, 3),
            "timing_source": "time.perf_counter; a single-run observation, not a benchmark or latency guarantee"}
    report_hash = _hash(_canonical(output))
    output["receipt"] = {"input_sha256": _hash(raw_bytes), "report_sha256_before_receipt": report_hash,
                         "protocol": "SHA-256 content-integrity receipt; unsigned; no semantic attestation"}
    return output



def _sentence_syllable_estimate(sentence: str) -> int:
    """Rough vowel-group count; a reading aid, not phonetic transcription."""
    total = 0
    for word in _word_tokens(sentence):
        groups = len(re.findall(r"[aeiouy]+", word))
        if len(word) > 2 and word.endswith("e") and not word.endswith("le") and groups > 1:
            groups -= 1
        total += max(1, groups)
    return total


def _orthographic_rhyme_key(word: str) -> str:
    """Last vowel-group plus following letters; deterministic spelling proxy."""
    matches = list(re.finditer(r"[aeiouy]+[^aeiouy]*$", word.lower()))
    return matches[-1].group(0) if matches else word.lower()[-3:]


def _sentence_spans(text: str) -> list[tuple[str, int, int]]:
    """Split sentences and retain sequential original offsets, including repeated sentences."""
    rows = []
    cursor = 0
    for part in re.split(r"(?<=[.!?])\s+|\n+", text):
        sentence = part.strip()
        if not sentence:
            continue
        start = text.find(sentence, cursor)
        if start < 0:
            continue
        end = start + len(sentence)
        rows.append((sentence, start, end))
        cursor = end
    return rows


def _quality_quantity_dynamics(text: str, tokens: list[str], field_spans: dict[str, list[dict[str, Any]]],
                               frame_fields: list[str], context_metrics: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Report separate descriptive axes; never collapse them into a quality verdict."""
    sentence_rows = _sentence_spans(text)
    sentences = [row[0] for row in sentence_rows]
    sentence_tokens = [_word_tokens(sentence) for sentence in sentences]
    lengths = [len(row) for row in sentence_tokens]
    content_tokens = [word for word in tokens if word not in STOP_WORDS]
    unique_content = set(content_tokens)
    matched_fields = [field for field in frame_fields if field in field_spans and field_spans[field]]
    quantity = {
        "characters_including_whitespace": len(text),
        "word_tokens": len(tokens),
        "nonempty_sentences_heuristic": len(sentences),
        "clause_delimiter_count": len(re.findall(r"[;:,—–]", text)),
        "paragraphs_heuristic": len([part for part in re.split(r"\n\s*\n", text) if part.strip()]),
    }
    lexical_variety = len(unique_content) / len(content_tokens) if content_tokens else None
    frame_coverage = len(matched_fields) / len(frame_fields) if frame_fields else None
    quality_proxies = {
        "content_token_variety": {"value": round(lexical_variety, 6) if lexical_variety is not None else None,
                                   "numerator": len(unique_content), "denominator": len(content_tokens),
                                   "definition": "distinct non-stopword tokens / non-stopword token occurrences"},
        "declared_frame_coverage": {"value": round(frame_coverage, 6) if frame_coverage is not None else None,
                                    "matched_fields": matched_fields, "frame_field_count": len(frame_fields),
                                    "definition": "frame fields with at least one rule span / declared frame fields"},
        "lexical_information_yield_per_100_tokens": round(100 * len(unique_content) / len(tokens), 6) if tokens else None,
        "matched_frame_fields_per_100_tokens": round(100 * len(matched_fields) / len(tokens), 6) if tokens else None,
        "source_overlap": context_metrics,
    }
    mean_length = sum(lengths) / len(lengths) if lengths else 0.0
    sd_length = math.sqrt(sum((value - mean_length) ** 2 for value in lengths) / len(lengths)) if lengths else 0.0
    cv = sd_length / mean_length if mean_length else None
    transitions = ["longer" if b > a else "shorter" if b < a else "same" for a, b in zip(lengths, lengths[1:])]
    if len(lengths) > 1:
        x_mean = (len(lengths) - 1) / 2
        denominator = sum((i - x_mean) ** 2 for i in range(len(lengths)))
        slope = sum((i - x_mean) * (value - mean_length) for i, value in enumerate(lengths)) / denominator if denominator else 0.0
    else:
        slope = None

    endings = []
    scheme_by_key: dict[str, str] = {}
    for index, row in enumerate(sentence_tokens):
        if not row:
            continue
        final_word = row[-1]
        key = _orthographic_rhyme_key(final_word)
        if key not in scheme_by_key:
            label_index = len(scheme_by_key)
            scheme_by_key[key] = chr(65 + label_index) if label_index < 26 else f"R{label_index + 1}"
        endings.append({"sentence_index": index + 1, "word": final_word, "orthographic_key": key,
                        "scheme_label": scheme_by_key[key]})
    key_counts = collections.Counter(row["orthographic_key"] for row in endings)
    word_counts_by_key: dict[str, collections.Counter[str]] = {}
    for row in endings:
        word_counts_by_key.setdefault(row["orthographic_key"], collections.Counter())[row["word"]] += 1
    total_rhyme_pairs = sum(count * (count - 1) // 2 for count in key_counts.values())
    repeated_identical_end_pairs = sum(count * (count - 1) // 2
                                       for counter in word_counts_by_key.values() for count in counter.values())
    distinct_word_rhyme_pairs = total_rhyme_pairs - repeated_identical_end_pairs
    adjacent_pairs = max(0, len(endings) - 1)
    adjacent_matches = sum(a["orthographic_key"] == b["orthographic_key"] for a, b in zip(endings, endings[1:]))

    dynamics = []
    cumulative_content: set[str] = set()
    cumulative_fields: set[str] = set()
    for index, (sentence, row) in enumerate(zip(sentences, sentence_tokens)):
        cumulative_content.update(word for word in row if word not in STOP_WORDS)
        sentence_start, sentence_end = sentence_rows[index][1], sentence_rows[index][2]
        for field in matched_fields:
            if any(hit["start"] >= sentence_start and hit["end"] <= sentence_end
                   for hit in field_spans[field]):
                cumulative_fields.add(field)
        dynamics.append({"sentence_index": index + 1, "token_count": len(row),
                         "cumulative_distinct_content_tokens": len(cumulative_content),
                         "cumulative_frame_fields_observed": len(cumulative_fields)})
    return {
        "axioms": [
            "Quantity is an exact count under the stated tokenizer and sentence/clause heuristics.",
            "Quality is represented as separate observable proxies; this report assigns no overall quality score.",
            "Density relates selected proxies to token count; greater density is descriptive, not inherently better.",
            "Dynamics follow supplied sentence order; comparisons require the same domain, frame, and rule version.",
            "Rhythm uses sentence token lengths and a rough vowel-group syllable estimate.",
            "Rhyme uses spelling-based endings; it is an orthographic approximation, not phonetic rhyme analysis.",
        ],
        "quantity": quantity,
        "quality_proxies": quality_proxies,
        "quality_quantity_balance": {
            "information_yield_per_100_tokens": quality_proxies["lexical_information_yield_per_100_tokens"],
            "frame_coverage_per_100_tokens": quality_proxies["matched_frame_fields_per_100_tokens"],
            "lexical_variety": quality_proxies["content_token_variety"]["value"],
            "interpretation": "paired vector of information/coverage densities and lexical variety; no single winner score",
        },
        "rhythm": {
            "sentence_token_counts": lengths,
            "sentence_syllable_estimates": [_sentence_syllable_estimate(sentence) for sentence in sentences],
            "mean_sentence_tokens": round(mean_length, 6) if lengths else None,
            "population_sd_sentence_tokens": round(sd_length, 6) if lengths else None,
            "sentence_length_coefficient_of_variation": round(cv, 6) if cv is not None else None,
            "regularity_proxy": round(1 / (1 + cv), 6) if cv is not None else None,
            "adjacent_length_transitions": transitions,
            "sentence_length_trend_tokens_per_sentence": round(slope, 6) if slope is not None else None,
            "interpretation": "descriptive cadence statistics; regularity is not an aesthetic rating",
        },
        "rhyme": {
            "sentence_endings": endings,
            "scheme": [row["scheme_label"] for row in endings],
            "orthographic_rhyme_pairs_distinct_end_words": distinct_word_rhyme_pairs,
            "repeated_identical_sentence_end_pairs": repeated_identical_end_pairs,
            "adjacent_ending_matches": adjacent_matches,
            "adjacent_ending_match_rate": round(adjacent_matches / adjacent_pairs, 6) if adjacent_pairs else None,
            "interpretation": "shared spelling-key signal; inspect audio/phonetics for true rhyme",
        },
        "sentence_order_dynamics": dynamics,
    }



FACT_CUES = ["fact", "facts", "know", "known", "evidence", "record", "verified", "source", "claim"]
AFFECT_CUES = ["feel", "feels", "felt", "hurt", "pain", "mark", "betrayed", "trust", "embarrassed", "uncomfortable", "grief", "anger", "fear"]
SURVIVAL_CUES = ["survive", "survival", "safe", "safety", "danger", "protect", "protection", "food", "shelter", "health", "threat", "risk", "loss"]
PLEASURE_CUES = ["pleasure", "enjoy", "enjoyment", "joy", "reward", "satisfy", "satisfaction", "delight", "fun", "comfort", "gratification"]
DECEPTION_PATTERNS = {
    "concealment_or_omission": r"(?i:\b(?:conceal(?:ed|s|ing)?|withheld|omitted|left out|undisclosed|hidden|obscured)\b)",
    "misdirection_or_false_presentation": r"(?i:\b(?:mislead(?:ing)?|misrepresent(?:ed|s|ing)?|deceiv(?:e|ed|es|ing)|false impression)\b)",
    "explicit_lie_or_fabrication_claim": r"(?i:\b(?:lie|lies|lied|lying|fabricat(?:ed|ion)|knowingly false)\b)",
}


def _word_cue_spans(text: str, terms: list[str], prefix: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for term in terms:
        hits.extend(span_hits(text, r"(?i:\b" + re.escape(term) + r"\b)", prefix + "." + term))
    return sorted(hits, key=lambda row: (row["start"], row["end"]))


SENSORY_FIELDS = {
    "root": {"captured_at_utc", "measurement_source", "device_class", "visual", "audio"},
    "visual": {"width_px", "height_px", "pixel_pitch_um", "focal_length_mm", "aperture_f_number",
               "exposure_time_ms", "frame_rate_fps", "color_space", "acuity_snellen"},
    "audio": {"sample_rate_hz", "channels", "bit_depth", "duration_ms", "codec", "rms_dbfs",
              "peak_dbfs", "snr_db", "clipping_fraction"},
}

def _validate_sensory_metadata(value: Any) -> dict[str, Any]:
    """Validate caller-provided metadata; it is not obtained from or verified against a device."""
    if not isinstance(value, dict):
        raise ValueError("sensory metadata must be a JSON object")
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ValueError("sensory metadata must contain JSON-compatible finite values") from exc
    if len(encoded) > MAX_SENSORY_METADATA_BYTES:
        raise ValueError(f"sensory metadata exceeds {MAX_SENSORY_METADATA_BYTES} bytes")
    extra = set(value) - SENSORY_FIELDS["root"]
    if extra:
        raise ValueError(f"unknown sensory metadata fields: {sorted(extra)}")
    for key in ("captured_at_utc", "measurement_source", "device_class"):
        item = value.get(key)
        if item is not None and (not isinstance(item, str) or len(item) > 128):
            raise ValueError(f"{key} must be a string of at most 128 characters")
    for modality in ("visual", "audio"):
        block = value.get(modality, {})
        if not isinstance(block, dict):
            raise ValueError(f"{modality} metadata must be an object")
        unknown = set(block) - SENSORY_FIELDS[modality]
        if unknown:
            raise ValueError(f"unknown {modality} metadata fields: {sorted(unknown)}")
        for key, item in block.items():
            if key in {"color_space", "acuity_snellen", "codec"}:
                if not isinstance(item, str) or not item or len(item) > 64:
                    raise ValueError(f"{modality}.{key} must be a non-empty string of at most 64 characters")
            elif key in {"width_px", "height_px", "sample_rate_hz", "channels", "bit_depth", "duration_ms"}:
                if isinstance(item, bool) or not isinstance(item, int):
                    raise ValueError(f"{modality}.{key} must be an integer")
                limits = {"width_px": (1, 100_000), "height_px": (1, 100_000),
                          "sample_rate_hz": (1, 768_000), "channels": (1, 128),
                          "bit_depth": (1, 64), "duration_ms": (1, 86_400_000)}
                low, high = limits[key]
                if not low <= item <= high:
                    raise ValueError(f"{modality}.{key} is outside {low}..{high}")
            else:
                if isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(float(item)):
                    raise ValueError(f"{modality}.{key} must be a finite number")
                bounds = {"pixel_pitch_um": (0, 100_000), "focal_length_mm": (0, 100_000),
                          "aperture_f_number": (0, 1_000), "exposure_time_ms": (0, 86_400_000),
                          "frame_rate_fps": (0, 1_000), "rms_dbfs": (-160, 0), "peak_dbfs": (-160, 0),
                          "snr_db": (-200, 200), "clipping_fraction": (0, 1)}
                low, high = bounds[key]
                in_range = (low <= float(item) <= high) if key == "clipping_fraction" or low != 0 else (low < float(item) <= high)
                if not in_range:
                    raise ValueError(f"{modality}.{key} is outside its permitted numeric range")
    visual, audio = value.get("visual", {}), value.get("audio", {})
    if "acuity_snellen" in visual:
        if not re.fullmatch(r"\d{1,3}/\d{1,3}", visual["acuity_snellen"]):
            raise ValueError("visual.acuity_snellen must use numeric n/d notation such as 20/20")
        numerator, denominator = (int(part) for part in visual["acuity_snellen"].split("/"))
        if numerator <= 0 or denominator <= 0:
            raise ValueError("visual.acuity_snellen numerator and denominator must be positive")
    if "rms_dbfs" in audio and "peak_dbfs" in audio and audio["rms_dbfs"] > audio["peak_dbfs"]:
        raise ValueError("audio.rms_dbfs cannot exceed audio.peak_dbfs")
    return value


def _sensory_lexicon_lens(text: str) -> dict[str, Any]:
    def hits(terms: list[str], prefix: str) -> list[dict[str, Any]]:
        result = []
        for term in terms:
            result.extend(span_hits(text, r"(?i:\b" + re.escape(term) + r"\b)", prefix + "." + term))
        return sorted(result, key=lambda row: (row["start"], row["end"]))
    optical = hits(OPTICAL_LEXICON, "sensory.optical")
    auditory = hits(AUDITORY_LEXICON, "sensory.auditory")
    profundity = hits(PROFUNDITY_CUES, "sensory.profundity")
    perception = hits(PERCEPTION_CUES, "sensory.perception")
    names = (("neither", 0), ("optical_only", 1), ("auditory_only", 2), ("both", 3))
    cells = dict.fromkeys((item[0] for item in names), 0)
    rows = []
    for index, (sentence, start, end) in enumerate(_sentence_spans(text), 1):
        has_optical = bool(hits(OPTICAL_LEXICON, "sensory.optical")) if sentence == text else any(
            re.search(r"(?i:\b" + re.escape(term) + r"\b)", sentence) for term in OPTICAL_LEXICON)
        has_auditory = any(re.search(r"(?i:\b" + re.escape(term) + r"\b)", sentence) for term in AUDITORY_LEXICON)
        cell = "both" if has_optical and has_auditory else "optical_only" if has_optical else "auditory_only" if has_auditory else "neither"
        cells[cell] += 1
        rows.append({"sentence_index": index, "start": start, "end": end,
                     "optical_cue_present": has_optical, "auditory_cue_present": has_auditory, "cell": cell})
    optical_count, auditory_count = len(optical), len(auditory)
    total = optical_count + auditory_count
    profound_count, perceive_count = len(profundity), len(perception)
    pp_total = profound_count + perceive_count
    pp_cells = {"neither": 0, "profundity_only": 0, "perception_only": 0, "both": 0}
    pp_rows = []
    for index, (sentence, start, end) in enumerate(_sentence_spans(text), 1):
        has_deep = any(re.search(r"(?i:\b" + re.escape(term) + r"\b)", sentence) for term in PROFUNDITY_CUES)
        has_perception = any(re.search(r"(?i:\b" + re.escape(term) + r"\b)", sentence) for term in PERCEPTION_CUES)
        cell = "both" if has_deep and has_perception else "profundity_only" if has_deep else "perception_only" if has_perception else "neither"
        pp_cells[cell] += 1
        pp_rows.append({"sentence_index": index, "start": start, "end": end,
                        "profundity_cue_present": has_deep, "perception_cue_present": has_perception, "cell": cell})
    return {"lexicon_sizes": {"optical": len(OPTICAL_LEXICON), "auditory": len(AUDITORY_LEXICON),
                              "profundity": len(PROFUNDITY_CUES), "perception": len(PERCEPTION_CUES)},
            "optical_auditory_dichotomy_table": {"matrix": [[cells["neither"], cells["auditory_only"]],
                                                              [cells["optical_only"], cells["both"]]],
                                                  "axis_order": ["optical absent/present", "auditory absent/present"],
                                                  "cell_counts": cells, "sentence_rows": rows,
                                                  "optical_cue_count": optical_count, "auditory_cue_count": auditory_count,
                                                  "optical_to_auditory_ratio": optical_count / auditory_count if auditory_count else None,
                                                  "normalized_optical_minus_auditory": (optical_count - auditory_count) / total if total else None,
                                                  "optical_spans": optical, "auditory_spans": auditory,
                                                  "interpretation": "configured vocabulary occurrences and sentence co-occurrence only; no image or sound content was assessed"},
            "profundity_perception_dichotomy_table": {"matrix": [[pp_cells["neither"], pp_cells["perception_only"]],
                                                                    [pp_cells["profundity_only"], pp_cells["both"]]],
                                                       "cell_counts": pp_cells, "sentence_rows": pp_rows,
                                                       "profundity_count": profound_count, "perception_count": perceive_count,
                                                       "profundity_to_perception_ratio": profound_count / perceive_count if perceive_count else None,
                                                       "normalized_profundity_minus_perception": (profound_count - perceive_count) / pp_total if pp_total else None,
                                                       "profundity_spans": profundity, "perception_spans": perception,
                                                       "interpretation": "configured lexical counts only; not actual perceptual acuity, depth of understanding, or awareness"}}


def _sensory_metadata_aperture(value: Optional[dict[str, Any]]) -> dict[str, Any]:
    if value is None:
        return {"status": "NOT_SUPPLIED", "metadata_source": None,
                "media_content_processed": {"visual": False, "audio": False},
                "interpretation": "no visual/audio metadata supplied; no device or media capture attempted"}
    data = _validate_sensory_metadata(value)
    visual, audio = data.get("visual", {}), data.get("audio", {})
    visual_expected, audio_expected = len(SENSORY_FIELDS["visual"]), len(SENSORY_FIELDS["audio"])
    visual_ratio = Fraction(int(visual["width_px"]), int(visual["height_px"])) if {"width_px", "height_px"} <= set(visual) else None
    snellen = visual.get("acuity_snellen")
    snellen_ratio = Fraction(*(int(part) for part in snellen.split("/"))) if snellen else None
    sample_frames = Fraction(audio["sample_rate_hz"] * audio["duration_ms"], 1000) if {"sample_rate_hz", "duration_ms"} <= set(audio) else None
    audio_bitrate = audio["sample_rate_hz"] * audio["channels"] * audio["bit_depth"] if {"sample_rate_hz", "channels", "bit_depth"} <= set(audio) else None
    return {"status": "METADATA_VALIDATED", "metadata_source": {k: data.get(k) for k in ("captured_at_utc", "measurement_source", "device_class")},
            "provided_metadata": data,
            "data_metadata_dichotomy": {"visual_media_payload_supplied": False, "audio_media_payload_supplied": False,
                                         "visual_metadata_supplied": bool(visual), "audio_metadata_supplied": bool(audio),
                                         "boundary": "metadata claims and sensor/media data are distinct; this CLI evaluates caller-provided metadata only"},
            "optical_measurements": {"metadata_field_count": len(visual), "configured_field_count": visual_expected,
                                     "metadata_completeness": round(len(visual) / visual_expected, 6),
                                     "pixel_count": visual["width_px"] * visual["height_px"] if {"width_px", "height_px"} <= set(visual) else None,
                                     "aspect_ratio_exact": _fraction_string(visual_ratio) if visual_ratio else None,
                                     "aspect_ratio_decimal": round(float(visual_ratio), 8) if visual_ratio else None,
                                     "reported_snellen": snellen, "reported_snellen_fraction": _fraction_string(snellen_ratio) if snellen_ratio else None,
                                     "twenty_twenty_reference": "20/20 equals 1/1 as a Snellen ratio; reference arithmetic only, not an eye exam or optics calibration" if snellen else None},
            "auditory_measurements": {"metadata_field_count": len(audio), "configured_field_count": audio_expected,
                                      "metadata_completeness": round(len(audio) / audio_expected, 6),
                                      "nominal_uncompressed_bitrate_bps": audio_bitrate,
                                      "sample_frames_per_channel_exact": _fraction_string(sample_frames) if sample_frames else None,
                                      "reported_peak_minus_rms_db": round(audio["peak_dbfs"] - audio["rms_dbfs"], 6) if {"peak_dbfs", "rms_dbfs"} <= set(audio) else None},
            "arithmetic_and_consistency": {"rms_not_above_peak": not ("rms_dbfs" in audio and "peak_dbfs" in audio and audio["rms_dbfs"] > audio["peak_dbfs"]),
                                           "snellen_is_20_20": bool(snellen_ratio == 1) if snellen_ratio is not None else None,
                                           "nominal_bitrate_formula": "sample_rate_hz × channels × bit_depth; uncompressed upper-level metadata arithmetic, not measured network or codec throughput"},
            "interpretation": "declared metadata completeness and arithmetic only; not verified device telemetry, sensor calibration, image/audio analysis, human perceptual quality, or live monitoring"}


def _load_sensory_metadata(path: str) -> dict[str, Any]:
    source = pathlib.Path(path)
    if source.stat().st_size > MAX_SENSORY_METADATA_BYTES:
        raise ValueError(f"sensory metadata exceeds {MAX_SENSORY_METADATA_BYTES} bytes")
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read sensory metadata JSON: {exc}") from exc
    return _validate_sensory_metadata(value)


def _fact_affect_sentence_table(text: str) -> dict[str, Any]:
    """Count configured fact/affect cue co-occurrence by sentence; no truth inference."""
    rows = []
    cells = {"neither": 0, "fact_only": 0, "affect_only": 0, "both": 0}
    for index, (sentence, start, end) in enumerate(_sentence_spans(text), 1):
        fact_present = bool(_word_cue_spans(sentence, FACT_CUES, "fact_table"))
        affect_present = bool(_word_cue_spans(sentence, AFFECT_CUES, "affect_table"))
        key = "both" if fact_present and affect_present else "fact_only" if fact_present else "affect_only" if affect_present else "neither"
        cells[key] += 1
        rows.append({"sentence_index": index, "start": start, "end": end,
                     "fact_cue_present": fact_present, "affect_cue_present": affect_present, "cell": key})
    return {"matrix": [[cells["neither"], cells["affect_only"]],
                       [cells["fact_only"], cells["both"]]],
            "row_axis": ["fact cue absent", "fact cue present"],
            "column_axis": ["affect cue absent", "affect cue present"],
            "cell_counts": cells, "sentence_rows": rows,
            "interpretation": "configured lexical cue co-occurrence only; source support and reported feeling remain separate, and no cell establishes truth"}


def _law_rule_lens(text: str) -> dict[str, Any]:
    law = _word_cue_spans(text, LAW_CUES, "law_cue")
    rule = _word_cue_spans(text, RULE_CUES, "rule_cue")
    law_count, rule_count = len(law), len(rule)
    cells = {"neither": 0, "law_only": 0, "rule_only": 0, "both": 0}
    rows = []
    for index, (sentence, start, end) in enumerate(_sentence_spans(text), 1):
        has_law = bool(_word_cue_spans(sentence, LAW_CUES, "law_cue"))
        has_rule = bool(_word_cue_spans(sentence, RULE_CUES, "rule_cue"))
        key = "both" if has_law and has_rule else "law_only" if has_law else "rule_only" if has_rule else "neither"
        cells[key] += 1
        rows.append({"sentence_index": index, "start": start, "end": end, "law_cue_present": has_law, "rule_cue_present": has_rule, "cell": key})
    total = law_count + rule_count
    return {"law_cue_spans": law, "rule_cue_spans": rule,
            "counts": {"law": law_count, "rule": rule_count},
            "law_to_rule_count_ratio": law_count / rule_count if rule_count else None,
            "normalized_difference_law_minus_rule": (law_count - rule_count) / total if total else None,
            "sentence_cooccurrence": {"matrix": [[cells["neither"], cells["rule_only"]], [cells["law_only"], cells["both"]]],
                                      "cell_counts": cells, "sentence_rows": rows},
            "ratio_definition": "configured exact-token cue count law/rule; null when rule count is zero",
            "interpretation": "lexical mention balance only; not legal hierarchy, jurisdiction, applicability, or legal advice"}


def _polarity_pair_table(text: str, pairs: list[tuple[str, str]], label: str) -> dict[str, Any]:
    result = []
    sentence_rows = _sentence_spans(text)
    for left, right in pairs:
        left_hits = _word_cue_spans(text, [left], label + "." + left)
        right_hits = _word_cue_spans(text, [right], label + "." + right)
        both_sentences = sum(bool(_word_cue_spans(sentence, [left], label)) and bool(_word_cue_spans(sentence, [right], label))
                             for sentence, _, _ in sentence_rows)
        total = len(left_hits) + len(right_hits)
        result.append({"curated_pair": [left, right], "left_count": len(left_hits), "right_count": len(right_hits),
                       "left_to_right_ratio": len(left_hits) / len(right_hits) if right_hits else None,
                       "normalized_polarity_balance": (len(left_hits) - len(right_hits)) / total if total else None,
                       "sentences_with_both": both_sentences, "left_spans": left_hits, "right_spans": right_hits,
                       "status": "configured candidate contrast; not a universal or context-resolved antonym"})
    return {"pairs": result, "interpretation": "counted lexical contrasts and same-sentence co-occurrence; no semantic substitution or intent is inferred"}


def _meaning_purpose_polarity(text: str) -> dict[str, Any]:
    dimensions = ["meaning", "purpose"]
    state_counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    cooccurrence = [[0, 0], [0, 0]]
    sentence_rows = []
    for index, (sentence, start, end) in enumerate(_sentence_spans(text), 1):
        vector = [int(bool(_word_cue_spans(sentence, AWARENESS_CUES[name], "metapragmatic." + name))) for name in dimensions]
        state = "".join(str(bit) for bit in vector)
        state_counts[state] += 1
        for i in range(2):
            for j in range(2):
                cooccurrence[i][j] += vector[i] * vector[j]
        sentence_rows.append({"sentence_index": index, "start": start, "end": end,
                              "feature_vector_order": dimensions, "feature_vector": vector,
                              "boolean_state": state,
                              "quadratic_outer_product": [[a * b for b in vector] for a in vector]})
    meta_terms = ["word", "words", "language", "text", "sentence", "phrase", "statement", "claim",
                  "meaning", "definition", "interpret", "imply", "implies", "said", "unsaid",
                  "rhetoric", "metaphor", "literal", "figurative"]
    return {"meaning_polarities": _polarity_pair_table(text, MEANING_POLARITY_PAIRS, "meaning_polarity"),
            "purpose_polarities": _polarity_pair_table(text, PURPOSE_POLARITY_PAIRS, "purpose_polarity"),
            "metapragmatic_aperture": {"configured_cue_spans": _word_cue_spans(text, meta_terms, "metapragmatic_aperture"),
                                       "interpretation": "explicit language-about-language cues only; no inferred subtext"},
            "meaning_purpose_boolean_quadratic_lattice": {"dimension": 2, "possible_nodes": 4,
                                                           "state_counts": state_counts,
                                                           "pairwise_binary_cooccurrence_matrix": cooccurrence,
                                                           "sentence_rows": sentence_rows,
                                                           "polynomial_basis": "x_meaning, x_purpose, and their product; binary idempotence x_i^2=x_i",
                                                           "diagonal_idempotence_holds_by_construction": True},
            "interpolation": "no ungrounded text is generated; balance and co-occurrence are reported as separate finite proxies"}


def _awareness_quadripartite_lattice(text: str) -> dict[str, Any]:
    """Encode four declared cue families as finite vectors, Boolean products and a quaternion."""
    names = list(AWARENESS_CUES)
    sentence_rows = []
    state_counts = {format(mask, "04b"): 0 for mask in range(16)}
    cooccurrence = [[0 for _ in names] for _ in names]
    counts = {name: 0 for name in names}
    for index, (sentence, start, end) in enumerate(_sentence_spans(text), 1):
        hits = {name: _word_cue_spans(sentence, terms, "awareness." + name) for name, terms in AWARENESS_CUES.items()}
        vector = [int(bool(hits[name])) for name in names]
        mask = sum(bit << (len(names) - position - 1) for position, bit in enumerate(vector))
        bit_key = format(mask, "04b")
        state_counts[bit_key] += 1
        for i, name in enumerate(names):
            counts[name] += len(hits[name])
            for j in range(len(names)):
                cooccurrence[i][j] += vector[i] * vector[j]
        sentence_rows.append({"sentence_index": index, "start": start, "end": end,
                              "feature_vector_order": names, "feature_vector": vector,
                              "boolean_state": bit_key, "quadratic_outer_product": [[a * b for b in vector] for a in vector]})
    norm = math.sqrt(sum(value * value for value in counts.values()))
    quaternion = [counts[name] / norm for name in names] if norm else None
    if quaternion is not None:
        a, b, c, d = quaternion
        left_matrix = [[a, -b, -c, -d], [b, a, -d, c], [c, d, a, -b], [d, -c, b, a]]
    else:
        left_matrix = None
    ranks = {str(rank): sum(1 for key, value in state_counts.items() if value and key.count("1") == rank)
             for rank in range(len(names) + 1)}
    return {"feature_order": names, "cue_counts": counts,
            "sentence_matrix_rows": sentence_rows,
            "pairwise_binary_cooccurrence_matrix": cooccurrence,
            "boolean_quadratic_lattice": {"dimension": len(names), "possible_nodes": 2 ** len(names),
                                           "observed_nodes": sum(value > 0 for value in state_counts.values()),
                                           "state_counts": state_counts, "observed_rank_counts": ranks,
                                           "polynomial_basis": "x_i and x_i*x_j over binary sentence indicators; x_i^2=x_i",
                                           "diagonal_idempotence_holds_by_construction": True},
            "quaternionic_cue_encoding": {"component_order": ["meaning/scalar", "purpose/i", "thought/j", "emotion/k"],
                                         "raw_components": [counts[name] for name in names],
                                         "l2_norm": round(norm, 8), "normalized_components": quaternion,
                                         "left_multiplication_matrix": left_matrix,
                                         "matrix_identity": "for q=a+bi+cj+dk, L(q)^T L(q)=||q||^2 I; normalized nonzero q yields I",
                                         "interpretation": "chosen algebraic encoding of cue counts; not a measurement of awareness, inner thought, divine logic, or semantic truth"},
            "separation_and_coupling": "axes are distinct coordinates; lexical cues can co-occur, so no semantic mutual-exclusion axiom is asserted"}


def _seven_letter_inversion_interpolation(text: str, row_cap: int = 64) -> dict[str, Any]:
    matches = list(re.finditer(r"(?<![A-Za-z])[A-Za-z]{7}(?![A-Za-z])", text))
    rows = []
    for match in matches[:row_cap]:
        token = match.group(0)
        reversed_token = token[::-1]
        # Exact twice-midpoint coordinates avoid floating-point rounding.
        midpoint_twice = [ord(a) + ord(b) for a, b in zip(token, reversed_token)]
        rows.append({"token": token, "start": match.start(), "end": match.end(),
                     "reversed_spelling": reversed_token, "reversal_permutation_1_based": [7, 6, 5, 4, 3, 2, 1],
                     "midpoint_codepoint_numerators_over_2": midpoint_twice,
                     "interpretation": "mechanical seven-ASCII-letter reversal and aligned codepoint midpoint; not decryption or recovered meaning"})
    return {"scope": "ASCII alphabetic tokens of exactly seven characters only",
            "detected_token_count": len(matches), "record_cap": row_cap, "records_omitted": max(0, len(matches) - row_cap),
            "records": rows, "nonmatching_words": "left unchanged; no premise that all words have seven letters"}


def _fact_truth_lens(text: str, context: Optional[str], context_metrics: Optional[dict[str, Any]]) -> dict[str, Any]:
    fact_cues = _word_cue_spans(text, FACT_CUES, "fact_record")
    affect_cues = _word_cue_spans(text, AFFECT_CUES, "reported_affect")
    first_person_affect = span_hits(text, r"(?i:\b(?:i|we)\s+(?:feel|felt|am|was|were|have been)\b[^.!?;]*)", "reported_affect.first_person_statement")
    return {
        "requested_distinction": {
            "fact_coordinate": "explicitly stated or evidenced proposition/record, assessed against a supplied source",
            "felt_truth_coordinate": "self-reported emotional impact, stored separately from proposition verification",
        },
        "fact_record": {"cue_spans": fact_cues, "source_comparison": context_metrics,
                        "verification_status": "unverified by this lexical analysis; requires an authoritative source and claim-level review"},
        "felt_truth": {"affect_cue_spans": affect_cues, "first_person_affect_spans": first_person_affect,
                       "status": "textual self-report cues only; emotion is not treated as proof of a proposition",
                       "logarithmic_emotion_profile": _emotion_log_profile(text)},
        "separation_rule": "Never merge a proposition's evidence status with a speaker's reported emotional response.",
    }


def _motivation_lens(text: str) -> dict[str, Any]:
    survival = _word_cue_spans(text, SURVIVAL_CUES, "motive.survival")
    pleasure = _word_cue_spans(text, PLEASURE_CUES, "motive.pleasure")
    counts = {"survival_cue_occurrences": len(survival), "pleasure_cue_occurrences": len(pleasure)}
    total = sum(counts.values())
    return {
        "survival_cues": survival,
        "pleasure_cues": pleasure,
        "counts": counts,
        "cue_balance": {"survival_share": round(len(survival) / total, 6) if total else None,
                        "pleasure_share": round(len(pleasure) / total, 6) if total else None},
        "co_present": bool(survival and pleasure),
        "interpretation": "lexical mentions in text; actual needs, involuntariness, or motive require independent evidence",
    }


def _lie_deception_lens(text: str) -> dict[str, Any]:
    cues = {name: span_hits(text, pattern, "deception." + name) for name, pattern in DECEPTION_PATTERNS.items()}
    required = ["a specific proposition and authoritative evidence establishing falsity",
                "evidence the speaker knew the proposition was false when stated",
                "evidence of deliberate intent to mislead",
                "evidence identifying the target and supporting the stipulated innocence criterion",
                "evidence supporting intent to harm that target"]
    explicit_lie_words = cues["explicit_lie_or_fabrication_claim"]
    return {
        "operational_definitions": {
            "deception": "observable concealment, omission, or misleading-presentation behavior; classification remains evidence-dependent",
            "lie_under_requested_policy": "a knowingly false statement deliberately made to mislead an innocent target with intent to harm",
        },
        "deception_surface_cues": cues,
        "deception_cue_present": any(cues.values()),
        "explicit_lie_accusation_cues": explicit_lie_words,
        "lie_classification": "UNASSESSED — required evidence is not supplied by cue matching",
        "required_evidence_for_lie_classification": required,
        "interpretation": "a textual cue or accusation records wording; it does not itself establish falsity, knowledge, intent, target status, or harm",
    }



_NUMBER_BODY = r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
_UNIT_ALT = r"%|USD\b|EUR\b|GBP\b|USDT\b|USDC\b|BTC\b|ETH\b|tokens?\b"
_UNIT_STILL_FOLLOWS = r"(?!\s*(?:%|USD\b|EUR\b|GBP\b|USDT\b|USDC\b|BTC\b|ETH\b|tokens?\b))"
_NUMBER_PATTERN = re.compile(
    r"(?<![\w.])(?P<currency>[$€£])?(?P<number>" + _NUMBER_BODY +
    r")(?:\s*(?P<unit>" + _UNIT_ALT + r")(?!\w))?" + _UNIT_STILL_FOLLOWS +
    r"(?!\w|\.(?=\d))",
    re.IGNORECASE,
)
_EQUATION_PATTERN = re.compile(
    r"(?<![\w.])(?P<ca>[$€£])?(?P<a>" + _NUMBER_BODY + r")(?:\s*(?P<ua>" + _UNIT_ALT + r")(?!\w))?"
    + _UNIT_STILL_FOLLOWS +
    r"\s*(?P<op>\+|-|\*|/|plus\b|minus\b|times\b|multiplied by\b|divided by\b)\s*"
    r"(?P<cb>[$€£])?(?P<b>" + _NUMBER_BODY + r")(?:\s*(?P<ub>" + _UNIT_ALT + r")(?!\w))?" + _UNIT_STILL_FOLLOWS +
    r"\s*(?:=|equals?\b)\s*(?P<cc>[$€£])?(?P<c>" + _NUMBER_BODY + r")(?:\s*(?P<uc>" + _UNIT_ALT + r")(?!\w))?" + _UNIT_STILL_FOLLOWS +
    r"(?!\w|\.(?=\d))",
    re.IGNORECASE,
)

def _exact_fraction(raw: str) -> Fraction:
    return Fraction(Decimal(raw.replace(",", "")))


def _fraction_string(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _numbers_in(text: Optional[str]) -> list[dict[str, Any]]:
    if text is None:
        return []
    date_spans = [m.span() for m in re.finditer(r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?Z?)?\b", text)]
    currency_unit = {"$": "USD", "€": "EUR", "£": "GBP"}
    rows = []
    for m in _NUMBER_PATTERN.finditer(text):
        if any(m.start() < end and m.end() > start for start, end in date_spans):
            continue
        try:
            value = _exact_fraction(m.group("number"))
        except (InvalidOperation, ValueError, ZeroDivisionError):
            continue
        symbol, raw_unit = m.group("currency") or "", m.group("unit") or ""
        symbol_unit = currency_unit.get(symbol)
        suffix_unit = "percent" if raw_unit == "%" else raw_unit.upper() if raw_unit else None
        conflict = bool(symbol_unit and suffix_unit and symbol_unit != suffix_unit)
        unit = f"AMBIGUOUS:{symbol_unit}|{suffix_unit}" if conflict else symbol_unit or suffix_unit or "unitless"
        rows.append({"surface": m.group(0), "value_exact": _fraction_string(value), "unit": unit,
                     "unit_conflict": conflict,
                     "start": m.start(), "end": m.end()})
    return rows


def _equations_in(text: str) -> list[dict[str, Any]]:
    rows = []
    for m in _EQUATION_PATTERN.finditer(text):
        try:
            a, b, stated = (_exact_fraction(m.group(k)) for k in ("a", "b", "c"))
        except (InvalidOperation, ValueError, ZeroDivisionError):
            continue
        raw_units = [(m.group(k) or "") for k in ("ua", "ub", "uc")]
        symbols = [(m.group(k) or "") for k in ("ca", "cb", "cc")]
        symbol_units = {"$": "USD", "€": "EUR", "£": "GBP"}
        units, unit_conflicts = [], []
        for suffix, symbol in zip(raw_units, symbols):
            suffix_unit = "percent" if suffix == "%" else suffix.upper() if suffix else None
            symbol_unit = symbol_units.get(symbol)
            conflict = bool(symbol_unit and suffix_unit and symbol_unit != suffix_unit)
            unit_conflicts.append(conflict)
            units.append(f"AMBIGUOUS:{symbol_unit}|{suffix_unit}" if conflict else symbol_unit or suffix_unit or "unitless")
        op = m.group("op").lower()
        op = {"plus": "+", "minus": "-", "times": "*", "multiplied by": "*", "divided by": "/"}.get(op, op)
        supported, reason, calculated = True, "", None
        if any(unit_conflicts):
            supported, reason = False, "currency symbol conflicts with explicit unit label"
        elif op in {"+", "-"}:
            if units[0] != units[1] or units[0] != units[2]:
                supported, reason = False, "addition/subtraction requires matching explicit units"
            else:
                calculated = a + b if op == "+" else a - b
        elif any(units):
            supported, reason = False, "multiplication/division is evaluated only for unitless values"
        elif op == "*":
            calculated = a * b
        elif op == "/":
            if b == 0:
                supported, reason = False, "division by zero"
            else:
                calculated = a / b
        matched = bool(supported and calculated == stated)
        rows.append({"surface": m.group(0), "operands_exact": [_fraction_string(a), _fraction_string(b)],
                     "operator": op, "stated_result_exact": _fraction_string(stated), "units": units,
                     "currency_symbols": symbols, "unit_conflicts": unit_conflicts,
                     "computed_result_exact": _fraction_string(calculated) if calculated is not None else None,
                     "supported_operation": supported, "arithmetic_match": matched,
                     "assessment": "exact rational arithmetic match" if matched else reason or "computed result differs from stated result",
                     "start": m.start(), "end": m.end()})
    return rows


def _arithmetic_fact_truth_lens(claim: str, context: Optional[str]) -> dict[str, Any]:
    claim_numbers, source_numbers = _numbers_in(claim), _numbers_in(context)
    claim_counts = collections.Counter((r["value_exact"], r["unit"]) for r in claim_numbers)
    source_counts = collections.Counter((r["value_exact"], r["unit"]) for r in source_numbers)
    matched = claim_counts & source_counts
    n_match = sum(matched.values())
    claim_extra, source_extra = claim_counts - matched, source_counts - matched
    def extras(rows: list[dict[str, Any]], counter: collections.Counter) -> list[dict[str, Any]]:
        result = []
        for row in rows:
            key = (row["value_exact"], row["unit"])
            if counter[key]:
                result.append(row)
                counter[key] -= 1
        return result
    precision = n_match / len(claim_numbers) if claim_numbers else None
    recall = n_match / len(source_numbers) if context is not None and source_numbers else None
    f1 = 2 * precision * recall / (precision + recall) if precision is not None and recall is not None and precision + recall else None
    return {
        "mathematical_facts": {"numeric_records": claim_numbers, "equation_records": _equations_in(claim),
                               "arithmetic": "exact rational evaluation from base-10 decimal strings; same-unit addition/subtraction; unitless multiplication/division; percent interpreted as displayed percentage points"},
        "arithmetic_truth": {"source_status": "SOURCE_REQUIRED" if context is None else "COMPARED",
                             "exact_value_unit_multiset_matches": n_match if context is not None else None,
                             "claim_count": len(claim_numbers), "source_count": len(source_numbers) if context is not None else None,
                             "precision": round(precision, 6) if precision is not None else None,
                             "recall": round(recall, 6) if recall is not None else None,
                             "f1": round(f1, 6) if f1 is not None else None,
                             "metrics_formula": "multiset exact (value,unit) matches; precision=matches/claim numeric records; recall=matches/source numeric records; F1=harmonic mean",
                             "claim_values_absent_from_source": extras(claim_numbers, claim_extra) if context is not None else None,
                             "source_values_absent_from_claim": extras(source_numbers, source_extra) if context is not None else None,
                             "interpretation": "numeric concordance against the supplied text and arithmetic consistency checks; no complete truth verdict"},
    }


def _emotion_log_profile(text: str) -> dict[str, Any]:
    output = {}
    for family, words in EMOTION_LEXICONS.items():
        hits = _word_cue_spans(text, words, "emotion." + family)
        output[family] = {"cue_count": len(hits), "ln_1_plus_count": round(math.log1p(len(hits)), 6), "spans": hits}
    return {"families": output, "formula": "E_f = ln(1+n_f), where n_f is the configured lexical cue count",
            "meaning": "logarithmically scaled word-cue frequency; it does not measure a person's inner emotional intensity"}


def _thought_matrix_lattice(text: str) -> dict[str, Any]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]
    rows = []
    for index, sentence in enumerate(sentences, 1):
        cues = {
            "numeric_fact": _numbers_in(sentence),
            "reported_affect": [h for terms in EMOTION_LEXICONS.values() for h in _word_cue_spans(sentence, terms, "matrix.affect")],
            "survival": _word_cue_spans(sentence, SURVIVAL_CUES, "matrix.survival"),
            "pleasure": _word_cue_spans(sentence, PLEASURE_CUES, "matrix.pleasure"),
            "deception_cue": [h for pat in DECEPTION_PATTERNS.values() for h in span_hits(sentence, pat, "matrix.deception")],
            "intention_cue": [h for pat in INTENTION_PATTERNS.values() for h in span_hits(sentence, pat, "matrix.intention")],
            "rhetoric_cue": [h for pat in RHETORIC_PATTERNS.values() for h in span_hits(sentence, pat, "matrix.rhetoric")],
            "embellishment_cue": [h for term in EMBELLISHMENT for h in span_hits(sentence, r"(?i:\b" + re.escape(term) + r"\b)", "matrix.embellishment")],
        }
        active = [name for name in THOUGHT_FEATURES if cues[name]]
        rows.append({"sentence_index": index, "feature_vector": [int(name in active) for name in THOUGHT_FEATURES],
                     "active_families": active, "evidence_by_family": cues})
    rank_counts = {str(k): math.comb(len(THOUGHT_FEATURES), k) for k in range(len(THOUGHT_FEATURES)+1)}
    return {"feature_columns": THOUGHT_FEATURES, "sentence_matrix_rows": rows,
            "boolean_lattice": {"ground_set": THOUGHT_FEATURES, "node_count": 2 ** len(THOUGHT_FEATURES),
                                "rank_counts": rank_counts, "meet": "set intersection", "join": "set union",
                                "represented_nodes": "all feature subsets are defined by the ground set; materialized on demand",
                                "interpretation": "formal lattice of observed text-cue combinations, not hidden thoughts or motives"}}


def _cultural_annotations(text: str, profile: str) -> dict[str, Any]:
    if profile == "none":
        return {"profile": profile, "phrase_hits": [], "candidate_ligatures": [],
                "input_mutated": False, "operation": "annotation only; original text remains the analyzed source"}
    phrases = CULTURAL_APERTURES[profile]
    hits = []
    for phrase in phrases:
        for hit in span_hits(text, r"(?i:\b" + re.escape(phrase) + r"\b)", "culture." + profile + ".phrase"):
            hits.append({**hit, "phrase": phrase, "candidate_ligature": LIGATURE_MAP.get(phrase),
                         "mapping_status": "candidate_for_review" if phrase in LIGATURE_MAP else "unmapped_surface_phrase"})
    hits.sort(key=lambda h: (h["start"], h["end"]))
    return {"profile": profile, "phrase_hits": hits,
            "candidate_ligatures": [h for h in hits if h["candidate_ligature"]],
            "aperture_policy": "tag and count selected regional phrases; preserve original text and all hits",
            "input_mutated": False,
            "mapping_policy": "ligatures are reviewable lexical hypotheses, not validated synonymy or a truth conversion"}


def _parse_csv(value: Optional[str]) -> Optional[list[str]]:
    if value is None:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def _self_test() -> dict[str, Any]:
    import unittest

    class PrimeTests(unittest.TestCase):
        def test_empty_input_is_empty_and_not_injected(self):
            result = run_omni_analysis("", domain="crypto")
            self.assertEqual(result["status"], "EMPTY")
            self.assertEqual(result["base_sensors"]["token_count"], 0)
            self.assertEqual(result["token_chain"]["adjacent_pair_count"], 0)
        def test_d1_fallback_is_finite(self):
            result = run_omni_analysis("verified", domain="crypto")
            self.assertTrue(math.isfinite(result["base_sensors"]["T_d"]))
        def test_projection_and_frame_gap_are_separate(self):
            result = run_omni_analysis("We may launch BTC on Ethereum in Q3, pending audit.", domain="crypto",
                                       frame=["actor", "action", "asset", "chain", "amount", "timing", "contract_address"],
                                       recorded_fields=["actor", "action"])
            projection = result["domain_projection"]
            self.assertIn("actor", projection["recorded_projection_R"])
            self.assertIn("asset", projection["measurement_residual_u"])
            self.assertIn("amount", projection["frame_gaps"])
            self.assertIn("contract_address", projection["frame_gaps"])
            self.assertGreater(projection["frame_coverage"], 0)
        def test_spans_refer_to_exact_original_text(self):
            text = "We may launch BTC on Ethereum in Q3, pending audit."
            result = run_omni_analysis(text, domain="crypto")
            hit = result["paired_lenses"]["said"]["domain_field_spans"]["asset"][0]
            self.assertEqual(text[hit["start"]:hit["end"]], hit["text"])
        def test_crypto_amount_and_quarter_spans(self):
            text = "Agency proposed a 5% BTC allocation for Q3, subject to approval."
            result = run_omni_analysis(text, domain="crypto")
            fields = result["paired_lenses"]["said"]["domain_field_spans"]
            self.assertEqual(fields["amount"][0]["text"], "5%")
            self.assertEqual(fields["timing"][0]["text"], "Q3")
        def test_d_one_uses_finite_fallback(self):
            result = run_omni_analysis("possibly", domain="crypto")
            self.assertEqual(result["base_sensors"]["evasion_count_D"], 1)
            self.assertTrue(math.isfinite(result["base_sensors"]["T_d"]))
        def test_receipt_changes_when_input_changes(self):
            a = run_omni_analysis("approved", domain="crypto")["receipt"]["input_sha256"]
            b = run_omni_analysis("denied", domain="crypto")["receipt"]["input_sha256"]
            self.assertNotEqual(a, b)
        def test_context_overlap_is_lexical_and_bounded(self):
            result = run_omni_analysis("BTC BTC rose", context="BTC fell", domain="crypto")
            self.assertEqual(result["context_overlap"]["shared_token_occurrences"], 1)
        def test_quality_quantity_metrics_remain_separate_and_bounded(self):
            result = run_omni_analysis("BTC rises. BTC rises sharply.", domain="crypto", context="BTC rises")
            profile = result["quality_quantity_dynamics"]
            self.assertEqual(profile["quantity"]["word_tokens"], 5)
            self.assertIsNone(profile.get("overall_quality_score"))
            self.assertGreaterEqual(profile["quality_proxies"]["content_token_variety"]["value"], 0)
            self.assertLessEqual(profile["quality_proxies"]["content_token_variety"]["value"], 1)
            self.assertIsNotNone(profile["quality_proxies"]["source_overlap"])
        def test_repeated_sentences_keep_their_own_source_offsets(self):
            result = run_omni_analysis("Agency proposed. Agency proposed.", domain="crypto")
            dynamics = result["quality_quantity_dynamics"]["sentence_order_dynamics"]
            self.assertEqual(len(dynamics), 2)
            self.assertEqual(dynamics[0]["cumulative_frame_fields_observed"], 2)
            self.assertEqual(dynamics[1]["cumulative_frame_fields_observed"], 2)
        def test_rhyme_and_rhythm_are_measured_in_sentence_order(self):
            result = run_omni_analysis("The cat sat. The bat fat.", domain="crypto")
            profile = result["quality_quantity_dynamics"]
            self.assertEqual(profile["rhythm"]["sentence_token_counts"], [3, 3])
            self.assertEqual(profile["rhyme"]["orthographic_rhyme_pairs_distinct_end_words"], 1)
            self.assertEqual(profile["rhyme"]["scheme"], ["A", "A"])
            self.assertEqual(profile["sentence_order_dynamics"][-1]["sentence_index"], 2)
        def test_fact_and_reported_affect_are_separate(self):
            result = run_omni_analysis("I know the report says 5%. I feel hurt by the claim.", domain="crypto", context="The report says 5%.")
            lens = result["fact_truth_motivation_lie_deception_lenses"]["fact_vs_felt_truth"]
            self.assertEqual(lens["fact_record"]["verification_status"].split(";")[0], "unverified by this lexical analysis")
            self.assertTrue(lens["felt_truth"]["first_person_affect_spans"])
            self.assertTrue(lens["fact_record"]["cue_spans"])
        def test_pleasure_and_survival_lexicons_balance_separately(self):
            result = run_omni_analysis("Safety and food protect survival; joy and comfort bring pleasure.", domain="crypto")
            lens = result["fact_truth_motivation_lie_deception_lenses"]["pleasure_vs_survival"]
            self.assertTrue(lens["co_present"])
            self.assertAlmostEqual(lens["cue_balance"]["survival_share"] + lens["cue_balance"]["pleasure_share"], 1.0)
        def test_deception_cues_do_not_auto_classify_lie(self):
            result = run_omni_analysis("The report concealed a fact and someone called it a lie.", domain="crypto")
            lens = result["fact_truth_motivation_lie_deception_lenses"]["deception_vs_lie"]
            self.assertTrue(lens["deception_cue_present"])
            self.assertTrue(lens["explicit_lie_accusation_cues"])
            self.assertTrue(lens["lie_classification"].startswith("UNASSESSED"))
            self.assertEqual(len(lens["required_evidence_for_lie_classification"]), 5)
        def test_systemic_root_frame_finds_named_patterns_as_surface_cues(self):
            text = "Use delegatecall with a proxy and latestRoundData; execute timelock through bridge."
            result = run_omni_analysis(text, domain="systemic_root")
            fields = result["paired_lenses"]["said"]["domain_field_spans"]
            self.assertTrue(fields["cascading_dependency"])
            self.assertTrue(fields["oracle_influence"])
            self.assertTrue(fields["governance_override"])
            self.assertTrue(fields["cross_chain_vector"])
        def test_cultural_aperture_annotates_without_rewriting(self):
            text = "Circle back after the vetted protocol review."
            result = run_omni_analysis(text, domain="crypto", culture="anglo_corporate")
            profile = result["cultural_aperture_and_ligature_annotations"]
            self.assertFalse(profile["input_mutated"])
            self.assertEqual(text[profile["phrase_hits"][0]["start"]:profile["phrase_hits"][0]["end"]], "Circle back")
            self.assertEqual(profile["candidate_ligatures"][0]["candidate_ligature"], "postpone")
        def test_exact_arithmetic_facts_and_numeric_source_matching(self):
            result = run_omni_analysis("Reserve 5 BTC; 5 + 2 = 7.", context="Reserve 5 BTC; budget 20 USD.", domain="crypto")
            audit = result["arithmetic_truth_and_mathematical_facts"]
            self.assertEqual(audit["arithmetic_truth"]["precision"], 0.25)
            self.assertEqual(audit["arithmetic_truth"]["recall"], 0.5)
            self.assertEqual(audit["mathematical_facts"]["numeric_records"][-1]["value_exact"], "7")
            self.assertTrue(audit["mathematical_facts"]["equation_records"][0]["arithmetic_match"])
        def test_numeric_units_survive_trailing_punctuation(self):
            rows = _numbers_in("Total: 20 USD. Then 5%.")
            self.assertEqual([(row["value_exact"], row["unit"]) for row in rows], [("20", "USD"), ("5", "percent")])
            eq = _equations_in("5 BTC + 2 BTC = 7 BTC.")
            self.assertEqual(len(eq), 1)
            self.assertTrue(eq[0]["arithmetic_match"])
        def test_currency_symbol_arithmetic_and_conflicting_units(self):
            equation = _equations_in("$5 + $2 = $7.")[0]
            self.assertTrue(equation["arithmetic_match"])
            self.assertEqual(equation["units"], ["USD", "USD", "USD"])
            conflicted = _equations_in("$5 EUR + $2 EUR = $7 EUR")[0]
            self.assertFalse(conflicted["supported_operation"])
            self.assertTrue(_numbers_in("$5 EUR")[0]["unit_conflict"])
        def test_direct_api_rejects_oversize_text(self):
            with self.assertRaises(ValueError):
                run_omni_analysis("x" * (MAX_TEXT_BYTES + 1))
        def test_custom_domain_is_literal_only_and_bounded(self):
            profile = {"name": "clinic_intake", "fields": {"requested_action": ["send [report]", "review form"]}}
            result = run_omni_analysis("Send [report] after review form.", custom_domain=profile)
            spans = result["paired_lenses"]["said"]["domain_field_spans"]["requested_action"]
            self.assertEqual([row["text"] for row in spans], ["Send [report]", "review form"])
            self.assertEqual(result["scope"]["domain"], "clinic_intake")
            with self.assertRaises(ValueError):
                _custom_domain_patterns({"name": "x", "fields": {"bad": [""]}})
        def test_unsigned_receipt_verifies_integrity_and_detects_tampering(self):
            report = run_omni_analysis("A report says 5%.", domain="crypto")
            self.assertTrue(verify_report(report, b"A report says 5%.")["report_integrity_valid"])
            self.assertTrue(verify_report(report, b"A report says 5%.")["input_source_match"])
            self.assertFalse(verify_report(report, b"changed")["input_source_match"])
            changed = dict(report)
            changed["status"] = "ALTERED"
            self.assertFalse(verify_report(changed)["report_integrity_valid"])
        def test_market_readiness_output_does_not_claim_validation(self):
            report = run_omni_analysis("A proxy calls delegatecall.", domain="systemic_root")
            readiness = report["market_readiness"]
            self.assertEqual(readiness["maturity"], "research prototype; not production-certified")
            self.assertTrue(any("contract safety" in item for item in readiness["not_established"]))
        def test_fraction_arithmetic_does_not_round_into_match(self):
            row = _equations_in("1 / 3 = 0.3333333333333333333333333333")[0]
            self.assertFalse(row["arithmetic_match"])
        def test_mixed_units_do_not_pass_as_valid_addition(self):
            row = _equations_in("5 BTC + 2 USD = 7 BTC")[0]
            self.assertFalse(row["supported_operation"])
            self.assertFalse(row["arithmetic_match"])
        def test_log_emotion_formula_counts_language_cues(self):
            result = run_omni_analysis("I feel hurt, hurt, and afraid.", domain="crypto")
            prof = result["fact_truth_motivation_lie_deception_lenses"]["fact_vs_felt_truth"]["felt_truth"]["logarithmic_emotion_profile"]
            self.assertEqual(prof["families"]["pain_distress"]["cue_count"], 3)
            self.assertAlmostEqual(prof["families"]["pain_distress"]["ln_1_plus_count"], math.log1p(3), places=5)
        def test_feature_matrix_and_boolean_lattice(self):
            result = run_omni_analysis("I feel joy. We protect safety with a guaranteed 5% plan.", domain="crypto")
            profile = result["algorithmic_thought_matrix_and_boolean_lattice"]
            self.assertEqual(profile["boolean_lattice"]["node_count"], 256)
            self.assertEqual(len(profile["sentence_matrix_rows"]), 2)
            self.assertEqual(len(profile["sentence_matrix_rows"][0]["feature_vector"]), 8)
        def test_fact_affect_sentence_table_keeps_axes_separate(self):
            table = run_omni_analysis("Fact recorded. I feel hurt.")["fact_truth_motivation_lie_deception_lenses"]["fact_vs_felt_truth"]["sentence_cooccurrence_table"]
            self.assertEqual(table["cell_counts"], {"neither": 0, "fact_only": 1, "affect_only": 1, "both": 0})
            self.assertEqual(table["matrix"], [[0, 1], [1, 0]])
        def test_law_rule_ratio_is_lexical_not_legal_judgment(self):
            lens = run_omni_analysis("The law sets rules.")["law_rule_polarity_lexicon_lens"]
            self.assertEqual(lens["counts"], {"law": 1, "rule": 1})
            self.assertEqual(lens["law_to_rule_count_ratio"], 1.0)
            self.assertIn("not legal hierarchy", lens["interpretation"])
        def test_four_axis_quaternion_and_boolean_lattice(self):
            lens = run_omni_analysis("Meaning purpose thought joy.")["four_part_awareness_quaternion_and_quadratic_lattice"]
            self.assertEqual(lens["cue_counts"], {"meaning": 1, "purpose": 1, "thought": 1, "emotion": 1})
            self.assertEqual(lens["boolean_quadratic_lattice"]["possible_nodes"], 16)
            self.assertEqual(lens["boolean_quadratic_lattice"]["observed_nodes"], 1)
            q = lens["quaternionic_cue_encoding"]["normalized_components"]
            self.assertAlmostEqual(sum(x*x for x in q), 1.0)
            self.assertEqual(len(lens["quaternionic_cue_encoding"]["left_multiplication_matrix"]), 4)
            self.assertIn("not a measurement of awareness", lens["quaternionic_cue_encoding"]["interpretation"])
        def test_seven_letter_reversal_and_midpoint_are_finite(self):
            lens = run_omni_analysis("Abcdefg is here.")["seven_letter_inversion_and_interpolation"]
            row = lens["records"][0]
            self.assertEqual(row["reversed_spelling"], "gfedcbA")
            self.assertEqual(row["reversal_permutation_1_based"], [7, 6, 5, 4, 3, 2, 1])
            self.assertEqual(len(row["midpoint_codepoint_numerators_over_2"]), 7)
            self.assertEqual(lens["detected_token_count"], 1)
        def test_meaning_purpose_polarity_pairs_are_curated_observables(self):
            lens = run_omni_analysis("Meaning is clear and ambiguous; purpose can support or oppose.")["meaning_purpose_polarity_tables"]
            meaning_pair = next(item for item in lens["meaning_polarities"]["pairs"] if item["curated_pair"] == ["clear", "ambiguous"])
            purpose_pair = next(item for item in lens["purpose_polarities"]["pairs"] if item["curated_pair"] == ["support", "oppose"])
            self.assertEqual(meaning_pair["sentences_with_both"], 1)
            self.assertEqual(purpose_pair["sentences_with_both"], 1)
            self.assertIn("not a universal", meaning_pair["status"])
            lattice = lens["meaning_purpose_boolean_quadratic_lattice"]
            self.assertEqual(lattice["possible_nodes"], 4)
            self.assertTrue(lattice["diagonal_idempotence_holds_by_construction"])
            self.assertTrue(lens["metapragmatic_aperture"]["configured_cue_spans"])
        def test_sensory_lexicons_are_exactly_twenty_and_form_tables(self):
            self.assertEqual(len(OPTICAL_LEXICON), 20)
            self.assertEqual(len(AUDITORY_LEXICON), 20)
            self.assertEqual(len(PROFUNDITY_CUES), 10)
            self.assertEqual(len(PERCEPTION_CUES), 10)
            lens = run_omni_analysis("The lens has contrast. Sound has pitch.")["sensory_lexicon_polarity_tables"]
            table = lens["optical_auditory_dichotomy_table"]
            self.assertEqual(table["optical_cue_count"], 2)
            self.assertEqual(table["auditory_cue_count"], 2)
            self.assertEqual(table["cell_counts"]["optical_only"], 1)
            self.assertEqual(table["cell_counts"]["auditory_only"], 1)
        def test_profundity_perception_balance_table(self):
            lens = run_omni_analysis("Profound perception can discern layers.")["sensory_lexicon_polarity_tables"]["profundity_perception_dichotomy_table"]
            self.assertEqual(lens["profundity_count"], 1)
            self.assertEqual(lens["perception_count"], 2)
            self.assertEqual(lens["cell_counts"]["both"], 1)
        def test_sensor_metadata_exact_arithmetic_and_20_20_reference(self):
            metadata = {"captured_at_utc": "2026-10-30T12:00:00Z", "measurement_source": "test fixture", "device_class": "illustrative",
                        "visual": {"width_px": 1920, "height_px": 1080, "acuity_snellen": "20/20"},
                        "audio": {"sample_rate_hz": 48000, "channels": 2, "bit_depth": 24, "duration_ms": 1000,
                                  "rms_dbfs": -20.0, "peak_dbfs": -3.0}}
            aperture = run_omni_analysis("sample", sensory_metadata=metadata)["sensory_metadata_aperture"]
            self.assertEqual(aperture["optical_measurements"]["pixel_count"], 2073600)
            self.assertEqual(aperture["optical_measurements"]["reported_snellen_fraction"], "1")
            self.assertTrue(aperture["arithmetic_and_consistency"]["snellen_is_20_20"])
            self.assertEqual(aperture["auditory_measurements"]["nominal_uncompressed_bitrate_bps"], 2304000)
            self.assertEqual(aperture["auditory_measurements"]["sample_frames_per_channel_exact"], "48000")
            self.assertEqual(_validate_sensory_metadata({"audio": {"clipping_fraction": 0.0}})["audio"]["clipping_fraction"], 0.0)
        def test_sensor_metadata_validation_fails_closed(self):
            with self.assertRaises(ValueError):
                _validate_sensory_metadata({"visual": {"width_px": True}})
            with self.assertRaises(ValueError):
                _validate_sensory_metadata({"audio": {"rms_dbfs": -2, "peak_dbfs": -5}})
            with self.assertRaises(ValueError):
                _validate_sensory_metadata({"visual": {"acuity_snellen": "20/0"}})
            with self.assertRaises(ValueError):
                _validate_sensory_metadata({"visual": {"camera_secret": "x"}})
        def test_opt_in_performance_profile_is_hashed_and_default_omits_timing(self):
            plain = run_omni_analysis("sample")
            self.assertNotIn("runtime_performance_profile", plain)
            profile = run_omni_analysis("sample", include_performance=True)
            self.assertGreaterEqual(profile["runtime_performance_profile"]["elapsed_ms"], 0)
            self.assertTrue(verify_report(profile)["report_integrity_valid"])
        def test_term_catalog_records_are_bounded_and_formula_labels_corrected(self):
            report = run_omni_analysis("A word is measured.")
            lens = report["terminology_consistency_audit"]
            self.assertEqual(lens["term_count"], 4)
            self.assertEqual(lens["records"][0]["name"], "tokenization")
            self.assertIn("not a calibrated dependability", lens["formula_review"]["dependability"])
            self.assertIn("Jaccard distance", lens["formula_review"]["proposed_reliability"])
            self.assertIn("no source reference supplied", lens["records"][0]["etymology"]["source_status"])
            self.assertTrue(verify_report(report)["report_integrity_valid"])
        def test_term_jaccard_distance_is_exact_and_not_named_reliability(self):
            lens = _term_catalog_lens()
            by_name = {row["name"]: row for row in lens["records"]}
            distance = by_name["definition"]["antonym_denotation_separation"]
            self.assertEqual(distance["exact_fraction"], "2/3")
            self.assertIn("not antonym quality", distance["interpretation"])
            self.assertEqual(by_name["tokenization"]["antonym_denotation_separation"]["exact_fraction"], None)
        def test_term_profile_reports_missing_references_and_unknown_antonym(self):
            profile = {"definitions": ["known"], "terms": [{"register": "observation", "name": "sample",
                "etymology": {"root": "unknown"}, "denotation": ["missing"], "connotation": "sample gloss",
                "antonym": "absent"}]}
            row = _term_catalog_lens(profile)["records"][0]
            self.assertEqual(row["denotation_reference_check"]["unresolved"], ["missing"])
            self.assertEqual(row["dependability_index"]["value"], 0)
            self.assertIsNone(row["antonym_denotation_separation"]["exact_fraction"])
        def test_term_profile_schema_rejects_duplicate_names(self):
            row = {"register": "definition", "name": "sample", "etymology": {}, "denotation": [],
                   "connotation": "gloss", "antonym": "none"}
            with self.assertRaises(ValueError):
                _term_catalog_objects({"definitions": [], "terms": [row, dict(row)]})
        def test_permutation_fidelity_4cycle_invariants_are_exact(self):
            profile = {"ground_set": ["numeric_fact", "reported_affect", "survival", "pleasure"],
                       "permutation": [1, 2, 3, 0],
                       "perception": {"modality": "optical", "received": [1, 1, 0, 1],
                                      "reference_count": 4, "matched_count": 3}}
            lens = _profundity_perception_lens(profile)
            prof = lens["profundity_proxy"]
            self.assertEqual(prof["symmetric_group_space_size_factorial"], 24)
            self.assertEqual(prof["permutation_sign"], -1)
            self.assertEqual(prof["cycle_count_orbits"], 1)
            self.assertEqual(prof["fixed_point_indices"], [])
            self.assertEqual(prof["permutation_order_lcm_cycle_lengths"], 4)
            self.assertEqual(prof["movement_density_exact"], "1")
            self.assertEqual(lens["perception_proxy"]["fidelity_exact"], "3/4")
            self.assertIn("caller-reported", lens["perception_proxy"]["evidence_basis"])
            self.assertTrue(lens["admissible_under_declared_checks"])
        def test_reference_values_verify_positional_matches(self):
            profile = {"ground_set": ["a", "b"], "permutation": [1, 0],
                       "perception": {"modality": "auditory", "received": ["x", "y"],
                                      "reference_count": 2, "matched_count": 1,
                                      "reference_values": ["x", "z"]}}
            lens = _profundity_perception_lens(profile)
            self.assertIn("verified by exact positional", lens["perception_proxy"]["evidence_basis"])
            with self.assertRaises(ValueError):
                _validate_dichotomy_profile({**profile, "perception": {**profile["perception"], "matched_count": 2}})
        def test_permutation_validation_rejects_duplicates_and_non_bijections(self):
            base = {"ground_set": ["a", "b"], "permutation": [0, 0],
                    "perception": {"modality": "optical", "received": [1], "reference_count": 1, "matched_count": 0}}
            with self.assertRaises(ValueError):
                _validate_dichotomy_profile(base)
            base["permutation"] = [0, 1]
            base["ground_set"] = ["a", "a"]
            with self.assertRaises(ValueError):
                _validate_dichotomy_profile(base)
        def test_empty_perception_reference_is_undefined_and_inadmissible(self):
            profile = {"ground_set": ["a", "b"], "permutation": [0, 1],
                       "perception": {"modality": "optical", "received": [], "reference_count": 0, "matched_count": 0}}
            lens = _profundity_perception_lens(profile)
            self.assertIsNone(lens["perception_proxy"]["fidelity_exact"])
            self.assertFalse(lens["admissible_under_declared_checks"])
        def test_dichotomy_profile_size_and_sample_bounds(self):
            too_many = {"ground_set": [str(i) for i in range(13)], "permutation": list(range(13)),
                        "perception": {"modality": "optical", "received": [], "reference_count": 0, "matched_count": 0}}
            with self.assertRaises(ValueError):
                _validate_dichotomy_profile(too_many)
        def test_word_dynamics_ledger_preserves_offsets_and_exact_letter_math(self):
            text = "Approved pleasure. denied safe."
            report = _word_dynamics_lens(text)
            rows = report["words"]
            self.assertEqual([text[row["start"]:row["end"]] for row in rows], [row["surface"] for row in rows])
            approved = rows[0]
            self.assertEqual(approved["letter_sum"], sum(map(ord, "approved")))
            self.assertEqual(approved["polarity_side"], "left")
            self.assertEqual(approved["polarity_balance_exact"], "-1")
            self.assertTrue(rows[1]["pleasure_cue"])
            self.assertEqual(rows[1]["pleasure_survival_balance_exact"], "1")
            self.assertEqual(rows[2]["polarity_side"], "right")
            self.assertEqual(rows[3]["pleasure_survival_balance_exact"], "0")
        def test_word_slot_permutation_is_bijective_and_links_opposites(self):
            report = _word_dynamics_lens("approved denied")
            perm = report["permutation"]
            self.assertEqual(sorted(perm["mapping_zero_based"]), list(range(perm["slot_count"])))
            self.assertEqual(perm["sign"], -1)
            self.assertEqual(len(perm["cross_polarity_links"]), 1)
            self.assertEqual(perm["cross_polarity_links"][0]["pair"], ["approved", "denied"])
            self.assertEqual(perm["cycle_count"], 1)
        def test_word_dynamics_empty_and_single_word_are_bounded(self):
            empty = _word_dynamics_lens("")
            self.assertEqual(empty["word_count"], 0)
            self.assertEqual(empty["permutation"]["mapping_zero_based"], [])
            single = _word_dynamics_lens("123")
            self.assertEqual(single["words"][0]["letter_sum"], 0)
            self.assertEqual(single["words"][0]["position"], "only")
        def test_word_dynamics_rejects_more_than_128_tokens(self):
            with self.assertRaises(ValueError):
                _word_dynamics_lens("x " * 129)
        def test_word_dynamics_output_is_integrated_and_report_hashes(self):
            report = run_omni_analysis("approved denied", include_word_dynamics=True)
            self.assertTrue(report["per_word_dynamics_and_slot_permutation"]["configured"])
            self.assertTrue(verify_report(report)["report_integrity_valid"])
            self.assertFalse(run_omni_analysis("approved")["per_word_dynamics_and_slot_permutation"]["configured"])

        def test_logical_action_spans_weights_and_compound_overlap(self):
            text = "If not approved, the plan may suggest a delay; however, all records are due by Friday."
            lens = _logical_action_lens(text)
            for hit in lens["source_spans"]:
                self.assertEqual(text[hit["start"]:hit["end"]], hit["text"])
                self.assertTrue(hit["source_slice_matches"])
            classes = {hit["class"] for hit in lens["source_spans"]}
            for expected in ("CONDITION", "NEGATION", "MODALITY_TENTATIVE", "CONTRAST", "QUANTIFIER", "TEMPORAL_BOUND", "ASSERTION", "HEDGE"):
                self.assertIn(expected, classes)
            self.assertTrue(any(h["class"] == "HEDGE" and h["text"].lower() == "may suggest" for h in lens["source_spans"]))
            compound = _logical_action_lens("No more than 3-of-5 tokens may pass.")
            self.assertIn(("QUANTIFIER", "No more than"), {(h["class"], h["text"]) for h in compound["source_spans"]})
            self.assertIn(("QUANTIFIER", "3-of-5"), {(h["class"], h["text"]) for h in compound["source_spans"]})
            self.assertIn(("NEGATION", "No"), {(h["class"], h["text"]) for h in compound["source_spans"]})
        def test_logical_action_reference_diff_and_recoverable_budget(self):
            v1 = "A multisig needs 3-of-5 approval for 180 days after review."
            v2 = "A multisig needs approval after review."
            lens = _logical_action_lens(v2, v1, target_words=40)
            self.assertTrue(any(row["phrase"] == "3-of-5" for row in lens["reference_comparison"]["reference_only_cues"]))
            self.assertTrue(all(row["recoverable"] for row in lens["reference_comparison"]["reference_only_cues"]))
            self.assertEqual(lens["ranked_index"]["word_budget"], 40)
            self.assertIn("not an optimal summary", lens["ranked_index"]["objective"])
            reverse = _logical_action_lens(v1, v2)
            self.assertTrue(any(row["phrase"] == "3-of-5" for row in reverse["reference_comparison"]["current_only_cues"]))
            overflow = _logical_action_lens("not " * 2200, "not " * 2201)
            self.assertEqual(overflow["reference_comparison"]["reference_only_occurrence_total"], 1)
            self.assertEqual(overflow["reference_comparison"]["reference_only_cues"][0]["occurrences"], 1)
        def test_logical_action_hit_bounds_and_budget_validation(self):
            lens = _logical_action_lens("not " * 2200)
            self.assertTrue(lens["hits_truncated"])
            self.assertLessEqual(lens["hits_returned"], MAX_LOGICAL_ACTION_HITS)
            with self.assertRaises(ValueError):
                _logical_action_lens("not", target_words=0)
            with self.assertRaises(ValueError):
                run_omni_analysis("not", logical_action_word_budget=40)
        def test_logical_action_integrates_as_opt_in_and_report_receipt(self):
            report = run_omni_analysis("If not approved, wait.", include_logical_actions=True, logical_action_word_budget=40)
            self.assertTrue(report["logical_action_cue_ledger_and_ranked_index"]["source_spans"])
            self.assertTrue(verify_report(report)["report_integrity_valid"])
            self.assertFalse(run_omni_analysis("approved")["logical_action_cue_ledger_and_ranked_index"]["configured"])

        def test_unknown_recorded_field_rejected(self):
            with self.assertRaises(ValueError):
                run_omni_analysis("hello", domain="crypto", recorded_fields=["mind"])
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PrimeTests)
    result = unittest.TestResult()
    suite.run(result)
    details = {"tests_run": result.testsRun, "failures": [str(x[1]) for x in result.failures],
               "errors": [str(x[1]) for x in result.errors]}
    details["passed"] = result.wasSuccessful()
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description="PRIME 6.7: bounded text, logical-action, terminology, word-dynamics, permutation-fidelity, arithmetic, and sensory-metadata review")
    parser.add_argument("--text", help="text to analyze; an explicitly empty string returns EMPTY")
    parser.add_argument("--text-file", help="UTF-8 source text file")
    parser.add_argument("--context", help="optional comparison text for lexical overlap only")
    parser.add_argument("--context-file", help="optional UTF-8 context file")
    parser.add_argument("--domain", choices=sorted(DOMAIN_PATTERNS), default="crypto")
    parser.add_argument("--domain-config", help="UTF-8 JSON with {name, fields}; fields map names to literal phrase lists (no regex/code)")
    parser.add_argument("--culture", choices=CULTURAL_CHOICES, default="none", help="annotate one regional phrase profile without rewriting source")
    parser.add_argument("--sensory-metadata-file", help="bounded UTF-8 JSON with caller-provided visual/audio metadata; does not capture media")
    parser.add_argument("--term-catalog-file", help="bounded UTF-8 JSON with caller-declared terms/definition references; no code execution or source verification")
    parser.add_argument("--dichotomy-file", help="bounded UTF-8 JSON with finite permutation and optical/auditory reference-sample counts")
    parser.add_argument("--word-dynamics", action="store_true", help="include per-token arithmetic/cue records and a bounded slot permutation (max 128 tokens)")
    parser.add_argument("--logical-actions", action="store_true", help="include source-linked logical-action cue spans and an optional ranked index")
    parser.add_argument("--logical-action-word-budget", type=int, help="optional ranked-index word budget (1-10000); requires --logical-actions")
    parser.add_argument("--profile-performance", action="store_true", help="include a local single-run timing observation")
    parser.add_argument("--frame", help="comma-separated checklist fields; defaults to the domain frame")
    parser.add_argument("--recorded-fields", help="comma-separated projection-mask fields; defaults to the full basis")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument("--verify-report", help="verify a PRIME JSON report receipt without executing its contents")
    parser.add_argument("--verify-input", help="optional original UTF-8 input file for source-hash comparison; requires --verify-report")
    parser.add_argument("--self-test", action="store_true", help="run built-in deterministic tests")
    parser.add_argument("--demo", action="store_true", help="analyze the bundled synthetic example")
    args = parser.parse_args()
    if args.verify_input and not args.verify_report:
        parser.error("--verify-input requires --verify-report")
    if args.verify_report:
        if any((args.text is not None, args.text_file, args.context is not None, args.context_file,
                args.domain_config, args.frame, args.recorded_fields, args.sensory_metadata_file, args.term_catalog_file, args.dichotomy_file, args.profile_performance, args.word_dynamics, args.logical_actions, args.logical_action_word_budget, args.demo, args.self_test)):
            parser.error("--verify-report is a standalone operation; do not combine it with analysis options")
        try:
            report_text, _ = _read_bounded_file(args.verify_report, MAX_REPORT_BYTES, "report")
            report = json.loads(report_text)
            input_bytes = _read_bounded_file(args.verify_input, MAX_TEXT_BYTES, "verification input")[1] if args.verify_input else None
            outcome = verify_report(report, input_bytes)
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            parser.error(str(exc))
        print(json.dumps(outcome, indent=2))
        return 0 if outcome["report_integrity_valid"] and outcome["input_source_match"] is not False else 1
    if args.self_test:
        result = _self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] else 1
    if args.text_file and args.text is not None:
        parser.error("choose one input: --text or --text-file")
    if args.domain_config and args.domain != "crypto":
        parser.error("--domain-config selects its own domain; omit --domain or leave it at crypto")
    try:
        custom_domain = _load_custom_domain(args.domain_config) if args.domain_config else None
        if args.text_file:
            text, raw_bytes = _read_bounded_file(args.text_file, MAX_TEXT_BYTES, "text input")
        elif args.text is not None:
            text, raw_bytes = args.text, args.text.encode("utf-8")
        elif args.demo:
            text = "Agency X proposed a 5% BTC allocation on Ethereum for Q3, subject to audit approval."
            raw_bytes = text.encode("utf-8")
        elif not sys.stdin.isatty():
            raw_bytes = sys.stdin.buffer.read(MAX_TEXT_BYTES + 1)
            if len(raw_bytes) > MAX_TEXT_BYTES:
                raise ValueError(f"stdin exceeds the {MAX_TEXT_BYTES}-byte limit")
            text = raw_bytes.decode("utf-8")
        else:
            parser.error("provide --text, --text-file, piped stdin, --demo, or --self-test")
        if len(raw_bytes) > MAX_TEXT_BYTES:
            raise ValueError(f"text input exceeds the {MAX_TEXT_BYTES}-byte limit")
        if args.context_file and args.context is not None:
            parser.error("choose one context: --context or --context-file")
        if args.context_file:
            context, _context_bytes = _read_bounded_file(args.context_file, MAX_CONTEXT_BYTES, "context input")
        else:
            context = args.context
        if context is not None and len(context.encode("utf-8")) > MAX_CONTEXT_BYTES:
            raise ValueError(f"context exceeds the {MAX_CONTEXT_BYTES}-byte limit")
        sensory_metadata = _load_sensory_metadata(args.sensory_metadata_file) if args.sensory_metadata_file else None
        term_catalog, term_catalog_bytes = _load_term_catalog(args.term_catalog_file) if args.term_catalog_file else (None, None)
        dichotomy_profile, dichotomy_profile_bytes = _load_dichotomy_profile(args.dichotomy_file) if args.dichotomy_file else (None, None)
        result = run_omni_analysis(text, context, args.domain, _parse_csv(args.frame),
                                   _parse_csv(args.recorded_fields), raw_bytes, args.culture, custom_domain,
                                   sensory_metadata, args.profile_performance, term_catalog, term_catalog_bytes, dichotomy_profile, dichotomy_profile_bytes, args.word_dynamics, args.logical_actions, args.logical_action_word_budget)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
