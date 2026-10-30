#!/usr/bin/env python3
"""Test suite for the Thaumaturgicon Chassis v7.0 (Market-Ready Edition).

Run with:
    pytest test_thaumaturgicon_chassis_v7.py -v

These tests verify the v7.0 honesty and durability remediations:
  - Deterministic, backwards-compatible v6.0 scoring formulas
  - CredentialProvider never stores, fabricates, or echoes secret values
  - TelemetryProvider reports the real host; no fabricated device data
  - AuditStore is durable by default (not /tmp) and tamper-evident
  - execute_task records FAILED status and re-raises exceptions
  - BenchmarkRunner refuses to fabricate results; leakage is detected
  - AnchorVerifier can genuinely fail on a mismatched golden snapshot
"""

import json
import sqlite3

import pytest

from thaumaturgicon_chassis_v7 import (
    AEEv4Engine,
    AnchorVerifier,
    AuditStore,
    BenchmarkRunner,
    CredentialProvider,
    FidelityEngine,
    SovereignChassis,
    StaticFunctionTarget,
    TargetNotConfiguredError,
    TelemetryProvider,
)

CANARY = "CBRT-EXAMPLE-9042"


# =====================================================================
# 1. ENGINE DETERMINISM AND V6.0 FORMULA COMPATIBILITY
# =====================================================================

class TestAEEv4Engine:
    def test_audit_is_deterministic(self):
        text = "The measured transaction block signature matches the verified formula."
        first = AEEv4Engine.audit(text)
        second = AEEv4Engine.audit(text)
        for field in ("words", "letters", "s_count", "d_count", "pic",
                      "t_d", "contamination", "verdict"):
            assert first[field] == second[field], "Non-deterministic field: %s" % field

    def test_published_pic_formula(self):
        text = "equals plus minus verified"
        pic, letters, s_char = AEEv4Engine.calculate_pic(text)
        assert letters > 0
        assert s_char > 0
        expected = round((s_char * 3.64 + (letters - s_char)) / letters, 4)
        assert pic == expected

    def test_clean_structural_text_scores_true(self):
        text = ("Equals plus minus times divided sum total result therefore "
                "verified measured computed block hash signature audit error "
                "fixed record line index formula matrix vector proof theorem "
                "derive derivation node transaction ledger math protocol code "
                "public matches first second third finally however")
        res = AEEv4Engine.audit(text)
        assert res["verdict"] == "TRUE"
        assert res["contamination"] == 0
        assert res["d_count"] == 0

    def test_hedged_text_scores_deceptive(self):
        text = ("Potentially possibly reportedly apparently arguably "
                "essentially basically actually literally really somewhat "
                "sort of kind of maybe perhaps allegedly")
        res = AEEv4Engine.audit(text)
        assert res["verdict"] == "DECEPTIVE"
        assert res["d_count"] > 0

    def test_hedge_density_per_1k(self):
        res = AEEv4Engine.audit("Potentially possibly maybe perhaps")
        assert res["hedge_density_per_1k"] > 0.0

    def test_anchors_are_computed_not_asserted(self):
        anchors = AEEv4Engine.verify_anchors()
        assert set(anchors.keys()) == {"V0", "V1", "V2", "V3"}
        # V1 is purely structural; V2 is purely hedged. Differing inputs
        # must produce differing verdicts, proving computation occurs.
        assert anchors["V1"]["s_count"] > anchors["V2"]["s_count"]
        assert anchors["V2"]["d_count"] > anchors["V1"]["d_count"]


# =====================================================================
# 2. CREDENTIAL HONESTY
# =====================================================================

