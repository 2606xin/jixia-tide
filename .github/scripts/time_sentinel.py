from __future__ import annotations

import argparse
import logging
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from common import commit_and_push, configure_logging, ensure_repo_dirs, run_git


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def tracked_markdown_files() -> list[Path]:
    result = run_git(["ls-files", "community/*.md"], check=True)
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def git_last_commit_at(path: Path) -> datetime | None:
    result = run_git(["log", "-1", "--format=%ct", "--", str(path)], check=False)
    value = result.stdout.strip()
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except ValueError:
        logging.warning("Could not parse git timestamp for %s: %s", path, value)
        return None


def frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        logging.warning("Skipping metadata read for %s: %s", path, exc)
        return {}
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        logging.warning("Skipping malformed frontmatter in %s: %s", path, exc)
        return {}
    return data if isinstance(data, dict) else {}


def parse_date(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if hasattr(value, "isoformat"):
        value = value.isoformat()
    if not isinstance(value, str):
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def last_activity_at(path: Path) -> datetime | None:
    metadata = frontmatter(path)
    candidates = [
        git_last_commit_at(path),
        parse_date(metadata.get("last_interaction_at")),
        parse_date(metadata.get("last_used_at")),
        parse_date(metadata.get("updated_at")),
    ]
    return max((candidate for candidate in candidates if candidate), default=None)


def archive_file(path: Path) -> Path:
    target = Path("legacy") / path.relative_to("community")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing legacy file: {target}")
    shutil.move(str(path), str(target))
    return target


def main() -> int:
    configure_logging()
    ensure_repo_dirs()
    parser = argparse.ArgumentParser(description="Archive inactive community skills.")
    parser.add_argument("--days", type=int, default=180)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    archived: list[tuple[Path, Path]] = []
    for path in tracked_markdown_files():
        try:
            last_activity = last_activity_at(path)
            if not last_activity:
                logging.warning("No activity timestamp for %s; leaving in community.", path)
                continue
            age_days = (now - last_activity).days
            logging.info("%s last active %s (%s days ago)", path, last_activity.isoformat(), age_days)
            if age_days > args.days:
                target = archive_file(path)
                archived.append((path, target))
                logging.info("Archived %s to %s", path, target)
        except Exception as exc:
            logging.exception("Failed to process %s: %s", path, exc)

    if not archived:
        logging.info("No inactive skills found.")
        return 0

    if len(archived) == 1:
        skill_name = archived[0][0].stem
        message = f"[Bot] Archive inactive skill: {skill_name} to Legacy"
    else:
        message = f"[Bot] Archive {len(archived)} inactive skills to Legacy"
    commit_and_push(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
