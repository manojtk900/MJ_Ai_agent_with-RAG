"""
MJ AI Assistant — Training Pipeline Evaluation & Benchmark
Tests the trained intent model against known examples.

Run:
    python evaluate.py
"""
from __future__ import annotations

import json
import time
from pathlib import Path

# ── Benchmark test cases ──────────────────────────────────────────────────────
BENCHMARK = [
    # (input_text, expected_intent)
    ("open youtube",                          "youtube_search"),
    ("search kannada songs on youtube",       "youtube_search"),
    ("youtube lofi music",                    "youtube_search"),
    ("play python tutorial on youtube",       "youtube_search"),
    ("google machine learning",               "google_search"),
    ("search for fastapi tutorial",           "google_search"),
    ("look up artificial intelligence",       "google_search"),
    ("open chrome",                           "open_browser"),
    ("launch browser",                        "open_browser"),
    ("start firefox",                         "open_browser"),
    ("open calculator",                       "open_application"),
    ("launch vs code",                        "open_application"),
    ("open notepad",                          "open_application"),
    ("create a task fix the login bug",       "create_task"),
    ("add task buy groceries",                "create_task"),
    ("remind me to pay electricity bill",     "create_task"),
    ("mark task fix the login bug as done",   "update_task"),
    ("delete task buy groceries",             "delete_task"),
    ("push my code to github",                "github_push"),
    ("git pull origin main",                  "github_pull"),
    ("create a github repo called ml-model",  "github_create_repo"),
    ("check my email",                        "read_email"),
    ("read my inbox",                         "read_email"),
    ("send email to boss@company.com",        "send_email"),
    ("summarize my emails",                   "summarize_email"),
    ("my college is VTU",                     "remember_fact"),
    ("remember that my project is mj-ai",     "remember_fact"),
    ("what is my college",                    "recall_memory"),
    ("who am i",                              "recall_memory"),
    ("upload resume.pdf",                     "upload_file"),
    ("analyze report.pdf",                    "analyze_pdf"),
    ("create a workflow to send daily report", "workflow_create"),
    ("run my daily routine workflow",         "workflow_run"),
    ("hi",                                    "chat"),
    ("hello mj",                              "chat"),
    ("what can you do",                       "chat"),
    ("how are you",                           "chat"),
    # Typos & noise
    ("opn youtube serach kannada songs",      "youtube_search"),
    ("serach for python on goggle",           "google_search"),
    ("hey mj open calclator",                 "open_application"),
]


def run_evaluation(predictor):
    """Run benchmark and print accuracy report."""
    print("\n" + "="*70)
    print(" MJ Intent Model — Benchmark Evaluation")
    print("="*70)

    correct = 0
    wrong = []
    total_latency = 0.0

    for text, expected in BENCHMARK:
        result = predictor.predict(text)
        pred = result["intent"]
        conf = result["confidence"]
        lat = result["latency_ms"]
        total_latency += lat

        ok = pred == expected
        if ok:
            correct += 1
        else:
            wrong.append((text, expected, pred, conf))

        status = "✅" if ok else "❌"
        print(f" {status} [{conf:.0%}] {text:<45} → {pred}")

    accuracy = correct / len(BENCHMARK)
    avg_latency = total_latency / len(BENCHMARK)

    print("\n" + "-"*70)
    print(f" Accuracy:      {accuracy:.1%}  ({correct}/{len(BENCHMARK)})")
    print(f" Avg Latency:   {avg_latency:.1f}ms")

    if wrong:
        print(f"\n Wrong predictions ({len(wrong)}):")
        for text, expected, pred, conf in wrong:
            print(f"   Input    : {text}")
            print(f"   Expected : {expected}")
            print(f"   Got      : {pred}  (conf={conf:.0%})")
            print()

    return accuracy


if __name__ == "__main__":
    try:
        from predictor import MJIntentPredictor
        predictor = MJIntentPredictor()
        accuracy = run_evaluation(predictor)
        if accuracy >= 0.90:
            print(f"\n Model is production-ready! ({accuracy:.1%} accuracy)")
        elif accuracy >= 0.80:
            print(f"\n Good model. Consider more training data ({accuracy:.1%} accuracy)")
        else:
            print(f"\n Needs improvement. Add more data or train longer ({accuracy:.1%} accuracy)")
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("Steps:")
        print("  1. python generate_dataset.py")
        print("  2. python train_intent.py")
        print("  3. python evaluate.py")
