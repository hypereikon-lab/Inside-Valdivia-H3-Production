# Native movement control research

Checked on 2026-08-31. This document extends the supplied early research on
Seedance 2.0, Seedance 2.5 and MiniMax H3 into a project-specific, falsifiable
research program. It is not a catalog of every advertised feature. It asks a
narrower question:

> Which native or near-native mechanisms can measurably direct, preserve,
> transfer, compose and repair movement for Inside Valdivia?

The fixed soundtrack remains an editorial clock only. Generated audio, audio
conditioning, training, LoRA work, acceleration and streaming are outside this
program. Images and clips remain arbitrary media. No semantic scene/entity
ontology is introduced.

## Executive conclusion

There is no single scalar called "movement control." The current systems expose
six materially different control channels:

1. **semantic instruction**: text asks for an action, camera relation or
   transformation;
2. **boundary state**: first and/or last images declare exact-looking visual
   states at the temporal boundary;
3. **time-local state**: an H3 still or clip guide is placed at an exact target
   frame;
4. **motion carrier**: a reference video supplies observed dynamics, timing,
   camera motion and possibly appearance;
5. **preservation field**: a continuous spatiotemporal mask specifies what H3
   may reconsider and what supplied state it must preserve;
6. **structural trajectory**: an external per-frame representation such as
   depth, edges or pose constrains geometry through an H3-specific ControlNet.

The first five are available through the current released H3/ComfyUI surface.
The sixth now exists as a released H3 checkpoint, but its two ComfyUI
integrations are still open pull requests and must remain a research watch item.

The practical strategy is therefore:

- use local H3 as the high-volume causal laboratory;
- express decisive temporal states with endpoints or AddGuide instead of hoping
  that longer prose will repair the trajectory;
- use reference video when the desired datum is motion rather than a single
  state;
- use native masks to localize authority, not to describe motion;
- reserve Seedance credits for controlled comparisons and final candidates that
  have already passed a cheaper H3 probe;
- treat every community recipe as a hypothesis until the mechanism survives a
  fixed-input ablation.

The complete architecture-derived grammar behind these channels is documented
in [H3 intent routing and latent operator space](H3_INTENT_ROUTING.md).

## 1. Audit of the supplied research

The supplied document is a strong capability inventory. Its most valuable
contribution is recognizing multimodal generation as a composition of asset
roles, temporal constraints and preservation rules rather than as prose-only
prompting. This project keeps that framing, with four corrections.

### 1.1 Keep as mechanisms

- first, last and first/last boundaries;
- ordered image and video references;
- source video as a temporal skeleton;
- H3 arbitrary-frame still and clip guides;
- H3 continuous native denoise masks;
- Seedance 2.5 long generation, white-model translation and timestamp editing;
- reference ablation, failure classification and process-sensitive evaluation;
- explicit route/version logging.

### 1.2 Keep as useful metaphors, not implementation facts

- "multimodal program interpreter";
- "prompt compiler";
- "retention contract";
- "state machine";
- "reference graph."

These phrases can organize human intent, but they must not be mistaken for an
exposed model schema or a guarantee that references are independently typed.
They earn operational meaning only through one-variable tests.

### 1.3 Downgrade to hypotheses

- exact transfer of a reference video's motion independently of appearance;
- reliable assignment of one reference to identity, another to camera and a
  third to timing without interference;
- automatic cross-model equivalence between Seedance references and H3 Ref2VA;
- prompt-only repair of a trajectory that was selected incorrectly early in
  denoising;
- broad claims derived from one successful public example.

### 1.4 Remove from the present program

- generated audio and audiovisual causality;
- soundtrack encoding into the model;
- dialogue, lip sync and voice control;
- training, fine-tuning and LoRA development;
- acceleration and streaming;
- direct affine, advection, depth-warp or feedback transformations of H3 latent
  tensors. Project experiments already found this family to produce ghosting
  rather than useful control, and diffusion research explains why naive latent
  warping fails when the denoiser is not equivariant to the chosen transform.

H3-Context-IR and H3-Regenerate-2K must also remain correctly scoped. They are
hosted MiniMax modules, not latent subsystems silently available inside the
open H3-Base checkpoint. A local ComfyUI H3-Base run does not call either one.

## 2. The control planes that actually reach H3

### 2.1 Semantic instruction

The Qwen vision-language path reads the prompt and the media presented to it.
It can assign semantic roles, describe an action and state camera behavior, but
it does not make a supplied picture an exact temporal anchor by itself.

