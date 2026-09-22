"""
Test End-to-End AI Analysis Pipeline on real LoveFraud02 conversation data.
"""

from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.pipeline import HerBeaconAnalysisEngine


def run_pipeline_test(sample_file: str = "AlbertCasey.txt"):
    file_path = repo_root / "data" / "LoveFraud02" / sample_file
    print("=" * 70)
    print(f"HERBEACON - END-TO-END AI ANALYSIS ENGINE TEST: {sample_file}")
    print("=" * 70)
    print(f"File Path: {file_path}")

    engine = HerBeaconAnalysisEngine()
    result = engine.analyze_file(file_path)

    # 1. Metadata
    meta = result["metadata"]
    print(f"\n[1] CONVERSATION METADATA")
    print(f"    - Conversation ID: {result['conversation_id']}")
    print(f"    - Analysis Mode: {result['analysis_mode']}")
    print(f"    - Total Messages: {meta['total_messages']}")
    print(f"    - Speakers: {', '.join(meta['speakers'])}")
    print(f"    - Avg Words/Message: {meta['avg_words_per_message']}")

    # 2. Risk Assessment
    risk = result["risk_assessment"]
    print(f"\n[2] RISK ASSESSMENT")
    print(f"    - Risk Score: {risk['risk_score']}/100")
    print(f"    - Risk Level: {risk['risk_level']}")
    print(f"    - Max Stage Reached: Stage {risk['max_stage']} ({risk['max_stage_name']})")
    print(f"    - Summary: {risk['summary']}")
    print(f"    - Disclaimer: {risk['safety_disclaimer']}")

    # 3. Behavioral Patterns
    patterns = result["behavioral_patterns"]
    print(f"\n[3] BEHAVIOURAL PATTERNS DETECTED")
    print(f"    - Total Cues: {patterns['total_cues_detected']} across {patterns['flagged_message_count']} flagged messages")
    for pkey, count in sorted(patterns["pattern_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"      * {pkey}: {count} occurrences")

    # 4. Escalation Progression
    esc = result["escalation_analysis"]
    print(f"\n[4] ESCALATION ENGINE")
    print(f"    - Escalation Score: {esc['escalation_score']}/100")
    print(f"    - Velocity: {esc['velocity']}")
    print(f"    - Funnel Status: {esc['funnel_status']} (is_funnel: {esc['is_funnel_escalation']})")
    print(f"    - Narrative: {esc['narrative']}")

    # 5. Explainability
    exp_info = result["explainability"]
    print(f"\n[5] EXPLAINABILITY ({exp_info['method']})")
    print(f"    - Baseline Prior: {exp_info['baseline_prior']}/100")
    print(f"    - Top Risk Drivers:")
    for d in exp_info["top_risk_drivers"][:3]:
        pts = d.get("contribution_points", d.get("shap_value", 0.0))
        print(f"      * {d['feature_name']}: +{pts} pts ({d.get('detail', '')})")
    print(f"    - Narrative: {exp_info['narrative']}")

    # 6. Safety Recommendations
    safety = result["safety_recommendations"]
    print(f"\n[6] SAFETY RECOMMENDATIONS")
    print(f"    - Priority Directive: [{safety['priority']}] {safety['primary_action']}")
    print(f"    - Action Items ({len(safety['actions'])} items):")
    for item in safety["actions"][:2]:
        print(f"      * [{item['priority']}] {item['headline']}: {item['action']}")

    # 7. Risk Timeline
    tl = result["risk_timeline"]
    print(f"\n[7] RISK TIMELINE")
    print(f"    - Trajectory Type: {tl['trajectory_type']}")
    print(f"    - Initial -> Peak -> Final: {tl['initial_risk_score']} -> {tl['peak_risk_score']} -> {tl['final_risk_score']}")
    print(f"    - Total Milestones Recorded: {tl['milestones_count']}")
    print(f"    - Checkpoints Sample:")
    for cp in [tl["checkpoints"][0], tl["checkpoints"][4], tl["checkpoints"][-1]]:
        print(f"      * {cp['percentage']} (Msg {cp['message_index']}): Cumulative Risk {cp['cumulative_risk_score']}/100 [{cp['risk_level']}]")

    print("\n" + "=" * 70)
    print("END-TO-END AI PIPELINE TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline_test()
