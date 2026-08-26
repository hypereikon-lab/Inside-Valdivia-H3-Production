# Current implementation state

This document is the authority for present capability claims. It records the
last verified laboratory state and the current repository state without using
implementation chronology as product documentation.

## Reachability

At the latest user report on 2026-08-25, the laboratory hostname returned HTTP
504 and is treated as unavailable. A gateway timeout alone does not distinguish
a stopped Cloudflare connector from a connector whose `localhost:8188` origin
is not responding. This blocks live schema queries, queue submission, GPU
execution, Manager operations, and visual inspection. It does not establish
that the installed ComfyUI, CAUCE, model, driver, or GPU state changed.

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

The project operation lock points to CAUCE 3.3.0 commit
`630218affb1c51bf7924e396feee9b540bad6f2e`. It retains the same seven semantic
operation contracts and now contains ten checked, non-executable topology
dossiers: one for every operation plus separate first-frame, image-reference,
and single-guide canonical variants. The source registry remains 24 nodes. The
five additional
primitives are:

```text
CauceH3ResolveTargetShape
CauceH3PrepareGuideClip
CauceH3PrepareReferenceClip
CauceH3InspectConditioning
CauceH3SplitAVLatent
```

All five are locally unit-validated. The first four expose official H3 temporal
input rules and active conditioning metadata without replacing official
encoding or sampling; the fifth splits an origin-zero cumulative packed AV
state into a valid prefix and reversible contiguous suffix span.

`generate.from_references` contract version 2 distinguishes the five-frame
minimum accepted by the current ComfyUI implementation from the model's
documented 2–15 second reference-video range. Production baselines therefore
start at the first compliant `17k+5` length, 56 frames.

The lock records the intended project source, not the currently imported
laboratory process. The laboratory remains last verified at the older 19-node
commit above. A targeted CAUCE update and one ComfyUI process restart are still
required before the five new nodes may be claimed in `/object_info` or used on
the RTX 5090.

`ComfyUI-Workspace-Control` commit
`60402644df18344b1a37216a86870e5c1c0c9d2d` is implemented and locally tested.
Before the current outage its capability route returned 404. One exact Manager
Git-URL installation request was subsequently submitted; the request timed out
while the ComfyUI origin stopped responding, so its outcome is unknown and it
was not submitted again. No ComfyUI restart was requested afterwards. When the
origin returns, inspect Manager's installed-node inventory and the capability
route before deciding whether any installation or restart action remains
necessary.

`ComfyUI-Runtime-Control` commit
`e5abab0a140a08dd6d8e8f6ad092daa3168aba11` implements the deterministic
bridge from one Workspace Control paired export to a guarded, variant-scoped
UI/API draft. It verifies source hashes, literal expected values, exact API
round trip, and—when a full probe manifest is supplied—the captured
`/object_info`. This is locally tested but has not yet been exercised against
the unavailable lab.

## Retired surfaces

`ComfyUI-Cauce-SamplerLab` is a rejected Euler latent-transport experiment. Its
visual result showed ghosting/delay and it is not a CAUCE capability or roadmap
item. `ComfyUI-Hypereikon-H3-Production` is also deprecated: its combined
runtime, timeline, plate, soundtrack-conditioning, and experimental inpainting
surface is outside the current architecture. Neither package should be
installed or updated. When the runtime returns, inventory both exact package
names and remove an installed copy through a targeted operation before the
canonical workflow session.

## Operation ownership and evidence

| Operation | Implementation | Retained graph artifact | Strongest current evidence |
| --- | --- | --- | --- |
| `generate.keyframed` | official H3 / vanilla ComfyUI | offline topology; no graph pair | locked contract |
| `generate.from_references` | official H3 / vanilla ComfyUI | offline topology; no graph pair | locked contract |
| `generate.with_guides` | official H3 / vanilla ComfyUI | offline topology; no graph pair | locked contract |
| `continue.native_av` | official H3 sampling + CAUCE native AV primitives | offline topology + exact smoke evidence; no reusable pair | synthetic live execution |
| `connect.two_sided_guides` | official H3 guides + CAUCE ranges + vanilla assembly | offline topology; no graph pair | locked contract |
| `reference.transform` | CAUCE decoded-media maps | offline topology; no graph pair | deterministic map layer unit-validated |
| `frames.assemble` | CAUCE exact ranges + vanilla assembly | offline topology; no graph pair | deterministic range layer unit-validated |

The three `generate.*` operations add no custom model capability. They provide
typed, reproducible contracts for official H3 behavior.

`continue.native_av` is the current operation whose central data behavior
depends on CAUCE: it preserves and extends packed H3 visual and
structural-audio state on exact absolute clocks. The remaining CAUCE-backed
operations provide deterministic transformations around official or vanilla
nodes.

## `continue.native_av` execution evidence

A minimal API graph completed under prompt id
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

Current retained products include a content-addressed CAUCE operation lock,
project invocation schemas, deterministic CAUCE primitives, visible H3 temporal
preflight and conditioning inspection, reversible native-state branching,
ten offline topology dossiers, nine project materialization plans, an empty
content-addressed media catalog ready for real assets, the paired-export bridge in
Runtime Control, and Workspace Control source code. The five CAUCE 3.3.0 nodes
are source- and unit-validated only until the live update. CAUCE does not yet
ship paired import-tested UI graphs and reusable API templates for these
operations.

The current system also does not claim masked temporal inpainting, arbitrary
sampler modification, automatic high-level graph synthesis, or a visually
accepted production operation. New graph compositions can be implemented
from official nodes and the existing primitives, but each concrete graph must
be materialized, schema-validated, executed, and visually evaluated before its
behavior becomes a current capability claim.
