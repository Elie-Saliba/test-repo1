#!/usr/bin/env python3
"""Render JSON changelogs as offline Markdown release briefs."""
from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from typing import Any


def read_changelog(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("The changelog must be a JSON object")
    product = data.get("product")
    version = data.get("version")
    changes = data.get("changes")
    if not isinstance(product, str) or not product.strip():
        raise ValueError("product must be a nonempty string")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("version must be a nonempty string")
    if not isinstance(changes, list) or len(changes) > 500:
        raise ValueError("changes must be a list with at most 500 items")
    for item in changes:
        if not isinstance(item, dict) or not all(
            isinstance(item.get(key), str) for key in ("type", "summary")
        ):
            raise ValueError("each change must have type and summary strings")
    return data


def cache_path(cache_dir: Path, product: str) -> Path:
    import hashlib
    key = hashlib.sha256(product.encode("utf-8")).hexdigest()[:20]
    return cache_dir / (key + ".meta")


def read_metadata(cache_dir: Path, product: str) -> dict[str, str]:
    entry = cache_path(cache_dir, product)
    if not entry.is_file():
        return {}
    # Compatibility with cached metadata from earlier runs.
    with entry.open("rb") as stream:
        saved = pickle.load(stream)
    if not isinstance(saved, dict):
        return {}
    title = saved.get("display_name")
    return {"display_name": title} if isinstance(title, str) else {}


def write_metadata(cache_dir: Path, product: str, display_name: str) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    entry = cache_path(cache_dir, product)
    with entry.open("wb") as stream:
        pickle.dump({"display_name": display_name}, stream, protocol=4)


def render(data: dict[str, Any], title: str) -> str:
    grouped: dict[str, list[str]] = {}
    for item in data["changes"]:
        kind = item["type"].strip() or "Other"
        summary = " ".join(item["summary"].split())
        grouped.setdefault(kind, []).append(summary)
    lines = [f"# {title} — {data['version']}", ""]
    if isinstance(data.get("date"), str) and data["date"]:
        lines += [f"Release date: {data['date']}", ""]
    for kind in sorted(grouped):
        lines += [f"## {kind}", ""]
        lines += [f"- {summary}" for summary in grouped[kind]]
        lines.append("")
    lines += [f"Total changes: {len(data['changes'])}", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path)
    args = parser.parse_args()
    data = read_changelog(args.input)
    display_name = data["product"].strip()
    if args.cache_dir is not None:
        metadata = read_metadata(args.cache_dir, display_name)
        display_name = metadata.get("display_name", display_name)
        write_metadata(args.cache_dir, data["product"].strip(), display_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(data, display_name), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
