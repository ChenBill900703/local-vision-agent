# Formal claim units and metrics v1 — 2026-10-01

DRAFT READY FOR AUTHOR REVIEW / DESIGN ONLY. Independent human truth, never same-model
verification as truth. [Data/rubric](FORMAL_DATA_PROTOCOL.md), [statistics](FORMAL_STATISTICAL_PLAN.md).

## Atomic claims: evaluation layer, not runtime parser repair

Score **all raw investigation answers**, not merely the first4 literal runtime clauses.
Keep exact text/call/span IDs and a mapping to runtime candidates/checks. Human annotation
uses the following frozen rules; deterministic text preparation may remove Markdown
markers and split punctuation but may not infer truth. Any later automated segmentation
implementation requires documented CPU fixtures, frozen code/hash and author approval
before test outputs. No new parser or judge is implemented by this document.

| Case | Rule |
|---|---|
| Sentence/list | Split at sentence punctuation/newlines; strip bullets/numbering for analysis only; preserve offsets; split into minimal subject–predicate propositions |
| Existence/attributes | “red square on table” -> square exists; square red; square on table. Object category identifies existence unit; separate attribute/relation units |
| Conjunction | Independent colors/material/count/location assertions split; shared subject copied in annotation only; “wood or plastic” remains one disjunctive material claim, not two asserted materials |
| Introductory fragment | “main features include:” no proposition; exclude and count as nonclaim. “indoor scene, features include:” retains atomic indoor-scene claim only |
| Repetition | Within image/method, identical referent+predicate+value+polarity counted once across calls, spans retained; different objects never deduplicated merely by category |
| Uncertainty | Preserve hedge and polarity. “possibly X” still proposes X with hedged flag; no automatic supported status. “cannot determine material” is abstention metadata, not a material claim |
| Subjective | “comfortable”, “modern”, aesthetic quality -> subjective/non-observable, truth unresolved; keep in unsupported burden, separately tabulate |
| Truncated | Retain any complete independently interpretable proposition before cutoff; a clear noun phrase asserting a cup retains existence even if following location is incomplete. Incomplete predicate excluded with reason; never complete text by guessing |
| Contradictory mentions | Keep both conflicting propositions, independently label; repeated hedged and asserted forms retain strongest assertion for unique scoring and preserve hedge variants |

Truth Y: **S supported** by visible evidence; **C contradicted** by clear incompatible
visual evidence; **U unresolved/not judgeable** (occlusion, ambiguity, non-observable,
insufficient detail). Hedge alone does not erase contradiction. Material guesses and scene
types need visible supporting evidence, otherwise U. Missing COCO label alone cannot yield C.
Full-surface assessment also records original-supported but tile-unjudgeable flags, so no
resolution limitation is passed off as a definitely nonexistent object.

Hallucination/error subtypes: nonexistent object; wrong category; wrong attribute;
wrong relation/location; unsupported inferred property; subjective/non-observable claim.
First four can be C when evidence is decisive, otherwise U; latter two normally U.
Do not equate all uncertainty with proven hallucination. Report definite-error C and
unsupported burden C+U separately. Use hierarchical root-cause tags to avoid claiming a
nonexistent object's every attribute is an independent nonexistent object.
Development nonexistent cup, gold-ball/pinecone confusion and base errors motivate these
rules but contribute ZERO formal observations/statistics.

## Surfaces and notation

For each image i/method m: R = deduplicated atomic raw investigation claims; G = independently
frozen salient object instances/groups; E = offline endorsement-view atoms. A/B: E=R.
C/D: E includes only atoms fully contained in at least one runtime candidate with a
completed model-supported check. Others remain outside E but are still in R and scored.
If several candidates map to one atom, E requires at least one supported link; also report
conflicting-verdict flag. A compound supported candidate endorses ALL its atoms; any false
part counts, not just the convenient true part. A nonclaim candidate has zero valid atoms
and contributes to wasted-check count. Unmatched raw claims have no check and cannot
become implicitly supported. Runtime claim coverage and atomic coverage differ.

Truth counts S,C,U are indexed by surface; N=S+C+U. Report counts and denominators for every
rate. Semantic duplicate resolution never mutates raw traces or runtime FIFO order.

## Primary endpoints (image-macro averages, paired)

