"""
Test Explainability on real LoveFraud02 data.
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
from ai.explainability import ShapExplainer


def run_explainability_test(sample_file: str = "AlbertCasey.txt"):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 65)
    print(f"TESTING EXPLAINABILITY ENGINE: {sample_file}")
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

    explainer = ShapExplainer(risk_model)
    exp_output = explainer.explain_prediction(features, escalation_result, risk_output)

    print(f"Explainability Method: {exp_output['explainability_method']}")
    print(f"Baseline Prior: {exp_output['baseline_prior']}/100")

    print(f"\n--- TOP RISK DRIVERS ---")
    for idx, d in enumerate(exp_output["top_risk_drivers"], 1):
        pts = d.get("contribution_points", d.get("shap_value", 0.0))
        print(f"  {idx}. {d['feature_name']}: +{pts} pts ({d.get('detail', '')})")

    print(f"\n--- NARRATIVE EXPLANATION ---")
    print(exp_output["narrative_explanation"])
    print("\n[PASS] Explainability test completed successfully.")


if __name__ == "__main__":
    run_explainability_test()
