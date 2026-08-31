# H3 intent routing and latent operator space

Checked on 2026-08-31 against ComfyUI `v0.34.0`, current ComfyUI master and
the released MiniMax H3 model surface. This document describes the control
grammar implied by the architecture. It distinguishes:

- operations available now;
- operations composable from released mechanisms;
- near-native operations that could be implemented without training H3;
- model-patch research;
- ideas that require training or have already failed empirically.

It is not a promise that every mathematically expressible intervention will
produce a useful image. Every new operator still needs causal and visual
evidence.

## 1. The architectural fact that organizes everything

H3 is not best understood as a conventional diffusion U-Net receiving a CLIP
embedding through a separate cross-attention bank. In the current ComfyUI
implementation, H3 constructs one packed token sequence:

```text
[Qwen text/vision states
 | target-aligned guide rows or native reference blocks
 | target audio rows
 | target video rows]
```

All rows are projected to the same hidden width and processed by the same
single-stream DiT blocks. The sequence uses three-dimensional RoPE coordinates
`(time, height, width)` and modality-specific adaptive normalization tags:

```text
video / visual conditioning  0
text                         1
audio                        2
```

The model therefore sees several kinds of evidence as peers in one attention
field, but their position, modality tag and diffusion timestep differ.

This creates four distinct axes on which intention can be routed:

1. **meaning**: what a Qwen token says or depicts;
2. **output address**: where evidence sits in target time and space;
3. **diffusion authority**: how much a target token is allowed to change;
4. **network route**: which tokens or residual branches can affect which DiT
   blocks and denoising steps.

## 2. Three meanings of time

Many apparent contradictions disappear when the three time domains are kept
separate.

### 2.1 Output time `τ`

The video timeline: frame zero, five seconds, a guide at frame 90. Native H3
video and condition rows receive temporal RoPE coordinates in this domain.

### 2.2 Diffusion time `σ`

The denoising trajectory from noise to a clean latent. H3's continuous mask
changes the effective `σ` of each target token. This controls generation
authority, not its output-frame address.

### 2.3 Conditioning lifecycle `λ`

Where influence is active across transformer depth or sampling steps. Released
references and guides remain available throughout the DiT. ControlNet branches,
attention patches or future schedules could vary influence across `λ`.

The Timed Qwen Reference changes the model's semantic representation of `τ`.
AddGuide changes the RoPE address in `τ`. A denoise mask changes `σ`. A future
attention gate would change `λ`.

## 3. An operator signature

Every control operation can be described with the same six fields:

```text
operator = {
  carrier,       # Qwen state, VAE latent row, target latent, mask, residual
  payload,       # semantics, appearance, motion, geometry, preserved state
  address,       # global, time, space-time, diffusion step, DiT depth
  authority,     # advisory ... strongly constrained ... preserved
  persistence,   # one position, interval, whole output, whole denoising run
  provenance     # exact source media/state/graph/model identity
}
```

This signature is more useful than naming nodes because it exposes when two
nodes duplicate the same model mechanism and when superficially similar inputs
reach different routes.

## 4. Released operators

### 4.1 Text instruction

```text
carrier      Qwen hidden states
payload      action, relation, camera, transformation, exclusions
address      global semantic context; temporal language remains soft
authority    advisory
persistence  available across the DiT and denoising run
```

Text chooses and qualifies a hypothesis. It does not provide exact geometry or
hard temporal placement. H3's text/vision states are refined and inserted into
the same token stream as references and target tokens.

### 4.2 Untimed Qwen visual reference

```text
carrier      Qwen vision tokens inside the presentation sequence
payload      semantic identity, appearance, visible relations
address      global
authority    advisory
persistence  whole run
```

The community Qwen-only node implements this without VAE reference rows. It is
useful for measuring what the language/vision encoder contributes independently
of native Ref2VA.

### 4.3 Timed Qwen image reference

```text
carrier      Qwen vision tokens plus a textual timestamp token
payload      semantic state associated with an output time
address      semantically tagged `τ`, not hard-gated
authority    advisory
persistence  globally available; intended meaning is time-local
```

The current community implementation presents a still as a two-frame video
block with identical timestamps. It says "this visual evidence belongs at
time `τ`" but does not assign target RoPE coordinates or VAE-encode the image.

### 4.4 Timed Qwen video reference

