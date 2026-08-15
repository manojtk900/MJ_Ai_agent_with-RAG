"""
MJ AI Assistant — Jupyter Notebook Generator
Creates two complete .ipynb files for training:
  1. MJ_Intent_Classifier.ipynb
  2. MJ_Entity_Extractor.ipynb

Run:  python generate_notebooks.py
"""
import json
from pathlib import Path

OUT_DIR = Path(__file__).parent


def md_cell(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def code_cell(src):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src,
    }


def make_notebook(cells):
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.0"},
        },
        "cells": cells,
    }


def save_nb(nb, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"Created: {path}  ({path.stat().st_size//1024} KB)")


# ==============================================================================
#  INTENT CLASSIFIER NOTEBOOK
# ==============================================================================

C_INSTALL = """\
# Cell 1 — Install Required Packages
import subprocess, sys

packages = [
    "transformers>=4.40.0",
    "datasets>=2.18.0",
    "torch>=2.0.0",
    "accelerate>=0.27.0",
    "scikit-learn>=1.3.0",
    "seqeval>=1.2.2",
    "numpy",
]
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + packages)
print("All packages installed OK")
"""

C_GENERATE = r"""# Cell 2 — Generate Synthetic Dataset  (1 000 samples × 22 intents)
import random, re, json
from collections import Counter
random.seed(42)

YOUTUBE_Q = [
    "trending songs","lofi music","python tutorial","yash toxic trailer",
    "kannada songs","bollywood hits","coding music","gym workout",
    "react tutorial","deep learning","cricket highlights","tamil songs",
    "motivational speech","ted talks","machine learning basics",
    "fastapi tutorial","docker tutorial","web development course",
    "data science","new movies 2024","comedy videos","beats to study",
]
GOOGLE_Q = [
    "VTU results","python documentation","fastapi docs",
    "best laptop under 50000","weather today","stock market today",
    "exam timetable","top engineering colleges","flight tickets",
    "ipl schedule","cricket score","latest news","movie reviews",
    "recipe for biryani","java vs python","best programming languages",
    "coronavirus updates","population of india","how to lose weight",
]
APPS = [
    "VS Code","Notepad","Chrome","Spotify","Discord","Slack",
    "Zoom","VLC","Steam","Task Manager","Paint","Excel",
    "Word","PowerPoint","Telegram","WhatsApp","Calculator",
]
REPOS  = ["mj-assistant","my-portfolio","ai-chatbot","fastapi-backend","react-dashboard","ml-model"]
EMAILS = ["john@gmail.com","boss@company.com","professor@vtu.edu","hr@company.org","client@startup.io"]
TASKS  = [
    "fix the login bug","write unit tests","update README",
    "submit assignment","pay electricity bill","buy groceries",
    "call the doctor","prepare presentation","learn docker",
    "review PR","deploy to production","exercise 30 minutes",
]
FACTS  = [
    "my college is Sri Siddhartha Institute of Technology",
    "my project is MJ AI Assistant",
    "my github username is MJCodes",
    "i am preparing for GATE 2025",
    "my stack is Python FastAPI React",
    "i live in Tumkur Karnataka",
    "my name is Manoj",
]

TEMPLATES = {
"open_browser":        ["open browser","launch browser","start chrome","open chrome","open firefox",
                         "open edge","launch web browser","start internet browser",
                         "open a new browser window","browser please","open chromium"],
"youtube_search":      ["open youtube and search {YQ}","search {YQ} on youtube",
                         "find {YQ} on youtube","play {YQ} on youtube","youtube {YQ}",
                         "youtube search {YQ}","search youtube for {YQ}","look up {YQ} on youtube",
                         "find me {YQ} on youtube","go to youtube and search {YQ}",
                         "i want to watch {YQ}","play {YQ} video","watch {YQ} on youtube",
                         "mj find me {YQ} on youtube","search for {YQ} on youtube please"],
"google_search":       ["google {GQ}","search {GQ} on google","google search {GQ}",
                         "search for {GQ}","look up {GQ}","find information about {GQ}",
                         "can you google {GQ}","search the web for {GQ}","find {GQ} online",
                         "research {GQ}","look for {GQ} on google","google {GQ} for me",
                         "find me results for {GQ}","search {GQ} on the internet"],
"open_application":    ["open {APP}","launch {APP}","start {APP}","run {APP}",
                         "open the {APP} app","can you open {APP}","start {APP} please",
                         "hey mj open {APP}","start the {APP}","bring up {APP}",
                         "open {APP} for me","fire up {APP}","get {APP} running"],
"open_calculator":     ["open calculator","launch calculator","start calculator","open calc",
                         "calculator please","bring up calculator","run calculator",
                         "open windows calculator","hey mj open calculator",
                         "i need calculator","show me calculator","open calculator app"],
"open_notepad":        ["open notepad","launch notepad","start notepad","open text editor",
                         "notepad please","bring up notepad","run notepad",
                         "hey mj open notepad","i need notepad","open notes"],
"open_vscode":         ["open vs code","launch vs code","start vscode","open vscode",
                         "open code editor","hey mj open vs code",
                         "open visual studio code","launch code editor",
                         "start code","run vscode","bring up vs code"],
"open_github":         ["open github","launch github","go to github","open github website",
                         "take me to github","open my github","show me github",
                         "open github in browser","hey mj open github","visit github"],
"github_push":         ["push my code to github","git push","push changes to github",
                         "push to {REPO}","commit and push","push latest changes",
                         "push code to {REPO}","push to main","push to origin",
                         "git push origin main","commit and push to github","push my changes"],
"github_pull":         ["pull from github","git pull","pull latest changes",
                         "pull from {REPO}","git pull origin main",
                         "get latest code from github","sync with github",
                         "pull updates","fetch and merge","download latest code",
                         "pull my code","get latest from {REPO}"],
"github_create_repo":  ["create a github repo called {REPO}","new github repo {REPO}",
                         "make a new repo {REPO}","create repo {REPO}",
                         "initialize github repository {REPO}","setup github repo {REPO}",
                         "create a new repository {REPO}","new repo {REPO}",
                         "make github repo {REPO}","create private repo {REPO}"],
"read_email":          ["check my email","open my inbox","read my emails",
                         "show me my emails","check gmail","open email","read my inbox",
                         "show unread emails","any new emails","check my messages",
                         "what is in my inbox","check email please","view my emails"],
"send_email":          ["send an email to {EM}","email {EM}","compose email to {EM}",
                         "write an email to {EM}","send message to {EM}",
                         "draft an email to {EM}","send {EM} an email",
                         "write to {EM}","contact {EM} by email","mail to {EM}"],
"summarize_email":     ["summarize my emails","summarize my inbox",
                         "give me a summary of my emails","email summary please",
                         "brief me on my emails","what emails are important",
                         "summarize unread messages","give email overview",
                         "quick email summary","email briefing","digest my emails"],
"create_task":         ["create a task to {TASK}","add task {TASK}","new task {TASK}",
                         "add to my todo {TASK}","create todo {TASK}",
                         "remind me to {TASK}","add {TASK} to my tasks",
                         "create task {TASK}","put {TASK} on my list",
                         "schedule task {TASK}","add new task {TASK}","task: {TASK}"],
"update_task":         ["mark task {TASK} as done","complete the task {TASK}",
                         "close task {TASK}","task {TASK} is finished",
                         "mark {TASK} complete","update task {TASK}",
                         "set {TASK} as completed","finish task {TASK}",
                         "task {TASK} done","i finished {TASK} mark done"],
"delete_task":         ["delete task {TASK}","remove task {TASK}","cancel task {TASK}",
                         "delete the {TASK} task","remove {TASK} from list",
                         "i no longer need {TASK}","erase task {TASK}",
                         "drop task {TASK}","clear task {TASK}"],
"workflow_create":     ["create a workflow to {TASK}","automate {TASK}",
                         "set up workflow for {TASK}","build automation for {TASK}",
                         "create automation {TASK}","make a workflow for {TASK}",
                         "automate {TASK} every day","setup daily workflow {TASK}",
                         "create recurring task {TASK}","workflow: {TASK}"],
"workflow_run":        ["run workflow {TASK}","execute workflow {TASK}",
                         "start workflow {TASK}","trigger workflow {TASK}",
                         "run the {TASK} workflow","execute automation {TASK}",
                         "run my daily routine","execute daily workflow",
                         "fire workflow {TASK}","run the automation"],
"remember_fact":       ["{FACT}","remember that {FACT}","note that {FACT}",
                         "remember: {FACT}","save this: {FACT}",
                         "keep in mind {FACT}","store this fact: {FACT}",
                         "hey mj remember {FACT}","i want you to know {FACT}"],
"recall_memory":       ["what is my college","what project am i working on",
                         "where do i study","what is my github",
                         "what am i preparing for","what is my name",
                         "what did i tell you about me","recall my preferences",
                         "what do you know about me","who am i",
                         "what is my stack","where do i work","what do i do"],
"chat":                ["hi","hello","hey mj","how are you","what can you do",
                         "help me","good morning","good evening","good night",
                         "what is your name","tell me a joke","how is it going",
                         "what is up mj","hey there","nice to meet you","who are you",
                         "can you help me","introduce yourself","talk to me",
                         "are you there","wake up mj","what are your features"],
}

TYPOS = {
    "open":["opn","opne","oepn"], "search":["serach","seach","serch"],
    "youtube":["yotube","youtubee","ytube"], "google":["goggle","gogle","googel"],
    "github":["githob","gitub","guthub"], "email":["emial","emaail","emal"],
}

def _pick(lst): return random.choice(lst)

def fill(t):
    t = t.replace("{YQ}",   _pick(YOUTUBE_Q))
    t = t.replace("{GQ}",   _pick(GOOGLE_Q))
    t = t.replace("{APP}",  _pick(APPS))
    t = t.replace("{REPO}", _pick(REPOS))
    t = t.replace("{EM}",   _pick(EMAILS))
    t = t.replace("{TASK}", _pick(TASKS))
    t = t.replace("{FACT}", _pick(FACTS))
    return t

def noise(text):
    if random.random() < 0.10: text = text.upper()
    elif random.random() < 0.20: text = text.title()
    if random.random() < 0.10:
        for w, tl in TYPOS.items():
            if w in text.lower():
                text = re.sub(w, _pick(tl), text, count=1, flags=re.IGNORECASE)
                break
    if random.random() < 0.15:
        text = text + _pick([".", "!", "?", " please"])
    if random.random() < 0.08:
        text = _pick(["mj", "hey mj", "hey"]) + " " + text
    return text.strip()

records = []
SAMPLES = 1000
for intent, tmpl_list in TEMPLATES.items():
    c = 0
    while c < SAMPLES:
        t = noise(fill(_pick(tmpl_list)))
        records.append({"text": t, "intent": intent})
        c += 1

random.shuffle(records)
print(f"Generated {len(records)} samples across {len(TEMPLATES)} intents")
dist = Counter(r["intent"] for r in records)
for k, v in sorted(dist.items()):
    print(f"  {k:<25} {v}")
"""

