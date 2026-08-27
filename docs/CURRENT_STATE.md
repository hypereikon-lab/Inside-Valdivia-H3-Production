# Current state

This is the authority for present capability claims.

## Source state

```text
CAUCE
  commit   99731a39d4e69b09153e564408b7029e50e8b1bb
  version  5.3.0
  nodes    20
  operations / topology dossiers / graph archetypes  10 / 28 / 25
  local release tests  41 passing, zero skips

Runtime Control
  commit   28dc00151912ecbd3ccf2093edf0c8259dce7473
  version  0.5.0
  local tests  24 passing

Workspace Control
  commit   2f9174e61ae911c1573a26b64e5ee4aa80527b0e
  version  0.4.0
  local tests  9 passing

Production data
  exact component commit/tree/version/metadata locks
  exact CAUCE operation and graph-archetype locks
  28 offline binding/materialization profiles over 25 graph archetypes
  12 controlled experiment definitions
  1 offline rolling-chain plan
  2 runtime requirements profiles
  10 acceptance profiles covering all 28 variants
  0 visual assessment records until live artifacts exist
  1 six-phase live materialization gate
  1 fail-closed storage policy
  local tests  25 passing
```

All 41 CAUCE tests pass under the bundled local Python runtime with NumPy. A
reduced interpreter without NumPy is not release evidence. Across the four
active repositories the complete offline suites currently contain 99 passing
checks.

The local source repositories are complete, public, pushed, and
content-addressed. CAUCE and Workspace Control are Registry-prepared but not
published; publishing still requires the `hypereikon-lab` Registry publisher
and its release secret. Runtime Control remains a separate source package.

## Live runtime state

There is no current runtime manifest for this source lock. The latest retained
live observations predate these three component commits and therefore cannot
satisfy the deployment or compatibility gate. A previous first-install request
for Workspace Control lost its response while Manager was cloning; its outcome
must be reconciled from Manager inventory and the exact host directory before
any resubmission.

The compatibility lock records the last tested frontend separately from the
next target. The core profile may be evaluated on ComfyUI 0.33.0, while the full
profile requires ComfyUI 0.34.0 for the released official H3 AddGuide and
per-token denoise-mask surface. Neither target is treated as installed until a
fresh `/system_stats`, `/object_info`, Manager inventory, queue, and browser
diagnostic capture says so.

## What is implemented

CAUCE provides deterministic primitives for:

- exact half-open decoded-frame ranges;
- H3 24 fps visual-token and 40 Hz structural-audio layout arithmetic;
- packed AV window allocation, span extraction and absolute placement;
- independent continuous video/audio denoise masks with linear, smoothstep,
  and smootherstep ramps;
- static and per-frame continuous video-mask projection onto native H3 tokens;
- exact 32-pixel-aligned native canvas expansion for outpainting;
- exact native AV interval replacement;
- native span guides, synchronized append, split/rollback, save, and load;
- H3 target/reference/guide preflight and conditioning inspection.

Official ComfyUI owns H3 first/last frames, Ref2VA references, arbitrary-frame
AddGuide conditioning, model loading, prompting, sampling, and decoding. CAUCE
composes those official mechanisms; it does not replace the model or sampler.

The ten operations are grouped as H3 conditioning grammar, native H3 AV state
algebra, and decoded media algebra. They are orthogonal functions, not workflow
stages. See [Project model](PROJECT_MODEL.md).

Runtime Control implements guarded materialization plus `comfy.run-series/1`:
all concrete graphs are validated against one fresh `/object_info`, each prompt
id is persisted atomically immediately after submission, exact submitted jobs
are resumed rather than duplicated, and every completed step receives an
immutable receipt. It intentionally neither interprets H3 nor binds one step's
outputs into the next graph.

