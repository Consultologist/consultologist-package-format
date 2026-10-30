# Workflow Package Format — specVersion 27 (A flow node inside a `for`)

Normative specification for `specVersion: 27` packages (design and rationale:
[#1173](https://github.com/Consultologist/Consultologist-Blazor/issues/1173), the design document
`docs/customizable-workflow/package-format-v27-design.md` in the engine repository, and the
issues it links — #1234 the format, #1235 the engine and the record, #1236 the editor, #1237 the
bump, #1238 the content). Like v26 this is a **full grammar**, not a delta: 27 keeps the v26
program and permits one shape v26 refused by name — an `if` or `case` node inside a `for`'s body,
decided **once per item**, the loop's length still known at job start. Nothing a v26 package
declared is retired; a v26 package is a v27 package by its version alone (see *Migration*).

**Unchanged from v26**, and not restated: the package identity and metadata, the whole `inputs[]`
grammar, the `formats` table and the format file, a node's `format`, `with`, `onInvalid`,
`failIfEmpty` and `reproducible`, the objects in templates and their closed member sets, the
derived edges, the mechanics sentence, the reply as a template, the strict render probe, the
top-level flow nodes (`for`, `if`, `case`) and their bodies of plain nodes, every gate keyed `if`
at its six sites and the condition scope at those sites, the node's prompt file, the JSON header
and the folders of one shape, a deliverable's `sources[]`, `check` and `signature`,
`deliverable.<id>.content`, the renderer pipe on the node, the hash ladders, and everything
*Refused at 26*. Their v26 sentences hold.

A manifest declares the rule set it was validated under. The engine accepts exactly
**{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26}**; 27 is
listed in `spec-versions.json` once the engine's bump
([#1237](https://github.com/Consultologist/Consultologist-Blazor/issues/1237)) runs it. Until then
a 27 manifest meets the accepted-set sentence, and this document says what the engine's validator
already says at 27 (pinned in its own suite). v5–v26 packages keep validating and executing under
their frozen rules.

What 27 opens, in one sentence: a `for`'s `nodes[]` may name an **`if` or `case` node**, whose
branches' nodes are body nodes of the loop too — attached once, through the flow node — and whose
condition is decided **once per item** over the item, the inputs and the loop's earlier body
nodes; the loop may **return** the flow node; **one level**: a branch holds plain nodes.

## Objects in templates at 27

As 26, with the loop element and the loop's reads widened by the inner flow node:

| Object | at 27 |
|---|---|
| `node.<loop>` | when the loop returns an inner `if`/`case`, "the returned node" is, per item, **the taken branch's returned node for that item**: `.content` the taken nodes' outputs in item order concatenated; `.value` the array of their values, typed only when every branch's returned node has one format — otherwise refused by name while `.content` stays (*"reads node.sections.value, but loop 'sections' returns 'triage', whose branches return 'object' and 'text'; node.sections.value needs one format — read node.sections.content"*) |
| `{{ for e in node.<loop> }}` | each element carries `item`, `content`, `value` and every body node by id — now **including the inner flow node** (`e.triage.content`, the taken branch's for that item); `e.value` is refused as `.value` is when the branches disagree (*"… e.value needs one format — read e.content"*) |
| `node.<inner flow>` | **inside the loop**, a later body node reads the flow node by bare id, item-aligned (`{{ node.triage.content }}`); **from outside** it is refused as a body node is (*"reads node 'triage', which runs inside loop 'sections'; read node.sections"*) — the flow node has no job-level value |
| `node.<branch node>` | a branch node is read by bare id by its branch's siblings; a **loop body node** outside the branch reads the flow node instead (*"reads node 'patient_draft', which runs inside node 'triage'; read node.triage"*); a branch node reads the **loop's body nodes** by bare id, one level up (*"Patient {{ item.label }}: {{ node.section_notes.content }}"*), and never the loop (*"reads node.sections, the loop it runs in; a body node reads its siblings, the outside reads the loop"*) |
| `item` | as 26 in a branch node's prompt — `.id`, `.label`, `.content` under a snippet folder; `.id`, `.label`, `.value` under an array input, `item.value.<field>` typed by the element's declaration — the inner flow node and its branch nodes run under the loop's fan |

## Derived edges at 27

As 26, with:

- an **inner flow node's expression** is walked at the node (*"Node 'triage' if"*) under the loop's
  fan and the flow node's own scope; what it reads is the flow node's edge, item-aligned where it is
  a body node; it is **not a gating read** of the job — the loop's length is known at start and the
  decision is inside the loop's run;
- a **branch node's** edges are its reads; the flow node's **decision** precedes its branch nodes
  (the engine attaches the taken branch per item);
- the loop depends on its `ret` as at 26 — the flow node, when returned.

## Flow nodes at 27

```jsonc
{ "id": "sections",
  "for": "item in snippet.standards",
  "nodes": [ "standard_draft", "triage" ],
  "ret": "node.triage" }

{ "id": "triage",
  "if": "item.id == \"narrative\"",
  "then": { "nodes": [ "patient_draft", "instructions" ], "ret": "node.instructions" },
  "else": { "nodes": [ "table_draft" ],                   "ret": "node.table_draft" } }

{ "id": "topic_sections",
  "for": "item in input.topics",
  "nodes": [ "route" ],
  "ret": "node.route" }

{ "id": "route",
  "case": "item.value.kind",
  "branches": [
    { "when": [ "narrative" ], "nodes": [ "plan" ],   "ret": "node.plan" },
    { "when": [ "table" ],     "nodes": [ "letter" ], "ret": "node.letter" } ] }
```

- **The shape.** A `for`'s `nodes[]` may name an `if` or `case` node. The flow node is a member of
  the loop's body like any other; its branches' nodes are **body nodes of the loop too**, attached
  once — through the flow node, never also listed in the loop's `nodes[]` (*"Node 'patient_draft'
  is attached to 'triage' and to loop 'sections'; a branch node is attached once, through its flow
  node"*); a node in the branches of two flow nodes of one loop meets the 26 sentence (*"a node runs
  in one body"*). They run once per item, item-aligned, as every body node does.
- **`ret`.** The loop's `ret` may name the flow node; then the loop returns, per item, what the flow
  node returned for that item. A loop may still return a plain body node beside the flow node —
  the flow node then gates a side branch that node reads by bare id. An inner flow node the loop
  neither returns nor a body node reads is unreachable (*"Node 'triage' in loop 'sections' is
  neither returned nor read; name it with ret or read it from a body node"*); inside each branch,
  reachability is as at 26.
- **One level.** A loop's body may hold flow nodes; a flow node's body holds **plain nodes** — an
  `if` inside an `if` inside a `for` is refused naming the chain (*"Node 'detail' runs inside node
  'triage', which runs inside loop 'sections'; at specVersion 27 a branch holds plain nodes"*). A
  `for` inside anything stays the next version's (*"Loop 'inner' runs inside node 'triage'; nesting
  waits for the scheduler redesign"*). An `if`/`case` inside an `if`/`case` **at the top level**
  stays refused, in 27's words (*"Node 'detail' runs inside node 'triage'; at specVersion 27 a
  branch holds plain nodes"*).
- **Below 27** an `if`/`case` in a `for` is a gate (*"Node 'triage' runs inside loop 'sections'; a
  flow node inside a loop requires specVersion 27"*), replacing the 26 "later issue" sentence for
  that case; the `for`-inside-anything sentence is unchanged.

**What the condition may read.** Inside a loop, the `if` expression (and a `case` subject) reads:

- **`item.*`** — the loop element: a folder item's `id`, `label`, `content`; an array input's
  element's `id`, `label`, `value` and its typed fields (`item.value.kind`);
- **inputs**, `run`, `profile` — the 26 condition scope;
- **body nodes earlier in the body**, by bare id — a plain body node of the same loop that the flow
  node's own reads order before it (`node.standard_draft.value.kind`), item-aligned; a
  classification body node is a `case` subject (`"case": "node.standard_draft.value"`);
- **a top-level scalar node's `.value`** — settled before the loop runs, as at 26.

Never: **the loop itself** (*"Node 'triage' if reads node.sections, the loop it runs in; a
condition inside a loop reads the item, inputs and earlier body nodes"*), **the flow node's own
branch nodes** (*"Node 'triage' if reads node 'patient_draft', which 'triage' decides; a
condition reads what runs before it"*), **a body node of another loop** (the 26 cross-scope
sentence, *"… which runs inside loop 'other'; read node.other"*), a `deliverable.` (as at 26).

A `case` inside a loop switches on a closed set as at 26 — an enum input, an enum-format body
node — or an **enum field of the item** (`item.value.<field>`, an `array` input of objects whose
field is declared `enum`); the rule at 27 reads *"a case switches on an enum input (input.<id>), an
enum-format node's value (node.<id>.value) or, inside a loop over an array input, an enum field of
the item (item.value.<field>)"*. A text field is refused (*"switches on item.value.title, which is
a text; …"*), a field the element does not declare names the fields (*"… which the item does not
carry (fields: kind, title); …"*), a folder item's field is text (*"… but a folder item's fields
are text; …"*), and a `case` on an item in no loop (*"… but it runs in no loop; …"*). A branch
value is one of the field's values, as at 26.

**When the decision is made.** A top-level `if`/`case` is decided once per job, as at 26. An inner
flow node is decided **once per item**, by the same rule applied inside the item: reads of
`item.*`, inputs, `run`, `profile` and top-level settled nodes only → decided when the item
starts; reads of an earlier body node → decided when that body node completes for the item. The
decision is made in an activity over the recorded outputs, once per `flow:item`; the job starts as
a 26 job does.

**Skipped by condition.** An inner `if` with no `else` and no branch taken, or a `case` whose
value no branch lists and no `else`, **skips the item for that flow node**. The item is still a row
of the loop (the count is kept): the flow node's row for the item is *skipped by condition*,
recorded with the **condition's text** — never the value it read (a record never prints a patient
value; the v26 wording "and the value it read" is superseded). The branch nodes of that item run
nothing and have no rows for it.

**What the loop returns with a skipped item:**

| read | with the skipped item |
|---|---|
| `node.sections.content` | the item contributes **nothing** — the concatenation runs over the items that returned; the record names the skipped ones |
| `node.sections.value` | **one element per returned item** (no null holes); a reader that needs the position iterates the loop |
| `{{ for e in node.sections }}` | **every item**, in order; a skipped element has `e.item`, `e.skipped == true`, and `e.content`/`e.value` null |
| a deliverable sourcing the loop | composes the returned items' parts; a document whose every item was skipped is a document with no section, **not** a skipped document |

The loop's aggregate input hash is over the present items' output hashes, in item order, so a 26
loop with no inner flow hashes byte-identically at 27.

## Deliverables at 27

As 26, with one rule widened: a `sources[]` entry naming a `for` node whose returned node is an
inner `if`/`case` composes when **every branch** returns prose; otherwise the first branch that
does not is named (*"Deliverable 'consult' source node.sections loops over 'triage', whose then
returns 'full_extract' of format 'concept_list'; a deliverable composes prose"*).

## The record

Record storage **9** (the engine's [#1235](https://github.com/Consultologist/Consultologist-Blazor/issues/1235);
the provenance registry's `provenance-record.md`): an inner flow row carries `in: <loop>` and a
per-item **`branches`** map (`itemId → "then" | "else" | "<values>" | "none"`) where a top-level
flow row keeps its one `branch`; a branch node's rows stay `nodeId:itemId` for the items it ran;
the inner flow node gets a `nodeOutputs` row per item **only when skipped** (`<flow>:<item>`,
status `skipped`, the condition's text as the reason). Documents are unchanged.

## Refused at 27

Everything *Refused at 26* holds. Named at 27:

| Refused | Replaced by |
|---|---|
| a branch node listed in the loop's `nodes[]` too | attached once, through its flow node |
| an `if`/`case` inside a branch (inside a loop, or at the top level) | one level: a branch holds plain nodes |
| a `for` inside anything; a count that changes; `while`; `for … until`; `let` | the next version, named in the sentence |
| an inner condition reading its loop, its own branch nodes, another loop's body node, `deliverable.<id>` | the item, inputs, earlier body nodes, a top-level scalar node |
| a `case` on a text field of the item, a field it does not carry, a folder item's field, an item in no loop | an enum field of an array input's element |
| `node.<loop>.value` and `e.value` when the returned flow node's branches disagree | `.content` |
| a sourced loop returning a flow node with a non-prose branch | every branch prose |
| `node.<inner flow>` from outside the loop; a loop body node reading a branch node; a branch node reading its loop | `node.<loop>`; the flow node; the loop's body nodes and `node.<loop>` from outside |
| recording the value a condition read | the condition's text |

## Validation

The sentence conventions are 26's. The sentences this document names are pinned by the engine's
suite at the seam; their vectors sit under `conformance/v27/` once the bump lists 27, and the
below-27 gate (*"… a flow node inside a loop requires specVersion 27"*) under `conformance/v26/`
(`invalid-if-inside-a-for-at-26`) from package-format v2026.10.14. The JSON schema for 27 is the 26
shape with its version: the permission is cross-field — a flow node's membership of a loop's body
— so every 27 refusal is the validator's and is listed `SHAPE_BLIND` in the registry's own check.

## Migration (26 → 27)

None: 27 only permits what 26 refused. The engine's `scripts/migrate-workflow-package.cs --to 27`
and the editor's upgrade raise `specVersion` and validate; the seven public packages are valid at
27 unchanged and do not republish for this bump. A new example package
(`example-conditional-sections`: a loop over sections whose `if` reads the item) is the content's
proof.
