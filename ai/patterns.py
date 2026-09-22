"""
HerBeacon - AI Analysis Engine
Module: ai.patterns

Behavioural Pattern Detection component.
Detects explainable behavioral signals from conversational messages.
"""

import re
from typing import List, Dict, Any, Optional, Set


class BehaviouralPatternDetector:
    """
    Analyzes conversation messages to identify explainable behavioral patterns
    commonly associated with romance and online relationship scams.
    
    USP: "We don't detect suspicious people; we detect suspicious behavioural patterns."
    """

    # Category definitions with keywords, regex rules, severity, and explainability templates
    PATTERN_RULES = {
        "trust_building": {
            "name": "Trust Building",
            "key": "trust_building",
            "severity": "LOW",
            "description": "Attempts to establish unearned rapport, shared values, destiny, or deep integrity.",
            "patterns": [
                r"\b(?:trust\s+me|believe\s+me|honest\s+man|honest\s+woman|honesty\s+is\s+my|god-fearing|god\s+fearing)\b",
                r"\b(?:good\s+heart|pure\s+heart|sincere\s+person|sincerity|never\s+hurt\s+you|never\s+lie\s+to\s+you)\b",
                r"\b(?:destiny|fate\s+brought\s+us|soulmate|god\s+brought\s+us|meant\s+to\s+be|true\s+friendship)\b",
                r"\b(?:open\s+my\s+heart|tell\s+you\s+everything|trust\s+each\s+other|foundation\s+of\s+trust)\b",
                r"\b(?:i\s+am\s+a\s+widower|lost\s+my\s+wife|lost\s+my\s+husband|single\s+father|orphan)\b"
            ]
        },
        "emotional_dependency": {
            "name": "Emotional Dependency & Love Bombing",
            "key": "emotional_dependency",
            "severity": "MEDIUM",
            "description": "Rapid escalation of affection, pet names, emotional dependency, or unrealistic attachment.",
            "patterns": [
                r"\b(?:my\s+darling|my\s+sweetheart|my\s+love|my\s+honey|my\s+queen|my\s+king|my\s+angel|my\s+world|my\s+life)\b",
                r"\b(?:love\s+you\s+so\s+much|falling\s+in\s+love|in\s+love\s+with\s+you|i\s+love\s+you|madly\s+in\s+love)\b",
                r"\b(?:can't\s+live\s+without\s+you|cannot\s+live\s+without\s+you|think\s+about\s+you\s+all\s+day|dreaming\s+of\s+you)\b",
                r"\b(?:marry\s+you|spend\s+my\s+life\s+with\s+you|spend\s+the\s+rest\s+of\s+my\s+life|be\s+my\s+wife|be\s+my\s+husband)\b",
                r"\b(?:special\s+woman|special\s+man|angel\s+sent\s+from\s+god|my\s+heart\s+beats\s+for\s+you)\b"
            ]
        },
        "move_communication": {
            "name": "Pressure to Move Communication",
            "key": "move_communication",
            "severity": "MEDIUM",
            "description": "Attempts to move communication away from monitored or initial platforms to private channels.",
            "patterns": [
                r"\b(?:hangouts|google\s+hangouts|whatsapp|telegram|viber|skype|wechat|signal\s+app)\b",
                r"\b(?:text\s+me\s+on|chat\s+on\s+hangouts|add\s+me\s+on\s+whatsapp|send\s+me\s+an\s+email\s+to)\b",
                r"\b(?:here\s+is\s+my\s+email|my\s+private\s+email|off\s+this\s+site|leave\s+this\s+site|delete\s+my\s+profile)\b",
                r"\b(?:give\s+me\s+your\s+number|what\s+is\s+your\s+phone\s+number|your\s+whatsapp\s+number|your\s+email\s+address)\b"
            ]
        },
        "secrecy": {
            "name": "Secrecy & Concealment",
            "key": "secrecy",
            "severity": "HIGH",
            "description": "Demands or suggestions to keep conversations, agreements, or financial matters confidential.",
            "patterns": [
                r"\b(?:keep\s+this\s+secret|keep\s+it\s+secret|between\s+you\s+and\s+me|between\s+the\s+two\s+of\s+us)\b",
                r"\b(?:don't\s+tell\s+anyone|do\s+not\s+tell\s+anyone|nobody\s+must\s+know|don't\s+tell\s+your\s+family)\b",
                r"\b(?:don't\s+tell\s+your\s+children|don't\s+tell\s+your\s+friends|private\s+matter|strictly\s+confidential)\b",
                r"\b(?:our\s+little\s+secret|keep\s+it\s+to\s+yourself|do\s+not\s+disclose|delete\s+this\s+message)\b"
            ]
        },
        "isolation": {
            "name": "Isolation Tactics",
            "key": "isolation",
            "severity": "HIGH",
            "description": "Attempts to disconnect the individual from their support network, family, or professional advice.",
            "patterns": [
                r"\b(?:they\s+don't\s+understand\s+us|they\s+are\s+jealous|people\s+are\s+jealous|evil\s+eyes)\b",
                r"\b(?:don't\s+listen\s+to\s+them|don't\s+listen\s+to\s+your\s+friends|family\s+will\s+ruin|friends\s+will\s+ruin)\b",
                r"\b(?:only\s+you\s+and\s+i|only\s+you\s+understand\s+me|nobody\s+loves\s+you\s+like\s+i\s+do)\b",
                r"\b(?:they\s+want\s+to\s+separate\s+us|they\s+are\s+against\s+our\s+happiness)\b"
            ]
        },
        "financial_pressure": {
            "name": "Financial Pressure & Solicitations",
            "key": "financial_pressure",
            "severity": "HIGH",
            "description": "Requests for money, financial transfers, gift cards, loan assistance, or monetary commitments.",
            "patterns": [
                r"\b(?:send\s+(?:me\s+)?money|transfer\s+(?:the\s+)?funds|bank\s+transfer|wire\s+transfer)\b",
                r"\b(?:western\s+union|moneygram|gift\s+card|steam\s+card|itunes\s+card|apple\s+card|amazon\s+card|bitcoin|crypto)\b",
                r"\b(?:bank\s+account\s+details|account\s+number|routing\s+number|iban|swift\s+code)\b",
                r"\b(?:customs\s+fee|clearance\s+fee|delivery\s+fee|shipping\s+fee|agent\s+fee|hospital\s+bill|medical\s+bill)\b",
                r"\b(?:emergency\s+money|borrow\s+money|lend\s+me|need\s+a\s+loan|help\s+me\s+pay|pay\s+for\s+my)\b",
                r"\b(?:[\$€£]\s*\d+|\b\d+\s*(?:dollars|euros|pounds|usd|gbp|eur|bucks)\b)"
            ]
        },
        "urgency": {
            "name": "Urgency & Artificial Time Constraints",
            "key": "urgency",
            "severity": "HIGH",
            "description": "Creating artificial time pressure, panic, or rush to prevent thoughtful reflection or verification.",
            "patterns": [
                r"\b(?:urgent|urgently|emergency|asap|as\s+soon\s+as\s+possible|right\s+now|immediately)\b",
                r"\b(?:time\s+is\s+running\s+out|no\s+time\s+to\s+waste|before\s+it\s+is\s+too\s+late|critical\s+situation)\b",
                r"\b(?:hurry\s+up|do\s+it\s+today|today\s+please|within\s+24\s+hours|matter\s+of\s+life\s+and\s+death)\b",
                r"\b(?:can't\s+wait|cannot\s+wait|please\s+rush|quick\s+response)\b"
            ]
        },
        "sensitive_info_request": {
            "name": "Requests for Sensitive Information",
            "key": "sensitive_info_request",
            "severity": "HIGH",
            "description": "Soliciting sensitive identity, credential, residence, or official documentation.",
            "patterns": [
                r"\b(?:send\s+your\s+passport|copy\s+of\s+your\s+passport|id\s+card|driver'?s\s+license|driver\s+license)\b",
                r"\b(?:social\s+security|ssn|credit\s+card|pin\s+number|password|login\s+details|verification\s+code)\b",
                r"\b(?:home\s+address|full\s+name\s+and\s+address|bank\s+statement|utility\s+bill)\b",
                r"\b(?:send\s+me\s+the\s+code|otp|security\s+question)\b"
            ]
        },
        "emotional_manipulation": {
            "name": "Emotional Manipulation & Guilt",
            "key": "emotional_manipulation",
            "severity": "HIGH",
            "description": "Leveraging guilt, questioning loyalty/love, or playing the victim to compel compliance.",
            "patterns": [
                r"\b(?:if\s+you\s+really\s+loved\s+me|if\s+you\s+love\s+me|prove\s+your\s+love|you\s+don't\s+love\s+me)\b",
                r"\b(?:you\s+don't\s+trust\s+me|why\s+don't\s+you\s+trust|how\s+can\s+you\s+doubt\s+me|breaking\s+my\s+heart)\b",
                r"\b(?:i\s+thought\s+you\s+cared|disappointed\s+in\s+you|after\s+all\s+i\s+did|you\s+are\s+breaking\s+my\s+heart)\b",
                r"\b(?:are\s+you\s+saying\s+i'm\s+a\s+liar|do\s+you\s+think\s+i'm\s+a\s+scammer|call\s+me\s+a\s+scammer)\b"
            ]
        },
        "coercion_threat": {
            "name": "Blackmail & Threatening Behaviour",
            "key": "coercion_threat",
            "severity": "CRITICAL",
            "description": "Explicit intimidation, legal threats, reputation blackmail, or retaliatory harassment.",
            "patterns": [
                r"\b(?:you\s+will\s+regret\s+this|i\s+will\s+ruin\s+you|i\s+will\s+destroy\s+you|make\s+you\s+pay)\b",
                r"\b(?:leak\s+your\s+pictures|expose\s+you|post\s+your\s+photos|send\s+to\s+your\s+family|send\s+to\s+your\s+friends)\b",
                r"\b(?:report\s+you\s+to\s+the\s+police|call\s+the\s+fbi|call\s+interpol|sue\s+you|my\s+lawyer)\b",
                r"\b(?:pay\s+me\s+or\s+else|unless\s+you\s+pay|face\s+the\s+consequences)\b"
            ]
        }
    }

    def __init__(self):
        # Compile regular expressions for efficiency
        self._compiled_patterns = {}
        for category, config in self.PATTERN_RULES.items():
            compiled_list = [
                re.compile(p, re.IGNORECASE) for p in config["patterns"]
            ]
            self._compiled_patterns[category] = compiled_list

    def detect_patterns_in_message(
        self,
        message_text: str,
        context_messages: List[Dict[str, Any]] = None,
        speaker: str = "Unknown",
        turn_index: int = 0,
    ) -> List[Dict[str, Any]]:
        """Detect behavioural cues using message text plus local conversation context.

        The regex rules remain the deterministic evidence layer. Context is then
        used to reduce isolated keyword interpretation and to capture repetition,
        chronology, speaker continuity, and cross-pattern relationships.
        Confidence is a rule-based detection confidence, never a scam probability.
        """
        if not message_text or not isinstance(message_text, str):
            return []

        context_messages = context_messages or []
        detected_patterns = []
        message_lower = message_text.lower()

        # Build context from nearby messages only; this keeps detection local and
        # avoids treating unrelated distant conversation as evidence for a cue.
        recent = context_messages[-6:]
        prior_pattern_keys = []
        same_speaker_prior = 0
        for item in recent:
            for prior in item.get("patterns", []):
                key = prior.get("pattern_key")
                if key:
                    prior_pattern_keys.append(key)
            if item.get("speaker") == speaker:
                same_speaker_prior += 1

        for category, compiled_regexes in self._compiled_patterns.items():
            matched_evidence: List[str] = []
            for regex in compiled_regexes:
                matches = regex.findall(message_text)
                for match in matches:
                    if isinstance(match, tuple):
                        match_text = " ".join(part for part in match if part)
                    else:
                        match_text = str(match)
                    if match_text and match_text.strip() not in matched_evidence:
                        matched_evidence.append(match_text.strip())

            if not matched_evidence:
                continue

            config = self.PATTERN_RULES[category]
            cue_count = len(matched_evidence)
            confidence = min(0.95, 0.70 + 0.15 * (cue_count - 1))
            context_reasons = []

            # Repetition: the same category was detected nearby.
            if category in prior_pattern_keys:
                confidence = min(0.98, confidence + 0.03)
                context_reasons.append("similar cue repeated in nearby conversation")

            # Chronology: later-stage cues are more meaningful when an earlier
            # behavioural signal is already present in the local context.
            related_prior = {
                "financial_pressure": {"emotional_dependency", "move_communication", "secrecy", "isolation"},
                "urgency": {"financial_pressure", "emotional_manipulation"},
                "coercion_threat": {"financial_pressure", "urgency", "emotional_manipulation"},
                "secrecy": {"emotional_dependency", "move_communication"},
                "isolation": {"emotional_dependency", "secrecy"},
                "sensitive_info_request": {"move_communication", "trust_building", "emotional_dependency"},
                "emotional_manipulation": {"emotional_dependency", "financial_pressure"},
            }
            if related_prior.get(category, set()).intersection(prior_pattern_keys):
                confidence = min(0.98, confidence + 0.03)
                context_reasons.append("related behavioural signal appeared earlier")

            if same_speaker_prior >= 2:
                context_reasons.append("pattern occurred within the same speaker's recent turns")

            explanation = config["description"]
            if context_reasons:
                explanation += " Context: " + "; ".join(context_reasons) + "."
            explanation += " Evidence: " + ", ".join(repr(e) for e in matched_evidence) + "."

            detected_patterns.append({
                "pattern_name": config["name"],
                "pattern_key": config["key"],
                "severity": config["severity"],
                "detection_confidence": round(confidence, 2),
                "evidence": matched_evidence,
                "explanation": explanation,
                "contextual": bool(context_reasons),
                "turn_index": turn_index,
                "speaker": speaker,
            })

        return detected_patterns

    def analyze_conversation(self, parsed_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns chronologically so nearby context can inform each turn."""
        analyzed_messages = []
        for msg in parsed_messages:
            msg_copy = dict(msg)
            detected = self.detect_patterns_in_message(
                msg.get("message", ""),
                context_messages=analyzed_messages,
                speaker=msg.get("speaker", "Unknown"),
                turn_index=msg.get("message_index", len(analyzed_messages) + 1),
            )
            msg_copy["patterns"] = detected
            analyzed_messages.append(msg_copy)
        return analyzed_messages

    def get_pattern_summary(self, analyzed_messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates pattern occurrences across all speakers and across the conversation.
        
        Returns:
            Summary dictionary with total occurrences, per-pattern counts, and per-speaker breakdowns.
        """
        total_pattern_occurrences = 0
        pattern_counts: Dict[str, int] = {}
        speaker_patterns: Dict[str, Dict[str, int]] = {}

        for msg in analyzed_messages:
            speaker = msg.get("speaker", "Unknown")
            if speaker not in speaker_patterns:
                speaker_patterns[speaker] = {}

            for p in msg.get("patterns", []):
                pkey = p["pattern_key"]
                total_pattern_occurrences += 1
                pattern_counts[pkey] = pattern_counts.get(pkey, 0) + 1
                speaker_patterns[speaker][pkey] = speaker_patterns[speaker].get(pkey, 0) + 1

        return {
            "total_messages": len(analyzed_messages),
            "total_pattern_occurrences": total_pattern_occurrences,
            "pattern_counts": pattern_counts,
            "speaker_breakdown": speaker_patterns
        }
