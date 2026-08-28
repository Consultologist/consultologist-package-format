# Workflow Package Format — specVersion 10 (The Deferred Grammar: Classifying Nodes, Expression Conditions, Nested Structure)

Normative specification for `specVersion: 10` packages, as implemented by
the Milestone 21 ladder (#492–#500; design and rationale:
[package-format-v10-design.md](https://github.com/Consultologist/Consultologist-Blazor/blob/f2882e35701dc36bac80684e957ed764010d25cc/docs/customizable-workflow/package-format-v10-design.md),
including the dated amendments where the design changed in the doing).
Everything not stated here is unchanged from
[package-format-v9.md](package-format-v9.md): structured inputs and their
wire forms, fans over caller data, package metadata, several documents per
slot, delivery, CalVer, immutability, `derivedFrom`.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10}**. v5–v9 packages keep validating and
executing under their frozen rules. A v9 package is a v10 package with
**one** edit (see *Migration*): nothing v10 opens is required.

What 10 opens, in one sentence: a package may **decide** part of its own
work — a node may answer one of a declared set of values, a deliverable's
condition may read that answer and may be an expression rather than one
clause, and an input's structure may nest to any depth the package
declares.

## `kind: classifier` — the classifying node

A node may declare a kind. `prompt` is the default and may be spelled;
`aggregator` is **not** a kind — an aggregator is declared by `aggregate`
alone, and spelling `kind: aggregator` or a `kind` beside `aggregate` is
refused by name. The one new kind is `classifier`:

```yaml
nodes:
  - id: scope
    kind: classifier
    label: Is the referral in scope?
    prompt: classify-scope
    bindings:
      referral: input:consult_draft
    values: [in_scope, out_of_scope, needs_information]
```

- **`values`** is required on a classifier and forbidden on every other
  node: at least two entries, unique, each matching `^[a-z][a-z0-9_]*$` —
  the enum rules. One value is a constant, not a choice, and is refused.
- A classifier declares `prompt` and `bindings` as a prompt node does.
  It declares **no `output`** — its output contract is `classification`,
  implied by its kind — and **no `forEach`**: a classification is one
  answer, so a classifier is never fanned.
- A classifier's bindings may name **inputs and other classifiers only**
  (`input:<id>`, `node:<classifier id>`). Binding a prompt node's output, a
  data value or a fan item is refused by name.
- A prompt node **may bind a classifier** (`node:<classifier id>` renders
  as the answered value). An aggregator **may not aggregate one**: a
  classifier's value is bindable, never aggregated.

### The contract

The classifier's agent receives the rendered prompt **with a trailer the
engine appends**: a blank line and *Answer with exactly one of: `<the
declared values, in declared order>`.* The agent answers under the
`classification` output contract — `{ "value": "<one of them>" }` — and
the engine **normalises** the reply (trimmed, lower-cased) and refuses any
reply outside the declared set as a retryable contract failure. What the
record carries is the normalised value; the raw reply never leaves the
node. The classification contract is a catalog contract like `concept-list`
(`conformance/catalog-schemas.json`, output-contracts `classification`).

### The boundary

A package with classifiers does not know at start which deliverables it
will produce. The engine runs the **classifier closure** first — every
classifier and what it binds — then evaluates every deliverable's `when`
once, with the answers, decides the fire set, prunes the nodes to the
closure of the firing deliverables, expands the blocks and stamps the
count. A package without classifiers is decided at start, exactly as
before, by control flow: none of its bytes move.

Consequences the record states (provenance-record.md, storage version 7):
`deciding` while the count is not yet known; `decidedAtUtc`, the boundary
time (start, for every package without a classifier); `classifications`,
each classifier's answer; a job that ends in the deciding stage is born
`Failed` with `decisionFailureKind` — `could-not-decide` when a classifier
failed, `nothing-applied` when no deliverable's condition held with the
answers — and `startFailure` naming each skipped deliverable's reason.

## `when` — the expression grammar

A condition is an **expression**; every v9 condition is a v10 expression
byte for byte — one clause, no operator words.

```
expression  := or-expr
or-expr     := and-expr ( "or" and-expr )*
and-expr    := not-expr ( "and" not-expr )*
not-expr    := "not" not-expr | clause
clause      := "(" expression ")" | term cmp term | truthy
cmp         := == | != | > | < | >= | <=
term        := sum
sum         := product ( ("+" | "-") product )*
product     := atom ( ("*" | "/") atom )*
atom        := operand | literal | "(" sum ")" | "-" atom
operand     := path | count(path) | node:<node-id>
path        := <input-id> ( "." <field-id> )*
truthy      := path                       (a boolean or an array, as v9)
literal     := true | false | <enum-value> | <number> | YYYY-MM-DD
```

**Order of operations**, highest first: parentheses; unary minus; `*` `/`;
`+` `-`; comparison; `not`; `and`; `or`. Stated here and pinned by the
conformance suite; the editor renders explicit grouping so an author never
relies on it.

**The whitespace rule.** `+ - * /` are operators only with whitespace on
both sides: `-1` and `2026-1-1` are one token each — a literal — and the v9
sentences about them (*not a whole number*, *not a date written
YYYY-MM-DD*) are produced by the v9 rules unchanged. `seen_on - 7` is
subtraction.

### Types

- A comparison's two sides are **both numbers, or both dates**. Arithmetic
  applies to a number, a count or a date; a date admits only `±` whole
  days, and `date + days` is a date. An enum, a boolean, a text or a
  classifier's value in arithmetic is refused by name; so is arithmetic
  with no comparison, and division by a literal zero.