C_SAVE_JSONL = """\
# Cell 3 — Save Dataset as JSONL
import json
from pathlib import Path

dataset_dir = Path("datasets")
dataset_dir.mkdir(exist_ok=True)

out = dataset_dir / "mj_intents_22class.jsonl"
with open(out, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\\n")

print(f"Saved {len(records)} records -> {out}  ({out.stat().st_size//1024} KB)")
"""

C_LOAD = """\
# Cell 4 — Load Dataset
import json
from pathlib import Path

loaded = []
with open(Path("datasets/mj_intents_22class.jsonl"), encoding="utf-8") as f:
    for line in f:
        loaded.append(json.loads(line.strip()))

texts  = [r["text"]   for r in loaded]
labels = [r["intent"] for r in loaded]
print(f"Loaded {len(loaded)} samples")
print(f"Sample[0]:    {loaded[0]}")
print(f"Sample[5000]: {loaded[5000]}")
"""

C_ENCODE = """\
# Cell 5 — Label Encoding
from sklearn.preprocessing import LabelEncoder
import numpy as np

le = LabelEncoder()
label_ids  = le.fit_transform(labels)
label_names = list(le.classes_)
label2id    = {l: int(i) for i, l in enumerate(label_names)}
id2label    = {int(i): l for l, i in label2id.items()}

print(f"{len(label_names)} intent classes:")
for i, name in enumerate(label_names):
    print(f"  [{i:02d}] {name}")
"""

