from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PYTHON_FILES = [
    ROOT / ".github" / "scripts" / "common.py",
    ROOT / ".github" / "scripts" / "gatekeeper.py",
    ROOT / ".github" / "scripts" / "time_sentinel.py",
    ROOT / ".github" / "scripts" / "chronicler.py",
    ROOT / ".github" / "scripts" / "influence_sentinel.py",
    ROOT / ".github" / "scripts" / "resurrection_council.py",
]
REQUIRED_DOCS = [
    ROOT / "README.md",
    ROOT / "README.en.md",
    ROOT / "CHARTER.md",
    ROOT / "CHARTER.en.md",
    ROOT / "docs" / "i18n.md",
    ROOT / "docs" / "impact.md",
    ROOT / "docs" / "capacity.md",
    ROOT / "docs" / "risks.md",
    ROOT / "governance" / "capacity.yml",
    ROOT / "SETUP.md",
    ROOT / ".project-skills.md",
    ROOT / "LICENSE",
    ROOT / "LICENSE-DOCS.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CONTRIBUTING.zh-CN.md",
    ROOT / "DCO.md",
    ROOT / "community" / "index.json",
    ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "skill_proposal.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "resurrection_vote.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "governance_change.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "translation_fix.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "automation_bug.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "other_discussion.yml",
]


def validate_required_docs() -> None:
    for path in REQUIRED_DOCS:
        print(f"check {path.relative_to(ROOT)}")
        if not path.exists():
            raise FileNotFoundError(path)


def compile_python() -> None:
    for path in PYTHON_FILES:
        print(f"compile {path.relative_to(ROOT)}")
        py_compile.compile(str(path), doraise=True)


def validate_workflows() -> None:
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        print(f"parse {path.relative_to(ROOT)}")
        yaml.safe_load(path.read_text(encoding="utf-8"))


def run_unittest() -> None:
    print("run unittest")
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests")],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    validate_required_docs()
    compile_python()
    validate_workflows()
    run_unittest()
    print("local tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
