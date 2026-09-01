#!/usr/bin/env python3
"""Build exact H3 dense-AddGuide temporal-expansion graphs.

Each retained source frame becomes an independent official
``MiniMaxH3AddGuide`` at a factor-spaced target index. H3 generates the gaps;
the delivery clock remains 24 fps, so the factor expands duration instead of
changing playback metadata.

Native visual-token dilation is intentionally absent. Live 2x and 3x tests ran
successfully but failed visual review as slow motion: H3 treated the dilated
state as a regenerative trajectory rather than a dense set of temporal
observations. The exact rejected graphs remain under the experiment directory
for evidence, but this builder cannot accidentally rematerialize them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments" / "workflows" / "temporal-expansion-2026-08-31"
SOURCE_LATENT = "cauce/latents/2026-08-31/03_fl2va_first_a_last_b_00001.safetensors"
CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
VAE = "minimax_h3_video_vae_fp16.safetensors"
MODEL = "minimax_h3_fl2va_pruned_fp8_scaled.safetensors"
PROMPT = (
    "Generate a single continuous slow-motion trajectory through the supplied "
    "temporally ordered visual anchors. Preserve the subjects, scene geometry, "
    "camera path, lighting, exposure, textures, motion direction and causal "
    "continuity. Generate coherent motion only between the anchors. No cuts, "
    "resets, duplicated gestures, temporal echoes, morphing, new objects, text "
    "or generated audio."
)


def legal_h3_frames(requested: int) -> int:
    resolved = max(5, int(requested))
    while resolved % 17 != 5:
        resolved += 1
    return resolved


def common_loaders(width: int, height: int, length: int) -> dict[str, dict]:
    return {
        "1": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"},
        },
        "2": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "3": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
        },
        "4": {
            "class_type": "CauceLoadAVLatent",
            "inputs": {"path_or_folder": SOURCE_LATENT, "artifact_index": 0},
        },
        "6": {
            "class_type": "MiniMaxH3ImageToVideo",
            "inputs": {
                "clip": ["1", 0],
                "vae": ["2", 0],
                "prompt": PROMPT,
                "width": width,
                "height": height,
                "length": length,
            },
        },
    }


def addguide_graph(factor: int) -> dict[str, dict]:
    source_frames = {2: 60, 3: 40, 4: 30}[factor]
    delivery_frames = (source_frames - 1) * factor + 1
    target_frames = legal_h3_frames(delivery_frames)
    graph = common_loaders(896, 512, target_frames)
    graph["5"] = {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["2", 0]}}

    previous = ["6", 0]
    for source_index in range(source_frames):
        select_id = str(20 + source_index * 2)
        guide_id = str(21 + source_index * 2)
        graph[select_id] = {
            "class_type": "CauceAcceptDecodedRange",
            "inputs": {"images": ["5", 0], "start_frame": source_index, "frame_count": 1},
        }
        graph[guide_id] = {
            "class_type": "MiniMaxH3AddGuide",
            "inputs": {
                "positive": previous,
                "vae": ["2", 0],
                "latent": ["6", 1],
                "image": [select_id, 0],
                "frame_idx": source_index * factor,
            },
        }
        previous = [guide_id, 0]

    graph.update(
        {
            "200": {"class_type": "RandomNoise", "inputs": {"noise_seed": 310900 + factor}},
            "201": {
                "class_type": "BasicGuider",
                "inputs": {"model": ["3", 0], "conditioning": previous},
            },
            "202": {
                "class_type": "BasicScheduler",
                "inputs": {"model": ["3", 0], "scheduler": "simple", "steps": 20, "denoise": 1.0},
            },
            "203": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "res_multistep"}},
            "204": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["200", 0],
                    "guider": ["201", 0],
                    "sampler": ["203", 0],
                    "sigmas": ["202", 0],
                    "latent_image": ["6", 1],
                },
            },
            "205": {
                "class_type": "CauceSaveAVLatent",
                "inputs": {
                    "latent": ["204", 0],
                    "filename_prefix": f"cauce/latents/2026-08-31/addguide_slowmo_{factor}x",
                    "artifact_index": factor,
                },
            },
            "206": {"class_type": "VAEDecode", "inputs": {"samples": ["204", 0], "vae": ["2", 0]}},
            "207": {
                "class_type": "CauceAcceptDecodedRange",
                "inputs": {"images": ["206", 0], "start_frame": 0, "frame_count": delivery_frames},
            },
            "208": {"class_type": "CreateVideo", "inputs": {"images": ["207", 0], "fps": 24, "bit_depth": 8}},
            "209": {
                "class_type": "SaveVideo",
                "inputs": {
                    "video": ["208", 0],
                    "filename_prefix": f"video/2026-08-31/addguide_slowmo_{factor}x",
                    "format": "auto",
                    "codec": "auto",
                },
            },
        }
    )
    return graph


def addguide_video_graph(
    *,
    factor: int,
    source_start: int,
    input_file: str,
    width: int,
    height: int,
    output_label: str,
    source_stride: int = 1,
) -> dict[str, dict]:
    source_frames = {2: 60, 3: 40, 4: 30}[factor]
    delivery_frames = (source_frames - 1) * factor + 1
    target_frames = legal_h3_frames(delivery_frames)
    graph = {
        "1": {
            "class_type": "CLIPLoader",
            "inputs": {"clip_name": CLIP, "type": "minimax", "device": "default"},
        },
        "2": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "3": {
            "class_type": "UNETLoader",
            "inputs": {"unet_name": MODEL, "weight_dtype": "default"},
        },
        "4": {"class_type": "LoadVideo", "inputs": {"file": input_file}},
        "5": {"class_type": "GetVideoComponents", "inputs": {"video": ["4", 0]}},
        "6": {
            "class_type": "MiniMaxH3ImageToVideo",
            "inputs": {
                "clip": ["1", 0],
                "vae": ["2", 0],
                "prompt": PROMPT,
                "width": width,
                "height": height,
                "length": target_frames,
            },
        },
    }

    source_offsets = list(range(0, source_frames, source_stride))
    if source_offsets[-1] != source_frames - 1:
        source_offsets.append(source_frames - 1)

    previous = ["6", 0]
    for guide_ordinal, source_offset in enumerate(source_offsets):
        select_id = str(20 + guide_ordinal * 2)
        guide_id = str(21 + guide_ordinal * 2)
        graph[select_id] = {
            "class_type": "CauceAcceptDecodedRange",
            "inputs": {
                "images": ["5", 0],
                "start_frame": source_start + source_offset,
                "frame_count": 1,
            },
        }
        graph[guide_id] = {
            "class_type": "MiniMaxH3AddGuide",
            "inputs": {
                "positive": previous,
                "vae": ["2", 0],
                "latent": ["6", 1],
                "image": [select_id, 0],
                "frame_idx": source_offset * factor,
            },
        }
        previous = [guide_id, 0]

    graph.update(
        {
            "200": {"class_type": "RandomNoise", "inputs": {"noise_seed": 310944}},
            "201": {
                "class_type": "BasicGuider",
                "inputs": {"model": ["3", 0], "conditioning": previous},
            },
            "202": {
                "class_type": "BasicScheduler",
                "inputs": {
                    "model": ["3", 0],
                    "scheduler": "simple",
                    "steps": 20,
                    "denoise": 1.0,
                },
            },
            "203": {
                "class_type": "KSamplerSelect",
                "inputs": {"sampler_name": "res_multistep"},
            },
            "204": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["200", 0],
                    "guider": ["201", 0],
                    "sampler": ["203", 0],
                    "sigmas": ["202", 0],
                    "latent_image": ["6", 1],
                },
            },
            "205": {
                "class_type": "CauceSaveAVLatent",
                "inputs": {
                    "latent": ["204", 0],
                    "filename_prefix": f"cauce/latents/2026-08-31/{output_label}",
                    "artifact_index": source_start,
                },
            },
            "206": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["204", 0], "vae": ["2", 0]},
            },
            "207": {
                "class_type": "CauceAcceptDecodedRange",
                "inputs": {
                    "images": ["206", 0],
                    "start_frame": 0,
                    "frame_count": delivery_frames,
                },
            },
            "208": {
                "class_type": "CreateVideo",
                "inputs": {"images": ["207", 0], "fps": 24, "bit_depth": 8},
            },
            "209": {
                "class_type": "SaveVideo",
                "inputs": {
                    "video": ["208", 0],
                    "filename_prefix": f"video/2026-08-31/{output_label}",
                    "format": "auto",
                    "codec": "auto",
                },
            },
        }
    )
    return graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uploaded-video")
    parser.add_argument("--window-starts", default="0,38,77,115")
    parser.add_argument("--source-strides", default="8,16")
    parser.add_argument("--factor", type=int, choices=(2, 3, 4), default=4)
    parser.add_argument("--width", type=int, default=672)
    parser.add_argument("--height", type=int, default=672)
    parser.add_argument("--output-label", default="gen45_slowmo4x")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.uploaded_video:
        starts = [int(value.strip()) for value in args.window_starts.split(",")]
        strides = [int(value.strip()) for value in args.source_strides.split(",")]
        if any(stride < 1 for stride in strides):
            raise ValueError("source strides must be positive integers")
        for ordinal, start in enumerate(starts, start=1):
            for stride in strides:
                label = (
                    f"{args.output_label}_w{ordinal:02d}_f{start:03d}_s{stride:02d}"
                )
                path = OUTPUT / f"{label}.api.json"
                path.write_text(
                    json.dumps(
                        addguide_video_graph(
                            factor=args.factor,
                            source_start=start,
                            input_file=args.uploaded_video,
                            width=args.width,
                            height=args.height,
                            output_label=label,
                            source_stride=stride,
                        ),
                        ensure_ascii=False,
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                print(path.relative_to(ROOT))
        return
    for factor in (2, 3, 4):
        source_frames = {2: 60, 3: 40, 4: 30}[factor]
        path = OUTPUT / f"addguide-{source_frames}-slowmo-{factor}x.api.json"
        path.write_text(
            json.dumps(addguide_graph(factor), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