```text
carrier      ordered Qwen two-frame vision blocks, each with a timestamp
payload      semantic motion sequence and visible state changes
address      semantically tagged interval in `τ`
authority    advisory
persistence  globally available
```

The implementation samples the source at an analysis rate, 2 fps by default,
and offsets every sampled timestamp by the desired target start. It preserves
ordering and real presentation timestamps, but it remains Qwen-only.

### 4.5 Native Ref2VA image

```text
carrier      Qwen vision states + H3-VAE reference rows
payload      semantic and native visual appearance/state
address      independent reference block before the target timeline
authority    strong reference, not preservation
persistence  whole run
```

The image is represented twice. Qwen sees its pixels. The H3 VAE produces a
latent reference block that is projected into DiT visual rows. The block has
its own spatial coordinates and a one-unit reference time span. It is not
copied into the target stream.

### 4.6 Native Ref2VA video

```text
carrier      Qwen sampled video states + full H3-VAE temporal reference rows
payload      semantics, appearance, internal motion and camera dynamics
address      independent reference timeline before the target timeline
authority    strong reference, not frame correspondence
persistence  whole run
```

The VAE path retains the legal-length reference video as a native temporal
latent. Qwen sees it more sparsely. The reference block preserves its internal
ordering and three-dimensional positions, but its frames are not aligned to
same-numbered target frames. The target may imitate, reinterpret or ignore
components of its motion.

### 4.7 First, last and arbitrary AddGuide

```text
carrier      H3-VAE condition rows
payload      exact-looking still state or short local motion clip
address      target-aligned RoPE `(τ,h,w)`
authority    stronger than reference; still not target preservation
persistence  condition rows remain available for the whole run
```

This is the important implementation detail: AddGuide creates a separate
`cond` segment. Its VAE rows share the target spatial grid, and its temporal
coordinates are calculated from the requested target frame. It does **not**
write those rows into the target latent. A still supplies target-aligned state;
a clip supplies target-aligned state and local derivatives.

### 4.8 Populated target state plus continuous denoise mask

```text
carrier      target H3 latent + per-token mask
payload      actual state to preserve or reconsider
address      exact target `(τ,h,w)`
authority    continuous from generate to preserve
persistence  applied at every sampling step
```

This is the strongest released route. Each visual target token gets its own
effective diffusion timestep:

```text
mask = 1  -> token follows the active noisy generation state
mask = 0  -> token is pinned near H3's visual conditioning timestep
0 < mask < 1 -> partial regeneration authority
```

ComfyUI also injects the supplied clean target latent at condition strength in
preserved regions. This is actual inpainting/preservation, not simply a guide.

### 4.9 Global visual-condition noise augmentation

```text
carrier      guide and native reference VAE rows
payload      confidence/degradation of visual conditioning
address      all current visual condition rows
authority    global soft-strength proxy
persistence  whole run
```

H3 already contains `minimax_visual_cond_noise_aug`. The default is `0.999`.
Condition rows are mixed with deterministic noise according to this value and
their timestep label is changed consistently. The official workflow does not
present it as a normal user control, but the backend accepts it.

This is not identical to an attention weight. It changes the condition itself
and how noisy the model believes it is. It deserves a controlled exposure test
before any per-reference generalization.

### 4.10 Seed and target noise

```text
carrier      initial target noise
payload      stochastic solution choice
address      entire generative target or selected unpreserved tokens
authority    selects a trajectory; does not state intent
persistence  determines the denoising path
```

Seed is exploration, not instruction. Fixed seed is required when testing
whether another operator has causal effect.

### 4.11 Sigma schedule and flow shifts

```text
carrier      sampler time schedule
payload      denoising dynamics
address      global diffusion time `σ`
authority    global numerical behavior
persistence  entire run
```

These controls can alter motion/texture behavior indirectly, but they do not
carry semantic intent. They belong to characterization and runtime stability,
not the primary movement grammar.

## 5. Released compositions that behave like new operations

These need no new model mechanism.

### 5.1 Semantic state at a time

```text
Timed Qwen image
```

Softly states what should be present around `τ`.

### 5.2 Exact-looking state at a time

```text
AddGuide still
```

Provides VAE condition rows at target-aligned coordinates.

### 5.3 Named and target-aligned state

```text
Timed Qwen image + AddGuide of the same source
```

Qwen can express the role of the state while AddGuide supplies native visual
evidence at the intended position.

### 5.4 Local motion boundary

