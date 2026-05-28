from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from github import Github


BOT_NAME = "jixia-bot"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


def configure_logging() -> None:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(message)s",
    )


def get_token() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing GH_TOKEN or GITHUB_TOKEN")
    return token


def get_repo():
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    if not repo_name:
        raise RuntimeError("Missing GITHUB_REPOSITORY")
    return Github(get_token()).get_repo(repo_name)


def run_git(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    logging.info("git %s", " ".join(args))
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def configure_git_identity() -> None:
    run_git(["config", "user.name", BOT_NAME])
    run_git(["config", "user.email", BOT_EMAIL])


def has_git_changes() -> bool:
    result = run_git(["status", "--porcelain"], check=True)
    return bool(result.stdout.strip())


def commit_and_push(message: str) -> bool:
    if not has_git_changes():
        logging.info("No repository changes to commit.")
        return False
    configure_git_identity()
    run_git(["add", "-A"])
    run_git(["commit", "-m", message])
    run_git(["push"])
    logging.info("Committed and pushed: %s", message)
    return True


def ensure_repo_dirs() -> None:
    Path("community").mkdir(exist_ok=True)
    Path("legacy").mkdir(exist_ok=True)
