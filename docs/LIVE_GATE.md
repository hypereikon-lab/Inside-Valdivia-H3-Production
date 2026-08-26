# Laboratory live gate

This is the exact boundary between offline preparation and claims about the
laboratory runtime. It is intentionally read-only until all compatibility gates
pass.

The source commits required by the gate, the two runtime profiles, every stop
condition, and the complete 21-topology evidence order are machine-readable in
`materialization/live-gate.json`.

## 1. Establish reachability without diagnosis by guess

Confirm that the hostname returns the authenticated ComfyUI page. A 502 or 504
does not identify whether the tower, Windows session, tunnel service, or ComfyUI
process is unavailable. Request only the smallest external check required.

Do not submit, update, restart, or install anything during this step.

## 2. Capture one immutable runtime truth

With Cloudflare service credentials, Runtime Control may probe directly:

```bash
comfy-runtime --url https://comfy.hypereikon.online \
  probe --output evidence/runtime/runtime-manifest.json
```

When authentication exists only in the browser, fetch these same-origin JSON
routes from the already authenticated page:

```text
/features
/system_stats
/object_info
/models
/queue
```

Save each response as its own JSON snapshot and assemble the manifest locally:

```bash
comfy-runtime manifest-from-snapshots \
  --runtime-label authenticated-browser-handoff \
  --snapshot features=evidence/runtime/features.json \
  --snapshot system_stats=evidence/runtime/system_stats.json \
  --snapshot object_info=evidence/runtime/object_info.json \
  --snapshot models=evidence/runtime/models.json \
  --snapshot queue=evidence/runtime/queue.json \
  --output evidence/runtime/runtime-manifest.json
```

This preserves the browser's authentication boundary. Never extract, print, or
persist its Cloudflare cookie.

The root `/models` route inventories model categories. Exact H3 filenames are
verified from the loader choices captured in `/object_info`, which is the same
schema snapshot used to validate workflow node inputs.

## 3. Evaluate the core profile

```bash
comfy-runtime check-requirements runtime/requirements/h3-core.json \
  --runtime-manifest evidence/runtime/runtime-manifest.json \
  --output evidence/runtime/h3-core-readiness.json
```

The automated gate checks:

- required routes;
- all 18 locked CAUCE nodes;
- official FL2VA, sampler, decode, `CreateVideo`, and `SaveVideo` nodes;
- exact expected FL2VA, Qwen, and video-VAE filenames;
- at least 60 GB total RAM and 30 GB total VRAM;
- a device name containing `5090`;
- an idle queue.

Complete the manual checks separately: at least 30 GB free on the actual
model/output volume, sleep disabled for the production window, and known
ComfyUI/cloudflared recovery behavior.

If the profile fails because CAUCE or Workspace Control is on an older locked
commit, stop and request confirmation for one targeted Manager update. Update
no core, CUDA, PyTorch, driver, model, or unrelated node.

## 4. Diagnose the browser workspace

In the authenticated ComfyUI page:

```js
window.comfyWorkspaceControl.diagnose()
```

Require:

```text
schema = comfy.workspace-diagnostic/1
readiness.ready = true
```

Then capture `inventory()`, treat every pre-existing workflow as user-owned,
and maintain at most one automation-owned active graph. Do not close modified,
temporary, unidentified, or signature-changed workflows.

## 5. Materialize, do not reconstruct from memory

Start with `generate.keyframed@text-only`. Build the graph from its topology
dossier using current live schemas. The artifact path must end in:

```text
VAEDecode -> CreateVideo(fps=24) -> SaveVideo
```

Export `uiGraph` and `apiGraph` together with `exportActive()`. Parameterize only
captured literal values and guard every pointer with its expected value. Use
`materialize-export` with the same runtime manifest.

The resulting pair remains `requires-live-review`. Validate it again before
submitting exactly once.

## 6. Evidence order

`materialization/catalog.json` is stable inventory order. It is not the live
execution order. `materialization/live-gate.json` owns the empirical order:

1. official FL2VA keyframed baselines under the core profile;
2. official Ref2VA and AddGuide baselines under the full profile;
3. native-state and deterministic baselines;
4. variants dependent on mechanisms already observed.

Stop after any failed schema, execution, artifact, or visual gate. Preserve a
negative result as evidence; do not silently change several parameters and call
the next result a causal comparison.

## 7. Completion of one topology

One topology advances only through:

```text
paired export
-> guarded materialization
-> same-manifest schema validation
-> exact prompt-id execution
-> resolvable saved artifact
-> immutable receipt
-> acceptance-profile review
```

Queue completion proves only `executes`. Promotion requires the acceptance
profile's successful-run count, all technical checks, and an explicit visual
verdict.