```text
AddGuide clip
```

Supplies state plus velocity/deformation over a short target-aligned interval.

### 5.5 Global motion driver plus exact boundary

```text
Ref2VA video + first/last/interior AddGuide
```

The reference proposes a motion manifold; the guide selects a state it must
pass near. This is currently the cleanest native motion-direction composition.

### 5.6 Two-sided temporal inpainting

```text
known left target state
+ generated middle mask
+ known right target state
```

The known target spans are populated and protected; the middle runs at higher
generation authority. Prompt and references influence the unknown interval.

### 5.7 Forward and backward completion

The same primitive changes only which side is known:

```text
known prefix + generated future
generated past + known suffix
```

Backward completion is not a separate model capability. It is target-state
placement plus authority geometry.

### 5.8 Local retake

```text
source target latent + spatiotemporal authority mask
```

Only a selected region and interval are reconsidered. A reference or guide can
state what should replace it.

### 5.9 Motion retargeting

```text
native motion reference video
+ appearance image reference
+ exact starting guide
+ prompt declaring transfer boundaries
```

This factorization is plausible but not guaranteed: appearance and dynamics
share the single attention stream and may interfere.

### 5.10 Temporal densification

```text
known source states placed on alternating target times
+ generated interstitial authority
```

This is model-native temporal inpainting over a denser target lattice. It must
still prove that H3 produces useful intermediate motion rather than merely
reconstructing or drifting.

### 5.11 Spatial regeneration and outpainting

```text
expanded or resized target latent
+ protected known area
+ generated new/partially regenerated area
```

The operation is native only when the result remains H3 state and the sampler
uses H3's own per-token authority. Quality and geometry remain empirical.

## 6. Near-native operators implementable without training H3

These require custom nodes or small core-compatible patches, but not new model
weights.

### 6.1 Per-reference bandwidth control

Manipulate what each route can carry before encoding:

- Qwen image resolution;
- Qwen video analysis fps;
- VAE reference spatial resolution;
- reference duration and temporal crop;
- spatial crop or region-of-interest reference;
- blurred, edge-reduced or color-reduced semantic copies.

This is a principled method for factorizing motion from appearance. It changes
information bandwidth rather than inventing semantic role types.

### 6.2 Reference temporal transforms

Preprocess a driver before VAE encoding:

- trim;
- reverse;
- hold selected states;
- resample faster or slower;
- repeat a local gesture;
- concatenate motion primitives.

These are decoded-media transformations, but their output becomes native H3
reference latents. They offer much safer motion manipulation than directly
warping latent values.

### 6.3 Separate Qwen and VAE versions of one reference

The architecture does not require the semantic presentation and native VAE
reference to have identical bandwidth. A transparent custom node could present:

```text
high-detail still to Qwen
low-bandwidth motion clip to VAE
```

or the reverse, while recording that the two carriers came from the same source.
This is a genuine architectural ablation, not a new ontology.

### 6.4 Expose visual condition noise augmentation

Expose the existing global backend value with a bounded node and compare it
over fixed references/guides. If it produces a monotonic fidelity/invention
tradeoff, a later implementation could generalize it per condition block.

Current limitation: the payload supplies one global value to all visual
conditions and restarts the same deterministic noise stream for every block.

### 6.5 Time-aligned latent reference

Native references currently occupy a separate timeline before the target;
AddGuide rows occupy target-aligned coordinates. A hybrid operator could encode
a reference latent as separate condition rows but assign it a chosen target
temporal origin.

```text
reference semantics: separate conditional evidence
guide geometry: target-aligned time coordinates
```

This would create a **soft latent timed reference**: stronger and more native
than Qwen timestamps, but not target preservation. It is the most direct
architecture-derived next operator.

It should first be implemented as a still/short-clip comparison against
AddGuide, because it may turn out to be exactly equivalent to AddGuide under a
different name.

### 6.6 Interval-addressed semantic reference

Timed Qwen video already labels sampled moments. A clearer interface could bind
a reference to `[τ_start, τ_end)` and validate that every timestamp falls inside
the generated duration. This is an interface/data-contract improvement, not a
new model channel.

### 6.7 Spatially sparse guide rows

AddGuide currently supplies a full target-aligned spatial grid. The packed
layout could theoretically include only selected guide patches with their
original `(τ,h,w)` coordinates.

Potential use:

