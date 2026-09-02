# Modular ComfyUI nodepack ecosystem

Checked on 2026-09-01. This document defines how external ComfyUI nodepacks
may extend the laboratory without turning CAUCE into a mega-pack or making
canonical H3 workflows depend on UI conveniences.

## Architectural rule

The runtime is split into five independently replaceable layers:

```text
official ComfyUI + official H3 nodes
  -> deterministic CAUCE data operations
  -> optional generic media/control sources
  -> optional authoring and observability tools
  -> project graphs, receipts and acceptance evidence
```

An external pack is admitted only when it supplies one of these bounded
functions:

1. a data transform not already available in ComfyUI or CAUCE;
2. an official-model input source, such as a depth or pose preprocessor;
3. non-destructive observability;
4. a measured runtime workaround for an actual resource failure.

It must not silently become a second sampler, prompt language, model manager,
timeline, persistence layer or project ontology. Canonical API graphs use
direct links and ordinary Comfy datatypes. Frontend-only routing and bypass
nodes are authoring conveniences, not serialized workflow requirements.

## Adoption classes

| Class | Meaning | Locking and evidence |
| --- | --- | --- |
| `core` | Required by every canonical H3 graph | Exact ComfyUI/CAUCE commits and live `/object_info` |
| `optional-data` | Produces standard `IMAGE`, `MASK`, `VIDEO`, `MODEL` or equivalent inputs | Exact public commit, node whitelist and one isolated restart |
| `optional-observability` | Preview or diagnostic only; disabling it must not change the saved result | Exact public commit plus fixed-seed output-equivalence test |
| `conditional-runtime` | Activated only to solve a measured OOM or runtime limit | Baseline/variant peak memory, duration and output comparison |
| `research-only` | Source of mechanisms and test hypotheses | No production graph dependency |
| `rejected` | Duplicate, opaque, unlicensed, incompatible or empirically harmful | Record the reason; do not install by habit |

## Recommended modules

### KJNodes: bounded adoption

Repository: <https://github.com/kijai/ComfyUI-KJNodes>

Observed source lock:

```text
repository  kijai/ComfyUI-KJNodes
commit      e8e88f7c88e3f6205b122f5de87e69a09fbce5ac
license     GPL-3.0
package     1.5.0
```

KJNodes is valuable because it contains generic transforms and because Kijai
regularly moves proven H3 fixes upstream into ComfyUI. Installing the pack does
not mean adopting every node.

Recommended whitelist:

| Function | Nodes or family | Class | Rule |
| --- | --- | --- | --- |
| Generic continuous-mask authoring | `CreateGradientMask`, `CreateFadeMaskAdvanced`, `GrowMaskWithBlur`, `RemapMaskRange`, `MaskBatchMulti`, `OffsetMask`, `ResizeMask` | `optional-data` | Feed standard `MASK` into CAUCE/native H3 projection; do not duplicate these transforms in CAUCE |
| Low-cost H3 previews | `ModelPreviewOverrideKJ`, `GetPreviewOverrideFramesKJ` | `optional-observability` | Pair with the separately pinned H3 TAE; saved output must remain unchanged |
| Feed-forward token chunking | `MiniMaxChunkFeedForward` | `conditional-runtime` | Use only after a baseline OOM or measured peak-memory need; fixed-seed A/B required |
| Lower-memory attention | `MiniMaxLowVRAMAttention` | `conditional-runtime` | Experimental model patch; fixed-seed numerical and visual A/B required |

Do not use as canonical dependencies:

- `MiniMaxH3TokenCounter`, because
  `CauceH3InspectPackedSequence` already provides project-owned exact row
  accounting and receipts;
- KJ Set/Get routing in saved API graphs, because hidden frontend indirection
  makes graph provenance harder to audit;
- `MiniMaxH3MemoryEfficientSageAttentionPatch` on the RTX 5090 until its
  Blackwell kernel compatibility is independently verified and an actual need
  exists;
- broad image/video helpers already provided by core unless a concrete graph
  demonstrates a missing transform.

KJNodes requirements are runtime mutations. They must be installed inside the
portable Comfy Python environment, never into an unrelated system Python.

### Kijai H3 TAE: preview weight

Repository: <https://huggingface.co/Kijai/MiniMax-H3-TAE/tree/main>

Observed weight lock:

```text
repository revision  a213ac8bf2f148b4f32372279a7f207846978900
file                 vae_approx/taeh3.safetensors
size                 9,791,388 bytes
sha256               f0f60fa072089997f817402098c2fd90777cb2660dd79cf5df42fc1e3e08e527
license               Apache-2.0
```

This is a cheap per-step visual diagnostic, not a decoder for accepted output.
The TAE must live under the standard `models/vae_approx` path. A comparison
must prove that preview-off and preview-on runs submit the same graph semantics
and produce the same final native state/output within the declared tolerance.

Do not also install `ComfyUI-MiniMaxH3-PreviewOverride`: it overlaps the generic
KJNodes preview route, bundles a larger preview weight and creates another pack
to maintain without adding a distinct H3 capability.

### ControlNet Auxiliary Preprocessors: structural-input sources

Repository: <https://github.com/Fannovel16/comfyui_controlnet_aux>

This pack produces ordinary control images. Canny, Depth Anything, HED, MLSD,
OpenPose and DWPose align with the control modalities accepted by the H3 Fun
Control Union checkpoint. It does not replace the official H3 control model or
sampler.

