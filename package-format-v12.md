# Workflow Package Format — specVersion 12 (The Deferred Grammar, Taken: the Chosen Macro, the Placed Word, the Embedded Signature, the Check, the Conditional, the Template)

Normative specification for `specVersion: 12` packages, as implemented by
the Milestone 23 ladder (#614–#623, with #631 § 14, #634 § 15; design and
rationale:
[package-format-v12-design.md](https://github.com/Consultologist/Consultologist-Blazor/blob/b16c99261af1904e961c64dae23c4de9b3a9dffb/docs/customizable-workflow/package-format-v12-design.md),
including the decisions recorded there where the design was settled in
conversation). Everything not stated here is unchanged from
[package-format-v11.md](package-format-v11.md): macros and their closed
placeholder grammar, the signed deliverable's flag, the reproducible
claim, and everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12}**. v5–v11 packages keep validating
and executing under their frozen rules. A v11 package is a v12 package
with **one** edit (see *Migration*): nothing v12 opens is required.

What 12 opens, in one sentence: the macro gains a **per-run choice**, a
**place** in the document, a **data-gated condition**, and the
**signature as a placeholder** inside its own text; a deliverable gains a
**check** that gates its recording; and the package gains a **template
node** — the third deterministic executor, one that renders.

## `macros[].optional` + `default` — the chosen macro

A macro may declare `optional: true`, and then **must** declare
`default:` (`true` or `false`): an optional macro must say what a run
that makes no choice does. The pair is refused apart, each by name.

```yaml
macros:
  - { id: followup, label: Follow-up paragraph, file: macros/followup.md,
      optional: true, default: true }
```

The start request may carry `macroChoices: { <id>: bool }` naming
declared optional macros only — an undeclared or non-optional id refuses
the start (a request rule, not a package rule). Resolution happens once,
in the starter: choice if supplied, else the declared default. The
record's `macroChoices` says both the value and its **origin**
(`chosen` | `default`) for every optional macro — the negative is
recorded, never omitted; required macros carry no entry.

## `results[].macros[]` placed entries — the placed word

A deliverable's macro list entry may be an **object** —
`{ id, before: node:<ref> }` or `{ id, after: node:<ref> }` — placing
the macro's text against one of the aggregated sections instead of after
them all. Exactly one anchor (`before` xor `after`); the anchor must be
a source the deliverable's aggregator aggregates. The bare string form
keeps its v11 bytes and meaning: appended after the sections, declared
order.

Placement is presentation: it moves where the expanded text sits in the
assembled document, and **nothing else**. No node's `outputHash` moves —
the aggregator's hash stays over the renderer's bytes, before any
append or interleave — and `documentHash` alone covers the placed text
(see *Provenance*).

## `{{profile:signature}}` — the embedded signature

The v11 grammar refused this token by design; v12 folds it in. A macro
file may carry `{{profile:signature}}` — the running clinician's
snapshotted signature block, the same block `results[].signature: true`
appends — so a closing macro can write "Sincerely," and the signature in
one owned text, placed where the letter wants it.

The signing rules do not weaken: **a deliverable is signed once**. The
flag beside a token-carrying macro is refused; the token twice across
one deliverable's macros is refused; the token inside an `optional`
macro is refused (a per-run signature choice was rejected in #516 and
stays rejected — the same sentence guards `when`, below). The record's
`appended[]` still carries the `kind: "signature"` entry with its
`asOf`, wherever the token put it; an account with no chosen block
produces the document unsigned, said by name.

## `results[].macros[].when` — the conditional macro

The placed-entry object takes `when:` — the same closed condition
grammar results already speak (declared inputs, paths, `count()`,
arithmetic, `node:<classifier> == value` against its declared set,
boolean algebra; one grammar, two doors). `when` composes freely with
`before`/`after` and stands alone; it composes with `optional` as *AND*
(the clinician's gate and the run's gate are orthogonal). N
mutually-exclusive when-gated entries on one result is match/case,
spelled as declarations: two held arms both land, in declared order —
disjointness is the author's, and the validator proves each clause's
vocabulary, not the set's exclusivity.

Evaluation is the result-condition's three-valued rule (absence is
never held), decided **once** at the fire-set boundary and never
re-judged. A non-held macro is stripped before the document pipeline
sees it; the record's `excludedMacros[]` names every when-excluded
macro on a firing result with the condition explainer's sentence as
the reason. A `when`-skipped result never evaluates its macro clauses —
skip stays skip. A blank condition, a compared value the classifier
does not declare, and `when` gating a token-carrying macro (the
conditional signature) are each refused by name.

## `kind: check` and `results[].check` — the deliverable's gate