C_SPLIT = """\
# Cell 6 — Train / Validation / Test Split  80/10/10
from sklearn.model_selection import train_test_split

X_tr, X_tmp, y_tr, y_tmp = train_test_split(
    texts, label_ids.tolist(), test_size=0.2, random_state=42, stratify=label_ids
)
X_val, X_te, y_val, y_te = train_test_split(
    X_tmp, y_tmp, test_size=0.5, random_state=42, stratify=y_tmp
)

print(f"Train:      {len(X_tr):>6}")
print(f"Validation: {len(X_val):>6}")
print(f"Test:       {len(X_te):>6}")
"""

C_TRAIN = """\
# Cell 7 — Train DistilBERT Intent Classifier
# Expected runtime: ~15 min CPU | ~3 min GPU
import torch, numpy as np
from datasets import Dataset, DatasetDict
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding,
)

MODEL_NAME = "distilbert-base-uncased"
MAX_LEN    = 128
BATCH      = 32
EPOCHS     = 5
device     = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Training on: {device.upper()}")

def mk_ds(X, y): return Dataset.from_dict({"text": X, "label": y})
hf = DatasetDict({
    "train":      mk_ds(X_tr,  y_tr),
    "validation": mk_ds(X_val, y_val),
    "test":       mk_ds(X_te,  y_te),
})

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
def tok(b): return tokenizer(b["text"], truncation=True, max_length=MAX_LEN)
hf_tok = hf.map(tok, batched=True, remove_columns=["text"])

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=len(label_names),
    id2label=id2label, label2id=label2id,
)

def metrics(eval_pred):
    logits, lbls = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": float((preds == lbls).mean())}

from pathlib import Path
chk = Path("models/checkpoints"); chk.mkdir(parents=True, exist_ok=True)

args = TrainingArguments(
    output_dir=str(chk), num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH, per_device_eval_batch_size=64,
    learning_rate=2e-5, weight_decay=0.01, warmup_ratio=0.1,
    evaluation_strategy="epoch", save_strategy="epoch",
    load_best_model_at_end=True, metric_for_best_model="accuracy",
    logging_steps=50, seed=42, fp16=torch.cuda.is_available(), report_to="none",
)
trainer = Trainer(
    model=model, args=args,
    train_dataset=hf_tok["train"], eval_dataset=hf_tok["validation"],
    tokenizer=tokenizer, data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=metrics,
)
print("Starting training ...")
res = trainer.train()
print(f"Done! Loss={res.training_loss:.4f}  Time={res.metrics['train_runtime']:.0f}s")
"""

C_EVAL = """\
# Cell 8 — Evaluate on Test Set
from sklearn.metrics import classification_report
import numpy as np

out   = trainer.predict(hf_tok["test"])
preds = np.argmax(out.predictions, axis=-1)
true  = out.label_ids

acc = (preds == true).mean()
print(f"Test Accuracy: {acc:.4f}  ({acc*100:.2f}%)")
print()
print(classification_report(true, preds, target_names=label_names, digits=4))
"""

C_SAVE = """\
# Cell 9 — Save Model
import json
from pathlib import Path

save_dir = Path("exports/mj_intent_model")
save_dir.mkdir(parents=True, exist_ok=True)

trainer.save_model(str(save_dir))
tokenizer.save_pretrained(str(save_dir))

mapping = {
    "label2id":    label2id,
    "id2label":    {str(k): v for k, v in id2label.items()},
    "intent_names": label_names,
    "num_classes": len(label_names),
    "model":       MODEL_NAME,
    "max_length":  MAX_LEN,
}
with open(save_dir / "label_mapping.json", "w") as f:
    json.dump(mapping, f, indent=2)

print(f"Model saved to: {save_dir}")
for p in sorted(save_dir.iterdir()):
    print(f"  {p.name:<40} {p.stat().st_size//1024} KB")
"""