Adoption is deferred until the live runtime contains the merged H3 model-patch
and reference/keyframe compatibility changes. Download only the detector model
needed by the current experiment; do not populate the entire preprocessor model
zoo on a host with approximately 120 GB free.

### VideoHelperSuite: authoring and remote preview only

Repository: <https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite>

VHS remains useful for bounded previews, frame selection, rate overrides and
remote authoring over the tunnel. Core ComfyUI already owns canonical
`LoadVideo`, `CreateVideo` and `SaveVideo`, while CAUCE owns exact half-open
ranges. Therefore production API graphs stay on core video nodes unless a
specific VHS transform is necessary and recorded.

### rgthree: frontend ergonomics only

Repository: <https://github.com/rgthree/rgthree-comfy>

Group bypass, Power LoRA and routing aids may improve interactive authoring.
They do not add H3 mathematics. Canonical API exports must be materialized with
explicit direct links and must remain executable without rgthree frontend
state.

## Research-only packs and authors

| Source | What to learn | Why it is not a production dependency now |
| --- | --- | --- |
| [MMH3Tools](https://github.com/ckinpdx/ComfyUI-MMH3Tools) / `ckinpdx` | Native latent-to-reference transport, AV-axis handling, overlap/continuation, context-window and in-context regeneration hypotheses | Very broad sampler/state surface, rapid churn and no detected license; use as a research oracle, not code to vendor |
| [ComfyUI-UtilsCollection](https://github.com/silveroxides/ComfyUI-UtilsCollection) / `silveroxides` | H3 conditioning probes, CLIP/Qwen projection and timed visual experiments | Large AGPL pack overlapping official conditioning; evaluate individual mechanisms only |
| [MiniMax H3 Guide](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide) / `EthanFel` | Transparent prompt/reference planning and routing UX | CAUCE deliberately has no semantic entity layer or second prompt language |
| [ComfyUI-Continuity](https://github.com/roadmaus/ComfyUI-Continuity) / `Roadmaus` | Cross-model product ergonomics and second-pass comparisons | One convenience node spans several model families and obscures canonical low-level wiring |
| [RES4LYF](https://github.com/ClownsharkBatwing/RES4LYF) / `ClownsharkBatwing` | Sampler and scheduling research | No sampler patch enters production without a bounded H3-specific causal A/B |
| [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF) / `city96` | Quantization compatibility and lower-memory model loading | Current laboratory H3 weights already fit; no present resource failure justifies another loader |

A research repository may be technically excellent and still be the wrong
production dependency. License, narrowness, upstream alignment and evidence are
separate gates.

## Developers and upstreams to follow

### Priority 0: source of truth or direct H3 maintainers

- `Comfy-Org/ComfyUI`, `comfyanonymous` and current H3 code owners: released
  runtime behavior and merge history;
- `Kijai`: H3 core contributions, KJNodes, optimized weights and preview
  models;
- `MiniMax-AI`: model architecture, checkpoints and official usage;
- `Alibaba PAI`: H3 Fun Control Union model and DiffSynth integration.

### Priority 1: high-signal experiments

- `ckinpdx`: fast empirical work on native H3 state and context handling;
- `Kosinkadink`: video workflow semantics and core-compatible utilities;
- `Fannovel16`: maintained structural preprocessors;
- `silveroxides`: advanced conditioning and encoder probes;
- `EthanFel`: reference/prompt routing design.

### Priority 2: supporting infrastructure

- `rgthree` and `ltdrdata`: authoring and Manager operations;
- `city96`: quantized loading;
- `ClownsharkBatwing`: sampler research.

Useful saved searches:

```text
repo:Comfy-Org/ComfyUI MiniMaxH3 is:pr sort:updated-desc
repo:kijai/ComfyUI-KJNodes MiniMax is:issue,pr sort:updated-desc
author:kijai repo:Comfy-Org/ComfyUI is:pr
repo:ckinpdx/ComfyUI-MMH3Tools sort:updated-desc
```

## Safe installation protocol

Never combine a ComfyUI core update, nodepack install and model download in one
unknown mutation window.

For each external module:

1. record the clean queue, current runtime manifest and free disk;
2. require a public repository and choose one exact commit;
3. install only that repository through the bounded repository/Manager plane;
4. restart the Comfy process once; never reboot or mutate CUDA/PyTorch;
5. capture fresh `/object_info` and import errors;
6. verify the intended node whitelist and confirm core H3/CAUCE nodes remain;
7. run the smallest technical smoke and retain its receipt;
8. compare against the unchanged baseline when the module patches a model;
9. pin the module in a runtime profile only after a real accepted graph uses it.

Unknown HTTP outcome is not permission to repeat an install. Reconcile the
Manager/repository state first. No module may install a private Git URL on the
shared host, because an interactive credential prompt can stall the Comfy
process behind the tunnel.

## Immediate recommendation

The next bounded adoption should be:

1. KJNodes at the recorded public commit;
2. only its continuous-mask utilities and generic H3 preview path;
3. the pinned 9.8 MB Kijai H3 TAE;
4. fixed-seed preview equivalence and a standard `MASK` -> CAUCE -> native H3
   mask smoke;
5. no attention/FFN patch unless a baseline actually exhausts memory.

Structural control is a separate later window: first update and capture a core
revision containing the merged model-patch and reference/keyframe compatibility
changes, then add only the chosen `controlnet_aux` preprocessor and its required
weight.
