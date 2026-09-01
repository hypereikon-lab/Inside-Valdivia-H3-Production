# Controlled H3 experiments

`experiments/catalog.json` contains sixteen controlled, one-variable comparisons:
endpoint mode, reference-image sizing, reference duration, guide length, guide
placement, continuation prompt relation, native mask boundary, overlap
transport, future guide, masked-edit edge profile, outpaint placement, native
refinement strength, native H3 temporal densification, native H3 spatial
regeneration, enhancement order, and dense-guide H3 temporal expansion.

Dense-guide expansion asserts the exact `(N - 1) * factor + 1` delivery count,
legal H3 target padding, factor-spaced official AddGuide indices, and an
unchanged 24 fps delivery clock before visual judgment. Factors expand duration;
they never multiply playback fps. Spatial regeneration asserts unchanged frame
count/fps and exact target geometry. The operation-order experiment starts only
after each operation has independent evidence.

The packed-token temporal-densification hypothesis is retained as rejected
evidence. Successful execution, correct frame arithmetic and non-duplicate
intermediate frames did not produce visually useful slow motion. It must not be
reintroduced as a supported variant without a new native H3 conditioning
mechanism and new empirical evidence.

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

The scope excludes generative audio, soundtrack encoding, acceleration,
streaming, and arbitrary sampler patches. Training/LoRA has a separate recipe
and evidence boundary. The fixed soundtrack
is used only when assigning accepted outputs to the edit.
