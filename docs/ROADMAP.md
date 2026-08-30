# Production roadmap

The next deliverable is a rebuilt native-first workflow suite. Historical
example graphs are evidence and source material, not restoration targets. The
remaining gates convert the current official H3 surface plus the smallest
necessary CAUCE state primitives into live, reproducible and visually assessed
workflows. See [H3 capability map](H3_CAPABILITY_MAP.md).

## Completion rule

```text
checked operation@variant plan
  -> paired UI/API export from one live graph
  -> guarded literal parameterization
  -> validation against the same /object_info capture
  -> exact prompt-id execution and immutable receipt
  -> retained native state when applicable
  -> explicit visual verdict
```

`executes` never implies `visually-accepted`.

## 0. Reconcile the laboratory

Probe runtime, queue, node inventory, Manager revisions, model filenames, and
free space. Reconcile the interrupted Workspace Control first-install against
Manager inventory and the exact host directory before considering a retry.
Compare CAUCE, Runtime Control, Workspace Control, ComfyUI, frontend, and
Manager with `runtime/compatibility-lock.json`.

The core readiness profile accepts the last verified ComfyUI baseline. The full
profile requires ComfyUI 0.34.0 and a fresh frontend diagnostic because the
official H3 AddGuide and per-token denoise-mask paths are release dependencies.
Treat any core/frontend update as its own guarded action; do not combine it
with custom-node, CUDA, PyTorch, driver, model, or unrelated-package changes.
After every accepted change, restart only ComfyUI and recapture the manifest.

Run the machine-readable core readiness profile and Workspace Control browser
diagnostic before any mutation. The exact commits, stop conditions, and phase
ordering live in `materialization/live-gate.json`; see [Live gate](LIVE_GATE.md).

## 1. Materialize the operational core

Construct and export one active graph at a time. Begin from released official
templates or the smallest live official graph; do not begin from a historical
CAUCE example. Establish the official conditioning baselines first:

1. `generate.keyframed@text-only` as the prompt-only control;
2. `generate.keyframed@first-frame`;
3. `generate.keyframed@last-frame`;
4. `generate.keyframed@first-last`;
5. `generate.from_references@image-reference-match`;
6. `generate.from_references@video-reference`;
7. `generate.with_guides@single-anchor`;
8. `generate.with_guides@guide-clip`.

Add two compositions that are now clearly native-first:

1. Ref2VA image/video references followed by an official interior AddGuide;
2. two official guide clips around a newly generated bridge window.

Only after those execute should an exact native-state counterpart be built.
This produces a controlled comparison between simple released conditioning and
CAUCE state transport instead of assuming that the more elaborate graph is
better.

Then establish the native-state and deterministic baselines:

1. `continue.native_av@keyframe-overlap`;
2. `continue.native_av@masked-overlap` only after native mask capability is
   observed in the live core;
3. `complete.native_av@two-sided-infill` with a hard mask before any fade;
4. `complete.native_av@local-replacement`;
5. `rollback.native_av@branch-suffix`, including exact split/append round trip;
6. `frames.assemble@ordered-concatenation`.

After those mechanisms execute, establish the new native editing surface:

1. `edit.masked_video@static-spatial` with a hard control mask;
2. `edit.masked_video@local-retake` as temporal/spatial intersection;
3. `reframe.outpaint_video@centered` with a 32-pixel border;
4. animated masks and offset outpaint only after their simpler controls;
5. `refine.video@full-frame` as a one-variable strength ladder, followed by
   `refine.video@masked` only if the full-frame pass shows useful behavior.

The remaining variants are retained and materialized after their underlying
mechanism earns baseline evidence. All 28 offline plans already exist; this
order controls evidence dependencies, not catalog importance or permanence.
It is duplicated as machine-validated phase data in the live gate so catalog
priority cannot be mistaken for execution order.

## 2. Establish exact baselines

For each graph retain model filenames, geometry, frame count, prompt, seed,
sampler, scheduler, steps, denoise, video/audio shifts, ordered input hashes,
output prefix, runtime manifest, graph hashes, prompt id, and receipt.

Reference-video baselines use legal `17k+5` lengths within the model's stated
2–15 second range. Completion and continuation baselines preserve explicit
timeline origins and independent native video/audio masks.

## 3. Characterize behavior

Run the twelve declared controlled comparisons one variable at a time. Prioritize
endpoint behavior, reference-video correspondence, AddGuide placement,
keyframe versus native-mask overlap, mask boundary/fade behavior, and
future-guide interaction, then masked-edit edge profiles, exact outpaint
placement, and native refinement strength.

For temporal completion, verify technical preservation before judging the
image: confirm exact unknown range, unchanged tokens outside it, independent
video/audio masks reaching the official sampler, and cleared mask metadata on
the retained result. Test a hard mask first, then linear, smoothstep, and
smootherstep boundaries. Record negative visual results as evidence; do not
keep an ineffective mechanism as accepted knowledge.

Apply the operation profile in `acceptance/catalog.json`. Generative operations
need two technically successful inspected runs; deterministic assembly and
rollback round trips need one. No variant is promoted without all technical
checks and an explicit visual verdict.

## 4. Prove rolling execution

Resolve the three-step native continuation example into concrete, prebound API
graphs. Compile a `comfy.run-series/1` plan, interrupt it after submission,
resume from its persisted exact prompt id, and verify that no duplicate prompt
was created. Retain a receipt and content-addressed native checkpoint after each
step.

Create branches only as new plans from checkpoints. Use
`rollback.native_av` when the branch point requires a synchronized prefix; do
not mutate accepted chain history.

## 5. Production and storage

Create project invocations from accepted or intentionally exploratory graphs.
Index actual media by content hash, download accepted outputs from the tower,
retain packed AV state for anything that may continue or branch, and delete
only explicitly identified redundant artifacts. Keep a declared storage
reserve and never automate model deletion.

Editorial segments assign accepted outputs to exact 24 fps ranges against the
fixed external soundtrack.

## Operational resilience

Outside these repositories, the laboratory operator should keep ComfyUI and
`cloudflared` configured for restart, disable sleep during agreed production
windows, and define desired recovery after AC loss. A Cloudflare service token
can remove interactive authentication from automation, but cannot revive an
offline tower or origin process.