This distinction matters for the new community Timed References nodes. They
present an image or selected video frames to Qwen at a timestamp, but do not
VAE-encode them, do not enter `minimax_refs`, and do not consume a native H3
reference slot. They create **time-addressed semantic evidence**, not exact
state. Their value should be measured against both ordinary Ref2VA and
`MiniMaxH3AddGuide`, not conflated with either one.

### 2.2 Boundary state

`MiniMaxH3ImageToVideo` supports no image, first image, last image, or both. A
first frame declares initial appearance and composition. A last frame declares
terminal evidence. First/last generation is a two-boundary interpolation
problem, not merely an image-to-video prompt with two references.

Boundary images constrain state, not the path taken between the states. When
the desired path is specific, an interior guide or motion reference is the next
native control, not more endpoint prose.

### 2.3 Time-local target-aligned guide

`MiniMaxH3AddGuide` encodes a still or legal-length clip as separate condition
rows whose RoPE coordinates align with a specific target frame. It does not
copy those rows into the target latent. A still carries state. A clip carries
state plus local temporal derivatives: direction, velocity, acceleration,
deformation and camera flow over its short interval.

This gives a direct, testable hierarchy:

```text
still guide       -> target-aligned local state evidence
short clip guide  -> target-aligned state plus local motion
two guide clips   -> left and right dynamic context around an unknown interval
```

It is the cleanest released primitive for asking whether extra dynamic context
improves a bridge or continuation.

### 2.4 Native reference video

H3 Ref2VA uses a video reference in two ways:

- Qwen receives sampled visual observations with timestamps for semantic
  interpretation;
- the H3 DiT receives VAE-encoded reference state through the native reference
  path.

Reference video is therefore richer than a text description and less exact in
target time than AddGuide. It may carry motion, camera, rhythm, appearance and
layout together. "Motion transfer" is an empirical factorization problem: the
project must determine which components survive and which interfere.

Reference resolution and sampling rate are control variables, not merely
quality settings. A deliberately lower-bandwidth driver may preserve gross
motion while reducing unwanted appearance detail; a high-resolution reference
may strengthen identity or texture but also transfer more of the source scene.
That community observation is plausible but unproven locally.

### 2.5 Continuous preservation field

The released H3 sampler consumes continuous video noise masks on the packed AV
state. For the visual stream, a mask is pooled to H3 patch tokens and quantized
to `1/256`. It specifies sampling authority:

```text
0.0  supplied state is strongly preserved
1.0  state is generated at the active H3 sigma
0..1 partial regeneration / transition of authority
```

A mask does not say "move right" or "accelerate." It says where and when the
model may alter supplied state. Its movement value comes from combining it with
known left/right context, a prompt, a reference driver or a structural control.

This supports:

- temporal inpainting between known contexts;
- interval retakes;
- spatial or animated-region edits;
- spatiotemporal intersections;
- soft boundary release;
- outpainting with a protected interior;
- controlled second-pass characterization.

The useful research variable is not simply hard versus soft mask. It is the
geometry of authority over time and space: protected scaffold size, temporal
feather, spatial falloff and interaction with the supplied context.

### 2.6 Structural trajectory: H3 Fun ControlNet Union

Alibaba PAI released an H3-specific ControlNet Union supporting Canny, depth,
HED, MLSD, pose and video inpainting. It attaches zero-initialized control
branches to five H3 transformer depths and exposes a control strength. This is
the first recent addition that changes the model's movement-control channel
rather than merely packaging existing H3 nodes.

Two ComfyUI integration approaches are still open:

- PR #15860: conventional ControlNet support;
- PR #15975: model-patch implementation.

The checkpoint and demonstration establish plausibility, not production
readiness in the laboratory. Installation is deferred until an implementation
is merged or a separately pinned test branch passes memory, correctness and
visual gates. The full checkpoint is large; community pruned variants are much
smaller but add their own provenance and quality questions. With approximately
120 GB free on the laboratory host, this is a deliberate future download, not
an exploratory Manager click.

## 3. New phenomena worth reproducing

The following are observations or deductions with a concrete falsification
test. They are not adopted truths.

### 3.1 Early trajectory commitment

VGI-Bench reports that later denoising steps seldom correct an initially wrong
process hypothesis. This predicts that a decisive interior state or structural
driver will outperform a longer prompt when the failure is topological or
temporal rather than cosmetic.

Test: same input and seed, compare prompt-only, prompt plus interior still, and
prompt plus short guide clip. Measure whether the intended ordering and motion
path appear, not only image quality.

