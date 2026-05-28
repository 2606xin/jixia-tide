from __future__ import annotations

import argparse
import logging
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from github import GithubException

from common import commit_and_push, configure_logging, ensure_repo_dirs, get_repo


def legacy_files() -> list[Path]:
    legacy = Path("legacy")
    return [path for path in legacy.rglob("*") if path.is_file() and path.name != ".gitkeep"]


def make_archive(year: int, files: list[Path]) -> Path:
    output_dir = Path(os.environ.get("RUNNER_TEMP", ".")).resolve() / "jixia-archives"
    output_dir.mkdir(exist_ok=True)
    archive_path = output_dir / f"Archive_{year}.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.as_posix())
            logging.info("Packed %s", path)
    return archive_path


def create_release(year: int, archive_path: Path) -> None:
    repo = get_repo()
    tag = f"archive-{year}"
    name = f"Jixia Guanlan Legacy Archive {year}"
    body = f"Automated annual archive for legacy skills in {year}."
    try:
        release = repo.get_release(tag)
        logging.info("Release %s already exists; uploading/replacing asset if needed.", tag)
    except GithubException:
        release = repo.create_git_release(tag=tag, name=name, message=body)
        logging.info("Created release %s", tag)

    for asset in release.get_assets():
        if asset.name == archive_path.name:
            logging.info("Deleting existing asset %s before replacement.", asset.name)
            asset.delete_asset()
    release.upload_asset(str(archive_path), name=archive_path.name, label=archive_path.name)
    logging.info("Uploaded archive asset %s", archive_path)


def clear_legacy(files: list[Path]) -> None:
    for path in files:
        path.unlink()
        logging.info("Removed %s", path)
    keep = Path("legacy/.gitkeep")
    keep.parent.mkdir(exist_ok=True)
    keep.touch()


def main() -> int:
    configure_logging()
    ensure_repo_dirs()
    parser = argparse.ArgumentParser(description="Create annual legacy archive release.")
    parser.add_argument("--year", type=int, default=datetime.now(timezone.utc).year)
    args = parser.parse_args()

    files = legacy_files()
    if not files:
        logging.info("No legacy files to archive.")
        return 0

    archive_path = make_archive(args.year, files)
    create_release(args.year, archive_path)
    clear_legacy(files)
    commit_and_push(f"[Bot] Clear legacy after archive release: {args.year}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
