# Workflow Package Format — specVersion 26 (The manifest is a program)

Normative specification for `specVersion: 26` packages (design and rationale:
[#1104](https://github.com/Consultologist/Consultologist-Blazor/issues/1104), the design document
`docs/customizable-workflow/package-format-v26-design.md` in the engine repository, and the
issues it links — #1100 the flow nodes, #1101 the deliverable, #1102 the prompt, #1105 the header,
#1089/#1090/#1094/#1096 the gates, #1099/#1116 the folders, #1059 the pipe, #1152 the migration).
Like v25 this is a **full grammar**, not a delta: 26 makes the manifest a program over the same
objects the templates read — a loop, a branch and a gate are manifest shapes, a deliverable names
what it composes, and every text says what it is. Everything a v25 package declared that this
document retires is **refused by name** at 26 (see *Refused at 26*), with the replacement in the
sentence.

**Unchanged from v25**, and not restated: the package identity and metadata (`name`, `version`,
`templating`, `title`, `description`, `tags`, `derivedFrom`), the whole `inputs[]` grammar, the
`formats` table and the format file (producer classes, the catalogue, parameters), a node's
`format`, `with`, `onInvalid`, `failIfEmpty` and `reproducible`, the derived edges, the mechanics
sentence, the reply as a template, the strict render probe, a deliverable's `check` and
`signature`, and the macro's `optional` and `default` (now in its header). Their v25 sentences hold —
the optional/default pair judged over the header from package-format v2026.10.13 (engine #1224), on a
standalone macro and on a folder item keyed `<folder>/<item>`, in the v12 words; before that version
the pair in a 26 header was not judged (an engine ran an optional macro with no default as false).

A manifest declares the rule set it was validated under. The engine accepts exactly
**{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26}** (since the
engine's bump, [#1149](https://github.com/Consultologist/Consultologist-Blazor/issues/1149)).
v5–v25 packages keep validating and executing under their frozen rules. A v25 package becomes a v26
package through the **migration** (see *Migration*): the rewrite is mechanical and byte-identical
in what the model sees.

What 26 opens, in one sentence: a node may be a **flow node** — `for` over a collection, `if`
over a condition, `case` over a closed set — with a body of plain nodes and a returned node the
outside reads; every gate is a data key, **`if`**, at six sites; a deliverable names its
**`sources[]`** and its composed text is readable as `deliverable.<id>.content`; a node names its
**prompt file**; a snippet, a folder item and a macro file open with a **JSON header** that carries
their label, instruction, option and gate, and a folder is one shape for snippets and macros, its
items readable directly; a renderer pipe takes the **node**.

## Objects in templates

Every prompt, every snippet, every folder item, every macro text and every macro instruction is a
Scriban template — and so is the model's reply. Nothing is declared: a template references eight
reserved objects, every member access is checked at publish, and **every object has a closed
member set** — any other member is a publish refusal naming it.

| Object | Members | Value |
|---|---|---|
| `input.<id>` | the value, bare | as 25: the supplied input, **typed** as declared |
| `node.<id>` | `.content`, `.value` | a plain node's composed output as text, and the parsed output of an `object`, `enum` or `array` format; a **flow node's** are its returned node's (see *Flow nodes*): a `for` node's `.content` is the returned node's outputs in item order concatenated and its `.value` an array of them; an `if`/`case` node's are the taken branch's. A `for` node is **iterable** — `{{ for e in node.sections }}` — each element carrying `item`, the returned node's `content` and `value`, and every body node by id (`e.standard_section_draft.content`). A **body node** is scoped to its flow node: inside the body it is read by bare id; from outside, the flow node is what one reads (*"reads node 'section_instructions', which runs inside loop 'sections'; read node.sections"*). |
| `snippet.<id>` | `.id`, `.label`, `.content` | the snippet rendered; `.label` is the header's (`.name` is refused with the replacement) |
| `snippet.<folder>` | iterable; `snippet.<folder>.<item>` | each item a snippet with the three members, in the index's order; **an item is a member of its folder** — `snippet.sections.hpi.content` reads it directly (an undeclared item is refused naming the folder's items); a folder read bare, as a value, is refused |
| `item` | `.id`, `.label`, `.content` (a snippet folder) / `.id`, `.label`, `.value` (an array input) | the element the body node runs for; refused on a node that runs in no loop |
| `macro.<id>` | `.id`, `.label`, `.content`, `.prompt`, `.instruction` | `.content` is the macro's text rendered, read like a snippet; `.prompt` is the inline macro's prompt text — the instruction rendered, then the mechanics sentence; `.instruction` is the instruction rendered alone, what the model will be told, and reads as `.prompt` does for reachability |
| `macro.<folder>` | iterable; `macro.<folder>.<item>` | each item a macro with the five members, in the index's order; an item readable directly (see *Snippets and macros*) |
| `deliverable.<id>` | `.content` | **new**: the deliverable's composed text — its sources composed in order, before its macros and the signature (see *Deliverables*); no `.value`; never in a condition; never piped |
| `run` | `.date`, `.job`, `.package`, `.host` | as 25 |
| `profile` | `.name`, `.signature` | as 25 |

Rules, as 25 (static member access only; loop, `with` and `capture` variables typed from what
they bind; iteration and indexing follow the type; a reference that does not resolve or a member
outside the set is refused by name; everything is a template; every template is probed; a literal
the enum never answers warns), with four changes:

- **A renderer pipe takes the node.** `{{ node.extract | concept_context }}` replaces
  `{{ node.extract.content | concept_context }}`: a renderer renders a `concept_list` node, and it
  needs the node — its identity carries the attested concept source. The `.content` spelling is
  refused with the replacement (*"pipes node.extract.content through concept_context; at
  specVersion 26 a renderer pipe takes the node — node.extract | concept_context"*), `.value` too (no
  node identity). An `if`/`case` node pipes when its returned node's format is the pipe's and is
  refused naming the disagreement otherwise; a `for` node is refused — a list has no one text —
  naming the body node to pipe inside it; **inside a loop the pipe takes the body node by id**
  (`{{ for e in node.sections }}{{ e.per_item | concept_bullets }}{{ end }}`; `e.content | pipe` is
  refused with that replacement, `e.content` stays readable as text). A deliverable's text, a
  snippet, an input and a bare element are not nodes. The rendered bytes are what they were at 25.
- **`.label` for `.name`**, on a snippet, a fan item, a loop element's item and a macro; `.name` is
  refused with the replacement (*"reads item.name; at specVersion 26 the member is .label"*).
- **The loop element's scope.** A body node's prompt and conditions read sibling body nodes by bare
  id (item-aligned); any other text reads them through the loop (`node.sections.content`, or an
  element inside `{{ for e in node.sections }}`). A snippet or a macro text is judged at its reader.
- **`deliverable.<id>.content`** is a read with edges on every source; a condition may not read it
  (*"reads deliverable.consult; a condition decides before the sections compose — read a scalar
  node"*).

## Derived edges

As 25 — every `node.<id>` read is an edge, every `input`, `snippet`, `item`, `macro` read a read,
a node's `with` the second edge source — with the 26 additions:

- a flow node's **expression** is walked at the node (*"Node 'triage' if"*; a `case`'s subject is
  read structurally) and is the flow node's edge; a flow node waits on what its expression reads;
- a **body node's** edges are the loop's as the outside sees them; the loop waits on what its
  body reads outside the body;
- a **deliverable read** (`deliverable.<id>.content`) is an edge on each of that deliverable's
  sources; a deliverable may not source a node that reads it — the cycle check takes
  `deliverable.<id>` as a vertex;
- a **gate's reads** are edges where the gate is judged: a node's instance gate at the node, a
  macro's own gate (its header's `if`) where the macro is read or placed, a snippet's own gate where
  the snippet is read — a reader waits on what a gate it depends on reads.

The structural references stay declared and spelled as object reads: a `for`'s collection
(`item in snippet.<folder>` | `item in input.<id>`), a body's `nodes[]` and `ret`, a deliverable's
`sources[]` and `check`, a `with` parameter.

## Flow nodes

A flow node is a node in `nodes[]` with an id and one of three flow keys in place of `format`.
It has a **body** — nodes that run inside it — and it **returns** one of them. The flow node is the
only name the outside sees.

```jsonc
{ "id": "sections",
  "for": "item in snippet.standards",
  "nodes": [ "standard_section_draft", "patient_section_draft", "section_instructions" ],
  "ret": "node.section_instructions" }

{ "id": "triage",
  "if": "input.kind == \"new\"",
  "then": { "nodes": [ "full_workup" ],  "ret": "node.full_workup" },
  "else": { "nodes": [ "brief_update" ], "ret": "node.brief_update" } }

{ "id": "route",
  "case": "node.scope.value",
  "branches": [
    { "when": [ "in_scope" ],                          "nodes": [ "plan" ],   "ret": "node.plan" },
    { "when": [ "out_of_scope", "needs_information" ], "nodes": [ "letter" ], "ret": "node.letter" } ],
  "else": { "nodes": [ "hold" ], "ret": "node.hold" } }
```

- **`for`** iterates a collection whose length is known at job start — `item in snippet.<folder>`
  or `item in input.<id>` (an array input); the grammar is exactly `item in <collection>`. The loop
  variable is `item`, as in a template. Every body node runs once per item; the body is a
  sub-graph (body nodes read one another by bare id, item-aligned); leaving the body is the join.
  Two `for` nodes over one collection are two loops, explicitly. A snippet that is a file, an
  input that is not an array, and a node's value are refused as collections — the last with the
  next version's name (*"a loop over a node's value waits for the scheduler redesign — iterate an
  input or a snippet folder"*).
- **`if`** holds one Scriban boolean expression over the condition scope (see *Gates*) and a
  `then` body; `else` is optional. An `if` without `then` is refused.
- **`case`** switches on an expression whose type is a closed set — an enum input or an
  enum-format node (`classification`) — its `branches[]` one per set of values (a branch's `when[]`
  lists one or more; Scriban's word for the label, and **the only place `when` appears in a
  manifest**) and an optional `else`. A value the set lacks is refused, not warned; a value listed
  twice, or taken by two branches, is refused naming both; an empty `when` is refused; a `case`
  over a text is refused.
- A node carries **one** flow key; a flow node declares no `format`, `prompt`, `with` or
  `onInvalid` (it is structural); a body key (`nodes`, `ret`, `then`, `else`, `branches`) on a node
  without its flow key is refused, and so is a key the kind does not carry (`then` on a `for`).

**The body is a set; `ret` is required.** A body's `nodes[]` carries no order — the body's reads
order it. A body node is declared once in `nodes[]` and *attached* by id; a node attached to two
bodies, or attached and read by bare id from outside, is refused naming the flow node to read;
a body naming an undeclared node is refused. Every flow node and every branch names the body node
the outside reads with **`ret`** (`node.<id>`, a member of that body) — required, no default
(*"loop 'sections' returns nothing; name the body node the outside reads with ret"*). A body node
that is neither returned nor read by another body node is refused as unreachable. **At 26 a body
holds plain nodes**: a `for` inside anything, and an `if` or `case` inside a `for`, are refused
naming the version that takes them (*"loop 'paragraphs' runs inside loop 'sections'; nesting
waits for the scheduler redesign"*); `while`, `for … until` and `let` are not 26 flow nodes.

**What the outside reads** (`node.<flow>`):

| read | `for` | `if` / `case` |
|---|---|---|
| `node.x.content` | the returned node's composed outputs in item order, concatenated — byte-identical to the 25 aggregator's `.content` over one fan source | the taken branch's returned node's `.content` |
| `node.x.value` | an array of the returned node's values, one per item, typed by the returned node's format; refused when the returned node is text | the taken branch's `.value`, typed only when every branch's returned node has one format — otherwise refused by name while `.content` stays |
| `node.x` bare, in `{{ for e in node.x }}` | iterable: `e.item`, `e.content`, `e.value`, every body node by id | not iterable; refused as a bare node read |
| `node.x \| <renderer pipe>` | refused — a list has no one text; pipe a body node inside it | allowed when the returned node's format is the pipe's |
| `node.x` in a condition | refused — a condition decides before the loop runs | allowed when typed; refused when the branches disagree |

An `if` or `case` with no `else` and no branch taken is **skipped**: the node reads as null in a
template (`{{ if node.triage }}` guards it), is refused in a condition, and a deliverable whose
source it is is skipped with the reason naming the branch. There is no merge node — the `ret` of
an `if`/`case` is the merge — no retry node and no sub-workflow node.

## Gates

A gate is a Scriban boolean expression on a thing that stays data: it does not move the thing into
a body, it says when the thing is live. Its key is **`if`**, everywhere; `when` outside a `case`
is refused with the replacement (*"declares when, which is retired at specVersion 26; a gate is
keyed if; when is a case branch's label only"*).

| site | home at 26 | effect when it does not hold |
|---|---|---|
| a macro's own gate | the macro file's header `if` | the macro is **inert**: `.prompt` and `.content` render empty, its placements skip (recorded with the gate's text) |
| a node instance's gate | `nodes[].macros[].if` | the placement skips; and the node's **inline read** of that macro (`macro.<id>.prompt`) renders empty — the instance's `if` governs it; two instances on one node: the read renders when any holds; no instance: the read renders as ever |
| a deliverable's gate | `deliverables[].if` | the deliverable is skipped (its readers read null) |
| a deliverable instance's gate | `deliverables[].macros[].if` | the placement skips |
| a folder item's gate | the item file's header `if` | the item is left out of every loop over its folder (the folder's size at job start) and reads empty where read directly |
| a standalone snippet's gate | the snippet file's header `if` | `snippet.<id>.content` renders empty where read |

- **The condition scope** is 25's: inputs (typed), a scalar node's `.value`, `run`, `profile`; a
  flow node's `.value` when typed; **never** a `for` node (*"reads node.sections, which loops; a
  condition decides before the loop runs — read a scalar node"*), never `deliverable.<id>`, never
  an item of a loop the gate does not sit in. A node instance's `if` on a body node may read
  `item.id`, typed against the loop's items (*"compares item.id to 'nope', which the folder does
  not contain (items: hpi, plan)"*); on a node in no loop `item.*` is refused. A folder item's `if`
  reads **inputs and its own `item.id`** only (*"… a folder item's if reads inputs and item.id
  only, so the folder's size is known at job start"*). A macro's and a standalone snippet's own `if`
  reads no item. Operators as 25; a literal an enum does not declare is refused.
- **Composition is AND.** A macro has three places that gate it: its own `if` (the source), an
  instance's `if` (the node), and the text guard around a read (the destination — `{{~ if … ~}}`,
  legal at 26). A read or a placement narrows the macro's gate and never widens it; a macro gated
  off is off everywhere. An empty inline read appends **no** mechanics sentence.
- **`forItem` folds into the gate**: `forItem: "hpi"` is `if: "item.id == \"hpi\""`; several items
  are one gate over `||`; the key is refused with the replacement.
- **The instruction is required where it is read inline** — `macro.<id>.prompt` reachable by a run
  from a node's prompt through the snippets and folder items it reads — and optional otherwise
  (*"Macro 'closing' is read inline by node 'assessment' and declares no instruction; the model
  is told nothing"*). A placed-only macro's instruction, when present, is kept and unread. A
  blank rendered instruction is an empty read: no mechanics sentence.
- Every gate is walked as a template (its reads are edges), typed, and evaluated by the strict
  render probe.

## Formats

Unchanged from 25 — the format file, the producer classes, the catalogue and `formats[]` are as
`package-format-v25.md` says. The node's 26 members:

```jsonc
{ "id": "assessment", "label": "Assessment", "prompt": "prompts/assessment.md", "format": "prose",
  "failIfEmpty": "The assessment is empty.",
  "macros": [ { "id": "closing", "at": "after", "if": "input.kind == \"new\"" } ] }

{ "id": "scope", "label": "Scope", "prompt": "prompts/scope.md", "format": "classification",
  "onInvalid": "fail", "with": { "values": [ "in_scope", "out_of_scope" ] } }
```

- **`prompt`** is a **file path** relative to the package root (`prompts/assessment.md`), required
  unless the producer is `computed`; `prompts[]` is gone (*"prompts is retired at specVersion 26; a
  node names its prompt file"*); a `prompt` that is a declared id rather than a path is refused
  naming the file; a missing file is refused. A prompt file carries **no header** — a prompt has no
  label, instruction or gate of its own; one that opens with a header is refused. Two nodes that
  want one text read one snippet from two one-line prompts, or hold two files. The walk's subject
  for a node's prompt is *"Node 'x' prompt"*.
- `forEach`, `aggregate` and `when` on a node are **retired** (see *Refused at 26*): a fan is a
  `for` node whose body holds the node, a gate an `if` node, an aggregator a deliverable's sources.
- `id`, `label`, `format`, `with`, `onInvalid`, `failIfEmpty`, `reproducible` as 25.

## Snippets and macros

The label, the instruction, the option and the gate of a snippet or a macro live **in the file**,
in a header the format reads and Scriban never sees. The manifest keeps what only the manifest can
know: the id, the order, the placements, the nodes.

### The header

```
{
  "label": "Assessment and plan",
  "if": "input.note_type == \"consult\"",
  "instruction": "If the plan prescribes letrozole, …"
}
The text begins on the line after the closing brace.
```

- The first line of the file is exactly `{`; the header ends at the first line that is exactly
  `}`; between them is one JSON object. A BOM and CRLF are tolerated. The text is everything after
  the closing line (one newline consumed). A Scriban line opens with `{{`, so a template body is
  never a header.
- A snippet or macro file with no header is refused naming its kind (*"snippets/standards.md has
  no header; a snippet file opens with { "label": … }"*). A header on a **prompt** file is refused.
- **Closed key set.** Snippet and folder item: `label` (required), `if`. Macro: `label` (required),
  `instruction` (required where read inline), `optional`, `default`, `if`. Anything else is refused
  naming the key; the reserved names `id`, `file`, `content`, `value`, `prompt` are refused by name;
  a value of the wrong type is refused; a header that is not one JSON object is refused.
- **One home.** `macros[]`'s `label`, `instruction`, `optional` and `default` in the manifest, and
  an index item's `name` and `when`, are retired by sentence naming the file.
- **Scriban never sees it.** The text that renders is the text after the header; `{{` in a header
  value is a string. The **stamp is unchanged**: files hash whole, header included.

### Snippets

```jsonc
"snippets": { "standards": "snippets/standards.md", "sections": "snippets/sections/" }
```

A snippet is a `.md` file with a header, a full Scriban template after it, used by **reading** it.
A **folder** is a directory with an `index.json` holding the ordered list **`[{ "id", "file" }]`**
— the index carries the order, and nothing else; the 25 object (`{ fields, items }`) and an item's
`name` or `when` are refused naming the header. Each item file carries its own header (`label`,
`if`). A snippet id and an item id are snake_case; a snippet's file, a folder's `index.json` and
every item's file must be in the package. A folder item is read by iterating the folder or
**directly** (`snippet.<folder>.<item>`); its header `if` governs both. Snippets may read snippets,
inputs, scalar nodes, `deliverable.<id>.content`, and `macro.<id>.content` / `.prompt`.

### Macros

On the wire `macros` is a **map**, as `snippets` is:

```jsonc
"macros": { "closing": "macros/closing.md", "section_notes": "macros/section_notes/" }
```

Each value is a file with a macro header, or a **folder** (a trailing `/`) with the same
`index.json` list whose items are macro files — the kind follows the declaration. The 25 list of
objects is refused at 26 (*"macros is a list; at specVersion 26 macros is a map { "<id>": "<file>"
| "<dir>/" } — the file's header carries label, instruction, optional, default and if"*). A macro
folder is **read, not placed**: `{{ for m in macro.section_notes }}{{ m.label }}: {{ m.prompt }}{{ end }}`
iterates its items in the index's order, and an item reads directly as `macro.<folder>.<item>`;
placing the folder, or an item by `<folder>.<item>`, is refused by name — a package that needs a
placed folder item is the case that decides its shape. An item read inline needs its instruction;
an item's header `if` is its own gate.

#### Instances

A macro is placed on a node (`nodes[].macros[]`: `{ id, at: before | after, if }`) or on a
deliverable (`deliverables[].macros[]`: `{ id, at: prepend | append, if }`), and **read inline** by
writing `{{ macro.<id>.prompt }}` in a prompt or a snippet — that read is the inline macro's
declaration. `at` as 25; **`if`** replaces `when` and `forItem` (see *Gates*); identity is
(id, at) on a node and on a deliverable, the same identity twice refused — two gates to one text
is one instance with `if: a || b`. Only a node whose format has `outputMacros: true` may carry an
instance or an inline read. A library macro never placed and never read from a template a run
renders is refused as unused; a folder is used when it is iterated or an item of it is read.

#### Composition and the record, the reference rule and cycles, the mechanics sentence, the reply is a template

As 25, with the 26 words: an instance excluded by its `if` is recorded with the gate's text; an
inert macro's placements are recorded with its header's gate; `deliverable.<id>` is a vertex of the
reference graph; the mechanics sentence is appended only to a non-empty rendered instruction.

## Deliverables

```jsonc
"deliverables": [
  { "id": "consult", "label": "Consultation note",
    "sources": [ "node.sections", "node.patient_header" ],
    "if": "input.encounter_kind == \"new_patient\"",
    "check": "node.note_coverage",
    "macros": [ { "id": "closing", "at": "append" } ],
    "signature": true }
]
```

- **`sources[]`** — required, ordered. Each entry is `node.<id>` naming a declared node, once,
  whose text is prose: a prose-format node, a `for` node whose returned node is prose, or an
  `if`/`case` node whose every branch returns prose. A node of an `object`, `enum`, `array` or
  `concept_list` format is refused as a source (*"source node.extract is a concept_list; a
  deliverable composes prose — read its .value from a prose node"*); a `check` node is refused
  (*"a check gates a deliverable, it is no text"*); a body node is refused naming its loop
  (*"source node.section_notes runs inside loop 'sections'; name node.sections"*). **Two
  deliverables may share a source.** `node` is retired (*"declares node, which is retired at
  specVersion 26; a deliverable names its sources"*) and so is the aggregator.
- **Composition order** is unchanged: prepended macros → the sources in list order (a `for`
  source's items in item order) → appended macros → the signature. The composed text's hash is the
  25 aggregator's, stamped on the deliverable.
- **`if`** replaces `when`; **`check`** as 25; a deliverable macro reads scalar nodes, flow nodes
  and `deliverable.<id>.content` — never a body node by name (*"place the macro on a body node to
  read its items"*).
- **Reachability**: every node must transitively reach a deliverable's sources (*"Node 'x' does
  not feed the deliverable: … name it in a deliverable's sources"*); every deliverable's sources
  must transitively include at least one `for` node (*"a deliverable with no loop has no consult"*),
  the sentence naming the loops the package has.
- **`deliverable.<id>.content`** is the composed text before macros and the signature; a reader
  waits on every source; a deliverable may not source a node that reads it (the cycle names it).

## Refused at 26

Each keeps its frozen rules below 26; at 26 each is a sentence naming the key and the replacement
(the 25 form, *"`<key>` is retired at specVersion 26; <replacement>."*).

| Refused | Replaced by |
|---|---|
| `nodes[].forEach` | a `for` node whose body holds the node |
| `nodes[].when` | an `if` node whose body holds the node |
| `nodes[].aggregate` | `deliverables[].sources[]` |
| `deliverables[].node` | `deliverables[].sources[]` |
| `prompts[]`; `nodes[].prompt: <prompt id>` | `nodes[].prompt: "<file path>"` |
| `nodes[].macros[].forItem` | the instance's `if` on `item.id` |
| `when` on a node instance, a deliverable, a deliverable instance, a folder item | `if`; `when` is a `case` branch's label only |
| `index.json` as the `{ fields, items }` object; an item's `name`, `when` | the ordered list `[{ id, file }]`; the item file's header `label`, `if` |
| `macros[]` as a list; `label`, `instruction`, `optional`, `default` in the manifest | the map `{ "<id>": "<file>" \| "<dir>/" }`; the macro file's header |
| a snippet, folder item or macro file with no header; a header on a prompt file | the header |
| `item.name`, `snippet.<id>.name`, `macro.<id>.name` | `.label` |
| `{{ node.x.content \| <renderer pipe> }}`; `node.x.value \| <pipe>`; `e.content \| <pipe>` in a loop | `{{ node.x \| <pipe> }}`; `e.<ret> \| <pipe>` |
| a flow node without `ret`; a branch without `ret` | `ret` |
| a body node read by bare id from outside its flow node; a node in two bodies | the flow node's id |
| a `case` value the set lacks; a value in two branches; an empty `when` | the enum's values |
| a `for` inside a `for`; an `if` or `case` inside a `for`; a `for` over `node.<id>.value`; a folder item's `if` reading a node; `while`; `for … until`; `let` | the next version, named in the sentence |
| `node.<for>` or `node.<for>.content` piped; `deliverable.<id>` in a condition; `deliverable.<id>.value`; `deliverable.<id>.content` piped | a body node piped inside the loop; a scalar node; `.content` |
| placing a macro folder, or an item by `<folder>.<item>` | reading the folder |

## Validation

The sentence conventions at 26: a retired key reads *"`<key>` is retired at specVersion 26;
<replacement>."*; a template refusal opens with its subject — *"Node 'x' prompt"*, *"Snippet
'x'"*, *"Snippet 'f/i'"*, *"Macro 'm'"*, *"Macro 'f/i'"*, *"Macro 'm' instruction"* — and a
condition's with its site — *"Node 'x' if"*, *"Node 'x' macro 'm' if"*, *"Deliverable 'd' if"*,
*"Deliverable 'd' macro 'm' if"*, *"Snippet folder 'f' item 'i' if"*, *"Macro 'm' if"*, *"Snippet
's' if"*; a header refusal opens with the file's path; a renderer refusal ends *"(node.<id>)"*; a
shape the next version takes names it.

Every sentence above is pinned by a vector under `conformance/v26/`, with the below-26 gates
(*"… requires specVersion 26"*) under `conformance/v25/` (the `macros` map below 26 is pinned in
the engine's suite alone: a 25 manifest's typed writer spells the list, so no vector can carry
the shape). A 26 case resolves its catalogue formats against
`conformance/format-catalog.json`. The JSON schema (`schemas/package-format-v26.schema.json`)
catches the retired keys, the `macros` map, the flow keys and the closed body shapes, `sources[]`
and `if`, the id patterns and the required members; everything cross-field — a flow node's body
and `ret`, a `case` value, a source's format, a header, a template's reads, a gate — is the
validator's and is listed `SHAPE_BLIND` in the registry's own check.

## Migration (25 → 26; mechanical, byte-identical in what the model sees)

The library rewriter `WorkflowPackageMigration25To26` — manifest and files in, manifest and files
at 26 out, one notice per rewrite, a refusal applying nothing — which the engine's
`scripts/migrate-workflow-package.cs --to 26` and the editor's upgrade both run.

| At 25 | At 26 |
|---|---|
| N nodes with `forEach: snippet.standards` | **a `for` node per aggregated chain**: for each body node an aggregator sources, one loop `{ id, for: "item in snippet.standards", nodes: [that node + the body nodes it reads inside the collection], ret: node.<that node> }`; the id is the collection's when it is the collection's only loop (`standards`), otherwise `<collection>_<ret>` (`sections_consult_note_section`), named in the notice; two aggregators sourcing one node share its loop; a fanned node no aggregator reaches, a node read by two chains, a loop id a node holds — refused |
| a node with `when: C` | an `if` node `{ id: "<node>_if", if: C, then: { nodes: [node], ret: node.<node> } }`; readers read `node.<node>_if`; siblings sharing C refused |
| `aggregate: [...]` + `deliverables[].node: node.<agg>` | `deliverables[].sources: [...]` — a fanned source becomes its loop, a scalar stays; the aggregator removed |
| a template's `node.<agg>.content` | `deliverable.<id>.content` where one deliverable names the aggregator; `node.<loop>.content` where none does and it has one fanned source; otherwise refused |
| `when` on an instance, a deliverable, a deliverable instance, a folder item | `if`, the expression unchanged |
| `forItem: "hpi"` (+ `when: C`) | `if: "item.id == \"hpi\""` (`(C) && …`) |
| `prompts[]` + `nodes[].prompt: <id>` | `nodes[].prompt: "<the prompt's file>"`; `prompts[]` removed; a prompt bound by two nodes refused |
| `{{ node.x.content \| concept_bullets }}` | `{{ node.x \| concept_bullets }}` |
| `index.json` `{ fields, items: [{ id, name, file, when? }] }` | `[{ id, file }]`; each item file gains the header `{ "label": <name>, "if": <when> }` |
| `macros[]` `{ id, label, file, optional?, default?, instruction? }` | the map `{ "<id>": "<file>" }`; each file gains the header with the rest |
| a standalone snippet file | gains `{ "label": <id humanised> }` — the one value the migration invents, named in the notice |
| `item.name`, `.name` in templates | `.label` |

The seven public packages migrate without a refusal and validate at 26: `general`, `test/general`
and `example-two-documents` with the loop `standards`; `example-v12-constructs` with
`standards_section_instructions` and `standards_letter_body`; `example-classifier-scope` with
`plan_sections`, `letter_decline_letter` and `letter_information_request`;
`example-conditional-documents` with `sections_consult_note_section` and
`sections_progress_note_section`; `example-structured-intake` with its three `sections_*` and two
`prior_notes_*` loops. A migrated prompt renders the bytes the 25 one did: a `for` node's
`.content` and `deliverable.<id>.content` are the aggregator's bytes, and the pipe on the node
renders what the pipe on its text rendered.
