# Primary technical sources

Implementation contracts were checked against primary code and merged upstream
changes, not inferred from workflow screenshots:

- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official ComfyUI video load/create/save nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_video.py)
- [ComfyUI PR #15439: MiniMax H3 AddGuide](https://github.com/Comfy-Org/ComfyUI/pull/15439)
- [ComfyUI PR #15375: continuous per-token denoise masks](https://github.com/Comfy-Org/ComfyUI/pull/15375)
- [Official H3 mask projection and preserved-state injection](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/model_base.py)
- [AddGuide embedded documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MiniMaxH3AddGuide/en.md)
- [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes)
- [ComfyUI frontend workflow service](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/platform/workflow/core/services/workflowService.ts)

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

The official source was rechecked on 2026-08-26. The current H3 surface exposes
`MiniMaxH3ImageToVideo`, `MiniMaxH3ReferenceToVideo`, `MiniMaxH3AddGuide`, and
`MiniMaxH3SigmaShift`; the core video path exposes `LoadVideo`, `CreateVideo`,
and `SaveVideo`. These upstream observations inform readiness requirements but
do not prove that the laboratory is on the same commit. Live `/object_info`
remains authoritative.