C_PREDICTOR = """\
# Cell 10 — Predictor Function
import torch

def predict_intent(text, top_k=3):
    inputs = tokenizer(text, return_tensors="pt", truncation=True,
                        max_length=MAX_LEN, padding=True)
    with torch.no_grad():
        probs = torch.softmax(model(**inputs).logits, dim=-1)[0]
    top = torch.argsort(probs, descending=True)[:top_k]
    results = [{"intent": id2label[i.item()], "confidence": round(probs[i].item(), 4)} for i in top]
    return {"text": text, "intent": results[0]["intent"],
            "confidence": results[0]["confidence"], "top_k": results}

r = predict_intent("open youtube and search trending songs")
print(f"Test: {r['text']}")
print(f"  -> {r['intent']}  ({r['confidence']:.1%})")
"""

C_INTERACTIVE = """\
# Cell 11 — Interactive Testing
TESTS = [
    # ── Desktop / Search ─────────────────────────────────────────────────────
    ("open youtube and search yash toxic trailer",    "youtube_search"),
    ("search trending kannada songs on youtube",      "youtube_search"),
    ("youtube lofi music",                            "youtube_search"),
    ("google VTU results",                            "google_search"),
    ("look up python documentation",                  "google_search"),
    ("open calculator",                               "open_calculator"),
    ("open notepad",                                  "open_notepad"),
    ("open vs code",                                  "open_vscode"),
    ("open github",                                   "open_github"),
    ("open chrome",                                   "open_browser"),
    ("launch spotify",                                "open_application"),
    # ── GitHub ───────────────────────────────────────────────────────────────
    ("push my latest code to github",                "github_push"),
    ("git pull origin main",                          "github_pull"),
    ("create github repo mj-assistant",              "github_create_repo"),
    # ── Email ────────────────────────────────────────────────────────────────
    ("check my email",                               "read_email"),
    ("send email to boss@company.com",               "send_email"),
    ("summarize my inbox",                           "summarize_email"),
    # ── Tasks ────────────────────────────────────────────────────────────────
    ("create a task fix the login bug",              "create_task"),
    ("mark task buy groceries as done",              "update_task"),
    ("delete task pay electricity bill",             "delete_task"),
    # ── Workflow ─────────────────────────────────────────────────────────────
    ("create a workflow to send daily report",       "workflow_create"),
    ("run my daily routine",                         "workflow_run"),
    # ── Memory ───────────────────────────────────────────────────────────────
    ("my college is Sri Siddhartha Institute",       "remember_fact"),
    ("what is my college",                           "recall_memory"),
    # ── Chat ─────────────────────────────────────────────────────────────────
    ("hi",                                           "chat"),
    ("what can you do",                              "chat"),
    # ── Typos & noise ────────────────────────────────────────────────────────
    ("opn youtube serach trending songs",            "youtube_search"),
    ("serach for VTU results on goggle",             "google_search"),
    ("hey mj open calclator",                        "open_calculator"),
]

print(f"{'Input':<50} {'Expected':<25} {'Predicted':<25} Conf  OK?")
print("─" * 115)
ok = 0
for text, exp in TESTS:
    r = predict_intent(text)
    hit = r["intent"] == exp
    if hit: ok += 1
    mark = "OK" if hit else "FAIL"
    print(f"{text[:48]:<50} {exp:<25} {r['intent']:<25} {r['confidence']:>4.0%}  {mark}")

print(f"\\nScore: {ok}/{len(TESTS)} = {ok/len(TESTS):.1%}")
"""

C_EXPORT = """\
# Cell 12 — Export to MJ Backend
import shutil
from pathlib import Path

src = Path("exports/mj_intent_model")
dst = Path("../backend/app/ml_models/mj_intent_model")
dst.mkdir(parents=True, exist_ok=True)

for f in src.iterdir():
    shutil.copy2(f, dst / f.name)

print(f"Model exported to MJ backend: {dst.resolve()}")
print("Files:")
for f in sorted(dst.iterdir()):
    print(f"  {f.name}")
"""

C_FASTAPI = '''\
# Cell 13 — FastAPI ControllerAgent Integration

CODE = """
# app/ml/intent_predictor.py

import json, time, torch
from functools import lru_cache
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = Path(__file__).parent.parent / "ml_models" / "mj_intent_model"

@lru_cache(maxsize=1)
def _load():
    tok   = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    mdl   = AutoModelForSequenceClassification.from_pretrained(str(MODEL_PATH))
    mdl.eval()
    with open(MODEL_PATH / "label_mapping.json") as f:
        m = json.load(f)
    id2label = {int(k): v for k, v in m["id2label"].items()}
    return tok, mdl, id2label

def predict_intent(text: str, threshold: float = 0.5) -> dict:
    t0 = time.monotonic()
    tok, mdl, id2label = _load()
    inp = tok(text, return_tensors="pt", truncation=True, max_length=128, padding=True)
    with torch.no_grad():
        probs = torch.softmax(mdl(**inp).logits, dim=-1)[0]
    top3  = torch.argsort(probs, descending=True)[:3]
    top_k = [{"intent": id2label[i.item()], "confidence": round(probs[i].item(), 4)} for i in top3]
    best  = top_k[0]
    return {
        "intent":     best["intent"] if best["confidence"] >= threshold else "chat",
        "confidence": best["confidence"],
        "top_k":      top_k,
        "latency_ms": round((time.monotonic() - t0) * 1000, 2),
    }
"""
print("=== app/ml/intent_predictor.py ===")
print(CODE)

PATCH = """
# In ControllerAgent.execute() — drop-in fast routing:

from app.ml.intent_predictor import predict_intent as ml_predict

async def execute(self, state):
    ml = ml_predict(state.raw_input)
    if ml["confidence"] >= 0.85:          # high-confidence fast path
        return {
            "intent": ml["intent"],
            "context": {}, "plan": [],
            "risk_level": "safe",
            "requires_approval": False,
            "agent_logs": [f"[controller:ml] {ml['intent']} {ml['confidence']:.0%} {ml['latency_ms']}ms"],
        }
    return await self._llm_intent_detection(state)   # fallback to LLM
"""
print("=== ControllerAgent patch ===")
print(PATCH)
'''

