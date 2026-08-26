# Primary technical sources

Implementation contracts were checked against primary code and merged upstream
changes, not inferred from workflow screenshots:

- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official ComfyUI video load/create/save nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_video.py)
- [ComfyUI PR #15439: MiniMax H3 AddGuide](https://github.com/Comfy-Org/ComfyUI/pull/15439)
- [ComfyUI PR #15375: continuous per-token denoise masks](https://github.com/Comfy-Org/ComfyUI/pull/15375)
- [AddGuide embedded documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MiniMaxH3AddGuide/en.md)
- [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes)
- [ComfyUI frontend workflow service](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/platform/workflow/core/services/workflowService.ts)

Inspected community implementations are design references, never runtime
dependencies or behavioral proof:

- [MiniMax H3 Continuation](https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation)
- [MMH3Tools](https://github.com/ckinpdx/ComfyUI-MMH3Tools)
- [H3 Continuum](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum)

The checked official surface establishes optional first/last images, ordered
Ref2VA references, arbitrary-frame AddGuide composition, packed visual and
structural-audio streams, and independent continuous noise masks consumed by
the H3 sampler. CAUCE preserves those semantics while adding exact timebase,
placement, mask-construction, replacement, persistence, and rollback
primitives. Community techniques become production capabilities only after
their mechanism is reproduced transparently and live evidence is retained.

The official source was rechecked on 2026-08-26. The current H3 surface exposes
`MiniMaxH3ImageToVideo`, `MiniMaxH3ReferenceToVideo`, `MiniMaxH3AddGuide`, and
`MiniMaxH3SigmaShift`; the core video path exposes `LoadVideo`, `CreateVideo`,
and `SaveVideo`. These upstream observations inform readiness requirements but
do not prove that the laboratory is on the same commit. Live `/object_info`
remains authoritative.
