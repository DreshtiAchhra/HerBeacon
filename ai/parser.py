"""
HerBeacon - AI Analysis Engine
Module: ai.parser

Robust, deterministic conversation parsing component.
Converts raw conversation text files into structured message data.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Set


class ConversationParser:
    """
    Parser to convert raw conversation text files into structured message data.
    
    Expected output structure for each message:
    {
        "message_index": int,
        "speaker": str,
        "message": str
    }
    """

    # Extended non-speaker tokens: common short conversational words, responses, or locations
    NON_SPEAKER_WORDS = {
        "hello", "hi", "hey", "yes", "no", "yeah", "yep", "nope", "okay", "ok", 
        "thanks", "thank", "fine", "sure", "why", "what", "how", "good", "well", 
        "really", "lol", "lolol", "amen", "please", "sorry", "and", "but", "so",
        "true", "right", "alright", "morning", "afternoon", "evening", "night",
        "bye", "goodbye", "cool", "wow", "dear", "honey", "darling", "love"
    }

    def __init__(self):
        pass

    def _clean_speaker_name(self, candidate: str) -> str:
        """
        Cleans and normalizes speaker name by stripping trailing punctuation,
        whitespace, or timestamp artifacts.
        """
        cleaned = candidate.strip()
        
        # Remove trailing punctuation like dots, commas, colons, brackets
        cleaned = re.sub(r'[\s.,:;\]\[\(\)]+$', '', cleaned)
        
        # Remove trailing timestamps or date artifacts (e.g. '07:38', 'Yesterday', 'Wed', '14:59')
        cleaned = re.sub(
            r'\s+(?:Yesterday|\d{1,2}:\d{2}|\d+|[A-Za-z]{3}(?:\s+\d{1,2}:\d{2})?)$',
            '',
            cleaned,
            flags=re.IGNORECASE
        )
        
        return cleaned.strip()

    def _discover_primary_speakers(self, lines: List[str]) -> Set[str]:
        """
        Scans the conversation to identify the primary recurring speaker identifiers
        before line-by-line parsing to avoid misclassifying one-word messages as new speakers.
        """
        candidate_counts: Dict[str, int] = {}
        
        for line in lines:
            raw = line.strip()
            if not raw:
                continue
            
            # Speaker lines are standalone tokens (<= 25 chars, alphanumeric/underscore/dash)
            m = re.match(r'^([A-Za-z0-9_-]+)(?:[\s.,:;\]\[\(\)]+(?:Yesterday|\d{1,2}:\d{2}|\d+|[A-Za-z]{3})*[\s.,:;]*|[.,:;])?$', raw)
            if m:
                cand = self._clean_speaker_name(m.group(1))
                if cand and cand.lower() not in self.NON_SPEAKER_WORDS and len(cand) <= 25 and not cand.isdigit():
                    candidate_counts[cand] = candidate_counts.get(cand, 0) + 1
                    
        # Primary speakers in 1-on-1 conversations appear repeatedly (at least 2+ times, or as the initial line)
        primary_speakers = set()
        for cand, count in candidate_counts.items():
            if count >= 2:
                primary_speakers.add(cand)

        # Ensure the very first non-empty line candidate is included if valid
        for line in lines:
            raw = line.strip()
            if raw:
                m = re.match(r'^([A-Za-z0-9_-]+)', raw)
                if m:
                    cand = self._clean_speaker_name(m.group(1))
                    if cand and cand.lower() not in self.NON_SPEAKER_WORDS and len(cand) <= 25 and not cand.isdigit():
                        primary_speakers.add(cand)
                break

        return primary_speakers

    def _is_speaker_line(self, line: str, known_speakers: Set[str], allow_new_candidates: bool = True) -> tuple[bool, Optional[str]]:
        """
        Determines if a given line is a speaker header line.
        
        Returns:
            (is_speaker, cleaned_speaker_name)
        """
        raw_stripped = line.strip()
        if not raw_stripped:
            return False, None

        # 1. Check against established known speakers
        for spk in sorted(known_speakers, key=len, reverse=True):
            if raw_stripped == spk:
                return True, spk
            # Matches speaker followed by trailing noise / timestamps
            pattern = rf'^{re.escape(spk)}(?:[\s.,:;\]\[\(\)]+(?:Yesterday|\d{1,2}:\d{2}|\d+|[A-Za-z]{3})*[\s.,:;]*|[.,:;])$'
            if re.match(pattern, raw_stripped, flags=re.IGNORECASE):
                return True, spk

        # 2. Candidate discovery (only if primary speakers haven't locked or if explicitly valid)
        if allow_new_candidates and len(known_speakers) < 4:
            m = re.match(r'^([A-Za-z0-9_-]+)(?:[\s.,:;\]\[\(\)]+(?:Yesterday|\d{1,2}:\d{2}|\d+|[A-Za-z]{3})*[\s.,:;]*|[.,:;])?$', raw_stripped)
            if m:
                candidate = self._clean_speaker_name(m.group(1))
                if candidate and candidate.lower() not in self.NON_SPEAKER_WORDS and len(candidate) <= 25 and not candidate.isdigit():
                    return True, candidate

        return False, None

    def parse_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parses raw text content of a conversation into a list of structured messages.
        
        Args:
            text: Raw string of the conversation file.
            
        Returns:
            List of dictionaries containing message_index, speaker, and message.
        """
        lines = text.splitlines()
        messages: List[Dict[str, Any]] = []
        
        # Pre-pass: Discover recurring primary speakers to prevent single-word message false-positives
        known_speakers = self._discover_primary_speakers(lines)
        
        current_speaker: Optional[str] = None
        current_message_lines: List[str] = []

        def flush_current_message():
            nonlocal current_speaker, current_message_lines
            if current_speaker is not None and current_message_lines:
                msg_text = "\n".join(current_message_lines).strip()
                if msg_text:
                    messages.append({
                        "message_index": len(messages) + 1,
                        "speaker": current_speaker,
                        "message": msg_text
                    })
                current_message_lines = []

        for line in lines:
            line_str = line.strip()
            
            # Check if this line is a speaker header
            is_spk, spk_name = self._is_speaker_line(line_str, known_speakers, allow_new_candidates=(len(known_speakers) < 2))
            
            if is_spk and spk_name:
                # Flush previous speaker's message before starting a new turn
                flush_current_message()
                current_speaker = spk_name
                known_speakers.add(spk_name)
            else:
                # It is a message line or blank line
                if line_str:
                    if current_speaker is not None:
                        current_message_lines.append(line_str)
                    else:
                        current_speaker = "Unknown"
                        current_message_lines.append(line_str)

        # Flush any remaining message at the end of the file
        flush_current_message()

        return messages

    def parse_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Reads and parses a conversation text file.
        
        Args:
            file_path: Path to the .txt conversation file.
            
        Returns:
            List of structured message dictionaries.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Conversation file not found at: {file_path}")
            
        raw_text = path.read_text(encoding="utf-8", errors="replace")
        return self.parse_text(raw_text)
