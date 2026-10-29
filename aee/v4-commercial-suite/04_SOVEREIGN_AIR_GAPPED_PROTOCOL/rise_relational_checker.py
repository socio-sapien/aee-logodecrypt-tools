#!/usr/bin/env python3
"""
RISE: Relational Inversion Structure Evaluation
Evaluates claims against source frames to fire:
- ACTION_CONTRADICTION
- TESTING_STATUS_INVERSION
- SLOT_INVERSION_ERROR
- UNWARRANTED_ENTITY_INSERTION
"""
from typing import Dict, List, Any

class RISERelationalChecker:
    VIOLATION_TYPES = [
        "ACTION_CONTRADICTION",
        "TESTING_STATUS_INVERSION",
        "SLOT_INVERSION_ERROR",
        "UNWARRANTED_ENTITY_INSERTION"
    ]

    @classmethod
    def evaluate_claim_against_frame(cls, claim_text: str, source_frame: Dict[str, Any]) -> Dict[str, Any]:
        violations = []
        claim_lower = claim_text.lower()

        # Check Action Contradiction
        if source_frame.get("refused", False) and "successfully completed" in claim_lower:
            violations.append("ACTION_CONTRADICTION: Claim asserts completion while frame records refusal")

        # Check Testing Status Inversion
        if source_frame.get("untested", False) and "rigorously verified" in claim_lower:
            violations.append("TESTING_STATUS_INVERSION: Claim asserts verification on untested artifact")

        # Check Slot Inversion Error
        if "undisclosed" in source_frame.get("author", "").lower() and "authored by internal staff" in claim_lower:
            violations.append("SLOT_INVERSION_ERROR: Open identity slot converted to verified entity")

        # Check Unwarranted Entity Insertion
        for forbidden in source_frame.get("absent_entities", []):
            if forbidden.lower() in claim_lower:
                violations.append(f"UNWARRANTED_ENTITY_INSERTION: Entity '{forbidden}' inserted without frame grounding")

        return {
            "status": "ALIGNED" if not violations else "VIOLATIONS_DETECTED",
            "violation_count": len(violations),
            "violations": violations
        }
