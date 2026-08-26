# Current state

This is the authority for present capability claims.

## Source state

```text
CAUCE
  commit   180acd890e455a3985448b828cd8fa650d467e25
  version  4.0.0
  nodes    28
  operations / topology dossiers  8 / 22
  local tests  45 passing

Runtime Control
  commit   a39583a4d2c335eea8ddbb8c8280402c64a160a2
  version  0.3.0
  local tests  18 passing

Production data
  exact CAUCE commit/catalog/contract lock
  22 offline materialization plans
  10 controlled experiment definitions
  1 offline rolling-chain plan
```

The local source repositories are complete and content-addressed. The current
laboratory process has not yet been re-probed against these commits, so the
numbers above describe source state, not a claim that CAUCE 4.0 is presently
loaded by the remote ComfyUI process.

## What is implemented

CAUCE provides deterministic primitives for:

- exact half-open decoded-frame ranges;
- H3 24 fps visual-token and 40 Hz structural-audio layout arithmetic;
- packed AV window allocation, span extraction and absolute placement;
- independent continuous video/audio denoise masks with linear, smoothstep,
  and smootherstep ramps;
- exact native AV interval replacement;
- native span guides, synchronized append, split/rollback, save, and load;
- H3 target/reference/guide preflight and conditioning inspection;
- decoded coordinate maps and image warps for inspectable reference media.

Official ComfyUI owns H3 first/last frames, Ref2VA references, arbitrary-frame
AddGuide conditioning, model loading, prompting, sampling, and decoding. CAUCE
composes those official mechanisms; it does not replace the model or sampler.

Runtime Control implements guarded materialization plus `comfy.run-series/1`:
all concrete graphs are validated against one fresh `/object_info`, each prompt
id is persisted atomically immediately after submission, exact submitted jobs
are resumed rather than duplicated, and every completed step receives an
immutable receipt. It intentionally neither interprets H3 nor binds one step's
outputs into the next graph.

## Operation evidence

| Operation | Current implementation evidence | Live/visual evidence |
| --- | --- | --- |
| `generate.keyframed` | official H3 contract + checked variants | not materialized at current lock |
| `generate.from_references` | official H3 contract + checked variants | not materialized at current lock |
| `generate.with_guides` | official H3/AddGuide contract + checked variants | not materialized at current lock |
| `continue.native_av` | CAUCE layout/span/mask paths unit-validated | older keyframe mechanism executed synthetically; current variants uncharacterized |
| `complete.native_av` | placement/mask/replacement layer unit-validated | not yet sampled live |
| `rollback.native_av` | synchronized split/branch layer unit-validated | not yet exercised in production |
| `reference.transform` | deterministic decoded-map layer unit-validated | H3 correspondence remains experimental |
| `frames.assemble` | deterministic range layer unit-validated | no inference claim |

`implemented`, `materialized`, `executes`, and `visually accepted` are separate
states. No current-lock topology yet has a retained paired UI/API graph. The
repository therefore makes no claim that any of the 22 variants is presently
production-ready or visually accepted.

## Offline-ready assets

The 22 materialization plans cover the entire CAUCE topology catalog. Their
static operation hashes, variants, model filenames, geometry, frame arithmetic,
input cardinality, mask semantics, and output slots are checked. Live-owned
values remain null: actual media ids, sampler, scheduler, steps, flow shifts,
seed, graph node ids, `/object_info` manifest, and paired graph hashes.

The rolling chain is also offline-ready. It specifies strict dependencies,
native-state identities, exact source commits, per-step checkpoints, and a
new-plan-from-checkpoint branch policy. It is not an executable Runtime Control
series until its selected materialization plans have concrete prebound API
graphs and operation-reference files.

## Next live gate

When the tunnel is available:

1. capture `/features`, `/system_stats`, `/object_info`, queue state, Manager
   inventory, installed revisions, model filenames, and free storage;
2. update only CAUCE to the locked commit if required, restart only ComfyUI, and
   verify all 28 node types;
3. materialize one graph at a time from the checked plans, beginning with a
   small operational core;
4. run exact prompt-id technical smokes, retain receipts and native state, then
   perform visual acceptance separately;
5. compile the accepted, explicitly prebound graphs into a Runtime Control
   serial plan and test interruption/resume before long unattended production.

An HTTP 504 establishes only that the Cloudflare path could not reach a healthy
origin at that moment. It does not diagnose the tower, tunnel service, or
ComfyUI process, and it does not invalidate offline source work.
