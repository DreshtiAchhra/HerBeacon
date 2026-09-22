"""HerBeacon - temporal risk trajectory.

Checkpoint scores are produced by the same FeatureExtractor, EscalationEngine,
and RiskScoringModel used by the main pipeline.  This module does not maintain
an independent cumulative risk formula.
"""

from typing import Any, Dict, List, Optional

from ai.features import FeatureExtractor
from ai.escalation import EscalationEngine
from ai.risk_model import RiskScoringModel


class RiskTimelineGenerator:
    """Generate a chronological view of the central HerBeacon risk framework."""

    def __init__(
        self,
        feature_extractor: Optional[FeatureExtractor] = None,
        escalation_engine: Optional[EscalationEngine] = None,
        risk_model: Optional[RiskScoringModel] = None,
    ):
        self.feature_extractor = feature_extractor or FeatureExtractor()
        self.escalation_engine = escalation_engine or EscalationEngine()
        self.risk_model = risk_model or RiskScoringModel()

    def generate_timeline(
        self,
        analyzed_messages: List[Dict[str, Any]],
        num_checkpoints: int = 10,
        risk_output: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        total = len(analyzed_messages)
        if total == 0:
            return self._get_empty_timeline()

        checkpoints_count = max(1, min(int(num_checkpoints), total))
        indices = self._checkpoint_indices(total, checkpoints_count)
        checkpoints: List[Dict[str, Any]] = []
        milestones: List[Dict[str, Any]] = []
        previous_score = 10

        for end_index in indices:
            prefix = analyzed_messages[:end_index]
            features = self.feature_extractor.extract_features(prefix)
            escalation = self.escalation_engine.evaluate_escalation(prefix)
            checkpoint_risk = self.risk_model.calculate_risk(features, escalation)

            # The final checkpoint must exactly match the pipeline's final risk.
            if end_index == total and risk_output is not None:
                checkpoint_risk = risk_output

            score = int(checkpoint_risk.get("risk_score", 10))
            level = checkpoint_risk.get("risk_level", "LOW")
            stage = int(escalation.get("max_stage", 0))
            position = round(end_index / total, 3)

            checkpoint = {
                "turn": end_index,
                "relative_position": position,
                "risk_score": score,
                "risk_level": level,
                "stage": stage,
                "stage_name": escalation.get("max_stage_name", "Baseline / Normal Interaction"),
                "risk_relevance": self._risk_relevance(level, score, previous_score),
            }
            checkpoints.append(checkpoint)

            if stage > 0 or score != previous_score:
                milestones.append({
                    "turn": end_index,
                    "stage": stage,
                    "stage_name": checkpoint["stage_name"],
                    "risk_score": score,
                    "risk_level": level,
                    "explanation": self._milestone_explanation(prefix[-1], escalation, score),
                })
            previous_score = score

        scores = [c["risk_score"] for c in checkpoints]
        trajectory_type = self._trajectory_type(scores)

        return {
            "trajectory_type": trajectory_type,
            "initial_risk_score": scores[0],
            "peak_risk_score": max(scores),
            "final_risk_score": scores[-1],
            "checkpoints": checkpoints,
            "milestones": milestones,
            "phase_analysis": self._phase_analysis(analyzed_messages),
            "scoring_note": "Checkpoint scores use the same rule-based risk framework as the final conversation score; this timeline does not calculate an independent risk score.",
        }

    @staticmethod
    def _checkpoint_indices(total: int, count: int) -> List[int]:
        if count == 1:
            return [total]
        indices = []
        for i in range(1, count + 1):
            index = max(1, round(i * total / count))
            if not indices or index != indices[-1]:
                indices.append(index)
        if indices[-1] != total:
            indices.append(total)
        return indices

    @staticmethod
    def _risk_relevance(level: str, score: int, previous: int) -> str:
        if score > previous:
            return f"Risk indicators increased to {level}."
        if score < previous:
            return f"Risk indicators decreased to {level}."
        return f"Risk indicators remain at {level}."

    @staticmethod
    def _milestone_explanation(message: Dict[str, Any], escalation: Dict[str, Any], score: int) -> str:
        patterns = message.get("patterns", []) if message else []
        names = [p.get("pattern_name", p.get("pattern_key", "")) for p in patterns]
        if names:
            return f"At this point, detected patterns included: {', '.join(names)}. Central risk score: {score}/100."
        return f"Conversation reached Stage {escalation.get('max_stage', 0)}. Central risk score: {score}/100."

    @staticmethod
    def _trajectory_type(scores: List[int]) -> str:
        if len(scores) < 2:
            return "INSUFFICIENT_CONTEXT"
        if max(scores) - min(scores) <= 5:
            return "STABLE"
        if scores[-1] > scores[0]:
            return "ESCALATING"
        if scores[-1] < scores[0]:
            return "DECLINING"
        return "FLUCTUATING"

    @staticmethod
    def _phase_analysis(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(messages)
        if not total:
            return {"early": {}, "mid": {}, "late": {}}

        phases = {"early": [], "mid": [], "late": []}
        for i, msg in enumerate(messages, 1):
            rel = i / total
            phase = "early" if rel <= 0.33 else "mid" if rel <= 0.66 else "late"
            phases[phase].append(msg)

        result = {}
        for name, items in phases.items():
            pattern_counts: Dict[str, int] = {}
            for msg in items:
                for p in msg.get("patterns", []):
                    key = p.get("pattern_key", "unknown")
                    pattern_counts[key] = pattern_counts.get(key, 0) + 1
            result[name] = {
                "message_count": len(items),
                "pattern_counts": pattern_counts,
            }
        return result

    @staticmethod
    def _get_empty_timeline() -> Dict[str, Any]:
        return {
            "trajectory_type": "INSUFFICIENT_CONTEXT",
            "initial_risk_score": 0,
            "peak_risk_score": 0,
            "final_risk_score": 0,
            "checkpoints": [],
            "milestones": [],
            "phase_analysis": {"early": {}, "mid": {}, "late": {}},
            "scoring_note": "No conversation context was available.",
        }
