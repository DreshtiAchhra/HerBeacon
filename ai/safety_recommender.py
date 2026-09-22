"""
HerBeacon - AI Analysis Engine
Module: ai.safety_recommender

Safety Recommendation Engine component.
Generates tailored, actionable, and non-judgmental safety guidance
and verification steps based on detected behavioral patterns and risk levels.
"""

from typing import List, Dict, Any, Optional


class SafetyRecommendationEngine:
    """
    Rule-based, explainable safety recommendation generator.
    
    Transforms behavioral risk signals and escalation stages into concrete,
    protective action items, verification checklists, and crisis support guidance.
    """

    DEFAULT_SUPPORT_RESOURCES = {
        "india_cybercrime_helpline": [
            {"name": "National Cyber Crime Reporting Portal (India)", "contact": "Helpline: 1930 | https://cybercrime.gov.in"},
            {"name": "National Commission for Women (NCW) Helpline", "contact": "Helpline: 7827170170 | http://ncw.nic.in"}
        ],
        "international_reporting": [
            {"name": "FBI Internet Crime Complaint Center (IC3 - US)", "url": "https://www.ic3.gov"},
            {"name": "Action Fraud (UK)", "url": "https://www.actionfraud.police.uk"},
            {"name": "Scamwatch (Australia)", "url": "https://www.scamwatch.gov.au"}
        ],
        "emotional_and_crisis_support": [
            {"name": "iCall Psychosocial Helpline (India)", "contact": "9152987821"},
            {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
            {"name": "VictimConnect Resource Center", "contact": "Call/Text 1-855-4-VICTIM"}
        ]
    }

    def __init__(self, custom_resources: Optional[Dict[str, Any]] = None):
        self.support_resources = custom_resources if custom_resources is not None else self.DEFAULT_SUPPORT_RESOURCES

    def generate_recommendations(
        self,
        features: Dict[str, Any],
        escalation_result: Dict[str, Any],
        risk_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates contextual safety recommendations based on analysis results.
        
        Args:
            features: Dictionary produced by FeatureExtractor.
            escalation_result: Dictionary produced by EscalationEngine.
            risk_output: Dictionary produced by RiskScoringModel.
            
        Returns:
            Dict containing:
            - primary_action (str)
            - priority_level (str)
            - action_items (List[Dict])
            - verification_steps (List[str])
            - support_resources (Dict)
        """
        risk_level = risk_output.get("risk_level", "LOW")
        max_stage = escalation_result.get("max_stage", 0)

        action_items: List[Dict[str, Any]] = []
        verification_steps: List[str] = []

        # 1. Financial Solicitation Guidance
        if features.get("count_financial_pressure", 0) > 0:
            action_items.append({
                "priority": "CRITICAL",
                "category": "Financial Protection",
                "headline": "Do Not Send Money or Share Financial Details",
                "action": "Decline all requests for bank transfers, gift cards, cryptocurrency, or customs/fee clearance.",
                "rationale": "Unexpected financial requests from an online romantic contact are a significant risk indicator and should be independently verified."
            })
            verification_steps.append(
                "If claims involve business contracts, customs fees, or medical emergencies, contact the official hospital, embassy, or company directly via publicly published contact information--never use contact numbers or links provided in the chat."
            )

        # 2. Urgency & Panic Mitigation
        if features.get("count_urgency", 0) > 0:
            action_items.append({
                "priority": "HIGH",
                "category": "Pacing & Boundary Control",
                "headline": "Institute a Mandatory 24-Hour Cooling-Off Period",
                "action": "Pause all communication for at least 24 hours before making any financial or personal commitments.",
                "rationale": "Artificial urgency is often engineered to bypass critical reflection and provoke impulsive compliance."
            })
            verification_steps.append(
                "Pause and reflect: If this urgent emergency were authentic, what official institutional channels would normally resolve it?"
            )

        # 3. Secrecy & Isolation Countermeasures
        if features.get("count_secrecy", 0) > 0 or features.get("count_isolation", 0) > 0:
            action_items.append({
                "priority": "HIGH",
                "category": "Social Support & Confidant Check",
                "headline": "Break the Secrecy: Consult a Trusted Confidant",
                "action": "Share these conversation transcripts with a trusted friend, family member, or professional counselor.",
                "rationale": "Requests to keep communications confidential can be an isolation tactic designed to avoid independent reality checks."
            })
            verification_steps.append(
                "Describe the situation objectively to someone you trust and invite their candid outside perspective."
            )

        # 4. Platform Migration Advice
        if features.get("count_move_communication", 0) > 0 or features.get("early_platform_switch_flag", 0.0) == 1.0:
            action_items.append({
                "priority": "MEDIUM",
                "category": "Channel Safety",
                "headline": "Maintain Monitored Communication Channels",
                "action": "Avoid moving the conversation to private unmoderated apps (Hangouts, Telegram, WhatsApp, private email).",
                "rationale": "Platform migration removes initial platform reporting mechanisms and enables unmonitored escalation."
            })

        # 5. Sensitive Identity / Credential Requests
        if features.get("count_sensitive_info_request", 0) > 0:
            action_items.append({
                "priority": "HIGH",
                "category": "Identity Security",
                "headline": "Protect Personal Identity Documents",
                "action": "Never provide images of passports, Aadhaar/ID cards, driver's licenses, utility bills, or OTP codes.",
                "rationale": "Shared identity credentials can be exploited for identity theft or unauthorized account access."
            })

        # 6. Coercion / Blackmail Response
        if features.get("count_coercion_threat", 0) > 0:
            action_items.append({
                "priority": "CRITICAL",
                "category": "Immediate Security & Law Enforcement",
                "headline": "Preserve Evidence and Cease Engagement",
                "action": "Take full screenshots/backups of all chats and receipts, stop direct replies immediately, and report the extortion to law enforcement.",
                "rationale": "Preserving unedited message records enables formal cyber investigation by law enforcement."
            })

        # Universal Verification Steps
        verification_steps.insert(
            0,
            "Request a live, real-time video call to verify the contact's physical presence and identity."
        )
        verification_steps.insert(
            1,
            "Perform a reverse image search on profile photos or media shared during the interaction."
        )

        # Determine Primary Headline
        if risk_level == "CRITICAL" or features.get("count_coercion_threat", 0) > 0:
            primary_action = "IMMEDIATE ACTION RECOMMENDED: Discontinue financial transfers, secure personal credentials, and consult cyber authorities."
            priority_level = "CRITICAL"
        elif risk_level == "HIGH" or max_stage >= 4:
            primary_action = "ELEVATED RISK DETECTED: Pause financial discussions, verify identity independently, and consult a trusted confidant."
            priority_level = "HIGH"
        elif risk_level == "MODERATE":
            primary_action = "CAUTION ADVISED: Maintain firm personal boundaries, avoid platform migration, and independently verify claims."
            priority_level = "MEDIUM"
        else:
            primary_action = "STANDARD SAFETY: Maintain regular digital privacy hygiene and situational awareness."
            priority_level = "LOW"
            if not action_items:
                action_items.append({
                    "priority": "LOW",
                    "category": "General Awareness",
                    "headline": "Maintain Healthy Digital Boundaries",
                    "action": "Keep personal and financial information private during introductory stages.",
                    "rationale": "Healthy conversational pacing protects digital and personal safety."
                })

        return {
            "risk_level": risk_level,
            "priority_level": priority_level,
            "primary_action": primary_action,
            "action_items": action_items,
            "verification_steps": verification_steps,
            "support_resources": self.support_resources
        }
