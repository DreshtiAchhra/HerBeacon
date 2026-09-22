from pathlib import Path
from collections import Counter

DATASET_PATH = Path("data/LoveFraud02")

files = list(DATASET_PATH.glob("*.txt"))

print("=" * 50)
print("HERBEACON DATASET INSPECTION")
print("=" * 50)

print(f"\nTotal conversation files: {len(files)}")

total_lines = 0
total_characters = 0

conversation_stats = []

for file in files:
    text = file.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    total_lines += len(lines)
    total_characters += len(text)

    conversation_stats.append({
        "file": file.name,
        "lines": len(lines),
        "characters": len(text)
    })

print(f"Total lines: {total_lines}")
print(f"Total characters: {total_characters}")

print("\n" + "-" * 50)
print("CONVERSATION LENGTH")
print("-" * 50)

conversation_stats.sort(key=lambda x: x["lines"])

print("\nShortest conversations:")

for item in conversation_stats[:5]:
    print(f"{item['file']}: {item['lines']} lines")

print("\nLongest conversations:")

for item in conversation_stats[-5:]:
    print(f"{item['file']}: {item['lines']} lines")

print("\n" + "-" * 50)
print("SAMPLE FILES")
print("-" * 50)

for file in files[:3]:
    text = file.read_text(encoding="utf-8", errors="replace")

    print(f"\n### {file.name}")
    print(text[:1000])

print("\n" + "=" * 50)
print("INSPECTION COMPLETED")
print("=" * 50)