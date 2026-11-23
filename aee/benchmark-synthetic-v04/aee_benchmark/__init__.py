"""AEE Benchmark package.

Aletheiac Entropy Engine (AEE) v0.4 structural hedging metrics:
Truth Decay (T_d), Phonetic Influence Coefficient (PIC), structural
anchor density, hedging marker counts, and deterministic verdicts.
"""

from .plugin import (
    AEEAuditor,
    METRTaskScorer,
    S_SET,
    D_SET,
    ELEUTHER_METRICS,
    process_results,
    agg_mean,
    agg_rate,
)

__version__ = "0.4.1"
__all__ = [
    "AEEAuditor",
    "METRTaskScorer",
    "S_SET",
    "D_SET",
    "ELEUTHER_METRICS",
    "process_results",
    "agg_mean",
    "agg_rate",
]
