# Workflow Package Format — specVersion 28 (A file name is its id)

Normative specification for `specVersion: 28` packages. For design and rationale, see
[#1268](https://github.com/Consultologist/Consultologist-Blazor/issues/1268), the design document
`docs/customizable-workflow/package-format-v28-design.md` in the engine repository, and the issues
it links: #1283 the format, #1284 the engine, #1285 the editor, #1286 the bump, #1287 the content.

Like v27, this is a **full grammar**, not a delta. 28 keeps the v27 program and changes one thing:
**a file's name is its id**. The manifest stops spelling the paths the ids imply. A node names no
prompt file, `macros` and `snippets` become lists of ids, and a folder's `index.json` becomes an
object of item ids. 28 also adds one member, a flow node's display-only `description`.

**Unchanged from v27**, and not restated:
- the package identity and metadata, and the whole `inputs[]` grammar;
- the `formats` table and the format file;
- a node's `format`, `with`, `onInvalid`, `failIfEmpty` and `reproducible`;
- the objects in templates and their closed member sets, which are read by id as before;
- the derived edges and the mechanics sentence;
- the reply as a template and the strict render probe;
- the flow nodes (`for`, `if`, `case`), their bodies, and a flow node inside a `for`;
- every gate keyed `if` at its six sites, and the condition scope at those sites;
- the JSON header of a snippet, folder item or macro file (`label`, `if`, a macro's `instruction`, `optional` and `default`);
- a deliverable's `sources[]`, `check` and `signature`, and `deliverable.<id>.content`;
- the renderer pipe on the node and the hash ladders;
- everything *Refused at 27*.

Their v27 sentences hold.

A manifest declares the rule set it was validated under. The engine accepts exactly
**{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28}**
(since the engine's bump, [#1286](https://github.com/Consultologist/Consultologist-Blazor/issues/1286)).
v5–v27 packages keep validating and executing under their frozen rules.

## The rule

An id is snake_case, as at 26: a lowercase letter, then lowercase letters, digits or underscores.
At 28 a file's stem is its id:

| Declared | Its file |
|---|---|
| a node (not computed, not a flow node) | `prompts/<id>.md` |
| a macro | `macros/<id>.md` |
| a macro folder | `macros/<id>/`, with `index.json` |
| a snippet | `snippets/<id>.md` |
| a snippet folder | `snippets/<id>/`, with `index.json` |
| a folder item | `<folder>/<id>.md`, beside the index |

A computed node (its format's producer is `computed`) and a flow node have no file. Package
names (`example-macros`) are names, not ids a template reads, and are unaffected. The `formats`
table keeps its `{ id, file }` entries at 28.

## The manifest at 28

**Nodes.** A node names no file; `prompt` is retired:

```json
"nodes": [
  { "id": "identify_problem", "format": "prose" },
  { "id": "coverage", "format": "terms_subset", "with": { "of": "node.extract", "in": "node.extract" } }
]
```

`identify_problem`'s prompt is `prompts/identify_problem.md`. `coverage` is computed and reads none.

**Macros and snippets.** Each is a list of ids. A trailing `/` says the id is a folder:

```json
"macros":   ["closing", "notes/"],
"snippets": ["standards", "sections/"]
```

`closing` is `macros/closing.md`, and `notes/` is the folder `macros/notes/`. The id a template
reads is the entry without its slash (`macro.notes`, `snippet.sections`). The list keeps the folder
mark on the entry, so a reader never probes the file set to tell a folder from a file.

**A flow node's description.** A `for`, `if` or `case` node may carry `description`, a non-empty
string of at most 500 characters, the package description's limit:

```json
{ "id": "sections", "label": "Sections",
  "description": "Drafts one note per section.",
  "for": "item in snippet.sections", "nodes": ["section_notes"], "ret": "node.section_notes" }
```

It is **display only**. It is never rendered, sent to a model or hashed, and no template reads it.
The editor shows it in the flow node's pane and under the box's label in the diagram.

## Folders at 28

A folder's `index.json` is an object:

```json
{ "label": "Sections", "items": ["hpi", "medications", "assessment_plan"] }
```

- **`items`** is required. It lists the item ids in run order, and each item's file is `<id>.md`
  beside the index. The item's header (`label`, `if`, and a macro item's facts) stays in that file,
  as at 26.
- **`label`** is optional: the folder's display name. It is display only; no template reads it
  (there is no `snippet.<folder>.label`), so it never reaches rendered text or a hash.
- **No other key.** The key set is closed.

Macro folders and snippet folders take the same index. A folder `if` does not exist: gating every
item is each item's own `if`, or an `if` node around the loop.

## Stray files

A file under `prompts/`, `macros/` or `snippets/` that names nothing is a **warning**, not a
refusal, so a package may carry notes and drafts. The warning says what the file would have to be
called:

- *"prompts/old-draft.md names no node; at specVersion 28 a prompt file is prompts/<node id>.md."*
- *"macros/spare.md names no macro; at specVersion 28 a macro file is macros/<id>.md, listed in macros."*
- *"snippets/loose.md names no snippet; at specVersion 28 a snippet file is snippets/<id>.md, listed in snippets."*
- *"snippets/sections/extra.md is not listed in snippets/sections/index.json; at specVersion 28 an item is <id>.md beside the index, listed in its items."*

A file anywhere else that nothing references is refused at publish, as before.

## The record

Record storage **9**, unchanged, and no provenance version moves. No hash covers a file's name: the
record pins a package by `name@vYYYY.MM.N`, and node hashes cover rendered text. A node row's
`prompt` names its file by path, as at 26, and at 28 that path is always `prompts/<id>.md`. The
engine fills each node's prompt from the file its id implies, and runs the package as it ran the
27 package it was migrated from: the same rendered bytes, the same hashes.

## Refused at 28

Everything *Refused at 27* holds. Named at 28, each sentence the validator's:

| Refused | Sentence |
|---|---|
| `prompt` on a node | *"Node 'extract' declares prompt, which is retired at specVersion 28; a node's prompt is prompts/extract.md."* |
| `macros` or `snippets` as a map, or the 25 list of macro objects | *"macros is a map; at specVersion 28 it is a list of ids — ["closing"]."* (the package's own ids, in order) |
| an id listed twice | *"macros lists 'closing' twice."* |
| an entry that is not snake_case | the 26 sentence (*"Macro id 'Closing' must be snake_case (…)."*) |
| a non-computed node whose file is absent | *"Node 'scope' has no prompt: prompts/scope.md is missing from the package."* |
| a computed node whose file is present | *"Node 'coverage' is computed (format 'terms_subset') and reads no prompt; remove prompts/coverage.md."* |
| a missing macro or snippet file, a folder with no index | the 26 sentences |
| an index in the 26 list shape | *"Snippet folder 'sections' index.json at specVersion 28 is an object { "label"?, "items": [ids] } — { "items": ["hpi", "plan"] }; each item's file is <id>.md beside the index."* |
| an index key other than `label` and `items` | *"… index.json declares 'order', which is not an index key at specVersion 28 (the keys are label and items)."* |
| no `items` | *"… index.json has no items; at specVersion 28 items lists the folder's item ids in order."* |
| a `label` that is not a non-empty string | *"… index.json label must be a non-empty string."* |
| an `{ id, file }` item | *"… index.json item { id, file } 'hpi' — at specVersion 28 an item is its id: "items": ["hpi"]."* |
| an empty `items`, a duplicate item, an item whose file is absent | the 26 resolver's sentences |
| a snippet folder item id that is not snake_case | *"Snippet folder 'sections' item id 'Plan' must be snake_case (…)."* (the 26 gap closed; a macro folder's were checked already) |
| `description` on a plain node | *"Node 'extract' declares description; only a for, if or case node carries one — a node's prompt file says what it does."* |
| an empty or over-long `description` | *"Node 'sections' description must not be empty."* / *"… must be at most 500 characters."* |

Below 28, what only 28 spells is refused by name: *"macros is a list of ids, which requires
specVersion 28."* (the same for `snippets`), and *"Node 'sections' declares description, which
requires specVersion 28."* An index in the 28 object shape is refused below 28 by the 26 index
sentence.

## Validation

The sentence conventions are 26's. The sentences this document names are pinned by the engine's
suite. Their vectors sit under `conformance/v28/` (since package-format v2026.11.1, the bump #1286),
and the below-28 gate (*"macros is a list of ids, which requires specVersion 28."*) sits under
`conformance/v27/` (`invalid-macros-id-list-at-27`). The JSON schema for 28 is the 27 shape with
three changes: no `prompt` on a node; `macros` and `snippets` as arrays of strings matching
`^[a-z][a-z0-9_]*/?$`; an optional `description` (1–500 characters) on a node.

What the schema can't see is the validator's, and is listed `SHAPE_BLIND` in the registry's own
check:
- the file set (an implied prompt present or absent, a folder's index and what it says, a folder
  item's id);
- the relation between a node's members (a description on a plain node).

## Migration (27 → 28)

`scripts/migrate-workflow-package.cs --to 28` and the editor's upgrade run the library's rewrite
(`WorkflowPackageMigration27To28`):
1. Every node prompt, macro, snippet and folder item moves to the path its id implies. A prompt
   that several nodes shared is copied to each node's own file.
2. The manifest drops every `prompt`, and `macros` and `snippets` become id lists in their 27 order.
3. Each `index.json` becomes `{ "items": [...] }` in its 27 order. No label is invented.

The targets are computed from the 27 files, so a swap or a chain of renames cannot collide with
itself. A target the package already holds with different text refuses the migration and names
both paths. The migrated package is validated at 28 before anything is written. The ten public
packages republish at 28 under #1287: 58 prompts and 2 folder items are renamed, and every package
validates with its 27 warnings unchanged.