- exact-looking regional guide without supplying the whole image;
- a moving sparse region guide;
- several disjoint guide regions at one time.

Risk: the released model was trained on particular condition layouts. Sparse
condition rows may be ignored or destabilize attention. Implement only after
full-frame mechanisms are characterized.

### 6.8 Guide confidence by condition degradation

Instead of scaling embeddings arbitrarily, create controlled versions of a
guide through the existing condition-noise mechanism or through resolution and
blur. This preserves the learned condition route while varying certainty.

### 6.9 Native state branch, merge and rollback

These are deterministic data operations rather than sampling changes:

- persist packed state;
- split at an exact synchronized time;
- branch several suffixes from one state;
- replace an interval;
- restore the last accepted checkpoint;
- compare outputs that share the exact same prefix state.

This is CAUCE's strongest justified role because it enables controlled
experiments without altering H3's learned computation.

## 7. Model-patch research operators

These exploit architecture hooks but have greater risk.

### 7.1 Per-reference attention strength

Because references are contiguous segments in one self-attention sequence, a
block patch could scale or gate interactions from each reference segment to
target video rows.

Possible control:

```text
target <- identity reference: 0.8
target <- motion reference:   1.2
target <- unrelated refs:     0.0
```

This would be more direct than degrading the condition, but it is not a learned
H3 input and may break attention normalization. It requires careful baselines.

### 7.2 Temporal attention windows

Gate a reference or guide so target frames attend strongly only inside a target
interval, with a continuous falloff outside it.

```text
weight(target_time, reference) = smooth window around [a,b)
```

This would convert global conditioning availability into actual time-local
influence. It is conceptually what Timed Qwen References do not currently
provide.

### 7.3 Spatial attention windows

Gate condition-to-target attention by `(h,w)` distance or a target mask. This
could direct an appearance/structure reference to one region while leaving the
rest free.

Again, this changes the network route rather than the target denoise mask. A
target mask controls where pixels may change; an attention window controls
which evidence can influence those pixels.

### 7.4 Diffusion-step conditioning schedule

Vary reference or guide influence over `σ`:

- strong structural reference early, weaker late;
- broad motion driver early, appearance reference late;
- exact guide throughout;
- local correction reference only near final refinement.

This matches the coarse-to-fine intuition of diffusion, but H3's actual
trajectory must be measured. VGI-Bench suggests early hypotheses are difficult
to overturn, making early structural control especially plausible.

### 7.5 Transformer-depth routing

Apply structural or reference residuals only at selected H3 blocks. Fun
ControlNet already takes this form: its released branch attaches at several
depths through zero-gated residual paths. A generic layer schedule is possible,
but arbitrary tuning without training is unlikely to be stable.

### 7.6 Attention diagnostics

Read-only block hooks could measure:

- target attention mass assigned to text, Qwen vision, guide and reference
  segments;
- how that distribution changes across layers and denoising steps;
- whether a nominally different prompt/reference produces a changed route.

This is valuable for debugging conditioning failure. Full attention capture is
memory-intensive; aggregate statistics are preferable on the 32 GB host.

### 7.7 Dynamic authority masks

Released masks are fixed fields whose values determine per-token effective
timesteps. A wrapper could change the mask as a function of `σ`, allowing:

- coarse global regeneration early and local protection late;
- progressive spatial reveal;
- moving temporal repair windows;
- different edit authority at different denoising phases.

This is a sampler/model patch and should not enter CAUCE's stable algebra until
it proves a benefit beyond one static continuous mask.

### 7.8 RoPE coordinate transforms

The packed layout exposes explicit `(t,h,w)` positions. Possible interventions
include:

- translating a condition block in target time;
- dilating its temporal coordinate system;
- aligning reference time with target time;
- moving or scaling condition spatial coordinates;
- giving several condition blocks a shared temporal origin.

This alters relational geometry without warping latent values. It is more
architecturally coherent than grid-sampling the latent, but still out of the
training distribution. Start only with time-alignment that reproduces known
AddGuide behavior.

## 8. Structural residual operators

H3 Fun ControlNet Union adds a different carrier:

```text
carrier      zero-gated residuals injected at selected DiT depths
payload      per-frame Canny, depth, HED, MLSD, pose or inpaint structure
address      explicit video-space structure over `τ,h,w`
authority    strength-controlled structural constraint
persistence  selected transformer depths and whole denoising run
```

This enables operations unavailable to Ref2VA alone:

- exact-ish camera/path geometry from depth or edges;
- pose trajectories;
- line/plane preservation;
- error-copy fidelity tests;
- sparse structural keyposes with generated intervals;
- local structural redirection combined with a target edit mask.

ControlNet does not replace references. A useful composition is:

```text
ControlNet       structure / trajectory
Ref2VA           appearance / motion example
Qwen             semantic relation
AddGuide         target-aligned state
target mask      preservation authority
```

The current checkpoint exists, but ComfyUI integration remains an upstream
watch item rather than a laboratory production dependency.

## 9. Operations that would require training

The following cannot be honestly claimed as node-only extensions:

- new modality tags beyond H3's learned text/video/audio classes;
- a learned point-trajectory, optical-flow or camera-control adapter;
- reliable per-reference semantic role embeddings;
- a true spatial correspondence field between arbitrary reference and target;
- a learned latent super-resolution prior;
- new ControlNet modalities not represented by the released checkpoint;
- guaranteed object identity disentangled from reference background;
- guaranteed causal or physical simulation.

They may inspire future research, but the current project excludes training and
must not disguise it as workflow wiring.

## 10. Rejected or low-value interventions

### Direct latent affine/advection/depth warp

Grid-sampling, rotating, zooming or advecting H3 latent tensors assumes the
denoiser is equivariant to that transform. Project tests produced ghostly lag
rather than useful motion, consistent with diffusion research. This branch
remains rejected.

### Arbitrary latent interpolation as final motion

Linear interpolation between unrelated latent states may be useful as an
initial guess inside a fully regenerated masked interval, but it is not a
reliable semantic motion operator and should not be presented as one.

### Monolithic prompt/director nodes

These package intent but do not create a new carrier, address or authority
mechanism. They obscure causal comparison and are not architectural operators.

### New interfaces around existing nodes

Timeline panels, all-in-one generation nodes and workflow wrappers may improve
convenience but do not expand H3's latent operation space. The project remains
ComfyUI-native and data-oriented.

## 11. Recommended operator roadmap

### Immediate: characterize released routes

1. Qwen-only global versus timed reference.
2. Native Ref2VA versus Qwen-only reference.
3. AddGuide still versus clip.
4. AddGuide versus populated target plus mask.
5. Ref2VA motion driver plus target-aligned guide.
6. Global visual-condition noise augmentation.

### Next: implement only transparent near-native additions

1. per-route reference bandwidth controls;
2. semantic/VAE split-reference experiment;
3. interval validation for timed semantic references;
4. time-aligned latent-reference prototype, beginning as an AddGuide
   equivalence test;
5. aggregate conditioning/attention diagnostics;
6. native state branch/merge/rollback workflows.

### Later: structural control

1. pin one merged Fun ControlNet route;
2. compare reference versus structural adherence;
3. test sparse structural keyposes;
4. combine structural control with local target masks;
5. characterize memory and storage before any production promotion.

### Research only after those results

1. temporal or spatial attention windows;
2. diffusion-step reference schedules;
3. dynamic masks;
4. minimal RoPE time-alignment transforms;
5. sparse guide rows.

The ordering is deliberate: every later mechanism should prove that a simpler
released route cannot express the same useful effect.

## 12. Sources

- [Official ComfyUI H3 model implementation](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/ldm/minimax/model.py)
- [Official ComfyUI H3 model wrapper and mask injection](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/model_base.py)
- [Official ComfyUI H3 nodes](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy_extras/nodes_minimax_h3.py)
- [Official H3 Qwen3-VL presentation encoder](https://github.com/Comfy-Org/ComfyUI/blob/master/comfy/text_encoders/minimax.py)
- [MiniMax H3 official repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [MiniMax H3 Timed References](https://github.com/ethanfel/ComfyUI-MiniMaxH3-Timed-References)
- [H3 Fun ControlNet Union](https://huggingface.co/alibaba-pai/MiniMax-H3-Fun-Controlnet-Union)
- [ComfyUI H3 Fun ControlNet PR #15860](https://github.com/Comfy-Org/ComfyUI/pull/15860)
- [Alternative H3 ControlNet model-patch PR #15975](https://github.com/Comfy-Org/ComfyUI/pull/15975)
- [VGI-Bench](https://arxiv.org/abs/2608.19583)
- [Warped Diffusion](https://arxiv.org/abs/2410.16152)