A check node judges instead of producing: `op: terms-subset` over two
`concept-list` operands, `of:` and `in:` (both `node:<id>` references
to nodes declaring the concept-list contract), with `failWith:` — the
package's own sentence for the failure. It declares **only** those
four members: prompt-family fields, `aggregate`, `values` and
`reproducible` are refused (a check is deterministic by construction,
and the claim is not its to make). A deliverable opts in with
`check: node:<id>` naming a check node; a check no result names is
refused (a check gates a deliverable, or it is dead weight); two
results may share one check — each gates itself.

`terms-subset` compares **SNOMED concept ids** (active, coded on both
sides): pass when `of`'s id set ⊆ `in`'s id set. Concepts the
extractor could not code are excluded from the test and recorded as
*untested*, never silently dropped.

At run time the settle and the recording split: the aggregator's
render and `outputHash` are computed exactly as today (the check gates
*recording the document*, never the node's output); the check executes
inline once both operands settle — no activity, no model, no retries.
Pass → the deferred completion chain runs (macros, signature,
`documentHash`, the document recorded — byte-identical to the
unchecked path). Fail → `failedDocuments[]` gains
`{ resultId, label, reason }` carrying the `failWith` sentence and the
uncovered ids/terms — a third state beside produced and skipped,
per-document: other deliverables are unaffected, and a package whose
only deliverable fails ends with no documents and says why. An operand
node that fails fails the checked document too — an unverifiable
document is not shipped. Check nodes (and nodes feeding only a check
chain) carry the classifier-style reachability exemption: they serve a
deliverable's existence, not its text.

## `kind: template` — the rendering node

The format's third deterministic executor, and the first that renders:
a node whose bound inputs go through the strict-mode Scriban renderer
and whose output **is** the rendered string — no model call, no agent,
no tokens. The declaration reuses the prompts table: `kind: template`
plus `prompt: <id>` naming an ordinary prompt entry; the kind alone
decides render-and-stop against render-and-ask-a-model. The
bindings-must-equal-variables rule, the publish-time probe render and
the orphan rule apply unchanged — and for a template the probe is the
strongest form of "what publishes is what runs": it renders the very
artifact the run outputs.

- `forEach` from day one: a template is a per-item chain step exactly
  as a prompt node is; binding resolution is inherited whole.
- It may declare `output:` with `failIfEmpty`: the rendered bytes must
  simply BE the contract JSON, parsed and validated by the same
  machinery a model answer goes through — except the classification
  contract, refused by name (a classification is answered from a value
  set, and a template renders, it does not answer).
- It may NOT declare `values`, the check members, `aggregate`, or
  `reproducible` (deterministic by construction — § 13's sentence, its
  second use).
- A template never enters the deciding stage: no template output can
  feed a `when`.

A render failure is deterministic — the same bytes re-render — so it
fails fast, excluded from the activity retry policy. The record: one
node row through the existing seam, **tokens null** (not recorded,
never zero), and `inputHash == outputHash == sha256(rendered)` — a
template sends no message, and the message-that-would-have-been IS the
output. The rerun verdict treats the equal pair as any other; the hash
definition does not move.

The unknown-kind sentence at 12 names four kinds
(accepted: prompt, classifier, check, template); the v10/v11 sentence
does not move.

## Provenance (normative bytes)

**No hash definition moves.** `effectiveInputHash` covers supplied
inputs only — `macroChoices` never enters it. Every node `outputHash`
is untouched by macros, placement included. `documentHash` alone
covers appended, placed and conditional text, exactly as v11's rule
already said — the digest is over `assembledDocuments[].text` with
everything inside. The rerun verdict compares clinical content and
cannot be moved by presentation choices.

What the record adds, each documented by the provenance registry
(`provenance@v2026.09.4`): `macroChoices` (value + origin per optional
macro), `excludedMacros[]` (when-excluded, with the explainer's
sentence), `failedDocuments[]` (the check's `failWith` + uncovered +
untested), the check's node row (boolean outcome, no tokens), the
template's node row (equal hashes, null tokens), and `appended[]`
re-worded to **document order** — "after the sections" becoming the
default rather than the definition, with no new field: the pinned
package version already says where each macro sits.

**The control:** a v12 package using nothing v12 opens renders and
hashes **byte-identically** to its v11 self — no choice enters, no
placement moves text, no check runs, no field appears. The conformance
case `v12-minimal-is-v11-plus-a-line` is that statement as a fixture.

## Migration

A v11 package becomes a v12 package with one edit: `specVersion: 12`.
Nothing v12 opens is required. `general` is the control — published at
11 and at 12 with no other change, byte-identical output and hashes
across the step. `example-v12-constructs` is the first package to use
what 12 opens — all six constructs in two deliverables, one of which
fails its check by construction — and the conformance suite's
`v12-all-constructs-demo` case takes its shape from it verbatim: the
demo the engine ran is the case the suite pins.
