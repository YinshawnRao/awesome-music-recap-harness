#!/usr/bin/env python3
"""PROJECT CONTRACT gate — structure first, media optional.

New projects use authoring schema v2. project_kind is one of:
top_ranking | narrative | free_exploration.

Default mode checks JSON structure, TOP N→1, spoiler rules, dual-platform
search declarations, narration roles, and the canonical CTA. Pass
--require-media to also demand clips, WAVs, and hash-bound receipts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from outro_cta import FIXED_OUTRO_CTA
except ImportError:  # python -m / package import
    from tools.video.outro_cta import FIXED_OUTRO_CTA

META_SPOILER = re.compile(
    r"05\s*→\s*01|05\s*->\s*01|N\s*→\s*1|倒数开始|从第\s*\d+\s*名开始"
)
INTRO_FORBIDDEN = "接下来"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("manifest must be a JSON object")
    return value


def _roles(sequence: list[dict]) -> list[str]:
    return [item.get("role") for item in sequence]


def verify_project(
    project: Path,
    manifest_name: str = "project-manifest.json",
    *,
    require_media: bool = False,
) -> list[str]:
    errors: list[str] = []
    root = project.resolve()
    manifest_path = root / manifest_name
    if not manifest_path.is_file():
        return [f"missing {manifest_name}"]
    try:
        manifest = _load(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"manifest unreadable: {exc}"]

    if manifest.get("schema_version") != 2:
        errors.append("schema_version must be 2 for new projects")
    kind = manifest.get("project_kind")
    if kind not in {"top_ranking", "narrative", "free_exploration"}:
        errors.append("project_kind must be top_ranking, narrative, or free_exploration")
    if kind == "free_exploration" and not str(manifest.get("rationale") or "").strip():
        errors.append("free_exploration requires a non-empty rationale")

    voice_selection = manifest.get("voice_selection")
    if not isinstance(voice_selection, str) or not voice_selection:
        errors.append("voice_selection path is required")
    elif not (root / voice_selection).is_file():
        errors.append(f"voice-selection file missing: {voice_selection}")

    cover = manifest.get("cover") or {}
    cover_text = cover.get("text") if isinstance(cover, dict) else ""
    disclosed = cover.get("disclosed_item_ids") if isinstance(cover, dict) else None
    if not isinstance(cover_text, str) or not cover_text.strip():
        errors.append("cover.text is required")
    if kind == "top_ranking":
        if disclosed:
            errors.append("top_ranking cover must not disclose item ids")
        if isinstance(cover_text, str) and META_SPOILER.search(cover_text):
            errors.append("cover text must not describe the N→1 mechanism")

    items = manifest.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items must be a non-empty array")
        items = []
    ranks: list[int] = []
    titles: dict[str, str] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"items[{index}] must be an object")
            continue
        item_id = item.get("id")
        if not item_id:
            errors.append(f"items[{index}] missing id")
        titles[str(item_id)] = str(item.get("title") or "")
        if kind == "top_ranking":
            rank = item.get("rank")
            if type(rank) is not int:
                errors.append(f"items[{index}] rank is required for top_ranking")
            else:
                ranks.append(rank)
        elif "rank" in item:
            errors.append(f"items[{index}] must not have rank unless project_kind is top_ranking")
        sources = item.get("sources") or {}
        platforms = sources.get("platforms") or {}
        for platform in ("youtube", "bilibili"):
            block = platforms.get(platform)
            if not isinstance(block, dict) or block.get("searched") is not True:
                errors.append(f"items[{index}] {platform} must be searched")
            elif not block.get("search_queries"):
                errors.append(f"items[{index}] {platform} search_queries is empty")
        selection = sources.get("selection") or {}
        if not selection.get("url") or not selection.get("decision_reason"):
            errors.append(f"items[{index}] selection url/decision_reason required")
        if require_media:
            clip = item.get("clip")
            if not clip or not (root / clip).is_file():
                errors.append(f"items[{index}] clip missing on disk")

    if kind == "top_ranking" and ranks:
        expected = list(range(max(ranks), 0, -1))
        if ranks != expected:
            errors.append(
                f"top_ranking items must be listed N→1 playback order; got ranks {ranks}"
            )

    sequence = manifest.get("narration_sequence")
    if not isinstance(sequence, list) or not sequence:
        errors.append("narration_sequence is required")
        sequence = []
    roles = _roles(sequence)
    if kind in {"top_ranking", "narrative"}:
        if not roles or roles[0] != "intro":
            errors.append("structured projects must start narration with intro")
        if "work_outro" not in roles:
            errors.append("structured projects need a work_outro")
        if roles[-1] != "outro_cta":
            errors.append("last narration role must be outro_cta")
        if kind == "top_ranking" and roles.count("transition") != len(items):
            errors.append("top_ranking needs one transition narration per item")
    for block in sequence:
        if not isinstance(block, dict):
            continue
        text = str(block.get("text") or "")
        if block.get("role") == "intro":
            if INTRO_FORBIDDEN in text:
                errors.append("intro text must not contain 接下来")
            if kind == "top_ranking" and any(
                title and title in text for title in titles.values()
            ):
                errors.append("intro must not reveal song titles")
            if kind == "top_ranking" and META_SPOILER.search(text):
                errors.append("intro must not describe the N→1 mechanism")
        if block.get("role") == "outro_cta" and text != FIXED_OUTRO_CTA:
            errors.append("outro_cta text must match tools/video/outro_cta.py::FIXED_OUTRO_CTA")
        sidecar = block.get("sidecar")
        wav = block.get("wav")
        if sidecar and not (root / sidecar).is_file():
            errors.append(f"sidecar missing: {sidecar}")
        if require_media and wav and not (root / wav).is_file():
            errors.append(f"wav missing: {wav}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--manifest", default="project-manifest.json")
    parser.add_argument(
        "--require-media",
        action="store_true",
        help="also require clips, WAVs, and on-disk evidence",
    )
    args = parser.parse_args()
    errors = verify_project(args.project, args.manifest, require_media=args.require_media)
    if errors:
        print("PROJECT CONTRACT: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    mode = "media" if args.require_media else "structure"
    print(f"PROJECT CONTRACT: PASS mode={mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