- `node:<id>` names a classifier — any other node is refused by name — and
  compares with `==` or `!=` only, against one of the classifier's declared
  values. A bare `node:` tests nothing.
- A **path of any depth** reaches a nested field (`patient.contact.phone`);
  each segment must be declared, and a segment into a scalar is refused
  naming the scalar's type. `count(<path>)` counts an array at any depth.
- A bare word on the right of a comparison is a literal, never an input.
- Below 10, `and`/`or`/`not`, parentheses, arithmetic, a path longer than
  two segments and `node:` are each refused **naming the version**.

### Evaluation

A clause over an absent optional input is **absent**, not false: it does
not hold, and neither does its negation — `not x` over an absent `x` is
absent too. `and` is absent when either side is absent; `or` holds when
either side holds and is absent otherwise. A `node:` clause is absent until
the boundary supplies the answer — never held, even negated. A deliverable
fires when its expression **holds**.

### Explain

A skipped deliverable's `reason` is composed of the package's own words. One
clause reads as v9's did — *needs `length_of_stay` to be > 7; it is not* —
and an expression of several reads what each clause wanted, then what each
found: *needs (length_of_stay to be > 7 and count(prior_notes) to be > 0);
length_of_stay is not, count(prior_notes) is 2*. An arithmetic clause
prints its terms by name; a classifier's answer is printed (it is a
declared value); a patient's text never is; a classifier not yet answered
reads *it is not decided*.

## Nested structure

The one-level bound is lifted: a field's `type` may be `object` or
`array`, `items` may be `array`, and `fields` and `items` recurse with the
same vocabulary at every level.

```yaml
inputs:
  - id: family_history
    type: array
    items: object
    fields:
      - id: relative
      - id: conditions
        type: array
        items: text
        required: false
      - id: contact
        type: object
        required: false
        fields:
          - id: phone
          - { id: preferred, type: enum, values: [phone, email], required: false }
  - id: grid
    type: array
    items: { type: array, items: number }
    required: false
```

- **`items` may be a type name (v9) or an element spec** — `{ type, items?,
  fields?, values? }` — recursively. A spec that is only a type writes the
  string form, so every v9 manifest round-trips byte for byte. When `items`
  is a spec it carries the element's own `fields` and `values`, and the
  array declares neither; declaring both is refused by name. Below 10 the
  object form is refused naming the version, as is a field that declares
  `items`, `fields`, or a type of `object` or `array`.
- The v9 completeness rules hold at every level: an array declares its
  `items`, an object at least one field, an enum at least two values.

### Wire form and canonical form

The v9 wire table applies at every level. The wire admits depth, so it is
bounded where the manifest cannot bound an undeclared value: a value
nested deeper than **eight** levels is a shape error (400); the per-array
(256) and per-object (64) caps apply at every level, and one total —
**4,096 values per input** — bounds what depth could multiply. Refused,
never truncated. Whether a declaration admits a value's shape in a given
slot stays the 422, with the path spelled: *element 1 field 'contact'
field 'phone' is a text and …*.

Canonicalisation is **effective-input hash definition 6**
(hash-definitions.md § 2): definition 5's rules applied recursively. A v10
map with no nested structure hashes byte-identically under 5 and 6 — the
control. v10 jobs stamp `effectiveInputHashVersion: 6`.

### Rendering, intake and the email door

Templates see nested objects and arrays as Scriban does natively; an absent
optional at any level renders as v9 says — an empty object, an empty array,
`null` for a number. The intake form is a tree: an object field a group
inside a row, an array field rows inside a row, each level with its own
*Add entry*; a value starts empty at every level and is never defaulted.

The email door names the **top-level array of text only** (numbered
stems). A required input whose structure is deeper than one level is
unreachable by email; publishing such a package **warns**, as v9 warns for
a required `number` or `object`.

### Paths and fans

A condition path reaches any depth. `forEach: input:<path>` may fan over a
nested array; the item is `{ id, name, value }` as v9 defines, with `name`
built from the labels along the path.

## Provenance (normative bytes)

- **Effective-input hash 6** — definition 5 recursed; the record stamps
  6 for a v10 job, 5 for v9, unchanged below. Definitions are never
  compared across versions.
- **Per-node hashes** — `hashVersion` does not move (5). A classifier's
  `inputHash` is over the rendered prompt **with the trailer**; its
  `outputHash` is the SHA-256 of the **normalised value**, so two runs that
  answer the same value hash the same however the model spelled its reply
  (hash-definitions.md § 4).
- **Workflow-output hash** — unchanged (definition 3).
- **The record** carries `deciding`, `decidedAtUtc`, `classifications`,
  `decisionFailureKind`, `nodeOutputs[].classification`, and the compound
  `skippedDocuments[].reason` (provenance-record.md, `provenance@v2026.08.7`
  or later).

## Migration

A v9 package becomes a v10 package by changing `specVersion` — one edit,
nothing else; the editor's *Upgrade to specVersion 10* writes it. `general`
is the control: its rendered output and its output hash are byte-identical
under 9 and 10, and its effective-input hash is byte-identical under
definitions 5 and 6, which is the assertion that nothing a v9 package does
was redefined. The first package to use what 10 opens is the demo
`example-classifier-scope` — a classifier answering *in scope*, *out of
scope* or *needs information*, and a plan, a decline letter or a request
for information produced accordingly — from which the conformance suite's
`v10-classifier-scope-demo` case is drawn.
