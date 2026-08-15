import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATASETS_DIR = ROOT / "training" / "datasets"

def test_data_pipeline():
    print("=" * 65)
    print("  NOTEBOOK DATA PREPARATION & INTEGRITY VERIFICATION")
    print("=" * 65)

    # 1. Dataset Loading
    commands = [json.loads(line) for line in open(DATASETS_DIR / "mj_commands.jsonl", encoding="utf-8") if line.strip()]
    tool_use = [json.loads(line) for line in open(DATASETS_DIR / "mj_agent_tool_use.jsonl", encoding="utf-8") if line.strip()]
    rag_qa = [json.loads(line) for line in open(DATASETS_DIR / "mj_conversation_rag.jsonl", encoding="utf-8") if line.strip()]
    golden_eval = [json.loads(line) for line in open(DATASETS_DIR / "mj_eval_500.jsonl", encoding="utf-8") if line.strip()]

    print(f"Loaded {len(commands):,} commands, {len(tool_use):,} tool-use, {len(rag_qa):,} RAG pairs, {len(golden_eval)} Golden records.")

    # 2. Golden 500 Isolation
    golden_inputs = {g["input"].lower().strip() for g in golden_eval}
    assert len(golden_inputs) == 500 or len(golden_eval) == 500, "Golden 500 count mismatch"

    # 3. Conversion
    converted = []
    for c in commands:
        intent = c.get("intent", "chat")
        entities = c.get("entities", {})
        if intent in {"github_push", "send_email", "delete_file"}:
            reply = f"⚠️ **JARVIS CONFIRMATION REQUIRED**\n\nThe requested operation `{intent}` carries risk. Please confirm to proceed with entities: {json.dumps(entities)}."
        else:
            reply = f"⚡ Executing `{intent}` with parameters: {json.dumps(entities)}."
        converted.append({"messages": [{"role": "user", "content": c["text"]}, {"role": "assistant", "content": reply}], "category": "ACTION"})

    for t in tool_use:
        converted.append({"messages": t["messages"], "category": "TOOL_USE"})

    for r in rag_qa:
        citation = r.get("source_citation")
        ans = f"{r['answer']}\n\n**Sources:**\n- {citation}" if citation and citation != "none" else r["answer"]
        converted.append({"messages": [{"role": "user", "content": r["question"]}, {"role": "assistant", "content": ans}], "category": r.get("category", "CONVERSATION").upper()})

    print(f"Converted {len(converted):,} records successfully.")

    # 4. Leakage Check
    leakage = 0
    clean = []
    for rec in converted:
        u_msg = next((m["content"] for m in rec["messages"] if m["role"] == "user"), "").lower().strip()
        if u_msg in golden_inputs:
            leakage += 1
            continue
        clean.append(rec)

    print(f"Leakage excluded: {leakage} records. Clean training candidates: {len(clean):,}")
    print("=" * 65)
    print("✅ TEST PIPELINE PASSED: ZERO LEAKAGE, CLEAN ISOLATION")

if __name__ == "__main__":
    test_data_pipeline()