### 3.2 Representation compatibility

The same benchmark finds open video models more sensitive to abstract or line
art inputs than to realistic visual inputs. This predicts that a rendered
motion driver, depth animation or edge video may communicate structure better
than a bare grid or symbolic sketch.

Test: encode the same motion as an RGB proxy, depth, edges and sparse pose.
Compare only when Fun ControlNet is available; ordinary Ref2VA and ControlNet
are separate conditions.

### 3.3 State versus local velocity

A still guide and a clip guide may show the same central frame while carrying
different information. If the clip improves the generated approach and exit,
the measurable gain comes from local motion context rather than appearance.

Test: derive the still from the center of the guide clip and keep every other
input fixed. Compare optical-flow direction and boundary jerk around the guide.

### 3.4 Target-aligned native guide versus semantic timestamp

AddGuide and Qwen-only Timed References can point to the same time while
affecting different channels.

The replacement test failed by spatially composing the semantic references
instead of treating them as target states. A subsequent midpoint-offset
Timed-Reference-plus-AddGuide trial restored a single-frame composition but was
also rejected by operator review as a useful slow-motion result. No hybrid
workflow is retained. Future work must reformulate the conditioning question,
not merely increase or interleave reference counts.

### 3.5 Reference bandwidth as factorization

Community reports suggest using a smaller motion reference to emphasize coarse
dynamics and a larger image reference for likeness. This is a bandwidth
hypothesis, not a magical role declaration.

Test: the same motion reference at 240p, 480p and the native maximum, plus a
fixed high-quality still identity reference. Measure motion correspondence and
appearance leakage separately.

### 3.6 Minimal preserved scaffold

Community masked-context users report that a narrow protected scaffold may be
enough to retain timing or cuts while allowing broad regeneration. The mask
therefore may exhibit a preservation threshold rather than a monotonic
quality relationship.

Test: preserve 100%, 50%, 25%, 10% and 5% of a known spatiotemporal scaffold,
with hard and smooth authority transitions. Look for the smallest region that
retains the intended motion topology without freezing the output.

### 3.7 Sparse structural keyposes

Early Fun ControlNet users report placing a pose for several repeated frames,
leaving the interval blank or neutral, then placing the next pose. This could
turn structural control into a sparse boundary interpolation problem.

Test after integration: two pose states repeated for 1, 3 and 6 frames, with a
black and mid-gray gap. Compare trajectory adherence, freezing and artifacts.
Do not generalize from the public six-frame recipe before this ablation.

### 3.8 Camera as relation, not a verb

Seedance community examples suggest that stable camera behavior improves when
the prompt states an invariant relationship between camera and subject rather
than only naming a move. For example, "the camera remains fixed to the
subject's chest while the world moves" is a constraint; "tracking shot" is a
label.

Test: same asset and seed where exposed, compare move label, relational
constraint and relational constraint plus negative shortcut. Estimate global
camera motion and subject-relative displacement.

### 3.9 Error copying as a fidelity probe

Users report that Fun ControlNet reproduces mistakes in a depth/control video
that ordinary H3 reference conditioning smooths over. If reproduced, the error
is useful diagnostic evidence: exact copying indicates structural adherence,
not quality.

Test: introduce one deliberate one-frame discontinuity into the control. An
accurate structural path should reproduce it; a semantic reference path should
usually reinterpret or smooth it.

### 3.10 Reference interference and capacity

Seedance 2.5 accepts many references, but count is not effective controllable
capacity. Extra media can compete, be ignored or entangle roles.

Test by addition, not by maximal packs: base prompt, then one motion video, then
one appearance image, then one spatial guide. Stop when the new asset no longer
produces a stable marginal gain.

## 4. What the newest community repositories actually add

| Project | Actual mechanism | Project decision |
| --- | --- | --- |
| H3 Fun ControlNet Union | New trained H3 structural-control branch | high-value watch item; do not install into production yet |
| MiniMax H3 Timed References | Qwen-only time-addressed image/video evidence | lightweight research candidate; compare against Ref2VA and AddGuide |
| H3 GuideMaster | Timeline UI and composition around released AddGuide | no new model capability; do not adopt a second UI |
| H3 Tone Compensate | Decoded RGB overlap-based additive/affine/LUT tone correction | potentially useful delivery utility, not movement control |
| H3 Native Masked Context | Packages released H3 mask/context preparation | overlaps CAUCE native-state responsibility; design comparison only |
| MMH3Tools / long-video packs | Context carry, masking, persistence and large convenience graphs | evidence source; avoid monolithic dependency |
| UltimateUpscale variants | Temporal chunking, spatial tiling and H3 resampling | mechanism reference; current quality claims remain unverified |
| prompt composers/directors | Prompt/UI packaging | no new H3 control plane; not a project dependency |

