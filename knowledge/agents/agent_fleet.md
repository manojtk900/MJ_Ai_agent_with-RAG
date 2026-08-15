# MJ AI Assistant — Specialized Agent Fleet

## 1. Multi-Agent Topology
The system deploys 15 specialized agents:

1. **Controller Agent**: The primary entry point. Runs local ML intent prediction, entity extraction, and invokes the `RouterGate`.
2. **Intelligence Agent**: Handles general conversation, reasoning, RAG question answering, coding assistance, and career/planning inquiries.
3. **Desktop Agent**: Executes local application launches and manages Windows OS system interactions.
4. **Search Agent**: Executes Google web searches and parses search results.
5. **Research Agent**: Performs deep web synthesis and information extraction across multiple sources.
6. **Execution Agent**: Executes git workflows (`git push`, `git pull`, `create_repo`) and automation scripts.
7. **Email Agent**: Connects to Gmail API/IMAP/SMTP to read, summarize, and draft emails.
8. **Reminder & Task Agent**: Manages scheduled reminders, task creation, updates, and deletion.
9. **Memory Agent**: Stores and retrieves user facts and preferences in Redis/PostgreSQL.
10. **File Agent**: Analyzes PDFs, documents, text files, and generates structured summaries.
11. **Planner Agent**: Decomposes complex multi-step user goals into executable ReAct plans.
12. **Reflection Agent**: Evaluates output quality and error state before presenting answers to the user.
13. **Scheduler Agent**: Executes background recurring cron jobs and periodic tasks.
14. **System Agent**: Monitors hardware resource telemetry (CPU, RAM, GPU, Disk).
15. **Voice Agent**: Transcribes voice input and generates natural text-to-speech audio.
