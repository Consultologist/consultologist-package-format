# Workflow Package Format — specVersion 21 (Schema References: `schemaRefs`)

Normative specification for `specVersion: 21` packages (design and rationale:
[#923](https://github.com/Consultologist/Consultologist-Blazor/issues/923)).
Everything not stated here is unchanged from
[package-format-v20.md](package-format-v20.md): the content channels, the value
types, the macro grammar and placement, the classifier, check and template nodes,
the node- and deliverable-level `when`, and the inline macro slots.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21}**.
v5–v20 packages keep validating and executing under their frozen rules. A v20
package is a v21 package with **one** edit (see *Migration*): nothing v21 opens is
required.

What 21 opens, in one sentence: a declared output schema may be a **reference** to
a published catalog output-contract **by name** — `schemaRefs: { "<schema-id>":
"<contract-id>" }` — instead of an inline JSON body carried in the bundle that must
canonically match the catalog.

## The problem it solves

Until v21 the only way to declare a node's output schema was to carry its JSON body
as a file in the bundle (`schemas: { "<id>": "schemas/<id>.json" }`) and have that
body **canonically match** one of the catalog's output-contracts. Because the only
shape the catalog publishes as declarable is `concept-list`, a package author's
"schema" was always a byte-for-structure **copy** of a known contract — a copy the
publisher then re-derived at publish and pinned in the publication stamp. Carrying a
copy that must equal a published shape is a reference written the long way round.

v21 lets the package **reference** the contract directly: name it, do not copy it.
The reference resolves to the same catalog contract (and therefore the same attested
agent) the inline body would have matched — by **id**, not by body comparison.

## `schemaRefs`

A manifest may declare, alongside `schemas` (inline bodies), a `schemaRefs` map from
a **schema id** to a **catalog contract id**:

```jsonc
{
  "specVersion": 21,
  "schemaRefs": { "patient-concepts": "concept-list" },
  "nodes": [
    { "id": "extract", "prompt": "extract", "output": { "schema": "patient-concepts" } }
  ]
}
```

A node names the schema id in `output.schema` exactly as it names an inline schema
id; whether that id resolves through `schemas` (an inline body) or `schemaRefs` (a
reference) is transparent to the node. A referenced schema carries **no file** in
the bundle and is **not** canonically matched — it resolves to the contract the id
names.

### Requirements

A `schemaRefs` declaration:

- requires **specVersion 21** — below it, `schemaRefs` is refused by name;
- each value must name a **catalog output-contract** the running catalog publishes;
  a reference to an unknown contract is refused;
- a schema id lives in **exactly one** of `schemas` or `schemaRefs` — declaring the
  same id as both an inline body and a reference is refused (it would be two
  declarations of one schema).

A referenced schema is, for every downstream rule, the contract it names: a node
whose output references `concept-list` *declares concept-list* (so a `terms-subset`
check may name it, a concept renderer may format it), exactly as an inline body that
canonically matched `concept-list` would.

## Pinning and provenance

The contract a reference resolves to is pinned by the package's publication stamp,
the same single `catalogRef` that already pins every inline schema's resolved
contract: the stamp records `<schema-id> → <contract-id>` for a referenced schema
just as it does for an inline one, and its byte shape is unchanged. A package is
therefore pinned **as a whole** to one catalog version; a reference does not carry
its own per-entry version.

## No hash definition moves

A reference changes only **how a node's output schema is declared**, never what a
node produces or how it is hashed. A node referencing `concept-list` runs the same
attested agent and produces the same output — and the same `outputHash` — as a node
whose inline body matched `concept-list`. The provenance record shape is unchanged,
so **no provenance version bump** accompanies v21.

A v21 package using nothing v21 opens — no `schemaRefs` — validates, renders and
hashes **byte-identically** to its v20 self. The conformance case
`v21-minimal-is-v20-plus-a-line` is the no-op statement as a fixture.

## Migration

A v20 package becomes a v21 package with one edit: `specVersion: 21`. Nothing v21
opens is required. To replace an inline schema with a reference, drop its
`schemas` entry and its `schemas/<id>.json` file and add
`"schemaRefs": { "<id>": "<contract-id>" }`; the node that names `<id>` in
`output.schema` is unchanged.
