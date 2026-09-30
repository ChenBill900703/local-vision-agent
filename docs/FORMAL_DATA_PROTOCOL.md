# Formal data and human reference protocol v1 — 2026-10-01

DRAFT READY FOR AUTHOR REVIEW / DESIGN ONLY. No acquisition or test inspection this phase.
[Design](FORMAL_EXPERIMENT_DESIGN.md) / [metrics and atomic claims](FORMAL_METRICS.md).

## Selected source and rights

Select **COCO 2017 val2017**, with `instances_val2017.json` and
`captions_val2017.json` from `annotations_trainval2017.zip`, plus independently authored
human references. This is a local thesis-held-out subset of a public validation split,
NOT official COCO test2017 or an official leaderboard evaluation. Official source lists
5K validation images and train/val annotation archive; no archive downloaded here.
[COCO official download source](https://raw.githubusercontent.com/cocodataset/cocodataset.github.io/master/dataset/download.htm).

COCO annotations are CC BY4.0; image copyrights remain with image owners, with use subject
to applicable Flickr terms. Do not label every image CC BY4.0. Per-image license ID/URL,
original attribution/source and intended research use must be reviewed and retained.
[COCO official terms](https://raw.githubusercontent.com/cocodataset/cocodataset.github.io/master/dataset/termsofuse.htm).
Author/institution rights confirmation remains a blocker; public data does not establish
ethics exemption or permission to publish identifiable images. No new scraping, identity
recognition, private data, redistribution or cloud image submission. Publication review
is separate. Unknown or unusable image rights exclude before split freeze, with reasons.

COCO categories/masks and captions help reference construction but are incomplete for
free-form attributes, relations, materials and context. An absent annotation is not proof
of absence. Human image review supplies independent truth for ALL output propositions.
No second dataset is selected: same paired photos support RQ2 and RQ3 only because this
additional annotation is required. Two private development photos and synthetic fixtures
are development-only; they are not alternative formal sources. No automatic fallback
source if eligibility leaves fewer than440 images: stop and amend before outputs.

## Selection algorithm and immutable manifests

Prospective sample:40 design/rubric images +400 formal test images, all four methods on
the same400. No training/calibration. Design set is for annotator training and CPU scoring
conformance, not prompt/model/preprocessing search; GPU work on it needs separate scope.
Selection is output-blind, not a selection of images the model handles well.

After separate acquisition approval, enumerate val2017 metadata and audit input safety,
rights and duplicates. Rank IDs by SHA256 UTF-8 `RD001-FORMAL-v1|<12-digit-image-id>`
ascending, tie numeric ID. Take the first40 eligible unique groups for design and next400
for test. Continue the same ranking for pre-freeze exclusions only; retain ranked audit.
Do not stratify by model outputs or choose illustrative success categories. Report the
selected category/size/scene mix; no claim of population representativeness beyond this
eligible source. Do not mix a different year's split (COCO reorganized images across years).

Eligibility: original JPEG/PNG safely decodable within existing source bounds; verifiable
research rights; no private documents, readable credentials, sensitive/graphic content,
or identity-analysis task; at least one independently identifiable object with visible
bounding-box area >=1% of448tile and both visible dimensions>=16px. Safety/content review
is by authorized humans, no cloud judge. Exclusion register stores ID, rule, reviewer/date;
no quality exclusion based on predictions, confidence, verifier verdict or later failure.

Exact duplicates: source SHA256 and oriented RGB pixel SHA256. Near duplicates: deterministic
64-bit dHash from grayscale9×8 BICUBIC pixels, horizontal left>right bits in row order;
Hamming<=5 flags for blinded human same-scene/crop/sequence review. Also review common
source IDs/URLs and visible near-duplicate candidates; cluster transitive confirmed pairs.
Keep lowest-ranked eligible member; no cluster crosses splits. Compare against local
private development photos/derivatives and synthetic fixtures without publishing them.
This heuristic misses some near duplicates; disclose it. Foundation-model pretraining
and public benchmark contamination UNKNOWN, not asserted absent.

Before test model execution, independently annotate test references without exposing
model outputs; restricted reference team may view images for rights/reference preparation
only after package approval. Development/tuning personnel may not use these images to
change policies. Final IDs and checksums cannot truthfully be listed now: not acquired.
**Manifest completion is a BLOCKER, not an assumed freeze.**

Required manifest fields: protocol/split version, dataset archive URLs and SHA256,
annotation-file SHA256, image ID/name/source URL/license/attribution, source/pixel hash,
bytes/dimensions/orientation, normalized hash and tile-tensor hash, duplicate-group ID,
inclusion reason, exclusion log, role, reference version/hash, reviewer/signoff, and
selection rank. Separate JSONL manifests sorted numeric ID, UTF-8/LF, hashed SHA256.
Retain rejected/pre-freeze candidates; after final freeze no replacement of failed cases.
No invented placeholder IDs or zero hashes allowed in executable manifests.

## Independent salient references (before outputs)

Two Traditional-Chinese-literate annotators independently inventory visible objects on
original and the exact448 model-facing image, with no captions/predictions/verifier labels.
Original may be zoomed up to200%; tile may be nearest-neighbor enlarged only, no enhancement.
Record instance IDs, region, generic category/synonyms, visible pixel bbox/area fraction,
occlusion/ambiguity, original-visible and tile-identifiable flags. Existence identifiable
in both views and threshold above -> salient primary reference. Background objects qualify
under exactly the same rule. No centrality/aesthetic preference; no automatic top-k.
For a partially occluded object use visible region, not inferred complete size. Heavily
occluded/unidentifiable objects are excluded from primary denominator and logged;
crowds not individually countable form one group reference, not invented instance counts.
Objects below threshold are tiny-object secondary references if still identifiable.
Original-visible but tile-unidentifiable items are resolution-loss references, not silently
missing data. Primary completeness is limited to this explicit operational salience rule.

Attributes do not add primary object recall points. Annotate visible color/basic shape
and clear relations separately; material/scene labels only when directly defensible.
No comfort/modernity/emotion/intention inference as truth. No person identification.
Instance match requires compatible category and distinguishing location/attribute if
needed; generic plural without location/count matches at most one group/instance, not all
identical objects. Explicit correct count may match that many distinct referenced objects.
One-to-one matching prevents duplicate mentions inflating coverage. Taxonomic synonyms
and allowed generic parents recorded in a versioned bilingual vocabulary before outputs;
unanticipated words resolved by blinded adjudication with reasons, never silent code edits.

## Human output annotation and adjudication

Human evaluation REQUIRED: two independent annotators for ALL400×4 outputs and all claims,
not a favorable subset; a third competent adjudicator resolves disagreements. Names,
availability, consent/compensation and institutional requirements still unconfirmed.
Forty design images train rubric; retain disagreements, revise only pretest version with
author approval, then sign rubric. No AI/VLM judge or machine translation.

Present anonymized image/output codes in SHA256-seeded shuffled order, strip method names,
state/verifier labels/resources; give raw investigation text with span IDs. Wording/length
can reveal workflow, so blinding is partial. Annotators first segment and independently
label atomic claims with image references; do not see same-model verdicts or another
annotator's labels. Reference vocabulary and original/tile views allowed; public captions
are supplementary clues only after visual judgment, never exhaustive ground truth.
After locked truth labels, an analyst joins candidate/check IDs for verifier metrics;
no truth relabeling in response to supported/contradicted labels.

Retain both original annotations and adjudication, with supported/contradicted/unresolved,
category, uncertainty, source spans, object/reference ID and reason. Report pre-adjudication
unit-boundary agreement (span F1), label raw agreement and Cohen kappa on aligned units;
unmatched units counted in boundary disagreement. Undefined kappa from no variation = NA,
not perfect agreement. Report per-class prevalence and counts. No invented inter-rater
scores now. If staff cannot support this workload, sample-size/rubric redesign is required
BEFORE outputs; no downgrade to one unblinded author after seeing outcomes.
