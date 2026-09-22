"""
Test Risk Scoring Model on real LoveFraud02 data.
"""

from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.parser import ConversationParser
from ai.patterns import BehaviouralPatternDetector
from ai.features import FeatureExtractor
from ai.escalation import EscalationEngine
from ai.risk_model import RiskScoringModel


def run_risk_model_test(sample_file: str = "AlbertCasey.txt"):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 65)
    print(f"TESTING RISK SCORING MODEL: {sample_file}")
    print("=" * 65)

    parser = ConversationParser()
    messages = parser.parse_file(file_path)

    detector = BehaviouralPatternDetector()
    analyzed_messages = detector.analyze_conversation(messages)

    extractor = FeatureExtractor()
    features = extractor.extract_features(analyzed_messages)

    escalation_engine = EscalationEngine()
    escalation_result = escalation_engine.evaluate_escalation(analyzed_messages)

    risk_model = RiskScoringModel()
    risk_output = risk_model.calculate_risk(features, escalation_result)

    print(f"Analysis Mode: {risk_output['analysis_mode']}")
    print(f"Risk Score: {risk_output['risk_score']}/100")
    print(f"Risk Level: {risk_output['risk_level']}")
    print(f"Highest Stage Reached: Stage {risk_output['max_stage']} ({risk_output['max_stage_name']})")

    print(f"\n--- FACTOR CONTRIBUTION BREAKDOWN ---")
    for factor_k, pts in risk_output["factor_breakdown"].items():
        print(f"  * {factor_k:<28}: +{pts} pts")

    print(f"\n--- PRIMARY CONTRIBUTING RISK FACTORS ---")
    for idx, factor in enumerate(risk_output["primary_risk_factors"], 1):
        print(f"  {idx}. [{factor['impact']}] {factor['factor']}")
        print(f"     Details: {factor['detail']}")

    print(f"\n--- DECISION SUPPORT SUMMARY ---")
    print(risk_output["decision_support_summary"])

    assert 0 <= risk_output["risk_score"] <= 100, "Score out of range 0-100!"
    print("\n[PASS] Risk model test completed successfully.")


if __name__ == "__main__":
    run_risk_model_test()
