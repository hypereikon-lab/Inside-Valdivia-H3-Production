# Expanded H3 capability gates

This document records the 2026-09-01 expansion review. It separates native,
official, and external H3 capabilities so a promising repository never becomes
an implicit production dependency.

## Current boundary

| Capability | Implementation owner | Production status |
| --- | --- | --- |
| Keyframes, references, guides, packed AV continuation/completion/editing | Official ComfyUI H3 plus deterministic CAUCE planning/state primitives | Existing core/full gates |
| Structural video control and masked control inpaint | Official ComfyUI `MiniMaxH3FunControlNetApply` plus Alibaba PAI union model patch | Offline-defined; runtime-gated characterization only |
| Exact packed-sequence inspection | CAUCE, reproducing official `PackedLayout` row arithmetic | Implemented and testable without GPU |
| Learned 3D latent initialization before an H3 second pass | External public nodepack and separately pinned weight | Isolated A/B only; never a core requirement |
| Reference plus structural control in one graph | Official ComfyUI work merged through #16020 | Upstream-supported; laboratory core update, schema capture and live characterization pending |
| Context-window continuation with absolute global position | Unresolved upstream behavior | Do not represent as solved |

CAUCE remains a deterministic low-level layer. It does not vendor the official
control sampler, model patches, or learned upscaler. The project repository owns
the exact runtime profiles, planned graph bindings, and acceptance decisions.

## New deterministic primitives

### `CauceH3PlanControlClip`

This node does not synthesize or modify pixels. It plans and reports the exact
normalization performed by the official H3 control path:

- a short control clip repeats its last frame to the target length;
- a long clip is truncated at the tail;
- spatial fitting uses bilinear resize followed by center crop;
- the report preserves source/target geometry and frame counts for receipts.

That behavior can create a frozen control tail. The planner makes it visible
before a costly run instead of hiding it inside the official node.

### `CauceH3InspectPackedSequence`

This node computes exact packed-sequence rows from the official H3 layout:
text, keyframes, reference streams, target audio, and target video. It reports
whether the cumulative offsets approach the signed 32-bit attention boundary.

The byte estimate is deliberately labelled heuristic. It defaults to the
currently observed packed-row calibration and is not presented as a VRAM law.

### `CauceH3ExtractVisualStream`

This node returns a cloned visual-only latent and an untouched source AV
carrier. An external visual initializer can operate on the clone, after which
`CauceH3ReplaceVisualStream` restores it into the original carrier. Structural
audio and other packed-state fields therefore have an explicit preservation
path instead of relying on an opaque full-latent mutation.

## Structural control characterization

The first official-control batch must hold prompt, seed, sampler, scheduler,
steps, resolution, duration, and source control clip fixed. Characterize:

1. control kind: pose, depth, then canny;
2. strength: `0.6`, `0.8`, `1.0`;
3. end percentage: `0.6`, `0.8`, `1.0`.

Masked inpaint is a separate characterization. The current merged path treats
the mask as binary at a `0.5` threshold, so a grayscale mask must not be
described as continuous influence unless a captured runtime proves otherwise.

Execution is blocked until the `h3-control-experimental` profile validates:

- `ModelPatchLoader`;
- `MiniMaxH3FunControlNetApply`;
- the exact union model patch;
- the required CAUCE deterministic nodes;
- the installed ComfyUI revision and applicable upstream correctness gates.

References/keyframes plus control remain excluded from the materializable
catalog only because the captured laboratory runtime predates #16020. Current
upstream supports the combination and also corrects a dynamic-VRAM prefetch
race. It may enter the catalog after one isolated core update, fresh schema
capture, mask-correctness checks and a bounded live run.

## Learned latent upscale characterization

The learned 3D upscaler is not accepted as an improvement by installation. It
must be compared with the existing native alternatives using the same source,
target geometry, prompt, seed, H3 checkpoint, sampler, scheduler, steps, and
second-pass denoise:

1. native latent initialization;
2. pixel resize plus H3 VAE re-encode;
3. tiled pixel/VAE path when required by memory;
4. learned 3D latent initialization.

The learned branch is rejected on shape incompatibility, flicker, terminal-frame
instability, motion drift, or no useful detail gain over the native controls.
Its repository commit and weight are independent locks, and the nodepack is not
part of the full production profile.

## Upstream gates that affect interpretation

- [Official H3 Fun ControlNet merge](https://github.com/Comfy-Org/ComfyUI/pull/15975)
- [Reference/keyframe plus control and dynamic-VRAM work](https://github.com/Comfy-Org/ComfyUI/pull/16020)
- [Mask-velocity conversion fix](https://github.com/Comfy-Org/ComfyUI/pull/15988)
- [Packed-row memory estimate](https://github.com/Comfy-Org/ComfyUI/pull/15983)
- [Alibaba PAI H3 Fun ControlNet union model](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union)
- [External learned H3 latent upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler)

These references are evidence inputs, not automatic installation authority.
Every live adoption still requires an exact public repository, pinned commit,
content-addressed model, clean queue, sufficient disk reserve, and a fresh
`/object_info` capture.

## Optional nodepack boundary

External packs extend standard Comfy datatypes around this surface; they do not
become part of CAUCE automatically:

- KJNodes may supply generic continuous-mask authoring and a low-cost H3
  preview. Its attention and feed-forward patches are conditional OOM tools,
  never defaults;
- `comfyui_controlnet_aux` may produce Canny, depth, HED, MLSD and pose control
  images after the official H3 control path is deployed;
- VideoHelperSuite and rgthree are authoring conveniences, not canonical API
  graph dependencies;
- broad or rapidly changing H3 packs remain research sources until one narrow
  mechanism passes licensing, schema, fixed-seed and visual gates.

The exact module classes, observed source locks, whitelist and safe mutation
sequence are defined in [Modular ComfyUI nodepack ecosystem](NODEPACK_ECOSYSTEM.md).