This table prevents repository count from being mistaken for capability count.
Most new packages wrap released nodes. The two genuinely distinct ideas found
in the current probe are structural ControlNet conditioning and Qwen-only timed
semantic references.

## 5. Model routing

### 5.1 Local H3-Base: mechanism laboratory

Use H3 for:

- large causal matrices and repeated seeds;
- exact first/last and internal guide comparisons;
- motion-reference bandwidth tests;
- mask topology and temporal inpainting;
- continuation, bridge and retake experiments;
- temporal densification and spatial regeneration characterization;
- future structural-control experiments;
- native-state persistence and chain/branch tests.

H3's local availability makes failed probes informative rather than expensive.
It is not automatically the final renderer for every accepted movement.

### 5.2 Seedance 2.0: short directorial and camera probe

Use 2.0 selectively for:

- short motion-reference transfer;
- camera-path scouting;
- first/last comparisons up to its route limit;
- checking whether a movement that H3 understands is rendered more cleanly by
  the hosted model.

FilmBench characterizes Seedance 2.0 as especially strong on camera movement,
focus and shot-scale control relative to other evaluated tasks. That is a
benchmark tendency, not a guarantee for arbitrary project imagery.

### 5.3 Seedance 2.5: longer constrained composition and revision

Use 2.5 when the experiment specifically needs:

- a 16--30 second control horizon;
- multi-round continuation;
- many references under one controlled addition sequence;
- white/clay-model translation;
- timestamp-localized editing;
- a camera edit of an existing candidate;
- a longer final candidate after the motion program is already understood.

The official release itself notes remaining difficulty with complex physics
and multi-subject interaction. Longer context and more references do not remove
the need for decomposition.

### 5.4 Route identity is part of the experiment

Official BytePlus documentation and the ByteDance product announce the model's
native envelope. Runway or another host may expose a different subset, defaults
or preprocessing layer. Every paid run must therefore record:

- visible product and model label;
- actual route/provider;
- duration, resolution and frame rate;
- source media hashes and reference order;
- exact prompt and negative constraints;
- seed if exposed;
- edit/extension mode and any hidden/default option visible in the UI;
- output hash and cost/credit receipt.

Never compare an unidentified "Seedance" output with a pinned local H3 run.

## 6. Controlled experimental program

The queue is ordered by information gain, not spectacle.

### Gate 0: runtime validity

#### R0.1 Prompt-dependence sentinel

An open ComfyUI issue reported pixel-identical H3 outputs for radically
different prompts under one INT8 setup. Before studying prompt syntax, run two
strongly disjoint prompts with identical seed and every other parameter fixed.
If the output is identical or nearly so, diagnose runtime/tokenization before
drawing artistic conclusions.

#### R0.2 Special-token and schema sentinel

Record ComfyUI commit/version, H3 node schemas, model hashes, quantization,
attention backend and the presence of the merged H3 special-token fix. A graph
that queues is not evidence that every conditioning channel reached the model.

#### R0.3 Hosted-route sentinel

Make one minimal Seedance 2.0 and 2.5 run using the same assets and record the
actual UI/route envelope. Do not spend on a matrix until the interface exposes
the assumed controls.

### Tier 1: local H3 control identity

#### H1 Boundary-control matrix

```text
text only
first image
last image
first + last image
```

Question: which motion features arise from the prompt and which arise from
boundary geometry?

#### H2 Exact state versus local motion

```text
interior still AddGuide
same central state as a 5-frame clip guide
22-frame clip guide
39-frame clip guide
```

Question: how far from the guide does dynamic influence extend?

#### H3 Semantic timestamp versus target-aligned native guide

```text
ordinary Qwen/native reference
Qwen-only timed reference
target-aligned AddGuide
timed reference + AddGuide
```

Question: are semantic identity and target-aligned native state complementary?

#### H4 Reference-video bandwidth

```text
240p / 2 fps semantic sampling
480p / 2 fps
native maximum / 2 fps
480p / higher semantic sampling
```

Keep the DiT reference clip and Qwen presentation paths explicitly identified.
Question: where is the best motion/appearance factorization?

#### H5 Context and authority field

