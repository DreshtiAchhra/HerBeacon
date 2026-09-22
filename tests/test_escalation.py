"""
Test Escalation Engine on real LoveFraud02 data and specific funnel edge cases.
"""

from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.parser import ConversationParser
from ai.patterns import BehaviouralPatternDetector
from ai.escalation import EscalationEngine


def test_escalation_funnel_logic():
    detector = BehaviouralPatternDetector()
    escalation_engine = EscalationEngine()

    # Case A: Only Late Stage triggers (Stage 4 financial + Stage 5 urgency) without early rapport
    late_only_messages = [
        {"message_index": 1, "speaker": "UserA", "message": "Hi"},
        {"message_index": 2, "speaker": "UserB", "message": "Send me money immediately via bank transfer, it is an urgent emergency!"}
    ]
    analyzed_late = detector.analyze_conversation(late_only_messages)
    res_late = escalation_engine.evaluate_escalation(analyzed_late)
    
    print("Test Case A: Late Stage Triggers Alone")
    print(f"  Max Stage: {res_late['max_stage']} ({res_late['max_stage_name']})")
    print(f"  Funnel Status: {res_late['funnel_status']}")
    print(f"  Is Funnel Escalation: {res_late['is_funnel_escalation']}")
    assert res_late["is_funnel_escalation"] is False, "Late triggers alone should NOT be classified as multi-phase funnel!"
    assert res_late["funnel_status"] == "LATE_STAGE_SURGE"
    print("  [PASS] Late stage surge correctly detected without fabricating a multi-phase grooming history.")

    # Case B: Multi-Phase Funnel (Stage 1 Trust -> Stage 2 Love -> Stage 4 Money -> Stage 5 Urgency)
    funnel_messages = [
        {"message_index": 1, "speaker": "UserA", "message": "Hello."},
        {"message_index": 2, "speaker": "UserB", "message": "I am an honest man and believe destiny brought us together."},
        {"message_index": 3, "speaker": "UserB", "message": "My darling, I am falling in love with you and cannot live without you."},
        {"message_index": 4, "speaker": "UserB", "message": "Please send money for my customs fee urgently right now!"}
    ]
    analyzed_funnel = detector.analyze_conversation(funnel_messages)
    res_funnel = escalation_engine.evaluate_escalation(analyzed_funnel)
    
    print("\nTest Case B: True Multi-Phase Grooming Funnel")
    print(f"  Max Stage: {res_funnel['max_stage']} ({res_funnel['max_stage_name']})")
    print(f"  Funnel Status: {res_funnel['funnel_status']}")
    print(f"  Is Funnel Escalation: {res_funnel['is_funnel_escalation']}")
    assert res_funnel["is_funnel_escalation"] is True, "Expected verified multi-phase funnel escalation!"
    assert res_funnel["funnel_status"] == "MULTI_PHASE_FUNNEL"
    print("  [PASS] Multi-phase grooming sequence verified.")


def test_escalation_real_file(sample_file: str = "AlbertCasey.txt"):
    fpath = repo_root / "data" / "LoveFraud02" / sample_file
    parser = ConversationParser()
    messages = parser.parse_file(fpath)

    detector = BehaviouralPatternDetector()
    analyzed_messages = detector.analyze_conversation(messages)

    escalation_engine = EscalationEngine()
    result = escalation_engine.evaluate_escalation(analyzed_messages)

    print(f"\nReal File Test ({sample_file}):")
    print(f"  Max Stage: Stage {result['max_stage']} ({result['max_stage_name']})")
    print(f"  Escalation Score: {result['escalation_score']}/100")
    print(f"  Velocity: {result['escalation_velocity']}")
    print(f"  Funnel Status: {result['funnel_status']}")
    print(f"  Narrative: {result['narrative_explanation']}")
    print("  [PASS] Escalation analysis completed.")


if __name__ == "__main__":
    test_escalation_funnel_logic()
    test_escalation_real_file()