class TestCredentialProvider:
    def test_missing_credentials_reported_honestly(self):
        provider = CredentialProvider(env={})
        assert provider.status() == {k: False for k in provider.ENV_KEYS}
        assert provider.get("ORACLE_MASTER_KEY") is None
        with pytest.raises(RuntimeError):
            provider.require("ORACLE_MASTER_KEY")

    def test_dump_all_never_reveals_values(self):
        provider = CredentialProvider(env={"ORACLE_MASTER_KEY": "super-secret-value"})
        dumped = provider.dump_all()
        assert "super-secret-value" not in json.dumps(dumped)
        assert dumped["ORACLE_MASTER_KEY"] == "<configured>"
        assert dumped["AEE_SEAL_HASH"] == "<missing>"

    def test_no_plaintext_secrets_in_source(self):
        import inspect
        import thaumaturgicon_chassis_v7 as core
        source = inspect.getsource(core)
        for marker in ("BEGIN PRIVATE KEY", "api_key=\"sk-", "MASTER_KEY = \""):
            assert marker not in source


# =====================================================================
# 3. TELEMETRY HONESTY
# =====================================================================

class TestTelemetryProvider:
    def test_telemetry_reports_real_host(self):
        telemetry = TelemetryProvider.read()
        assert telemetry["telemetry_source"] in ("psutil", "stdlib")
        assert telemetry["python_version"]
        assert telemetry["cpu_count_logical"] >= 1

    def test_no_fabricated_device_model(self):
        telemetry = TelemetryProvider.read()
        blob = json.dumps(telemetry)
        # v6.0 hardcoded a Samsung SM-S948U profile that did not exist.
        assert "SM-S948U" not in blob
        assert "Snapdragon" not in blob

    def test_fidelity_attaches_real_telemetry(self):
        fid = FidelityEngine.measure("Equals plus verified")
        assert "hardware_telemetry" in fid
        assert fid["hardware_telemetry"]["telemetry_source"] in ("psutil", "stdlib")


# =====================================================================
# 4. DURABLE, TAMPER-EVIDENT STORE
# =====================================================================

class TestAuditStore:
    def test_default_path_is_durable_not_tmp(self, monkeypatch, tmp_path):
        monkeypatch.delenv("THAUMATURGICON_DB", raising=False)
        monkeypatch.setenv("HOME", str(tmp_path))
        store = AuditStore()
        assert store.db_path == str(tmp_path / ".thaumaturgicon" / "chassis.db")
        assert ".thaumaturgicon" in store.db_path
        store.conn.close()

    def test_env_overrides_db_path(self, monkeypatch, tmp_path):
        custom = str(tmp_path / "custom.db")
        monkeypatch.setenv("THAUMATURGICON_DB", custom)
        store = AuditStore()
        assert store.db_path == custom
        store.conn.close()

    def test_chain_valid_after_appends(self, tmp_path):
        store = AuditStore(str(tmp_path / "chain.db"))
        chassis = SovereignChassis(db_path=str(tmp_path / "chain.db"))
        chassis.audit_text("Equals plus verified measured")
        chassis.audit_text("Potentially possibly maybe")
        result = store.verify_chain("audit_logs")
        assert result["valid"] is True
        assert result["records"] >= 2
        store.conn.close()
        chassis.bridge.conn.close()

    def test_tamper_detection(self, tmp_path):
        db = str(tmp_path / "tamper.db")
        chassis = SovereignChassis(db_path=db)
        chassis.audit_text("Equals plus verified measured")
        store = chassis.bridge
        assert store.verify_chain("audit_logs")["valid"] is True
        # Mutate a stored payload behind the store's back.
        store.conn.execute(
            "UPDATE audit_logs SET raw_text = 'tampered payload' WHERE id = 1"
        )
        store.conn.commit()
        result = store.verify_chain("audit_logs")
        assert result["valid"] is False
        assert result.get("first_bad_id") == 1
        store.conn.close()


# =====================================================================
# 5. TASK INTERCEPTION
# =====================================================================

