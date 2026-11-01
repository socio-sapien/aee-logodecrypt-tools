# Decision-room validation

The decision room is a browser interface to the existing PRIME 1.0.0 deterministic Python core, not a replacement scoring engine.

## Reproduced before publication

- The committed gallery rebuild check verifies all eleven constructed fixtures and their integrity records.
- The repository suite passes 94 tests.
- The original PRIME core passes 36 self-tests in native Python and in the browser worker.
- The Playwright browser regression passes 28 checks in Chromium 145 (Playwright 1.58.0), including exact native-Python result parity and digest verification for all eleven fixtures, custom input, source-off and empty input, inert HTML text, stale-result hiding, JSON/review/collaboration downloads, desktop and 390px mobile flows, and the real mobile worker.
- Exercised browser requests are same-origin GETs. The application does not upload entered text or call an external model.
- The actual desktop and mobile pages were visually inspected.

`test_browser.py` is the reproducible browser check and also runs in the Pages build. Its output is written to `/tmp/prime-demo-browser-validation`. Set `PRIME_DEMO_BASE_URL` to a hosted root to repeat it on the deployment.

## What these checks do not establish

No independent semantic-accuracy study, downstream outcome measurement or conversion/persuasion test has occurred. The role-assignment reversal remains an explicit known miss. Scenario consequence paths are constructed illustrations. The separate public-record briefs are source-linked context, not PRIME analyses. Receipts are unsigned integrity records, not provenance attestation.

The worker downloads approximately 14 MB of bundled Python runtime from the same site on first start. WebAssembly and WebWorkers are required; startup depends on the browser/device. Browser testing here covers Chromium, not every browser or screen reader. Input fields each accept up to 20,000 JavaScript characters, with a combined 40,000-character check; long inputs may be slower. Generated transformations are bounded to twelve tokens in this core configuration. No files persist until the viewer downloads them.
