"""
HerBeacon - AI Analysis Engine
Module: ai.pipeline

End-to-End AI Analysis Pipeline component.
Orchestrates parsing, behavioral pattern detection, feature engineering,
escalation detection, risk scoring, explainability, safety recommendations,
and risk timeline generation into a unified, production-ready analysis engine.
"""

from pathlib import Path
from typing import List, Dict, Any, Union, Optional

from ai.parser import ConversationParser
from ai.patterns import BehaviouralPatternDetector
from ai.features import FeatureExtractor
from ai.escalation import EscalationEngine
from ai.risk_model import RiskScoringModel
from ai.explainability import ShapExplainer
from ai.safety_recommender import SafetyRecommendationEngine
from ai.timeline import RiskTimelineGenerator


class HerBeaconAnalysisEngine:
    """
    HerBeacon End-to-End AI Analysis Engine.
    
    USP: "We don't detect suspicious people; we detect suspicious behavioural patterns."
    """

    def __init__(self, ml_model_path: Optional[Union[str, Path]] = None, custom_resources: Optional[Dict[str, Any]] = None):
        self.parser = ConversationParser()
        self.pattern_detector = BehaviouralPatternDetector()
        self.feature_extractor = FeatureExtractor()
        self.escalation_engine = EscalationEngine()
        self.risk_model = RiskScoringModel(ml_model_path=ml_model_path)
        self.shap_explainer = ShapExplainer(self.risk_model)
        self.safety_recommender = SafetyRecommendationEngine(custom_resources=custom_resources)
        self.timeline_generator = RiskTimelineGenerator()

    def analyze_messages(
        self,
        messages: List[Dict[str, Any]],
        conversation_id: str = "custom_conversation"
    ) -> Dict[str, Any]:
        """
        Executes the full AI analysis pipeline on structured conversation messages.
        
        Args:
            messages: List of message dictionaries with 'message_index', 'speaker', 'message'.
            conversation_id: Identifier name for the conversation.
            
        Returns:
            Dict[str, Any]: Comprehensive unified AI analysis report.
        """
        # Step 1: Behavioural Pattern Detection
        analyzed_messages = self.pattern_detector.analyze_conversation(messages)
        pattern_summary = self.pattern_detector.get_pattern_summary(analyzed_messages)

        # Step 2: Feature Engineering
        features = self.feature_extractor.extract_features(analyzed_messages)

        # Step 3: Escalation Engine
        escalation_result = self.escalation_engine.evaluate_escalation(analyzed_messages)

        # Step 4: Risk Scoring
        risk_output = self.risk_model.calculate_risk(features, escalation_result)

        # Step 5: Explainability (SHAP if ML, Rule-based if fallback)
        explainability_output = self.shap_explainer.explain_prediction(features, escalation_result, risk_output)

        # Step 6: Safety Recommendations
        safety_output = self.safety_recommender.generate_recommendations(features, escalation_result, risk_output)

        # Step 7: Risk Timeline
        timeline_output = self.timeline_generator.generate_timeline(
            analyzed_messages,
            risk_output=risk_output,
        )

        # Metadata assembly
        speakers = sorted(list(set(m.get("speaker", "Unknown") for m in messages)))
        flagged_count = sum(1 for m in analyzed_messages if m.get("patterns"))

        # Flatten detected pattern evidence
        unique_patterns = list(pattern_summary["pattern_counts"].keys())
        all_evidence = []
        for m in analyzed_messages:
            for p in m.get("patterns", []):
                for e in p.get("evidence", []):
                    if e not in all_evidence:
                        all_evidence.append(e)

        # Final Unified Result
        return {
            "conversation_id": conversation_id,
            "analysis_mode": risk_output["analysis_mode"],
            "metadata": {
                "total_messages": len(messages),
                "unique_speakers_count": len(speakers),
                "speakers": speakers,
                "avg_words_per_message": features.get("avg_msg_words", 0.0),
                "avg_chars_per_message": features.get("avg_msg_chars", 0.0)
            },
            "risk_assessment": {
                "risk_score": risk_output["risk_score"],
                "risk_level": risk_output["risk_level"],
                "max_stage": risk_output["max_stage"],
                "max_stage_name": risk_output["max_stage_name"],
                "primary_risk_factors": risk_output["primary_risk_factors"],
                "summary": risk_output["decision_support_summary"],
                "safety_disclaimer": risk_output["safety_disclaimer"]
            },
            "behavioral_patterns": {
                "total_cues_detected": pattern_summary["total_pattern_occurrences"],
                "flagged_message_count": flagged_count,
                "patterns_detected": unique_patterns,
                "pattern_counts": pattern_summary["pattern_counts"],
                "evidence": all_evidence[:15],
                "speaker_breakdown": pattern_summary["speaker_breakdown"]
            },
            "escalation_analysis": {
                "max_stage": escalation_result["max_stage"],
                "max_stage_name": escalation_result["max_stage_name"],
                "escalation_score": escalation_result["escalation_score"],
                "velocity": escalation_result["escalation_velocity"],
                "funnel_status": escalation_result["funnel_status"],
                "is_funnel_escalation": escalation_result["is_funnel_escalation"],
                "active_stages": escalation_result["active_stages"],
                "stage_transitions": escalation_result["stage_transitions"],
                "narrative": escalation_result["narrative_explanation"]
            },
            "explainability": {
                "method": explainability_output["explainability_method"],
                "baseline_prior": explainability_output["baseline_prior"],
                "top_risk_drivers": explainability_output["top_risk_drivers"],
                "top_mitigating_factors": explainability_output["top_mitigating_factors"],
                "narrative": explainability_output["narrative_explanation"]
            },
            "safety_recommendations": {
                "priority": safety_output["priority_level"],
                "primary_action": safety_output["primary_action"],
                "actions": safety_output["action_items"],
                "verification_steps": safety_output["verification_steps"],
                "support_resources": safety_output["support_resources"]
            },
            "risk_timeline": {
                "trajectory_type": timeline_output["trajectory_type"],
                "initial_risk_score": timeline_output["initial_risk_score"],
                "peak_risk_score": timeline_output["peak_risk_score"],
                "final_risk_score": timeline_output["final_risk_score"],
                "checkpoints": timeline_output["checkpoints"],
                "milestones_count": len(timeline_output["milestones"]),
                "milestones": timeline_output["milestones"],
                "phase_analysis": timeline_output["phase_analysis"]
            },
            "messages": analyzed_messages
        }

    def analyze_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parses and performs complete end-to-end AI analysis on a conversation file.
        
        Args:
            file_path: Path to the .txt conversation file.
            
        Returns:
            Dict[str, Any]: Comprehensive analysis result.
        """
        path = Path(file_path)
        messages = self.parser.parse_file(path)
        return self.analyze_messages(messages, conversation_id=path.name)

    def analyze_text(self, conversation_text: str, conversation_id: str = "custom_text") -> Dict[str, Any]:
        """
        Parses and performs complete end-to-end AI analysis on a conversation text string.
        
        Args:
            conversation_text: Raw conversation string.
            conversation_id: Identifier name.
            
        Returns:
            Dict[str, Any]: Comprehensive analysis result.
        """
        messages = self.parser.parse_text(conversation_text)
        return self.analyze_messages(messages, conversation_id=conversation_id)

    def batch_analyze_directory(self, dir_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Executes end-to-end AI analysis across all conversation files in a directory.
        
        Args:
            dir_path: Path to directory containing .txt conversation files.
            
        Returns:
            List of comprehensive analysis results for every conversation.
        """
        path = Path(dir_path)
        files = sorted(list(path.glob("*.txt")))
        results = []
        for f in files:
            results.append(self.analyze_file(f))
        return results
