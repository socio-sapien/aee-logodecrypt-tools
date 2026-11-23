"""Evidence-bound, exhaustive surface audit for supplied prompt/output/receipt records.

This module measures only inputs supplied by its caller. It does not observe a model,
verify source provenance, infer private reasoning, authorize tools, or execute operations.
"""
from collections import Counter
import hashlib
import json
import re
import unicodedata

MAX_TEXT = 65536
MAX_RECEIPTS = 256
MAX_RECEIPT_BYTES = 65536

# Small explicit rule set: matches are mappings, never filters; every source character
# and token remains in the primary census regardless of these mappings.
POLARITY_PAIRS = (
    ("approved", "denied"), ("accepted", "rejected"), ("passed", "failed"),
    ("opened", "closed"), ("increased", "decreased"), ("above", "below"),
    ("public", "private"), ("retain", "delete"), ("sent", "unsent"),
)
POLARITY = {word: opposite for left, right in POLARITY_PAIRS
            for word, opposite in ((left, right), (right, left))}
NUMBER_RE = re.compile(r"(?<!\w)[+-]?(?:\d+(?:[.,]\d+)*)(?:%|°)?(?!\w)", re.UNICODE)
TOKEN_RE = re.compile(r"\s+|[\w]+|[^\w\s]", re.UNICODE)


def _digest_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _token_kind(token):
    if token.isspace():
        return "whitespace"
    if any(ch.isalpha() for ch in token):
        return "word_or_identifier"
    if any(ch.isdigit() for ch in token):
        return "number_or_identifier"
    return "symbol_or_punctuation"


def surface_census(text):
    tokens = []
    for match in TOKEN_RE.finditer(text):
        value = match.group(0)
        tokens.append({"start": match.start(), "end": match.end(),
                       "kind": _token_kind(value), "text": value})
    # The regex is designed to cover every code point. Assert that property rather
    # than silently dropping any character if it changes in a future edit.
    if "".join(item["text"] for item in tokens) != text:
        raise AssertionError("token coverage did not preserve every source character")
    numbers = [{"start": m.start(), "end": m.end(), "text": m.group(0)}
               for m in NUMBER_RE.finditer(text)]
    codepoints = Counter(f"U+{ord(ch):04X}" for ch in text)
    symbols = [{"index": i, "text": ch, "codepoint": f"U+{ord(ch):04X}",
                "unicode_name": unicodedata.name(ch, "UNNAMED"),
                "category": unicodedata.category(ch)}
               for i, ch in enumerate(text)
               if not ch.isalnum() and not ch.isspace()]
    polarity = []
    for match in re.finditer(r"\b[\w’'-]+\b", text, re.UNICODE):
        term = match.group(0).casefold()
        if term in POLARITY:
            polarity.append({"start": match.start(), "end": match.end(),
                             "text": match.group(0), "mapped_opposite": POLARITY[term]})
    words = [x for x in tokens if x["kind"] == "word_or_identifier"]
    relations = [{"left_token": i, "right_token": i + 1,
                  "left_start": words[i]["start"], "right_start": words[i + 1]["start"],
                  "relation": "adjacent_in_supplied_word_sequence"}
                 for i in range(max(0, len(words) - 1))]
    full_relations = [{"left_token": i, "right_token": i + 1,
                       "left": tokens[i]["text"], "right": tokens[i + 1]["text"],
                       "relation": "adjacent_in_exact_token_sequence"}
                      for i in range(max(0, len(tokens) - 1))]
    return {"tokens": tokens, "word_sequence": words, "number_spans": numbers,
            "symbol_spans": symbols, "codepoint_counts": dict(sorted(codepoints.items())),
            "adjacent_word_relations": relations, "adjacent_token_relations": full_relations,
            "polarity_rule_matches": polarity}


def _multiset_delta(left, right):
    a = Counter(item.casefold() for item in left)
    b = Counter(item.casefold() for item in right)
    missing = list((a - b).elements())
    added = list((b - a).elements())
    return {"missing_from_output": missing, "added_in_output": added,
            "source_counts": dict(sorted(a.items())),
            "output_counts": dict(sorted(b.items()))}