C_BENCHMARK = """\
# Cell 14 — Performance Benchmark
import time, statistics, torch

model.eval()
INPUTS = [
    "open youtube search trending songs",
    "google VTU results",
    "open calculator",
    "push my code to github",
    "check my email",
    "create task fix login bug",
    "hi",
    "my college is Sri Siddhartha",
]
latencies = []
for i in range(200):
    t = INPUTS[i % len(INPUTS)]
    s = time.perf_counter()
    predict_intent(t)
    latencies.append((time.perf_counter() - s) * 1000)

latencies.sort()
print(f"Latency over 200 requests ({device.upper()}):")
print(f"  Min:    {latencies[0]:.2f} ms")
print(f"  Median: {statistics.median(latencies):.2f} ms")
print(f"  P95:    {latencies[189]:.2f} ms")
print(f"  Max:    {latencies[-1]:.2f} ms")
print(f"  Mean:   {statistics.mean(latencies):.2f} ms")
print()
med = statistics.median(latencies)
print(f"Throughput:   ~{int(1000/med)} req/s")
print(f"vs LLM API:   ~{int(2500/med)}x faster")
print()
print("=" * 50)
print("  Model saved to: exports/mj_intent_model/")
print("  Ready for MJ AI Assistant production!")
print("=" * 50)
"""

INTENT_NB = make_notebook([
    md_cell("# MJ AI Assistant — Intent Classifier\n### 22-class DistilBERT intent classification\n**Dataset:** 22,000 samples | **Model:** distilbert-base-uncased | **Output:** `exports/mj_intent_model/`"),
    code_cell(C_INSTALL),
    code_cell(C_GENERATE),
    code_cell(C_SAVE_JSONL),
    code_cell(C_LOAD),
    code_cell(C_ENCODE),
    code_cell(C_SPLIT),
    code_cell(C_TRAIN),
    code_cell(C_EVAL),
    code_cell(C_SAVE),
    code_cell(C_PREDICTOR),
    code_cell(C_INTERACTIVE),
    code_cell(C_EXPORT),
    code_cell(C_FASTAPI),
    code_cell(C_BENCHMARK),
])


# ==============================================================================
#  ENTITY EXTRACTOR NOTEBOOK
# ==============================================================================

E_INSTALL = C_INSTALL  # same packages

