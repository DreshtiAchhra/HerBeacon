"""
Test Conversation Parser on real LoveFraud02 data and edge cases.
"""

from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from ai.parser import ConversationParser


def test_parser_edge_cases():
    parser = ConversationParser()

    # 1. Edge Case: Single-word conversational message like "Pamela" or "Okay"
    custom_convo = """
Doc01
Hello Pamela.

PFB
Pamela

Doc01
Nice to meet you.
Doc01
Where are you from?
"""
    messages = parser.parse_text(custom_convo)
    print("Edge Case Single Word Message Test:")
    for m in messages:
        print(f"  Msg {m['message_index']} | {m['speaker']}: {repr(m['message'])}")
    
    assert len(messages) == 4, f"Expected 4 messages, got {len(messages)}"
    assert messages[1]["speaker"] == "PFB" and messages[1]["message"] == "Pamela", "Single-word message 'Pamela' was misclassified!"
    print("[PASS] Single-word message preserved correctly without creating false speakers.")


def test_parser_real_files():
    parser = ConversationParser()
    sample_files = ["AlbertCasey.txt", "AdamAdalet.txt", "BenNewman.txt", "MarvinJordan.txt"]
    
    print("\nTesting Real LoveFraud02 Files:")
    for sf in sample_files:
        fpath = repo_root / "data" / "LoveFraud02" / sf
        if fpath.exists():
            msgs = parser.parse_file(fpath)
            speakers = set(m["speaker"] for m in msgs)
            print(f"  - {sf:<20}: {len(msgs):>4} messages parsed | Speakers: {speakers}")
            assert len(msgs) > 0, f"Failed to parse {sf}"
    print("[PASS] Real files parsed successfully.")


if __name__ == "__main__":
    test_parser_edge_cases()
    test_parser_real_files()
