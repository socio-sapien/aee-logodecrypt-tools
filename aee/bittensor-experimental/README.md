# Experimental Bittensor examples

These scripts are prototypes, not a verified live Bittensor integration. In `bittensor_subnet_automator.py`, a missing Bittensor package or a connection exception makes `connect_network` return success, and `sync_metagraph` can return four simulated miners without an active connection. Its printed telemetry must not be treated as evidence of a connection or live miner data. The example prepares and prints weight vectors; it does not submit them on-chain.

The validator applies heuristic entropy thresholds. Its labels and weights do not establish fraud, deception, output truth, or miner quality. Do not use these examples to allocate real incentives or make financial/security decisions without independent validation and implementation review.
