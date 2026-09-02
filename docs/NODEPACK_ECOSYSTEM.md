# Modular ComfyUI extension ecosystem

Checked on 2026-09-01. This document decides which external ComfyUI
extensions, official auxiliary weights and optional runtime patches may extend
the laboratory. It is deliberately organized by capability and data contract,
not by repository popularity.

## Decision summary

The recommended system is not a large collection of custom nodes. It is:

```text
official ComfyUI + official H3 implementation
  -> CAUCE exact native-state and mask algebra
  -> selected official perception/control weights
  -> a small whitelist of generic KJNodes utilities
  -> project graphs, receipts and acceptance evidence
```

The 2026-08-31 laboratory capture already exposes official Canny, Depth
Anything 3, SAM3 video tracking and SDPose nodes. Consequently:

- do not install another nodepack merely to obtain Canny, depth, pose or video
  mask tracking;
- add the required official weight only when a workflow is ready to use it;
- use KJNodes for bounded generic mask, batch and diagnostic
  utilities;
- make compatible Turbo/PDD profiles first-class iteration modes while
  retaining the ordinary 20-step quality baseline;
- update core in isolation before adopting the newly merged H3 Fun Control
  model patch;
- consider `comfyui_controlnet_aux` only for a modality absent from core, such
  as HED, MLSD or DWPose, and only after native Canny/depth/pose tests;
- keep VideoHelperSuite and rgthree outside the first installation wave;
- never let an external pack own the H3 sampler, native AV-state format,
  project ontology or canonical workflow provenance.

This is a core-first architecture, not a rejection of community work. The
community is used as a source of generic transforms, observability, upstream
patches and hypotheses. The model-specific semantics remain where they can be
audited most reliably: official ComfyUI and small CAUCE data operations.

## Current official baseline

The following nodes are present in the saved live `/object_info` capture from
2026-08-31. A node being present proves its schema is available; it does not
prove that its optional model weight is already on disk.

| Capability | Live official nodes | Data produced | Additional nodepack needed? |
| --- | --- | --- | --- |
| H3 FL2VA | `MiniMaxH3ImageToVideo` | native H3 conditioning/state | no |
| H3 Ref2VA | `MiniMaxH3ReferenceToVideo` | native H3 conditioning/state | no |
| exact visual guides | `MiniMaxH3AddGuide` | target-aligned H3 guide | no |
| Qwen image references | `MiniMaxH3AddQwenImageReference` | semantic conditioning | no |
| timed Qwen references | `MiniMaxH3AddTimedImageReference`, `MiniMaxH3AddTimedVideoReference` | time-addressed semantic conditioning | no |
| edge map | `Canny` | `IMAGE` | no |
| depth/geometry | `LoadDA3Model`, `DA3Inference`, `DA3Render` | `DA3_GEOMETRY`, then `IMAGE` | no; weight required |
| object mask detection | `SAM3_Detect` | `MASK`, bounding boxes | no; weight required |
| video mask propagation | `SAM3_VideoTrack`, `SAM3_TrackToMask`, `SAM3_TrackPreview` | tracked `MASK` batch | no; weight required |
| human pose map | `SDPoseKeypointExtractor`, `SDPoseDrawKeypoints`, `SDPoseFaceBBoxes` | keypoints, bounding boxes, then `IMAGE` | no; weights required |
| video load/save/slicing | core video nodes plus `Video Slice` | `VIDEO`, `IMAGE`, audio | no |

Current upstream core also contains `VideoTrim` and `VideoCrop`; they were
merged after the captured laboratory revision. Their absence is a core-version
gate, not a reason by itself to install an additional video suite.

## Responsibility and datatype boundaries

### Official ComfyUI owns

- H3 model loading, text/vision conditioning, FL2VA, Ref2VA and AddGuide;
- the official H3 sampler, VAE and packed AV semantics;
- H3 Fun Control loading/application after the corresponding core update;
- ordinary media loading, preview, creation and saving;
- official perception nodes such as SAM3, DA3 and SDPose.

