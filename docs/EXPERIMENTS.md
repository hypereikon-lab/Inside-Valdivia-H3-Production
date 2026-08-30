# Controlled H3 experiments

`experiments/catalog.json` contains sixteen planned, one-variable comparisons:
endpoint mode, reference-image sizing, reference duration, guide length, guide
placement, continuation prompt relation, native mask boundary, overlap
transport, future guide, masked-edit edge profile, outpaint placement, native
refinement strength, decoded interpolation model, SeedVR2 scale, enhancement
order, and sparse-guide H3 retiming.

Decoded enhancement keeps the clocks explicit. RIFE/FILM comparisons assert
the exact `(N - 1) * 2 + 1` output and original-frame positions before visual
judgment. SeedVR2 comparisons assert unchanged frame count/fps. The operation-
order experiment starts only after one interpolation and one restoration
setting have independent evidence.

Every run records source hashes/order, operation and materialized graph hashes,
model files, geometry, frame count, exact prompt/seed, sampler/scheduler/steps,
video/audio shifts, runtime manifest, prompt id, artifacts, the sole changed
variable, and a visual verdict.

Native masks are tested as the official H3 sampler consumes them: continuous
per-token video and structural-audio strengths. Comparisons isolate curve,
fade, boundary, or transport; they do not mix several changes and call the
result causal.

Refinement is intentionally a characterization experiment: no denoise value is
accepted as a default. The source native state, prompt, seed, sampler,
scheduler, steps, and shifts remain fixed while only the video strength changes.

Metrics such as pixel difference, optical-flow magnitude, or queue completion
are diagnostic only. They cannot establish useful motion correspondence,
identity preservation, temporal boundary quality, or visual acceptance.

The scope excludes generative audio, soundtrack encoding, training, LoRA,
acceleration, streaming, and arbitrary sampler patches. The fixed soundtrack
is used only when assigning accepted outputs to the edit.
