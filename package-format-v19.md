# Workflow Package Format — specVersion 19 (Per-Fan-Item Macro Placement: `forItem`)

Normative specification for `specVersion: 19` packages (design and rationale:
[#845](https://github.com/Consultologist/Consultologist-Blazor/issues/845)).
Everything not stated here is unchanged from
[package-format-v18.md](package-format-v18.md): the content channels, the value
types, the macro grammar, the classifier, check and template nodes, the node- and
deliverable-level `when`, and the v12 macro placement (`before`/`after`).

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}**. v5–v18
packages keep validating and executing under their frozen rules. A v18 package is
a v19 package with **one** edit (see *Migration*): nothing v19 opens is required.

What 19 opens, in one sentence: a placed macro may add **`forItem:`** to anchor it
to **one item of a `forEach` fan** the `before`/`after` section aggregates, instead
of wrapping the whole fanned block.

## `results[].macros[].forItem`

Since v12 (§ 4), a deliverable's macro entry may be a **placement object** that
carries `before` or `after` naming one of the deliverable's aggregated sources — a
macro then lands around that whole section. When the section is a **`forEach`
fan** (a node whose `forEach` fans a `data:` collection, producing one block per
item), that anchor addresses the *entire* fan as a single unit.

`forItem` refines such an anchor to a **single item** of the fan:

```jsonc
"results": [
  { "id": "consult", "node": "node:assemble-note",
    "macros": [
      { "id": "assessment-caveat", "after": "node:section-instructions", "forItem": "assessment" }
    ] }
]
```

The macro is emitted **immediately before or after that one item's rendered
block** (its `## {item name}` heading and body), between it and its neighbour —
not around the whole fan. Its value is the item's **`id`** (the stable key in the
collection's `index.json`), not its display name. Item order, and the position of
non-anchored blocks, are unchanged.

`forItem` is only meaningful on a `forEach` fan over a **`data:` collection**,
whose item ids are fixed in the package and so are validated at publish. It is
**not** offered for an `input:`-array fan, whose items are the caller's run-time
array (identity is a run-time index, unknowable at publish).

**Requirements.** A `forItem`:

- requires **specVersion 19** — below it, a `forItem` is refused by name;
- requires exactly one `before`/`after` anchor on the same entry (a `forItem`
  with no section, or with both `before` and `after`, is refused);
- requires that anchor to name a node that **`forEach`-fans a `data:` collection**
  (a `forItem` on a non-`forEach` section, or on an `input:` fan, is refused);
- must name an item the fanned collection **contains** (a `forItem` naming a
  missing item is refused).

A placement with **no `forItem`** is exactly the v12 placement: it wraps the whole
section, fanned or not.

## No hash definition moves

A v19 package using nothing v19 opens validates, renders, and hashes
**byte-identically** to its v18 self — no macro declares `forItem`. When a macro
does anchor to an item, the assembled document is the same bytes as the whole-fan
placement would produce for every other block, with the macro's expansion inserted
between the named item's block and its neighbour under the same blank-line join.
The conformance case `v19-minimal-is-v18-plus-a-line` is the no-op statement as a
fixture.

## Migration

A v18 package becomes a v19 package with one edit: `specVersion: 19`. Nothing v19
opens is required. A placed macro anchors to a section item by adding
`forItem: <item-id>` to an entry that already names that fanned section with
`before` or `after`; every other entry is unchanged.