### CAUCE owns

- exact frame, visual-token and structural-audio-token arithmetic;
- allocation, extraction, placement, replacement, append, split and rollback
  of native H3 AV state;
- construction and projection of continuous temporal/spatial masks into H3's
  packed state;
- native-state persistence, inspection and provenance;
- deterministic preflight for control fitting and packed-row cost.

CAUCE must accept ordinary `IMAGE` and `MASK` values without knowing whether
they came from a hand-painted asset, SAM3, DA3, KJNodes or another future
source. That makes mask/control sources replaceable without changing the H3
state algebra.

### External extensions may own

- generic `IMAGE` or `MASK` transforms absent from core;
- generic batch/index manipulation that removes transparent graph boilerplate;
- previews and diagnostics that do not alter accepted output;
- measured memory workarounds for an actual runtime limit.

They must not silently become a second sampler, model manager, timeline,
prompt language, persistence layer or project ontology. Canonical API graphs
use explicit links and ordinary Comfy datatypes.

## Adoption classes

| Class | Meaning | Locking and evidence |
| --- | --- | --- |
| `core` | Required by every canonical H3 graph | exact ComfyUI/CAUCE commits and live `/object_info` |
| `official-weight` | Optional model used by an official core node | repository revision, filename, bytes, digest, license and one bounded smoke |
| `optional-data` | Produces standard `IMAGE`, `MASK`, `VIDEO` or equivalent input | exact public commit, node whitelist and isolated restart |
| `optional-observability` | Preview or diagnostic only; disabling it must not change the saved result | exact public commit plus fixed-seed output-equivalence test |
| `conditional-runtime` | Activated only to solve a measured OOM or runtime limit | baseline/variant peak memory, duration and output comparison |
| `research-only` | Source of mechanisms and test hypotheses | no production graph dependency |
| `rejected` | Duplicate, opaque, unlicensed, incompatible or empirically harmful | record the reason; do not install by habit |

## Capability-to-module map

| Needed operation | Required input or mechanism | Best current source | Extension decision |
| --- | --- | --- | --- |
| endpoint generation and image/video references | official H3 conditioning | core H3 nodes | keep core-only |
| exact sparse or dense frame anchors | target-aligned guides | core `MiniMaxH3AddGuide` plus CAUCE frame arithmetic | keep core-only |
| arbitrary local temporal/spatial retake | continuous `MASK` batch plus native H3 state | manual/core mask nodes, optional SAM3 tracking, selected KJ mask transforms, CAUCE projection | add only the source actually needed |
| temporally tracked object edit | one initial mask or detector prompt, video tracking, mask cleanup | official SAM3 plus KJ/core mask transforms | official weight, no new tracker pack |
| Canny structural generation | edge-map `IMAGE` plus H3 Fun Control patch | core `Canny` plus official Fun Control path | core update + control weight only |
| depth structural generation | depth-map `IMAGE` plus H3 Fun Control patch | core DA3 plus official Fun Control path | add one DA3 weight + control weight |
| pose structural generation | pose-map `IMAGE` plus H3 Fun Control patch | core SDPose plus official Fun Control path | add SDPose weights + control weight |
| HED/MLSD/DWPose structural generation | control-map `IMAGE` not supplied by current core | `comfyui_controlnet_aux` or externally prepared control video | late optional pack |
| exact frame/index batch assembly | indexed `IMAGE` batch operations | core first, selected KJNodes if materially clearer | bounded whitelist |
| lower peak H3 memory | FFN or attention chunking | KJ H3 experimental patches | conditional, never default |
| faster sampling | Turbo or PDD LoRA matched to trunk and FL2VA/Ref2VA family | ordinary core LoRA path; PDD requires newer core | named iteration profile, no nodepack |
| remote authoring ergonomics | previews, selection, graph navigation | core first; KJ UI helpers; VHS/rgthree only after measured need | defer broad UI packs |

## Module A: KJNodes, bounded adoption

