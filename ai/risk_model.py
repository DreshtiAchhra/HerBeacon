"""HerBeacon - transparent behavioural risk scoring.

LoveFraud02-compatible rule-based risk engine.  No synthetic training data or
supervised ML is used: the score is an explainable decision-support indicator,
not a probability that a person is fraudulent.
"""

from typing import Any, Dict, List


class RiskScoringModel:
    """Deterministic 0-100 behavioural risk scorer."""

    THRESHOLDS = {
        "LOW": (0, 24),
        "MODERATE": (25, 49),
        "HIGH": (50, 74),
        "CRITICAL": (75, 100),
    }

    def __init__(self, ml_model_path=None):
        # Kept as an optional compatibility argument for existing pipeline code.
        # It is intentionally ignored: HerBeacon uses only the transparent
        # rule-based engine for LoveFraud02.
        self.analysis_mode = "RULE_BASED"

    def calculate_risk(
        self,
        features: Dict[str, Any],
        escalation_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        total_triggers = int(features.get("total_pattern_triggers", 0) or 0)
        if total_triggers == 0:
            return self._format_risk_output(
                10,
                features,
                escalation_result,
                {"baseline_prior": 10.0},
            )

        max_stage = int(escalation_result.get("max_stage", 0) or 0)
        breakdown: Dict[str, float] = {}

        # Keep all scoring contributions explicit and bounded.
        breakdown["escalation_stage"] = round((max_stage / 5.0) * 35.0, 1)

        fin_count = int(features.get("count_financial_pressure", 0) or 0)
        urg_count = int(features.get("count_urgency", 0) or 0)
        secrecy_count = int(features.get("count_secrecy", 0) or 0)
        isolation_count = int(features.get("count_isolation", 0) or 0)
        sensitive_count = int(features.get("count_sensitive_info_request", 0) or 0)
        coercion_count = int(features.get("count_coercion_threat", 0) or 0)

        breakdown["financial_solicitations"] = round(min(25.0, fin_count * 6.0), 1)
        breakdown["artificial_urgency"] = round(min(15.0, urg_count * 4.0), 1)
        boundary_count = secrecy_count + isolation_count + sensitive_count
        breakdown["secrecy_and_isolation"] = round(min(15.0, boundary_count * 5.0), 1)

        if coercion_count > 0:
            breakdown["coercion_and_threats"] = 40.0

        funnel_pts = 0.0
        if escalation_result.get("is_funnel_escalation", False):
            funnel_pts += 6.0
        if features.get("early_platform_switch_flag", 0.0) == 1.0:
            funnel_pts += 4.0
        breakdown["funnel_dynamics"] = funnel_pts

        raw_score = 10.0 + sum(breakdown.values())

        # Explicit high-risk conditions prevent a severe signal from being
        # diluted by unrelated low-risk conversation.
        if coercion_count > 0:
            raw_score = max(raw_score, 90.0)
        elif fin_count > 0 and urg_count > 0 and max_stage >= 4:
            raw_score = max(raw_score, 75.0)
        elif fin_count > 0 and max_stage >= 4:
            raw_score = max(raw_score, 50.0)

        score = max(0, min(100, int(round(raw_score))))
        return self._format_risk_output(score, features, escalation_result, breakdown)

    def _risk_level(self, score: int) -> str:
        for level, (lower, upper) in self.THRESHOLDS.items():
            if lower <= score <= upper:
                return level
        return "CRITICAL" if score >= 75 else "LOW"

    def _format_risk_output(
        self,
        score: int,
        features: Dict[str, Any],
        escalation_result: Dict[str, Any],
        factor_breakdown: Dict[str, float],
    ) -> Dict[str, Any]:
        level = self._risk_level(score)
        max_stage = int(escalation_result.get("max_stage", 0) or 0)
        max_stage_name = escalation_result.get("max_stage_name", "Baseline / Normal Interaction")
        factors = self._identify_primary_factors(features, escalation_result)

        return {
            "analysis_mode": "RULE_BASED",
            "risk_score": score,
            "risk_level": level,
            "max_stage": max_stage,
            "max_stage_name": max_stage_name,
            "primary_risk_factors": factors,
            "factor_breakdown": factor_breakdown,
            "decision_support_summary": self._generate_summary(score, level, max_stage, factors),
            "safety_disclaimer": (
                "Detected behavioural patterns indicate conversational risk signals. "
                "This score is an automated decision-support indicator and is not a "
                "conclusive determination of identity or intent."
            ),
        }

    def _identify_primary_factors(
        self,
        features: Dict[str, Any],
        escalation_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []

        fin = int(features.get("count_financial_pressure", 0) or 0)
        urg = int(features.get("count_urgency", 0) or 0)
        coercion = int(features.get("count_coercion_threat", 0) or 0)
        secrecy = int(features.get("count_secrecy", 0) or 0)
        isolation = int(features.get("count_isolation", 0) or 0)
        sensitive = int(features.get("count_sensitive_info_request", 0) or 0)

        if fin:
            candidates.append({
                "factor": "Financial Pressure & Solicitations",
                "impact": "HIGH",
                "detail": f"{fin} financial solicitation cues detected.",
            })
        if urg:
            candidates.append({
                "factor": "Artificial Urgency & Time Pressure",
                "impact": "HIGH",
                "detail": f"{urg} urgency cues detected.",
            })
        if coercion:
            candidates.append({
                "factor": "Coercion or Intimidation Cues",
                "impact": "CRITICAL",
                "detail": f"{coercion} coercion/threat cues detected.",
            })
        if secrecy or isolation or sensitive:
            candidates.append({
                "factor": "Boundary, Secrecy & Isolation Signals",
                "impact": "HIGH",
                "detail": (
                    f"Secrecy={secrecy}, isolation={isolation}, "
                    f"sensitive-information requests={sensitive}."
                ),
            })
        if escalation_result.get("is_funnel_escalation", False):
            candidates.append({
                "factor": "Multi-Phase Behavioural Progression",
                "impact": "HIGH",
                "detail": "Earlier rapport/affection signals chronologically preceded later financial or crisis-stage signals.",
            })

        candidates.sort(
            key=lambda item: {"CRITICAL": 3, "HIGH": 2, "MEDIUM": 1, "LOW": 0}.get(item["impact"], 0),
            reverse=True,
        )
        return candidates

    def _generate_summary(
        self,
        score: int,
        level: str,
        max_stage: int,
        factors: List[Dict[str, Any]],
    ) -> str:
        names = ", ".join(f["factor"] for f in factors[:3]) or "baseline conversational indicators"
        return (
            f"Overall conversational risk is {level} ({score}/100), reaching Stage {max_stage}. "
            f"Primary behavioural contributors: {names}."
        )

    def train_from_annotations(self, *args, **kwargs) -> Dict[str, Any]:
        """Retained only for API compatibility; ML training is intentionally disabled."""
        return {
            "status": "DISABLED",
            "message": "Supervised ML training is not used. HerBeacon uses the transparent rule-based engine with LoveFraud02.",
        }
