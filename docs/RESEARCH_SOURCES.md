# Primary technical sources

Implementation contracts were checked against primary code and merged upstream
changes, not inferred from workflow screenshots:

- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official ComfyUI video load/create/save nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_video.py)
- [ComfyUI PR #15439: MiniMax H3 AddGuide](https://github.com/Comfy-Org/ComfyUI/pull/15439)
- [ComfyUI PR #15375: continuous per-token denoise masks](https://github.com/Comfy-Org/ComfyUI/pull/15375)
- [ComfyUI PR #15697: MiniMax H3 prompt embeddings](https://github.com/Comfy-Org/ComfyUI/pull/15697)
- [ComfyUI PR #15908: MiniMax H3 PDD LoRA support](https://github.com/Comfy-Org/ComfyUI/pull/15908)
- [ComfyUI PR #15735: proposed native H3 AV latent builder](https://github.com/Comfy-Org/ComfyUI/pull/15735)
- [ComfyUI PR #15860: proposed H3 Fun ControlNet support](https://github.com/Comfy-Org/ComfyUI/pull/15860)
- [ComfyUI PR #15975: proposed H3 ControlNet model-patch path](https://github.com/Comfy-Org/ComfyUI/pull/15975)
- [Official ComfyUI H3 workflow templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates)
- [MiniMax H3 community-maintained integration index](https://github.com/MiniMax-AI/awesome-minimax-h3-integration)
- [Alibaba PAI MiniMax H3 Fun ControlNet Union](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union)
- [ComfyUI v0.34.0 release](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.34.0)
- [ComfyUI frontend v1.53.2 release](https://github.com/Comfy-Org/ComfyUI_frontend/releases/tag/v1.53.2)
- [Official H3 mask projection and preserved-state injection](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/model_base.py)
- [AddGuide embedded documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MiniMaxH3AddGuide/en.md)
- [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes)
- [ComfyUI frontend workflow service](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/platform/workflow/core/services/workflowService.ts)
- [Official Comfy Registry metadata specification](https://docs.comfy.org/registry/specifications)
- [Official Comfy Registry publishing guide](https://docs.comfy.org/registry/publishing)

Inspected community implementations are design references, never runtime
dependencies or behavioral proof:

- [MiniMax H3 Continuation](https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation)
- [MMH3Tools](https://github.com/ckinpdx/ComfyUI-MMH3Tools)
- [H3 Continuum](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum)
- [Community H3 V2V refinement workflows](https://github.com/mdkberry/comfyui_workflows/tree/main/workflows_by_model/Minimax-H3)
- [Community MiniMax H3 latent upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler)

The checked official surface establishes optional first/last images, ordered
Ref2VA references, arbitrary-frame AddGuide composition, packed visual and
structural-audio streams, and independent continuous noise masks consumed by
the H3 sampler. CAUCE preserves those semantics while adding exact timebase,
placement, mask-construction, replacement, persistence, and rollback
primitives. Community techniques become production capabilities only after
their mechanism is reproduced transparently and live evidence is retained.

The learned latent upscaler and local high-resolution in-context regeneration
remain isolated experiments, not dependencies of the current 20-node CAUCE
surface. The still-draft H3 Fun ControlNet integration is likewise deferred;
neither is represented as an implemented production operation.

The official source was rechecked on 2026-08-30. The released H3 surface exposes
`MiniMaxH3ImageToVideo`, `MiniMaxH3ReferenceToVideo`, `MiniMaxH3AddGuide`, and
`MiniMaxH3SigmaShift`; the core video path exposes `LoadVideo`, `CreateVideo`,
and `SaveVideo`. ComfyUI `v0.34.0` is pinned at commit
`12d5279438bfefc058a269eae805ceab6047777f`; the 2026-08-30 source observation
used master commit `8a33128f2f8c5585c57486c07de481241e70a39c` only to watch unreleased work.
These upstream observations inform readiness requirements but do not prove
that the laboratory is on the same commit. Live `/object_info` remains
authoritative. See [H3 capability map](H3_CAPABILITY_MAP.md) for the native-first
workflow rebuild and the exact boundary between released, project, pending and
excluded mechanisms.
