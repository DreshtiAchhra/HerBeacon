"""
HerBeacon - AI Analysis Engine
Module: ai.escalation

Escalation Engine component.
Analyzes behavioral stage progression, velocity, and escalation funnels
across conversational interactions.
"""

from typing import List, Dict, Any, Optional, Set


class EscalationEngine:
    """
    Evaluates the progression and velocity of behavioral stages in a conversation.
    
    Identifies how and when interpersonal interactions escalate from casual/trust building
    to boundary testing, financial extraction, urgency, and coercion.
    """

    STAGE_DEFINITIONS = {
        0: {
            "name": "Baseline / Normal Interaction",
            "description": "Standard introductory or social conversation with no detected harmful patterns.",
            "patterns": []
        },
        1: {
            "name": "Rapport & Trust Cultivation",
            "description": "Establishing unearned integrity, shared destiny, faith, or personal rapport.",
            "patterns": ["trust_building"]
        },
        2: {
            "name": "Affection Escalation & Migration",
            "description": "Rapid love bombing, excessive pet names, and pressure to migrate to off-platform channels.",
            "patterns": ["emotional_dependency", "move_communication"]
        },
        3: {
            "name": "Boundary Testing & Isolation",
            "description": "Attempts to isolate the individual, enforce secrecy, or request sensitive identification.",
            "patterns": ["secrecy", "isolation", "sensitive_info_request"]
        },
        4: {
            "name": "Financial Extraction & Manipulation",
            "description": "Direct or indirect financial requests, wire solicitations, gift cards, and guilt manipulation.",
            "patterns": ["financial_pressure", "emotional_manipulation"]
        },
        5: {
            "name": "Crisis, Urgency & Coercion",
            "description": "High-urgency artificial crises, deadlines, panic creation, or explicit extortion/blackmail.",
            "patterns": ["urgency", "coercion_threat"]
        }
    }

    def __init__(self):
        # Invert pattern mapping for quick lookup: pattern_key -> stage_number
        self._pattern_to_stage = {}
        for stage_num, config in self.STAGE_DEFINITIONS.items():
            for pkey in config["patterns"]:
                self._pattern_to_stage[pkey] = stage_num

    def evaluate_escalation(self, analyzed_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the full conversation for behavioral stage progression and transitions.
        
        Args:
            analyzed_messages: List of message dictionaries with detected 'patterns'.
            
        Returns:
            Dict containing:
            - max_stage (int): Highest behavioral stage reached (0 to 5)
            - max_stage_name (str)
            - active_stages (List[int])
            - stage_transitions (List[Dict]): Chronological stage advancement events
            - escalation_velocity (str): 'Rapid Escalation', 'Moderate Escalation', 'Gradual Progression', or 'None'
            - funnel_status (str): 'MULTI_PHASE_FUNNEL', 'LATE_STAGE_SURGE', 'EARLY_STAGE_PACING', 'NO_ESCALATION'
            - is_funnel_escalation (bool): True if verified multi-phase funnel progression occurred
            - escalation_score (float): 0.0 to 100.0 escalation index
            - narrative_explanation (str): Human-readable summary of escalation path
        """
        total_messages = len(analyzed_messages)
        if total_messages == 0:
            return self._get_empty_escalation_result()

        current_stage = 0
        active_stages = set([0])
        stage_first_seen = {0: 1}  # Stage 0 seen at message 1
        transitions = []
        
        # Track timeline of stage activations
        for msg in analyzed_messages:
            msg_idx = msg.get("message_index", 1)
            patterns = msg.get("patterns", [])
            speaker = msg.get("speaker", "Unknown")

            for p in patterns:
                pkey = p.get("pattern_key")
                stage = self._pattern_to_stage.get(pkey, 0)

                if stage > 0:
                    active_stages.add(stage)
                    if stage not in stage_first_seen:
                        stage_first_seen[stage] = msg_idx

                    # Check for upward stage transition
                    if stage > current_stage:
                        transitions.append({
                            "from_stage": current_stage,
                            "from_stage_name": self.STAGE_DEFINITIONS[current_stage]["name"],
                            "to_stage": stage,
                            "to_stage_name": self.STAGE_DEFINITIONS[stage]["name"],
                            "message_index": msg_idx,
                            "relative_position": round(msg_idx / total_messages, 3),
                            "speaker": speaker,
                            "trigger_pattern": p.get("pattern_name", pkey),
                            "evidence": p.get("evidence", [])
                        })
                        current_stage = stage

        max_stage = max(active_stages)
        
        # Calculate Escalation Velocity
        velocity_str, span_ratio = self._calculate_velocity(stage_first_seen, max_stage, total_messages)

        # Rigorous funnel verification
        funnel_status, is_funnel = self._evaluate_funnel_status(stage_first_seen, max_stage)

        # Compute Escalation Score (0 to 100)
        escalation_score = self._compute_escalation_score(max_stage, len(active_stages), span_ratio)

        # Generate Narrative Explanation
        narrative = self._generate_narrative(max_stage, active_stages, transitions, velocity_str, funnel_status)

        return {
            "max_stage": max_stage,
            "max_stage_name": self.STAGE_DEFINITIONS[max_stage]["name"],
            "active_stages": sorted(list(active_stages)),
            "stage_transitions": transitions,
            "escalation_velocity": velocity_str,
            "funnel_status": funnel_status,
            "is_funnel_escalation": is_funnel,
            "escalation_score": round(escalation_score, 1),
            "narrative_explanation": narrative
        }

    def _calculate_velocity(self, stage_first_seen: Dict[int, int], max_stage: int, total_messages: int) -> tuple[str, float]:
        if max_stage == 0 or total_messages == 0:
            return "None", 1.0

        earliest_trigger_idx = min([idx for stage, idx in stage_first_seen.items() if stage > 0], default=1)
        max_stage_idx = stage_first_seen.get(max_stage, earliest_trigger_idx)
        
        span_msgs = max_stage_idx - earliest_trigger_idx
        span_ratio = span_msgs / max(1, total_messages)

        if max_stage >= 4 and span_ratio < 0.15:
            return "Rapid Escalation", span_ratio
        elif max_stage >= 3 and span_ratio < 0.40:
            return "Moderate Escalation", span_ratio
        elif max_stage >= 1:
            return "Gradual Progression", span_ratio
        return "None", span_ratio

    def _evaluate_funnel_status(self, stage_first_seen: Dict[int, int], max_stage: int) -> tuple[str, bool]:
        """
        Evaluates whether genuine multi-phase grooming funnel progression occurred.
        
        A multi-phase funnel requires BOTH:
        1. An observed early rapport/affection stage (Stage 1 or 2).
        2. An observed late extraction/crisis stage (Stage 4 or 5) that chronologically followed the early stage.
        """
        early_stage_indices = [stage_first_seen[s] for s in [1, 2] if s in stage_first_seen]
        late_stage_indices = [stage_first_seen[s] for s in [4, 5] if s in stage_first_seen]

        if max_stage == 0:
            return "NO_ESCALATION", False

        if early_stage_indices and late_stage_indices:
            if min(early_stage_indices) < min(late_stage_indices):
                return "MULTI_PHASE_FUNNEL", True
            else:
                return "OUT_OF_ORDER_ESCALATION", False
        elif late_stage_indices and not early_stage_indices:
            # Late stage triggers appeared without earlier grooming phases
            return "LATE_STAGE_SURGE", False
        elif early_stage_indices and not late_stage_indices:
            return "EARLY_STAGE_PACING", False

        return "PARTIAL_PROGRESSION", False

    def _compute_escalation_score(self, max_stage: int, active_stage_count: int, span_ratio: float) -> float:
        base = (max_stage / 5.0) * 70.0
        diversity = min(15.0, (active_stage_count / 6.0) * 15.0)
        
        velocity_bonus = 0.0
        if max_stage >= 3:
            velocity_bonus = max(0.0, (1.0 - span_ratio) * 15.0)

        score = min(100.0, base + diversity + velocity_bonus)
        return score

    def _generate_narrative(
        self,
        max_stage: int,
        active_stages: Set[int],
        transitions: List[Dict[str, Any]],
        velocity: str,
        funnel_status: str
    ) -> str:
        if max_stage == 0:
            return "Interaction remains within baseline conversational parameters with no escalating behavioral cues."

        stage_names = [self.STAGE_DEFINITIONS[s]["name"] for s in sorted(active_stages) if s > 0]
        summary_parts = [
            f"Conversation progressed to Stage {max_stage} ({self.STAGE_DEFINITIONS[max_stage]['name']}).",
            f"Observed behavioral stages: {', '.join(stage_names)}.",
            f"Escalation dynamic is evaluated as {velocity.lower()}."
        ]

        if funnel_status == "MULTI_PHASE_FUNNEL":
            summary_parts.append(
                "The conversation exhibits a classic multi-phase funnel: initial trust cultivation was followed by emotional escalation and subsequent financial solicitations."
            )
        elif funnel_status == "LATE_STAGE_SURGE":
            summary_parts.append(
                "Late-stage risk indicators were detected without sufficient evidence of earlier conversational grooming phases."
            )
        elif funnel_status == "EARLY_STAGE_PACING":
            summary_parts.append(
                "Early-stage rapport and affection cues were observed without progressing to financial solicitations or crisis coercion."
            )

        return " ".join(summary_parts)

    def _get_empty_escalation_result(self) -> Dict[str, Any]:
        return {
            "max_stage": 0,
            "max_stage_name": self.STAGE_DEFINITIONS[0]["name"],
            "active_stages": [0],
            "stage_transitions": [],
            "escalation_velocity": "None",
            "funnel_status": "NO_ESCALATION",
            "is_funnel_escalation": False,
            "escalation_score": 0.0,
            "narrative_explanation": "Empty conversation."
        }
