#!/usr/bin/env python3
"""Build a fixed-input MiniMax H3 Fun Control characterization matrix."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any


WIDTH = 768
HEIGHT = 768
FRAMES = 73
FPS = 24
SEED = 20260902
STEPS = 20
SOURCE_VIDEO = "Gen-4_5.gen-4_5 (5).mp4"
REFERENCE_A = "inside-valdivia-frame-a.png"
REFERENCE_B = "inside-valdivia-frame-b.png"
CLIP_MODEL = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VIDEO_VAE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE = "minimax_h3_audio_vae_fp32.safetensors"
FL2VA_MODEL = "minimax_h3_fl2va_pruned_int8_convrot.safetensors"
REF2VA_MODEL = "minimax_h3_ref2va_pruned_int8_convrot.safetensors"
FUN_PATCH = "minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors"

BASE_PROMPT = (
    "One continuous accelerating camera flight through a dense southern temperate "
    "rainforest, rotating smoothly around the vertical axis while moving forward. "
    "Preserve the circular domemaster projection, black exterior, forest structure, "
    "spatial rhythm, and camera path. One uninterrupted shot, no cuts, no text, silent."
)


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self._next = 1

    def add(self, class_type: str, **inputs: Any) -> str:
        node_id = str(self._next)
        self._next += 1
        self.nodes[node_id] = {"class_type": class_type, "inputs": inputs}
        return node_id

    @staticmethod
    def link(node_id: str, output: int = 0) -> list[Any]:
        return [node_id, output]


def _loaders(graph: Graph, *, reference: bool) -> dict[str, str]:
    clip = graph.add("CLIPLoader", clip_name=CLIP_MODEL, type="minimax", device="default")
    vae = graph.add("VAELoader", vae_name=VIDEO_VAE)
    audio_vae = graph.add("VAELoader", vae_name=AUDIO_VAE) if reference else ""
    model = graph.add(
        "UNETLoader",
        unet_name=REF2VA_MODEL if reference else FL2VA_MODEL,
        weight_dtype="default",
    )
    patch = graph.add("ModelPatchLoader", name=FUN_PATCH)
    return {"clip": clip, "vae": vae, "audio_vae": audio_vae, "model": model, "patch": patch}


def _source(graph: Graph) -> dict[str, str]:
    video = graph.add("LoadVideo", file=SOURCE_VIDEO)
    cropped = graph.add("VideoTemporalCrop", video=graph.link(video), start_frame=0, length=FRAMES)
    components = graph.add("GetVideoComponents", video=graph.link(cropped))
    frames = graph.add(
        "ImageScale",
        image=graph.link(components),
        upscale_method="lanczos",
        width=WIDTH,
        height=HEIGHT,
        crop="center",
    )
    first = graph.add("ImageFromBatch", image=graph.link(frames), batch_index=0, length=1)
    middle = graph.add("ImageFromBatch", image=graph.link(frames), batch_index=36, length=1)
    last = graph.add("ImageFromBatch", image=graph.link(frames), batch_index=72, length=1)
    return {"frames": frames, "first": first, "middle": middle, "last": last}


def _canny(graph: Graph, frames: str, *, low: float = 0.2, high: float = 0.5) -> str:
    return graph.add(
        "Canny",
        image=graph.link(frames),
        low_threshold=low,
        high_threshold=high,
    )


def _depth(graph: Graph, frames: str) -> str:
    model = graph.add(
        "LoadDA3Model",
        model_name="depth_anything_3_mono_large.safetensors",
        weight_dtype="default",
    )
    inference = graph.add(
        "DA3Inference",
        da3_model=graph.link(model),
        image=graph.link(frames),
        resolution=392,
        resize_method="upper_bound_resize",
        mode="mono",
    )
    return graph.add(
        "DA3Render",
        da3_geometry=graph.link(inference),
        output="depth",
        **{"output.normalization": "v2_style", "output.apply_sky_clip": False},
    )


def _control_carrier(graph: Graph, frames: str, spec: dict[str, Any]) -> str:
    kind = spec["kind"]
    if kind == "canny":
        return _canny(graph, frames, low=spec.get("low", 0.2), high=spec.get("high", 0.5))
    if kind == "depth":
        return _depth(graph, frames)
    if kind == "canny-envelope":
        canny = _canny(graph, frames)
        mask = graph.add(
            "CreateFadeMaskAdvanced",
            points_string=spec["points"],
            invert=False,
            frames=FRAMES,
            width=WIDTH,
            height=HEIGHT,
            interpolation=spec.get("interpolation", "ease_in_out"),
        )
        black = graph.add("EmptyImage", width=WIDTH, height=HEIGHT, batch_size=FRAMES, color=0)
        return graph.add(
            "ImageCompositeMasked",
            destination=graph.link(black),
            source=graph.link(canny),
            x=0,
            y=0,
            resize_source=False,
            mask=graph.link(mask),
        )
    if kind == "hybrid":
        canny = _canny(graph, frames)
        depth = _depth(graph, frames)
        mask = graph.add(
            "CreateFadeMaskAdvanced",
            points_string="0:(0.0),\n72:(1.0)",
            invert=False,
            frames=FRAMES,
            width=WIDTH,
            height=HEIGHT,
            interpolation="ease_in_out",
        )
        destination, source = (depth, canny) if spec["direction"] == "depth-to-canny" else (canny, depth)
        return graph.add(
            "ImageCompositeMasked",
            destination=graph.link(destination),
            source=graph.link(source),
            x=0,
            y=0,
            resize_source=False,
            mask=graph.link(mask),
        )
    raise ValueError(f"unknown control carrier {kind!r}")


def _mask(graph: Graph, kind: str) -> str:
    if kind == "temporal-middle":
        return graph.add(
            "CreateFadeMaskAdvanced",
            points_string="0:(0.0),\n23:(0.0),\n24:(1.0),\n48:(1.0),\n49:(0.0),\n72:(0.0)",
            invert=False,
            frames=FRAMES,
            width=WIDTH,
            height=HEIGHT,
            interpolation="none",
        )
    if kind == "spatial-center":
        return graph.add(
            "CreateShapeMask",
            shape="circle",
            frames=FRAMES,
            location_x=WIDTH // 2,
            location_y=HEIGHT // 2,
            grow=0,
            frame_width=WIDTH,
            frame_height=HEIGHT,
            shape_width=384,
            shape_height=384,
        )
    raise ValueError(f"unknown mask kind {kind!r}")


def _conditioning(
    graph: Graph,
    loaders: dict[str, str],
    source: dict[str, str],
    spec: dict[str, Any],
) -> tuple[str, str]:
    generator = spec.get("generator", "fl2va")
    if generator == "ref2va":
        refs = spec.get("references", [REFERENCE_A])
        inputs: dict[str, Any] = {
            "clip": graph.link(loaders["clip"]),
            "vae": graph.link(loaders["vae"]),
            "audio_vae": graph.link(loaders["audio_vae"]),
            "prompt": spec.get("prompt") or _reference_prompt(len(refs)),
            "width": WIDTH,
            "height": HEIGHT,
            "length": FRAMES,
            "ref_image_size": spec.get("ref_image_size", "match"),
        }
        for index, filename in enumerate(refs):
            image = graph.add("LoadImage", image=filename)
            inputs[f"ref_images.ref_image_{index}"] = graph.link(image)
        base = graph.add("MiniMaxH3ReferenceToVideo", **inputs)
    else:
        inputs = {
            "clip": graph.link(loaders["clip"]),
            "vae": graph.link(loaders["vae"]),
            "prompt": spec.get("prompt", BASE_PROMPT),
            "width": WIDTH,
            "height": HEIGHT,
            "length": FRAMES,
        }
        first_mode = spec.get("first", "source")
        if first_mode == "source":
            inputs["first_frame"] = graph.link(source["first"])
        elif first_mode == "reference-a":
            image = graph.add("LoadImage", image=REFERENCE_A)
            scaled = graph.add(
                "ImageScale",
                image=graph.link(image),
                upscale_method="lanczos",
                width=WIDTH,
                height=HEIGHT,
                crop="center",
            )
            inputs["first_frame"] = graph.link(scaled)
        elif first_mode != "none":
            raise ValueError(f"unknown first mode {first_mode!r}")
        if spec.get("last") == "source":
            inputs["last_frame"] = graph.link(source["last"])
        base = graph.add("MiniMaxH3ImageToVideo", **inputs)

    positive = base
    if spec.get("guide"):
        guide_spec = spec["guide"]
        image = source["middle"]
        if guide_spec["image"] == "reference-a":
            image = graph.add("LoadImage", image=REFERENCE_A)
        elif guide_spec["image"] == "reference-b":
            image = graph.add("LoadImage", image=REFERENCE_B)
        positive = graph.add(
            "MiniMaxH3AddGuide",
            positive=graph.link(base),
            latent=graph.link(base, 1),
            frame_idx=guide_spec.get("frame_idx", 36),
            vae=graph.link(loaders["vae"]),
            image=graph.link(image),
        )
    return positive, base


def _reference_prompt(count: int) -> str:
    tags = " and ".join(f"<Picture {index}>" for index in range(1, count + 1))
    return (
        f"Use {tags} as visual appearance and spatial-identity references while following "
        "the camera movement and geometry carried by the control video. Maintain one coherent "
        "continuous southern temperate rainforest and circular domemaster projection. "
        "One uninterrupted shot, no cuts, no text, silent."
    )


def build_graph(spec: dict[str, Any]) -> dict[str, Any]:
    graph = Graph()
    reference = spec.get("generator") == "ref2va"
    loaders = _loaders(graph, reference=reference)
    source = _source(graph)
    control = None
    if spec.get("control"):
        control = _control_carrier(graph, source["frames"], spec["control"])
    mask = _mask(graph, spec["mask"]) if spec.get("mask") else None
    positive, latent = _conditioning(graph, loaders, source, spec)

    patch_inputs: dict[str, Any] = {
        "model": graph.link(loaders["model"]),
        "model_patch": graph.link(loaders["patch"]),
        "vae": graph.link(loaders["vae"]),
        "strength": spec.get("strength", 1.0),
        "start_percent": spec.get("start_percent", 0.0),
        "end_percent": spec.get("end_percent", 1.0),
    }
    if control:
        patch_inputs["control_video"] = graph.link(control)
    if mask:
        patch_inputs["mask"] = graph.link(mask)
        patch_inputs["source_video"] = graph.link(source["frames"])
    patched_model = graph.add("MiniMaxH3FunControlNetApply", **patch_inputs)

    noise = graph.add("RandomNoise", noise_seed=SEED)
    guider = graph.add(
        "BasicGuider",
        model=graph.link(patched_model),
        conditioning=graph.link(positive),
    )
    scheduler = graph.add(
        "BasicScheduler",
        model=graph.link(patched_model),
        scheduler="simple",
        steps=STEPS,
        denoise=1.0,
    )
    sampler = graph.add("KSamplerSelect", sampler_name="res_multistep")
    sampled = graph.add(
        "SamplerCustomAdvanced",
        noise=graph.link(noise),
        guider=graph.link(guider),
        sampler=graph.link(sampler),
        sigmas=graph.link(scheduler),
        latent_image=graph.link(latent, 1),
    )
    decoded = graph.add("VAEDecode", samples=graph.link(sampled, 1), vae=graph.link(loaders["vae"]))
    video = graph.add("CreateVideo", images=graph.link(decoded), fps=FPS)
    prefix = f"experiments/2026-09-02/fun-control/{spec['id']}"
    graph.add("SaveVideo", video=graph.link(video), filename_prefix=f"{prefix}/generated", format="auto")

    if control:
        preview = graph.add("CreateVideo", images=graph.link(control), fps=FPS)
        graph.add("SaveVideo", video=graph.link(preview), filename_prefix=f"{prefix}/control", format="auto")
    if mask:
        mask_image = graph.add("MaskToImage", mask=graph.link(mask))
        preview = graph.add("CreateVideo", images=graph.link(mask_image), fps=FPS)
        graph.add("SaveVideo", video=graph.link(preview), filename_prefix=f"{prefix}/mask", format="auto")
    return graph.nodes


def experiment_specs() -> list[dict[str, Any]]:
    canny = {"kind": "canny"}
    depth = {"kind": "depth"}
    specs: list[dict[str, Any]] = []

    for strength in (0.25, 0.5, 0.75, 1.25, 1.5):
        specs.append(
            {
                "id": f"canny-strength-{str(strength).replace('.', '')}",
                "family": "strength",
                "control": canny,
                "strength": strength,
            }
        )
    specs.extend(
        [
            {"id": "canny-stage-early", "family": "diffusion-window", "control": canny, "end_percent": 0.35},
            {"id": "canny-stage-earlymid", "family": "diffusion-window", "control": canny, "end_percent": 0.65},
            {"id": "canny-stage-late", "family": "diffusion-window", "control": canny, "start_percent": 0.35},
            {"id": "canny-stage-middle", "family": "diffusion-window", "control": canny, "start_percent": 0.2, "end_percent": 0.8},
            {"id": "canny-dense", "family": "carrier", "control": {"kind": "canny", "low": 0.1, "high": 0.3}},
            {"id": "canny-sparse", "family": "carrier", "control": {"kind": "canny", "low": 0.3, "high": 0.7}},
            {"id": "depth-strength-05", "family": "carrier", "control": depth, "strength": 0.5},
            {"id": "depth-strength-075", "family": "carrier", "control": depth, "strength": 0.75},
            {
                "id": "canny-envelope-midpulse",
                "family": "temporal-envelope",
                "control": {
                    "kind": "canny-envelope",
                    "points": "0:(0.0),\n18:(0.0),\n36:(1.0),\n54:(0.0),\n72:(0.0)",
                },
            },
            {
                "id": "canny-envelope-rampin",
                "family": "temporal-envelope",
                "control": {"kind": "canny-envelope", "points": "0:(0.0),\n72:(1.0)"},
            },
            {
                "id": "hybrid-depth-to-canny",
                "family": "carrier-interpolation",
                "control": {"kind": "hybrid", "direction": "depth-to-canny"},
            },
            {
                "id": "hybrid-canny-to-depth",
                "family": "carrier-interpolation",
                "control": {"kind": "hybrid", "direction": "canny-to-depth"},
            },
        ]
    )

    for strength in (0.5, 0.75, 1.0):
        specs.append(
            {
                "id": f"ref-a-canny-{str(strength).replace('.', '')}",
                "family": "reference-control",
                "generator": "ref2va",
                "references": [REFERENCE_A],
                "control": canny,
                "strength": strength,
            }
        )
    specs.extend(
        [
            {"id": "ref-a-depth-075", "family": "reference-control", "generator": "ref2va", "references": [REFERENCE_A], "control": depth, "strength": 0.75},
            {"id": "ref-ab-canny-075", "family": "reference-control", "generator": "ref2va", "references": [REFERENCE_A, REFERENCE_B], "control": canny, "strength": 0.75},
            {"id": "ref-a-max-canny-075", "family": "reference-fidelity", "generator": "ref2va", "references": [REFERENCE_A], "ref_image_size": "max", "control": canny, "strength": 0.75},
            {"id": "fl-firstlast-canny-075", "family": "endpoint-control", "last": "source", "control": canny, "strength": 0.75},
            {"id": "fl-externalfirst-canny-075", "family": "endpoint-control", "first": "reference-a", "control": canny, "strength": 0.75},
            {"id": "fl-firstlast-depth-075", "family": "endpoint-control", "last": "source", "control": depth, "strength": 0.75},
            {"id": "fl-guide-source-canny-075", "family": "guide-control", "guide": {"image": "source-middle", "frame_idx": 36}, "control": canny, "strength": 0.75},
            {"id": "fl-guide-refa-canny-075", "family": "guide-control", "guide": {"image": "reference-a", "frame_idx": 36}, "control": canny, "strength": 0.75},
            {"id": "ref-a-guide-b-canny-075", "family": "reference-guide-control", "generator": "ref2va", "references": [REFERENCE_A], "guide": {"image": "reference-b", "frame_idx": 36}, "control": canny, "strength": 0.75},
            {"id": "inpaint-temporal", "family": "inpaint", "mask": "temporal-middle"},
            {"id": "inpaint-temporal-canny-075", "family": "inpaint-control", "mask": "temporal-middle", "control": canny, "strength": 0.75},
            {"id": "inpaint-spatial", "family": "inpaint", "mask": "spatial-center"},
            {"id": "inpaint-spatial-canny-075", "family": "inpaint-control", "mask": "spatial-center", "control": canny, "strength": 0.75},
            {"id": "ref-a-inpaint-temporal-canny-075", "family": "reference-inpaint-control", "generator": "ref2va", "references": [REFERENCE_A], "mask": "temporal-middle", "control": canny, "strength": 0.75},
        ]
    )
    return specs


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="experiments/workflows/fun-control-2026-09-02",
        help="output directory relative to the repository",
    )
    args = parser.parse_args()
    root = Path(args.output)
    graphs = root / "graphs"
    operation_ref = {
        "schema": "inside-valdivia.operation-ref/1",
        "id": "generate.with_control",
        "version": 1,
        "contract_hash": "54420901a719ea708848ff24c8c61c0268fa578cfc14c498064aba49687a69fd",
    }
    write_json(root / "operation-ref.json", operation_ref)

    specs = experiment_specs()
    steps = []
    for spec in specs:
        graph_path = graphs / f"{spec['id']}.api.json"
        write_json(graph_path, build_graph(deepcopy(spec)))
        steps.append(
            {
                "id": spec["id"],
                "graph": f"graphs/{spec['id']}.api.json",
                "operation_ref": "operation-ref.json",
            }
        )
    write_json(root / "batch-plan.json", {"schema": "comfy.run-batch/1", "id": "h3-fun-control-20260902", "steps": steps})
    write_json(
        root / "matrix.json",
        {
            "schema": "inside-valdivia.h3-fun-control-matrix/1",
            "status": "planned",
            "held_constant": {
                "source_video": SOURCE_VIDEO,
                "source_window": [0, FRAMES],
                "dimensions": [WIDTH, HEIGHT],
                "fps": FPS,
                "seed": SEED,
                "steps": STEPS,
                "scheduler": "simple",
                "sampler": "res_multistep",
                "prompt": BASE_PROMPT,
            },
            "previous_fixed_baselines": [
                "workflows/evaluations/2026-09-02/fun-control-canny-quality20.api.json",
                "workflows/evaluations/2026-09-02/fun-control-depth-quality20.api.json",
            ],
            "experiments": specs,
        },
    )
    print(json.dumps({"output": str(root), "experiment_count": len(specs)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
