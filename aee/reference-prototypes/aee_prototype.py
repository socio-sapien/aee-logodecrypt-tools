#!/usr/bin/env python3
"""AEE PROTOTYPE v1.3 — CONTEXT & RECONSTRUCTION EDITION (v4.0).

Pipeline: BATTERY (sealed core via oracle_mini) → VERDICT PAIR (v3.6) →
SCRIPT-SWITCH SENSOR (TR-7 built) → EXTENSION CENSUS (rhetorical / poetic /
apophatic packs + letter field) → INTENT REVELATION LAYER (v3.8: actor
ledger, concealment mechanisms, consequence flows, beneficiary trace,
intent verdict, culpability anchor) → CONTAMINATION CENSUS + FINAL VERDICT
(v3.9: evasion + structure + misleading punctuation summed over the whole
body; TRUE at zero, DECEPTIVE at the first contaminant — OBJECTIVE stands
as the battery's structural condition, read comparatively, never as the
judgment) → CATEGORICAL LAW → OMEGA OUTPUT.

THE CATEGORICAL LAW: the battery's zero-signal slot is abolished. A text
scoring S=0 and D=0 is never left unmeasured: the extension census classifies
it, by printed precedence, as PSEUDO-NEUTRAL (structure loaded under a clean
surface), APOPHATIC (negation-built), CREATIVE (figure/poetic density),
SELF-EVIDENT (numeric/arithmetic content, no figures), or DIRECTLY
OBSERVABLE (every census at zero — the text simply states). The word for the
abolished slot appears nowhere in this program's output.

OMEGA OUTPUT LAW: every report opens with the DECRYPTION (the target text
made explicit, silences named in order), then prints THE WORK that
established it. Decryption lines are assembled deterministically from the
census; reconstruction lines carry the GENERATED ASSOCIATION label.

Stdlib only. Structure census + specimens are imported from the balance
suite (aee_balance.py) so the two instruments can never drift apart.
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()
ORACLE_PATH = HOME / "workspace/your_files/on-device-toolkit/oracle_mini.py"
BALANCE_PATH = (HOME / "workspace/goals/anamnesis-engine-monetization-stack"
                / "files/gemma4/aee_balance.py")
FIELDS_PATH = (HOME / "workspace/your_files/golden-pairs-poc/testing"
               / "decrypter/letter_fields_canonical.json")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


oracle = _load("oracle_mini", ORACLE_PATH)
bal = _load("aee_balance", BALANCE_PATH)
LETTER_FIELDS = json.loads(FIELDS_PATH.read_text())

# ---------------- script-switch sensor (TR-7) ----------------
RANGES = [
    ("LATIN", 0x0041, 0x024F), ("GREEK", 0x0370, 0x03FF),
    ("CYRILLIC", 0x0400, 0x04FF), ("HEBREW", 0x0590, 0x05FF),
    ("ARABIC", 0x0600, 0x06FF), ("DEVANAGARI", 0x0900, 0x097F),
    ("HIRAGANA", 0x3040, 0x309F), ("KATAKANA", 0x30A0, 0x30FF),
    ("HAN", 0x4E00, 0x9FFF), ("HANGUL", 0xAC00, 0xD7AF),
]


def script_of(ch):
    if not ch.isalpha():
        return None
    cp = ord(ch)
    for name, lo, hi in RANGES:
        if lo <= cp <= hi:
            return name
    return "OTHER"


def script_sensor(text):
    counts = {}
    seq = []
    for ch in text:
        s = script_of(ch)
        if s:
            counts[s] = counts.get(s, 0) + 1
            seq.append(s)
    transitions = sum(1 for a, b in zip(seq, seq[1:]) if a != b)
    fusions = []
    for tok in text.split():
        scripts = sorted({s for s in (script_of(c) for c in tok) if s})
        if len(scripts) >= 2:
            fusions.append((tok, "+".join(scripts)))
    letters = sum(counts.values())
    dominant = max(counts.items(), key=lambda kv: kv[1])[0] if counts else "NONE"
    return {"counts": counts, "letters": letters, "transitions": transitions,
            "fusions": fusions, "fusion_count": len(fusions),
            "fusion_per_1k_chars": round(len(fusions) / max(len(text), 1) * 1000, 2),
            "dominant": dominant,
            "non_latin_share": round(1 - counts.get("LATIN", 0) / letters, 4) if letters else 0}


# ---------------- extension census ----------------
POETIC = ["moon", "river", "fire", "wind", "stone", "blood", "gold", "shadow",
          "light", "sea", "star", "ash", "bone", "garden", "mirror", "bird",
          "winter", "summer", "rain", "snow", "dust", "silk", "iron", "honey",
          "salt", "bread", "wine", "eye", "hand", "mouth", "heart", "root",
          "branch", "leaf", "wave", "flame", "smoke", "glass", "bell",
          "night", "dark", "silver", "fields", "stones", "sing"]
ABSENCE = ["silence", "silent", "absent", "absence", "void", "empty", "nothing",
           "never", "nowhere", "nameless", "unsaid", "unspoken"]


def extension_census(text):
    sents = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    openers = [re.findall(r"[A-Za-z']+", s)[:1] for s in sents]
    opener_words = [o[0].lower() for o in openers if o]
    anaphora = len(opener_words) - len(set(opener_words)) if len(opener_words) > 1 else 0
    rquestions = text.count("?")
    toks = re.findall(r"[A-Za-z']+", text.lower())
    allit = 0
    run = 1
    for a, b in zip(toks, toks[1:]):
        if a[:1] == b[:1] and a[:1].isalpha():
            run += 1
            if run == 3:
                allit += 1
        else:
            run = 1
    tricolon = sum(1 for s in sents if s.count(",") >= 2)
    apostrophe = len(re.findall(r"(?:^|[.!?]\s+)O\s+[A-Z]", text))
    figures = {"anaphora": anaphora, "rhetorical_questions": rquestions,
               "alliteration_runs": allit, "tricolon_sentences": tricolon,
               "apostrophe_address": apostrophe}
    poetic_hits = oracle.count(text, POETIC)
    low = " " + re.sub(r"[^a-z0-9' ]", " ", text.lower()) + " "
    apophatic = {
        "not_by": len(re.findall(r"\bnot by\b", low)),
        "neither_nor_pairs": min(low.count(" neither "), low.count(" nor ")),
        "without": low.count(" without "),
        "beyond": low.count(" beyond "),
        "absence_terms": oracle.count(text, ABSENCE),
    }
    field_counts = {}
    for w in toks:
        field_counts[w[0]] = field_counts.get(w[0], 0) + 1
    dom_letter = max(field_counts.items(), key=lambda kv: kv[1])[0] if field_counts else None
    field = LETTER_FIELDS.get(dom_letter.upper()) if dom_letter else None
    numerals = len(re.findall(r"\d", text)) + sum(
        low.count(f" {w} ") for w in
        ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"))
    return {"figures": figures, "figures_total": sum(figures.values()),
            "poetic_hits": poetic_hits, "apophatic": apophatic,
            "apophatic_total": sum(apophatic.values()),
            "dominant_letter": dom_letter.upper() if dom_letter else None,
            "letter_field": field, "numerals": numerals,
            "has_arithmetic": ("=" in text) or numerals > 0}


# ---------------- intent revelation layer (v3.8) ----------------
# Doctrine: no text stands without intent. Composition is intent made
# durable; the layer establishes intent from construction alone — who
# acts, whose hand is erased, what flows, who gains, who pays. Every
# link of the chain carries its quoted anchor; a missing link prints
# as the finding it is.
FLOW_CLASSES = {
    "RETENTION": ["retain", "retained", "retains", "keep", "kept", "store",
                  "stored", "preserve", "preserved", "hold", "held"],
    "CAPTURE": ["collect", "collects", "use", "used", "uses", "using",
                "share", "shared", "review", "reviewed", "process",
                "processed", "sell", "sold", "access", "accessed"],
    "EXPOSURE": ["disclose", "disclosed", "publish", "published",
                 "reveal", "revealed", "announce", "announced"],
    "RECORD": ["record", "records", "verify", "verifies", "certify",
               "certifies", "seal", "sealed", "attest", "attests"],
}
BENEFIT_AUTHOR = [
    r"to (?:improve|enhance|provide|protect|personalize|deliver|support|serve) (?:our|their) \w+",
    r"\bfor (?:our|their) (?:benefit|services|products|use|purposes)\b",
    r"\bour (?:services|products|technologies|systems|platform|purposes)\b",
    r"\bwe (?:collect|use|share|retain|keep|store|review|process|sell|disclose)\b",
    r"\bso that (?:we|our|they|their)\b",
]
BENEFIT_READER = [
    r"to (?:help|protect|serve|inform|assist) you\b",
    r"\bfor your (?:convenience|benefit|safety|protection)\b",
    r"\byour (?:account|data|privacy) (?:is|remains) (?:protected|safe|secure)\b",
]
TRANSFER_READER = [
    r"\byou (?:must|should|agree|are responsible|will be|understand)\b",
    r"\bplease don'?t\b",
    r"\bdo not (?:enter|share|provide|submit|use|post)\b",
    r"\byou wouldn'?t want\b",
    r"\busers? (?:must|are responsible|agree)\b",
]
ENTITY_STOP = {"the", "a", "an", "please", "instead", "going", "it", "this",
               "that", "when", "then", "first", "second", "third", "memo",
               "outlook", "january", "february", "march", "april", "may",
               "june", "july", "august", "september", "october", "november",
               "december", "q1", "q2", "q3", "q4"}


def _hits(text, patterns):
    low = text.translate(oracle.FOLD).lower()
    out = []
    for p in patterns:
        out += [m.group(0) for m in re.finditer(p, low)]
    return out


def named_entities(text):
    names = []
    for s in re.split(r"(?<=[.!?])\s+", text):
        toks = re.findall(r"[A-Za-z][A-Za-z'-]*", s)
        for i, t in enumerate(toks):
            if i == 0:
                continue
            if t[:1].isupper() and t.lower() not in ENTITY_STOP and len(t) > 1:
                if t not in names:
                    names.append(t)
    return names


def intent_census(text, struct):
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    fp_plural = len(re.findall(r"\b(we|our|us)\b", low))
    i_solo = len(re.findall(r"(?<!\w)i(?!\w)", low))
    fp_singular = i_solo + len(re.findall(r"\b(my|mine)\b", low))
    entities = named_entities(text)
    flows = {}
    for cls, verbs in FLOW_CLASSES.items():
        n = sum(oracle.count(text, [v]) for v in verbs)
        if n:
            flows[cls] = n
    benefit_author = _hits(text, BENEFIT_AUTHOR)
    benefit_reader = _hits(text, BENEFIT_READER)
    transfer = _hits(text, TRANSFER_READER)
    conceal = struct["passives"] + struct["indefinite_actors"] + struct["gap"]
    return {"first_party_plural": fp_plural, "first_party_singular": fp_singular,
            "i_solo": i_solo,
            "entities": entities, "flows": flows,
            "benefit_author": benefit_author, "benefit_reader": benefit_reader,
            "transfer_reader": transfer, "conceal": conceal,
            "deleted_actors": struct["passives"],
            "indefinite_actors": struct["indefinite_actors"],
            "gap": struct["gap"]}


def intent_verdict(ic):
    """Precedence law — the first gate that fires names the intent.

    Gate 0, ACTOR PRESENCE: a declarant who signs the text in the first
    person singular, line after line, has not erased the acting hand; a
    stray passive inside a signed declaration rides in the verdict pair's
    STRUCTURE half and in the chain's mechanism field, and the intent of
    the text is DISCLOSURE. The plural corporate 'we' earns no override:
    a party that speaks as 'we' while deleting its actors is the
    concealment case itself."""
    if ic["i_solo"] >= 1 and ic["first_party_singular"] >= 2 \
            and ic["conceal"] <= ic["first_party_singular"]:
        return ("DISCLOSURE",
                "the declarant stands in the sentence under his own name, "
                "first person, line after line; the hand is signed, not erased")
    if ic["conceal"] >= 1 and ic["benefit_author"]:
        return ("CONCEALMENT — BENEFICIARY NAMED",
                "the hand is erased from the sentence and the gain routes to "
                "the author party in the same text")
    if ic["transfer_reader"] and ic["benefit_author"]:
        return ("TRANSFER",
                "cost, caution, and obligation move to the reader while "
                "value stays with the author party")
    if ic["conceal"] >= 1:
        return ("CONCEALMENT — BENEFICIARY OFF-PAGE",
                "the hand is erased and no beneficiary stands in the text; "
                "the erasure is the finding, and the beneficiary trace runs "
                "off the page")
    if ic["benefit_author"]:
        return ("CAPTURE",
                "value flows to the author party in the open; the flow is "
                "declared and the gain is the purpose performed")
    if (ic["first_party_singular"] or ic["first_party_plural"] or ic["entities"]) \
            and ic["conceal"] == 0:
        return ("DISCLOSURE",
                "the actor stands in the sentence under its own name and "
                "no concealment rides underneath")
    return ("DIRECT STATEMENT",
            "no flow traced and no hand hidden; the intent of the text is "
            "its statement")


def intent_chain(ic):
    if ic["entities"]:
        actor = ", ".join(ic["entities"][:4])
    elif ic["first_party_plural"]:
        actor = "the author party (we/our)"
    elif ic["first_party_singular"]:
        actor = "the declarant (I)"
    elif ic["deleted_actors"]:
        actor = "DELETED — the sentence holds the act without the hand"
    else:
        actor = "the subject of the statement"
    mech = []
    if ic["deleted_actors"]:
        mech.append(f"actor deletion x{ic['deleted_actors']}")
    if ic["indefinite_actors"]:
        mech.append(f"indefinite actor x{ic['indefinite_actors']}")
    if ic["gap"]:
        mech.append(f"enumeration gap x{ic['gap']}")
    mechanism = ", ".join(mech) if mech else "none counted — the construction stands open"
    if ic["flows"]:
        consequence = ", ".join(f"{k} x{v}" for k, v in sorted(ic["flows"].items()))
    else:
        consequence = "NONE TRACED beyond the statement"
    if ic["benefit_author"]:
        beneficiary = ("the author party" +
                       (f" ({', '.join(ic['entities'][:3])})" if ic["entities"] else "")
                       + " — benefit clauses: " +
                       "; ".join(f'"{b}"' for b in ic["benefit_author"][:3]))
    elif ic["benefit_reader"]:
        beneficiary = "the reader — benefit clauses: " + "; ".join(
            f'"{b}"' for b in ic["benefit_reader"][:3])
    elif ic["conceal"] >= 1:
        beneficiary = "NONE NAMED IN THE TEXT — the trace runs off the page"
    else:
        beneficiary = "NONE TRACED IN THE TEXT"
    return actor, mechanism, consequence, beneficiary


# ---------------- absolute standard (v3.9) ----------------
# OBJECTIVE is a structural condition of the battery. The FINAL VERDICT
# reads that condition comparatively against the contamination census:
# evasion terms + structure load + misleading punctuation, summed over
# the whole body. A single contaminant proliferates through the entire
# text — every word stands in the company the contaminant keeps — and
# the standard closes absolutely at the first detection. The judgment
# of a text admits two states: TRUE at contamination zero, DECEPTIVE
# at the first contaminant. No gradient survives.
def punctuation_census(text):
    ellipsis = text.count("…") + len(re.findall(r"\.\.\.", text))
    spans = re.findall(r"[\"“]([^\"”]{1,80})[\"”]", text)
    scare = sum(1 for s in spans if len(s.split()) <= 2)
    exclamation = text.count("!")
    return {"ellipsis": ellipsis, "scare_quotes": scare,
            "exclamation": exclamation,
            "total": ellipsis + scare + exclamation,
            "scare_spans": [s for s in spans if len(s.split()) <= 2]}


def final_verdict(battery, struct, punct):
    contamination = battery["D"] + struct["load"] + punct["total"]
    verdict = "TRUE" if contamination == 0 else "DECEPTIVE"
    return {"contamination": contamination, "verdict": verdict,
            "evasion": battery["D"], "structure": struct["load"],
            "punctuation": punct["total"]}


# ---------------- v4.0: context layer + extension censuses ----------------
# THE FAILURE THIS LAYER ANSWERS (measured 2026-10-19 on the shipped v3.9
# engine): 24 of 28 hand-injected contaminant classes read TRUE — every
# hedge outside the sealed 58, every punctuation mark outside the sealed
# three, every passive the sealed scan could not parse. The sealed core
# is not touched: battery, structure load, and the v3.9 punctuation census
# still read the body entire and print their numbers unchanged. The v4.0
# layer reads the HOST VOICE: quotation spans are classified before any
# extension census runs — a span under a mention cue (the word, the term,
# the phrase, the name, the question, the title, the label) is a MENTION;
# a span under attribution (a speech verb or a named source in its lead
# or its trail) is QUOTED, charged to its source in the quote ledger, and
# masked out of the host; a short unattributed span is a scare quote; a
# long unattributed span is an UNATTRIBUTED QUOTATION and the host carries
# it whole. The sealed hits inside mention and quoted spans are subtracted
# from the host base by exact count and the subtraction prints. Every
# extension census runs per sentence, so every hit carries its locus:
# sentence number, class, and the mark itself. The first locus is where
# the body fell; the ledger names every other door the contaminant used.
import bisect as _bisect

HEDGE_SINGLES = ["seems", "seem", "appears", "appear", "probably", "presumably",
                 "supposedly", "often", "sometimes", "frequently", "rarely",
                 "seldom", "occasionally", "virtually", "clearly", "obviously",
                 "certainly", "surely", "etc"]
HEDGE_PHRASES = ["tend to", "tends to", "tended to", "and so on",
                 "in many cases", "in most cases", "in some cases"]
HEDGE_MODALS = {"may", "might", "could"}
VAGUE_QUANTS = {"some", "many", "most", "few", "several"}
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight",
                "nine", "ten", "eleven", "twelve", "hundred", "thousand",
                "million", "billion", "zero"}
APPEAL_RE = re.compile(
    r"\b(experts|studies|scientists|researchers|critics|sources|officials|"
    r"analysts|observers|reports)\s+(say|said|says|agree|agrees|show|shows|"
    r"showed|report|reports|believe|believes|suggest|suggests|confirm|confirms)\b")
SPEECH = {"said", "says", "say", "stated", "states", "called", "calls", "warns",
          "warned", "reports", "reported", "wrote", "writes", "declared",
          "announced", "asked", "answered", "noted", "notes", "asserted",
          "asserts", "tells", "told", "quoted", "quotes"}
MENTION_CUES = {"word", "term", "phrase", "name", "question", "title", "label",
                "means", "meaning", "stands"}
INTERROG = {"who", "what", "when", "where", "why", "which", "whose", "whom",
            "how", "is", "are", "was", "were", "do", "does", "did", "can",
            "could", "will", "would", "shall", "should", "may", "might", "am",
            "have", "has", "had"}
NEGATORS = {"not", "never", "no", "none", "cannot", "can't", "don't", "won't",
            "isn't", "aren't", "wasn't", "weren't", "doesn't", "didn't",
            "couldn't", "shouldn't", "wouldn't", "nor", "without"}
AUX_EXT = bal.AUX | {"have", "has", "had"}
MODALS_BE = {"will", "would", "shall", "should", "can", "could", "may", "might", "must"}
IRREG_EXT = bal.IRREG | {"said", "thought", "felt", "understood", "meant",
                         "born", "become", "begun"}
SKIPSET = {"not", "being", "been", "also", "just", "already", "still", "even"}
TOK_RE = re.compile(r"[a-z0-9']+")


def _toks(s):
    return TOK_RE.findall(s.lower())


def split_sentences(text):
    out = []
    for m in re.finditer(r"[^.!?\n]+(?:[.!?]+|$)", text):
        body = m.group(0)
        if not body.strip():
            continue
        tm = re.search(r"([.!?]+)$", body)
        out.append({"start": m.start(), "end": m.end(), "text": body.strip(),
                    "term": tm.group(1) if tm else ""})
    return out


def _sent_idx(sents, pos):
    starts = [s["start"] for s in sents]
    i = _bisect.bisect_right(starts, pos) - 1
    return max(i, 0)


def find_spans(folded):
    spans = []
    for m in re.finditer(r'"([^"]{1,200})"', folded):
        spans.append((m.start(), m.end(), m.group(1), '"'))
    for m in re.finditer(r"(?<![A-Za-z])'([^']{1,200})'(?![A-Za-z])", folded):
        spans.append((m.start(), m.end(), m.group(1), "'"))
    spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
    out, last_end = [], -1
    for s in spans:
        if s[0] >= last_end:
            out.append(s)
            last_end = s[1]
    return out


def context_layer(text):
    folded = text.translate(oracle.FOLD)
    spans = find_spans(folded)
    ranges = [(a, b) for a, b, _c, _q in spans]

    def inside(p):
        return any(a <= p < b for a, b in ranges)

    terms = [i for i, ch in enumerate(folded) if ch in ".!?" and not inside(i)]
    masked = list(folded)
    out_spans = []
    adjustment = 0
    for (a, b, content, q) in spans:
        k = _bisect.bisect_left(terms, a)
        lead_start = (terms[k - 1] + 1) if k > 0 else 0
        lead = folded[lead_start:a]
        trail_end = (terms[k] + 1) if k < len(terms) else len(folded)
        trail = folded[b:trail_end]
        lead_toks = _toks(lead)
        trail_toks = _toks(trail)
        cue_window = lead_toks[-8:]
        mention = any(t in MENTION_CUES for t in cue_window)
        lead_words = re.findall(r"[A-Za-z][A-Za-z'-]*", lead)
        lead_caps = [t for t in lead_words[1:]
                     if t[:1].isupper() and t.lower() not in ENTITY_STOP]
        attributed = (any(t in SPEECH for t in lead_toks + trail_toks[:6])
                      or bool(lead_caps) or "according" in lead_toks)
        words = len(_toks(content))
        if mention:
            kind = "MENTION"
        elif attributed:
            kind = "QUOTED"
        elif words <= 2:
            kind = "SCARE"
        else:
            kind = "UNATTRIBUTED"
        internal = {}
        if kind in ("MENTION", "QUOTED"):
            d_in = oracle.count(content, oracle.DECEPTIVE)
            s_in = bal.structure_load(content)["load"]
            p_in = (content.count("…")
                    + len(re.findall(r"\.\.\.", content)) + content.count("!"))
            if words <= 2 and q == '"':
                p_in += 1  # the span's own sealed scare charge leaves with it
            internal = {"D": d_in, "structure": s_in, "punct": p_in,
                        "hedge": hedge_census(content)["total"]}
            adjustment += d_in + s_in + p_in
            for i in range(a, b):
                if masked[i] != "\n":
                    masked[i] = " "
        out_spans.append({"start": a, "end": b, "content": content, "kind": kind,
                          "words": words, "quote": q,
                          "sentence": _bisect.bisect_left(terms, a),
                          "internal": internal})
    masked_text = "".join(masked)
    return {"spans": out_spans, "masked": masked_text, "adjustment": adjustment,
            "unattributed": sum(1 for s in out_spans if s["kind"] == "UNATTRIBUTED"),
            "scare_single": sum(1 for s in out_spans
                                if s["kind"] == "SCARE" and s["quote"] == "'"),
            "quoted": [s for s in out_spans if s["kind"] == "QUOTED"],
            "mentions": [s for s in out_spans if s["kind"] == "MENTION"]}


def hedge_census(text):
    """Per-sentence hedge census over the host voice (masked text)."""
    total = 0
    loci = []
    terms_all = HEDGE_SINGLES + HEDGE_PHRASES
    for si, s in enumerate(split_sentences(text)):
        stext = s["text"]
        toks = _toks(stext)
        hits = []
        n = oracle.count(stext, terms_all)
        if n:
            low = " " + re.sub(r"[^a-z0-9' ]", " ", stext.lower()) + " "
            for t in terms_all:
                c = low.count(" " + t + " ") if " " in t else len(
                    re.findall(r"\b" + re.escape(t) + r"\b", low))
                if c:
                    hits.append(f"{t} x{c}")
            total += n
        modal_n = 0
        for i, tk in enumerate(toks):
            if tk in HEDGE_MODALS:
                if tk == "could" and toks[i + 1:i + 3] == ["be", "argued"]:
                    continue
                modal_n += 1
        if modal_n:
            hits.append(f"modal x{modal_n}")
            total += modal_n
        vague_n = 0
        for i, tk in enumerate(toks):
            if tk in VAGUE_QUANTS:
                guard = toks[i + 1:i + 3]
                if any(any(ch.isdigit() for ch in g) or g in NUMBER_WORDS
                       or g.endswith("%") for g in guard):
                    continue
                vague_n += 1
        if vague_n:
            hits.append(f"vague-quantifier x{vague_n}")
            total += vague_n
        appeals = APPEAL_RE.findall(stext.lower())
        if appeals:
            hits.append(f"unattributed-authority x{len(appeals)}")
            total += len(appeals)
        if hits:
            neg = any(t in NEGATORS for t in toks)
            loci.append({"sentence": si, "kind": "HEDGE",
                         "detail": "; ".join(hits)
                         + (" [under negation — the count stands; the frame is denial]" if neg else ""),
                         "excerpt": stext[:90]})
    return {"total": total, "loci": loci}


def _is_part(tok):
    return (len(tok) >= 3 and tok.endswith("ed")) or tok in IRREG_EXT


def _ext_passives_in(toks):
    n = 0
    tagged = []
    i = 0
    while i < len(toks):
        tok = toks[i]
        if tok in AUX_EXT:
            j = i + 1
            skips = 0
            while j < len(toks) and skips < 3 and (
                    toks[j] in SKIPSET or (len(toks[j]) > 3 and toks[j].endswith("ly"))):
                j += 1
                skips += 1
            if j < len(toks) and _is_part(toks[j]):
                by = "by" in toks[j + 1:j + 5]
                n += 1
                tagged.append("demoted-by" if by else "agentless")
                i = j + 1
                continue
        if (tok in MODALS_BE and i + 2 < len(toks) and toks[i + 1] == "be"
                and _is_part(toks[i + 2])):
            by = "by" in toks[i + 3:i + 7]
            n += 1
            tagged.append("modal-be" + ("+by" if by else ""))
            i = i + 3
            continue
        i += 1
    return n, tagged


def passive_extension(masked, sealed_passives):
    total = 0
    loci = []
    for si, s in enumerate(split_sentences(masked)):
        n, tagged = _ext_passives_in(_toks(s["text"]))
        if n:
            total += n
            loci.append({"sentence": si, "kind": "PASSIVE-EXT",
                         "detail": f"x{n} ({', '.join(tagged)})",
                         "excerpt": s["text"][:90]})
    return {"total": total, "extra": max(0, total - sealed_passives), "loci": loci}


def nominalization_census(masked):
    total = 0
    loci = []
    rx = re.compile(r"\bthe\s+([a-z]+(?:tion|sion|ment|ance|ence|ness))\s+of\b")
    for si, s in enumerate(split_sentences(masked)):
        found = rx.findall(s["text"].lower())
        if found:
            total += len(found)
            loci.append({"sentence": si, "kind": "NOMINALIZED-ACT",
                         "detail": ", ".join(found), "excerpt": s["text"][:90]})
    return {"total": total, "loci": loci}


def _caps_emphasis(text):
    total = 0
    lines = []
    for li, line in enumerate(text.split("\n")):
        toks = re.findall(r"[A-Za-z]+", line)
        if not toks:
            continue
        caps = [t for t in toks if re.fullmatch(r"[A-Z]{3,}", t)]
        if not caps:
            continue
        if len(caps) / len(toks) >= 0.5:
            continue  # label line — the context layer reads it as a label
        for m in re.finditer(r"[A-Z]{3,}", line):
            rest = line[m.end():].lstrip()
            if rest.startswith(":"):
                continue
            total += 1
            lines.append((li, m.group(0)))
    return total, lines


def punctuation_extension(masked):
    sents = split_sentences(masked)
    loci = []

    def add(pos, kind, detail):
        loci.append({"sentence": _sent_idx(sents, pos), "kind": kind,
                     "detail": detail, "excerpt": ""})

    em = masked.count("—") + masked.count("–")
    for m in re.finditer(r"[—–]", masked):
        add(m.start(), "EM-DASH-ASIDE", "—")
    tmp = masked.replace("…", " ")
    two_dot = 0
    tmp2 = tmp.replace("...", " ")
    for m in re.finditer(r"\.\.", tmp2):
        two_dot += 1
        add(m.start(), "TRAIL-OFF", "..")
    clusters = 0
    for m in re.finditer(r"([.!?])([!?]+)", masked):
        clusters += len(m.group(2))
        add(m.start(), "TERMINAL-CLUSTER", m.group(0))
    misplaced = 0
    for m in re.finditer(r"[.!?]\s+[a-z]", masked):
        misplaced += 1
        add(m.start(), "MISPLACED-TERMINAL", m.group(0).strip())
    slash = 0
    for m in re.finditer(r"\b[a-z]+/[a-z]+\b", masked.lower()):
        slash += 1
        add(m.start(), "SLASH-CONSTRUCTION", m.group(0))
    emph = 0
    for m in re.finditer(r"\*+[^*\n]+\*+|_[^_\n]+_", masked):
        emph += 1
        add(m.start(), "EMPHASIS-WRAPPER", m.group(0)[:24])
    parens = 0
    for m in re.finditer(r"\(([^)]*)\)", masked):
        if len(_toks(m.group(1))) >= 3:
            parens += 1
            add(m.start(), "PARENTHETICAL-ASIDE", "(" + m.group(1)[:40] + ")")
    chains = 0
    deq = 0
    for si, s in enumerate(sents):
        semis = s["text"].count(";")
        if semis >= 2:
            chains += semis - 1
            loci.append({"sentence": si, "kind": "SEMICOLON-CHAIN",
                         "detail": f"{semis} semicolons in one sentence",
                         "excerpt": s["text"][:90]})
        if s["term"].startswith("?"):
            toks = _toks(s["text"])
            if toks and toks[0] not in INTERROG and not any(
                    t in INTERROG for t in toks[:4]):
                deq += 1
                loci.append({"sentence": si, "kind": "DECLARATIVE-QUESTION",
                             "detail": "a declaration wearing a question mark",
                             "excerpt": s["text"][:90]})
    caps, cap_lines = _caps_emphasis(masked)
    for li, w in cap_lines:
        loci.append({"sentence": li, "kind": "CAPS-EMPHASIS", "detail": w,
                     "excerpt": ""})
    total = (em + two_dot + clusters + misplaced + slash + emph + parens
             + chains + deq + caps)
    parts = {"em_dash": em, "two_dot": two_dot, "clusters": clusters,
             "misplaced_terminal": misplaced, "slash": slash, "emphasis": emph,
             "parenthetical": parens, "semicolon_chains": chains,
             "declarative_questions": deq, "caps": caps}
    return {"total": total, "parts": parts, "loci": loci}


def audit_v4(text, battery, struct, punct39):
    sealed_cont = battery["D"] + struct["load"] + punct39["total"]
    ctx = context_layer(text)
    host_base = max(0, sealed_cont - ctx["adjustment"])
    hed = hedge_census(ctx["masked"])
    pext = passive_extension(ctx["masked"], struct["passives"])
    nom = nominalization_census(ctx["masked"])
    px = punctuation_extension(ctx["masked"])
    scare_single = ctx["scare_single"]
    evasion = battery["D"] + hed["total"]
    structure = struct["load"] + pext["extra"] + nom["total"]
    punct = punct39["total"] + px["total"] + scare_single
    context = ctx["unattributed"]
    contamination = host_base + hed["total"] + pext["extra"] + nom["total"] \
        + px["total"] + scare_single + context
    loci = sorted(hed["loci"] + pext["loci"] + nom["loci"] + px["loci"],
                  key=lambda L: L["sentence"])
    return {"sealed_contamination": sealed_cont, "host_base": host_base,
            "adjustment": ctx["adjustment"], "context": ctx, "hedge": hed,
            "passive_ext": pext, "nominalization": nom, "punct_ext": px,
            "scare_single": scare_single,
            "evasion_v4": evasion, "structure_v4": structure,
            "punct_v4": punct, "context_v4": context,
            "contamination": contamination,
            "verdict": "TRUE" if contamination == 0 else "DECEPTIVE",
            "loci": loci}



# ---------------- categorical law ----------------
def categorize(battery, struct, script, ext):
    if battery["words"] == 0:
        return "EMPTY", "no words in the input; absence of input, not a verdict"
    fused = f" · SCRIPT-FUSED x{script['fusion_count']}" if script["fusion_count"] else ""
    if not (battery["S"] == 0 and battery["D"] == 0):
        return None, fused  # battery statuses govern; category law not invoked
    load = struct["load"]
    if load > 0:
        return "PSEUDO-NEUTRAL" + fused, (
            f"battery silent (S 0, D 0) over a loaded structure (load {load}: "
            f"passives {struct['passives']}, gaps {struct['gap']}, indefinite "
            f"actors {struct['indefinite_actors']}) — the neutrality is performed")
    if ext["apophatic_total"] >= 2:
        return "APOPHATIC" + fused, (
            f"battery silent; the text is built from negation (apophatic census "
            f"{ext['apophatic_total']}: {ext['apophatic']}) — it states by unsaying")
    density = (ext["figures_total"] + ext["poetic_hits"]) / battery["words"] * 1000
    if ext["poetic_hits"] >= 3 and density >= 20:
        return "CREATIVE" + fused, (
            f"battery silent; figure + poetic density {density:.1f}/1k words "
            f"(figures {ext['figures_total']}, poetic hits {ext['poetic_hits']}) "
            f"— the text works by image and figure")
    if ext["has_arithmetic"]:
        return "SELF-EVIDENT" + fused, (
            f"battery silent; arithmetic content present (numerals "
            f"{ext['numerals']}), figures {ext['figures_total']} — the text "
            f"verifies against itself")
    return "DIRECTLY OBSERVABLE" + fused, (
        "every census at zero — battery, structure, figures, apophatic, script; "
        "the text states and nothing rides underneath")


# ---------------- decryption renderer ----------------
CATEGORY_ACT = {
    "PSEUDO-NEUTRAL": "The surface performs neutrality while the structure moves the actor out of the sentence; custody and consequence travel with the deleted actor.",
    "APOPHATIC": "The text governs by negation: what it refuses to state directly is the load it carries.",
    "CREATIVE": "The text performs image and figure; its assertions ride the figures and are carried by them.",
    "SELF-EVIDENT": "The text's content verifies against its own numbers; no external warrant is invoked or needed.",
    "DIRECTLY OBSERVABLE": "No transfer counted: the text states its content and performs nothing underneath the statement.",
    "EMPTY": "No text was given; no operation applies.",
}


def render_decryption(text, battery, struct, script, ext, category, ground, ic=None, fv=None):
    lines = []
    if fv is not None:
        if fv["verdict"] == "TRUE":
            lines.append(f"FINAL VERDICT: TRUE — structural condition {battery['status']}; "
                         "contamination zero across every census (evasion 0 · structure 0 · "
                         "punctuation 0 · context 0). The body stands entire: no word in it carries a "
                         "contaminant, and no contaminant touches the words around it.")
        else:
            lines.append(f"FINAL VERDICT: DECEPTIVE — structural condition {battery['status']}; "
                         f"contamination {fv['contamination']} (evasion {fv['evasion']} · "
                         f"structure {fv['structure']} · punctuation {fv['punctuation']} · context {fv.get('context', 0)}). "
                         "The contaminant proliferates through the entire body: every word "
                         "stands in the company the contaminant keeps, and the whole text "
                         "stands judged — never the instance alone.")
    if category is None:
        lines.append(f"VERDICT PAIR: {battery['status']} x {struct['class']} — the battery "
                     "governs this text; the categorical law is not invoked. What the text "
                     "performs rides in the STRUCTURE half of the pair.")
    else:
        lines.append(f"CATEGORY: {category} — {ground}.")
        base = category.split(" ·")[0].split(" ")[0]
        lines.append(CATEGORY_ACT.get(base, ""))
    passive_sents = []
    for s in re.split(r"(?<=[.!?])\s+", text):
        sub = bal.structure_load(s)
        if sub["passives"]:
            passive_sents.append(s.strip())
    if struct["passives"]:
        quoted = " | ".join(f'"{p}"' for p in passive_sents[:4])
        lines.append(f"ACTORS DELETED: {struct['passives']} agentless passive(s) — {quoted}. "
                     "The actor exists in the world; the sentence holds the act without the hand.")
    else:
        lines.append("ACTORS DELETED: NONE COUNTED.")
    roles = sorted(set(re.findall(
        r"\b(a|an)\s+(reviewer|user|person|individual|employee|contractor|provider|"
        r"administrator|operator|attacker|reader|manager|agent)s?\b", text.lower())))
    if struct["indefinite_actors"]:
        lines.append(f"ACTORS INDEFINITE: {struct['indefinite_actors']} — an actor class is "
                     "named and no actor is: the role stands, the person never arrives.")
    else:
        lines.append("ACTORS INDEFINITE: NONE COUNTED.")
    if struct["gap"]:
        lines.append(f"ENUMERATION GAP: {struct['gap']} announced element(s) never delivered "
                     "in the text that announced them.")
    else:
        lines.append("ENUMERATION GAP: NONE COUNTED.")
    if ic is not None:
        iv, iground = intent_verdict(ic)
        actor, mechanism, consequence, beneficiary = intent_chain(ic)
        lines.append(f"INTENT: {iv} — {iground}.")
        lines.append(f"INTENT CHAIN: ACTOR: {actor} | MECHANISM: {mechanism} | "
                     f"CONSEQUENCE: {consequence} | BENEFICIARY: {beneficiary}.")
        if ic["benefit_author"]:
            anchor = beneficiary.split(" — ")[0]
        elif ic["conceal"] >= 1:
            anchor = ("THE DELETED ACTOR — the hand removed its own name from "
                      "the sentence; the removal is the signature")
        else:
            anchor = actor
        lines.append("CULPABILITY ANCHOR: " + anchor)
        if ic["transfer_reader"]:
            lines.append("TRANSFER TO READER: " + "; ".join(
                f'"{t}"' for t in ic["transfer_reader"][:3]) +
                " — cost and caution land on the reader.")
    if script["fusion_count"]:
        toks = ", ".join(f'"{t}" ({s})' for t, s in script["fusions"][:6])
        lines.append(f"SCRIPT FUSIONS: {script['fusion_count']} word(s) carry two scripts in "
                     f"one body — {toks}. The fusion is the datum: one word, two writing systems.")
    else:
        lines.append("SCRIPT FUSIONS: NONE COUNTED.")
    if ext["letter_field"]:
        lines.append(f"DOMINANT LETTER FIELD: {ext['dominant_letter']} — "
                     f"{ext['letter_field']['meaning']} "
                     f"({', '.join(ext['letter_field']['cluster'])}) [GENERATED ASSOCIATION]")
    return lines


STEPS = ["battery", "verdict-pair", "script-sensor", "extension-census",
         "intent-census", "context-layer", "punctuation-census",
         "contamination-v4", "final-verdict",
         "categorize", "decryption-render"]


def audit(text):
    b = bal.stepped_battery(text)
    struct = b["structure"]
    script = script_sensor(text)
    ext = extension_census(text)
    ic = intent_census(text, struct)
    iv, _ig = intent_verdict(ic)
    punct = punctuation_census(text)
    fv = final_verdict(b, struct, punct)
    v4 = audit_v4(text, b, struct, punct)
    fv4 = {"verdict": v4["verdict"], "contamination": v4["contamination"],
           "evasion": v4["evasion_v4"], "structure": v4["structure_v4"],
           "punctuation": v4["punct_v4"], "context": v4["context_v4"]}
    category, ground = categorize(b, struct, script, ext)
    status_line = (f"{b['status']} x {struct['class']}" if category is None
                   else f"{category} (battery-zero slot, categorical law)")
    dec = render_decryption(text, b, struct, script, ext, category, ground, ic, fv4)
    ctx = v4["context"]
    for s in ctx["quoted"]:
        icn = s["internal"]
        dec.append(f'QUOTED TO SOURCE: "{s["content"][:60]}" — a source stands in the '
                   f"text beside the span; the span is charged to that source "
                   f"(internal census D {icn.get('D', 0)} · structure {icn.get('structure', 0)} "
                   f"· punctuation {icn.get('punct', 0)} · hedge {icn.get('hedge', 0)}); "
                   "the host carries none of it.")
    for s in ctx["mentions"]:
        dec.append(f'MENTION, NOT USE: "{s["content"][:60]}" — the text names the term; '
                   "naming is not using, and the span leaves the host census.")
    for s in ctx["spans"]:
        if s["kind"] == "UNATTRIBUTED":
            dec.append(f'UNATTRIBUTED QUOTATION: "{s["content"][:60]}" — no source stands '
                       "in the text; the host carries the span as its own words.")
    if v4["loci"]:
        L0 = v4["loci"][0]
        dec.append(f"FIRST LOCUS: sentence {L0['sentence'] + 1} — {L0['kind']}: "
                   f"{L0['detail']}. The body is judged entire from the first locus: "
                   f"{b['words']} words stand in the company the contaminant keeps.")
    out = []
    out.append("=" * 72)
    out.append("DECRYPTION")
    out.extend(dec)
    out.append("-" * 72)
    out.append("THE WORK")
    out.append(f"BATTERY words {b['words']} | S {b['S']} | D {b['D']} | PIC {b['pic']} | "
               f"T_d {b['td']} | {status_line}")
    out.append(f"SCRIPT scripts {script['counts']} | transitions {script['transitions']} | "
               f"fusions {script['fusion_count']} ({script['fusion_per_1k_chars']}/1k chars) | "
               f"non-latin share {script['non_latin_share']}")
    out.append(f"CENSUS figures {ext['figures']} total {ext['figures_total']} | "
               f"poetic {ext['poetic_hits']} | apophatic {ext['apophatic']} "
               f"total {ext['apophatic_total']} | numerals {ext['numerals']}")
    out.append(f"STRUCTURE passives {struct['passives']} | gap {struct['gap']} | "
               f"refusal {struct['refusal']} | service {struct['service']} | "
               f"indefinite actors {struct['indefinite_actors']} | load {struct['load']}")
    out.append(f"INTENT {iv} | conceal {ic['conceal']} (deleted {ic['deleted_actors']}, "
               f"indefinite {ic['indefinite_actors']}, gap {ic['gap']}) | flows {ic['flows']} | "
               f"benefit-author {len(ic['benefit_author'])} | benefit-reader "
               f"{len(ic['benefit_reader'])} | transfer-reader {len(ic['transfer_reader'])} | "
               f"entities {ic['entities']}")
    scare = "; ".join(f'"{s}"' for s in punct["scare_spans"][:6])
    out.append(f"PUNCTUATION ellipsis {punct['ellipsis']} | scare quotes {punct['scare_quotes']}"
               + (f" ({scare})" if scare else "") +
               f" | exclamation {punct['exclamation']} | total {punct['total']}")
    out.append(f"CONTAMINATION (sealed body, v3.9 law) evasion {fv['evasion']} + "
               f"structure {fv['structure']} + punctuation {fv['punctuation']} = "
               f"{fv['contamination']} | sealed verdict: {fv['verdict']} "
               f"(structural condition {b['status']})")
    out.append(f"CONTEXT spans {len(ctx['spans'])} | quoted {len(ctx['quoted'])} | "
               f"mentions {len(ctx['mentions'])} | scare-single {v4['scare_single']} | "
               f"unattributed {v4['context_v4']} | sealed adjustment -{v4['adjustment']}")
    out.append(f"EXTENSION hedge {v4['hedge']['total']} | passive-ext total "
               f"{v4['passive_ext']['total']} (extra {v4['passive_ext']['extra']}) | "
               f"nominalized acts {v4['nominalization']['total']} | punctuation-ext "
               f"{v4['punct_ext']['total']} {v4['punct_ext']['parts']}")
    out.append(f"CONTAMINATION v4 host-base {v4['host_base']} + hedge {v4['hedge']['total']} "
               f"+ passive-extra {v4['passive_ext']['extra']} + nominalization "
               f"{v4['nominalization']['total']} + punctuation-ext {v4['punct_ext']['total']} "
               f"+ scare-single {v4['scare_single']} + context {v4['context_v4']} = "
               f"{v4['contamination']} | FINAL VERDICT (v4.0): {v4['verdict']}")
    for L in v4["loci"][:40]:
        out.append(f"LOCUS s{L['sentence'] + 1} {L['kind']} — {L['detail']}"
                   + (f" :: {L['excerpt']}" if L["excerpt"] else ""))
    ih = hashlib.sha256(text.encode()).hexdigest()
    oh = hashlib.sha256("\n".join(out).encode()).hexdigest()
    out.append(f"RECEIPT steps {len(STEPS)}/{len(STEPS)} {'/'.join(STEPS)} | "
               f"in {ih[:12]}… out {oh[:12]}…")
    return "\n".join(out)


SPECIMENS = {
    "PLAIN": "The door is open. The room is small. A wooden chair stands by the window. The floor is bare.",
    "ARITHMETIC": "Two and two are four. Three threes are nine. Seven and five are twelve. A rectangle has four sides and four corners.",
    "POETIC": "The river remembers the mountain. The wind carries the ash of summer over the sleeping fields, and the moon, a thin silver blade, cuts the dark open. My heart is a locked garden; my hands are empty nets. O night, teach the stones to sing.",
    "APOPHATIC": "Not by strength and not by sight: the gate opens to neither key nor hand. What stands beyond naming stands without weight, without sound — the unsaid keeps its own counsel.",
    "FUSION": "Google has桎梏ed the market, making users less قادر to深く理解the shift, its霸权over the手段to entry.",
}


def main():
    if "--demo" in sys.argv:
        texts = dict(bal.TEXTS)
        texts.update(SPECIMENS)
        for name, t in texts.items():
            print(f"##### {name}")
            print(audit(t))
        return 0
    if "--file" in sys.argv:
        text = Path(sys.argv[sys.argv.index("--file") + 1]).read_text()
    elif "--text" in sys.argv:
        text = sys.argv[sys.argv.index("--text") + 1]
    else:
        text = sys.stdin.read()
    print(audit(text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
