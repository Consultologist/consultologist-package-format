# Workflow Package Format — specVersion 30 (Nesting, repeating and computing)

Normative specification for `specVersion: 30` packages. For design and rationale, see
[#1337](https://github.com/Consultologist/Consultologist-Blazor/issues/1337), the design document
`docs/customizable-workflow/package-format-v30-design.md` in the engine repository, and the issues
it links: #1280 nesting, #1281 `while` and `until`, #1282 `let`, #1252 item naming, #1339 the
format, #1347 the bump.

Like v29, this is a **full grammar**, not a delta. 30 keeps the v29 program and permits four things
29 refused:
- **nesting.** A `for`, `while`, `if` or `case` may sit in a `for`'s or a `while`'s body, and a
  `for` or `while` in a branch, to any depth;
- **repeating.** A `while` runs its body again for as long as its check holds, at most `max` times;
  a `for` may stop early (`until`) or run its first items only (`max`);
- **computing.** A `let` node computes one typed value from one expression, with no model call;
- **naming.** An item may be named by one of its own fields (`labelField`).

Nothing 29 accepts changes meaning. A 29 package is a valid 30 package with the version changed.

**Unchanged from v29**, and not restated:
- the package identity and metadata, and the `inputs[]` grammar but for `labelField`;
- the `formats` table and the format file;
- the file-name rule (a file's name is its id), the manifest's id lists, a folder's `index.json`,
  and the stray-file warnings;
- a model node's `format`, `with`, `onInvalid`, `failIfEmpty`, `reproducible` and a flow node's
  `description`;
- the objects in templates and their closed member sets, which are read by id as before;
- the derived edges and the mechanics sentence;
- the reply as a template and the strict render probe;
- a loop over `snippet.<folder>`, `input.<id>` or a top-level node's value, and its count;
- a folder item's `if` and when it is decided;
- every gate keyed `if` at its six sites, and the condition scope at those sites;
- the JSON header of a snippet, folder item or macro file;
- a deliverable's `sources[]`, `check` and `signature`, the deliverable recorded at composition,
  and *produced* meaning released;
- the renderer pipe on the node and the hash ladders;
- everything *Refused at 29* but the nesting the version lifts.

Their v29 sentences hold.

A manifest declares the rule set it was validated under. The engine accepts exactly
**{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
30}** (since the engine's bump, [#1347](https://github.com/Consultologist/Consultologist-Blazor/issues/1347)).
v5–v29 packages keep validating and executing under their frozen rules.

## Nesting and paths

```json
{ "id": "parts", "label": "Parts", "for": "item in node.plan.value.sections", "nodes": ["outline", "paragraphs"], "ret": "node.paragraphs" },
{ "id": "outline", "label": "Outline the part", "format": "outline" },
{ "id": "paragraphs", "label": "Paragraphs", "for": "item in node.outline.value.points", "nodes": ["draft_paragraph"], "ret": "node.draft_paragraph" },
{ "id": "draft_paragraph", "label": "Draft paragraph", "format": "prose" }
```

**The shape.** A `for`, `while`, `if` or `case` may be listed in a `for`'s or a `while`'s `nodes`,
and a `for` or `while` in a branch, to any depth. A body may not hold the node that holds it.

**What an inner loop iterates.** Everything a loop may iterate, and what exists only inside the
outer loop:

| source | example | its count is known |
|---|---|---|
| a snippet folder, an array input | `item in snippet.subsections`, `item in input.questions` | when the job starts (the same list for every outer item) |
| a top-level node's value | `item in node.plan.value.themes` | when that node completes, once |
| the outer item's list field | `item in item.value.paragraphs` | when the outer item is known |
| a node in an enclosing loop's body | `item in node.outline.value.points` | when that node completes **for that outer item** |

The inner `for` names the **outer** item as `item`, because its own item does not exist yet.

**Item paths.** An item path is the item ids from the outermost loop inward, joined by `/`. At one
level a path is the item id, so every 29 key reads unchanged (`draft_problem:2`). Deeper, a
paragraph's row is `draft_paragraph:2/1` and its block `note:paragraphs:2/1`. A reader shows the
path with the loop ids interleaved: `parts/2/paragraphs/1`. Item ids keep their source's form:
array inputs from 0, a node's list from 1, folder items by their file stems. No id holds `/` or `:`.

**One count per loop instance.** A loop instance is an inner loop under one outer path. Each
instance settles its own count, once, and says so as a `count-resolved` event keyed by instance
(`{ loopId, count, total, pending, path }`; `path` is null for a top-level loop). An instance is
*not yet known* until its outer item exists and its source has completed. An empty inner list
settles that instance at zero items, with its reason; the outer item still completes.

**Reads across levels.**
- `item` is the innermost loop's item; `item.parent` is the enclosing loop's, and so on outward
  (`item.parent.parent`). A paragraph reads its part's title as `item.parent.value.title`.
- A node in an enclosing body is read by id and aligned on the common path: `node.outline` from
  inside `paragraphs` is this part's outline.
- A node in an inner body is a list from outside it, read as a loop's elements are
  (`{{ for e in node.paragraphs }}`).
- Another instance's nodes cannot be named: `node.draft_paragraph` always aligns to the reader's
  own path.

## `while`

```json
{ "id": "refine", "label": "Refining the summary", "while": "node.judge.value.verdict != \"good\"", "max": 3,
  "nodes": ["draft", "judge"], "ret": "node.draft" }
```

A `while` runs its body once, then again for as long as its check holds, at most `max` times. It
returns the last pass's `ret`.
- **`max` is required, 1 to 10.** There is no default: the bound is the author's.
- **The check runs after each pass**, so a `while` runs at least once — unless it declares
  **`checkFirst: true`**: then the check runs before each pass, and the `while` may run none.
- **The check is a condition** over the pass's body nodes by bare id, `pass`, and anything that
  runs before the loop.
- **`until`** may sit beside `while`, checked after each pass; whichever fires first stops it.
- **Reaching the bound is a named state**, never a silent stop: *"stopped at its bound of 3; the
  check never stopped holding"*. The run continues with the last pass's output.

**The pass.** A pass is an object with one shape everywhere: `pass`, `pass.previous`, `pass.parent`
and each element of `pass.history` have `.number` (from 1), `.node.<id>`, `.previous`, `.parent` and
`.history`.

| read | means | a dependency edge? |
|---|---|---|
| `node.judge`, `pass.node.judge` | this pass's node | yes |
| `pass.previous.node.judge`, `pass.previous.previous.node.judge` | one or two passes back (null before the first) | no |
| `{{ for p in pass.history }}…{{ end }}`, `pass.history[-1]` | every earlier pass, oldest first | no |
| `pass.parent.number`, `pass.parent.previous.node.critic` | the enclosing while's pass, skipping any `for` between | this pass: yes; earlier: no |

`pass.….node.<id>` names a node under that pass's while at any depth. Reading an earlier pass adds
no edge, so a redraft and its judge form no cycle. A negative index counts from the end of a
history only.

**From outside**, `node.refine` reads like a loop's returned node: `.content` and `.value` are the
last pass's `ret`, `.passes` the pass count, `.stopped` how it ended, and `.history` every pass
(each element's `.number` and `.node.<id>` for the while's direct body nodes, in pass order).

**A row per pass.** Body rows are keyed by pass, the pass number as the path segment (`draft:2`).
Only the last pass feeds a deliverable, so a `while` adds one block however many passes it runs.

`onInvalid: retry` stays the one-rung repair of a model node; it retries inside its pass.

## `for … until` and a `for`'s `max`

```json
{ "id": "documents", "for": "item in input.documents", "until": "node.classify.value.final == true",
  "nodes": ["classify", "extract"], "ret": "node.extract" }
```

- **A `for` with `until` runs its items in order, one at a time**, and stops after the item where
  the check holds, so which items ran is the same on every run. Only that loop (that instance, when
  nested) is serialized.
- **What `until` reads:** the item's body nodes by bare id, `item`, and anything that runs before
  the loop.
- **The items it did not run stay rows**: *"not run: stopped early at item 3"*. Their blocks are
  skipped with that reason, as an item skipped by condition is at 27. The count does not shrink.
- **`max` on a `for`** is at least 1, with no cap: the loop runs its first `max` items.
- **`.stopped`** on a `for` and on a `while` is one of `check` (a while's check stopped holding,
  zero passes included), `until`, `bound` (its `max` was reached) or `end` (a `for` ran out of
  items).

Leaving from inside a body (`break`, `continue`) is not in 30.

## `let`

```json
{ "id": "problem_count", "label": "Counting the problems", "let": "node.find_problems.value.problems | array.size", "type": "number", "onInvalid": "fail" }
```

A `let` node computes one typed value from one Scriban expression, with no model call.
- **`type`** is `text`, `number`, `boolean` or a declared object format's id. There is no bare
  list: a list is a format whose field is an array. A text format is refused.
- **`onInvalid` is required**: `fail` or `flag`. `retry` is refused — there is no model to repair.
- **It carries none of a model node's keys** (`format`, `with`, `failIfEmpty`, `reproducible`,
  `macros`, `aggregate`) and implies no prompt file.
- **It reads what a template reads at its place**: inputs, nodes, `item` inside a loop, `pass`
  inside a `while`. A `let` inside a loop computes once per item; a reduce over a nested list waits
  for that instance to settle.
- **Pure builtins only.** A `let` must give the same value on replay, so `date.now`,
  `date.utc_now`, `math.random`, `math.uuid`, `object.eval`, `include` and date's culture-settable
  format are refused by name. (A prompt may still read the clock.)
- **A type the walk can know** (`… | array.size` is a number, a comparison a boolean) is checked
  at publish; the rest at the run, under `onInvalid`.

Its row records the input hash (over the expression and the values it read), the output hash and
`producer: computed`. A deliverable that reads it is attested as one that reads a model's node.

## `labelField`

```json
{ "id": "sections", "label": "Sections to produce", "type": "array", "items": "object",
  "fields": [{ "id": "title", "type": "text", "required": true }], "labelField": "title" }
```

- **On an `array<object>` input**, `labelField` names a **required `text` field** of the element.
- **On a loop over objects** (a node's value, or an outer item's field), the loop declares it,
  validated against the element's type: in a format's schema, a field listed in `required`, typed
  as a string and not an enum. A loop over an input takes the input's `labelField`; a folder's
  items keep their `label` header.
- **The name** is the field's text, trimmed, and cut to **120 characters** ending in "…". A blank
  value falls back to the 29 name, the label and the position (*"Sections to produce 2"*).
- **Where it reaches:** the composed heading, the run rail, History, block names, item progress
  and the `block-skipped` labels.

**The item's name is kept in the job's record after its text is deleted.** The retention sweep
deletes produced text, concepts and held inputs, not names, so a name drawn from a field stays for
the life of the record, as a folder item's `label` does. **Pick a field that names the item without
patient detail** — a section's title, not a finding. A field that holds patient text puts that text
in the permanent record.

## The deliverable at 30

- **A nested list composes as nested iteration:**
  `{{ for s in node.parts }}{{ for p in s.paragraphs }}{{ p.content }}{{ end }}{{ end }}`. An outer
  element exposes each inner loop by its id, with the element members 27 gave (`item`, `content`,
  `value`, `skipped`).
- **The pipe takes the node**, inside nested iteration too (`p.draft_paragraph | concept_bullets`).
- **A `while`** composes as its returned node; **a `let`** is read as any node's value.
- **An item not run** (stopped early) composes as a skipped element.

## The record

Record storage **11** for a job at specVersion 30. A record at storage 10 or below reads as before.
The record is the provenance registry's (`provenance-record.md`, provenance v2026.11.2). At 11:
- **item keys are paths**;
- **loop-instance rows**, one per inner instance: its loop, outer path, count, settled moment and
  reason. A top-level loop keeps its 29 row;
- **pass rows** for a `while`, and the `while` row's `passes` and `stopped`;
- **the stopped-early state** of an item an `until` or `max` did not run, and the item it stopped at;
- **the `let` row**, `producer: computed`;
- **item progress per loop**, so two loops whose items share ids keep apart;
- **item names may be element text**, drawn from a `labelField`.

As at 29, the record holds hashes, ids, counts and reasons and never element values — except an
item's name drawn from its `labelField`, kept past the retention sweep and capped at 120
characters.

## Refused at 30

Everything *Refused at 29* holds but nesting. Named at 30, each sentence the validator's:

| Refused | Sentence |
|---|---|
| a body holding its holder | *"Node 'paragraphs' runs inside itself (paragraphs in parts in paragraphs); a body cannot hold the node that holds it."* |
| an inner loop over a text field | *"Loop 'paragraphs' iterates item.value.title, which the outer item types as a text, not an array."* |
| an inner loop over an undeclared field | *"Loop 'paragraphs' iterates item.value.missing; the outer item does not declare 'missing' under item.value (fields: kind, title, topics)."* |
| an inner loop over `item.id` | *"Loop 'paragraphs' iterates item.id; an inner loop iterates a list field of the outer item — item.value.<field>."* |
| a top-level loop over `item` | *"Loop 'parts' iterates item.value.sections, but it runs inside no loop; item.value names the enclosing loop's item."* |
| a source in a loop that does not enclose it | *"Loop 'paragraphs' iterates node.draft_problem.value.points; draft_problem runs inside loop 'problems' — a loop iterates a node outside it, or in an enclosing loop's body."* |
| `item.parent` with no enclosing loop | *"Node 'outline' prompt reads item.parent, but its loop runs inside no loop; item.parent is the enclosing loop's item."* |
| an inner body node read from outside | *"Node 'outline' prompt reads node 'draft_paragraph', which runs inside loop 'paragraphs'; read node.paragraphs."* |
| an inner source reading its loop | *"Loop 'paragraphs' iterates node.outline.value.points, and outline reads node.paragraphs — a loop's source runs before the loop."* |
| a while with no bound | *"While 'refine' declares no max; a while must declare its bound (1 to 10)."* |
| a bound above the cap, or zero | *"While 'refine' declares max 11; the most is 10."* / *"While 'refine' declares max 0; the least is 1."* / *"Loop 'parts' declares max 0; the least is 1."* |
| `until` or `checkFirst` misplaced | *"Node 'plan' declares until, which belongs to a for or while node."* / *"Node 'parts' declares checkFirst, which belongs to a while node."* |
| a body node reading its while | *"Node 'judge' reads node.refine, the branch it runs in; a body node reads its siblings, the outside reads node.refine."* |
| `pass` outside a while | *"Node 'plan' prompt reads pass.number, but it runs inside no while; pass is a while's pass."* |
| `pass.parent` with no enclosing while | *"Node 'draft' prompt reads pass.parent, but its while runs inside no while; pass.parent is the enclosing while's pass."* |
| a pass naming an outside node | *"Node 'draft' prompt reads pass.previous.node.plan, which is not in while 'refine'; a pass reads the while's own nodes."* |
| a history read as a value | *"Node 'draft' prompt reads pass.history as a value; a history is iterated ({{ for p in pass.history }}) or indexed (pass.history[-1])."* |
| an outside history element's `previous` | *"Node 'trail' prompt reads node.refine.history[-1].previous; a pass of node.refine.history has .number and .node.<id> — the list is in pass order."* |
| a let with no type, or a text format | *"Let 'problem_count' declares no type; a let names its value's type — text, number, boolean or an object format."* / *"Let 'problem_count' type 'prose' is a text format; a let's format types an object — or write type text, number or boolean."* |
| a let that would retry | *"Let 'problem_count' declares onInvalid retry; retry needs a model — use fail or flag."* |
| a let with a format | *"Let 'problem_count' declares format, which a let does not carry; a let computes its value from its expression and names it with type."* |
| a let reading the clock | *"Let 'problem_count' calls date.now, which is not deterministic; a let must give the same value on replay."* |
| a let's type contradicted | *"Let 'problem_count' yields a number; it declares type text."* |
| a labelField that is not a field | *"Loop 'problems' labelField 'title' is not a field of the elements of node.find_problems.value.problems (fields: name, severity)."* |
| a labelField on an enum | *"Loop 'problems' labelField 'severity' names an enum field; labelField names a required text field."* |

**Below 30**, each new key is the version gate: *"Node 'refine' declares while, which requires
specVersion 30."* — likewise `max`, `until`, `checkFirst`, `let`, `type` and `labelField` — and
*"Input 'sections' declares labelField, which requires specVersion 30."* Nesting is the gate too:
*"Loop 'paragraphs' runs inside loop 'parts', which requires specVersion 30."* and *"… runs inside
node 'gate', which requires specVersion 30."* (since package-format v2026.11.3; 26–29 said *"nesting
waits for the scheduler redesign"* and, at 27–29, *"a branch holds plain nodes"* before it).

No warning is added at 30.

## Validation

The sentence conventions are 26's. The sentences this document names are pinned by the engine's
suite. Their vectors sit under `conformance/v30/`: eighteen valid (nesting to three levels, an inner
loop over the outer item's field, a loop in a branch in a loop, a nested list in a template, a
while alone, in a loop and in a while, its passes and history, a check first, a while with until,
a for with until and with max, a let at the top, in a loop and of a format, and items named by a
field) and twenty-nine invalid. The ten below-30 gates sit under
`conformance/v29/`, and the v26 and v27 cases that pinned the older nesting sentences
(`invalid-for-inside-a-for-at-26`, `invalid-if-inside-an-if-inside-a-for-at-27`) now carry the gate
sentence. The JSON schema for 30 is the 29 schema with the version changed and a node's new
members (`while`, `max`, `until`, `checkFirst`, `let`, `type`, `labelField`) and an input's
`labelField` added; it refuses a zero `max`.

What the schema can't see is the validator's, and is listed `SHAPE_BLIND` in the registry's own
check: what an inner loop iterates, what a pass or a `let` may read, a `while`'s required bound and
its cap, and the field an item is named by are relations to the loops that enclose a node and to
the formats.

## Migration (29 → 30)

**None.** 30 only permits what 29 refused, so a valid 29 package is a valid 30 package with the
version changed. `scripts/migrate-workflow-package.cs --to 30` raises the version through the
library's `WorkflowPackageVersionRaise`, rewrites nothing, and validates at 30 before it writes
`manifest.json` and `dag.mmd`. The editor's upgrade adds the rung with the notice *"Through 30:
nothing changes in this package; loops may now nest, repeat (while) or stop early (until), and a
let computes a value."*