Repository: <https://github.com/kijai/ComfyUI-KJNodes>

Observed source lock:

```text
repository  kijai/ComfyUI-KJNodes
commit      e8e88f7c88e3f6205b122f5de87e69a09fbce5ac
license     GPL-3.0
package     1.5.0
```

KJNodes is the strongest first community addition because it supplies several
small generic transforms and Kijai is simultaneously contributing H3 support
upstream. Installing the repository still does not make all of its nodes part
of the project contract.

### A1. Continuous and animated mask authoring

Recommended nodes:

| Node | Utility in this system | Boundary |
| --- | --- | --- |
| `CreateFadeMaskAdvanced` | constructs a per-frame continuous authority schedule across a batch | temporal strength envelope; it does not select content |
| `GrowMaskWithBlur` | dilation/erosion plus soft edge and per-frame evolution | generic mask cleanup before CAUCE projection |
| `RemapMaskRange` | remaps black/white authority into a bounded continuous interval | useful for denoise ladders that avoid hard 0/1 masks |
| `OffsetMask` | translates/rotates a mask batch with explicit padding/roll behavior | procedural animated mask source |
| `MaskBatchMulti` | concatenates multiple mask batches | assembly only; CAUCE still validates duration |
| `ResizeMask` | makes spatial size explicit before native projection | no implicit model fitting |
| `CreateShapeMask` | cheap circles/squares/triangles for causal mask tests | diagnostic/procedural source, not semantic tracking |

The core composition is:

```text
MASK source
  -> optional grow / blur / offset / remap
  -> CAUCE exact temporal interval and spatial intersection
  -> CAUCE projection to native H3 visual-token authority
  -> official H3 sampler
```

Avoid making `SplineEditor`, the deprecated `CreateShapeMaskOnPath`, or an
untested gradient generator a canonical requirement. They can be explored in
scratch graphs without entering paired API workflows.

### A2. Image-batch and guide-ladder operations

Potentially useful nodes are `GetImageRangeFromBatch`,
`GetImagesFromBatchIndexed`, `InsertImagesToBatchIndexed`,
`PadImageBatchInterleaved`, `ReplaceImagesInBatch`, `ReverseImageBatch` and
`ImageBatchRepeatInterleaving`.

These can reduce wiring in dense AddGuide experiments, guide extraction and
exact sparse-anchor ladders. Adoption is conditional because core already has
basic `ImageFromBatch` and repeat operations, while CAUCE already owns exact
index arithmetic. A KJ batch node is accepted only when:

1. its index convention is explicit and covered by a tiny deterministic test;
2. it outputs an ordinary `IMAGE` batch;
3. the canonical API graph remains legible;
4. it replaces boilerplate rather than hiding temporal semantics.

### A3. Preview override is not adopted

KJNodes contains `ModelPreviewOverrideKJ` and
`GetPreviewOverrideFramesKJ`, but approximate per-step TAE preview is not useful
for the current production practice. Do not download TAEH3 or make preview
override part of any runtime profile. Results are reviewed from official H3 VAE
decodes and saved videos.

### A4. Runtime and memory diagnostics

Useful only in diagnostic graphs:

| Node | What it measures | Restriction |
| --- | --- | --- |
| `TimerNodeKJ` | elapsed wall time around a graph section | profiling only |
| `ModelMemoryUseReportPatch` | CUDA peak allocated/reserved around sampling | profile baseline and variant separately |
| CUDA memory-history start/end/visualization nodes | detailed allocator history and snapshot | dedicated troubleshooting only; can create large artifacts |
| `PreviewLatentNoiseMask` | generic latent mask metadata | helpful smoke, but CAUCE remains authoritative for packed H3 mask inspection |

`VRAM_Debug` may unload models or clear caches. It is not allowed in canonical
production graphs because it changes runtime state and can make performance
measurements non-comparable.

### A5. Conditional H3 memory patches

