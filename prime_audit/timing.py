"""Monotonic, local timing observations; targets do not authorize or cancel operations."""
from time import perf_counter_ns

TARGET_NS = 7_000_000

class Timing:
    def __init__(self, target_ns=TARGET_NS, clock=perf_counter_ns):
        if type(target_ns) is not int or target_ns <= 0:
            raise ValueError("positive integer target required")
        self.target_ns, self.clock, self.stages = target_ns, clock, []
        self.started = clock()

    def mark(self, stage, started):
        elapsed = max(0, self.clock() - started)
        self.stages.append({"stage": stage, "elapsed_ns": elapsed,
            "target_ns": self.target_ns, "within_target": elapsed <= self.target_ns})

    def record(self):
        total = max(0, self.clock() - self.started)
        return {"schema": "prime.timing.v1", "clock": "monotonic",
            "target_ns": self.target_ns, "target_kind": "advisory",
            "elapsed_ns": total, "within_target": total <= self.target_ns,
            "stages": self.stages,
            "scope": "measured local process only; excludes GitHub queues and providers"}
