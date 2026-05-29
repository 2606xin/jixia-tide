from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from common import commit_and_push, configure_logging, ensure_repo_dirs, get_repo, run_git


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
RESURRECTION_MARKER_RE = re.compile(r"jixia-resurrection\s+({.*?})", re.S)
OUTPUT_JSON = Path("community/index.json")
OUTPUT_MARKDOWN = Path("docs/impact.md")
README_ZH = Path("README.md")
README_EN = Path("README.en.md")
README_ZH_START = "<!-- jixia-impact:start zh -->"
README_ZH_END = "<!-- jixia-impact:end zh -->"
README_EN_START = "<!-- jixia-impact:start en -->"
README_EN_END = "<!-- jixia-impact:end en -->"


@dataclass
class InteractionSignals:
    mentions: int = 0
    vote_support: int = 0
    vote_oppose: int = 0
    sources: list[str] = field(default_factory=list)


@dataclass
class SkillRecord:
    path: str
    title: str
    author: str
    tags: list[str]
    created_at: str
    last_activity_at: str | None
    age_days: int | None
    commit_count: int
    mention_count: int
    vote_support: int
    vote_oppose: int
    impact_score: int


def tracked_skill_files() -> list[Path]:
    result = run_git(["ls-files", "community/*.md"], check=True)
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def frontmatter(path: Path) -> dict[str, Any]:
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
        logging.warning("Malformed frontmatter in %s: %s", path, exc)
        return {}
    return data if isinstance(data, dict) else {}


def parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)
    if hasattr(value, "isoformat"):
        value = value.isoformat()
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def git_timestamp(path: Path, fmt: str) -> datetime | None:
    result = run_git(["log", "-1", f"--format={fmt}", "--", str(path)], check=False)
    value = result.stdout.strip()
    if not value:
        return None
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except ValueError:
        logging.warning("Could not parse git timestamp for %s: %s", path, value)
        return None


def last_activity_at(path: Path, metadata: dict[str, Any]) -> datetime | None:
    candidates = [
        git_timestamp(path, "%ct"),
        parse_date(metadata.get("last_interaction_at")),
        parse_date(metadata.get("last_used_at")),
        parse_date(metadata.get("updated_at")),
        parse_date(metadata.get("created_at")),
    ]
    return max((candidate for candidate in candidates if candidate), default=None)


def commit_count(path: Path) -> int:
    result = run_git(["rev-list", "--count", "HEAD", "--", str(path)], check=False)
    value = result.stdout.strip()
    try:
        return int(value)
    except ValueError:
        logging.warning("Could not parse commit count for %s: %s", path, value)
        return 0


