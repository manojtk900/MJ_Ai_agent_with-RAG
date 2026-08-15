"""
MJ AI Assistant — Synthetic Training Dataset Generator
Generates diverse intent + entity labelled data for all 21 MJ intents.
Run:  python generate_dataset.py
Output: datasets/intents.jsonl  (intent-only)
        datasets/entities.jsonl (intent + extracted entities)
"""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

# ── Intent Templates ──────────────────────────────────────────────────────────
# Each intent has a list of template strings.
# {query}, {app}, {email}, {date}, {time}, {repo}, {file}, {task}
# are filled in at generation time.

INTENTS: dict[str, list[str]] = {

    "open_browser": [
        "open browser", "launch my browser", "start chrome", "open chrome",
        "open firefox", "launch firefox", "open edge", "start the browser",
        "open a web browser", "start browser please", "can you open chrome",
        "hey open the browser", "browser open", "show me a browser",
        "open internet explorer", "open browser window", "launch web browser",
        "start internet browser", "open chromium", "browser please",
    ],

    "youtube_search": [
        "open youtube search {query}", "search {query} on youtube",
        "find {query} on youtube", "play {query} on youtube",
        "youtube {query}", "youtube search {query}",
        "search youtube for {query}", "look up {query} on youtube",
        "find me {query} on youtube", "can you search {query} on youtube",
        "search for {query} on youtube please", "go to youtube and search {query}",
        "open youtube and search for {query}", "hey mj search youtube for {query}",
        "i want to watch {query}", "play {query} video",
        "find {query} song on youtube", "youtube search for {query} please",
        "look for {query} on youtube", "find {query} tutorial on youtube",
        "search {query} song", "find {query} movie trailer on youtube",
        "watch {query} on youtube", "mj find me {query} on youtube",
    ],

    "google_search": [
        "google {query}", "search {query} on google",
        "google search {query}", "search for {query}",
        "look up {query}", "find information about {query}",
        "can you google {query}", "search the web for {query}",
        "find {query} online", "search {query} please",
        "i need information on {query}", "look for {query} on google",
        "search {query} on the internet", "google {query} for me",
        "find me results for {query}", "search for {query} online",
        "what is {query} google it", "find {query} information",
        "research {query}", "i need to find {query}",
        "search {query} in google", "look {query} up on google",
    ],

    "open_application": [
        "open {app}", "launch {app}", "start {app}", "run {app}",
        "open the {app} app", "can you open {app}", "start {app} please",
        "launch {app} application", "open {app} program",
        "hey mj open {app}", "start the {app}", "bring up {app}",
        "open {app} for me", "launch the {app} app",
        "start up {app}", "fire up {app}", "get {app} running",
        "open {app} on my computer", "can you launch {app} for me",
        "open {app} app please",
    ],

    "create_task": [
        "create a task to {task}", "add a task {task}", "new task {task}",
        "add to my todo list {task}", "create todo {task}",
        "remind me to {task}", "add {task} to my tasks",
        "create task: {task}", "make a new task for {task}",
        "i need to {task} add it to my tasks",
        "add {task} to my to-do", "create a reminder for {task}",
        "task: {task}", "set a task for {task}",
        "add new task {task} please", "make a task to {task}",
        "put {task} on my task list", "schedule task {task}",
        "add task {task} high priority", "create an urgent task {task}",
    ],

    "update_task": [
        "update my task about {task}", "mark task {task} as done",
        "complete the task {task}", "close task {task}",
        "task {task} is finished", "mark {task} complete",
        "update task {task} to in progress", "change task {task} status",
        "task {task} done", "finish task {task}",
        "update task: {task}", "set {task} as completed",
        "edit my task {task}", "change the {task} task",
        "task update {task}", "i finished {task} mark it done",
    ],

    "delete_task": [
        "delete task {task}", "remove task {task}", "cancel task {task}",
        "delete the task about {task}", "remove {task} from my list",
        "i no longer need task {task}", "delete {task} task",
        "remove the {task} reminder", "cancel the task for {task}",
        "get rid of task {task}", "erase task {task}",
        "drop task {task}", "clear task {task}",
        "i don't need to {task} anymore delete it",
        "task {task} not needed delete it",
    ],

    "github_push": [
        "push my code to github", "git push to {repo}",
        "push changes to {repo}", "commit and push to github",
        "push to main branch", "push my latest changes",
        "git push origin main", "commit my code and push",
        "push code to {repo} repo", "push to {repo} on github",
        "send my changes to github", "push the code",
        "push latest commit to {repo}", "github push",
        "push to origin", "push my commits",
    ],

    "github_pull": [
        "pull from github", "git pull {repo}", "pull latest changes",
        "pull from {repo}", "git pull origin main",
        "get latest code from github", "sync with github",
        "pull updates from {repo}", "fetch and merge from github",
        "git pull", "pull the latest version", "get latest from {repo}",
        "sync code with {repo}", "download latest changes from github",
        "pull origin main", "pull my code",
    ],

    "github_create_repo": [
        "create a github repo called {repo}", "new github repository {repo}",
        "make a new repo {repo}", "create repo {repo} on github",
        "initialize github repository {repo}", "set up a new github repo for {repo}",
        "make github repo {repo}", "create github project {repo}",
        "new repo {repo}", "create a new repository named {repo}",
        "initialize repo {repo}", "setup github repo {repo}",
        "create a private repo {repo}", "create public repo {repo}",
        "github new repo {repo}",
    ],

    "read_email": [
        "check my email", "open my inbox", "read my emails",
        "show me my emails", "what emails do i have",
        "check gmail", "open email", "read my inbox",
        "show unread emails", "any new emails",
        "check my messages", "read latest emails",
        "open my email inbox", "what is in my inbox",
        "show me unread messages", "check email please",
        "read my new emails", "view my emails",
        "check for new emails", "show email notifications",
    ],

    "send_email": [
        "send an email to {email}", "email {email}", "compose email to {email}",
        "write an email to {email}", "send message to {email}",
        "draft an email to {email}", "send email to {email} about {task}",
        "write email to {email} regarding {task}", "email {email} about {task}",
        "compose a message to {email}", "send {email} an email",
        "write to {email}", "contact {email} by email",
        "send an email about {task} to {email}",
        "email {email} the {task} details",
    ],

    "summarize_email": [
        "summarize my emails", "summarize my inbox",
        "give me a summary of my emails", "what did i receive today in email",
        "email summary please", "summarize latest emails",
        "brief me on my emails", "what emails are important",
        "summarize unread messages", "give email overview",
        "quick email summary", "what are my top emails",
        "summarize today's emails", "email briefing",
        "digest my emails", "what's in my email today",
    ],

    "remember_fact": [
        "my college is {query}", "my project is {query}",
        "remember that my name is {query}", "my github is {query}",
        "i am preparing for {query}", "remember: {query}",
        "note that {query}", "remember this: {query}",
        "store this fact: {query}", "my preference is {query}",
        "save that {query}", "keep in mind that {query}",
        "my stack is {query}", "i work at {query}",
        "my location is {query}", "remember my {query}",
    ],

    "recall_memory": [
        "what is my college", "what project am i working on",
        "where do i study", "what is my github",
        "what am i preparing for", "what is my name",
        "what did i tell you about me", "recall my preferences",
        "what do you know about me", "what is my stack",
        "who am i", "what is my location", "where do i work",
        "what college did i say", "tell me about my project",
        "what do i do", "what is my background",
    ],

    "upload_file": [
        "upload file {file}", "upload {file} to mj",
        "attach {file}", "send me {file}",
        "upload document {file}", "add {file} to system",
        "upload {file} please", "submit {file}",
        "attach document {file}", "upload my {file}",
        "send {file} to mj", "add document {file}",
        "upload the {file}", "attach {file} file",
        "upload {file} for analysis",
    ],

    "analyze_pdf": [
        "analyze this pdf", "read this pdf {file}",
        "summarize pdf {file}", "extract text from {file}",
        "analyze {file}", "summarize this document {file}",
        "what does this pdf say {file}", "read document {file}",
        "analyze the pdf", "summarize this pdf",
        "extract data from {file}", "read the pdf",
        "analyze this document", "what is in this pdf {file}",
        "pdf analysis {file}", "analyze {file} document",
    ],

    "workflow_create": [
        "create a workflow to {task}", "automate {task}",
        "set up workflow for {task}", "build automation for {task}",
        "create automation {task}", "make a workflow for {task}",
        "automate the process of {task}", "schedule workflow {task}",
        "setup automated task {task}", "create pipeline for {task}",
        "build workflow {task}", "workflow: {task}",
        "automate {task} every day", "create recurring task for {task}",
        "set up daily automation for {task}",
    ],

    "workflow_run": [
        "run workflow {task}", "execute workflow {task}",
        "start workflow {task}", "trigger workflow {task}",
        "run the {task} workflow", "execute my automation {task}",
        "start automation {task}", "run my daily routine",
        "execute daily workflow", "run {task} pipeline",
        "trigger {task} automation", "start {task} workflow",
        "run the automation for {task}", "execute {task} now",
        "fire workflow {task}",
    ],

    "chat": [
        "hi", "hello", "hey mj", "how are you",
        "what can you do", "help me", "good morning",
        "good evening", "what is your name", "tell me a joke",
        "how's it going", "what's up mj", "hey there",
        "hello mj", "what can you help me with",
        "nice to meet you", "who are you",
        "can you help me", "what do you do",
        "introduce yourself", "what are your features",
        "i need help", "help please", "mj help",
        "tell me something", "talk to me",
    ],
}

