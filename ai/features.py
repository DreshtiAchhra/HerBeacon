"""
HerBeacon - AI Analysis Engine
Module: ai.features

Feature Engineering component.
Transforms parsed and behavioral pattern-annotated conversations into
structured numerical and relational feature vectors for ML modeling,
escalation detection, and explainability.
"""

from typing import List, Dict, Any, Optional


class FeatureExtractor:
    """
    Extracts structured, explainable features from behavioral pattern-annotated conversations.
    
    Feature Categories:
    1. Metadata & Text Metrics: message count, word count, character count.
    2. Pattern Counts: raw integer count of occurrences per behavioral category.
    3. Pattern Densities: normalized occurrences per 100 messages (count / total_messages * 100).
    4. First Occurrence Timing: relative conversation position (0.0 to 1.0, or -1.0 if absent).
    5. Relational & Sequential Dynamics: love-before-money flag, early platform switch flag.
    6. Conversational Phase Dynamics: early (0-33%), mid (33-66%), late (66-100%) cue counts.
    7. Aggregate Severity Metrics: weighted severity score, high/critical ratio, risk signal density.
    """

    SEVERITY_WEIGHTS = {
        "LOW": 1.0,
        "MEDIUM": 2.0,
        "HIGH": 4.0,
        "CRITICAL": 8.0
    }

    ALL_PATTERN_KEYS = [
        "trust_building",
        "emotional_dependency",
        "move_communication",
        "secrecy",
        "isolation",
        "financial_pressure",
        "urgency",
        "sensitive_info_request",
        "emotional_manipulation",
        "coercion_threat"
    ]

    def __init__(self):
        pass

    def extract_features(self, analyzed_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extracts a comprehensive dictionary of numerical and categorical features
        from a list of pattern-analyzed messages.
        
        Args:
            analyzed_messages: List of message dictionaries containing 'message_index',
                               'speaker', 'message', and 'patterns'.
                               
        Returns:
            Dict[str, Any]: Structured feature vector.
        """
        total_messages = len(analyzed_messages)
        if total_messages == 0:
            return self._get_empty_feature_vector()

        # 1. Basic Metadata & Text Metrics
        speakers = set()
        total_chars = 0
        total_words = 0
        speaker_msg_counts = {}

        for msg in analyzed_messages:
            spk = msg.get("speaker", "Unknown")
            speakers.add(spk)
            speaker_msg_counts[spk] = speaker_msg_counts.get(spk, 0) + 1
            
            text = msg.get("message", "")
            total_chars += len(text)
            total_words += len(text.split())

        avg_msg_chars = total_chars / max(1, total_messages)
        avg_msg_words = total_words / max(1, total_messages)

        # 2. Behavioral Pattern Counts and First Occurrence Tracking
        pattern_counts = {k: 0 for k in self.ALL_PATTERN_KEYS}
        pattern_first_idx = {k: -1 for k in self.ALL_PATTERN_KEYS}
        pattern_first_rel_pos = {k: -1.0 for k in self.ALL_PATTERN_KEYS}
        
        # Track triggers across conversation phases (Early: first 33%, Mid: 33-66%, Late: >66%)
        phase_early_cues = 0
        phase_mid_cues = 0
        phase_late_cues = 0

        weighted_severity_score = 0.0
        high_critical_count = 0
        total_pattern_triggers = 0

        for i, msg in enumerate(analyzed_messages):
            rel_pos = (i + 1) / max(1, total_messages)
            msg_patterns = msg.get("patterns", [])
            
            # Phase attribution
            if rel_pos <= 0.33:
                phase_early_cues += len(msg_patterns)
            elif rel_pos <= 0.66:
                phase_mid_cues += len(msg_patterns)
            else:
                phase_late_cues += len(msg_patterns)

            for p in msg_patterns:
                pkey = p.get("pattern_key")
                severity = p.get("severity", "LOW")
                
                total_pattern_triggers += 1
                if pkey in pattern_counts:
                    pattern_counts[pkey] += 1
                    if pattern_first_idx[pkey] == -1:
                        pattern_first_idx[pkey] = msg.get("message_index", i + 1)
                        pattern_first_rel_pos[pkey] = round(rel_pos, 4)

                # Severity weighting
                weight = self.SEVERITY_WEIGHTS.get(severity, 1.0)
                weighted_severity_score += weight

                if severity in ("HIGH", "CRITICAL"):
                    high_critical_count += 1

        # 3. Density & Relational Features (normalized per 100 messages)
        densities = {
            f"density_{k}": round((pattern_counts[k] / max(1, total_messages)) * 100, 3)
            for k in self.ALL_PATTERN_KEYS
        }

        # Sequence heuristics
        # Love bombing before financial request?
        love_pos = pattern_first_rel_pos["emotional_dependency"]
        money_pos = pattern_first_rel_pos["financial_pressure"]
        love_before_money = 1.0 if (love_pos > 0 and money_pos > 0 and love_pos < money_pos) else 0.0

        # Platform switch in first 20% of conversation?
        switch_pos = pattern_first_rel_pos["move_communication"]
        early_platform_switch = 1.0 if (0 < switch_pos <= 0.20) else 0.0

        # Escalation gradient: (mid + late cues) / (early cues + 1)
        escalation_gradient = round((phase_mid_cues + phase_late_cues) / (phase_early_cues + 1.0), 3)

        high_critical_ratio = round((high_critical_count / total_pattern_triggers), 3) if total_pattern_triggers > 0 else 0.0
        risk_signal_density = round((total_pattern_triggers / max(1, total_messages)), 4)

        # Assemble Final Feature Vector
        features = {
            # Metadata
            "total_messages": total_messages,
            "unique_speakers_count": len(speakers),
            "avg_msg_chars": round(avg_msg_chars, 2),
            "avg_msg_words": round(avg_msg_words, 2),
            
            # Raw Counts
            **{f"count_{k}": pattern_counts[k] for k in self.ALL_PATTERN_KEYS},
            
            # Densities (per 100 messages)
            **densities,
            
            # Relative Positional Timing (0.0 to 1.0, or -1.0 if absent)
            **{f"first_rel_pos_{k}": pattern_first_rel_pos[k] for k in self.ALL_PATTERN_KEYS},
            
            # Relational & Sequential Dynamics
            "love_before_money_flag": love_before_money,
            "early_platform_switch_flag": early_platform_switch,
            
            # Phase Dynamics
            "phase_early_cues": phase_early_cues,
            "phase_mid_cues": phase_mid_cues,
            "phase_late_cues": phase_late_cues,
            "escalation_gradient": escalation_gradient,
            
            # Aggregate Severity Metrics
            "total_pattern_triggers": total_pattern_triggers,
            "weighted_severity_score": round(weighted_severity_score, 2),
            "high_critical_ratio": high_critical_ratio,
            "risk_signal_density": risk_signal_density
        }

        return features

    def _get_empty_feature_vector(self) -> Dict[str, Any]:
        """Returns a zeroed feature vector for empty conversations."""
        empty = {
            "total_messages": 0,
            "unique_speakers_count": 0,
            "avg_msg_chars": 0.0,
            "avg_msg_words": 0.0,
            "love_before_money_flag": 0.0,
            "early_platform_switch_flag": 0.0,
            "phase_early_cues": 0,
            "phase_mid_cues": 0,
            "phase_late_cues": 0,
            "escalation_gradient": 0.0,
            "total_pattern_triggers": 0,
            "weighted_severity_score": 0.0,
            "high_critical_ratio": 0.0,
            "risk_signal_density": 0.0
        }
        for k in self.ALL_PATTERN_KEYS:
            empty[f"count_{k}"] = 0
            empty[f"density_{k}"] = 0.0
            empty[f"first_rel_pos_{k}"] = -1.0
        return empty