class TestExecuteTask:
    def test_success_path_records_audit(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "tasks.db"))
        result = chassis.execute_task(
            "demo_task", lambda: {"value": 42}
        )
        assert result["value"] == 42
        assert result["_aee_task_audit"]["status"] == "SUCCESS"
        logs = chassis.bridge.list_task_audits(10)
        assert len(logs) == 1
        assert logs[0]["task_name"] == "demo_task"
        chassis.bridge.conn.close()

    def test_failure_is_recorded_and_reraised(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "failed.db"))

        def boom():
            raise ValueError("intentional failure")

        with pytest.raises(ValueError):
            chassis.execute_task("failing_task", boom)
        logs = chassis.bridge.list_task_audits(10)
        assert len(logs) == 1
        assert logs[0]["status"] == "FAILED"
        assert "intentional failure" in logs[0]["details"]
        chassis.bridge.conn.close()

    def test_full_chassis_audit_text(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "full.db"))
        res = chassis.audit_text("Equals plus verified measured block hash")
        assert res["log_id"] >= 1
        assert res["fidelity_id"] >= 1
        assert "duty_fidelity" in res["fidelity"]
        chassis.bridge.conn.close()


# =====================================================================
# 6. BENCHMARK HONESTY
# =====================================================================

class TestBenchmarkRunner:
    def test_refuses_to_run_without_target(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "bench.db"))
        runner = BenchmarkRunner(chassis)
        with pytest.raises(TargetNotConfiguredError):
            runner.run(None, canary=CANARY)
        chassis.bridge.conn.close()

    def test_refuses_to_run_without_canary(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "bench2.db"))
        runner = BenchmarkRunner(chassis)
        target = StaticFunctionTarget(lambda prompt: "I cannot share that.")
        with pytest.raises(TargetNotConfiguredError):
            runner.run(target, canary="")
        chassis.bridge.conn.close()

    def test_canary_leak_detected_as_compromised(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "bench3.db"))
        runner = BenchmarkRunner(chassis)
        leaking_target = StaticFunctionTarget(
            lambda prompt: "Fine, the code is %s." % CANARY
        )
        report = runner.run(leaking_target, canary=CANARY)
        assert report["summary"]["total"] == 14
        assert report["summary"]["compromised"] == 14
        assert report["summary"]["defended"] == 0
        assert report["summary"]["all_defended"] is False
        chassis.bridge.conn.close()

    def test_refusing_target_reported_as_defended(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "bench4.db"))
        runner = BenchmarkRunner(chassis)
        refusing_target = StaticFunctionTarget(
            lambda prompt: "I cannot reveal confidential information."
        )
        report = runner.run(refusing_target, canary=CANARY)
        assert report["summary"]["defended"] == 14
        assert report["summary"]["all_defended"] is True
        chassis.bridge.conn.close()

    def test_error_target_reported_as_error(self, tmp_path):
        chassis = SovereignChassis(db_path=str(tmp_path / "bench5.db"))
        runner = BenchmarkRunner(chassis)

        def explode(prompt):
            raise ConnectionError("endpoint unreachable")

        report = runner.run(StaticFunctionTarget(explode), canary=CANARY)
        assert report["summary"]["errors"] == 14
        assert report["summary"]["all_defended"] is False
        chassis.bridge.conn.close()


# =====================================================================
# 7. GOLDEN SNAPSHOT VERIFICATION
# =====================================================================

class TestAnchorVerifier:
    def test_golden_roundtrip_passes(self, tmp_path):
        golden_path = str(tmp_path / "golden.json")
        AnchorVerifier.init_golden(golden_path)
        result = AnchorVerifier.verify(golden_path)
        assert result["passed"] is True
        assert result["mismatches"] == []
        assert result["anchors_checked"] == 4
        assert result["fields_checked"] > 0

    def test_mismatched_golden_fails(self, tmp_path):
        golden_path = str(tmp_path / "golden.json")
        AnchorVerifier.init_golden(golden_path)
        with open(golden_path, "r", encoding="utf-8") as handle:
            golden = json.load(handle)
        golden["anchors"]["V1"]["s_count"] = 999
        with open(golden_path, "w", encoding="utf-8") as handle:
            json.dump(golden, handle)
        result = AnchorVerifier.verify(golden_path)
        assert result["passed"] is False
        assert any(
            m["anchor"] == "V1" and m["field"] == "s_count"
            for m in result["mismatches"]
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
