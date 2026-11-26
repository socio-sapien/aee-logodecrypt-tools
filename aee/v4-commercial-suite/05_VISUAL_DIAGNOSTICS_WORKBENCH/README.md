# AEE Visual Diagnostics & Interactive Dashboard [Visual Suite]
### Subtitle: Standalone Web Workbench, Live Gauges & Interactive Shatter GUI

## Overview
The Visual Suite provides an intuitive, high-fidelity visual interface for forensic scriveners, legal auditors, and non-technical executives. Features real-time visual gauges for Truth Decay ($T_d$), Phonetic Influence Coefficient ($PIC$), Shannon Entropy, live text reconstruction, and the iconic Cryptographic Shatter visual representation.

## Key Artifacts
- `oracle_app_ui.html`: Comprehensive single-page HTML5/JS forensic diagnostic workbench with real-time gauges, history ledger, and certificate exporter.
- `oraclepal_standalone.html`: Ultralight mobile-responsive diagnostic utility.
- `aee_fidelity_cli_ui.py`: Interactive ANSI terminal dashboard for power-users in terminal environments.
- `skeletal_web_schema.html`: Minimalist embeddable HTML/JavaScript widget for dropping into existing web apps.

## Usage
Simply double-click `oracle_app_ui.html` to open directly in any modern web browser (Chrome, Firefox, Safari, Edge) with zero web server setup required.
For terminal UI:
```bash
python3 aee_fidelity_cli_ui.py
```

## Scope and safety

These interfaces are experimental prototypes, not verified truth or deception detectors. The minimal gauge uses word lists; its labels do not establish truth, deception, intent, or accuracy. The standalone interface contains scripted responses and illustrative operational and credential strings, not evidence of a working model, device, or signing key. The connected interface attempts to send entered prompts and audit text to a loopback service at `http://127.0.0.1:8080`; its displayed fallback and metrics do not establish that a backend or model is running. Review the local service and avoid entering sensitive text unless you trust it. The pages use an external Tailwind script and are not a security-hardened deployment.
