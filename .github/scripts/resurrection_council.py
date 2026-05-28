from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import commit_and_push, configure_logging, ensure_repo_dirs, get_repo


COMMAND_RE = re.compile(r"^/vote-resurrect\s+([A-Za-z0-9_.\-/]+)\s*$", re.I | re.M)
MARKER_RE = re.compile(r"<!--\s*jixia-resurrection\s+({.*?})\s*-->", re.S)
DONE_RE = re.compile(r"<!--\s*jixia-resurrection-done\s+({.*?})\s*-->", re.S)


def sanitize_skill_name(value: str) -> Path:
    cleaned = value.strip().lstrip("/")
    if not cleaned.endswith(".md"):
        cleaned += ".md"
    path = Path(cleaned)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Invalid skill path")
    return path


def legacy_path_for(skill_name: str) -> Path:
    return Path("legacy") / sanitize_skill_name(skill_name)


def community_path_for(skill_name: str) -> Path:
    return Path("community") / sanitize_skill_name(skill_name)


def reaction_counts(comment) -> tuple[int, int]:
    up = down = 0
    for reaction in comment.get_reactions():
        if reaction.content == "+1":
            up += 1
        elif reaction.content == "-1":
            down += 1
    return up, down


def start_vote(repo, issue_number: int, comment_body: str) -> int:
    issue = repo.get_issue(issue_number)
    matches = COMMAND_RE.findall(comment_body)
    if not matches:
        logging.info("No resurrection command found.")
        return 0

    for skill_name in matches:
        try:
            legacy_path = legacy_path_for(skill_name)
            if not legacy_path.exists():
                issue.create_comment(f"Cannot start resurrection vote: `{legacy_path.as_posix()}` was not found.")
                continue
            ends_at = datetime.now(timezone.utc) + timedelta(days=7)
            payload = {
                "skill": sanitize_skill_name(skill_name).as_posix(),
                "ends_at": ends_at.isoformat(),
                "issue": issue_number,
            }
            body = (
                f"Resurrection vote started for `{payload['skill']}`.\n\n"
                "React with :+1: to support or :-1: to oppose. Voting closes at "
                f"`{payload['ends_at']}`.\n\n"
                f"<!-- jixia-resurrection {json.dumps(payload, sort_keys=True)} -->"
            )
            vote_comment = issue.create_comment(body)
            vote_comment.create_reaction("+1")
            vote_comment.create_reaction("-1")
            logging.info("Started resurrection vote for %s on issue #%s", skill_name, issue_number)
        except Exception as exc:
            logging.exception("Failed to start vote for %s: %s", skill_name, exc)
            issue.create_comment(f"Failed to start resurrection vote for `{skill_name}`: {exc}")
    return 0


def already_done(issue, skill: str) -> bool:
    for comment in issue.get_comments():
        for match in DONE_RE.findall(comment.body or ""):
            try:
                payload = json.loads(match)
            except json.JSONDecodeError:
                continue
            if payload.get("skill") == skill:
                return True
    return False


def resurrect(skill: str) -> tuple[Path, Path]:
    source = legacy_path_for(skill)
    target = community_path_for(skill)
    if not source.exists():
        raise FileNotFoundError(f"{source.as_posix()} not found")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"{target.as_posix()} already exists")
    shutil.move(str(source), str(target))
    return source, target


def process_votes(repo) -> int:
    now = datetime.now(timezone.utc)
    processed = 0
    for issue in repo.get_issues(state="open"):
        try:
            for comment in issue.get_comments():
                body = comment.body or ""
                for raw_payload in MARKER_RE.findall(body):
                    payload = json.loads(raw_payload)
                    skill = payload["skill"]
                    ends_at = datetime.fromisoformat(payload["ends_at"])
                    if ends_at.tzinfo is None:
                        ends_at = ends_at.replace(tzinfo=timezone.utc)
                    if now < ends_at:
                        continue
                    if already_done(issue, skill):
                        continue

                    up, down = reaction_counts(comment)
                    total = up + down
                    approved = total > 0 and up / total > 0.5
                    logging.info("Vote for %s: up=%s down=%s approved=%s", skill, up, down, approved)
                    result_payload = {
                        "skill": skill,
                        "processed_at": now.isoformat(),
                        "approved": approved,
                    }
                    if approved:
                        source, target = resurrect(skill)
                        commit_and_push(f"[Bot] Resurrect skill: {Path(skill).stem}")
                        issue.create_comment(
                            f"Resurrection succeeded for `{skill}`. Moved `{source.as_posix()}` to `{target.as_posix()}`.\n\n"
                            f"<!-- jixia-resurrection-done {json.dumps(result_payload, sort_keys=True)} -->"
                        )
                    else:
                        issue.create_comment(
                            f"Resurrection vote for `{skill}` did not pass. Final count: +1={up}, -1={down}.\n\n"
                            f"<!-- jixia-resurrection-done {json.dumps(result_payload, sort_keys=True)} -->"
                        )
                    processed += 1
        except Exception as exc:
            logging.exception("Failed to process issue #%s: %s", issue.number, exc)
    logging.info("Processed %s completed votes.", processed)
    return 0


def main() -> int:
    configure_logging()
    ensure_repo_dirs()
    parser = argparse.ArgumentParser(description="Manage resurrection votes.")
    parser.add_argument("mode", choices=["start", "process"])
    parser.add_argument("--issue-number", type=int, default=int(os.environ.get("ISSUE_NUMBER", "0") or "0"))
    parser.add_argument("--comment-body", default=os.environ.get("COMMENT_BODY", ""))
    args = parser.parse_args()

    repo = get_repo()
    if args.mode == "start":
        if not args.issue_number:
            raise RuntimeError("start mode requires --issue-number or ISSUE_NUMBER")
        return start_vote(repo, args.issue_number, args.comment_body)
    return process_votes(repo)


if __name__ == "__main__":
    sys.exit(main())
