# Primary technical sources

Implementation contracts were checked against primary code and merged upstream
changes, not inferred from workflow screenshots:

- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official H3 prompt-writing skill](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/.agents/skills/h3-prompt-writing)
- [Official H3 base-mode prompt guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/.agents/skills/h3-prompt-writing/references/base-en.txt)
- [Official H3 Ref2VA prompt guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/.agents/skills/h3-prompt-writing/references/ref-en.txt)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official ComfyUI video load/create/save nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_video.py)
- [ComfyUI PR #15439: MiniMax H3 AddGuide](https://github.com/Comfy-Org/ComfyUI/pull/15439)
- [ComfyUI PR #15375: continuous per-token denoise masks](https://github.com/Comfy-Org/ComfyUI/pull/15375)
- [ComfyUI PR #15697: MiniMax H3 prompt embeddings](https://github.com/Comfy-Org/ComfyUI/pull/15697)
- [ComfyUI PR #15908: MiniMax H3 PDD LoRA support](https://github.com/Comfy-Org/ComfyUI/pull/15908)
- [ComfyUI PR #15735: proposed native H3 AV latent builder](https://github.com/Comfy-Org/ComfyUI/pull/15735)
- [ComfyUI PR #15860: superseded H3 Fun ControlNet proposal](https://github.com/Comfy-Org/ComfyUI/pull/15860)
- [ComfyUI PR #15975: merged H3 ControlNet model-patch path](https://github.com/Comfy-Org/ComfyUI/pull/15975)
- [ComfyUI PR #16020: merged reference/keyframe control support and dynamic-VRAM prefetch correction](https://github.com/Comfy-Org/ComfyUI/pull/16020)
- [ComfyUI PR #15988: pending H3 mask-velocity conversion correction](https://github.com/Comfy-Org/ComfyUI/pull/15988)
- [ComfyUI issue #15978: H3 masking regression report](https://github.com/Comfy-Org/ComfyUI/issues/15978)
- [ComfyUI issue #15981: H3 mask grid-artifact report](https://github.com/Comfy-Org/ComfyUI/issues/15981)
- [ComfyUI PR #15808: merged H3 special-token fix](https://github.com/Comfy-Org/ComfyUI/pull/15808)
- [ComfyUI issue #15805: prompt-dependence failure report](https://github.com/Comfy-Org/ComfyUI/issues/15805)
- [ComfyUI PR #15983: proposed H3 memory-estimation correction](https://github.com/Comfy-Org/ComfyUI/pull/15983)
- [Official ComfyUI H3 workflow templates](https://github.com/Comfy-Org/workflow_templates/tree/main/templates)
- [DiffSynth-Studio H3 training documentation](https://github.com/modelscope/DiffSynth-Studio/blob/main/docs/en/Model_Details/MiniMax-H3.md)
- [FrescoDiffusion tiled regeneration](https://arxiv.org/abs/2603.17555)
- [STCDiT anchor-frame video super-resolution](https://arxiv.org/abs/2511.18786)
- [Warped Diffusion for video inverse problems](https://arxiv.org/abs/2410.16152)
- [VGI-Bench process-sensitive video-generation evaluation](https://arxiv.org/abs/2608.19583)
- [FilmBench fine-grained film-oriented video evaluation](https://arxiv.org/abs/2607.24241)
- [FlexTraj point-trajectory video control](https://arxiv.org/abs/2510.08527)
- [MagicMotion dense-to-sparse trajectory guidance](https://arxiv.org/abs/2503.16421)
- [MiniMax H3 community-maintained integration index](https://github.com/MiniMax-AI/awesome-minimax-h3-integration)
- [Alibaba PAI MiniMax H3 Fun ControlNet Union](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union)
- [Alibaba PAI MiniMax H3 PDD acceleration LoRAs](https://huggingface.co/alibaba-pai/MiniMax-H3-Acc-LoRAs)
- [Official ComfyUI SAM3 detection and video-tracking nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_sam3.py)
- [Official Comfy-Org SAM3.1 checkpoint](https://huggingface.co/Comfy-Org/sam3.1/blob/main/checkpoints/sam3.1_multiplex_fp16.safetensors)
- [Official ComfyUI Depth Anything 3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_depth_anything_3.py)
- [Official ComfyUI SDPose nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_sdpose.py)
- [Seedance 2.0 official launch](https://seed.bytedance.com/en/blog/seedance-2-0-%E6%AD%A3%E5%BC%8F%E5%8F%91%E5%B8%83)
- [Seedance 2.5 official launch](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [Seedance 2.5 official product page](https://seed.bytedance.com/en/seedance2_5)
- [BytePlus Seedance API capability documentation](https://docs.byteplus.com/en/docs/byteplus_las/video_gen_enhanced)
- [ComfyUI v0.34.0 release](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.34.0)
- [ComfyUI frontend v1.53.2 release](https://github.com/Comfy-Org/ComfyUI_frontend/releases/tag/v1.53.2)
- [Official H3 mask projection and preserved-state injection](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/model_base.py)
- [AddGuide embedded documentation](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/MiniMaxH3AddGuide/en.md)
- [ComfyUI server routes](https://docs.comfy.org/development/comfyui-server/comms_routes)
- [ComfyUI frontend workflow service](https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/platform/workflow/core/services/workflowService.ts)
- [Official Comfy Registry metadata specification](https://docs.comfy.org/registry/specifications)
- [Official Comfy Registry publishing guide](https://docs.comfy.org/registry/publishing)
- [KJNodes](https://github.com/kijai/ComfyUI-KJNodes)
- [KJNodes MiniMax H3 implementation](https://github.com/kijai/ComfyUI-KJNodes/blob/main/nodes/minimax_nodes.py)
- [Comfy-Org MiniMax H3 repack and Comfy-format Turbo LoRAs](https://huggingface.co/Comfy-Org/MiniMax-H3)
- [LightX2V MiniMax H3 Turbo LoRAs](https://huggingface.co/lightx2v/Minimax-h3-Turbo)
- [Kijai converted pruned PDD LoRAs](https://huggingface.co/Kijai/MiniMax-H3-experimental/tree/main/loras)
- [ComfyUI ControlNet Auxiliary Preprocessors](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite)
- [rgthree-comfy](https://github.com/rgthree/rgthree-comfy)
- [H3 prompt journal](https://github.com/LoveRain1997/h3-prompt-journal)
- [Community H3 Guide nodepack](https://github.com/ethanfel/ComfyUI-MiniMax-H3-Guide)
- [Community H3 Prompt Writer](https://github.com/duckyshell/ComfyUI-MiniMaxH3-Prompt-Writer)

Inspected community implementations are design references, never runtime
dependencies or behavioral proof:

- [MiniMax H3 Continuation](https://github.com/ttulttul/ComfyUI-Minimax-H3-Continuation)
- [MMH3Tools](https://github.com/ckinpdx/ComfyUI-MMH3Tools)
- [H3 Continuum](https://github.com/ukr8b3g-cmyk/ComfyUI-H3-Continuum)
- [Community H3 V2V refinement workflows](https://github.com/mdkberry/comfyui_workflows/tree/main/workflows_by_model/Minimax-H3)
- [Community MiniMax H3 latent upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler)
- [ComfyUI-Continuity H3 native latent second pass](https://github.com/roadmaus/ComfyUI-Continuity)
- [H3 latent upscaler experiments](https://github.com/rockerBOO/h3-latent-upscaler)
- [MiniMax H3 Timed References](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Timed-References)
- [MiniMax H3 Tone Compensate](https://github.com/rkfg/ComfyUI-MiniMaxH3-ToneCompensate)
- [H3 GuideMaster](https://github.com/MajoorWaldi/ComfyUI-Majoor-H3-GuideMaster)
- [H3 Native Masked Context](https://github.com/wjc573/ComfyUI-H3-Native-Masked-Context)
- [MMH3 UltimateUpscale](https://github.com/irregular-dressing1531/Comfyui-MMH3-UltimateUpscale)

The checked official surface establishes optional first/last images, ordered
Ref2VA references, arbitrary-frame AddGuide composition, packed visual and
structural-audio streams, and independent continuous noise masks consumed by
the H3 sampler. CAUCE preserves those semantics while adding exact timebase,
placement, mask-construction, replacement, persistence, and rollback
primitives. Community techniques become production capabilities only after
their mechanism is reproduced transparently and live evidence is retained.

Learned latent upscalers remain research references, not dependencies of the
current 28-node CAUCE surface. H3 Fun ControlNet and reference/keyframe-plus-
control support were merged upstream through #15975 and #16020 and have since
executed in the laboratory. Canny and depth control, a 34-run control matrix,
and two Hydra-carrier handoff tests are retained as technical evidence; none is
yet a visually promoted production capability. Open mask-correctness questions
still require per-workflow characterization.

The official source was rechecked on 2026-08-31. The released H3 surface exposes
`MiniMaxH3ImageToVideo`, `MiniMaxH3ReferenceToVideo`, `MiniMaxH3AddGuide`, and
`MiniMaxH3SigmaShift`, plus `EmptyMiniMaxH3LatentAV`; the core video path
exposes `LoadVideo`, `CreateVideo`, and `SaveVideo`. ComfyUI `v0.34.0` is pinned
at commit
`12d5279438bfefc058a269eae805ceab6047777f`; the 2026-08-31 source observation
used master commit `95d755cd8107a72258d452b5d3657273d571f07d` only to watch unreleased work.
These upstream observations inform readiness requirements but do not prove
that the laboratory is on the same commit. Live `/object_info` remains
authoritative. See [H3 capability map](H3_CAPABILITY_MAP.md) for the native-first
workflow rebuild and the exact boundary between released, project, pending and
excluded mechanisms.

Presence in `/object_info` is not the same as canonical use. The 2026-08-31
official I2V template and the known-running laboratory FL2VA workflow connect
the model directly to the guider and scheduler; the sigma-shift node is retained
only as an explicit comparison variable.

See [Native movement control research](MOVEMENT_CONTROL_RESEARCH.md) for the
project-specific evidence audit, current community probe, model-routing policy
and controlled H3/Seedance experiment queue.

See [H3 intent routing and latent operator space](H3_INTENT_ROUTING.md) for the
architecture-derived operator grammar and the boundary between released,
near-native, model-patch, training-required and rejected interventions.

See [Modular ComfyUI extension ecosystem](NODEPACK_ECOSYSTEM.md) for the
external-pack adoption classes, KJNodes whitelist, official auxiliary weights,
installation protocol and developer watch list. See
[H3 acceleration profiles](ACCELERATION_PROFILES.md) for family-matched
Turbo/PDD execution modes.

See [H3 prompting as an experimental control surface](H3_PROMPTING.md) for the
pinned public grammar, exact one-variable prompt matrices, evaluation protocol,
and the boundary between official syntax, community hypotheses and project
evidence.
