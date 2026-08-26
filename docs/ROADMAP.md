# Production roadmap

The offline implementation surface is complete for the present scope. The
remaining gates convert checked contracts into live, reproducible and visually
assessed workflows.

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
free space. Update only CAUCE to commit
`291bff0307d0717fbe6376346799720a9ebdf891` if needed, restart only ComfyUI, and
verify all 18 nodes. Do not change ComfyUI core, CUDA, PyTorch, drivers, models,
or unrelated packages during this gate.

## 1. Materialize the operational core

Construct and export one active graph at a time. Start with:

1. `generate.keyframed@first-frame`;
2. `generate.keyframed@first-last`;
3. `generate.from_references@video-reference`;
4. `generate.with_guides@single-anchor`;
5. `continue.native_av@keyframe-overlap`;
6. `continue.native_av@masked-overlap`;
7. `complete.native_av@two-sided-infill`;
8. `rollback.native_av@branch-suffix`;
9. `frames.assemble@ordered-concatenation`.

Then materialize the remaining catalog entries as their concrete use arises.
All 21 offline plans already exist; priority here controls live effort, not
contract completeness.

## 2. Establish exact baselines

For each graph retain model filenames, geometry, frame count, prompt, seed,
sampler, scheduler, steps, denoise, video/audio shifts, ordered input hashes,
output prefix, runtime manifest, graph hashes, prompt id, and receipt.

Reference-video baselines use legal `17k+5` lengths within the model's stated
2–15 second range. Completion and continuation baselines preserve explicit
timeline origins and independent native video/audio masks.

## 3. Characterize behavior

Run the nine declared controlled comparisons. Prioritize endpoint behavior,
reference-video correspondence, AddGuide placement, keyframe versus native-mask
overlap, mask boundary/fade behavior, and future-guide interaction. Record
negative visual results as evidence; do not keep an ineffective mechanism as
accepted knowledge.

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
