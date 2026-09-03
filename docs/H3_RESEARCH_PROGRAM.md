# H3 research program

Inside Valdivia treats H3 as a new, rapidly changing generative system whose
useful behavior must be mapped empirically. The objective is not to accumulate
nodepacks or prompts. It is to build a compact body of repeatable knowledge
about how textual, visual, temporal and structural conditions interact.

The machine-readable research queue is `research/catalog.json`. Prompt-only
stimuli live separately in `prompting/catalog.json`; executable graphs,
invocations, receipts and visual assessments retain their existing ownership.

## The two loops

### Discovery loop

The discovery loop is intentionally permissive:

```text
new source or observation
  -> mechanism hypothesis
  -> cheapest discriminating experiment
  -> one fixed-seed screen
  -> retain, revise, reject or mark inconclusive
```

Its outputs are questions and candidate mechanisms. They are not production
defaults. A strange one-off result is useful if it reveals a better question,
but it remains a one-off result.

### Production loop

The production loop is conservative:

```text
screening signal
  -> exact repeat across seeds
  -> full-motion human review
  -> profile and input-class boundary
  -> accepted operation variant
  -> reproducible invocation
```

Only this loop may promote a technique. A discovery can fail promotion without
being erased; negative evidence prevents the same weak idea from repeatedly
returning under a new name.

## Truth levels

Every claim uses exactly one level:

| Level | Meaning |
| --- | --- |
| `source-fact` | Directly established by official model, ComfyUI or merged implementation code |
| `community-report` | A public result, tutorial, issue or case study without project-controlled reproduction |
| `project-hypothesis` | A mechanism or predicted effect that has not run |
| `project-executes` | The exact graph ran and produced valid artifacts; visual utility is not implied |
| `project-repeat-supported` | The intended effect repeated under the declared seeds and review boundary |
| `project-rejected` | The declared mechanism failed its visual or causal test and is retained as negative evidence |

`community-report` never automatically upgrades to `source-fact` because a
repository has many stars. `project-executes` never automatically upgrades to
useful knowledge because a video file exists.

## Research card

Before spending GPU time, each investigation must answer:

1. What exact question distinguishes two plausible explanations?
2. Which model input is being changed?
3. What remains byte-identical or numerically identical?
4. What observable result would support the hypothesis?
5. What result would falsify it?
6. Which confounds remain, including seed, acceleration profile, quantization,
   reference order, guide placement and control strength?
7. What is the cheapest valid screen?
8. What replication is required before using the result in production?

If an experiment changes prompt, guide density and model profile together, it
is a creative exploration but not a causal comparison. It may generate useful
material; it cannot answer which mechanism worked.

## Experimental corpus

Use a small set of opaque, content-addressed stimuli. The research system does
not need to understand or describe them.

The minimum corpus should eventually contain:

- one first frame with room for forward continuation;
- one first/last pair with modest geometric distance;
- one first/last pair with a difficult spatial or semantic distance;
- one reference clip with a legible camera trajectory;
- one ordered AddGuide ladder already known to reconstruct;
- one structural carrier already judged visually useful;
- one counterexample that previously caused a failure mode.

Every stimulus receives only an id, hash, technical geometry, time range and
human-authored intended test role. Do not store inferred subjects, objects,
actions or scene categories.

## Standard run design

### Screening tier

- one source tuple;
- one seed;
- one fixed H3 family and acceleration profile;
- 124 frames at 24 fps unless the question requires another legal length;
- 768-short-edge native canvas;
- one changed variable;
- exact artifact and receipt retention;
- rapid full-motion review.

### Replication tier

- the best two variants from screening;
- at least three seeds;
- `quality-20` confirmation;
- exact same source tuple and graph except prompt or declared variable;
- quantitative diagnostics plus independent human visual verdict;
- explicit input-class and acceleration-profile scope.

### Transfer tier

Only after replication:

- repeat on a second opaque source tuple;
- test the intended production acceleration profile;
- compose with one adjacent conditioning mechanism;
- record whether the effect transfers, weakens or reverses.

No technique becomes universal merely because it transferred once.

## Observation and measurement

The measurement follows the research question.

