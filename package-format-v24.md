# Workflow Package Format — specVersion 24 (Per-item Node Macros)

Normative specification for `specVersion: 24` packages (design and rationale:
[#957](https://github.com/Consultologist/Consultologist-Blazor/issues/957)).
Everything not stated here is unchanged from
[package-format-v23.md](package-format-v23.md): the node macro attachment site,
its `before`/`after` placement and node-level `when`, the macro library and token
grammar, the deliverable placement, the classifier, check and template nodes, the
inline macro slots, schema references and custom schemas.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24}**.
v5–v23 packages keep validating and executing under their frozen rules. A v23
package is a v24 package with **one** edit (see *Migration*): nothing v24 opens is
required.

What 24 opens, in one sentence: a node macro on a node that **fans a collection**
may vary **per item** — anchored to one item (`forItem`), gated on the item
(`item:id` in its `when`), and filled from the item (`{{item:<field>}}` tokens).

## The problem it solves

v23 composes a macro into a node's prompt once per **node**: the same text, under
the same gate, for every item a `forEach` node fans. A fan over a `data:` collection
of sections (history, examination, assessment) often wants section-specific guidance
— a macro appended only for one section, or a macro whose text names the section it
is composed for. v24 resolves the node macro per **instance** instead: the fan item
the instance runs for is in scope, and the three per-item forms read it.

## `nodes[].macros[]`, per item

A node macro's placement object gains **`forItem`**, and its `when` and text gain the
item:

```jsonc
{
  "specVersion": 24,
  "macros": [ { "id": "section_guidance", "label": "Section guidance", "file": "macros/section_guidance.md" } ],
  "nodes": [
    { "id": "section-instructions", "forEach": "data:standards", "prompt": "section-instructions",
      "macros": [
        { "id": "section_guidance", "at": "after", "when": "item:id == hpi" },
        { "id": "assessment_guardrails", "forItem": "assessment_plan" }
      ] }
  ]
}
```

```markdown
<!-- macros/section_guidance.md -->
When drafting **{{item:name}}**, keep to the standard: {{item:content}}
```

- **`forItem`** — the id of one item of the `data:` collection the node fans. The
  macro is composed into that item's instance only. The collection must be a
  `data:` collection and must contain the item.
- **`item:id` in `when`** — a new condition operand, judged per instance against the
  item it runs for. The collection's item ids are a **closed set at publish**, so the
  literal is validated the way a classifier's value is: `item:id == hpi` or
  `item:id != hpi`, where `hpi` is an id the collection contains. `item:id` composes
  with the node-level grammar (`item:id == hpi and node:scope == in_scope`). It is the
  only item operand: an item's other fields are text, which a condition never
  compares. On an instance with no item in scope the clause is **absent**, never
  held.
- **`{{item:<field>}}` tokens** — filled per instance from the fan item's fields: a
  `data:` collection's declared fields (`id`, `name`, and `content` when declared),
  an input fan's `id`, `name` and `value`. The field is checked **where the macro is
  attached**, since the library macro itself has no fan.

### Input fans

An `input:` array fan's items are the caller's: their count and content are known
only at run time. So neither `forItem` nor an `item:` operand reads an input fan —
both are refused at publish. Item **tokens** do fill on an input fan (the item map
carries `id`, `name`, `value`), the way `item:` bindings always have.

### Deliverables

A deliverable composes no fan item: its macros are placed at assembly, where there is
nothing to fill `{{item:…}}` from. A macro whose text carries an item token is
therefore attached only to a node that fans — a `results[].macros[]` attachment of it
(a slot one included) is refused.

## Execution

A node macro is resolved when an **instance** is dispatched — once per fan item on a
`forEach` node. The instance's item is in scope: a `forItem` macro is skipped on every
other item; a `when` reading `item:id` is judged against the item; `{{item:…}}`
tokens are substituted from its fields. Each instance already sends its own prompt
and records its own input hash (keyed `node:item`), so a per-item macro is attested
by the instance's hash exactly as its bindings are — no new record field.

A macro whose text reads `{{classification:<id>}}` names that classifier as a
**scheduling dependency** of the node (as a `node:` operand in its `when` already did
at v23), so the token is never expanded before the classifier has answered.

## Validation

A v24 package is refused when, beyond the v23 rules:

- a node macro declares `forItem`, an `item:` operand or an item token and
  `specVersion` < 24 (each refused by name; the token as a version requirement);
- `forItem` sits on a node that does not fan a `data:` collection, or names an item
  the collection does not contain;
- an `item:` operand sits anywhere but a node macro on a node that fans a `data:`
  collection, reads a field other than `id`, is bare, is ordered, or compares to an
  id the collection does not contain;
- an `item:` operand appears in arithmetic (an item's field is a symbol);
- an item token sits on a macro attached to a node that does not fan, names a field
  the fan does not expose, or is attached to a deliverable.

All v5–v23 closures continue to hold.

## Migration

A v23 package becomes a v24 package by setting `specVersion: 24`. Nothing per item
is required; a v24 package with no `forItem`, `item:` operand or item token behaves
exactly as the v23 package it was.
