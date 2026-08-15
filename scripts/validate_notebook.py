import ast
import json
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

NOTEBOOK_PATH = Path(__file__).resolve().parent.parent / "training" / "MJ_Intelligence_Agent_Training.ipynb"

def validate():
    print("=" * 65)
    print("  MJ INTELLIGENCE AGENT NOTEBOOK SYNTAX & STRUCTURE AUDIT")
    print("=" * 65)

    if not NOTEBOOK_PATH.exists():
        print(f"❌ Notebook not found: {NOTEBOOK_PATH}")
        sys.exit(1)

    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    print(f"Total Cells: {len(cells)}")
    assert len(cells) == 27, f"Expected 27 cells, got {len(cells)}"

    syntax_errors = 0
    for idx, cell in enumerate(cells, 1):
        cell_type = cell.get("cell_type")
        source = "".join(cell.get("source", []))
        first_line = cell.get("source", [""])[0].strip() if cell.get("source") else ""
        
        if cell_type == "code":
            try:
                ast.parse(source)
                status = "SYNTAX OK"
            except SyntaxError as e:
                status = f"SYNTAX ERROR: {e}"
                syntax_errors += 1
        else:
            status = "MARKDOWN OK"

        print(f"Cell {idx:02d} [{cell_type:<8}] ({status:<12}): {first_line[:50]}")

    print("=" * 65)
    if syntax_errors == 0:
        print("✅ ALL 27 CELLS PASSED SYNTAX & STRUCTURE AUDIT")
    else:
        print(f"❌ Found {syntax_errors} syntax errors")
        sys.exit(1)

if __name__ == "__main__":
    validate()