| Node | Mechanism | Expected tradeoff | Gate |
| --- | --- | --- | --- |
| `MiniMaxChunkFeedForward` | chunks the packed-token dimension through H3's SwiGLU feed-forward blocks | lower peak memory, additional calls/latency | use only after an OOM or documented peak-memory need |
| `MiniMaxLowVRAMAttention` | restructures attention to release intermediates and process independent heads in chunks | lower peak memory, more overhead and stronger coupling to H3 internals | fixed-seed numerical and visual A/B |

Do not use by default:

- `MiniMaxH3TokenCounter`, because `CauceH3InspectPackedSequence` already owns
  exact project row accounting and receipts;
- `MiniMaxH3MemoryEfficientSageAttentionPatch` on the RTX 5090 until current
  Blackwell kernel compatibility is proven. Multiple open reports concern
  SageAttention kernel resolution on compute capability 12.x;
- Set/Get links in canonical API graphs. They are useful during authoring, but
  KJ's conversion command should materialize every Set/Get as a direct link
  before paired export;
- model patches merely because they exist. Core updates may alter internal H3
  method signatures, as already occurred around PDD support.

KJNodes requirements are runtime mutations. Install them inside the portable
Comfy Python environment through the bounded repository/Manager plane, never
into an unrelated system Python.

## Module B: official auxiliary weights, not nodepacks

### B1. SAM3 for tracked masks

Official core SAM3 can detect objects, propagate identity-aware masks over a
video and return a standard mask batch. The current official checkpoint is:

```text
file    checkpoints/sam3.1_multiplex_fp16.safetensors
size    1,745,546,848 bytes (about 1.75 GB)
sha256  9ba99c92703c2e8b4f47de2d34a539bb8e18923049e238b780d70dbe6368eb03
license SAM license
```

Recommended graph:

```text
video frames
  -> SAM3_Detect on first frame OR a manual initial MASK
  -> SAM3_VideoTrack
  -> SAM3_TrackToMask
  -> optional KJ grow / blur / remap
  -> CAUCE interval × spatial-mask projection
  -> edit.masked_video, refine.video@masked,
     or complete.native_av@local-replacement
```

This is the correct route for a mask that follows an arbitrary object. A
procedural KJ mask is the correct route when the mask itself is the authored
motion. CAUCE does not need to know the semantic difference; both arrive as
opaque `MASK` batches.

Do not install Kijai's older SAM2 pack for this purpose. The official core
surface is newer, narrower and already present in the laboratory schema.

### B2. Depth Anything 3

Official DA3 nodes load one geometry-estimation weight and can render depth,
colored depth, sky or confidence images. Available official variants have
different cost/outputs:

| Variant | Approximate bytes | Character |
| --- | ---: | --- |
| small | 137,254,980 | cheapest control-map experiment |
| base | 541,524,124 | stronger quality/cost compromise |
| mono large | 1,336,748,056 | higher-detail relative depth and sky |
| metric large | 1,336,748,056 | metric-depth specialization |

Start with `base` for structural-control evaluation unless the official H3
example requires a different variant. Do not download all four. DA3's
multi-view geometry is interesting research data but is not automatically an
H3 motion-control mechanism; the immediate production interface is the
rendered depth `IMAGE`.

### B3. SDPose

The official pose path uses approximately:

```text
sdpose_wholebody_fp16.safetensors    1,916,645,792 bytes
rt_detr_v4-x-hgnet_fp16.safetensors   123,968,978 bytes
total                                 about 2.04 GB
```

It can extract whole-body keypoints, render an OpenPose-compatible map and use
bounding boxes for multi-person detection. This module is valuable only when
human articulation is a real source material need. It should not precede the
zero-weight Canny baseline or the more general depth experiment.

## Module C: official H3 Fun Control model patch

Model: <https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union>

The single 6,806,843,904-byte checkpoint supports Canny, depth, HED, MLSD,
pose and masked video inpainting. It attaches a control branch to five of H3's
50 transformer blocks. In current ComfyUI it is applied as an H3 model patch,
not as a generic classic ControlNet.

The official node accepts:

