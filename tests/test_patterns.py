"""
Test Behavioural Pattern Detection on real LoveFraud02 conversation data.
"""

from pathlib import Path
import sys

# Ensure repository root is in sys.path
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.parser import ConversationParser
from ai.patterns import BehaviouralPatternDetector


def run_pattern_test(sample_file: str = "AlbertCasey.txt", display_limit: int = 6):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 65)
    print(f"TESTING BEHAVIOURAL PATTERN DETECTOR: {sample_file}")
    print("=" * 65)
    print(f"File Path: {file_path}")

    parser = ConversationParser()
    messages = parser.parse_file(file_path)
    print(f"Total parsed messages: {len(messages)}")

    detector = BehaviouralPatternDetector()
    analyzed_messages = detector.analyze_conversation(messages)

    # Filter messages that triggered at least one behavioral pattern
    flagged_messages = [m for m in analyzed_messages if m.get("patterns")]
    print(f"Messages with detected behavioral patterns: {len(flagged_messages)}\n")

    print("-" * 65)
    print(f"SAMPLE DETECTED PATTERNS (First {min(display_limit, len(flagged_messages))} occurrences):")
    print("-" * 65)

    for item in flagged_messages[:display_limit]:
        print(f"Message {item['message_index']}")
        print(f"Speaker: {item['speaker']}")
        print(f"Message: {item['message']}")
        print("Detected Patterns:")
        for p in item["patterns"]:
            print(f"  - [{p['severity']}] {p['pattern_name']} (Confidence: {p['confidence']})")
            print(f"    Evidence: {p['evidence']}")
            print(f"    Explanation: {p['explanation']}")
        print()

    summary = detector.get_pattern_summary(analyzed_messages)
    print("=" * 65)
    print("BEHAVIOURAL PATTERN SUMMARY:")
    print("=" * 65)
    print(f"Total Pattern Cues Triggered: {summary['total_pattern_occurrences']}")
    print("\nPattern Breakdown:")
    for pkey, count in sorted(summary["pattern_counts"].items(), key=lambda x: x[1], reverse=True):
        pname = detector.PATTERN_RULES[pkey]["name"]
        print(f"  - {pname} ({pkey}): {count} times")

    print("\nSpeaker Breakdown:")
    for spk, spk_dict in summary["speaker_breakdown"].items():
        total_spk_patterns = sum(spk_dict.values())
        print(f"  Speaker '{spk}' ({total_spk_patterns} total pattern triggers):")
        for pkey, count in sorted(spk_dict.items(), key=lambda x: x[1], reverse=True):
            pname = detector.PATTERN_RULES[pkey]["name"]
            print(f"    * {pname}: {count}")

    print("=" * 65)
    print("BEHAVIOURAL PATTERN TEST COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    run_pattern_test()
