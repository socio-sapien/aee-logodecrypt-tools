# Experimental Bittensor examples

These scripts are prototypes, not a verified live Bittensor integration. In `bittensor_subnet_automator.py`, connection errors now return false and failed or absent metagraph sync raises an error instead of returning simulated miners. The old validation loop generated its own payloads, not miner responses; it now raises `NotImplementedError` and its CLI exits nonzero. These changes break callers that depended on the simulated fallback. No on-chain weights are submitted and live Bittensor compatibility has not been tested.

The validator applies heuristic entropy thresholds. Its labels and weights do not establish fraud, deception, output truth, or miner quality. Do not use these examples to allocate real incentives or make financial/security decisions without independent validation and implementation review.

## Validator input and output limitations

Offline synthetic tests found these behaviors in `aee_bittensor_subnet_validator.py`:

- String encoding silently drops unpaired Unicode surrogates before hashing. Different input strings can therefore have the same encoded bytes and digest; this is not a SHA-256 collision.
- Non-finite thresholds can produce non-finite weights; such output is not valid strict JSON.
- An unrecognized network name falls back to the Finney endpoint while the object retains the unrecognized name. The validator does not itself establish a connection or submit weights.
- Independently rounded normalized weights may not sum to 1. For three equal weights, the synthetic test returned 0.9999. Downstream acceptance was not tested.

These are warnings, not fixes. Input limits, deployed compatibility, security, and network behavior have not been established by these tests.