- the H3 model;
- the loaded model patch;
- the H3 VAE;
- `strength`, `start_percent` and `end_percent`;
- optional control-video `IMAGE` batch;
- optional `MASK` and source-video `IMAGE` batch for inpainting.

The model card specifies fixed 24 fps, legal `17n+5` frame counts, at most 15
seconds, preserved control-video aspect ratio and guidance-distilled sampling
at guidance scale 1. The project must treat control strength, temporal start/end
and prompt as independent experimental axes.

### Structural-control compositions

```text
source video -> core Canny --------------------------┐
source video -> core DA3 -> depth IMAGE -------------┼-> H3 Fun Control patch
source video -> core SDPose -> pose IMAGE -----------┘   -> ordinary official H3 sampling
```

`generate.with_control@structural-video` should first compare:

1. no control;
2. Canny at a short strength ladder;
3. depth at the same seed/prompt;
4. only then pose or another modality.

Control video is not a semantic reference and not a preservation mask. It
constrains spatial/temporal structure while H3 still generates appearance.
References, first/last frames and guides remain separate conditioning channels.
The recently merged upstream compatibility fix means combined reference plus
Fun Control is plausible, but it still needs a live graph on the exact updated
core before entering the canonical profile.

### Masked-inpaint composition

```text
source video IMAGE + continuous MASK
  -> official H3 Fun Control patch
  -> H3 generation conditioned on source/mask
```

This is a distinct mechanism from CAUCE native-state masked editing. Both
should be retained for comparison:

- CAUCE/native mask path preserves and re-denoises already available packed
  H3 state directly;
- Fun Control inpainting accepts decoded source video and a control branch,
  which can be used when native state is absent or when the control model gives
  better local synthesis.

They must not share the same operation name or silently substitute for one
another.

## Module D: extra control preprocessors, late and narrow

Repository: <https://github.com/Fannovel16/comfyui_controlnet_aux>

This pack is not part of the initial recommendation. Core already supplies the
three most relevant baselines:

- Canny with no learned preprocessor weight;
- DA3 depth;
- SDPose pose.

The remaining reasons to install it are a demonstrated need for HED, MLSD,
DWPose or another unique detector. Its dependency surface includes OpenCV,
ONNX Runtime, MediaPipe and other scientific packages, which increases the
chance of conflicts in a shared Windows portable runtime. A safer alternative
is to generate the control map outside the tower and upload an ordinary
`IMAGE`/video input.

If admitted, select one detector, pin one public commit, capture the full pip
delta, download only its weight, and prove the ordinary H3 baseline still
imports after restart. Never install the entire detector zoo speculatively.

## Module E: VideoHelperSuite, conditional authoring utility

Repository: <https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite>

VHS offers advanced preview encoding, force-rate/force-size controls, frame
caps, skip/select-Nth operations and convenient video assembly. These are
useful when tunnel bandwidth or interactive browsing is a measured bottleneck.

It is not an H3 capability and is not needed for exact production semantics:

- core already owns canonical load/create/save and the captured `Video Slice`;
- newer core adds `VideoTrim` and `VideoCrop`;
- CAUCE owns exact half-open frame ranges;
- delivery fps and temporal expansion must not be hidden inside a preview
  node.

Therefore omit VHS initially. Add it only if a concrete remote-authoring test
shows a material preview or selection improvement. Even then, paired API
workflows should remain on core nodes where possible.

## Module F: rgthree, deferred frontend ergonomics

Repository: <https://github.com/rgthree/rgthree-comfy>

rgthree adds routing, group bypass, bookmarks and other graph-authoring aids.
It adds no H3 mathematics. KJNodes already contributes Set/Get and editing
helpers, so installing both immediately creates overlapping frontend mutation
and a larger debugging surface.

Adopt rgthree only after a named authoring need remains unsolved. No canonical
API graph may depend on frontend-only state, hidden routing or group bypass.

## Module G: acceleration profiles without another nodepack

Fast iteration is a current production objective. Acceleration remains an
execution profile over an existing operation, not a new operation or nodepack.

