"""HerBeacon rule-based explainability.

Explainability mirrors the deterministic risk model and never presents a
model probability or SHAP attribution as evidence.
"""

from typing import List, Dict, Any, Optional
from ai.risk_model import RiskScoringModel


class ShapExplainer:
    """
    Explainability Engine for HerBeacon.
    
    Provides transparent factor contributions for the deterministic risk score.
    """

    FEATURE_HUMAN_NAMES = {
        "weighted_severity_score": "Cumulative Severity Score",
        "escalation_score": "Escalation Progression Score",
        "density_financial_pressure": "Financial Solicitation Density",
        "density_urgency": "Artificial Urgency & Time Pressure",
        "density_emotional_dependency": "Emotional Dependency / Love Bombing",
        "density_secrecy": "Secrecy & Concealment Cues",
        "density_isolation": "Isolation Tactics",
        "density_move_communication": "Platform Migration Pressure",
        "density_sensitive_info_request": "Sensitive Information Requests",
        "density_emotional_manipulation": "Emotional Manipulation & Guilt",
        "density_coercion_threat": "Coercion & Blackmail Signals",
        "love_before_money_flag": "Funnel Sequence (Love Before Money)",
        "early_platform_switch_flag": "Early Platform Switching",
        "high_critical_ratio": "Proportion of High/Critical Cues",
        "risk_signal_density": "Overall Risk Signal Density",
        "escalation_gradient": "Escalation Acceleration Gradient"
    }

    def __init__(self, risk_model: Optional[RiskScoringModel] = None):
        self.risk_model = risk_model if risk_model is not None else RiskScoringModel()
        self.base_value = 10.0

    def explain_prediction(
        self,
        features: Dict[str, Any],
        escalation_result: Dict[str, Any],
        risk_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates explainability attribution report.
        
        Args:
            features: Dictionary from FeatureExtractor.
            escalation_result: Dictionary from EscalationEngine.
            risk_output: Optional dictionary from RiskScoringModel.
            
        Returns:
            Dict containing:
            - method (str): "RULE_BASED"
            - baseline_prior (float)
            - feature_contributions (List[Dict])
            - top_risk_drivers (List[Dict])
            - top_mitigating_factors (List[Dict])
            - narrative_explanation (str)
        """
        return self._explain_with_rule_contributions(features, escalation_result, risk_output)

    def _explain_with_rule_contributions(
        self,
        features: Dict[str, Any],
        escalation_result: Dict[str, Any],
        risk_output: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Transparent rule-based factor attribution explaining the composite score."""
        drivers = []
        mitigating = []

        breakdown = (risk_output or {}).get("factor_breakdown", {})

        # Use the exact contribution values returned by RiskScoringModel so
        # explainability cannot drift from the score calculation.
        labels = {
            "escalation_stage": ("Escalation Stage Progression", "Escalation stage contribution"),
            "financial_solicitations": ("Financial & Resource Solicitations", "Financial solicitation contribution"),
            "artificial_urgency": ("Artificial Urgency & Time Pressure", "Urgency contribution"),
            "secrecy_and_isolation": ("Secrecy, Isolation & Sensitive Information", "Boundary-signal contribution"),
            "coercion_and_threats": ("Coercion & Threats", "Critical coercion/threat contribution"),
            "funnel_dynamics": ("Funnel Dynamics", "Chronological behavioural progression contribution"),
        }

        for key, (name, detail) in labels.items():
            points = float(breakdown.get(key, 0.0) or 0.0)
            if points > 0:
                drivers.append({
                    "feature_key": key,
                    "feature_name": name,
                    "contribution_points": round(points, 1),
                    "detail": detail,
                })

        if not drivers:
            mitigating.append({
                "feature_key": "baseline",
                "feature_name": "Baseline Interaction",
                "contribution_points": 0.0,
                "detail": "No elevated behavioural risk contribution was detected.",
            })

        drivers.sort(key=lambda x: x["contribution_points"], reverse=True)

        # Build narrative
        if drivers:
            driver_texts = [f"{d['feature_name']} (+{d['contribution_points']} pts)" for d in drivers[:3]]
            narrative = f"Rule-based risk score is primarily driven by: {', '.join(driver_texts)}."
        else:
            narrative = "No elevated risk drivers detected; interaction remains at baseline parameters."

        return {
            "explainability_method": "RULE_BASED",
            "baseline_prior": 10.0,
            "feature_contributions": drivers + mitigating,
            "top_risk_drivers": drivers[:5],
            "top_mitigating_factors": mitigating[:3],
            "narrative_explanation": narrative
        }