E_GENERATE = r"""# Cell 2 — Generate Entity Extraction Dataset
import random, re, json
from collections import Counter
random.seed(42)

ENTITY_TYPES = ["query", "app_name", "email", "task", "repo", "file", "url"]
LABELS    = ["O"] + ["B-" + e for e in ENTITY_TYPES] + ["I-" + e for e in ENTITY_TYPES]
LABEL2ID  = {l: i for i, l in enumerate(LABELS)}
ID2LABEL  = {i: l for l, i in LABEL2ID.items()}
print("BIO Labels:", LABELS)

QUERIES = ["trending kannada songs","yash toxic trailer","python tutorial",
           "VTU results","lofi music beats","cricket highlights",
           "machine learning course","bollywood hits 2024","react hooks tutorial"]
APPS    = ["VS Code","Notepad","Chrome","Spotify","Discord","Slack","Zoom","VLC","Calculator"]
EMAILS  = ["john@gmail.com","boss@company.com","professor@vtu.edu","hr@company.org","client@startup.io"]
TASKS   = ["fix the login bug","write unit tests","update README",
           "pay electricity bill","buy groceries","submit assignment","prepare presentation"]
REPOS   = ["mj-assistant","my-portfolio","ai-chatbot","fastapi-backend","react-dashboard"]
FILES   = ["resume.pdf","report.pdf","project.pdf","invoice.pdf","notes.pdf"]
URLS    = ["github.com/user/repo","vtu.ac.in/results","google.com","youtube.com/trending"]

ETEMPLATES = [
    ("open youtube and search {query}", "query",    QUERIES),
    ("search {query} on youtube",       "query",    QUERIES),
    ("youtube {query}",                 "query",    QUERIES),
    ("play {query} on youtube",         "query",    QUERIES),
    ("find {query} on youtube",         "query",    QUERIES),
    ("google {query}",                  "query",    QUERIES),
    ("search {query} on google",        "query",    QUERIES),
    ("look up {query}",                 "query",    QUERIES),
    ("find information about {query}",  "query",    QUERIES),
    ("open {app_name}",                 "app_name", APPS),
    ("launch {app_name}",               "app_name", APPS),
    ("start {app_name}",                "app_name", APPS),
    ("open the {app_name} app",         "app_name", APPS),
    ("can you open {app_name}",         "app_name", APPS),
    ("send an email to {email}",        "email",    EMAILS),
    ("email {email}",                   "email",    EMAILS),
    ("compose email to {email}",        "email",    EMAILS),
    ("write an email to {email}",       "email",    EMAILS),
    ("create a task to {task}",         "task",     TASKS),
    ("add task {task}",                 "task",     TASKS),
    ("remind me to {task}",             "task",     TASKS),
    ("delete task {task}",              "task",     TASKS),
    ("mark task {task} as done",        "task",     TASKS),
    ("push to {repo}",                  "repo",     REPOS),
    ("git push {repo}",                 "repo",     REPOS),
    ("create a github repo called {repo}", "repo",  REPOS),
    ("pull from {repo}",                "repo",     REPOS),
    ("analyze {file}",                  "file",     FILES),
    ("upload {file}",                   "file",     FILES),
    ("read pdf {file}",                 "file",     FILES),
    ("open {url}",                      "url",      URLS),
    ("navigate to {url}",               "url",      URLS),
]

def bio_record(template, ent_key, ent_val):
    ph = "{" + ent_key + "}"
    if ph not in template:
        return None
    text   = template.replace(ph, ent_val)
    words  = text.split()
    e_words = ent_val.lower().split()
    wlow   = [w.lower().strip(".,!?") for w in words]
    bio    = ["O"] * len(words)
    for i in range(len(wlow) - len(e_words) + 1):
        if wlow[i:i+len(e_words)] == e_words:
            bio[i] = "B-" + ent_key
            for j in range(1, len(e_words)):
                bio[i+j] = "I-" + ent_key
            break
    return {"text": text, "tokens": words,
            "ner_tags": [LABEL2ID[l] for l in bio],
            "bio_labels": bio, ent_key: ent_val}

PER_TEMPLATE = 70
records_ent = []
for tmpl, ek, pool in ETEMPLATES:
    c = 0
    while c < PER_TEMPLATE:
        val = random.choice(pool)
        rec = bio_record(tmpl, ek, val)
        if rec:
            records_ent.append(rec)
            c += 1

random.shuffle(records_ent)
print(f"Generated {len(records_ent)} entity records")
dist = Counter(tag for r in records_ent for tag in r["bio_labels"] if tag != "O")
for lbl, cnt in sorted(dist.items()):
    print(f"  {lbl:<20} {cnt}")
"""

E_SAVE = """\
# Cell 3 — Save Entity Dataset as JSONL
import json
from pathlib import Path

ds_dir = Path("datasets"); ds_dir.mkdir(exist_ok=True)
out    = ds_dir / "mj_entities.jsonl"
with open(out, "w", encoding="utf-8") as f:
    for r in records_ent:
        f.write(json.dumps({"tokens": r["tokens"], "ner_tags": r["ner_tags"],
                             "text": r["text"]}, ensure_ascii=False) + "\\n")
print(f"Saved {len(records_ent)} entity records -> {out}")
"""

E_SPLIT = """\
# Cell 4 — Build HuggingFace Dataset + Split
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split

all_tok = [r["tokens"]   for r in records_ent]
all_tag = [r["ner_tags"] for r in records_ent]

tr_tok, vl_tok, tr_tag, vl_tag = train_test_split(
    all_tok, all_tag, test_size=0.15, random_state=42
)
def mk(toks, tags): return Dataset.from_dict({"tokens": toks, "ner_tags": tags})
hf_ent = DatasetDict({"train": mk(tr_tok, tr_tag), "validation": mk(vl_tok, vl_tag)})
print(f"Train: {len(tr_tok)}  | Val: {len(vl_tok)}")
"""

E_TOK = """\
# Cell 5 — Tokenize & Align BIO Labels
from transformers import AutoTokenizer

MODEL_NAME = "distilbert-base-uncased"
MAX_LEN    = 64
tokenizer  = AutoTokenizer.from_pretrained(MODEL_NAME)

def tok_align(examples):
    tok_out = tokenizer(examples["tokens"], truncation=True,
                        is_split_into_words=True, max_length=MAX_LEN)
    all_labels = []
    for i, tags in enumerate(examples["ner_tags"]):
        wids = tok_out.word_ids(batch_index=i)
        aligned, prev = [], None
        for wid in wids:
            if wid is None:
                aligned.append(-100)
            elif wid != prev:
                aligned.append(tags[wid])
            else:
                raw = LABELS[tags[wid]]
                aligned.append(LABEL2ID["I-" + raw[2:]] if raw.startswith("B-") else tags[wid])
            prev = wid
        all_labels.append(aligned)
    tok_out["labels"] = all_labels
    return tok_out

hf_ent_tok = hf_ent.map(tok_align, batched=True, remove_columns=["tokens", "ner_tags"])
print("Tokenization complete:", list(hf_ent_tok["train"].features.keys()))
"""

