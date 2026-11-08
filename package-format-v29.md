# Workflow Package Format — specVersion 29 (A count the run discovers)

Normative specification for `specVersion: 29` packages. For design and rationale, see
[#1277](https://github.com/Consultologist/Consultologist-Blazor/issues/1277), the design document
`docs/customizable-workflow/package-format-v29-design.md` in the engine repository, and the issues
it links: #1062 the scheduler core, #1278 a loop over a node's value, #1279 a folder item's `if`
reading a node, #1194 the deliverable at 29, #1301 the format, #1307 the bump.

Like v28, this is a **full grammar**, not a delta. 29 keeps the v28 program and permits two things
28 refused:
- **a loop over a node's value.** A `for` may iterate a field path under `node.<id>.value` that the
  node's format types as an array, so the loop's count is known only when that node completes;
- **a folder item's `if` reading a node.** An item's header `if` may read a scalar node's `.value`,
  and the item is then decided when that node completes.

Nothing 28 accepts changes meaning, and no new member is added to the manifest. Loops stay one
level deep.

**Unchanged from v28**, and not restated:
- the package identity and metadata, and the whole `inputs[]` grammar;
- the `formats` table and the format file;
- the file-name rule (a file's name is its id), the manifest's id lists, a folder's `index.json`,
  and the stray-file warnings;
- a node's `format`, `with`, `onInvalid`, `failIfEmpty`, `reproducible` and a flow node's
  `description`;
- the objects in templates and their closed member sets, which are read by id as before;
- the derived edges and the mechanics sentence;
- the reply as a template and the strict render probe;
- the flow nodes (`for`, `if`, `case`), their bodies, a flow node inside a `for`, and a `for` over
  `snippet.<folder>` or `input.<id>`;
- every gate keyed `if` at its six sites, and the condition scope at those sites;
- the JSON header of a snippet, folder item or macro file;
- a deliverable's `sources[]`, `check` and `signature`, and `deliverable.<id>.content`;
- the renderer pipe on the node and the hash ladders;
- everything *Refused at 28*.

Their v28 sentences hold.

A manifest declares the rule set it was validated under. The engine accepts exactly
**{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29}**
(since the engine's bump, [#1307](https://github.com/Consultologist/Consultologist-Blazor/issues/1307)).
v5–v28 packages keep validating and executing under their frozen rules.

## A loop over a node's value

```json
{ "id": "find_problems", "label": "Find problems", "format": "problem_list", "onInvalid": "fail" },
{ "id": "problems", "label": "Problems",
  "for": "item in node.find_problems.value.problems", "nodes": ["draft_problem"], "ret": "node.draft_problem" }
```

**The source** is a field path under `node.<id>.value` (`node.find_problems.value.problems`):
- A format's value is an object at the top, so the bare `node.<id>.value` is not a list. The path
  names the array field, and may go deeper through object fields (`node.x.value.a.b`).
- The field must be typed as an **array** by the node's format: `type: "array"`, its `items` an
  object or a string schema. A `concept_list`'s `concepts` field is iterated like any other array
  field.
- The node is a **plain node outside every loop and every flow node**. It is not a flow node, and
  not a node that returns prose.
- The source runs **before** the loop. The reference is the loop's edge on the node, drawn as any
  read is, so the source may not read the loop or its body.

**The items.**
- An item's id is its **1-based position**: `1`, `2`, … A node's list has no ids of its own, and a
  position is stable for one run. Rows are `draft_problem:1`, blocks `result:problems:1`.
- `item.value` is the element. `item.value.<field>` reads a field of an object element, typed from
  the format's `items` schema, so a body reading a field the element does not declare is refused.
  `item.id` is the position.
- An item's name, in rows, headings and progress, is the loop's label and the position
  (*"Problems 1"*), as an array input's elements are named.

**The count.** A loop over a node's value has no items when the job starts. It is **not yet
known**: never zero, and never a provisional count read as final. When the source node completes,
the engine reads the list from that node's recorded output and the count settles, **once**.
Nothing at 29 changes a count after it settles. A job's total is the blocks laid out so far, and
it is final when no loop is still unsettled. The stream says each settling as a `count-resolved`
event (`{ loopId, count, total, pending }`).

**An empty list** settles the loop at zero items, and the job does not fail. What reads the loop
sees what 27 gives a loop whose every item was skipped: `.content` is empty, `.value` is `[]`, and
a deliverable sourcing it composes a document with no section, not a skipped document.

**A source that fails** leaves the count *never known*, and the body does not run. The source is a
top-level node, and a top-level node's failure fails the job, naming that node, as at 28. A reply
whose value has no list there (the field is absent, is not an array, or the reply is not JSON)
fails the job the same way: *"Problems could not read its list:
node.find_problems.value.problems is not a list."*

## A folder item's `if` that reads a node

At 29 a folder item's header `if` may read, beyond inputs and `item.id`, **a scalar node's
`.value`**, in the condition grammar of the gates:

```json
{ "label": "Billing", "if": "node.scope.value == \"in_scope\"" }
```

- The node is outside every loop. It is not the loop over this folder, its body, or any other loop:
  a condition decides before the loop runs.
- `.content`, `snippet.*`, `macro.*`, item members other than `id`, `run.*` and `profile.*` stay
  refused.

**When it is decided.** An item whose `if` reads inputs only is decided when the job starts and,
when it does not hold, is dropped, **as at 28**. An item whose `if` reads a node **stays in the
folder**: it is a block and a row from the start, so the folder's count is known when the job
starts. It is decided when that node completes. When the condition does not hold, the item is
**skipped by condition**: the 27 named state, recorded with the condition's text and never the
value it read. A loop over the folder sees the item as 27's loop sees a skipped item.

**A folder read without a loop.** A template or a node that reads the folder (`snippet.sections`)
gains an edge on the gating node. It runs after that node completes and sees only the items whose
`if` holds.

## The deliverable at 29

At 29 only (26–28 are unchanged):
- A deliverable is recorded **when it is composed**. Its row carries `composedHash` and `sources`,
  and is *composed, held on its check* until its release fills in the text.
- **"Produced" means released.** A deliverable counts as produced when its document was recorded,
  or failed its check. A deliverable composed and never released does not count as produced. The
  record names it and why it was held, and the job is failed with that reason (*"Consultation note
  was composed but held: its check 'coverage' never settled."*).

## The record

Record storage **10** for a job at specVersion 29. A record at storage 9 or below reads as before.
The record is the provenance registry's (`provenance-record.md`, provenance v2026.11.1). At 10:
- **`unresolvedLoops`** names the loops whose counts are not yet known. It is empty when every
  count is known.
- **`totalBlockCount`** is the blocks laid out so far, and is final when `unresolvedLoops` is
  empty.
- **A loop row over a node's value** carries its source as written, a `count` that is null until it
  settles, `resolvedAtUtc`, and a `reason` for an empty list.
- **`heldDocuments`** lists a deliverable that was composed and not yet released.

No hash ladder moves, and the record never copies the list's element values. The source node's own
row carries its output hash, which covers the list. A settled loop's aggregate input hash is over
its items' output hashes in item order, the 25 ladder.

## Refused at 29

Everything *Refused at 28* holds, and a `for` inside a `for` is still refused. Named at 29, each
sentence the validator's:

| Refused | Sentence |
|---|---|
| the whole value, an object | *"Loop 'problems' iterates node.find_problems.value, which find_problems's format types as an object, not an array."* |
| a field typed as a text, a number or a boolean | *"Loop 'problems' iterates node.find_problems.value.summary, which find_problems's format types as a text, not an array."* |
| a field the format does not declare | *"Loop 'problems' iterates node.find_problems.value.issues; find_problems's format does not declare 'issues' under node.find_problems.value (fields: problems, summary)."* |
| a path through a field that is not an object | *"Loop 'problems' iterates node.find_problems.value.summary.x; node.find_problems.value.summary is a text, not an object."* |
| a prose node | *"Loop 'problems' iterates node.assessment.value.x; assessment returns prose — a loop iterates a value its format types as an array."* |
| a node's content | *"Loop 'problems' iterates node.find_problems.content; a loop iterates a node's value — node.find_problems.value.<field>."* |
| an undeclared node | *"Loop 'problems' iterates node.nowhere.value.x; the package declares no node 'nowhere'."* |
| a flow node | *"Loop 'problems' iterates node.sections.value; 'sections' is a flow node — a loop iterates a plain node's value."* |
| a node inside a loop, or inside a flow node | *"Loop 'problems' iterates node.section_notes.value.x; section_notes runs inside loop 'sections' — a loop iterates a node outside every loop."* (*"…runs inside node 'x' — a loop iterates a node outside every flow node."* for a branch node) |
| a source that reads the loop | *"Loop 'problems' iterates node.find_problems.value.problems, and find_problems reads node.problems — a loop's source runs before the loop."* |
| a body reading a field the element does not declare | the walker's sentence: *"Node 'draft_problem' prompt reads field 'stage' of 'item.value', which it does not declare (fields: name, severity)."* |
| a folder item's `if` reading a node's content | *"Snippet folder 'sections' item 'plan' if reads node.scope.content; a folder item's if reads a node's .value (a scalar), inputs and item.id."* |
| a folder item's `if` reading a loop, or a node inside one | *"Snippet folder 'sections' item 'plan' if reads node.sections, which loops; a condition decides before the loop runs — read a scalar node."* |
| a folder item's `if` reading anything else | *"Snippet folder 'sections' item 'plan' if reads run.date; a folder item's if reads inputs, item.id and a scalar node's .value."* |

**Below 29**, both reads are the version gate: *"Loop 'problems' iterates
node.find_problems.value.problems, which requires specVersion 29."* and *"Snippet folder
'sections' item 'plan' if reads node.scope.value, which requires specVersion 29."* (since
package-format v2026.11.2; 26–28 said the scheduler-redesign and "inputs and item.id only"
sentences before it). A folder item's other reads keep the 26 sentence below 29.

No warning is added at 29. That a loop's count is known only when its source completes is a fact
about the run, said on the Create page, not a fault in the package.

## Validation

The sentence conventions are 26's. The sentences this document names are pinned by the engine's
suite. Their vectors sit under `conformance/v29/`: three valid (a loop over an object array, a loop
over an array of strings, a node-gated folder item) and twelve invalid. The two below-29 gates sit
under `conformance/v28/` (`invalid-loop-over-a-node-value-at-28`,
`invalid-folder-item-if-reads-a-node-at-28`), and the two v26 cases that pinned the older sentences
(`invalid-loop-over-a-node-value-at-26`, `invalid-folder-item-if-reads-a-node-at-26`) now carry the
gate sentences. The JSON schema for 29 is the 28 schema with the version changed: a `for` source
and an item's header `if` are strings to a schema.

What the schema can't see is the validator's, and is listed `SHAPE_BLIND` in the registry's own
check: what a loop's source and a folder item's `if` may reach is a relation to the nodes the
manifest declares and to their formats.

## Migration (28 → 29)

**None.** 29 only permits what 28 refused, so a valid 28 package is a valid 29 package with the
version changed. `scripts/migrate-workflow-package.cs --to 29` raises the version through the
library's `WorkflowPackageVersionRaise`, rewrites nothing, and validates at 29 before it writes
`manifest.json` and `dag.mmd`. The editor's upgrade adds the rung with the notice *"Through 29:
nothing changes in this package; loops may now iterate a node's value."*