Compare hard, linear, smoothstep and smootherstep temporal boundaries over the
same two-sided bridge. Then compare preserved scaffold fractions. Question:
which mask topology minimizes seam jerk and off-mask drift without freezing the
transition?

#### H6 Temporal densification

Use the existing native H3 plan that retains source anchors and regenerates the
interstitial token positions. Compare source clock, 2x target clock and a
deterministic non-generative interpolation reference. This remains experimental
until native H3 sampling and visuals pass.

#### H7 Spatial regeneration

Compare native latent resize and pixel/VAE re-encode at a fixed target size
over a denoise-strength ladder. Frame count and fps must remain unchanged.
Later tiling research should prefer per-step tile fusion with a global prior
over independently completed tiles plus a terminal crossfade.

### Tier 2: pending structural control

#### C1 Ref2VA versus Fun ControlNet

Use one driver represented as RGB video, depth and edges. Compare the native
reference path with each ControlNet mode at a strength ladder. This isolates
semantic motion imitation from framewise structural adherence.

#### C2 Sparse keypose interpolation

Use two and three structural keyposes with controlled repetition and neutral
gaps. Measure path adherence and whether the model invents a coherent
interpolation rather than holding or snapping.

#### C3 Animated spatial retake

Combine an animated mask with structural control inside the editable region.
Question: can geometry be redirected locally while the surrounding shot stays
native-state preserved?

These tests do not begin until the ComfyUI integration is pinned and the host
passes a separate storage/runtime gate.

### Tier 3: Seedance credit validation

#### S1 Camera relation language

Compare a camera-move label with a subject-relative invariant on the same short
source. Run one 2.0/2.5 pair only after the wording shows a stable distinction
in a cheaper pilot or is specifically testing a hosted-only behavior.

#### S2 Driver versus visualized movement plan

Compare one source motion video with a short rendered keypose/movement board.
The point is not to prove that more references are better; it is to identify
whether Seedance responds more reliably to observed motion or to explicit
intermediate state.

#### S3 2.0 versus 2.5 on one 15-second program

Keep assets, order, prompt and duration equal. This is the only valid basis for
choosing a default between the two versions for that class of movement.

#### S4 H3 motion spine to Seedance renderer

Take one H3 candidate with accepted motion but insufficient finish and use it as
the only motion driver for Seedance. Add appearance media one at a time. This
tests a real division of labor: H3 discovers/constructs motion; Seedance renders
the selected trajectory.

#### S5 Timestamp-localized retake

On an otherwise accepted 2.5 output, edit one bounded interval. Measure change
inside and outside the requested interval. The test fails if improvement
requires accepting broad uncontrolled drift.

## 7. Measurement

No single metric accepts a video. The following diagnostics answer different
questions and accompany visual judgment.

### State fidelity

- endpoint and guide-frame LPIPS/SSIM;
- DINO or equivalent feature similarity where appearance is relevant;
- local crop comparison for the actual controlled region.

### Motion correspondence

- optical-flow direction and magnitude correlation with the driver;
- trajectory correlation for selected points or regions;
- warped-frame residual;
- temporal frequency distribution and acceleration profile.

### Camera behavior

- robust global affine/homography estimate per frame;
- decomposed translation, scale and rotation;
- subject-relative displacement;
- velocity and jerk at guide, edit and seam boundaries.

### Preservation and edit locality

- pixel/feature change outside the editable mask;
- temporal leakage before and after the target interval;
- mask-boundary discontinuity;
- preserved-state hash/identity before sampling when exact native transport is
  claimed.

### Composition quality

- ordering of required events;
- direction reversals or topology errors;
- unintended cuts or pauses;
- seam velocity, luminance and color discontinuity;
- explicit human accept/reject with a written failure class.

Metrics diagnose effect. They do not replace artistic acceptance.

## 8. Replication and stop rules

### H3

- run three fixed seeds for an initial signal;
- expand to eight only when the mechanism produces a repeatable, useful effect;
- change one variable per comparison;
- retain source, native state, prompt, seed, graph, runtime manifest and output;
- abandon a branch after three clean replicates show no material effect, unless
  a runtime sentinel fails.

### Seedance

- spend zero credits on broad random exploration;
- begin with one minimal paired comparison;
- allow at most two confirmation runs after a material signal;
- never add a second new reference in the same run as a prompt rewrite;
- use identical 15-second inputs for 2.0/2.5 comparisons;
- only scale duration or resolution after motion correctness is accepted.

### Cross-model