- official workflow templates already expose compatible 4-step/8-step H3
  Turbo LoRAs;
- ComfyUI merged support for H3 PDD LoRAs;
- Alibaba PAI publishes separate official 8-step PDD LoRAs for FL2VA and
  Ref2VA.

The installed FP8-scaled trunks are incidental, not a constraint. Given the
captured RTX 5090, PyTorch `2.13.0+cu130` and `comfy-kitchen 0.2.31`, the target
baseline replaces both with the official preferred pruned `int8_convrot`
FL2VA/Ref2VA trunks. Turbo is the first acceleration adoption because it uses
the ordinary LoRA loader and official templates demonstrate it with that
quantized trunk strategy. PDD enters after a pinned core update because its
output-head bank support was merged after the captured runtime.

Every operation may select a visible profile:

```text
quality-20
turbo-fl2va-8
turbo-fl2va-4
turbo-ref2va-4
pdd-fl2va-8
pdd-ref2va-8
```

Turbo/PDD weights are family-specific and never mixed. The accepted PDD profile
uses the matching pruned conversion, exactly 8 steps, `simple`, LoRA strength
1.0 and an independently tested sampler. Details, exact filenames, source
revisions, sizes and evaluation gates are defined in
[H3 acceleration profiles](ACCELERATION_PROFILES.md).

## Installable runtime profiles

Profiles are additive manifests, not different Comfy installations.

### `h3-core`

- official ComfyUI and H3 models;
- CAUCE;
- no optional nodepack.

Purpose: canonical baseline and recovery target.

### `h3-utility-light`

- `h3-core`;
- pinned KJNodes;
- whitelist: masks, selected batch/index utilities and timer/memory
  diagnostics.

Purpose: generic authoring and diagnostics. No TAE preview or H3 model patch.

### `h3-mask-tracking`

- `h3-utility-light`;
- official SAM3 1.75 GB checkpoint;
- paired SAM3 -> standard `MASK` -> CAUCE smoke.

Purpose: temporally stable local edits and retakes. No external tracking pack.

### `h3-fast-turbo`

- selected pruned `int8_convrot` H3 trunks;
- one matching Comfy-format Turbo LoRA per active conditioning family;
- nominal 4/8-step `simple` profile;
- paired 20-step quality baseline.

Purpose: default fast scouting and workflow iteration without code/nodepack
mutation.

### `h3-fast-pdd`

- pinned core containing PDD output-head-bank support;
- matching pruned Comfy-format FL2VA or Ref2VA PDD LoRA;
- exactly 8 steps, `simple`, LoRA strength 1.0;
- no simultaneous Turbo or KJ model patch.

Purpose: second fast candidate after core update and unchanged-baseline smoke.

### `h3-structural-canny`

- updated/pinned core containing official H3 Fun Control support and reference
  compatibility fix;
- 6.8 GB H3 Fun Control Union model patch;
- existing core Canny.

Purpose: lowest-dependency proof that structural control works.

### `h3-structural-depth`

- `h3-structural-canny`;
- one pinned DA3 weight, preferably `base` for the first cost/quality test.

Purpose: geometry-following motion/camera structure without hard edges.

### `h3-structural-pose`

- `h3-structural-canny`;
- official SDPose and RT-DETR weights.

Purpose: articulated human motion when production material actually needs it.

### `h3-preprocessors-extra`

- one pinned `comfyui_controlnet_aux` commit;
- one named detector and weight only.

Purpose: HED/MLSD/DWPose or another proven modality absent from core. Not a
general production profile.

### `h3-low-vram-experimental`

- a specific KJ FFN or attention patch;
- a paired unchanged baseline;
- explicit activation in the graph.

Purpose: solve a measured resource failure, never routine sampling.

### `h3-remote-preview-extra`

- optional VHS only after bandwidth/browser measurements.

Purpose: authoring ergonomics; canonical outputs remain independent.

## Storage plan for the 120 GB host

