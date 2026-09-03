# Modular ComfyUI extension ecosystem

Live-checked on 2026-09-02. This document decides which external ComfyUI
extensions, official auxiliary weights and optional runtime patches may extend
the laboratory. It is deliberately organized by capability and data contract,
not by repository popularity.

## Decision summary

The recommended system is not a large collection of custom nodes. It is:

```text
official ComfyUI + official H3 implementation
  -> CAUCE exact native-state and mask algebra
  -> selected official perception/control weights
  -> optional ComfyUI-Hydra deterministic IMAGE-sequence transforms
  -> a small whitelist of generic KJNodes utilities
  -> project graphs, receipts and acceptance evidence
```

The live laboratory now exposes official Canny, Depth Anything 3, SAM3 video
tracking, SDPose, RT-DETR, H3 Fun Control, and current PDD support. KJNodes
`1.5.0` is enabled and exposes 248 nodes. Consequently:

- do not install another nodepack merely to obtain Canny, depth, pose or video
  mask tracking;
- use the already installed, digest-verified official weights through narrow
  workflow graphs rather than adding duplicate detector packs;
- use KJNodes for bounded generic mask, batch and diagnostic
  utilities;
- make compatible Turbo/PDD profiles first-class iteration modes while
  retaining the ordinary 20-step quality baseline;
- keep the technically validated H3 Fun Control route isolated until its
  Canny/depth/pose and masked-inpaint outputs receive visual verdicts;
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

The following nodes are present in the live `/object_info` surface. The model
column distinguishes schema presence from the now verified local artifact.

| Capability | Live official nodes | Verified local model | Additional nodepack? |
| --- | --- | --- | --- |
| H3 FL2VA | `MiniMaxH3ImageToVideo` | pruned INT8 trunk | no |
| H3 Ref2VA | `MiniMaxH3ReferenceToVideo` | pruned INT8 trunk | no |
| exact visual guides | `MiniMaxH3AddGuide` | none | no |
| Qwen image/timed references | official H3 Qwen reference nodes | existing Qwen encoder | no |
| edge map | `Canny` | none | no |
| depth/geometry | `LoadDA3Model`, `DA3Inference`, `DA3Render` | DA3 mono-large | no |
| object/video mask | `SAM3_Detect`, `SAM3_VideoTrack`, `SAM3_TrackToMask` | SAM 3.1 multiplex FP16 | no |
| human pose | `RTDETR_detect`, `SDPoseKeypointExtractor`, `SDPoseDrawKeypoints` | RT-DETR + SDPose FP16 | no |
| structural control/inpaint | `ModelPatchLoader`, `MiniMaxH3FunControlNetApply` | pruned INT8 Fun Control | no |
| video load/save/slicing | core video nodes, `Video Slice`, `VideoTrim`, `VideoCrop` | none | no |
| procedural or transformed control carriers | `HydraRenderSequence` | none | optional public data nodepack |

`VideoTrim` and `VideoCrop` are present in the live core. Their ordinary media
semantics remain separate from CAUCE exact native-state range operations.

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

ComfyUI-Hydra is one such optional data extension. Browser-side Hydra code is
compiled to a signed portable WGSL/GLSL plan; the portable Comfy process renders
that plan to an ordinary `IMAGE` batch through GL/ANGLE. It may create a
procedural sequence or transform linked `IMAGE` inputs. It does not load H3,
alter native H3 state, patch the sampler, define an operation ontology, or own
remote execution. The live commit used by the causal test is
`f96bc23f42466a1c9e137c10c7d860e9d9d7923f`.

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
| faster sampling | Turbo or PDD LoRA matched to trunk and FL2VA/Ref2VA family | ordinary live core LoRA path | named iteration profile, no nodepack |
| remote authoring ergonomics | previews, selection, graph navigation | core first; KJ UI helpers; VHS/rgthree only after measured need | defer broad UI packs |
| deterministic procedural carrier authoring | Hydra code compiled to an ordinary `IMAGE` batch | optional `ComfyUI-Hydra` | accept only with exact pass-through and fixed-seed causal comparisons |

## Module A: KJNodes, bounded adoption

Repository: <https://github.com/kijai/ComfyUI-KJNodes>

