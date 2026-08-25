# Technical sources

Primary implementations used to define the current contracts:

- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official ComfyUI MiniMax H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official AddGuide embedded documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MiniMaxH3AddGuide/en.md)
- [MiniMax H3 native continuation pack](https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation)
- [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes)
- [ComfyUI JavaScript extension overview](https://docs.comfy.org/custom-nodes/js/javascript_overview)
- [ComfyUI frontend workflow service](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/platform/workflow/core/services/workflowService.ts)

Current specs derive H3 facts from implementation behavior: 24 fps, packed
visual/structural-audio latent streams, `17k+5` frame counts, optional
first/last keyframes, ordered reference blocks, arbitrary-frame AddGuide chains,
and coherent video/audio flow shifts. Community claims are not promoted into a
canonical workflow until their mechanism is inspectable and a live experiment
produces relevant evidence.