For camera and temporal prompts:

- optical-flow direction and magnitude;
- apparent scale trajectory;
- parallax and occlusion evolution;
- velocity and jerk profiles;
- early endpoint landing and terminal hold duration;
- cut, dissolve, reset or reversal candidates.

For keyframes and guides:

- supplied-state reconstruction;
- incoming and outgoing motion around each anchor;
- frozen or duplicated intervals;
- endpoint pixel fidelity;
- endpoint approach quality over the preceding window.

For references:

- intended role correspondence;
- unintended visible-content leakage;
- reference-order sensitivity;
- camera-motion and timing transfer;
- identity or appearance stability when that role is explicitly requested.

For structural control:

- control-carrier correspondence;
- text/control agreement or conflict;
- distortion and overconstraint;
- sensitivity to strength and diffusion interval, tested separately.

Metrics locate differences; they do not decide aesthetic value. Every claimed
improvement still needs full-speed and frame-by-frame visual review.

## Research sequence

### A. Linguistic control

Current active questions:

1. Does exact prompt text measurably affect a fixed-seed output?
2. Does H3 distinguish optical zoom from physical camera translation?
3. Can it follow a requested velocity profile?
4. Can it reach the last frame with coherent incoming motion?
5. How much causal path detail is useful at five seconds?

These are the Stage-1 matrices in `prompting/catalog.json`.

### B. Native multimodal binding

After a useful FL2VA vocabulary exists:

1. characterize I2VA departure from one frame;
2. compare flat and six-section Ref2VA role binding;
3. test motion-reference authority independently of appearance;
4. test AddGuide gap intent with identical target-time states;
5. later characterize L2VA as backward causal inference, not assumed reverse
   I2VA.

### C. Text plus structural control

Choose one accepted prompt and one useful carrier. First map neutral,
congruent and conflicting text. Only then vary control strength, interval,
carrier type or mask.

### D. Composition

Once individual mechanisms repeat:

- first/last frames plus structural control;
- Ref2VA role reference plus AddGuide arrival;
- prompt-shaped camera path plus spatial mask;
- continuation plus an explicit future guide;
- retained prompt behavior under production acceleration.

Composition begins from two understood operators. It is not a search across all
possible combinations.

### E. Prompt systems

Only after direct prompting is characterized:

- prompt embeddings;
- external rewriter LoRAs;
- local multimodal prompt writers;
- deterministic prompt linting or repair;
- reusable prompt fragments.

The comparison unit is always the exact produced prompt, not the reputation of
the tool that produced it. Automatic captioning remains outside the default
path because project media is intentionally opaque.

## Radar process

H3 upstream and its community are checked on different cadences.

Before every GPU batch:

- official MiniMax H3 prompt/model changes;
- `nodes_minimax_h3.py` history and current schema;
- official ComfyUI H3 workflow templates;
- the laboratory's live `/object_info` and locked runtime profile.

Daily during active research:

- new MiniMax H3 integrations and nodepacks;
- H3 prompt, control, continuation and editing repositories;
- new ComfyUI issues and pull requests with reproducible mechanisms.

Weekly:

- architecture-compatible video conditioning, completion, editing and
  evaluation papers;
- adjacent model ecosystems, used only to propose mechanisms that fit H3's
  released architecture.

A radar observation updates a research track. It does not trigger automatic
installation, model download, core update or GPU execution.

## Batch review cadence

After each batch:

1. verify exact prompts, graphs, seeds and artifacts;
2. generate a contact sheet only as navigation aid;
3. inspect every video at full speed;
4. inspect decisive temporal windows frame by frame;
5. record the visual verdict before discussing a new variation;
6. update the research track's evidence level;
7. choose the next discriminating test, not merely a stronger parameter;
8. stop a branch when its mechanism is falsified.

The next batch should be small enough to review completely. Unreviewed output
volume is not research progress.

## Current boundary

The project now has a research method, twelve open tracks, seven prompt
matrices, controlled-operation experiments, runtime receipts and visual
assessment records. It does not yet have a repeat-supported H3 prompting
technique. The immediate objective is to earn the first one through the three
Stage-1 FL2VA matrices.