# ── Filler values for placeholders ───────────────────────────────────────────
QUERIES = [
    "python tutorial", "machine learning basics", "kannada songs", "latest news",
    "how to cook pasta", "javascript tips", "react hooks", "fastapi tutorial",
    "best movies 2024", "cricket highlights", "tamil songs", "bollywood songs",
    "lofi music", "coding music", "gym workout", "yoga for beginners",
    "docker tutorial", "kubernetes guide", "web scraping python",
    "data science course", "artificial intelligence", "deep learning",
    "natural language processing", "computer vision", "blockchain basics",
    "stock market tips", "personal finance", "how to invest",
    "trending songs", "new music 2024", "motivational speeches",
    "ted talks", "programming memes", "funny videos",
]

APPS = [
    "calculator", "notepad", "vs code", "file explorer", "settings",
    "chrome", "spotify", "discord", "slack", "zoom",
    "microsoft word", "excel", "powerpoint", "vlc", "steam",
    "task manager", "control panel", "terminal", "powershell",
    "paint", "snipping tool",
]

EMAILS = [
    "john@gmail.com", "boss@company.com", "team@startup.io",
    "professor@university.edu", "client@business.com",
    "hr@company.org", "support@service.com", "friend@gmail.com",
    "recruiter@tech.com", "mentor@college.edu",
]

