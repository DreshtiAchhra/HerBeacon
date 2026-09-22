"""
Test Feature Engineering on real LoveFraud02 conversation data.
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


def run_features_test(sample_file: str = "AlbertCasey.txt"):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 65)
    print(f"TESTING FEATURE EXTRACTOR: {sample_file}")
    print("=" * 65)
    print(f"File Path: {file_path}")

    # Step 1: Parse
    parser = ConversationParser()
    messages = parser.parse_file(file_path)

    # Step 2: Detect Patterns
    detector = BehaviouralPatternDetector()
    analyzed_messages = detector.analyze_conversation(messages)

    # Step 3: Extract Features
    extractor = FeatureExtractor()
    features = extractor.extract_features(analyzed_messages)

    print(f"Total features extracted: {len(features)}\n")

    print("--- 1. CONVERSATION METRICS ---")
    print(f"Total Messages: {features['total_messages']}")
    print(f"Unique Speakers: {features['unique_speakers_count']}")
    print(f"Avg Chars / Msg: {features['avg_msg_chars']}")
    print(f"Avg Words / Msg: {features['avg_msg_words']}")

    print("\n--- 2. BEHAVIOURAL PATTERN COUNTS & DENSITIES (per 100 msgs) ---")
    for k in extractor.ALL_PATTERN_KEYS:
        count = features[f"count_{k}"]
        density = features[f"density_{k}"]
        first_pos = features[f"first_rel_pos_{k}"]
        pos_str = f"{first_pos * 100:.1f}% into convo" if first_pos >= 0 else "N/A"
        print(f"  - {k:<25}: Count = {count:<3} | Density = {density:<6.2f}% | First Seen = {pos_str}")

    print("\n--- 3. RELATIONAL & SEQUENTIAL DYNAMICS ---")
    print(f"Love Before Money Flag: {bool(features['love_before_money_flag'])}")
    print(f"Early Platform Switch Flag: {bool(features['early_platform_switch_flag'])}")

    print("\n--- 4. CONVERSATIONAL PHASE DYNAMICS ---")
    print(f"Early Phase Cues (0-33%): {features['phase_early_cues']}")
    print(f"Mid Phase Cues (33-66%): {features['phase_mid_cues']}")
    print(f"Late Phase Cues (66-100%): {features['phase_late_cues']}")
    print(f"Escalation Gradient: {features['escalation_gradient']}")

    print("\n--- 5. AGGREGATE SEVERITY METRICS ---")
    print(f"Total Pattern Triggers: {features['total_pattern_triggers']}")
    print(f"Weighted Severity Score: {features['weighted_severity_score']}")
    print(f"High/Critical Severity Ratio: {features['high_critical_ratio'] * 100:.1f}%")
    print(f"Risk Signal Density: {features['risk_signal_density']:.4f}")

    print("=" * 65)
    print("FEATURE EXTRACTION TEST COMPLETED SUCCESSFULLY")
    print("=" * 65)


if __name__ == "__main__":
    run_features_test()
