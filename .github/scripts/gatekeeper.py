from __future__ import annotations

import base64
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Any

import yaml
from github import GithubException

from common import configure_logging, get_repo


REQUIRED_FIELDS = {"title", "author", "tags", "created_at"}
MAX_ACTIVE_SKILLS_PER_AUTHOR = 5
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MALICIOUS_PATTERNS = [
    (re.compile(r"\brm\s+-rf\s+/(?:\s|$)"), "destructive rm command"),
    (re.compile(r"\b(?:curl|wget)\b.+\|\s*(?:sh|bash|zsh|pwsh|powershell)\b", re.I | re.S), "download-and-execute shell pipeline"),
    (re.compile(r"\bpowershell\b.+-(?:enc|encodedcommand)\b", re.I | re.S), "encoded PowerShell command"),
    (re.compile(r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;:", re.S), "fork bomb pattern"),
    (re.compile(r"\bmkfs(?:\.[a-z0-9]+)?\b", re.I), "filesystem formatting command"),
    (re.compile(r"\bdd\s+if=.+\s+of=/dev/(?:sd|hd|nvme)", re.I | re.S), "raw disk overwrite command"),
    (re.compile(r"\bchmod\s+-R\s+777\s+/(?:\s|$)", re.I), "unsafe recursive chmod on root"),
]
SIGNED_OFF_BY_RE = re.compile(r"^Signed-off-by:\s+.+\s+<[^@\s]+@[^@\s]+>$", re.I | re.M)


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def decode_file(repo, path: str, ref: str) -> str:
    content_file = repo.get_contents(path, ref=ref)
    if isinstance(content_file, list):
        raise ValueError(f"{path} resolved to a directory")
    raw = base64.b64decode(content_file.content)
    return raw.decode("utf-8")


def parse_frontmatter(text: str) -> dict[str, Any]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        return {}
    return data


def validate_metadata(path: str, text: str) -> list[str]:
    metadata = parse_frontmatter(text)
    errors: list[str] = []
    missing = sorted(REQUIRED_FIELDS - metadata.keys())
    if missing:
        errors.append(f"{path}: missing required frontmatter fields: {', '.join(missing)}")
    if "tags" in metadata and not isinstance(metadata["tags"], list):
        errors.append(f"{path}: frontmatter field 'tags' must be a YAML list")
    return errors


def normalize_author(value: Any) -> str:
    return str(value or "").strip().casefold()


def skill_author(path: str, text: str) -> str:
    metadata = parse_frontmatter(text)
    return normalize_author(metadata.get("author"))


def community_markdown_paths(repo, ref: str) -> list[str]:
    try:
        contents = repo.get_contents("community", ref=ref)
    except Exception as exc:
        logging.warning("Unable to list community directory at %s: %s", ref, exc)
        return []

    paths: list[str] = []
    stack = contents if isinstance(contents, list) else [contents]
    while stack:
        item = stack.pop()
        if item.type == "dir":
            nested = repo.get_contents(item.path, ref=ref)
            stack.extend(nested if isinstance(nested, list) else [nested])
        elif item.path.endswith(".md"):
            paths.append(item.path)
    return paths


def author_counts_for_ref(repo, ref: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in community_markdown_paths(repo, ref):
        try:
            author = skill_author(path, decode_file(repo, path, ref))
        except Exception as exc:
            logging.warning("Skipping author count for %s at %s: %s", path, ref, exc)
            continue
        if author:
            counts[author] = counts.get(author, 0) + 1
    return counts


def validate_author_quota(repo, pr, changed_files) -> list[str]:
    errors: list[str] = []
    base_counts = author_counts_for_ref(repo, pr.base.sha)
    prospective_counts = dict(base_counts)

    for changed in changed_files:
        path = changed.filename
        if changed.status == "removed" or not path.startswith("community/") or not path.endswith(".md"):
            continue
        try:
            author = skill_author(path, decode_file(repo, path, pr.head.sha))
        except Exception as exc:
            errors.append(f"{path}: failed to read author for quota check: {exc}")
            continue
        if not author:
            continue
        if changed.status == "added":
            prospective_counts[author] = prospective_counts.get(author, 0) + 1
        elif changed.status in {"modified", "renamed"}:
            try:
                base_author = skill_author(path, decode_file(repo, path, pr.base.sha))
            except Exception:
                base_author = ""
            if author != base_author:
                prospective_counts[author] = prospective_counts.get(author, 0) + 1

    for author, count in sorted(prospective_counts.items()):
        if count > MAX_ACTIVE_SKILLS_PER_AUTHOR:
            current = base_counts.get(author, 0)
            errors.append(
                f"author `{author}` would have {count} active skills in community/ "
                f"(current: {current}, limit: {MAX_ACTIVE_SKILLS_PER_AUTHOR})"
            )
    return errors


def scan_for_malicious_content(path: str, text: str) -> list[str]:
    errors: list[str] = []
    if "\x00" in text:
        errors.append(f"{path}: contains NUL byte")
    control_chars = [ch for ch in text if ord(ch) < 32 and ch not in "\n\r\t"]
    if control_chars:
        errors.append(f"{path}: contains unsupported control characters")
    for pattern, description in MALICIOUS_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path}: suspicious content detected ({description})")
    return errors


def validate_dco(pr) -> list[str]:
    errors: list[str] = []
    for commit in pr.get_commits():
        message = commit.commit.message or ""
        if not SIGNED_OFF_BY_RE.search(message):
            sha = getattr(commit, "sha", "")[:7]
            errors.append(
                f"commit {sha}: missing DCO sign-off. "
                "Please recommit with `git commit -s` or add a `Signed-off-by: Name <email>` line."
            )
    return errors


def validate_pr(pr) -> ValidationResult:
    repo = pr.base.repo
    errors: list[str] = []
    changed_files = list(pr.get_files())

    if not changed_files:
        errors.append("PR does not contain any changed files.")

    errors.extend(validate_dco(pr))
    errors.extend(validate_author_quota(repo, pr, changed_files))

    for changed in changed_files:
        path = changed.filename
        status = changed.status
        logging.info("Checking %s (%s)", path, status)

        if status == "removed":
            errors.append(f"{path}: deleting files is not allowed through Gatekeeper")
            continue
        if not path.startswith("community/") or not path.endswith(".md"):
            errors.append(f"{path}: only Markdown files under community/ are allowed")
            continue

        try:
            text = decode_file(repo, path, pr.head.sha)
        except Exception as exc:
            errors.append(f"{path}: failed to read file from PR head: {exc}")
            continue

        errors.extend(validate_metadata(path, text))
        errors.extend(scan_for_malicious_content(path, text))

    return ValidationResult(ok=not errors, errors=errors)


def ensure_label(repo, name: str, color: str, description: str):
    try:
        return repo.get_label(name)
    except GithubException:
        return repo.create_label(name=name, color=color, description=description)


def comment(pr, body: str) -> None:
    logging.info("Commenting on PR #%s", pr.number)
    pr.as_issue().create_comment(body)


def wait_for_mergeable(pr) -> None:
    for _ in range(12):
        pr.update()
        if pr.mergeable is not None:
            return
        time.sleep(5)


def approve_and_merge(pr) -> None:
    wait_for_mergeable(pr)
    if pr.mergeable is False:
        raise RuntimeError("GitHub reports this PR is not mergeable.")
    pr.create_review(event="APPROVE", body="Gatekeeper checks passed. Auto-approving.")
    result = pr.merge(
        commit_title=f"[Bot] Merge approved skill PR #{pr.number}",
        merge_method=os.environ.get("GATEKEEPER_MERGE_METHOD", "squash"),
    )
    if not result.merged:
        raise RuntimeError(result.message or "GitHub merge API did not merge the PR.")


def main() -> int:
    configure_logging()
    pr_number = os.environ.get("PR_NUMBER") or os.environ.get("GITHUB_REF_NAME", "").split("/")[0]
    if not pr_number:
        logging.error("Missing PR_NUMBER")
        return 2

    repo = get_repo()
    pr = repo.get_pull(int(pr_number))
    failure_label = ensure_label(repo, "gatekeeper:failed", "d73a4a", "Automated quality gate failed")
    success_label = ensure_label(repo, "gatekeeper:passed", "2da44e", "Automated quality gate passed")

    result = validate_pr(pr)
    if not result.ok:
        pr.as_issue().add_to_labels(failure_label.name)
        comment(
            pr,
            "Gatekeeper rejected this PR.\n\n"
            + "\n".join(f"- {error}" for error in result.errors)
            + "\n\nPlease update the contribution and push again.",
        )
        logging.error("PR validation failed: %s", result.errors)
        return 1

    try:
        pr.as_issue().remove_from_labels(failure_label.name)
    except Exception:
        pass
    pr.as_issue().add_to_labels(success_label.name)
    comment(pr, "Gatekeeper checks passed. Attempting automatic approval and merge.")
    try:
        approve_and_merge(pr)
    except Exception as exc:
        pr.as_issue().add_to_labels(failure_label.name)
        comment(pr, f"Gatekeeper validation passed, but automatic merge failed: `{exc}`")
        logging.exception("PR #%s merge failed: %s", pr.number, exc)
        return 1
    logging.info("PR #%s approved and merged.", pr.number)
    return 0


if __name__ == "__main__":
    sys.exit(main())
