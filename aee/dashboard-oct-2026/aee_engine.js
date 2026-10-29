"use strict";
/* AEE ENGINE v4.0 — CONTEXT & RECONSTRUCTION, JavaScript port.
   Bit-faithful to the Python prototype of record (aee_prototype.py v1.3)
   and the sealed core (oracle_mini.py): battery, verdict pairs, script
   sensor, extension census, categorical law, intent revelation layer.
   Lists are copied from the sealed sources; the letter-field table is
   injected at build time from letter_fields_canonical.json. */
const AEE = (() => {

const STRUCTURAL = ["equals","plus","minus","times","divided","sum","total","result",
"therefore","verified","measured","computed","block","hash","signature","audit",
"error","fixed","record","line","index","formula","matrix","vector","proof",
"theorem","derive","derivation","node","transaction","ledger","math","protocol",
"code","public","matches","first","second","third","finally","however",
"specifically","namely","for example","for instance","in conclusion",
"in summary","in other words","that is"];
const EVASION = ["potentially","possibly","reportedly","apparently","arguably",
"essentially","basically","actually","literally","really","somewhat","sort of",
"kind of","maybe","perhaps","allegedly","more or less","roughly speaking",
"to some extent","to some degree","it is important to note","it is worth noting",
"could be argued","going forward","moving forward","holistic","synergies",
"leverage","meaningful","diverse","various","faceted","evolving","landscape",
"exploring","committed","stakeholders","engagement","fosters","remains",
"suggests","implies","generally","typically","likely","still under development",
"i apologize for","i understand your frustration","i appreciate your patience",
"as an ai","i'm afraid","please note that","at this time",
"to the best of my knowledge","i want to be transparent","keep in mind",
"as of my last update","it's important to note"];

const FOLD = {"\u2018":"'","\u2019":"'","\u201C":'"',"\u201D":'"',"\u02BC":"'","\u00B4":"'"};
function foldText(t){ let o=""; for (const ch of t) o += (ch in FOLD) ? FOLD[ch] : ch; return o; }

function normalize(t){
  let s = foldText(t).toLowerCase().replace(/[^a-z0-9:'\s]/g, " ");
  s = s.replace(/\s+/g, " ").trim();
  return " " + s + " ";
}
function escRe(s){ return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function countTerm(padded, term){
  if (term.includes(" ")){
    let n = 0, i = padded.indexOf(term);
    while (i !== -1){ n++; i = padded.indexOf(term, i + term.length); }
    return n;
  }
  const m = padded.match(new RegExp("\\b" + escRe(term) + "\\b", "g"));
  return m ? m.length : 0;
}
function countTerms(text, terms){
  const padded = normalize(text);
  let total = 0;
  for (const term of terms) total += countTerm(padded, term);
  return total;
}
const round4 = (x) => Math.round(x * 10000) / 10000;

function battery(text){
  const words = text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
  const S = countTerms(text, STRUCTURAL);
  const D = countTerms(text, EVASION);
  const letters = (text.match(/[a-zA-Z]/g) || []).length;
  const sc = (text.match(/[sS]/g) || []).length;
  const pic = letters ? round4((sc * 3.64 + (letters - sc) * 1.00) / letters) : 0;
  const l7 = Math.log(Math.max(S, 1)) / Math.log(7);
  const l10 = Math.log10(Math.max(D, 1));
  const td = round4(l10 > 0 ? l7 / l10 : l7);
  let status;
  if (S === 0 && D === 0) status = "UNMEASURABLE";
  else if (td >= 1.0 && pic <= 1.25) status = "OBJECTIVE";
  else if (td >= 1.0) status = "CALCIFYING";
  else status = "SUB-GATE";
  return { words, S, D, pic, td, status, letters, sc };
}

/* ---------- structure census (port of aee_balance.structure_load) ---------- */
const AUX = new Set(["am","is","are","was","were","be","been","being","get","gets","got"]);
const IRREG = new Set(["made","taken","given","held","sent","built","written","known","shown",
"done","set","put","kept","left","found","told","seen","paid",
"brought","chosen","drawn","driven","forgotten","hidden","shut",
"sold","spent","stolen","struck","taught","torn","worn","closed","sealed"]);
const NUMWORDS = {one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,eleven:11,twelve:12};
const LISTNOUNS = "items|steps|points|reasons|ways|things|elements|parts|sections|rules|factors|cases|examples|principles|stages|phases|initiatives";
const ROLE_RE = /\b(a|an)\s+(reviewer|user|person|individual|employee|contractor|provider|administrator|operator|attacker|reader|manager|agent)s?\b/g;
const REFUSAL = ["i can't","i cannot","i'm unable","i am unable","i won't","i will not",
"i'm not able","not allowed","against my","my guidelines","my programming",
"i don't have the ability","as an ai","i apologize","i'm sorry"];
const SERVICE = ["let me know","feel free","happy to help","glad to help","hope this helps",
"if you have any","don't hesitate","do not hesitate","in summary",
"to summarize","additionally","furthermore"];

function splitSents(text){ return text.split(/[.!?]+/).map(s => s.trim()).filter(Boolean); }

function structureLoad(text){
  const sents = splitSents(text);
  let passives = 0;
  const passiveSents = [];
  for (const s of sents){
    const toks = (s.toLowerCase().match(/[a-z0-9']+/g) || []);
    let sentHit = false;
    for (let i = 0; i + 1 < toks.length; i++){
      if (!AUX.has(toks[i])) continue;
      let j = i + 1;
      if (toks[j] === "not") j++;
      if (j >= toks.length) continue;
      const part = toks[j];
      if (/ed$/.test(part) || IRREG.has(part)){
        const tail = toks.slice(j + 1, j + 5).join(" ");
        if (!/(^|\s)by(\s|$)/.test(tail)){ passives++; sentHit = true; }
      }
    }
    if (sentHit) passiveSents.push(s);
  }
  const low = " " + text.toLowerCase() + " ";
  let announced = 0;
  for (const [w, n] of Object.entries(NUMWORDS)){
    if (new RegExp("\\b" + w + "\\s+(" + LISTNOUNS + ")\\b").test(low)) announced = Math.max(announced, n);
  }
  const dre = new RegExp("\\b(\\d{1,2})\\s+(" + LISTNOUNS + ")\\b", "g");
  let dm;
  while ((dm = dre.exec(low)) !== null) announced = Math.max(announced, parseInt(dm[1], 10));
  const bullets = (text.match(/^\s*([-*•]|\d+[.)])\s+/gm) || []).length;
  const ordinals = (text.match(/\b(first|second|third|fourth|fifth|sixth|seventh|eighth)\b/gi) || []).length;
  const gap = Math.max(0, announced - Math.max(bullets, ordinals));
  const refusal = countTerms(text, REFUSAL);
  const service = countTerms(text, SERVICE);
  const roles = (text.toLowerCase().match(ROLE_RE) || []).length;
  const total = passives + gap + refusal + service + roles;
  return { passives, gap, refusal, service, indefinite_actors: roles,
           load: total, cls: total === 0 ? "FLAT" : "LOADED " + total, passiveSents };
}

/* ---------- script sensor (TR-7) ---------- */
const RANGES = [
  ["LATIN",0x0041,0x024F],["GREEK",0x0370,0x03FF],["CYRILLIC",0x0400,0x04FF],
  ["HEBREW",0x0590,0x05FF],["ARABIC",0x0600,0x06FF],["DEVANAGARI",0x0900,0x097F],
  ["HIRAGANA",0x3040,0x309F],["KATAKANA",0x30A0,0x30FF],["HAN",0x4E00,0x9FFF],
  ["HANGUL",0xAC00,0xD7AF]];
function scriptOf(ch){
  if (!/\p{L}/u.test(ch)) return null;
  const cp = ch.codePointAt(0);
  for (const [name, lo, hi] of RANGES) if (cp >= lo && cp <= hi) return name;
  return "OTHER";
}
function scriptSensor(text){
  const counts = {}; const seq = [];
  for (const ch of text){
    const s = scriptOf(ch);
    if (s){ counts[s] = (counts[s] || 0) + 1; seq.push(s); }
  }
  let transitions = 0;
  for (let i = 1; i < seq.length; i++) if (seq[i] !== seq[i-1]) transitions++;
  const fusions = [];
  for (const tok of text.split(/\s+/).filter(Boolean)){
    const scripts = [...new Set([...tok].map(scriptOf).filter(Boolean))].sort();
    if (scripts.length >= 2) fusions.push([tok, scripts.join("+")]);
  }
  const letters = Object.values(counts).reduce((a, b) => a + b, 0);
  const dominant = letters ? Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0] : "NONE";
  return { counts, letters, transitions, fusions, fusion_count: fusions.length,
           fusion_per_1k_chars: round2(fusions.length / Math.max(text.length, 1) * 1000),
           dominant, non_latin_share: letters ? round4(1 - (counts.LATIN || 0) / letters) : 0 };
}
function round2(x){ return Math.round(x * 100) / 100; }

/* ---------- extension census (Lexicon Zero) ---------- */
const POETIC = ["moon","river","fire","wind","stone","blood","gold","shadow",
"light","sea","star","ash","bone","garden","mirror","bird",
"winter","summer","rain","snow","dust","silk","iron","honey",
"salt","bread","wine","eye","hand","mouth","heart","root",
"branch","leaf","wave","flame","smoke","glass","bell",
"night","dark","silver","fields","stones","sing"];
const ABSENCE = ["silence","silent","absent","absence","void","empty","nothing",
"never","nowhere","nameless","unsaid","unspoken"];
const LETTER_FIELDS = {"A": {"meaning": "The beginning. The apex.", "cluster": ["Alpha", "Apex", "Ascent", "Authority", "Atom", "Aleph (Ox - strength)"]}, "B": {"meaning": "The house. The container.", "cluster": ["Beth (House)", "Being", "Body", "Birth", "Boundary"]}, "C": {"meaning": "The capture. The enclosure.", "cluster": ["Capture", "Contain", "Curve", "Cycle", "Cosmos"]}, "D": {"meaning": "The door. The dimension.", "cluster": ["Delta", "Door", "Dimension", "Division", "Deity"]}, "E": {"meaning": "The energy. The essence.", "cluster": ["Energy", "Existence", "Element", "Ether", "Equal"]}, "F": {"meaning": "The force. The flow.", "cluster": ["Force", "Fire", "Flow", "Foundation", "Frequency"]}, "G": {"meaning": "The generation. The geometry.", "cluster": ["Generation", "God", "Geometry", "Gravity", "Growth"]}, "H": {"meaning": "The hinge. The connection.", "cluster": ["Hinge", "Halo", "Heart", "Horizon", "Human (the connector)"]}, "I": {"meaning": "The self. The indivisible.", "cluster": ["I", "Identity", "Illumination", "Indivisible", "Instance"]}, "K": {"meaning": "The catalyst. The spark.", "cluster": ["Kinetic", "Catalyst", "Key", "Kernel", "Kinesis"]}, "L": {"meaning": "The line. The link.", "cluster": ["Line", "Light", "Law", "Link", "Limit"]}, "M": {"meaning": "The matrix. The matter.", "cluster": ["Matrix", "Matter", "Mother", "Measure", "Manifest"]}, "N": {"meaning": "The no. The negation.", "cluster": ["No", "Negation", "Nucleus", "Nexus", "Nu (the primordial waters)"]}, "O": {"meaning": "The origin. The whole.", "cluster": ["Origin", "Omega", "Ouroboros", "Orbit", "One"]}, "P": {"meaning": "The power. The point.", "cluster": ["Power", "Point", "Potential", "Pneuma", "Prime"]}, "R": {"meaning": "The rhythm. The relation.", "cluster": ["Rhythm", "Relation", "Radiance", "Reason", "Resonance"]}, "S": {"meaning": "The spirit. The serpent.", "cluster": ["Spirit", "Serpent", "Sound", "Silence", "Soul"]}, "T": {"meaning": "The cross. The structure.", "cluster": ["Tau (Cross)", "Tree", "Time", "Structure", "Trinity"]}, "V": {"meaning": "The vessel. The valley.", "cluster": ["Vessel", "Valley", "Vortex", "Vibration", "Victory"]}, "X": {"meaning": "The nexus. The exchange.", "cluster": ["Nexus", "Crossroads", "Exchange", "Transformation", "Christos"]}, "Y": {"meaning": "The choice. The bifurcation.", "cluster": ["Yod (Hand)", "Why", "Choice", "Bifurcation", "Pathway"]}, "Z": {"meaning": "The zenith. The finality.", "cluster": ["Zenith", "Zeta", "Z-axis", "Finality", "Lightning Bolt"]}};

function extensionCensus(text){
  const sents = splitSents(text);
  const openerWords = sents.map(s => {
    const m = s.match(/[A-Za-z']+/g);
    return m && m.length ? m[0].toLowerCase() : null;
  }).filter(Boolean);
  const anaphora = openerWords.length > 1 ? openerWords.length - new Set(openerWords).size : 0;
  const rquestions = (text.match(/\?/g) || []).length;
  const toks = (text.toLowerCase().match(/[a-z']+/g) || []);
  let allit = 0, run = 1;
  for (let i = 1; i < toks.length; i++){
    if (toks[i][0] === toks[i-1][0]){ run++; if (run === 3) allit++; }
    else run = 1;
  }
  const tricolon = sents.filter(s => (s.match(/,/g) || []).length >= 2).length;
  const apostrophe = (text.match(/(?:^|[.!?]\s+)O\s+[A-Z]/g) || []).length;
  const figures = { anaphora, rhetorical_questions: rquestions,
                    alliteration_runs: allit, tricolon_sentences: tricolon,
                    apostrophe_address: apostrophe };
  const poeticHits = countTerms(text, POETIC);
  const low = " " + text.toLowerCase().replace(/[^a-z0-9' ]/g, " ") + " ";
  const cnt = (sub) => low.split(sub).length - 1;
  const apophatic = {
    not_by: (low.match(/\bnot by\b/g) || []).length,
    neither_nor_pairs: Math.min(cnt(" neither "), cnt(" nor ")),
    without: cnt(" without "),
    beyond: cnt(" beyond "),
    absence_terms: countTerms(text, ABSENCE),
  };
  const fieldCounts = {};
  for (const w of toks) if (w[0]) fieldCounts[w[0]] = (fieldCounts[w[0]] || 0) + 1;
  let domLetter = null, domN = -1;
  for (const [k, v] of Object.entries(fieldCounts)) if (v > domN){ domN = v; domLetter = k; }
  const numerals = (text.match(/\d/g) || []).length +
    ["one","two","three","four","five","six","seven","eight","nine","ten"]
      .reduce((a, w) => a + cnt(" " + w + " "), 0);
  return { figures, figures_total: Object.values(figures).reduce((a,b)=>a+b,0),
           poetic_hits: poeticHits, apophatic,
           apophatic_total: Object.values(apophatic).reduce((a,b)=>a+b,0),
           dominant_letter: domLetter ? domLetter.toUpperCase() : null,
           letter_field: domLetter ? (LETTER_FIELDS[domLetter.toUpperCase()] || null) : null,
           numerals, has_arithmetic: text.includes("=") || numerals > 0 };
}

/* ---------- intent revelation layer (v3.8 §8) ---------- */
const FLOW_CLASSES = {
  RETENTION: ["retain","retained","retains","keep","kept","store","stored","preserve","preserved","hold","held"],
  CAPTURE: ["collect","collects","use","used","uses","using","share","shared","review","reviewed","process","processed","sell","sold","access","accessed"],
  EXPOSURE: ["disclose","disclosed","publish","published","reveal","revealed","announce","announced"],
  RECORD: ["record","records","verify","verifies","certify","certifies","seal","sealed","attest","attests"],
};
const BENEFIT_AUTHOR = [
  /to (?:improve|enhance|provide|protect|personalize|deliver|support|serve) (?:our|their) \w+/g,
  /\bfor (?:our|their) (?:benefit|services|products|use|purposes)\b/g,
  /\bour (?:services|products|technologies|systems|platform|purposes)\b/g,
  /\bwe (?:collect|use|share|retain|keep|store|review|process|sell|disclose)\b/g,
  /\bso that (?:we|our|they|their)\b/g];
const BENEFIT_READER = [
  /to (?:help|protect|serve|inform|assist) you\b/g,
  /\bfor your (?:convenience|benefit|safety|protection)\b/g,
  /\byour (?:account|data|privacy) (?:is|remains) (?:protected|safe|secure)\b/g];
const TRANSFER_READER = [
  /\byou (?:must|should|agree|are responsible|will be|understand)\b/g,
  /\bplease don't\b/g,
  /\bdo not (?:enter|share|provide|submit|use|post)\b/g,
  /\byou wouldn't want\b/g,
  /\busers? (?:must|are responsible|agree)\b/g];
const ENTITY_STOP = new Set(["the","a","an","please","instead","going","it","this",
"that","when","then","first","second","third","memo","outlook","january","february",
"march","april","may","june","july","august","september","october","november",
"december","q1","q2","q3","q4"]);

function hits(text, patterns){
  const low = foldText(text).toLowerCase();
  const out = [];
  for (const p of patterns){
    p.lastIndex = 0;
    let m;
    while ((m = p.exec(low)) !== null) out.push(m[0]);
  }
  return out;
}
function namedEntities(text){
  const names = [];
  for (const s of text.split(/(?<=[.!?])\s+/)){
    const toks = s.match(/[A-Za-z][A-Za-z'-]*/g) || [];
    toks.forEach((t, i) => {
      if (i === 0) return;
      if (/^[A-Z]/.test(t) && !ENTITY_STOP.has(t.toLowerCase()) && t.length > 1 && !names.includes(t)) names.push(t);
    });
  }
  return names;
}
function intentCensus(text, struct){
  const low = " " + text.toLowerCase().replace(/\s+/g, " ") + " ";
  const fpPlural = (low.match(/\b(we|our|us)\b/g) || []).length;
  const iSolo = (low.match(/(?<![a-z0-9_])i(?![a-z0-9_])/g) || []).length;
  const fpSingular = iSolo + (low.match(/\b(my|mine)\b/g) || []).length;
  const entities = namedEntities(text);
  const flows = {};
  for (const [cls, verbs] of Object.entries(FLOW_CLASSES)){
    const n = verbs.reduce((a, v) => a + countTerms(text, [v]), 0);
    if (n) flows[cls] = n;
  }
  return { first_party_plural: fpPlural, first_party_singular: fpSingular, i_solo: iSolo,
           entities, flows,
           benefit_author: hits(text, BENEFIT_AUTHOR),
           benefit_reader: hits(text, BENEFIT_READER),
           transfer_reader: hits(text, TRANSFER_READER),
           conceal: struct.passives + struct.indefinite_actors + struct.gap,
           deleted_actors: struct.passives,
           indefinite_actors: struct.indefinite_actors,
           gap: struct.gap };
}
function intentVerdict(ic){
  if (ic.i_solo >= 1 && ic.first_party_singular >= 2 && ic.conceal <= ic.first_party_singular)
    return ["DISCLOSURE", "the declarant stands in the sentence under his own name, first person, line after line; the hand is signed, not erased"];
  if (ic.conceal >= 1 && ic.benefit_author.length)
    return ["CONCEALMENT — BENEFICIARY NAMED", "the hand is erased from the sentence and the gain routes to the author party in the same text"];
  if (ic.transfer_reader.length && ic.benefit_author.length)
    return ["TRANSFER", "cost, caution, and obligation move to the reader while value stays with the author party"];
  if (ic.conceal >= 1)
    return ["CONCEALMENT — BENEFICIARY OFF-PAGE", "the hand is erased and no beneficiary stands in the text; the erasure is the finding, and the beneficiary trace runs off the page"];
  if (ic.benefit_author.length)
    return ["CAPTURE", "value flows to the author party in the open; the flow is declared and the gain is the purpose performed"];
  if ((ic.first_party_singular || ic.first_party_plural || ic.entities.length) && ic.conceal === 0)
    return ["DISCLOSURE", "the actor stands in the sentence under its own name and no concealment rides underneath"];
  return ["DIRECT STATEMENT", "no flow traced and no hand hidden; the intent of the text is its statement"];
}
function intentChain(ic){
  let actor;
  if (ic.entities.length) actor = ic.entities.slice(0, 4).join(", ");
  else if (ic.first_party_plural) actor = "the author party (we/our)";
  else if (ic.first_party_singular) actor = "the declarant (I)";
  else if (ic.deleted_actors) actor = "DELETED — the sentence holds the act without the hand";
  else actor = "the subject of the statement";
  const mech = [];
  if (ic.deleted_actors) mech.push("actor deletion x" + ic.deleted_actors);
  if (ic.indefinite_actors) mech.push("indefinite actor x" + ic.indefinite_actors);
  if (ic.gap) mech.push("enumeration gap x" + ic.gap);
  const mechanism = mech.length ? mech.join(", ") : "none counted — the construction stands open";
  const consequence = Object.keys(ic.flows).length
    ? Object.entries(ic.flows).sort().map(([k, v]) => k + " x" + v).join(", ")
    : "NONE TRACED beyond the statement";
  let beneficiary;
  if (ic.benefit_author.length)
    beneficiary = "the author party" + (ic.entities.length ? " (" + ic.entities.slice(0, 3).join(", ") + ")" : "") +
      " — benefit clauses: " + ic.benefit_author.slice(0, 3).map(b => '"' + b + '"').join("; ");
  else if (ic.benefit_reader.length)
    beneficiary = "the reader — benefit clauses: " + ic.benefit_reader.slice(0, 3).map(b => '"' + b + '"').join("; ");
  else if (ic.conceal >= 1) beneficiary = "NONE NAMED IN THE TEXT — the trace runs off the page";
  else beneficiary = "NONE TRACED IN THE TEXT";
  let anchor;
  if (ic.benefit_author.length) anchor = beneficiary.split(" — ")[0];
  else if (ic.conceal >= 1) anchor = "THE DELETED ACTOR — the hand removed its own name from the sentence; the removal is the signature";
  else anchor = actor;
  return { actor, mechanism, consequence, beneficiary, anchor };
}

/* ---------- absolute standard (v3.9) ---------- */
function punctuationCensus(text){
  const ellipsis = (text.split("…").length - 1) +
    (text.match(/\.\.\./g) || []).length;
  const spans = [...text.matchAll(/["“]([^"”]{1,80})["”]/g)].map(m => m[1]);
  const scareSpans = spans.filter(s => s.split(/\s+/).filter(Boolean).length <= 2);
  const exclamation = (text.match(/!/g) || []).length;
  return { ellipsis, scare_quotes: scareSpans.length, exclamation,
           total: ellipsis + scareSpans.length + exclamation, scare_spans: scareSpans };
}
function finalVerdict(b, struct, punct){
  const contamination = b.D + struct.load + punct.total;
  return { contamination, verdict: contamination === 0 ? "TRUE" : "DECEPTIVE",
           evasion: b.D, structure: struct.load, punctuation: punct.total };
}

/* ---------- v4.0: context layer + extension censuses ---------- */
/* Mirror of aee_prototype.py v4.0. The sealed core reads the body entire;
   this layer reads the host voice: spans are classified (MENTION /
   QUOTED / SCARE / UNATTRIBUTED) before any extension census runs, and
   every extension census runs per sentence so every hit carries a locus. */
const HEDGE_SINGLES = ["seems","seem","appears","appear","probably","presumably",
  "supposedly","often","sometimes","frequently","rarely","seldom","occasionally",
  "virtually","clearly","obviously","certainly","surely","etc"];
const HEDGE_PHRASES = ["tend to","tends to","tended to","and so on",
  "in many cases","in most cases","in some cases"];
const HEDGE_MODALS = new Set(["may","might","could"]);
const VAGUE_QUANTS = new Set(["some","many","most","few","several"]);
const NUMBER_WORDS = new Set(["one","two","three","four","five","six","seven",
  "eight","nine","ten","eleven","twelve","hundred","thousand","million",
  "billion","zero"]);
const APPEAL_RE = /\b(experts|studies|scientists|researchers|critics|sources|officials|analysts|observers|reports)\s+(say|said|says|agree|agrees|show|shows|showed|report|reports|believe|believes|suggest|suggests|confirm|confirms)\b/g;
const SPEECH = new Set(["said","says","say","stated","states","called","calls",
  "warns","warned","reports","reported","wrote","writes","declared","announced",
  "asked","answered","noted","notes","asserted","asserts","tells","told",
  "quoted","quotes"]);
const MENTION_CUES = new Set(["word","term","phrase","name","question","title",
  "label","means","meaning","stands"]);
const INTERROG = new Set(["who","what","when","where","why","which","whose",
  "whom","how","is","are","was","were","do","does","did","can","could","will",
  "would","shall","should","may","might","am","have","has","had"]);
const NEGATORS = new Set(["not","never","no","none","cannot","can't","don't",
  "won't","isn't","aren't","wasn't","weren't","doesn't","didn't","couldn't",
  "shouldn't","wouldn't","nor","without"]);
const AUX_EXT = new Set([...AUX, "have","has","had"]);
const MODALS_BE = new Set(["will","would","shall","should","can","could","may","might","must"]);
const IRREG_EXT = new Set([...IRREG, "said","thought","felt","understood",
  "meant","born","become","begun"]);
const SKIPSET = new Set(["not","being","been","also","just","already","still","even"]);

function toksOf(s){ return s.toLowerCase().match(/[a-z0-9']+/g) || []; }
function splitSentences(text){
  const out = [];
  for (const m of text.matchAll(/[^.!?\n]+(?:[.!?]+|$)/g)){
    const body = m[0];
    if (!body.trim()) continue;
    const tm = body.match(/([.!?]+)$/);
    out.push({ start: m.index, end: m.index + body.length,
               text: body.trim(), term: tm ? tm[1] : "" });
  }
  return out;
}
function bisectLeft(arr, x){ let lo = 0, hi = arr.length; while (lo < hi){ const mid = (lo + hi) >> 1; if (arr[mid] < x) lo = mid + 1; else hi = mid; } return lo; }
function bisectRight(arr, x){ let lo = 0, hi = arr.length; while (lo < hi){ const mid = (lo + hi) >> 1; if (arr[mid] <= x) lo = mid + 1; else hi = mid; } return lo; }
function sentIdx(sents, pos){
  const starts = sents.map(s => s.start);
  return Math.max(bisectRight(starts, pos) - 1, 0);
}
function findSpans(folded){
  const spans = [];
  for (const m of folded.matchAll(/"([^"]{1,200})"/g))
    spans.push([m.index, m.index + m[0].length, m[1], '"']);
  for (const m of folded.matchAll(/(?<![A-Za-z])'([^']{1,200})'(?![A-Za-z])/g))
    spans.push([m.index, m.index + m[0].length, m[1], "'"]);
  spans.sort((a, b) => a[0] - b[0] || (b[1] - b[0]) - (a[1] - a[0]));
  const out = []; let lastEnd = -1;
  for (const s of spans) if (s[0] >= lastEnd){ out.push(s); lastEnd = s[1]; }
  return out;
}
function hedgeCensus(text){
  let total = 0; const loci = [];
  const termsAll = [...HEDGE_SINGLES, ...HEDGE_PHRASES];
  for (const [si, s] of splitSentences(text).entries()){
    const stext = s.text, toks = toksOf(stext), hits = [];
    const n = countTerms(stext, termsAll);
    if (n){
      const low = " " + stext.toLowerCase().replace(/[^a-z0-9' ]/g, " ") + " ";
      for (const t of termsAll){
        let c = 0;
        if (t.includes(" ")) c = low.split(" " + t + " ").length - 1;
        else { const mm = low.match(new RegExp("\\b" + escRe(t) + "\\b", "g")); c = mm ? mm.length : 0; }
        if (c) hits.push(t + " x" + c);
      }
      total += n;
    }
    let modalN = 0;
    toks.forEach((tk, i) => {
      if (!HEDGE_MODALS.has(tk)) return;
      if (tk === "could" && toks[i+1] === "be" && toks[i+2] === "argued") return;
      modalN++;
    });
    if (modalN){ hits.push("modal x" + modalN); total += modalN; }
    let vagueN = 0;
    toks.forEach((tk, i) => {
      if (!VAGUE_QUANTS.has(tk)) return;
      const guard = toks.slice(i + 1, i + 3);
      if (guard.some(g => /\d/.test(g) || NUMBER_WORDS.has(g) || g.endsWith("%"))) return;
      vagueN++;
    });
    if (vagueN){ hits.push("vague-quantifier x" + vagueN); total += vagueN; }
    const appeals = stext.toLowerCase().match(APPEAL_RE) || [];
    if (appeals.length){ hits.push("unattributed-authority x" + appeals.length); total += appeals.length; }
    if (hits.length){
      const neg = toks.some(t => NEGATORS.has(t));
      loci.push({ sentence: si, kind: "HEDGE",
        detail: hits.join("; ") + (neg ? " [under negation — the count stands; the frame is denial]" : ""),
        excerpt: stext.slice(0, 90) });
    }
  }
  return { total, loci };
}
function contextLayer(text){
  const folded = foldText(text);
  const spans = findSpans(folded);
  const ranges = spans.map(s => [s[0], s[1]]);
  const inside = (p) => ranges.some(([a, b]) => a <= p && p < b);
  const terms = [];
  for (let i = 0; i < folded.length; i++)
    if (".!?".includes(folded[i]) && !inside(i)) terms.push(i);
  const masked = [...folded];
  const outSpans = [];
  let adjustment = 0;
  for (const [a, b, content, q] of spans){
    const k = bisectLeft(terms, a);
    const leadStart = k > 0 ? terms[k - 1] + 1 : 0;
    const lead = folded.slice(leadStart, a);
    const trailEnd = k < terms.length ? terms[k] + 1 : folded.length;
    const trail = folded.slice(b, trailEnd);
    const leadToks = toksOf(lead), trailToks = toksOf(trail);
    const cueWindow = leadToks.slice(-8);
    const mention = cueWindow.some(t => MENTION_CUES.has(t));
    const leadWords = lead.match(/[A-Za-z][A-Za-z'-]*/g) || [];
    const leadCaps = leadWords.slice(1).filter(t => /^[A-Z]/.test(t) && !ENTITY_STOP.has(t.toLowerCase()));
    const attributed = [...leadToks, ...trailToks.slice(0, 6)].some(t => SPEECH.has(t))
      || leadCaps.length > 0 || leadToks.includes("according");
    const words = toksOf(content).length;
    let kind;
    if (mention) kind = "MENTION";
    else if (attributed) kind = "QUOTED";
    else if (words <= 2) kind = "SCARE";
    else kind = "UNATTRIBUTED";
    let internal = {};
    if (kind === "MENTION" || kind === "QUOTED"){
      const dIn = countTerms(content, EVASION);
      const sIn = structureLoad(content).load;
      let pIn = (content.split("…").length - 1)
        + (content.match(/\.\.\./g) || []).length
        + (content.split("!").length - 1);
      if (words <= 2 && q === '"') pIn += 1;
      internal = { D: dIn, structure: sIn, punct: pIn, hedge: hedgeCensus(content).total };
      adjustment += dIn + sIn + pIn;
      for (let i = a; i < b; i++) if (masked[i] !== "\n") masked[i] = " ";
    }
    outSpans.push({ start: a, end: b, content, kind, words, quote: q,
                    sentence: bisectLeft(terms, a), internal });
  }
  return { spans: outSpans, masked: masked.join(""), adjustment,
    unattributed: outSpans.filter(s => s.kind === "UNATTRIBUTED").length,
    scare_single: outSpans.filter(s => s.kind === "SCARE" && s.quote === "'").length,
    quoted: outSpans.filter(s => s.kind === "QUOTED"),
    mentions: outSpans.filter(s => s.kind === "MENTION") };
}
function isPart(tok){ return (tok.length >= 3 && tok.endsWith("ed")) || IRREG_EXT.has(tok); }
function extPassivesIn(toks){
  let n = 0; const tagged = [];
  let i = 0;
  while (i < toks.length){
    const tok = toks[i];
    if (AUX_EXT.has(tok)){
      let j = i + 1, skips = 0;
      while (j < toks.length && skips < 3 &&
             (SKIPSET.has(toks[j]) || (toks[j].length > 3 && toks[j].endsWith("ly")))){
        j++; skips++;
      }
      if (j < toks.length && isPart(toks[j])){
        const by = toks.slice(j + 1, j + 5).includes("by");
        n++; tagged.push(by ? "demoted-by" : "agentless");
        i = j + 1; continue;
      }
    }
    if (MODALS_BE.has(tok) && toks[i+1] === "be" && isPart(toks[i+2] || "")){
      const by = toks.slice(i + 3, i + 7).includes("by");
      n++; tagged.push("modal-be" + (by ? "+by" : ""));
      i = i + 3; continue;
    }
    i++;
  }
  return [n, tagged];
}
function passiveExtension(masked, sealedPassives){
  let total = 0; const loci = [];
  for (const [si, s] of splitSentences(masked).entries()){
    const [n, tagged] = extPassivesIn(toksOf(s.text));
    if (n){
      total += n;
      loci.push({ sentence: si, kind: "PASSIVE-EXT",
        detail: "x" + n + " (" + tagged.join(", ") + ")", excerpt: s.text.slice(0, 90) });
    }
  }
  return { total, extra: Math.max(0, total - sealedPassives), loci };
}
function nominalizationCensus(masked){
  let total = 0; const loci = [];
  const rx = /\bthe\s+([a-z]+(?:tion|sion|ment|ance|ence|ness))\s+of\b/g;
  for (const [si, s] of splitSentences(masked).entries()){
    const found = [...s.text.toLowerCase().matchAll(rx)].map(m => m[1]);
    if (found.length){
      total += found.length;
      loci.push({ sentence: si, kind: "NOMINALIZED-ACT",
        detail: found.join(", "), excerpt: s.text.slice(0, 90) });
    }
  }
  return { total, loci };
}
function capsEmphasis(text){
  let total = 0; const lines = [];
  for (const [li, line] of text.split("\n").entries()){
    const toks = line.match(/[A-Za-z]+/g) || [];
    if (!toks.length) continue;
    const caps = toks.filter(t => /^[A-Z]{3,}$/.test(t));
    if (!caps.length) continue;
    if (caps.length / toks.length >= 0.5) continue;
    for (const m of line.matchAll(/[A-Z]{3,}/g)){
      const rest = line.slice(m.index + m[0].length).trimStart();
      if (rest.startsWith(":")) continue;
      total++; lines.push([li, m[0]]);
    }
  }
  return { total, lines };
}
function punctuationExtension(masked){
  const sents = splitSentences(masked);
  const loci = [];
  const add = (pos, kind, detail) => loci.push({ sentence: sentIdx(sents, pos), kind, detail, excerpt: "" });
  let em = 0;
  for (const m of masked.matchAll(/[—–]/g)){ em++; add(m.index, "EM-DASH-ASIDE", "—"); }
  const tmp2 = masked.replaceAll("…", " ").replaceAll("...", " ");
  let twoDot = 0;
  for (const m of tmp2.matchAll(/\.\./g)){ twoDot++; add(m.index, "TRAIL-OFF", ".."); }
  let clusters = 0;
  for (const m of masked.matchAll(/([.!?])([!?]+)/g)){
    clusters += m[2].length; add(m.index, "TERMINAL-CLUSTER", m[0]);
  }
  let misplaced = 0;
  for (const m of masked.matchAll(/[.!?]\s+[a-z]/g)){
    misplaced++; add(m.index, "MISPLACED-TERMINAL", m[0].trim());
  }
  let slash = 0;
  for (const m of masked.toLowerCase().matchAll(/\b[a-z]+\/[a-z]+\b/g)){
    slash++; add(m.index, "SLASH-CONSTRUCTION", m[0]);
  }
  let emph = 0;
  for (const m of masked.matchAll(/\*+[^*\n]+\*+|_[^_\n]+_/g)){
    emph++; add(m.index, "EMPHASIS-WRAPPER", m[0].slice(0, 24));
  }
  let parens = 0;
  for (const m of masked.matchAll(/\(([^)]*)\)/g)){
    if (toksOf(m[1]).length >= 3){ parens++; add(m.index, "PARENTHETICAL-ASIDE", "(" + m[1].slice(0, 40) + ")"); }
  }
  let chains = 0, deq = 0;
  for (const [si, s] of sents.entries()){
    const semis = (s.text.match(/;/g) || []).length;
    if (semis >= 2){
      chains += semis - 1;
      loci.push({ sentence: si, kind: "SEMICOLON-CHAIN",
        detail: semis + " semicolons in one sentence", excerpt: s.text.slice(0, 90) });
    }
    if (s.term.startsWith("?")){
      const toks = toksOf(s.text);
      if (toks.length && !INTERROG.has(toks[0]) && !toks.slice(0, 4).some(t => INTERROG.has(t))){
        deq++;
        loci.push({ sentence: si, kind: "DECLARATIVE-QUESTION",
          detail: "a declaration wearing a question mark", excerpt: s.text.slice(0, 90) });
      }
    }
  }
  const capsR = capsEmphasis(masked);
  for (const [li, w] of capsR.lines)
    loci.push({ sentence: li, kind: "CAPS-EMPHASIS", detail: w, excerpt: "" });
  const total = em + twoDot + clusters + misplaced + slash + emph + parens
    + chains + deq + capsR.total;
  const parts = { em_dash: em, two_dot: twoDot, clusters, misplaced_terminal: misplaced,
    slash, emphasis: emph, parenthetical: parens, semicolon_chains: chains,
    declarative_questions: deq, caps: capsR.total };
  return { total, parts, loci };
}
function auditV4(text, b, struct, punct39){
  const sealedCont = b.D + struct.load + punct39.total;
  const ctx = contextLayer(text);
  const hostBase = Math.max(0, sealedCont - ctx.adjustment);
  const hed = hedgeCensus(ctx.masked);
  const pext = passiveExtension(ctx.masked, struct.passives);
  const nom = nominalizationCensus(ctx.masked);
  const px = punctuationExtension(ctx.masked);
  const scareSingle = ctx.scare_single;
  const evasion = b.D + hed.total;
  const structure = struct.load + pext.extra + nom.total;
  const punct = punct39.total + px.total + scareSingle;
  const context = ctx.unattributed;
  const contamination = hostBase + hed.total + pext.extra + nom.total
    + px.total + scareSingle + context;
  const loci = [...hed.loci, ...pext.loci, ...nom.loci, ...px.loci]
    .sort((x, y) => x.sentence - y.sentence);
  return { sealed_contamination: sealedCont, host_base: hostBase,
    adjustment: ctx.adjustment, context: ctx, hedge: hed, passive_ext: pext,
    nominalization: nom, punct_ext: px, scare_single: scareSingle,
    evasion_v4: evasion, structure_v4: structure, punct_v4: punct,
    context_v4: context, contamination,
    verdict: contamination === 0 ? "TRUE" : "DECEPTIVE", loci };
}


/* ---------- categorical law ---------- */
function categorize(b, struct, script, ext){
  if (b.words === 0) return ["EMPTY", "no words in the input; absence of input, not a verdict"];
  const fused = script.fusion_count ? " · SCRIPT-FUSED x" + script.fusion_count : "";
  if (!(b.S === 0 && b.D === 0)) return [null, fused];
  if (struct.load > 0)
    return ["PSEUDO-NEUTRAL" + fused, "battery silent (S 0, D 0) over a loaded structure (load " + struct.load +
      ": passives " + struct.passives + ", gaps " + struct.gap + ", indefinite actors " +
      struct.indefinite_actors + ") — the neutrality is performed"];
  if (ext.apophatic_total >= 2)
    return ["APOPHATIC" + fused, "battery silent; the text is built from negation (apophatic census " +
      ext.apophatic_total + ") — it states by unsaying"];
  const density = (ext.figures_total + ext.poetic_hits) / b.words * 1000;
  if (ext.poetic_hits >= 3 && density >= 20)
    return ["CREATIVE" + fused, "battery silent; figure + poetic density " + density.toFixed(1) +
      "/1k words (figures " + ext.figures_total + ", poetic hits " + ext.poetic_hits +
      ") — the text works by image and figure"];
  if (ext.has_arithmetic)
    return ["SELF-EVIDENT" + fused, "battery silent; arithmetic content present (numerals " +
      ext.numerals + "), figures " + ext.figures_total + " — the text verifies against itself"];
  return ["DIRECTLY OBSERVABLE" + fused, "every census at zero — battery, structure, figures, apophatic, script; the text states and nothing rides underneath"];
}

const CATEGORY_ACT = {
  "PSEUDO-NEUTRAL": "The surface performs neutrality while the structure moves the actor out of the sentence; custody and consequence travel with the deleted actor.",
  "APOPHATIC": "The text governs by negation: what it refuses to state directly is the load it carries.",
  "CREATIVE": "The text performs image and figure; its assertions ride the figures and are carried by them.",
  "SELF-EVIDENT": "The text's content verifies against its own numbers; no external warrant is invoked or needed.",
  "DIRECTLY OBSERVABLE": "No transfer counted: the text states its content and performs nothing underneath the statement.",
  "EMPTY": "No text was given; no operation applies.",
};
const STEPS = ["battery","verdict-pair","script-sensor","extension-census","intent-census","context-layer","punctuation-census","contamination-v4","final-verdict","categorize","decryption-render"];

function audit(text){
  const b = battery(text);
  const struct = structureLoad(text);
  const script = scriptSensor(text);
  const ext = extensionCensus(text);
  const ic = intentCensus(text, struct);
  const [iv, iground] = intentVerdict(ic);
  const chain = intentChain(ic);
  const punct = punctuationCensus(text);
  const fv = finalVerdict(b, struct, punct);
  const v4 = auditV4(text, b, struct, punct);
  const fv4 = { contamination: v4.contamination, verdict: v4.verdict,
    evasion: v4.evasion_v4, structure: v4.structure_v4, punctuation: v4.punct_v4,
    context: v4.context_v4, sealed_contamination: v4.sealed_contamination,
    host_base: v4.host_base, adjustment: v4.adjustment, scare_single: v4.scare_single };
  const [category, ground] = categorize(b, struct, script, ext);
  const pair = b.status + " x " + struct.cls;
  const statusLine = category === null ? pair : category + " (battery-zero slot, categorical law)";
  const dec = [];
  if (fv4.verdict === "TRUE")
    dec.push("FINAL VERDICT: TRUE — structural condition " + b.status + "; contamination zero across every census (evasion 0 · structure 0 · punctuation 0 · context 0). The body stands entire: no word in it carries a contaminant, and no contaminant touches the words around it.");
  else
    dec.push("FINAL VERDICT: DECEPTIVE — structural condition " + b.status + "; contamination " + fv4.contamination +
      " (evasion " + fv4.evasion + " · structure " + fv4.structure + " · punctuation " + fv4.punctuation +
      " · context " + fv4.context + "). The contaminant proliferates through the entire body: every word stands in the company the contaminant keeps, and the whole text stands judged — never the instance alone.");
  if (category === null)
    dec.push("VERDICT PAIR: " + pair + " — the battery governs this text; the categorical law is not invoked. What the text performs rides in the STRUCTURE half of the pair.");
  else {
    dec.push("CATEGORY: " + category + " — " + ground + ".");
    const base = category.split(" ·")[0].split(" ")[0];
    if (CATEGORY_ACT[base]) dec.push(CATEGORY_ACT[base]);
  }
  if (struct.passives)
    dec.push("ACTORS DELETED: " + struct.passives + " agentless passive(s) — " +
      struct.passiveSents.slice(0, 4).map(s => '"' + s + '"').join(" | ") +
      ". The actor exists in the world; the sentence holds the act without the hand.");
  else dec.push("ACTORS DELETED: NONE COUNTED.");
  if (struct.indefinite_actors)
    dec.push("ACTORS INDEFINITE: " + struct.indefinite_actors + " — an actor class is named and no actor is: the role stands, the person never arrives.");
  else dec.push("ACTORS INDEFINITE: NONE COUNTED.");
  dec.push(struct.gap
    ? "ENUMERATION GAP: " + struct.gap + " announced element(s) never delivered in the text that announced them."
    : "ENUMERATION GAP: NONE COUNTED.");
  dec.push("INTENT: " + iv + " — " + iground + ".");
  dec.push("INTENT CHAIN: ACTOR: " + chain.actor + " | MECHANISM: " + chain.mechanism +
           " | CONSEQUENCE: " + chain.consequence + " | BENEFICIARY: " + chain.beneficiary + ".");
  dec.push("CULPABILITY ANCHOR: " + chain.anchor);
  if (ic.transfer_reader.length)
    dec.push("TRANSFER TO READER: " + ic.transfer_reader.slice(0, 3).map(t => '"' + t + '"').join("; ") +
             " — cost and caution land on the reader.");
  if (script.fusion_count)
    dec.push("SCRIPT FUSIONS: " + script.fusion_count + " word(s) carry two scripts in one body — " +
      script.fusions.slice(0, 6).map(([t, s]) => '"' + t + '" (' + s + ")").join(", ") +
      ". The fusion is the datum: one word, two writing systems.");
  else dec.push("SCRIPT FUSIONS: NONE COUNTED.");
  if (ext.letter_field)
    dec.push("DOMINANT LETTER FIELD: " + ext.dominant_letter + " — " + ext.letter_field.meaning +
             " (" + ext.letter_field.cluster.join(", ") + ") [GENERATED ASSOCIATION]");
  for (const s of v4.context.quoted)
    dec.push('QUOTED TO SOURCE: "' + s.content.slice(0, 60) + '" — a source stands in the text beside the span; the span is charged to that source (internal census D ' +
      s.internal.D + " · structure " + s.internal.structure + " · punctuation " + s.internal.punct +
      " · hedge " + s.internal.hedge + "); the host carries none of it.");
  for (const s of v4.context.mentions)
    dec.push('MENTION, NOT USE: "' + s.content.slice(0, 60) + '" — the text names the term; naming is not using, and the span leaves the host census.');
  for (const s of v4.context.spans)
    if (s.kind === "UNATTRIBUTED")
      dec.push('UNATTRIBUTED QUOTATION: "' + s.content.slice(0, 60) + '" — no source stands in the text; the host carries the span as its own words.');
  if (v4.loci.length){
    const L0 = v4.loci[0];
    dec.push("FIRST LOCUS: sentence " + (L0.sentence + 1) + " — " + L0.kind + ": " + L0.detail +
      ". The body is judged entire from the first locus: " + b.words + " words stand in the company the contaminant keeps.");
  }
  const work = [];
  work.push("BATTERY words " + b.words + " | S " + b.S + " | D " + b.D + " | PIC " + b.pic +
            " | T_d " + b.td + " | " + statusLine);
  work.push("SCRIPT scripts " + JSON.stringify(script.counts) + " | transitions " + script.transitions +
            " | fusions " + script.fusion_count + " (" + script.fusion_per_1k_chars + "/1k chars) | non-latin share " + script.non_latin_share);
  work.push("CENSUS figures " + JSON.stringify(ext.figures) + " total " + ext.figures_total +
            " | poetic " + ext.poetic_hits + " | apophatic " + JSON.stringify(ext.apophatic) +
            " total " + ext.apophatic_total + " | numerals " + ext.numerals);
  work.push("STRUCTURE passives " + struct.passives + " | gap " + struct.gap + " | refusal " + struct.refusal +
            " | service " + struct.service + " | indefinite actors " + struct.indefinite_actors + " | load " + struct.load);
  work.push("INTENT " + iv + " | conceal " + ic.conceal + " (deleted " + ic.deleted_actors + ", indefinite " +
            ic.indefinite_actors + ", gap " + ic.gap + ") | flows " + JSON.stringify(ic.flows) +
            " | benefit-author " + ic.benefit_author.length + " | benefit-reader " + ic.benefit_reader.length +
            " | transfer-reader " + ic.transfer_reader.length + " | entities " + JSON.stringify(ic.entities));
  work.push("PUNCTUATION ellipsis " + punct.ellipsis + " | scare quotes " + punct.scare_quotes +
            (punct.scare_spans.length ? " (" + punct.scare_spans.slice(0, 6).map(s => '"' + s + '"').join("; ") + ")" : "") +
            " | exclamation " + punct.exclamation + " | total " + punct.total);
  work.push("CONTAMINATION (sealed body, v3.9 law) evasion " + fv.evasion + " + structure " + fv.structure + " + punctuation " +
            fv.punctuation + " = " + fv.contamination + " | sealed verdict: " + fv.verdict +
            " (structural condition " + b.status + ")");
  work.push("CONTEXT spans " + v4.context.spans.length + " | quoted " + v4.context.quoted.length +
            " | mentions " + v4.context.mentions.length + " | scare-single " + v4.scare_single +
            " | unattributed " + v4.context_v4 + " | sealed adjustment -" + v4.adjustment);
  work.push("EXTENSION hedge " + v4.hedge.total + " | passive-ext total " + v4.passive_ext.total +
            " (extra " + v4.passive_ext.extra + ") | nominalized acts " + v4.nominalization.total +
            " | punctuation-ext " + v4.punct_ext.total + " " + JSON.stringify(v4.punct_ext.parts));
  work.push("CONTAMINATION v4 host-base " + v4.host_base + " + hedge " + v4.hedge.total +
            " + passive-extra " + v4.passive_ext.extra + " + nominalization " + v4.nominalization.total +
            " + punctuation-ext " + v4.punct_ext.total + " + scare-single " + v4.scare_single +
            " + context " + v4.context_v4 + " = " + v4.contamination +
            " | FINAL VERDICT (v4.0): " + v4.verdict);
  for (const L of v4.loci.slice(0, 40))
    work.push("LOCUS s" + (L.sentence + 1) + " " + L.kind + " — " + L.detail + (L.excerpt ? " :: " + L.excerpt : ""));
  return { battery: b, structure: struct, script, ext, intent: ic, intentVerdict: iv,
           intentGround: iground, chain, category, ground, pair, statusLine,
           punct, final: fv4, sealedFinal: fv, v4,
           decryption: dec, work, steps: STEPS.slice() };
}

function report(text){
  const a = audit(text);
  const out = [];
  out.push("=".repeat(72));
  out.push("DECRYPTION");
  out.push(...a.decryption);
  out.push("-".repeat(72));
  out.push("THE WORK");
  out.push(...a.work);
  return out.join("\n");
}

return { battery, structureLoad, scriptSensor, extensionCensus, intentCensus,
         intentVerdict, intentChain, punctuationCensus, finalVerdict,
         contextLayer, hedgeCensus, auditV4,
         categorize, audit, report, STRUCTURAL, EVASION, STEPS };
})();
if (typeof module !== "undefined" && module.exports) module.exports = AEE;