A cross-model result answers a routing question, not a universal model ranking.
The same assets and constraints may enter each model through different internal
channels. Record that difference instead of calling the runs equivalent by
name.

## 9. Immediate project decisions

1. Do not install an all-in-one director, timeline UI or prompt compiler.
2. Do not restore direct latent warps or feedback/advection experiments.
3. Retain only the pinned pruned INT8 Fun Control patch already load-tested in
   the laboratory. Direct Canny and depth execute; Hydra pass-through is exact,
   while transformed carriers remain review-gated experiments.
4. Keep Timed References as an optional semantic mechanism; its semantics are
   explicitly Qwen-only. The matched sparse 2x replacement test is rejected:
   correct target timestamps did not become target-aligned visual states.
5. Treat Tone Compensate as an optional decoded delivery correction, never as
   evidence of movement continuity.
6. Keep CAUCE responsible for transparent H3 state/mask algebra only. It should
   not duplicate AddGuide, Ref2VA, ControlNet or a second timeline UI.
7. Run the prompt-dependence and schema sentinels before the next prompt or
   movement study on the laboratory runtime.
8. Spend the first Seedance credits on one route-identification pair and one
   high-information H3-to-Seedance motion-spine comparison.

## 10. Source ledger

### Official model and runtime sources

- [MiniMax H3 model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [MiniMax H3 official repository and prompt guides](https://github.com/MiniMax-AI/MiniMax-H3)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [ComfyUI H3 per-token mask PR #15375](https://github.com/Comfy-Org/ComfyUI/pull/15375)
- [ComfyUI H3 AddGuide PR #15439](https://github.com/Comfy-Org/ComfyUI/pull/15439)
- [ComfyUI H3 special-token fix PR #15808](https://github.com/Comfy-Org/ComfyUI/pull/15808)
- [ComfyUI H3 prompt-dependence issue #15805](https://github.com/Comfy-Org/ComfyUI/issues/15805)
- [Alibaba PAI MiniMax H3 Fun ControlNet Union](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union)
- [ComfyUI Fun ControlNet PR #15860](https://github.com/Comfy-Org/ComfyUI/pull/15860)
- [Alternative H3 ControlNet model-patch PR #15975](https://github.com/Comfy-Org/ComfyUI/pull/15975)
- [Seedance 2.0 official launch](https://seed.bytedance.com/en/blog/seedance-2-0-%E6%AD%A3%E5%BC%8F%E5%8F%91%E5%B8%83)
- [Seedance 2.5 official launch](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [Seedance 2.5 official product page](https://seed.bytedance.com/en/seedance2_5)
- [BytePlus Seedance API capability documentation](https://docs.byteplus.com/en/docs/byteplus_las/video_gen_enhanced)

### Research

- [VGI-Bench: process-sensitive evaluation of video generation](https://arxiv.org/abs/2608.19583)
- [FilmBench: fine-grained evaluation of film-oriented video generation](https://arxiv.org/abs/2607.24241)
- [FrescoDiffusion: training-free tiled video regeneration](https://arxiv.org/abs/2603.17555)
- [STCDiT: anchor-frame video super-resolution](https://arxiv.org/abs/2511.18786)
- [Warped Diffusion for video inverse problems](https://arxiv.org/abs/2410.16152)
- [FlexTraj: flexible point-trajectory control](https://arxiv.org/abs/2510.08527)
- [MagicMotion: dense-to-sparse trajectory guidance](https://arxiv.org/abs/2503.16421)

The last two trajectory papers require trained control architectures and are
not directly portable into H3-Base. They inform representation and evaluation,
not a current implementation claim.

### Community mechanism references

- [MiniMax H3 Timed References](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Timed-References)
- [MiniMax H3 Tone Compensate](https://github.com/rkfg/ComfyUI-MiniMaxH3-ToneCompensate)
- [H3 GuideMaster](https://github.com/MajoorWaldi/ComfyUI-Majoor-H3-GuideMaster)
- [H3 Native Masked Context](https://github.com/wjc573/ComfyUI-H3-Native-Masked-Context)
- [MMH3Tools](https://github.com/ckinpdx/ComfyUI-MMH3Tools)
- [MMH3 UltimateUpscale](https://github.com/irregular-dressing1531/Comfyui-MMH3-UltimateUpscale)
- [Fun ControlNet community discussion](https://www.reddit.com/r/StableDiffusion/comments/1vwzukc/minimaxh3_fun_controlnet_union_released/)

Community sources supply testable observations, not authoritative behavior.
