# Browser runtime notices

The decision room uses the actual repository Python core, not a JavaScript approximation. It runs in a dedicated browser worker through Pyodide 0.27.7 (CPython/WebAssembly).

The five files under `runtime/` were retrieved from the pinned upstream distribution at https://cdn.jsdelivr.net/pyodide/v0.27.7/full/ on 2026-11-01. They are hosted with this site, not loaded from a third-party CDN at runtime. Pyodide's upstream license is preserved in `runtime/LICENSE`. CPython’s license is preserved separately in `runtime/PYTHON-LICENSE`; see also https://docs.python.org/3/license.html and https://pyodide.org/en/0.27.7/project/about.html.

These assets total about 14 MB. The first engine start downloads them from the same origin. The analyzer has no model calls or application text-upload endpoint. The site host still receives ordinary asset requests and may retain access logs. Browser extensions and a modified host are outside this application's control.

Serve the complete package over HTTP(S), including `prime/aee_logodecrypt_prime.py`. Opening `lab.html` directly with a `file://` URL is not supported because browsers restrict workers and fetches. `index.html` remains the self-contained static walkthrough for direct-file viewing.

The engine bridge accepts up to 40,000 combined source/candidate characters, with 20,000 per field in the interface. Generated associations use the core's token cap of 12. Results and inputs live only in page/worker memory; downloads occur only when selected. Reloading clears them.
