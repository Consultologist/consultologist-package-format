# Workflow Package Format — specVersion 20 (Inline Macro Slots: `slot` + `[[slot:<id>]]`)

Normative specification for `specVersion: 20` packages (design and rationale:
[#863](https://github.com/Consultologist/Consultologist-Blazor/issues/863)).
Everything not stated here is unchanged from
[package-format-v19.md](package-format-v19.md): the content channels, the value
types, the macro grammar, the classifier, check and template nodes, the node- and
deliverable-level `when`, and the v12/v19 macro placement (`before`/`after`/`forItem`).

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}**. v5–v19
packages keep validating and executing under their frozen rules. A v19 package is
a v20 package with **one** edit (see *Migration*): nothing v20 opens is required.

What 20 opens, in one sentence: a deliverable's macro entry may be **`slot: true`**,
marking a macro the **section prompt's model output** may place *inline* — wherever
it writes the marker `[[slot:<macro-id>]]` — and the engine replaces that marker,
at document assembly, with the macro's verbatim expanded text.

## The problem it solves

A macro is deterministic, package-owned text, and until v20 it lands at a
**section/deliverable boundary**: appended after the sections, or placed
`before`/`after`/`forItem` one of them. That is the right granularity when the
author knows where the text belongs. It cannot express *"drop this fixed paragraph
wherever the model decides is the natural spot inside the prose it is writing"* —
for example, a standing side-effects paragraph the model should weave into the
Assessment & Plan at the point it discusses the drug, not before or after the whole
section.

v20 splits the decision: the **model chooses where and whether** (it emits a
marker), and the **package still owns what** (the macro's exact bytes). The model
never authors the fixed text; it only positions it.

## `results[].macros[].slot`

A deliverable's macro entry (since v11 a bare id, since v12 a placement object) may
set **`slot: true`**:

```jsonc
"results": [
  { "id": "consult", "node": "node:assemble-note",
    "macros": [
      { "id": "side_effects", "slot": true }
    ] }
]
```

This authorizes the macro `side_effects` to be filled **inline** wherever a section
prompt's model output places the marker for it. It does **not** append the macro
anywhere on its own: a `slot` macro that the model never places produces no text.

### The marker `[[slot:<macro-id>]]`

A section prompt instructs the model, in its own words, to emit the literal token
`[[slot:<macro-id>]]` at the position it chooses (or to omit it). At document
assembly the engine scans the composed document and, for each `[[slot:<id>]]`:

- if `<id>` is a macro this deliverable references with `slot: true` **and** that
  macro's `when`/`optional` gate holds → the marker is replaced with the macro's
  **verbatim expanded text** (the same `{{ns:id}}` substitution every macro gets);
- otherwise — an unknown id, a macro this deliverable did not authorize as a slot,
  or one its gate excluded — the marker is **removed** (replaced with nothing).

The `[[…]]` delimiter is deliberately **not** the `{{…}}` macro-placeholder
delimiter: the marker is written in a prompt template (whose strict `{{ }}` would
otherwise try to bind it) and must never collide with the macro grammar. The
marker lives **only in model output** — never in a macro file, never in a rendered
prompt — so neither the prompt renderer nor the macro-file validator ever sees it.
`<macro-id>` is a snake_case declared id (the macro-id grammar).

### Placement is the model's; inclusion is the author's

Emitting the marker is the model's **placement** choice. Whether the macro's text
appears at all is still governed by the macro's `when`/`optional` gate, exactly as
for an appended or placed macro: a `when`-excluded or declined-optional slot macro's
marker resolves to **empty**. A `slot` macro's marker the model does not emit
simply never appears. The two decisions are independent and each is recorded.

### Requirements

A `slot` entry:

- requires **specVersion 20** — below it, `slot` is refused by name;
- names **no anchor**: `slot` is mutually exclusive with `before`, `after` and
  `forItem` (the model owns the position, so the entry declares none). An entry
  with both is refused;
- may still carry **`when`** (the inclusion gate) and the macro may be declared
  **`optional`** — those govern inclusion as always;
- may **not** carry `{{profile:signature}}` in its macro file: a slot is placed
  wherever the model drops a marker, and a deliverable is **signed once**, so a
  slot macro carrying the signature token is refused (the same single-signature
  rule as the v12 conditional/optional macros).

The orphan rule is unchanged: a `slot` reference **counts as a use**, so a macro
referenced only as a slot is not flagged orphan.

## No hash definition moves

The marker is **model output**. It survives verbatim in the section node's
`outputHash` — that hash covers exactly what the model produced, marker included —
and the fill happens **later**, at document assembly, over the composed document.
No package text is ever folded into a node hash.

The filled text is attributed the same way an appended macro is: a **`slot`**
appended entry, recorded **outside** the node hashes and **inside** the document
hash (the assembled bytes). The provenance record shape is unchanged (the entry is
additive), so **no provenance version bump** accompanies v20.

A v20 package using nothing v20 opens — no macro declares `slot`, no model emits a
marker — validates, renders and hashes **byte-identically** to its v19 self. The
conformance case `v20-minimal-is-v19-plus-a-line` is the no-op statement as a
fixture.

## Migration

A v19 package becomes a v20 package with one edit: `specVersion: 20`. Nothing v20
opens is required. To use an inline slot, reference the macro on a deliverable with
`{ "id": "<macro-id>", "slot": true }` and instruct the relevant section prompt to
emit `[[slot:<macro-id>]]` where the model should place it; every other entry is
unchanged.
