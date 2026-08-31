# Workflow Package Format — specVersion 11 (The Appended Word: Macros, the Signed Deliverable, the Reproducible Claim)

Normative specification for `specVersion: 11` packages, as implemented by
the Milestone 22 ladder (#563–#566; design and rationale:
[package-format-v11-design.md](https://github.com/Consultologist/Consultologist-Blazor/blob/200e547d3336000cbc5527828ae7d9d2c0850453/docs/customizable-workflow/package-format-v11-design.md),
including the decisions recorded there where the design was settled in
conversation). Everything not stated here is unchanged from
[package-format-v10.md](package-format-v10.md): the classifying node and
its boundary, expression conditions, nested structure, and everything
those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11}**. v5–v10 packages keep validating and
executing under their frozen rules. A v10 package is a v11 package with
**one** edit (see *Migration*): nothing v11 opens is required.

What 11 opens, in one sentence: a package may own **named texts** that the
engine appends to a deliverable after its aggregated sections — expanded by
substitution, never by a model — and may mark a deliverable **signed** (the
signature block itself belongs to the running clinician's profile) and a
node **reproducible** (a claim the rerun verdict will read).

## `macros` — package-owned appended texts

One construct with three senses. A macro is a template file the package
owns; a template with no placeholders is fixed canned text, a template
over the run's values is a form text, and the closed `run:`/`profile:`
words are facts about the run.

```yaml
macros:
  - { id: disclaimer, label: Standing disclaimer, file: macros/disclaimer.md }
  - { id: closing,    label: Closing paragraph,   file: macros/closing.md }
results:
  - { id: letter, node: node:assemble-letter, label: Decline letter,
      macros: [disclaimer, closing], signature: true }
```

- `macros` is a top-level list; each entry has `id` (snake_case, the
  declared-id grammar, unique among macros), `label` (non-blank) and
  `file` (present in the package and **non-empty** — stated because
  prompts check presence only). `macros/<id>.md` is the convention; any
  path is legal.
- `results[].macros` is an ordered list of declared macro ids. Each named
  macro must exist; naming one twice on a deliverable is refused; and a
  macro no result names is an error — the orphan rule, as prompts have.
- Below specVersion 11 both keys are refused by name, the standing
  pattern: `macros requires specVersion 11.` and
  `Result '<id>' declares macros, which requires specVersion 11.`

### Placeholders — the closed grammar

A macro file is markdown that may contain `{{namespace:id}}` tokens. The
namespaces are **closed**:

| Namespace | Resolves from |
|---|---|
| *(none — no placeholders)* | the file itself, verbatim |
| `input:<declaredId>` | the run's effective inputs; an **optional** input draws a publish warning and renders as the empty string when not supplied |
| `data:<id>` | the package's single-value data entries (collections are not data values) |
| `classification:<nodeId>` | a classifier's normalised answer |
| `run:date` \| `run:job` \| `run:package` \| `run:host` | the run: its date (UTC, `yyyy-MM-dd`), the job id's first 8, the package ref, the deployment's canonical host (empty when the deployment names none) |
| `profile:name` | the account's display name (empty when the account has none) |

Publish-time validation resolves **every** token against the declared
inputs, data values and classifiers and the closed word lists; anything
else is refused naming the token:
`Macro '<id>' placeholder '{{token}}' does not resolve.` A malformed token
(no namespace) falls under the same sentence. `profile:signature` is
deliberately absent — the signature is `results[].signature`'s flag, with
placement and recording of its own. Expansion is substitution at assembly:
no model, no template engine, no recursion (a macro cannot include a
macro) — deterministic by construction.

### The append rule

A deliverable's assembled document is: the aggregated sections exactly as
the aggregate renderer produces them, then each macro of
`results[].macros` **in declared order**, each separated by a blank line,
expanded, verbatim — no heading is invented for a macro; its file brings
its own markdown. Then the signature (below), last. The recorded document
carries the appended text inside `text`, so every surface — the app,
history, the delivered PDF — is one text.

## `results[].signature` — the signed deliverable

`signature: true` is the package's entire vocabulary: this deliverable is
signed. The signature **block** — name, credentials, contact — belongs to
the running clinician's profile, never to the package (publication facts
are stamped, never asserted). The engine snapshots the profile's chosen
block when the job starts and appends it at completion, after every
macro, inside the document and its hash. An account with **no chosen
block** produces the deliverable **unsigned**, and the record and the
job's history say so by name — the document is the work; the signature is
a block on it. Below specVersion 11 the key's presence — even `false` —
is refused by name.

## `nodes[].reproducible` — the carried claim

`reproducible: true` on a node is the package's claim that this node's
output is the same for the same input; the classifier and
concept-extraction stages are the intended cases. Any node may carry it.
**No behaviour changes at run time**: the flag is carried onto the run's
record, not enforced. A rerun verdict reads it: a rerun passes when every
reproducible node's `outputHash` equals the source run's for the same
`inputHash`, and fails naming the first that differs; non-reproducible
nodes are shown, not counted. The honest caveat is the design record's:
reproducibility is the agent's property as much as the package's, and the
format's promise is only that the package *asked*. Below specVersion 11
the key is refused by name.

## Provenance (normative bytes)

**No hash definition moves.** The per-document digest stays SHA-256 of
`assembledDocuments[].text`; appended text — macros, the signature — is
inside `text` before the hash is stamped, so it is inside `documentHash`
and the result-set hash with no new rule. No node's `inputHash` or
`outputHash` changes: appended text is not a node's work, and the
aggregator's `outputHash` remains over the renderer's bytes, before the
append. The record names each appended block
(`assembledDocuments[].appended[]`: `{ kind: macro | signature, id,
asOf? }`, applied order) and the unsigned-although-requested state; the
provenance registry documents both (`provenance@v2026.08.11`).

**The control:** a v11 package with no `macros`, no `signature: true` and
no `reproducible: true` renders and hashes **byte-identically** to its
v10 self — no append enters, no field appears. The conformance case
`v11-minimal-is-v10-plus-a-line` is that statement as a fixture.

## Migration

A v10 package becomes a v11 package with one edit: `specVersion: 11`.
Nothing v11 opens is required. `general` is the control — published at 10
and at 11 with no other change, byte-identical output and hashes across
the step. `example-classifier-scope` is the first package to use what 11
opens: its decline letter gains `signature: true` and a `closing` macro —
from which the conformance suite's `v11-macro-signed-reproducible` case
takes its shape.
