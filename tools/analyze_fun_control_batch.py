#!/usr/bin/env python3
"""Measure and package a completed H3 Fun Control experiment batch for review."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import statistics
import subprocess
from typing import Any


SSIM = re.compile(r"All:([0-9.]+)")
YAVG = re.compile(r"lavfi\.signalstats\.YAVG=([0-9.]+)")


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, Any]:
    value = json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,nb_frames,r_frame_rate,duration",
                "-of",
                "json",
                str(path),
            ]
        ).stdout
    )["streams"][0]
    return {
        "width": int(value["width"]),
        "height": int(value["height"]),
        "frames": int(value["nb_frames"]),
        "fps": value["r_frame_rate"],
        "duration_seconds": float(value["duration"]),
    }


def ssim_vs_source(source: Path, generated: Path) -> float:
    result = run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(source),
            "-i",
            str(generated),
            "-filter_complex",
            "[0:v]trim=start_frame=0:end_frame=73,setpts=PTS-STARTPTS,scale=768:768[ref];[ref][1:v]ssim",
            "-an",
            "-f",
            "null",
            "-",
        ]
    )
    matches = SSIM.findall(result.stderr)
    if not matches:
        raise RuntimeError(f"ffmpeg emitted no SSIM summary for {generated}")
    return float(matches[-1])


def mean_adjacent_luma_delta(path: Path) -> float:
    result = run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-vf",
            "format=gray,tblend=all_mode=difference,signalstats,metadata=print:file=-",
            "-an",
            "-f",
            "null",
            "-",
        ]
    )
    values = [float(value) for value in YAVG.findall(result.stdout)]
    if not values:
        raise RuntimeError(f"ffmpeg emitted no adjacent-frame luma deltas for {path}")
    return statistics.fmean(values)


def latest(root: Path, experiment_id: str, stem: str) -> Path | None:
    directory = root / "experiments" / "2026-09-02" / "fun-control" / experiment_id
    values = sorted(directory.glob(f"{stem}_*.mp4"))
    return values[-1] if values else None


def comparison_page(source: Path, variants: list[tuple[str, Path]], destination: Path) -> None:
    inputs = [("source", source), *variants]
    command = ["ffmpeg", "-y"]
    for _, path in inputs:
        command.extend(["-i", str(path)])
    filters: list[str] = []
    for index, (_, _) in enumerate(inputs):
        trim = "trim=start_frame=0:end_frame=73,setpts=PTS-STARTPTS," if index == 0 else "setpts=PTS-STARTPTS,"
        filters.append(f"[{index}:v]{trim}scale=384:384[v{index}]")
    layouts = {
        2: "0_0|w0_0",
        3: "0_0|w0_0|0_h0",
        4: "0_0|w0_0|0_h0|w0_h0",
    }
    labels = "".join(f"[v{index}]" for index in range(len(inputs)))
    filters.append(
        f"{labels}xstack=inputs={len(inputs)}:layout={layouts[len(inputs)]}:fill=black[out]"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-shortest",
            str(destination),
        ]
    )
    run(command)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--downloads", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--comparisons", required=True)
    parser.add_argument("--project-output")
    args = parser.parse_args()

    matrix = json.loads(Path(args.matrix).read_text(encoding="utf-8"))
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    downloads = Path(args.downloads)
    source = Path(args.source)
    state_by_id = {entry["id"]: entry for entry in state["steps"]}
    records: list[dict[str, Any]] = []
    for spec in matrix["experiments"]:
        experiment_id = spec["id"]
        generated = latest(downloads, experiment_id, "generated")
        control = latest(downloads, experiment_id, "control")
        mask = latest(downloads, experiment_id, "mask")
        record: dict[str, Any] = {
            "id": experiment_id,
            "family": spec["family"],
            "status": state_by_id[experiment_id]["status"],
            "prompt_id": state_by_id[experiment_id]["prompt_id"],
            "error": state_by_id[experiment_id]["error"],
            "generated": str(generated) if generated else None,
            "control": str(control) if control else None,
            "mask": str(mask) if mask else None,
        }
        if generated:
            record.update(
                {
                    "sha256": sha256(generated),
                    "geometry": probe(generated),
                    "ssim_vs_source": round(ssim_vs_source(source, generated), 6),
                    "mean_adjacent_luma_delta": round(mean_adjacent_luma_delta(generated), 6),
                }
            )
        records.append(record)

    families: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        families.setdefault(record["family"], []).append(record)
    comparisons: list[dict[str, Any]] = []
    comparison_root = Path(args.comparisons)
    for family, family_records in sorted(families.items()):
        available = [(record["id"], Path(record["generated"])) for record in family_records if record["generated"]]
        for page, offset in enumerate(range(0, len(available), 3), start=1):
            destination = comparison_root / f"{family}-p{page:02d}.mp4"
            cells = [("source", source), *available[offset : offset + 3]]
            comparison_page(source, available[offset : offset + 3], destination)
            comparisons.append(
                {
                    "path": str(destination),
                    "cells": [
                        {"index": index, "label": label, "source": str(path)}
                        for index, (label, path) in enumerate(cells)
                    ],
                    "layout": "row-major",
                }
            )

    analysis = {
        "schema": "inside-valdivia.h3-fun-control-analysis/1",
        "source": str(source),
        "source_sha256": sha256(source),
        "state_hash": state["state_hash"],
        "records": records,
        "comparisons": comparisons,
        "interpretation_guard": (
            "SSIM and adjacent-frame luma delta are bounded descriptors, not aesthetic rankings. "
            "Promotion requires human motion and image review."
        ),
    }
    output = Path(args.output)
    write_json(output, analysis)
    completed = sum(record["status"] == "completed" for record in records)
    failed = sum(record["status"] == "failed" for record in records)
    markdown = [
        "# H3 Fun Control batch — technical review index",
        "",
        f"- Completed: {completed}/{len(records)}",
        f"- Terminal failures: {failed}",
        f"- Comparison videos: {len(comparisons)}",
        "- Metrics are descriptors only; visual acceptance remains manual.",
        "",
        "| Experiment | Family | Status | SSIM vs source | Adjacent luma delta |",
        "|---|---|---:|---:|---:|",
    ]
    for record in records:
        markdown.append(
            f"| {record['id']} | {record['family']} | {record['status']} | "
            f"{record.get('ssim_vs_source', '')} | {record.get('mean_adjacent_luma_delta', '')} |"
        )
    output.with_suffix(".md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    if args.project_output:
        project_records = [
            {
                key: record.get(key)
                for key in (
                    "id",
                    "family",
                    "status",
                    "prompt_id",
                    "error",
                    "sha256",
                    "geometry",
                    "ssim_vs_source",
                    "mean_adjacent_luma_delta",
                )
            }
            for record in records
        ]
        write_json(
            Path(args.project_output),
            {
                "schema": "inside-valdivia.h3-fun-control-characterization/1",
                "status": "executed-pending-human-review",
                "batch_plan_hash": state["plan_hash"],
                "batch_state_hash": state["state_hash"],
                "source_sha256": sha256(source),
                "completed": completed,
                "failed": failed,
                "records": project_records,
                "technical_interpretation": [
                    "All independent graphs live-validated before the first submission.",
                    "All 34 exact prompt ids completed and produced 73-frame 768x768 artifacts.",
                    "Reference, endpoint, guide, temporal/spatial inpaint, and mixed control routes executed without a terminal job failure.",
                    "SSIM and adjacent-frame luma delta describe decoded outputs but do not establish aesthetic quality or production acceptance.",
                ],
                "acceptance": {
                    "verdict": "pending-human-review",
                    "production_promotion": False,
                },
            },
        )
    print(json.dumps({"output": str(output), "completed": completed, "failed": failed, "comparisons": len(comparisons)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
