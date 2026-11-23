"""Deterministic behavior checks; synthetic inputs are not reference evidence."""
import math
from aee_benchmark.plugin import AEEAuditor, METRTaskScorer, process_results

def test_empty():
    r = AEEAuditor().audit("")
    assert (r["S"], r["D"], r["VERDICT"]) == (0, 0, "UNMEASURABLE")

def test_pic():
    assert AEEAuditor().calculate_pic("sA") == (2.32, 1, 2)

def test_td_guard():
    a = AEEAuditor()
    assert a.calculate_td(9,0) == round(math.log(9,7),4)
    assert a.calculate_td(9,1) == round(math.log(9,7),4)

def test_phrase_count():
    r = AEEAuditor().audit("It is important to note that results may vary.")
    assert r["D_TERMS"].count("it is important to note") == 1

def test_adapter_float_fields():
    result = process_results({}, ["The result is verified, perhaps."])
    assert len(result) == 9 and all(isinstance(x,float) for x in result.values())
    assert result["aee_hedge_count"] == 1.0

def test_batch():
    r = METRTaskScorer().evaluate_batch([{"completion":"The result is verified."},{"completion":"Perhaps."}])
    assert r["total_records"] == 2
    assert sum(r["verdict_distribution"].values()) == 2
