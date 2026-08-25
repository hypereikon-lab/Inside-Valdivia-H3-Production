# Current implementation state

This document is the authority for present capability claims. It records the
last verified laboratory state and the current repository state without using
implementation chronology as product documentation.

## Reachability

At the latest user report on 2026-08-25, the laboratory tunnel was temporarily
unavailable and expected to return later the same day. That blocks live schema
queries, queue submission, GPU execution, Manager operations, and visual
inspection. It does not imply that the installed ComfyUI or CAUCE state changed.

The last verified laboratory runtime was:

```text
ComfyUI                 0.33.0
required frontend       1.49.6
Python                  3.12.10 embedded, Windows
PyTorch                 2.13.0+cu130
GPU                     NVIDIA GeForce RTX 5090
GPU memory              34,190,458,880 bytes reported by runtime
RAM                     67,768,381,440 bytes reported by runtime
registered node types   913
frontend extensions     53
```

Free disk space was not measured through the runtime audit.

## Installed model and node state

The last verified H3 model files were:

```text
diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors
diffusion_models/minimax_h3_ref2va_pruned_fp8_scaled.safetensors
text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
vae/minimax_h3_video_vae_fp16.safetensors
vae/minimax_h3_audio_vae_fp32.safetensors
```

The laboratory had `ComfyUI-Cauce` commit
`81cc8fc6b44b1983c55d587f82c2628a95542258` installed. All 19 CAUCE nodes and
all six H3 AV primitive nodes were present in `/object_info`.

`ComfyUI-Workspace-Control` is implemented and locally tested but is not
installed in the laboratory. Its capability route therefore remains absent
until a separately confirmed targeted installation and ComfyUI-process restart.

## Workflow ownership and evidence

| ID | Implementation | Retained graph artifact | Strongest current evidence |
| --- | --- | --- | --- |
| W1 | official H3 / vanilla ComfyUI | none | declarative spec |
| W2 | official H3 / vanilla ComfyUI | none | declarative spec |
| W3 | official H3 / vanilla ComfyUI | none | declarative spec |
| W4 | official H3 sampling + CAUCE native AV primitives | exact smoke graph not yet retained as a reusable template | synthetic live execution |
| W5 | official H3 guides + CAUCE exact decoded ranges + vanilla assembly | none | declarative spec; CAUCE range primitive unit-validated |
| W6 | CAUCE decoded-media maps + official H3 reference conditioning | none | deterministic map layer unit-validated |
| W7 | CAUCE exact decoded ranges + vanilla assembly | none | deterministic range layer unit-validated |

W1–W3 add no custom model capability. They are canonical, reproducible uses of
the official H3 nodes shipped with ComfyUI.

W4 is the only current workflow whose central data operation depends on CAUCE:
it preserves and extends packed H3 visual and structural-audio state on exact
absolute clocks. W5–W7 use CAUCE only for deterministic transformations around
official or vanilla nodes.

## W4 execution evidence

A minimal W4 API graph completed under prompt id
`d6ca67c6-71af-4172-9ab7-cc18a0e6ad7e`. It used a synthetic 22-frame source AV
latent, 5-frame overlap, 51-frame extension, a 56-frame sampled window at
global origin 17, and one H3 sampling step.

The saved packed latent was loaded and inspected under prompt id
`aa5bf2cc-ea0d-4f8f-80a4-0fe3b64317bc`:

```text
frames                   73
video tokens             22
structural-audio tokens  122
video shape              [1, 24, 22, 12, 20]
audio shape              [1, 32, 2, 122]
```

This proves that the live native-AV mechanics execute and remain synchronized.
It does not prove production-resolution continuation quality because the source
was synthetic, resolution was 320x192, the run used one step, and no decoded
video was visually evaluated.

## Implemented, materialized, and possible

Use these distinctions:

```text
implemented
  code or official nodes exist and have the stated local/live evidence

materialized
  a retained UI graph or API template exists for one concrete composition

possible to compose
  available nodes can express the graph, but the graph artifact and its
  execution/visual evidence do not yet exist
```

Current retained products include workflow specifications, deterministic CAUCE
primitives, Runtime Control, and Workspace Control source code. The repository
does not yet ship import-tested UI graphs or reusable API templates for W1–W7.

The current system also does not claim masked temporal inpainting, arbitrary
sampler modification, automatic high-level graph synthesis, or a visually
accepted production workflow. New workflow compositions can be implemented
from official nodes and the existing primitives, but each concrete graph must
be materialized, schema-validated, executed, and visually evaluated before its
behavior becomes a current capability claim.