Approximate incremental model storage:

| Module | Increment |
| --- | ---: |
| one Comfy-format Turbo LoRA | 1.96 GB |
| one pruned Comfy-format PDD LoRA | 1.73 GB |
| SAM3 tracked masks | 1.75 GB |
| H3 Fun Control Union | 6.81 GB |
| DA3 base | 0.54 GB |
| DA3 mono large instead of base | 1.34 GB |
| SDPose + RT-DETR | 2.04 GB |

A useful structural stack of SAM3 + Fun Control + DA3 base costs roughly 9.1 GB
before filesystem overhead. One Turbo file brings that to roughly 11.1 GB; one
PDD profile instead brings it to roughly 10.8 GB. All three Turbo files consume
about 5.87 GB, while both pruned PDD files consume about 3.45 GB. Do not stage
every accelerator before its conditioning family is actually used: model
storage, input assets, temporary frames and outputs share the same disk.
Preserve an explicit safety reserve and clean generated media through the
bounded file-control plane.

## Recommended adoption sequence

Each wave is independently reversible and produces evidence before the next.

### Wave 0: reconcile the baseline

1. capture current core, CAUCE and custom-node commits;
2. verify free disk and a clean queue;
3. query `/object_info` and model-folder inventories;
4. distinguish available node schema from actual weight presence;
5. retain one known-good core H3 smoke.

### Wave 1: isolated core update

1. update core to one pinned public commit containing PDD, H3 Fun Control and
   reference/control compatibility support;
2. do not add or replace a model in the same mutation;
3. restart, capture `/object_info` and import errors;
4. reproduce the existing FP8 20-step FL2VA and Ref2VA baseline.

### Wave 2: chosen trunks and Turbo/PDD

1. stage FL2VA pruned `int8_convrot`, reproduce the 20-step graph, then retire
   its FP8 predecessor;
2. repeat independently for Ref2VA;
3. add only the FL2VA Turbo 8-step Comfy-format LoRA;
4. run a paired 20-step versus nominal 8-step graph with identical inputs;
5. add FL2VA 4-step only after the 8-step result is understood;
6. add the separate Ref2VA 4-step weight only when a Ref2VA graph is ready;
7. add matching pruned PDD 8-step weights in later one-file windows;
8. retain execution time, peak memory and visual assessment for every profile.

### Wave 3: KJ utilities and tracked-mask operation

1. install pinned KJNodes without its preview path;
2. verify only mask, selected batch/index and diagnostic nodes;
3. run one animated continuous-mask graph into CAUCE inspection;
4. add the SAM3 weight independently;
5. track a short source clip from a manual first-frame mask;
6. feed the standard mask through KJ cleanup and CAUCE projection;
7. compare native masked edit against untracked/static-mask baseline.

### Wave 4: official H3 structural control

1. add the 6.8 GB Fun Control checkpoint in its own weight window;
2. run Canny control first because it needs no detector weight;
3. evaluate control strength and start/end ladders;
4. only after acceptance add DA3 base and test depth control;
5. test references plus control as a separate graph.

### Wave 5: production-specific modalities

- add SDPose only for real human-motion material;
- add one extra `controlnet_aux` detector only if Canny/depth/pose cannot
  express the needed structure;
- evaluate VHS/rgthree only when remote authoring friction is measured.

## Safe installation protocol

Never combine a ComfyUI core update, nodepack install and model download in one
unknown mutation window.

For each external module:

1. record the clean queue, current runtime manifest and free disk;
2. require a public repository and choose one exact commit;
3. install only that repository through the bounded repository/Manager plane;
4. restart the Comfy process once; never reboot or mutate CUDA/PyTorch;
5. capture fresh `/object_info`, logs and import errors;
6. verify the intended node whitelist and confirm core H3/CAUCE nodes remain;
7. run the smallest technical smoke and retain its receipt;
8. compare against the unchanged baseline when the module patches a model;
9. pin the module in a runtime profile only after a real accepted graph uses it.