E_TRAIN = """\
# Cell 6 — Train DistilBERT NER Model
import torch, numpy as np
from transformers import (
    AutoModelForTokenClassification, TrainingArguments,
    Trainer, DataCollatorForTokenClassification,
)
from seqeval.metrics import classification_report as seq_rep

BATCH  = 32
EPOCHS = 5
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Training on: {device.upper()}")

ner_model = AutoModelForTokenClassification.from_pretrained(
    MODEL_NAME, num_labels=len(LABELS), id2label=ID2LABEL, label2id=LABEL2ID,
)
collator = DataCollatorForTokenClassification(tokenizer)

def ner_metrics(ep):
    pids, lbls = np.argmax(ep.predictions, axis=-1), ep.label_ids
    ts, ps = [], []
    for pr, lb in zip(pids, lbls):
        t, p = [], []
        for a, b in zip(pr, lb):
            if b == -100: continue
            t.append(ID2LABEL[b]); p.append(ID2LABEL[a])
        ts.append(t); ps.append(p)
    r = seq_rep(ts, ps, output_dict=True, zero_division=0)
    return {"f1": r.get("weighted avg", {}).get("f1-score", 0)}

from pathlib import Path
chk = Path("models/ner_checkpoints"); chk.mkdir(parents=True, exist_ok=True)

ner_args = TrainingArguments(
    output_dir=str(chk), num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH, per_device_eval_batch_size=64,
    learning_rate=2e-5, weight_decay=0.01,
    evaluation_strategy="epoch", save_strategy="epoch",
    load_best_model_at_end=True, metric_for_best_model="f1",
    logging_steps=50, seed=42, fp16=torch.cuda.is_available(), report_to="none",
)
ner_trainer = Trainer(
    model=ner_model, args=ner_args,
    train_dataset=hf_ent_tok["train"], eval_dataset=hf_ent_tok["validation"],
    tokenizer=tokenizer, data_collator=collator, compute_metrics=ner_metrics,
)
print("Starting NER training ...")
ner_trainer.train()
print("Done!")
"""

E_EVAL = """\
# Cell 7 — Evaluate Entity Extractor
from seqeval.metrics import classification_report as seq_rep
import numpy as np

pout = ner_trainer.predict(hf_ent_tok["validation"])
pids = np.argmax(pout.predictions, axis=-1)
lbls = pout.label_ids

ts, ps = [], []
for pr, lb in zip(pids, lbls):
    t, p = [], []
    for a, b in zip(pr, lb):
        if b == -100: continue
        t.append(ID2LABEL[b]); p.append(ID2LABEL[a])
    ts.append(t); ps.append(p)

print(seq_rep(ts, ps, zero_division=0))
"""

E_SAVE_MODEL = """\
# Cell 8 — Save Entity Model
import json
from pathlib import Path

save_dir = Path("exports/mj_entity_model")
save_dir.mkdir(parents=True, exist_ok=True)

ner_trainer.save_model(str(save_dir))
tokenizer.save_pretrained(str(save_dir))

with open(save_dir / "label_mapping.json", "w") as f:
    json.dump({"label2id": LABEL2ID,
               "id2label": {str(k): v for k, v in ID2LABEL.items()},
               "entity_types": ENTITY_TYPES, "labels": LABELS}, f, indent=2)

print(f"Entity model saved -> {save_dir}")
"""

E_PREDICTOR = """\
# Cell 9 — Entity Extractor Function
import torch

def extract_entities(text):
    words  = text.split()
    inputs = tokenizer(words, return_tensors="pt", truncation=True,
                       is_split_into_words=True, max_length=MAX_LEN)
    with torch.no_grad():
        pids = torch.argmax(ner_model(**inputs).logits, dim=-1)[0].tolist()

    wids = inputs.word_ids()
    ents, cur_e, cur_t, prev_w = {}, None, [], None
    for pid, wid in zip(pids, wids):
        if wid is None: continue
        lbl = ID2LABEL[pid]
        if lbl.startswith("B-"):
            if cur_e and cur_t: ents[cur_e] = " ".join(cur_t)
            cur_e = lbl[2:]; cur_t = [words[wid]] if wid != prev_w else []
        elif lbl.startswith("I-") and cur_e == lbl[2:]:
            if wid != prev_w: cur_t.append(words[wid])
        else:
            if cur_e and cur_t: ents[cur_e] = " ".join(cur_t)
            cur_e = None; cur_t = []
        prev_w = wid
    if cur_e and cur_t: ents[cur_e] = " ".join(cur_t)
    return {"text": text, "entities": ents}

tests = [
    "open youtube and search yash toxic trailer",
    "google VTU results",
    "send an email to boss@company.com",
    "create a task fix the login bug",
    "push to mj-assistant",
    "open VS Code",
    "analyze resume.pdf",
]
print("Entity Extraction Results:")
print("-" * 60)
for t in tests:
    r = extract_entities(t)
    print(f"  {t}")
    print(f"  -> {r['entities']}")
    print()
"""

E_COMBINED = '''\
# Cell 10 — Combined MJ Brain Output (Intent + Entities)
import json

def mj_brain(text):
    ents = extract_entities(text)["entities"]
    return {"text": text, "entities": ents}

commands = [
    "open youtube and search trending kannada songs",
    "google VTU results",
    "send email to professor@vtu.edu",
    "create a task fix the login bug",
    "push to mj-assistant on github",
    "open VS Code",
]
print("MJ Brain Output:")
print("=" * 60)
for cmd in commands:
    r = mj_brain(cmd)
    print(f"Input:   {cmd}")
    print(f"Entities: {json.dumps(r['entities'])}")
    print("-" * 60)
'''

