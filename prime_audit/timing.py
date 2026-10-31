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


# Live, best-effort local detection. The scheduler controls wake-up time; no real-time guarantee.
import functools
import json
import sys
import threading


def monitored(stage, target_ns=TARGET_NS):
    """Signal overdue work while still running, and record elapsed completion.

    Events contain only a fixed stage name and timing. They never cancel or authorize
    an operation. stderr avoids corrupting protocol stdout; delivery is best effort.
    """
    if not isinstance(stage, str) or not stage or not stage.replace('_', '').isalnum():
        raise ValueError('fixed stage name required')
    if type(target_ns) is not int or target_ns <= 0:
        raise ValueError('positive integer target required')
    def decorate(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            started = perf_counter_ns()
            lock = threading.Lock()
            state = {'finished': False, 'alerted': False}
            def emit(event, elapsed):
                try:
                    print(json.dumps({'schema':'prime.temporal-event.v1', 'stage':stage,
                        'event':event, 'target_ns':target_ns, 'elapsed_ns':elapsed,
                        'scope':'local wrapper elapsed; external response not controlled'}),
                        file=sys.stderr, flush=True)
                except (OSError, ValueError):
                    pass
            def alert():
                with lock:
                    if not state['finished']:
                        state['alerted'] = True
                        emit('deadline_exceeded', max(0, perf_counter_ns()-started))
            timer = threading.Timer(target_ns/1_000_000_000, alert)
            timer.daemon = True
            timer.start()
            try:
                return fn(*args, **kwargs)
            finally:
                with lock:
                    state['finished'] = True
                    elapsed = max(0, perf_counter_ns()-started)
                    timer.cancel()
                    # If the scheduler delayed the timer, still report a missed target.
                    if elapsed > target_ns and not state['alerted']:
                        emit('deadline_exceeded', elapsed)
                    emit('completed', elapsed)
        return wrapped
    return decorate