Unknown HTTP outcome is not permission to repeat an install. Reconcile the
Manager/repository state first. No module may install a private Git URL on the
shared host because an interactive credential prompt can stall the Comfy
process behind the tunnel.

## Research-only packs and authors

| Source | What to learn | Why it is not a production dependency now |
| --- | --- | --- |
| [MMH3Tools](https://github.com/ckinpdx/ComfyUI-MMH3Tools) / `ckinpdx` | native latent/reference transport, AV-axis handling, overlap, continuation and context hypotheses | broad sampler/state surface, rapid churn and no detected license; research oracle only |
| [ComfyUI-UtilsCollection](https://github.com/silveroxides/ComfyUI-UtilsCollection) / `silveroxides` | H3 conditioning probes, CLIP/Qwen projection and timed-reference experiments | large AGPL pack overlapping official conditioning; evaluate individual mechanisms |
| [MiniMax H3 Guide](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide) / `EthanFel` | transparent prompt/reference planning and routing UX | CAUCE deliberately has no semantic entity layer or second prompt language |
| [ComfyUI-Continuity](https://github.com/roadmaus/ComfyUI-Continuity) / `Roadmaus` | cross-model product ergonomics and second-pass comparisons | convenience surface spans models and obscures canonical low-level wiring |
| [RES4LYF](https://github.com/ClownsharkBatwing/RES4LYF) / `ClownsharkBatwing` | sampler and scheduling research | no sampler patch enters production without a bounded H3-specific causal A/B |
| [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) / `city96` | quantization compatibility and lower-memory loading | current H3 weights fit; no resource failure justifies another loader |

A repository may be technically excellent and still be the wrong production
dependency. License, narrowness, upstream alignment, dependency cost and
visible evidence are separate gates.

## Developers and upstreams to follow

### Priority 0: source of truth and direct H3 maintainers

- `Comfy-Org/ComfyUI`, `comfyanonymous` and current H3 code owners for released
  runtime behavior and merge history;
- `Kijai` for H3 core contributions, KJNodes, optimized weights and preview
  models;
- `MiniMax-AI` for architecture, checkpoints and official usage;
- `Alibaba PAI` for H3 Fun Control Union, PDD LoRAs and DiffSynth work.

### Priority 1: high-signal mechanism experiments

- `ckinpdx` for fast empirical work on native H3 state and context handling;
- `silveroxides` for advanced conditioning/encoder probes;
- `Kosinkadink` for video graph semantics and core-compatible utilities;
- `Fannovel16`/`comfyorg` for maintained structural preprocessors;
- `EthanFel` for reference/prompt routing design.

### Priority 2: supporting infrastructure

- `ltdrdata` for Manager operations;
- `rgthree` for authoring ergonomics;
- `city96` for quantized loaders;
- `ClownsharkBatwing` for sampler research.

Useful saved searches:

```text
repo:Comfy-Org/ComfyUI MiniMaxH3 is:pr sort:updated-desc
repo:kijai/ComfyUI-KJNodes MiniMax is:issue,pr sort:updated-desc
author:kijai repo:Comfy-Org/ComfyUI is:pr sort:updated-desc
repo:ckinpdx/ComfyUI-MMH3Tools sort:updated-desc
```

## Final recommendation

The next model window should first replace FL2VA FP8 with the pruned
`int8_convrot` trunk and reproduce the current 20-step graph. After that, add
only the FL2VA Turbo 8-step LoRA and compare it with the new 20-step baseline.
This provides immediate iteration speed without installing a nodepack. Repeat
the trunk/LoRA process independently for Ref2VA. KJNodes follows for generic
masks/batches/diagnostics; no TAE preview is adopted. SAM3 is the next
independent weight-only module if tracked edits are immediately useful.

PDD and H3 Fun Control follow after one isolated core update, but as separate
weight/evidence windows. Control begins with core Canny and then DA3 depth.
Pose, extra preprocessors, VHS and rgthree remain opt-in modules triggered by a
named production need, not parts of a default full install.
