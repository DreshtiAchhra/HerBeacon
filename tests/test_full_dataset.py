"""
Full 83-Conversation Dataset Analysis over LoveFraud02.
Produces descriptive corpus statistics across all conversations.
"""

from pathlib import Path
import sys
from collections import Counter

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.pipeline import HerBeaconAnalysisEngine


def run_full_dataset_analysis():
    data_dir = repo_root / "data" / "LoveFraud02"
    files = sorted(list(data_dir.glob("*.txt")))
    
    print("=" * 70)
    print(f"HERBEACON - FULL DATASET ANALYSIS ({len(files)} Conversations)")
    print("=" * 70)

    engine = HerBeaconAnalysisEngine()
    
    total_conversations = len(files)
    total_messages = 0
    risk_scores = []
    risk_levels = Counter()
    max_stages = Counter()
    funnel_statuses = Counter()
    pattern_totals = Counter()
    conversations_with_patterns = 0

    # Process each conversation
    for idx, f in enumerate(files, 1):
        result = engine.analyze_file(f)
        total_messages += result["metadata"]["total_messages"]
        
        score = result["risk_assessment"]["risk_score"]
        level = result["risk_assessment"]["risk_level"]
        stage = result["escalation_analysis"]["max_stage"]
        funnel = result["escalation_analysis"]["funnel_status"]
        
        risk_scores.append(score)
        risk_levels[level] += 1
        max_stages[stage] += 1
        funnel_statuses[funnel] += 1

        p_counts = result["behavioral_patterns"]["pattern_counts"]
        if sum(p_counts.values()) > 0:
            conversations_with_patterns += 1
        for pkey, cnt in p_counts.items():
            pattern_totals[pkey] += cnt

    avg_risk = sum(risk_scores) / max(1, total_conversations)
    max_risk = max(risk_scores) if risk_scores else 0
    min_risk = min(risk_scores) if risk_scores else 0

    print(f"\n[1] CORPUS SUMMARY")
    print(f"    - Total Conversations Analysed: {total_conversations}")
    print(f"    - Total Messages Analysed: {total_messages}")
    print(f"    - Conversations with Detected Patterns: {conversations_with_patterns}/{total_conversations} ({conversations_with_patterns/total_conversations*100:.1f}%)")

    print(f"\n[2] RISK SCORE DISTRIBUTION")
    print(f"    - Average Risk Score: {avg_risk:.1f}/100")
    print(f"    - Minimum Risk Score: {min_risk}/100")
    print(f"    - Maximum Risk Score: {max_risk}/100")
    print(f"    - Risk Level Breakdown:")
    for lvl in ["LOW", "MODERATE", "HIGH", "CRITICAL"]:
        print(f"      * {lvl:<10}: {risk_levels[lvl]:>3} conversations ({risk_levels[lvl]/total_conversations*100:.1f}%)")

    print(f"\n[3] ESCALATION STAGE DISTRIBUTION")
    for stage_num in range(6):
        s_name = engine.escalation_engine.STAGE_DEFINITIONS[stage_num]["name"]
        print(f"    - Stage {stage_num} ({s_name}): {max_stages[stage_num]:>3} conversations ({max_stages[stage_num]/total_conversations*100:.1f}%)")

    print(f"\n[4] FUNNEL CLASSIFICATION DISTRIBUTION")
    for f_status, count in funnel_statuses.most_common():
        print(f"    - {f_status:<25}: {count:>3} conversations ({count/total_conversations*100:.1f}%)")

    print(f"\n[5] BEHAVIOURAL PATTERN FREQUENCIES ACROSS DATASET")
    for pkey, total_count in pattern_totals.most_common():
        pname = engine.pattern_detector.PATTERN_RULES[pkey]["name"]
        print(f"    - {pname:<38} ({pkey}): {total_count:>4} occurrences")

    print("\n" + "=" * 70)
    print("FULL DATASET ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    run_full_dataset_analysis()
