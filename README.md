# AEE and LOGODECRYPT tools

A collection of Nathaniel Jaffe-Norris’s Aletheiac-Entropy Engine and LOGODECRYPT software variants and specifications.

- `aee/reference-prototypes/`: original Python prototype files.
- `aee/v4-commercial-suite/`: developer, streaming, enterprise, sovereign and visual components from the v4 suite.
- `aee/bittensor-experimental/`: experimental crypto/subnet scripts; no live integration is claimed here.
- `logodecrypt/payloads-and-specifications/`: versions 0.1–0.9 and an apparatus specification.

These materials are research prototypes. Their labels, signatures and text-pattern outputs are not independent verification of truth, intent, security, market predictions or performance. Evaluate before production use. The corpus and data-bearing fine-tuning materials are not included.

This is an initial selection from files accessible through the connected Drive, not a complete export. The components are preserved as supplied; dependencies, licensing and runnable status may vary.

## GitHub agent workflow scaffold

The Chassis v7 → Mistral Vibe → optional ChainGPT scaffold is in [`integrations/wabi-vibe-chaingpt/`](integrations/wabi-vibe-chaingpt/), with a GitHub Actions workflow at [`.github/workflows/wabi-vibe-chaingpt.yml`](.github/workflows/wabi-vibe-chaingpt.yml). The automated CI path runs tests without provider credentials; the real-provider job requires a private repository and owner-provisioned API secrets. See the integration README for scope and setup.
