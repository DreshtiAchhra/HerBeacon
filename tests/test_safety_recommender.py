"""
Test Safety Recommendation Engine on real LoveFraud02 conversation data.
"""

from pathlib import Path
import sys

# Ensure repository root is in sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.parser import ConversationParser
from ai.patterns import BehaviouralPatternDetector
from ai.features import FeatureExtractor
from ai.escalation import EscalationEngine
from ai.risk_model import RiskScoringModel
from ai.safety_recommender import SafetyRecommendationEngine


def run_safety_test(sample_file: str = "AlbertCasey.txt"):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 65)
    print(f"TESTING SAFETY RECOMMENDATION ENGINE: {sample_file}")
    print("=" * 65)
    print(f"File Path: {file_path}")

    # Pipeline: Parse -> Patterns -> Features -> Escalation -> Risk -> Safety Recommendations
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

    recommender = SafetyRecommendationEngine()
    recommendations = recommender.generate_recommendations(features, escalation_result, risk_output)

    print(f"\n--- PRIMARY SAFETY DIRECTIVE ---")
    print(f"Priority: [{recommendations['priority_level']}]")
    print(f"Directive: {recommendations['primary_action']}")

    print(f"\n--- ACTIONABLE SAFETY MEASURES ({len(recommendations['action_items'])} items) ---")
    for idx, item in enumerate(recommendations["action_items"], 1):
        print(f"  {idx}. [{item['priority']}] {item['headline']}")
        print(f"     Action: {item['action']}")
        print(f"     Rationale: {item['rationale']}")
        print()

    print(f"--- RECOMMENDED VERIFICATION STEPS ---")
    for idx, step in enumerate(recommendations["verification_steps"], 1):
        print(f"  {idx}. {step}")

    print(f"\n--- EMERGENCY SUPPORT RESOURCES ---")
    for cat, res_list in recommendations["support_resources"].items():
        print(f"  * {cat.replace('_', ' ').title()}:")
        for res in res_list:
            contact_info = res.get("url") or res.get("contact")
            print(f"    - {res['name']}: {contact_info}")

    print("=" * 65)
    print("SAFETY RECOMMENDATION TEST COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    run_safety_test()
