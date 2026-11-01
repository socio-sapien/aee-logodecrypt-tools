# PRIME Demonstration Environment

A public, self-contained customer demonstration for AEE × LOGODECRYPT PRIME. It makes the tool's strongest verifiable behavior legible while showing the boundaries that a credible evaluation must preserve.

## Open the demo

**Start with `lab.html`: the decision room and live browser analyzer.** Serve the repository root with `python3 -m http.server 8000`, then open `http://localhost:8000/prime/demo-environment/lab.html`. The bundled Pyodide worker runs the actual Python core on editable source/candidate pairs. It includes three guided decisions, all eleven fixtures, a visible known miss, exact JSON and review-brief downloads, and a collaboration kit. The first engine start loads about 14 MB of same-origin assets; no text is uploaded by the application. See `RUNTIME_NOTICES.md`.

On the published site, the root opens the decision room directly. The gallery remains available at `index.html`.

### Static gallery


Open `index.html` in a browser. It is static and self-contained: no network calls, login, hosted model, tracking, or personal data. `scenario-results.json` is the machine-readable PRIME output for eleven constructed fixtures; they are not customer evidence, live market data, or observed system incidents. Three separately linked public-record briefs appear on the page with source and date. PRIME has not analyzed those records.

## Rebuild and verify

From the repository root, with Python 3.10+:

```sh
python3 prime/demo-environment/build_demo.py
python3 prime/demo-environment/build_demo.py --check
python3 prime/aee_logodecrypt_prime.py --self-test
```

The builder imports the actual local PRIME module, runs each supplied candidate against its paired context/frame, verifies each unsigned receipt, and regenerates both public artifacts. `--check` fails if the committed HTML or JSON has drifted from the scenario manifest and engine. No third-party package is needed.

## Suggested customer walkthrough

1. Start with `01`: the refund amount stays fixed while the status reverses. Let the audience inspect the source and candidate side by side, then show the exact curated polarity cue.
2. Move to `02`: a release summary conflicts with its synthetic test receipt. Ask what source ID and timestamp would prove the real handoff; do not call a text cue a deployment block.
3. Use `04` to show what a privacy frame matches and what it leaves open. “No cue match in this excerpt” is a review prompt, not proof the policy lacks the term.
4. Use `05` to reveal code points that visual rendering can conceal. The character/control census identifies text properties, not an attack or exploitable weakness.
5. Use `07` to contrast quoted evidence with a generated lexical alternative. The alternative is a tool-generated illustration, not recovered intent.
6. Use `08` for the smart-contract handoff: one synthetic authorization test and the draft summary disagree on count, test status, and release state. PRIME flags the literal changes; a reviewer still needs the code revision, test run, network, and chain of custody.
7. Use `10` for the agent-execution status mismatch: a constructed dry run with zero broadcasts is paired with a draft summary reporting one live transaction. Ask for a signed transaction, chain/block, authorization test, and settlement receipt; no real transaction is shown.
8. Use `11` for oracle freshness: the block reference is unchanged while the test and update statuses flip. A real review would need the signed update time, source identity, and protocol rule version—not just a matching number.
9. End with `09`: the counts trade places while the number multiset and both polarity words remain. PRIME reports no selected cue difference. This known miss is part of the demo, not a footnote.
10. Open “Impact map” to follow each synthetic consequence from individual to workflow, industry, market, and second-order reuse. The evidence note states that real effects and demand have not been measured; PRIME detects text cues, not downstream outcomes. The public-record briefs are linked context, not PRIME results.

The walkthrough opens on a person, follows the consequence through widening handoffs, then reveals a known miss. Ready to test it? Start the prototype, then use [`CUSTOMER_PILOT.md`](CUSTOMER_PILOT.md) to propose a bounded evaluation with authorized traces and independent reviewers.

## What the demo demonstrates—and does not

The analyzer provides literal text measurements, a bounded frame checklist, number-multiset and curated-polarity comparisons, a range-based script/control census, explicitly labeled transformations, and deterministic local SHA-256 integrity receipts. The contract-security example is synthetic and shows text discrepancies, not a vulnerability assessment. The included test suite is implementation/smoke coverage, not an independent accuracy or performance benchmark.

It does not establish semantic equivalence, authorship, intent, truth, legal meaning, exploitability, market performance, causal propagation, customer demand, or integrations in live services. A matching word, an unmatched checklist cue, or a hash is not proof of those things. The output is unsigned; it does not authenticate who created the text or independently attest to it.

## Files

- `index.html` — polished, accessible, interactive static walkthrough.
- `index.template.html` — editable source for the page.
- `social-preview.png` — 1200×630 public-share artwork.
- `scenarios.json` — synthetic evidence pairs and scenario-specific consequence maps and illustrative 1 → 2 → 4 → 8 cascade stories.
- `public-records.json` — three dated summaries linked to official institutional records; these texts are not analyzed by PRIME.
- `scenario-results.json` — complete locally computed receipts/results.
- `build_demo.py` — deterministic builder and drift check.
- `CUSTOMER_PILOT.md` — a bounded evaluation plan with independent labels and decision gates.

### Browser regression check

Run `uv run --with playwright==1.58.0 python prime/demo-environment/test_browser.py` after installing that Playwright version's Chromium (`uv run --with playwright==1.58.0 python -m playwright install chromium`). CI runs the same browser test. It exercises the decision paths, every fixture against native Python, receipt verification, editable text, downloads, no-source/empty/XSS-text states, and mobile layout and runtime. Set `PRIME_DEMO_BASE_URL` to test an actual hosted deployment. This tests implementation, not independent accuracy or persuasion.

Exact JSON exports preserve Python's original serialization (including float representation); reserializing through JavaScript can otherwise break the unsigned output digest. The WebWorker returns both parsed display data and the original JSON string.
