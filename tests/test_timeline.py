"""
Test Risk Timeline Generator on real LoveFraud02 conversation data.
"""

from pathlib import Path
import sys

# Ensure repository root is in sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.parser import ConversationParser
from ai.patterns import BehaviouralPatternDetector
from ai.timeline import RiskTimelineGenerator


def run_timeline_test(sample_file: str = "AlbertCasey.txt"):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 65)
    print(f"TESTING RISK TIMELINE GENERATOR: {sample_file}")
    print("=" * 65)
    print(f"File Path: {file_path}")

    # Pipeline: Parse -> Patterns -> Timeline
    parser = ConversationParser()
    messages = parser.parse_file(file_path)

    detector = BehaviouralPatternDetector()
    analyzed_messages = detector.analyze_conversation(messages)

    timeline_gen = RiskTimelineGenerator()
    timeline = timeline_gen.generate_timeline(analyzed_messages, num_checkpoints=10)

    print(f"\n--- TRAJECTORY PROFILE ---")
    print(f"Trajectory Classification: {timeline['trajectory_type']}")
    print(f"Initial Risk: {timeline['initial_risk_score']}/100 -> Peak Risk: {timeline['peak_risk_score']}/100 -> Final Risk: {timeline['final_risk_score']}/100")

    print(f"\n--- 10-POINT TEMPORAL CHECKPOINTS ---")
    for cp in timeline["checkpoints"]:
        print(f"  Checkpoint {cp['checkpoint']:>2} ({cp['percentage']:>4} | Msg {cp['message_index']:>3}): Risk = {cp['cumulative_risk_score']:>3}/100 [{cp['risk_level']}]")

    print(f"\n--- KEY RISK INFLECTION MILESTONES (First 5) ---")
    for m in timeline["milestones"][:5]:
        print(f"  * Msg {m['message_index']:>3} ({m['relative_position'] * 100:4.1f}% | {m['speaker']}) -> Risk: {m['risk_score_at_message']}/100 (+{m['score_delta']} pts)")
        print(f"    Triggers: {', '.join(m['patterns_triggered'])}")
        print(f"    Evidence: {m['evidence']}")
        print(f"    Snippet: {repr(m['snippet'])}")
        print()

    print(f"--- CONVERSATIONAL PHASE BREAKDOWN ---")
    for phase_key, phase_info in timeline["phase_analysis"].items():
        print(f"  * {phase_info['phase_name']} ({phase_info['message_count']} msgs, {phase_info['total_cues']} cues):")
        for pname, count in phase_info["dominant_patterns"]:
            print(f"    - {pname}: {count} cues")

    print("=" * 65)
    print("RISK TIMELINE TEST COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    run_timeline_test()