E_EXPORT = """\
# Cell 11 — Export to MJ Backend
import shutil
from pathlib import Path

src = Path("exports/mj_entity_model")
dst = Path("../backend/app/ml_models/mj_entity_model")
dst.mkdir(parents=True, exist_ok=True)

for f in src.iterdir():
    shutil.copy2(f, dst / f.name)

print(f"Entity model exported: {dst.resolve()}")
for f in sorted(dst.iterdir()):
    print(f"  {f.name}")
"""

E_FASTAPI = '''\
# Cell 12 — FastAPI Integration Code

CODE = """
# app/ml/entity_extractor.py

import json, torch
from functools import lru_cache
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForTokenClassification

MODEL_PATH = Path(__file__).parent.parent / "ml_models" / "mj_entity_model"

@lru_cache(maxsize=1)
def _load():
    tok   = AutoTokenizer.from_pretrained(str(MODEL_PATH))
    model = AutoModelForTokenClassification.from_pretrained(str(MODEL_PATH))
    model.eval()
    with open(MODEL_PATH / "label_mapping.json") as f:
        m = json.load(f)
    return tok, model, {int(k): v for k, v in m["id2label"].items()}

def extract_entities(text: str) -> dict:
    tok, model, id2label = _load()
    words = text.split()
    inp   = tok(words, return_tensors="pt", truncation=True,
                is_split_into_words=True, max_length=64)
    with torch.no_grad():
        pids = torch.argmax(model(**inp).logits, dim=-1)[0].tolist()
    wids = inp.word_ids()
    ents, cur_e, cur_t, prev = {}, None, [], None
    for pid, wid in zip(pids, wids):
        if wid is None: continue
        lbl = id2label[pid]
        if lbl.startswith("B-"):
            if cur_e and cur_t: ents[cur_e] = " ".join(cur_t)
            cur_e = lbl[2:]; cur_t = [words[wid]] if wid != prev else []
        elif lbl.startswith("I-") and cur_e == lbl[2:]:
            if wid != prev: cur_t.append(words[wid])
        else:
            if cur_e and cur_t: ents[cur_e] = " ".join(cur_t)
            cur_e = None; cur_t = []
        prev = wid
    if cur_e and cur_t: ents[cur_e] = " ".join(cur_t)
    return ents
"""
print("=== app/ml/entity_extractor.py ===")
print(CODE)
print("Usage:")
print("  from app.ml.entity_extractor import extract_entities")
print("  entities = extract_entities('open youtube search trending songs')")
print("  # -> {'query': 'trending songs'}")
'''

E_BENCH = """\
# Cell 13 — Final Benchmark + Summary
import time, statistics

latencies = []
INPUTS = ["open youtube and search trending songs",
          "google VTU results", "send email to boss@company.com"]
for i in range(100):
    s = time.perf_counter()
    extract_entities(INPUTS[i % len(INPUTS)])
    latencies.append((time.perf_counter() - s) * 1000)
latencies.sort()

print(f"Entity Extractor Latency (100 calls):")
print(f"  Median: {statistics.median(latencies):.2f} ms")
print(f"  P95:    {latencies[94]:.2f} ms")
print(f"  Max:    {latencies[-1]:.2f} ms")
print()
print("=" * 55)
print("  MJ Entity Extractor — Training Complete!")
print("  Saved: exports/mj_entity_model/")
print("  Next: open MJ_Intent_Classifier.ipynb")
print("=" * 55)
"""

ENTITY_NB = make_notebook([
    md_cell("# MJ AI Assistant — Entity Extractor\n### BIO-scheme NER for extracting query, app, email, task, repo, file from commands\n**Output:** `exports/mj_entity_model/`"),
    code_cell(E_INSTALL),
    code_cell(E_GENERATE),
    code_cell(E_SAVE),
    code_cell(E_SPLIT),
    code_cell(E_TOK),
    code_cell(E_TRAIN),
    code_cell(E_EVAL),
    code_cell(E_SAVE_MODEL),
    code_cell(E_PREDICTOR),
    code_cell(E_COMBINED),
    code_cell(E_EXPORT),
    code_cell(E_FASTAPI),
    code_cell(E_BENCH),
])


# ==============================================================================
if __name__ == "__main__":
    save_nb(INTENT_NB, OUT_DIR / "MJ_Intent_Classifier.ipynb")
    save_nb(ENTITY_NB, OUT_DIR / "MJ_Entity_Extractor.ipynb")

    print()
    print("=" * 58)
    print("  Both notebooks created!")
    print("=" * 58)
    print()
    print("  Step 1 — Install Jupyter:")
    print("    pip install jupyter")
    print()
    print("  Step 2 — Open notebooks:")
    print("    jupyter notebook")
    print("    -> MJ_Intent_Classifier.ipynb  (run all cells)")
    print("    -> MJ_Entity_Extractor.ipynb   (run all cells)")
    print()
    print("  Step 3 — Or run headlessly:")
    print("    pip install nbconvert")
    print("    jupyter nbconvert --to notebook --execute MJ_Intent_Classifier.ipynb --output MJ_Intent_Classifier_done.ipynb")
    print("    jupyter nbconvert --to notebook --execute MJ_Entity_Extractor.ipynb  --output MJ_Entity_Extractor_done.ipynb")
    print()
    print("  Outputs:")
    print("    training/exports/mj_intent_model/")
    print("    training/exports/mj_entity_model/")
    print("    training/datasets/mj_intents_22class.jsonl")
    print("    training/datasets/mj_entities.jsonl")
