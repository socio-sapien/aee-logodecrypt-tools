# Experimental Bittensor examples

These scripts are prototypes, not a verified live Bittensor integration. In `bittensor_subnet_automator.py`, connection errors now return false and failed or absent metagraph sync raises an error instead of returning simulated miners. The old validation loop generated its own payloads, not miner responses; it now raises `NotImplementedError` and its CLI exits nonzero. These changes break callers that depended on the simulated fallback. No on-chain weights are submitted and live Bittensor compatibility has not been tested.

The validator applies heuristic entropy thresholds. Its labels and weights do not establish fraud, deception, output truth, or miner quality. Do not use these examples to allocate real incentives or make financial/security decisions without independent validation and implementation review.