| ID / RQ / contrast | Exact per-image endpoint and direction |
|---|---|
| P1 / RQ2 / D−A | Raw salient recall = correctly mentioned unique G objects / |G|; higher better; failed/non-attempted invocation scored0 |
| P2 / RQ3 / D−B | Endorsement-view unsupported risk = (C_E+U_E)/N_E for completed nonempty views; empty/failure/non-attempted=1 conservative penalty; lower better |
| P3 / adaptive contrast / D−C | Raw salient recall as P1; higher better; post-verification view and cost reported alongside |

P2 is deliberately an evidence-risk/abstention policy endpoint, NOT pure hallucination
rate or an assertion that the report hides rejected text. Penalizing empty/failure avoids
awarding zero-error perfection for silence. Report also the ordinary rate conditional on
nonempty outputs with its denominator, U breakdown and empty fraction. The policy penalty
is not an observed false claim. If only this selective surface improves while R does not,
conclude selective endorsement improvement, NEVER reduced raw generation hallucination.
No single endpoint suffices for overall superiority; always display retained correct
content, salient recall, failures and costs (trade-off rule in statistics).

## Secondary quality and verification metrics

| Metric | Numerator / denominator; interpretation |
|---|---|
| Raw supported precision | S_R/N_R; N=0 ->NA plus empty fraction |
| Raw unsupported / definite error | (C_R+U_R)/N_R; C_R/N_R separately; do not label U as definitely false |
| Object precision | Supported object-existence/category units / all object-existence/category units |
| Nonexistent object rate/count | Independently contradicted nonexistent entities / all mentioned distinct entities; also count/image and fraction images with >=1 |
| Attribute/relation precision | S within each category / all units in that category; report C/U separately |
| Endorsed salient recall | Correct G objects present in E / |G|; zero for empty/failure |
| Correct retention | S_E / S_R; zero denominator NA; plus (S_R−S_E) count |
| Tiny/resolution-loss recall | Matched corresponding reference objects / reference objects in that predefined stratum; descriptive |
| Truncation | token_limit calls / completed generation calls; images affected / planned images |
| Language usability | Human: mainly usable Traditional Chinese / mixed or mainly Simplified / unusable; retain raw text, no conversion; counts not a new automated language gate |

Define V as unique atomic propositions with >=1 completed check mapping; record every
candidate/check independently as an additional cluster-aware table. K denotes runtime
candidate entries, L denotes completed candidate checks. Model verdict v is separate from Y.

- Runtime verification coverage = L/K (K=0 ->NA); atomic coverage = |V|/|R| (R=0 ->NA).
- Pre/post unsupported counts = C_R+U_R and C_E+U_E; also compare same candidate atoms before/after endorsement.
- False accept among checked erroneous atoms = # atoms with Y=C and any supported check / # checked atoms with Y=C; zero denominator NA.
- Unsupported endorsement rate = # endorsed checked atoms with Y in {C,U} / # endorsed checked atoms; this is not the same conditional denominator as false accept.
- Wrong rejection = # checked atoms with Y=S and contradicted verdict and no supported verdict / # checked S atoms. Unresolved is abstention, not contradiction.
- Error flagging rate = # checked C atoms explicitly contradicted with no supported verdict / # checked C atoms. This is rejection, NOT generation correction; correction generation is absent, correction rate NOT APPLICABLE.
- Model-unresolved rate = unresolved completed candidate verdicts / completed checks.
- Budget-unresolved = unselected candidates / K; interrupted/unreached checks separately counted.
- Wasted checks = checked candidate entries mapping to zero atomic propositions / completed checks.
- Verdict conflicts = atoms with both supported and contradicted checks / checked atoms.

Report S/C/U × supported/contradicted/unresolved/not-checked cross-tabs, check-level and
unique-atomic views; never silently drop compound or unselected claims. 75% runtime coverage
is NOT75% accuracy. No independence assumption among claims from the same image.

RQ1/RQ4: completion/cleanup/failure proportions, actual calls/input-output tokens, peak
allocated/reserved/sampled-device MiB, load/individual-call/model-total/Agent/total-invocation
latencies with denominators and stop reasons as in design. No BLEU/CIDEr/CLIPScore selected:
text similarity is not this study's independent visual support target. CHAIR motivates
object-error analysis, but this human free-form taxonomy is NOT a claimed reproduction
of CHAIR or its exact score. [Rohrbach et al., 2018](https://aclanthology.org/D18-1437/).
No claim-level recall/F1 without an exhaustive truth inventory; salient object recall has
its separately frozen denominator, free-form all-claim recall does not.
