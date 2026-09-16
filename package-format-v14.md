# Workflow Package Format — specVersion 14 (The Union Type: a Slot That Accepts One of Several)

Normative specification for `specVersion: 14` packages (design and rationale:
[#729](https://github.com/Consultologist/Consultologist-Blazor/issues/729)).
Everything not stated here is unchanged from
[package-format-v13.md](package-format-v13.md): the single value types, the
content channels (`expectedContent`), the macro grammar, the check and template
nodes, and everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14}**. v5–v13 packages keep validating
and executing under their frozen rules. A v13 package is a v14 package with
**one** edit (see *Migration*): nothing v14 opens is required.

What 14 opens, in one sentence: an input slot's `type` may be a **set** of value
types — "this or that" — and the engine accepts a supplied value that matches
**any** arm, recording which one it matched.

## `inputs[].type` as a union

`type` may be a single type name (the v≤13 form, unchanged) **or an array of two
or more distinct type names** — a union. The engine accepts a supplied value
matching any arm, trying them **in the array's order** and taking the first that
fits (first-match).

```yaml
inputs:
  - { id: notes, label: Prior notes, type: [text, array], items: text }   # one string OR many
  - { id: code, label: Billing code, type: [enum, text], values: [a, b, c] } # a choice OR free text
```

**Value types only.** A union is over value kinds (`text, date, enum, boolean,
number, object, array`); the content channel (`expectedContent`, v13) is a
separate, single-valued axis and **may not** be declared on a union slot.

**One sub-declaring arm.** The slot carries a single `items`/`fields`/`values`,
so a union carries **at most one** arm that needs a sub-declaration: `items`
serves an `array` arm, `fields` an `object` (or array-of-objects) arm, `values`
an `enum` arm. A union pairing two such arms (e.g. `[array, object]`) is refused
by name. Any number of scalar arms may join the one structured/enum arm.

**Refused by name:** a union on a manifest below 14; an arm outside the type
vocabulary; a type named more than once; two sub-declaring arms; `expectedContent`
on a union.

## Provenance (normative bytes)

**No hash definition moves.** The union is enforced at start exactly as a single
type is; the `effectiveInputHash` is over the supplied value's bytes, unchanged.
Which arm a value matched is recorded on the record as **`resolvedInputTypes`**
(input id → the matched arm) — beside the input hash, never inside it, the
`inputOrigins` posture (provenance@v2026.09.9). It is attribution: derivable from
the stored value and the pinned declaration, recorded for convenience.

**The control:** a v14 package using nothing v14 opens renders and hashes
**byte-identically** to its v13 self — no slot declares a union, no arm is
recorded. The conformance case `v14-minimal-is-v13-plus-a-line` is that statement
as a fixture.

## Migration

A v13 package becomes a v14 package with one edit: `specVersion: 14`. Nothing
v14 opens is required. A slot adopts a union by writing `type` as an array of
type names on an otherwise unchanged input; a single type name keeps writing —
and reading — exactly as before.