TASKS = [
    "fix the login bug", "write unit tests", "update documentation",
    "review pull request", "prepare presentation", "send weekly report",
    "buy groceries", "pay electricity bill", "call the doctor",
    "exercise for 30 minutes", "read 20 pages", "complete assignment",
    "submit project proposal", "attend team meeting", "learn docker",
    "setup ci cd pipeline", "deploy to production", "optimize database",
    "refactor auth module", "write api documentation",
]

REPOS = [
    "mj-assistant", "my-portfolio", "ai-chatbot", "fastapi-backend",
    "react-dashboard", "ml-model", "data-pipeline", "personal-blog",
    "ecommerce-app", "mobile-app",
]

FILES = [
    "resume.pdf", "report.pdf", "project.pdf", "invoice.pdf",
    "notes.pdf", "document.pdf", "specification.docx", "proposal.docx",
    "data.csv", "analysis.xlsx",
]

DATES = [
    "tomorrow", "next monday", "today", "friday", "next week",
    "in 2 days", "next month", "this evening", "tonight", "next tuesday",
]

TIMES = [
    "9am", "10:30am", "2pm", "3:30pm", "6pm", "8pm", "noon", "midnight",
]

TYPOS = {
    "open": ["opn", "opne", "ope", "oepn"],
    "search": ["serach", "seach", "earch", "serch"],
    "youtube": ["yotube", "youtubee", "youttube", "ytube", "yt"],
    "google": ["goggle", "gogle", "goolge", "googel"],
    "please": ["pls", "plz", "plese"],
    "create": ["crate", "creat", "craete"],
    "email": ["emial", "emaail", "emal"],
    "task": ["taks", "tsk", "tsak"],
}