Live package identity:

```text
repository   kijai/ComfyUI-KJNodes
distribution Manager registry
package      1.5.0
state        enabled
live nodes   248
license      GPL-3.0
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

The live host uses only `mono large`; it loaded, inferred, and rendered depth
successfully. Do not download the other variants without a measured need.
DA3's
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

The live model is Kijai's curve-form pruned INT8 conversion of the Alibaba PAI
Fun Control Union checkpoint:

```text
file      minimax_h3_fun_controlnet_union_pruned_int8_convrot.safetensors
bytes     2,296,635,360
revision  c79bdb788d0f77460c3952a4c1ae3b3b7d71a4c8
sha256    9c645c0a308c8af361efd43b409710f6f8fec0db297c29503e141a84991fed0c
```

The original 6,806,843,904-byte full-width AdaLN artifact is incompatible with
the selected pruned curve-form trunks and the current loader. Its smoke failed
inside `ModelPatchLoader`; it was removed and must not be reintroduced. The
correct pruned INT8 artifact loaded and sampled successfully through the
official H3 model-patch route.

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
The current core exposes the combined surface. Reference plus control still
needs its own fixed-seed visual characterization before entering a canonical
profile; the successful control smoke proves compatibility, not useful control
adherence.

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
- ComfyUI exposes support for H3 PDD LoRAs on the live host;
- Alibaba PAI publishes separate official 8-step PDD LoRAs for FL2VA and
  Ref2VA.

Both FP8-scaled trunks have been replaced by the pruned `int8_convrot` FL2VA
and Ref2VA trunks. All three Turbo and both pruned PDD files are installed,
digest-verified, and have passed exact-family technical sampling. They remain
profiles over official nodes, not a nodepack dependency.

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

- live core containing PDD output-head-bank support;
- matching pruned Comfy-format FL2VA or Ref2VA PDD LoRA;
- exactly 8 steps, `simple`, LoRA strength 1.0;
- no simultaneous Turbo or KJ model patch.

Purpose: second fast candidate; visual comparison with `quality-20` is still
required.

### `h3-structural-canny`

- live core containing official H3 Fun Control support and reference
  compatibility fixes;
- 2.30 GB pruned INT8 H3 Fun Control Union model patch;
- existing core Canny.

Purpose: lowest-dependency proof that structural control works.

### `h3-structural-depth`

- `h3-structural-canny`;
- the installed DA3 mono-large weight.

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
| H3 Fun Control Union, pruned INT8 | 2.30 GB |
| DA3 mono large | 1.34 GB |
| SDPose + RT-DETR | 2.04 GB |

A useful structural stack of SAM3 + pruned Fun Control + DA3 mono-large costs
roughly 5.38 GB before filesystem overhead. All three Turbo files consume
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

### Waves 1–4: completed technical installation

Completed independently and reconciled after each mutation: current core,
INT8 FL2VA/Ref2VA trunks, Turbo/PDD files, KJNodes, SAM3, DA3 mono-large,
SDPose/RT-DETR, and the compatible pruned Fun Control patch. Every model has a
matching digest and at least one bounded technical load/execute smoke. The
first full-width Fun Control attempt failed compatibility validation and was
removed before the corrected artifact was installed.

### Next wave: remaining visual characterization

Completed: the fixed-input `quality-20`/Turbo/PDD ladder, direct Canny/depth
Fun-Control comparisons, and an exact Hydra pass-through plus one causal affine
carrier. Remaining:

1. perform full-motion operator review of Canny, depth and Hydra affine output;
2. test SAM3 propagation on a short real video, then mask cleanup/projection;
3. test RT-DETR/SDPose on actual human material;
4. test reference plus structural control separately;
5. promote nothing from technical execution without a human visual verdict.

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

Installation is no longer the bottleneck. The host now has the selected INT8
trunks, every named Turbo/PDD profile, KJ utilities, tracked masks, depth, pose,
and compatible Fun Control. The next work is fixed-input visual evaluation and
canonical paired workflow export. Extra preprocessors, VHS, rgthree, preview
TAEs, and speculative kernel patches remain opt-in responses to a measured
need, not default dependencies.
