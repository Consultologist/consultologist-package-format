# Workflow Package Format — specVersion 22 (Custom Output Schemas: `customSchemas`)

Normative specification for `specVersion: 22` packages (design and rationale:
[#760](https://github.com/Consultologist/Consultologist-Blazor/issues/760)).
Everything not stated here is unchanged from
[package-format-v21.md](package-format-v21.md): the content channels, the value
types, the macro grammar and placement, the classifier, check and template nodes,
the node- and deliverable-level `when`, the inline macro slots, and schema
references.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22}**.
v5–v21 packages keep validating and executing under their frozen rules. A v21
package is a v22 package with **one** edit (see *Migration*): nothing v22 opens is
required.

What 22 opens, in one sentence: a declared output schema may be a **custom**,
user-defined shape — `customSchemas: { "<schema-id>": "schemas/<id>.json" }` —
whose inline JSON body is **not** a catalog contract and is **not** canonically
matched, run by a generic no-tool agent and marked **unattested**.

## The problem it solves

Until v22 every declared output schema had to resolve to a catalog output-contract:
an inline body (`schemas`) that **canonically matched** one, or a **reference**
(`schemaRefs`, v21) that named one. Both are limited to the shapes the catalog
publishes as declarable — effectively `concept-list`. A package author who wanted a
*different* structured output — their own fields, for their own downstream
formatting — had no way to declare it.

v22 lets a package carry a **custom** schema: an arbitrary, author-defined JSON
object shape. It is produced by a generic, no-tool model agent (there is no
domain-attested agent and no terminology grounding behind it), so its output is
explicitly **unattested**. Execution is still reproducible — the shape is run by a
content-addressed agent pinned by the schema (and model) hash — but the shape itself
carries none of the catalog's attestation guarantees, and a deliverable block
produced from it is marked as such.

## `customSchemas`

A manifest may declare, alongside `schemas` (inline catalog bodies) and `schemaRefs`
(catalog references), a `customSchemas` map from a **schema id** to a **package
file** holding the custom JSON body:

```jsonc
{
  "specVersion": 22,
  "customSchemas": { "visit-summary": "schemas/visit-summary.json" },
  "nodes": [
    { "id": "summarise", "prompt": "summarise", "output": { "schema": "visit-summary" } }
  ]
}
```

A node's `output.schema` names a **schema id**; that id is resolved by looking it up
across `schemaRefs`, `schemas`, then `customSchemas`. A custom schema has a file
(like `schemas`) but is **not** canonically matched (like a reference); it resolves
to the reserved contract id **`custom`**.

### Single home

A schema id lives in **exactly one** of `schemas`, `schemaRefs` or `customSchemas`.
Declaring the same id in two of them is refused.

### The strict structured-output subset

A custom body is enforced at run time by a strict `json_schema`, so it must be
expressible as one. Every custom body MUST obey the structured-output subset:

- every object sets `"additionalProperties": false`;
- every one of an object's `properties` is listed in its `required` array —
  optionality is expressed by a **nullable type** (`"type": ["string", "null"]`),
  never by omission from `required`;
- nesting is bounded (at most 8 levels).

A body outside this subset is refused at validation (author/publish) time, not at
run time.

## Attestation

A custom output is **unattested** and **ungrounded**: it is produced by a generic
no-tool agent with no SNOMED binding and no domain-expert-attested prompt. The
engine records the schema hash and the generic agent/model version for
reproducibility and marks the resulting deliverable block unattested; a custom
output is never mistakable for an attested catalog contract such as `concept-list`.

## Validation

A v22 package is refused when:

- `customSchemas` is present and `specVersion` < 22;
- a custom schema id is also declared in `schemas` or `schemaRefs`;
- a custom body file is missing from the bundle, or is not valid JSON;
- a custom body violates the strict structured-output subset above.

All v5–v21 closures continue to hold.

## Migration

A v21 package becomes a v22 package by setting `specVersion: 22`. No `customSchemas`
entry is required; a v22 package with none behaves exactly as the v21 package it was.
To add a custom output, declare the id in `customSchemas`, carry its body file, and
point a node's `output.schema` at it.