def _fill(template: str) -> str:
    """Fill placeholders with random sample values."""
    r = template
    r = r.replace("{query}", random.choice(QUERIES))
    r = r.replace("{app}", random.choice(APPS))
    r = r.replace("{email}", random.choice(EMAILS))
    r = r.replace("{task}", random.choice(TASKS))
    r = r.replace("{repo}", random.choice(REPOS))
    r = r.replace("{file}", random.choice(FILES))
    r = r.replace("{date}", random.choice(DATES))
    r = r.replace("{time}", random.choice(TIMES))
    return r


def _add_noise(text: str) -> str:
    """Randomly apply casing, typos, leading/trailing spaces."""
    casing = random.random()
    if casing < 0.1:
        text = text.upper()
    elif casing < 0.25:
        text = text.title()

    if random.random() < 0.12:
        for word, typos in TYPOS.items():
            if word in text.lower():
                text = re.sub(word, random.choice(typos), text, count=1, flags=re.IGNORECASE)
                break

    if random.random() < 0.2:
        text = text + random.choice([".", "!", "?", "...", " please"])

    if random.random() < 0.07:
        text = random.choice(["mj", "hey mj", "hey", "yo"]) + " " + text

    return text.strip()


def generate_intent_dataset(samples_per_intent: int = 500) -> list[dict]:
    """Generate intent classification dataset."""
    records: list[dict] = []
    for intent, templates in INTENTS.items():
        count = 0
        while count < samples_per_intent:
            template = random.choice(templates)
            filled = _fill(template)
            noisy = _add_noise(filled)
            records.append({"text": noisy, "intent": intent})
            count += 1
    random.shuffle(records)
    return records


def generate_entity_dataset(samples_per_intent: int = 200) -> list[dict]:
    """Generate entity extraction dataset for intents that carry entities."""
    entity_intents = {
        "youtube_search": ("query", QUERIES),
        "google_search": ("query", QUERIES),
        "open_application": ("app_name", APPS),
        "send_email": ("email", EMAILS),
        "create_task": ("task", TASKS),
        "github_push": ("repo", REPOS),
        "github_pull": ("repo", REPOS),
        "github_create_repo": ("repo", REPOS),
        "analyze_pdf": ("file", FILES),
        "remember_fact": ("fact", QUERIES),
    }

    records: list[dict] = []
    for intent, (entity_key, entity_pool) in entity_intents.items():
        templates = INTENTS[intent]
        count = 0
        while count < samples_per_intent:
            template = random.choice(templates)
            entity_value = random.choice(entity_pool)
            placeholder = {
                "query": "{query}", "app_name": "{app}", "email": "{email}",
                "task": "{task}", "repo": "{repo}", "file": "{file}", "fact": "{query}",
            }[entity_key]

            if placeholder in template:
                text = template.replace(placeholder, entity_value)
                text = _fill(text)
                noisy = _add_noise(text)
                records.append({
                    "text": noisy,
                    "intent": intent,
                    entity_key: entity_value,
                })
                count += 1
    random.shuffle(records)
    return records


def save_jsonl(records: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Saved {len(records)} records -> {path}")


if __name__ == "__main__":
    random.seed(42)

    OUT_DIR = Path(__file__).parent / "datasets"

    print("Generating intent dataset (500 samples x 21 intents)...")
    intent_data = generate_intent_dataset(samples_per_intent=500)
    save_jsonl(intent_data, OUT_DIR / "intents.jsonl")

    print("Generating entity dataset (200 samples x 10 entity intents)...")
    entity_data = generate_entity_dataset(samples_per_intent=200)
    save_jsonl(entity_data, OUT_DIR / "entities.jsonl")

    from collections import Counter
    dist = Counter(r["intent"] for r in intent_data)
    print("\nIntent Distribution:")
    for intent, count in sorted(dist.items()):
        print(f"   {intent:<30} {count}")
    print(f"\n   TOTAL intent samples: {len(intent_data)}")
    print(f"   TOTAL entity samples: {len(entity_data)}")
