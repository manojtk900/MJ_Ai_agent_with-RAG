# MJ AI Assistant — Tool Specifications & Risk Tiers

## 1. Tool Registry Overview
All tools in MJ Assistant are registered with strict Pydantic parameter schemas, execution timeouts, and risk tiers.

## 2. Tool Matrix & Risk Levels

| Tool Name | Action | Risk Level | Confirmation Required | Timeout (s) |
| :--- | :--- | :--- | :--- | :--- |
| `youtube_search` | Opens YouTube search in browser | LOW | False | 10.0 |
| `google_search` | Opens Google search in browser | LOW | False | 10.0 |
| `open_browser` | Opens browser URL or browser app | LOW | False | 10.0 |
| `open_vscode` | Launches Visual Studio Code | LOW | False | 10.0 |
| `open_calculator` | Launches Windows Calculator | LOW | False | 10.0 |
| `open_notepad` | Launches Windows Notepad | LOW | False | 10.0 |
| `open_application` | Launches named desktop application | LOW | False | 10.0 |
| `create_task` | Creates task / reminder | LOW | False | 10.0 |
| `delete_task` | Removes task from scheduler | MEDIUM | False | 10.0 |
| `remember_fact` | Saves personal user fact to memory | LOW | False | 10.0 |
| `recall_memory` | Retrieves user fact from memory | LOW | False | 10.0 |
| `send_email` | Drafts and transmits email | HIGH | True | 15.0 |
| `github_push` | Pushes git commits to remote repository | HIGH | True | 30.0 |
| `delete_file` | Permanently deletes a local file | CRITICAL | True | 10.0 |