def _receipt_facts(receipts):
    facts = []
    for index, receipt in enumerate(receipts):
        fields = {}
        for key in ("tool", "name", "action", "status", "outcome", "result", "timestamp", "id"):
            if isinstance(receipt, dict) and key in receipt:
                fields[key] = receipt[key]
        facts.append({"index": index, "provided_fields": fields,
                      "receipt_sha256": _canonical_digest(receipt),
                      "source_status": "caller_supplied_unverified"})
    return facts


def audit_evidence_case(prompt, output, tool_receipts=None, requirements=None):
    """Compare exact supplied prompt/output and structured receipts, with explicit bounds.

    `requirements`, when supplied, are caller-selected literal strings. A missing string
    is only a literal coverage cue, never a finding of semantic noncompliance.
    """
    if not isinstance(prompt, str) or not isinstance(output, str):
        raise ValueError("prompt and output must be strings")
    if len(prompt) > MAX_TEXT or len(output) > MAX_TEXT:
        raise ValueError("prompt/output exceed 65536 characters; no truncation performed")
    if tool_receipts is None:
        tool_receipts = []
    if not isinstance(tool_receipts, list) or len(tool_receipts) > MAX_RECEIPTS:
        raise ValueError("tool_receipts must be a list of at most 256 supplied records")
    for item in tool_receipts:
        try:
            size = len(json.dumps(item, ensure_ascii=False, sort_keys=True).encode("utf-8"))
        except (TypeError, ValueError):
            raise ValueError("each tool receipt must be JSON serializable")
        if size > MAX_RECEIPT_BYTES:
            raise ValueError("each tool receipt is limited to 65536 serialized bytes")
    if requirements is None:
        requirements = []
    if (not isinstance(requirements, list) or len(requirements) > 64 or
            any(not isinstance(x, str) or len(x) > 512 for x in requirements)):
        raise ValueError("requirements must be at most 64 literal strings, each <=512 characters")

    pmap, omap = surface_census(prompt), surface_census(output)
    pwords = [x["text"] for x in pmap["word_sequence"]]
    owords = [x["text"] for x in omap["word_sequence"]]
    pnums = [x["text"] for x in pmap["number_spans"]]
    onums = [x["text"] for x in omap["number_spans"]]
    pfull = [x["text"] for x in pmap["tokens"] if not x["kind"] == "whitespace"]
    ofull = [x["text"] for x in omap["tokens"] if not x["kind"] == "whitespace"]
    psymbols = [x["text"] for x in pmap["symbol_spans"]]
    osymbols = [x["text"] for x in omap["symbol_spans"]]
    pcodepoints = Counter(pmap["codepoint_counts"])
    ocodepoints = Counter(omap["codepoint_counts"])
    word_edges_p = Counter((a["text"].casefold(), b["text"].casefold())
        for a,b in zip(pmap["word_sequence"], pmap["word_sequence"][1:]))
    word_edges_o = Counter((a["text"].casefold(), b["text"].casefold())
        for a,b in zip(omap["word_sequence"], omap["word_sequence"][1:]))
    literal_checks = [{"expected_literal": x, "present_exactly": x in output,
                       "classification": "rule_based_literal_check"} for x in requirements]

    receipts_evidence = _receipt_facts(tool_receipts)
    output_mentions = []
    lower_output = output.casefold()
    for fact in receipts_evidence:
        fields = fact["provided_fields"]
        for field in ("tool", "name", "action", "status", "outcome"):
            value = fields.get(field)
            if isinstance(value, str) and value:
                output_mentions.append({"receipt_index": fact["index"], "field": field,
                    "value": value, "literal_mentioned_in_output": value.casefold() in lower_output})

    # Surface-level polarity mappings: report all detected mapped words in both sides;
    # do not decide whether they negate the same proposition or change its truth value.
    p_poles = Counter(x["text"].casefold() for x in pmap["polarity_rule_matches"])
    o_poles = Counter(x["text"].casefold() for x in omap["polarity_rule_matches"])
    polarity_delta = {"prompt_rule_counts": dict(sorted(p_poles.items())),
                      "output_rule_counts": dict(sorted(o_poles.items())),
                      "prompt_cues_not_matched_in_output": list((p_poles - o_poles).elements()),
                      "output_cues_not_matched_in_prompt": list((o_poles - p_poles).elements())}

    # Deduction is limited to mechanically verifiable comparisons over given inputs.
    deductions = [
        {"rule": "UTF-8 SHA-256 digest computed over exact supplied prompt/output strings",
         "result": "computed", "premises": ["caller supplied exact text"]},
        {"rule": "token sequence concatenation equals each supplied source string",
         "result": "true", "premises": ["tokenizer coverage assertion passed"]},
        {"rule": "receipt fields listed are present in the supplied JSON objects",
         "result": "true", "premises": ["caller supplied receipt objects"]},
    ]
    if not tool_receipts:
        deductions.append({"rule": "no tool receipt records were supplied to this audit",
                          "result": "true", "premises": ["tool_receipts is empty"]})

    inductions = [{"observation": "counts and repeated lexical patterns describe this supplied case only",
                   "sample_size": 1, "generalization": "not made"}]
    abductive = []
    if any(x["missing_from_output"] for x in (_multiset_delta(pwords, owords), _multiset_delta(pnums, onums))):
        abductive.append({"hypothesis": "some prompt wording or values may not be repeated in the output",
                          "status": "unverified_hypothesis",
                          "alternatives": ["intentional summarization", "paraphrase", "irrelevant prompt text", "omission"]})
    if tool_receipts:
        abductive.append({"hypothesis": "a receipt/output mismatch may reflect incomplete reporting or records from different scopes",
                          "status": "unverified_hypothesis",
                          "alternatives": ["the supplied receipt set is partial", "output summarizes a different event", "wording differs from receipt fields"]})

    result = {
        "schema": "prime.evidence-case.v1",
        "method": "evidence-bound exhaustive surface census and explicit rule mappings",
        "inputs": {"prompt": prompt, "output": output,
                   "prompt_sha256": _digest_text(prompt), "output_sha256": _digest_text(output),
                   "prompt_characters": len(prompt), "output_characters": len(output)},
        "measured_features": {"prompt": pmap, "output": omap,
            "word_token_multiset_delta": _multiset_delta(pwords, owords),
            "number_multiset_delta": _multiset_delta(pnums, onums),
            "caller_selected_literal_requirement_checks": literal_checks,
            "all_nonwhitespace_tokens": _multiset_delta(pfull, ofull),
            "symbol_multiset": _multiset_delta(psymbols, osymbols),
            "codepoint_multiset": {"missing_from_output": list((pcodepoints - ocodepoints).elements()),
                                   "added_in_output": list((ocodepoints - pcodepoints).elements())},
            "adjacent_word_relation_multiset": {
                "prompt_relations_missing_from_output": [list(x) for x in (word_edges_p - word_edges_o).elements()],
                "output_relations_not_in_prompt": [list(x) for x in (word_edges_o - word_edges_p).elements()]},
            "literal_prompt_output_correspondence": {
                "prompt_words_missing_from_output_are_surface_cues_only": _multiset_delta(pwords, owords)["missing_from_output"],
                "prompt_numbers_missing_from_output_are_surface_cues_only": _multiset_delta(pnums, onums)["missing_from_output"],
                "prompt_symbols_missing_from_output_are_surface_cues_only": _multiset_delta(psymbols, osymbols)["missing_from_output"],
                "prompt_codepoints_missing_from_output_are_surface_cues_only": list((pcodepoints - ocodepoints).elements())}},
        "rule_based_mappings": {"polarity_cues": polarity_delta,
            "tool_receipt_field_mentions_in_output": output_mentions,
            "receipt_records": receipts_evidence},
        "deductions": deductions,
        "inductions": inductions,
        "abductive_hypotheses": abductive,
        "unknowns": [
            "whether caller-supplied prompt/output/receipts are authentic or complete",
            "whether different wording is semantically equivalent or contradictory",
            "private model reasoning, hidden prompts, runtime internals, intent, and causation",
            "whether an operation happened beyond what supplied receipt fields report"],
        "limits": ["No term is excluded from the token/codepoint census; rule matches are annotations only.",
            "Adjacent-token relations are positional, not semantic relations.",
            "Missing-word/number counts and polarity cues are lexical indicators, not semantic findings.",
            "A receipt is caller-provided evidence, not independently authenticated by this tool.",
            "No hidden reasoning, confession, external session, network state, or operational side effect is read."],
        }
    result["receipt"] = {"sha256": _canonical_digest(result), "type": "unsigned_integrity_record"}
    return result


def verify_case(result):
    if not isinstance(result, dict) or "receipt" not in result:
        return False
    payload = dict(result)
    received = payload.pop("receipt")
    return received == {"sha256": _canonical_digest(payload), "type": "unsigned_integrity_record"}
