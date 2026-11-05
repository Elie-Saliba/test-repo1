"""Offline, stdlib-only smoke tests for the two benchmark skills."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

with tempfile.TemporaryDirectory() as temp:
    for name in ("alpha", "beta"):
        skill = ROOT / "skills" / f"change-brief-{name}"
        out = Path(temp) / name / "brief.md"
        command = [
            sys.executable, str(skill / "scripts" / "build_brief.py"),
            "--input", str(skill / "examples" / "changes.json"),
            "--output", str(out), "--cache-dir", str(Path(temp) / name / "cache"),
        ]
        for _ in range(2):
            subprocess.run(command, check=True, capture_output=True, text=True)
        text = out.read_text(encoding="utf-8")
        assert "# Orion Workspace — 2.4.1" in text
        assert "Total changes: 3" in text
        print(f"{name}: passed (fresh and cached)")