def normalize_tags(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def skill_aliases(path: Path, metadata: dict[str, Any]) -> set[str]:
    aliases = {
        path.as_posix().casefold(),
        path.name.casefold(),
        path.stem.casefold(),
    }
    title = str(metadata.get("title") or "").strip()
    if title:
        aliases.add(title.casefold())
    return aliases


def text_mentions_alias(text: str, aliases: set[str]) -> bool:
    lowered = text.casefold()
    return any(alias and alias in lowered for alias in aliases)


def safe_text(value: Any) -> str:
    return str(value or "")


def reaction_totals(comment) -> tuple[int, int]:
    support = oppose = 0
    try:
        for reaction in comment.get_reactions():
            if reaction.content == "+1":
                support += 1
            elif reaction.content == "-1":
                oppose += 1
    except Exception as exc:
        logging.warning("Unable to read reactions for comment %s: %s", getattr(comment, "id", "?"), exc)
    return support, oppose


def collect_interactions(repo, skill_alias_map: dict[str, set[str]]) -> dict[str, InteractionSignals]:
    signals = {path: InteractionSignals() for path in skill_alias_map}
    try:
        issues = repo.get_issues(state="all")
        for issue in issues:
            issue_text = "\n".join([safe_text(issue.title), safe_text(issue.body)])
            note_matches(issue_text, issue.html_url, skill_alias_map, signals)
            try:
                comments = issue.get_comments()
                for comment in comments:
                    body = safe_text(comment.body)
                    matched_paths = note_matches(body, comment.html_url, skill_alias_map, signals)
                    if RESURRECTION_MARKER_RE.search(body):
                        support, oppose = reaction_totals(comment)
                        for path in matched_paths:
                            signals[path].vote_support += support
                            signals[path].vote_oppose += oppose
            except Exception as exc:
                logging.warning("Unable to read comments for issue #%s: %s", issue.number, exc)
    except Exception as exc:
        logging.warning("Unable to collect GitHub interactions: %s", exc)
    return signals


def note_matches(
    text: str,
    source_url: str,
    skill_alias_map: dict[str, set[str]],
    signals: dict[str, InteractionSignals],
) -> list[str]:
    matched: list[str] = []
    for path, aliases in skill_alias_map.items():
        if text_mentions_alias(text, aliases):
            signals[path].mentions += 1
            if source_url and source_url not in signals[path].sources:
                signals[path].sources.append(source_url)
            matched.append(path)
    return matched


def impact_score(age_days: int | None, commits: int, mentions: int, support: int, oppose: int) -> int:
    freshness = 0 if age_days is None else max(0, 30 - min(age_days, 30))
    commit_points = min(commits * 3, 20)
    mention_points = min(mentions * 5, 30)
    vote_points = max(0, min(support * 3 - oppose * 2, 25))
    return 10 + freshness + commit_points + mention_points + vote_points


def build_records(now: datetime, repo=None) -> list[SkillRecord]:
    paths = tracked_skill_files()
    metadata_by_path = {path.as_posix(): frontmatter(path) for path in paths}
    alias_map = {path: skill_aliases(Path(path), metadata) for path, metadata in metadata_by_path.items()}
    interactions = collect_interactions(repo, alias_map) if repo else {path: InteractionSignals() for path in alias_map}

    records: list[SkillRecord] = []
    for raw_path, metadata in metadata_by_path.items():
        path = Path(raw_path)
        last_activity = last_activity_at(path, metadata)
        age_days = (now - last_activity).days if last_activity else None
        commits = commit_count(path)
        signal = interactions.get(raw_path, InteractionSignals())
        score = impact_score(age_days, commits, signal.mentions, signal.vote_support, signal.vote_oppose)
        records.append(
            SkillRecord(
                path=raw_path,
                title=str(metadata.get("title") or path.stem),
                author=str(metadata.get("author") or ""),
                tags=normalize_tags(metadata.get("tags")),
                created_at=str(metadata.get("created_at") or ""),
                last_activity_at=last_activity.isoformat() if last_activity else None,
                age_days=age_days,
                commit_count=commits,
                mention_count=signal.mentions,
                vote_support=signal.vote_support,
                vote_oppose=signal.vote_oppose,
                impact_score=score,
            )
        )
    return sorted(records, key=lambda item: (-item.impact_score, item.path))


def write_json(records: list[SkillRecord], generated_at: datetime) -> None:
    payload = {
        "generated_at": generated_at.isoformat(),
        "schema_version": 1,
        "score_formula": "10 + freshness(max 30) + commits(max 20) + mentions(max 30) + votes(max 25)",
        "records": [record.__dict__ for record in records],
    }
    OUTPUT_JSON.parent.mkdir(exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(records: list[SkillRecord], generated_at: datetime) -> None:
    lines = [
        "# Skill Impact Signals",
        "",
        f"Generated at: `{generated_at.isoformat()}`",
        "",
        "This is not a store ranking or a final judgment of value. It is a public experiment panel built from auditable repository and GitHub signals.",
        "",
        "Formula: `10 + freshness(max 30) + commits(max 20) + mentions(max 30) + votes(max 25)`.",
        "",
        "| Score | Skill | Author | Last activity | Commits | Mentions | Votes |",
        "| ---: | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for record in records:
        votes = f"+{record.vote_support}/-{record.vote_oppose}"
        last_activity = record.last_activity_at or "unknown"
        lines.append(
            f"| {record.impact_score} | [{record.title}](../{record.path}) | "
            f"{record.author or 'unknown'} | {last_activity} | {record.commit_count} | "
            f"{record.mention_count} | {votes} |"
        )
    OUTPUT_MARKDOWN.parent.mkdir(exist_ok=True)
    OUTPUT_MARKDOWN.write_text("\n".join(lines) + "\n", encoding="utf-8")


def readme_summary_block(records: list[SkillRecord], generated_at: datetime, language: str) -> str:
    top_records = records[:5]
    if language == "zh":
        lines = [
            README_ZH_START,
            "### 公开生命体征",
            "",
            f"最近生成：`{generated_at.isoformat()}`",
            "",
            "这不是商店排名，也不是最终价值裁判。它只是把公开、可审计的互动信号摆出来，方便创作者观察自己的 Skill 是否仍在被看见、讨论和触碰。",
            "",
            "| Score | Skill | Author | Mentions | Votes |",
            "| ---: | --- | --- | ---: | ---: |",
        ]
        empty = "暂无 Skill。"
        full_link = "完整面板见 [docs/impact.md](docs/impact.md)，机器可读索引见 [community/index.json](community/index.json)。"
    else:
        lines = [
            README_EN_START,
            "### Public Vitality Signals",
            "",
            f"Generated at: `{generated_at.isoformat()}`",
            "",
            "This is not a store ranking or a final judgment of value. It exposes public, auditable interaction signals so creators can see whether their Skills are still being noticed, discussed, or touched.",
            "",
            "| Score | Skill | Author | Mentions | Votes |",
            "| ---: | --- | --- | ---: | ---: |",
        ]
        empty = "No Skills yet."
        full_link = "Full panel: [docs/impact.md](docs/impact.md). Machine-readable index: [community/index.json](community/index.json)."

    if top_records:
        for record in top_records:
            votes = f"+{record.vote_support}/-{record.vote_oppose}"
            lines.append(
                f"| {record.impact_score} | [{record.title}]({record.path}) | "
                f"{record.author or 'unknown'} | {record.mention_count} | {votes} |"
            )
    else:
        lines.append(f"| - | {empty} | - | - | - |")
    lines.extend(["", full_link, "", README_ZH_END if language == "zh" else README_EN_END])
    return "\n".join(lines)


def replace_between_markers(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise ValueError(f"Missing README impact markers: {start} / {end}")
    return pattern.sub(replacement, text)


def update_readme_summary(records: list[SkillRecord], generated_at: datetime) -> None:
    replacements = [
        (README_ZH, README_ZH_START, README_ZH_END, readme_summary_block(records, generated_at, "zh")),
        (README_EN, README_EN_START, README_EN_END, readme_summary_block(records, generated_at, "en")),
    ]
    for path, start, end, block in replacements:
        text = path.read_text(encoding="utf-8")
        path.write_text(replace_between_markers(text, start, end, block) + "\n", encoding="utf-8")


def main() -> int:
    configure_logging()
    ensure_repo_dirs()
    parser = argparse.ArgumentParser(description="Generate public Skill impact signals.")
    parser.add_argument("--no-github", action="store_true", help="Skip GitHub Issue/PR interaction collection.")
    parser.add_argument("--no-commit", action="store_true", help="Generate files without committing or pushing.")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    repo = None if args.no_github else get_repo()
    records = build_records(now, repo=repo)
    write_json(records, now)
    write_markdown(records, now)
    update_readme_summary(records, now)
    logging.info("Generated impact signals for %s skills.", len(records))

    if not args.no_commit:
        commit_and_push("[Bot] Update skill impact signals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