Runtime Control 0.5 also evaluates project requirements against one full
content-addressed manifest. A manifest can come from direct HTTP access or from
bounded endpoint JSON captured inside an authenticated browser; browser cookies
are never extracted. First installs now persist a mutation journal before the
Manager request and require reconciliation after an unknown transport outcome.
Workspace Control 0.4 adds browser-local dry-run plans for exact open/close
targets, whole-set close validation, and provenance-rich paired exports. Its
diagnostic must pass before tab or graph automation begins.

## Operation evidence

| Operation | Current implementation evidence | Live/visual evidence |
| --- | --- | --- |
| `generate.keyframed` | official H3 contract + checked variants | not materialized at current lock |
| `generate.from_references` | official H3 contract + checked variants | not materialized at current lock |
| `generate.with_guides` | official H3/AddGuide contract + checked variants | not materialized at current lock |
| `continue.native_av` | CAUCE layout/span/mask paths unit-validated | older keyframe mechanism executed synthetically; current variants uncharacterized |
| `complete.native_av` | placement/mask/replacement layer unit-validated | not yet sampled live |
| `edit.masked_video` | static/animated mask projection and composition unit-validated | static mask primitive executes live; H3 result unassessed |
| `refine.video` | bounded native-state denoise contract unit-validated | useful strength range uncharacterized |
| `reframe.outpaint_video` | aligned allocation, exact copy, and new-region mask unit-validated | expansion primitive executes live; H3 result unassessed |
| `rollback.native_av` | synchronized split/branch layer unit-validated | not yet exercised in production |
| `frames.assemble` | deterministic range layer unit-validated | no inference claim |

`implemented`, `materialized`, `executes`, and `visually accepted` are separate
states. No current-lock topology yet has a retained paired UI/API graph. The
repository therefore makes no claim that any of the 28 variants is presently
production-ready or visually accepted.

## Offline-ready assets

The 28 materialization plans cover the entire CAUCE topology catalog and map
through the locked archetype catalog to 25 distinct node/edge structures. Their
static operation hashes, variants, model filenames, geometry, frame arithmetic,
input cardinality, mask semantics, and output slots are checked. Live-owned
values remain null: actual media ids, sampler, scheduler, steps, flow shifts,
seed, graph node ids, `/object_info` manifest, and paired graph hashes.

Stable catalog priority no longer doubles as empirical execution order. The
six phases in `materialization/live-gate.json` cover every topology once and
put core FL2VA controls before full Ref2VA/AddGuide and native-state mechanisms.
The runtime core and full profiles verify expected H3/CAUCE nodes, models,
hardware, and queue; free storage and physical recovery remain explicit manual
checks.

The rolling chain is also offline-ready. It specifies strict dependencies,
native-state identities, exact source commits, per-step checkpoints, and a
new-plan-from-checkpoint branch policy. It is not an executable Runtime Control
series until its selected materialization plans have concrete prebound API
graphs and operation-reference files.

## Next live gate

When the laboratory origin is healthy again:

1. inspect Manager inventory and the exact Workspace Control directory to
   reconcile the interrupted first-install outcome; do not resubmit blindly;
2. capture a full content-addressed runtime manifest, verify free storage, and
   compare it with `runtime/compatibility-lock.json`;
3. update to the full-profile ComfyUI target only as a separate guarded action,
   then re-capture schemas and run Workspace Control's browser diagnostic;
4. materialize one archetype at a time from the checked profiles, beginning with a
   small operational core;
5. run exact prompt-id technical smokes, retain receipts and native state, then
   perform visual acceptance separately;
6. compile the accepted, explicitly prebound graphs into a Runtime Control
   serial plan and test interruption/resume before long unattended production.

Every graph must persist a resolvable video artifact through the current core
`CreateVideo -> SaveVideo` path. `VAEDecode` alone is not sufficient evidence
of a durable production result.

An HTTP 504 establishes only that the Cloudflare path could not reach a healthy
origin at that moment. It does not diagnose the tower, tunnel service, or
ComfyUI process, and it does not invalidate offline source work.
