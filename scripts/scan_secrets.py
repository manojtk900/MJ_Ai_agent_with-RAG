import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    "node_modules", ".pytest_cache", ".git", "env312", "env", ".venv",
    "__pycache__", "checkpoints", "ner_checkpoints"
}

EXCLUDE_EXTS = {
    ".safetensors", ".pt", ".bin", ".onnx", ".exe", ".png", ".jpg", ".jpeg",
    ".lock", ".wasm", ".pyc"
}

PATTERNS = [
    (r"(?:api[_-]?key|secret|token|password|auth|bearer)\s*[:=]\s*['\"]([^'\"]{10,})['\"]", "Generic Secret"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google/Gemini API Key"),
    (r"ghp_[0-9A-Za-z]{36}", "GitHub Personal Access Token"),
    (r"gsk_[0-9A-Za-z]{48}", "Groq API Key"),
    (r"sk-[0-9A-Za-z]{32,}", "OpenAI API Key"),
    (r"hf_[0-9A-Za-z]{34}", "Hugging Face Token"),
]

WHITELIST = {
    "your_openai_api_key_here", "your_groq_api_key_here", "your_gemini_api_key_here",
    "your_anthropic_api_key", "your_github_token_here", "your_tavily_api_key_here",
    "your_langsmith_api_key", "your_weather_api_key", "your_alpha_vantage_key",
    "change_me_super_secret_session_key", "your_jwt_secret_key_change_in_production",
    "your_secure_password", "placeholder", "dummy_token"
}

def scan():
    findings = []
    for p in ROOT.rglob("*"):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in EXCLUDE_EXTS:
            continue
        # Skip .env since it must be ignored in git
        if p.name == ".env":
            findings.append((p.relative_to(ROOT), 1, "Direct .env file found (MUST BE IGNORED)", "Local Environment File"))
            continue

        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, 1):
            for regex, desc in PATTERNS:
                matches = re.finditer(regex, line, re.IGNORECASE)
                for m in matches:
                    val = m.group(1) if m.groups() else m.group(0)
                    if any(w in val.lower() for w in WHITELIST):
                        continue
                    if "example" in p.name.lower():
                        continue
                    findings.append((p.relative_to(ROOT), idx, line.strip()[:80], desc))

    print(f"=== SECRET SCAN REPORT ({len(findings)} findings) ===")
    for rel_path, line_no, snippet, desc in findings:
        print(f"[{desc}] {rel_path}:{line_no} -> {snippet[:60]}...")
    return findings

if __name__ == "__main__":
    scan()
