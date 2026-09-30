# Formal sample size and statistical plan v1 — 2026-10-01

DRAFT READY FOR AUTHOR REVIEW / DESIGN ONLY. No measurements collected for this plan.
[Endpoints](FORMAL_METRICS.md) / [data and annotation](FORMAL_DATA_PROTOCOL.md).

## Sample and precision rationale

400 formal images, every image paired across A/B/C/D:1600 planned invocations.
40 separate rubric/design images; no prompt tuning. One greedy invocation per method/image,
seed0; no best-of or favorable repeated seed. This estimates image variation conditional on
one run, NOT run-to-run/GPU nondeterminism. Hardware repetition experiments require a
separate prospective design. Duplicate clusters removed before selection.

Primary per-image values in[0,1], paired differences in[-1,1]. Worst-case SD of differences
<=1; large-sample unadjusted95% half-width <=1.96/sqrt(400)=0.098. This is a conservative
planning approximation, not a promised CI width or80% power calculation. With three-primary
Bonferroni reference critical value about2.394, corresponding half-width about0.120.
Actual variance and sparse erroneous-claim frequency are unknown; small effects around
0.05 may remain inconclusive.400 is chosen for a roughly0.10 unadjusted worst-case precision
scale plus feasible annotation, not because two development images looked successful.
No optional stopping for significance. Fewer than400 valid planned IDs requires prospective
amendment, not silently smaller claims of power; execution failures stay in400 denominators.

Planning workload assumptions (not measured):440 images×2annotators×4min reference work
=58.7 person-hours;1600 outputs×2×5min claim scoring=266.7 hours;30% extra for adjudication,
training and bookkeeping gives about423 hours. Long outputs can exceed estimate. No cap on
claims annotated to save work; staff and timetable acceptance is a BLOCKER. Author may
revise sample size before any formal output, disclosing weaker precision and a new version.
Do not promise10/31 or11/1 despite this workload.

## Schedule and failure policy

After manifests freeze, image order sorted by SHA256 `RD001-order-v1|<id>`.
Four sequential method invocations per image; rotate ABCD,BCDA,CDAB,DABC by image-order
index modulo4 (100 images/order). Fresh worker/load per method, no warmup model calls,
no shared chat/embedding cache. Stable pinned environment and logged device baseline;
OS file caching may remain, balanced order mitigates but does not eliminate it.
Cold-process load is not proof of cold disk cache. Batch1 always.

Before each authorized invocation apply identical source/assets/guard checks. No retry or
replacement. Safety failure halts the block; subsequent slots NOT_ATTEMPTED. Resume of
unattempted slots requires a separately logged safe authorization with unchanged policy;
failed slots are never rerun into a better answer. Analyze only after fixed planned block
is closed, never stop because an endpoint appears significant. If a block remains incomplete,
report provisional/incomplete status, missingness and worst/best bounds, no confirmatory claim.

## Estimands, intervals and tests

Unit of inference is image, never individual claims as independent samples. Compute the
three paired mean differences P1(D−A),P2(D−B),P3(D−C), with signs as in metrics; show absolute
percentage-point effects, paired SD and group means. Do not rely on standardized effect
sizes when bounded scales already have useful units. Counts/times: also paired mean and
median differences, p50/p95, full distributions and denominators; no unsupported FLOP claims.

Preselect a paired image-cluster bootstrap:10000 resamples of400 image IDs with replacement,
keeping all methods/claims for each sampled ID together; NumPy default_rng seed20261001,
freeze installed NumPy/scoring version before use. Percentile2.5/97.5 intervals for each
effect; also simultaneous conservative0.8333/99.1667 percentile intervals for the three
primary differences (Bonferroni reference). These are approximate sampling intervals.
For ratio-of-sums secondary metrics recompute both numerator and denominator in each
resample; zero-denominator resamples ->NA, report count, no fake interval if unsupported.

Two-sided centered paired-bootstrap tests of zero mean difference, fixed procedure:
let dbar be observed image-mean difference, and bbar each resampled difference mean;
p=(1+count(abs(bbar−dbar)>=abs(dbar)))/10001. Approximate bootstrap null test, not an exact
randomization claim; samples with all differences zero return p=1. Apply Holm step-down
to the three p-values at family alpha0.05. Never change tests after seeing significance.
Bootstrap behavior/zero cases must be CPU validated before execution; no current outputs
used to tune methods. Bounded/skewed/sparse results may yield poor approximations; report
counts/distributions and uncertainty, no claim that nominal coverage is guaranteed.

Secondary comparisons/strata are descriptive with95% intervals, no unadjusted discovery
claims. Completion/cleanup rates show numerators/denominators and Wilson95% intervals;
paired rate differences use image bootstrap. No per-category confirmatory claims or
post-hoc easiest-subset analysis. Prefix-identical B/D subset is explicitly descriptive.

## Missing, failed, unresolved, empty

All400 planned images retained. Per metrics: primary recall failure/non-attempted=0;
primary evidence-risk failure/non-attempted/empty=1, transparently a conservative operational
penalty. Also report available raw claims, completed-only values and counts as sensitivity,
not substitute primary denominator. A partial report with real text remains scored in
raw secondary analysis; primary operational penalty still applies to non-completion.
Truth U contributes unsupported burden but never definite C. Missing human annotation is
not automatic model error: halt final analysis until adjudicated, or report incomplete
study plus[0,1] bounds for missing endpoints; do not silently impute truth. Undefined
conditional rates are NA with zero denominator, not0% hallucination or100% precision.
Missing timing/VRAM is NA with cause; report observed durations to failure and timeout
bound separately, no invented max value or zero cost. Missing resource fields preclude
formal resource acceptance for that invocation.

## Interpretation and trade-offs

Predeclared smallest practically interesting absolute difference:0.05 in recall or risk,
for author review. Significance alone is not practical relevance; an interval spanning
zero or the0.05 scale remains inconclusive at that resolution. No claim of equivalence
from nonsignificance. Report D−B endorsed salient recall/correct retention alongside P2;
lower risk from throwing away correct information is a trade-off, not unqualified RQ3
success. Raw risk unchanged but selective risk lower cannot establish reduced raw hallucination.

No single aggregate score, no cherry-picked quality/cost weight. Present quality vs latency,
VRAM and failure jointly. Call one method descriptively Pareto-better only if observed
recall is no lower, unsupported risk no higher, completion no lower and measured resource
costs no higher, with at least one strict difference; label this descriptive, not a
simultaneous statistical superiority proof. Otherwise explicitly report the trade-off.
Negative/null verification and costly adaptation are valid thesis outcomes.

All analysis scripts, input hashes, annotation version, seeds, denominators and table/figure
regeneration commands must be frozen and CPU-tested before final test output access.
Not implemented/executed in this design-only task; a reproducibility blocker remains.
