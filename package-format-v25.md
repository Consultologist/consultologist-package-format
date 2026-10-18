# Workflow Package Format — specVersion 25 (The template is the source of truth)

Normative specification for `specVersion: 25` packages (design and rationale:
[#987](https://github.com/Consultologist/Consultologist-Blazor/issues/987), the design document
`docs/customizable-workflow/package-format-v25-design.md` in the engine repository). Unlike
v13–v24 this is a **full grammar**, not a delta: 25 restructures how a template reaches the
package, what a node declares, and where text comes from. Everything a v24 package declared
that this document retires is **refused by name** at 25 (see *Refused at 25*), with the
replacement in the sentence.

**Unchanged from v24**, and not restated: the package identity and metadata (`name`, `version`,
`templating`, `title`, `description`, `tags` — required, as since v9 — and `derivedFrom`), the
whole `inputs[]` grammar (the type vocabulary, `values`, `items`, `fields`, unions,
`expectedContent`), a macro's `optional` and `default`, and a node's `reproducible` (see *The
node* for the one rule 25 adds to it). Their v24 sentences hold.

A manifest declares the rule set it was validated under; the engine accepts exactly
**{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25}** — this
version is listed in `spec-versions.json` since package-format v2026.10.5. v5–v24 packages keep
validating and executing under their frozen rules. A v24 package becomes a v25 package through the editor's **migration**
(see *Migration*): the rewrite is mechanical and byte-identical in what the model sees.

What 25 opens, in one sentence: a template **reads** the package through seven reserved
objects with closed member sets, its edges are **derived** from what it reads, a node declares
one **format** (shape, producer, macro rule, parameters) that replaces the output schemas and
the classifier/check/template kinds, **snippets** are text that is read and **macros** are
text that is placed, and the list of deliverables is called `deliverables`.

## Objects in templates

Every prompt, every snippet, every macro text and every macro instruction is a Scriban
template — and so is the model's reply (see *The reply is a template*). Nothing is declared:
a template references seven reserved objects, every member access is checked at publish, and
**every object has a closed member set** — any other member is a publish refusal naming it.

| Object | Members | Value |
|---|---|---|
| `input.<id>` | the value, bare | the supplied input, **typed** as declared: a date formats, a boolean branches, an object's fields path (`input.patient.name`), an array iterates |
| `node.<id>` | `.content`, `.value` | `.content` is the node's **composed** output as text; `.value` is the parsed output of an `object`, `enum` or `array` format — fields path, arrays iterate, every path checked against the format's schema at publish. The bare read is refused by a sentence naming `.content`; `.value` on a `text` format is refused. |
| `snippet.<id>` | `.id`, `.name`, `.content` | the snippet rendered |
| `snippet.<folder>` | iterable | each item a snippet with the three members; a folder read bare, as a value, is refused |
| `item` | `.id`, `.name`, `.content` (snippet-folder fan) / `.id`, `.name`, `.value` (input fan) | the fan item the instance runs for; refused on a node that does not fan |
| `macro.<id>` | `.id`, `.name`, `.content`, `.prompt` | `.content` is the macro's text rendered, read like a snippet; `.prompt` is the inline macro's prompt text — the instruction rendered, then the mechanics sentence (see *Macros*) |
| `run` | `.date`, `.job`, `.package`, `.host` | the run facts, as the v11 `{{run:…}}` tokens gave them |
| `profile` | `.name`, `.signature` | the profile facts, as the v11/v12 `{{profile:…}}` tokens gave them; a `profile.signature` read in a placed deliverable macro signs (see *Macros*); anywhere else — a prompt, an instruction, a reply — it is the node's fact, empty unless a deliverable placement carried the signature |

Rules:

- **Static member access only.** A dynamic index on a reserved chain (`node[name]`,
  `input.history[s.id]`) is refused. A literal integer index on an array path is static and
  steps into the element (`node.extract.value.concepts[0].term`). A string-literal index is a
  member spelled the only way Scriban allows a hyphen (`node["identify-problem"].content`) and
  stays a valid static access; it is never the expected spelling, since node ids are
  snake_case at 25 (see *Formats*).
- **Loop, `with` and `capture` variables are typed from what they bind.** `for s in
  snippet.sections` gives `s` the snippet members; `for c in node.extract.value.concepts` the
  schema's element; `for h in input.history` the declared element; anything else is untyped
  and its members pass. A variable named one of the seven objects is refused — as a loop
  variable, as an assignment target (`{{ node = 1 }}`) or as a `capture` target.
- **Iteration and indexing follow the type.** A `for` over a text, or an index into one, is
  refused naming the operand; a field read on a scalar (`input.notes.length`) is refused as a
  field of a text.
- **The ≤24 words are named when they appear.** A read of `data` is answered with `snippet`; a
  read of `bindings` with the objects a template reads.
- **A reference that does not resolve, or a member outside the closed set, is refused by
  name.** A bare global that is not an object, a loop variable or a Scriban builtin is refused.
- **Renderer pipes are typed.** `{{ node.extract.content | concept_context }}` is the attested
  rendering a binding's `as: concept-context` gave; the renderer set is unchanged. A renderer
  renders the `.content` of a `concept_list` node and only that: the text of a node of another
  format, a node's `.value`, an input's, a snippet's, an item's or a macro's text, a folder or a
  literal piped through a renderer is **refused** by name; an operand the walk cannot type (an
  assigned or loop variable, a nested expression) is judged when it renders. A loop over
  `node.extract.value.concepts` is the package's own rendering. A bare `.content` read of a
  structured format renders the JSON and the validator **warns**; the same read through a
  renderer pipe does not.
- **Everything is a template.** Snippets render, macro text renders, prompts render. `raw`
  prompts are refused; a literal `{{` is escaped the Scriban way (`{{ "{{" }}` or a
  `{%{ … }%}` block), and a `{{` never closed is refused naming its line.
- **Every template is probed.** After the walk, each prompt, snippet, macro text and macro
  instruction is rendered strictly over a probe scope shaped like the package (every input,
  node value and snippet given a typed placeholder); a template that parses and types but
  fails to render (`input.notes | date.to_string "%Y"`) is refused with Scriban's message, the
  sentence opening with the template (`Prompt 'x' failed strict rendering: …`, `Macro 'x'
  instruction failed strict rendering: …`).
- The v24 placeholder form `{{ns:id}}` is refused naming the placeholder: at 25 references are
  objects.

## Derived edges

At publish the validator parses each template and walks its syntax tree:

- every `node.<id>` read is an **edge** (a scheduling dependency, reachability, the diagram);
  a reference inside a conditional branch is still an edge — conservative, stated;
- every `input.<id>`, `snippet.<id>`, `item.<member>`, `macro.<id>` read is a **read**;
- the **second edge source** is a node's `with` (see *Formats*): each value is an object
  reference in the same grammar, typed by the parameter's declaration.

Edges carry the rules bindings carried: a cycle is refused naming the nodes; a fan reading a
node that fans a different source is refused (two fans align only over one source); a node
that does not fan and reads a fan is refused — aggregation is explicit, through an aggregator
node (`aggregate`). A `forEach` names a declared snippet **folder** (a snippet that is a file
is refused as such) or a declared input of type `array` (any other type is refused naming it). What stays declared is structure, not prose: a node's `forEach`, an
aggregator's `aggregate`, a deliverable's `node` and `check` — each spelled as an object
reference (`snippet.<folder>`, `input.<id>`, `node.<id>`; see *Conditions and references*).

A template that reads a node is, in effect, that node's prompt. One prompt used by two nodes
with *different* upstream nodes needs a per-node alias map, deferred until a package needs it.

## Formats

A **format** is one file saying what a node's output is, who produces it, and whether macros
may be placed on it. It replaces `schemas`, `schemaRefs`, `customSchemas`, `output.schema` and
the `classifier`, `check` and `template` node kinds. A node declares one.

### The format file

```jsonc
{
  "type": "object",            // the input type vocabulary, reused: text | enum | boolean | number | date | object | array
  "producer": "custom",        // attested | custom | rendered | computed
  "outputMacros": false,       // may macros be placed on this output — true only on text; absent reads as false
  "description": "…",
  "schema": { … },             // required on every type object (a custom file carries the package's shape, a catalogue file its own); refused elsewhere
  "values": [ … ],             // only with type enum — or the set comes through a parameter of kind values
  "parameters": { … }          // only with producer attested or computed: name → { kind: node | text | values, format?: <catalogue id> }
}
```

The file carries **no id**. The id belongs to whoever lists the file — the manifest's
`formats[]` for a package-local format, the catalogue index for a catalogue one. One file
shape, one validator, for both.

### Producer classes

| Producer | Meaning | What the file must carry | Who stands behind it |
|---|---|---|---|
| `attested` | a purpose-built agent from the catalogue, git-attested | `schema` if `type: object`; `parameters` if it takes typed input | the catalogue entry's agent |
| `custom` | the package's own shape, served by the catalogue's generic structured agent and validated by the engine | `schema`, `type: object` | the generic agent + the engine's validation |
| `rendered` | no agent: the output is the rendered prompt's bytes (the v12 template kind) | `type: text`, `outputMacros: false` | the engine |
| `computed` | an engine operation over typed parameters; no prompt (the v12 check kind) | `parameters`, `type: object` with the result `schema` | the engine's published operation set |

Cross-checks on every format file: `type` and `producer` are from their vocabularies;
`description` is present and not blank; `schema` ⇔ `type: object`; `custom` and `computed` ⇒
`type: object`; `rendered` ⇒ `type: text`; `outputMacros: true` ⇒ `type: text`; `rendered`
and `computed` ⇒ no `outputMacros`; `values` ⇒ `type: enum`, and an enum takes its set from
`values` or from one parameter of kind `values` (at most one), never both; `parameters` ⇒
`attested` or `computed`, required on `computed`; a parameter name is an identifier, its
`format` only with kind `node`, kind `values` only on an enum format. A file that is not JSON,
or is missing from the package, is refused naming the format. **A package-local format is always
`custom`**; attested, rendered and computed formats come from the catalogue.

A parameter means one thing per producer: on a computed format it is an operand the engine
evaluates; on an attested format it is typed input the engine passes to the agent.

### The catalogue

The catalogue lives in the agents registry (`agents/formats.json`, one file per format under
`agents/formats/`), published per CalVer version. The index has two sections:

```jsonc
{
  "version": "vYYYY.MM.N",
  "formats": {
    "prose":          { "file": "formats/prose.json",          "agentName": "consult-prose",      "agentVersion": 3 },
    "classification": { "file": "formats/classification.json", "agentName": "classification",     "agentVersion": 1 },
    "concept_list":   { "file": "formats/concept_list.json",   "agentName": "concept-extraction", "agentVersion": 1 },
    "rendered":       { "file": "formats/rendered.json" },
    "terms_subset":   { "file": "formats/terms_subset.json",   "op": "terms_subset" }
  },
  "producers": {
    "custom": { "agentName": "custom-json", "agentVersion": 1, "trailer": "Answer with one JSON object conforming to this schema." }
  }
}
```

An attested entry names an agent (`agentName`, integer `agentVersion`), a computed entry an
`op` the engine publishes, a rendered entry neither; `custom` is a producer binding, never a
format entry. A catalogue id is snake_case (`^[a-z][a-z0-9_]*$`), as every declared id, and so
is a computed entry's `op` (`terms_subset`). An earlier catalogue (formats@v2026.10.1) published
a hyphenated spelling (`concept-list`, `terms-subset`); since formats@v2026.10.2 the engine reads
only the snake_case form. A package references a
catalogue format **by id only, never with a version**: publish resolves the id through the
engine's pinned index and stamps the file's canonical-JSON hash beside the catalogue version.

| Entry | Type | Producer | Output macros | Replaces |
|---|---|---|---|---|
| `prose` | text | attested | allowed | a node with no contract |
| `rendered` | text | rendered | no | `kind: template` |
| `classification` | enum | attested | no | `kind: classifier` — parameter `values` (kind `values`) carries the answer set |
| `concept_list` | object | attested | no | the `schemaRefs` entry |
| `terms_subset` | object `{ pass, uncovered[], untested[] }` | computed | no | `kind: check` — parameters `of`, `in` (nodes of format `concept_list`), `failWith` (text) |

### The manifest's `formats[]`

```jsonc
"formats": [ { "id": "medication_list", "file": "formats/medication_list.json" } ]
```

A package-local format: a snake_case id, declared once, never a catalogue id (catalogue ids
are reserved), a file in the package that reads as a format file and validates as
package-local (so: `producer: custom`, `type: object`, a `schema` in the strict
structured-output subset).

### The node

```jsonc
{ "id": "assessment", "label": "Assessment", "prompt": "assessment", "format": "prose",
  "failIfEmpty": "The assessment is empty.",
  "macros": [ { "id": "closing", "at": "after" } ] }

{ "id": "meds", "label": "Medications", "prompt": "meds", "format": "medication_list", "onInvalid": "fail" }

{ "id": "scope", "label": "Scope", "prompt": "scope", "format": "classification", "onInvalid": "fail",
  "with": { "values": [ "in_scope", "out_of_scope" ] } }

{ "id": "coverage", "label": "Coverage", "format": "terms_subset", "onInvalid": "fail",
  "with": { "of": "node.extract", "in": "node.source",
            "failWith": "The note names problems the source does not." } }

{ "id": "cover_letter", "label": "Cover letter", "prompt": "cover_letter", "format": "rendered" }

{ "id": "all", "label": "Everything", "aggregate": [ "node.assessment", "node.meds" ] }
```

- **`id`** — snake_case (`^[a-z][a-z0-9_]*$`), as every other declared id: a template reads a
  node as a Scriban member, and Scriban reads `node.identify-problem` as a subtraction. A
  hyphenated id is refused with the rename in the sentence; a duplicate id is refused.
- **`label`** — required, not blank (the record and the editor name the node by it).
- **`format`** — required on every node that does not aggregate; a catalogue id or a
  package-local id, anything else refused as neither. An **aggregator** (`aggregate`) is
  structural: no `format`, no `prompt`, no `with`, no `onInvalid`, and no `macros` (place them
  on the nodes it aggregates or on the deliverable); its sources are declared nodes, never
  itself.
- **`prompt`** — required unless the producer is `computed`, refused then; names a declared
  prompt, whose id is snake_case too (every declared id is; a hyphenated prompt id is refused
  with the rename in the sentence).
- **`with`** — exactly the parameters the format declares, every one supplied, none extra;
  `with` on a format that declares no parameters is refused. A `node` parameter is a bare
  `node.<id>` (it names the node, so it is an edge; `.content` / `.value` are refused there,
  and so is a bare id) naming a declared node whose format must match the declaration's
  `format` when one is named; a `text` parameter is a string literal or an `input.<id>`
  reference to a text input (an input of another type is refused naming its type); a `values`
  parameter is a list of snake_case values (at least two, distinct) or an `input.<id>`
  reference to an enum input. A string that is exactly an object reference is read as one; a
  reference to any other object is refused there; anything else is a literal.
- **`onInvalid`** — `fail` | `retry` | `flag`; required when the format's type is not `text`
  (the reply is validated against the format after parsing), refused when it is. What happens
  on an invalid reply is package-defined on the node, never on the format and never by the
  user at run time. `retry` re-sends once with the errors as a repair message — a later rung,
  the word reserved here.
- **`failIfEmpty`** — a **node** key at 25 (it was `output.failIfEmpty`; `output` is retired):
  a sentence, not blank, spoken when the reply is empty — a blank reply on a `text` format, an
  empty top-level array on an `array` format. Refused on a `rendered` or `computed` format,
  which has no reply to judge. The migration moves it up and drops it where the format no
  longer takes it.
- **`reproducible`** — the v11 claim, kept on `attested` and `custom` nodes; refused on a
  `rendered` or `computed` format, which is deterministic by construction (the ≤24 rule for a
  template or a check, in the format's words).
- `forEach`, `aggregate`, `when` (v18) — unchanged in meaning; `forEach` names
  `snippet.<folder>` or `input.<id>` (see *Derived edges* for what each must be), `aggregate`
  lists `node.<id>` sources (each declared, never the aggregator itself), and `when` is a
  Scriban boolean expression (see *Conditions and references*).

## Snippets

`manifest.data` becomes **`manifest.snippets`**: a snippet is a `.md` file that is a full
Scriban template, and a **folder** of snippets is a collection with an `index.json` listing
`id`, `name`, `file` and, optionally, `when` per item.

```jsonc
"snippets": { "standards": "snippets/standards.md", "sections": "snippets/sections/" }
```

- A snippet is used by **reading** it — `{{ snippet.standards.content }}`, or
  `{{ for s in snippet.sections }}{{ s.content }}{{ end }}` — from a prompt, another snippet, or
  a macro's text. It is never attached to a node or a deliverable: an inline read at the top
  of a template is the prompt-side "before" of v23, and a Scriban `if` around it is that
  attachment's condition, with the edge derived like any other.
- A folder item's **`when`** matters only inside a folder iteration and may read **inputs
  only**: the folder's effective size is resolved at job start, so a fan's item count stays
  the start-time scalar the scheduler, the progress total and the record's item rows depend
  on. A `when` on a snippet that is not in a folder, or one reading a node, is refused by a
  sentence saying the template's own `if` does that.
- A node fans over a folder as `forEach: snippet.<folder>` and over an array input as
  `forEach: input.<id>`; `item.content` is the item's rendered content (the ≤24 `item:content`, under the object spelling),
  `item.value` the array element typed as declared.
- Snippets may read snippets, inputs, nodes, `macro.<id>.content` and `macro.<id>.prompt` (the
  section-instructions pattern: a standard that carries an inline macro's prompt text). A snippet is
  a macro without an instruction; a snippet is only ever read, a macro may also be placed.
- A snippet id is snake_case; a snippet's file, a folder's `index.json` and every item's file
  must be in the package — each absence is refused naming the entry.

## Macros

The library (`manifest.macros[]`: `id` — snake_case, declared once — `label` — not blank —
`file` — in the package — **`instruction`** (mandatory), `optional`/`default`) is the only
kind of placed text. A macro's text is a Scriban template
that renders where it is used and may read snippets, inputs, node outputs and the run and
profile facts. It may also be **read** inline as `{{ macro.<id>.content }}`, prompt-side, exactly
as a snippet is. The instruction is a Scriban template too, rendered where `macro.<id>.prompt`
is read, over the same scope, with the same reads a snippet may make (a `.prompt` read inside
an instruction is a reference to that macro's instruction, see *The reference rule and cycles*).

### Instances

A macro is used in three ways, all on the output side:

```jsonc
// on a node — nodes[].macros[]
{ "id": "closing", "at": "after" }
{ "id": "tool_note", "at": "before", "when": "node.scope.value == \"in_scope\"", "forItem": "hpi" }

// on a deliverable — deliverables[].macros[]: document scope only
{ "id": "disclaimer", "at": "prepend", "when": "input.jurisdiction == \"on\"" }
{ "id": "signature", "at": "append" }
```

and **inline**, by writing `{{ macro.letrozole.prompt }}` in a prompt or a snippet where the
macro goes: that read *is* the inline macro's declaration — the model is told the instruction and asked
to write `{{ macro.letrozole.content }}` where the content belongs, and the reply renders it (see
*The reply is a template*). There is no `at: slot`, no `use` toggle and no instruction on an
instance (one instruction per macro; a different instruction is a different macro).

- **`at`** — `before` | `after` on a node, where it is optional and absent reads as `before`
  (the bare-id form of an instance, `"closing"`, is still accepted there and means the same);
  `prepend` | `append` on a deliverable, where it is **required** (a bare id is refused naming
  the two words). Any other word is refused.
- **`when`** — a Scriban boolean expression (see *Conditions and references*); `item.id` is
  readable at a fan, and compared only to an id the folder contains.
- **`forItem`** — an item of the snippet folder the node fans; refused on a node that fans no
  folder, and naming an item the folder does not contain. An instance naming a macro the
  library does not declare is refused.
- Only a node whose format has **`outputMacros: true`** may carry an instance or an inline
  `.prompt` read (directly, through a snippet it reads, or through at least one item of the
  folder it fans); anything else is refused by name. Items of a fanned folder that lack the
  read are named in a warning.
- Identity is (id, at, forItem) on a node and (id, at) on a deliverable; the same identity
  twice is refused. A library macro never placed and never read **from a template a run
  renders** — a node's prompt, the folder items it fans, a placed text, a condition, and what
  those reach — is refused as unused; what an unplaced macro's own instruction or text reads,
  or a snippet nothing reads, does not count (#1067).
- **Item reads follow the node.** A macro's text may read `item.<member>` only where it is
  composed on a node that fans — directly, through a snippet the text reads ("reaches
  `item.name` through snippet 'x'"), or as the fill of an inline macro whose `.prompt` the
  node's prompt reads. A **deliverable** instance composes no fan item: its text reading
  `item.<member>` is refused, and so is its text reading a fanned node (a deliverable macro
  reads scalar nodes and aggregators; place it on the node to read its items).
- A deliverable with `signature: true` whose placed text also reads `profile.signature` is
  refused, and so are two placed macros that both read it: a deliverable is signed once.

### Composition and the record

Before-blocks in list order, the rendered reply, then after-blocks. Inline macros have no
order: the model places the read, and the reply's render fills it. An instance whose `when`
refuses is withheld and the node row records the exclusion; a reply's `macro.<id>.content` read
is never withheld (the reply renders over the node's full scope). The output-side text becomes
part of the node's output: the record carries two per-node hashes (the agent's reply as it
came, and the composed output), and names each macro text the reply read, in order.

### The reference rule and cycles

Nothing on the reference path from a macro's text may reach a `macro.<id>.prompt` read: the
text is placed after a reply somewhere, and no model is asked anything there — and that holds
however else the text is read. That is the one transitive rule, checked over the derived
reference graph. A `macro.<id>.prompt` read is an edge to that macro's instruction, so an
instruction's own reads join the graph and the closure (what the instruction reads, the node
whose prompt reads the inline macro reads too). Cycles anywhere in that graph — snippet to snippet,
macro text to snippet to macro, instruction to macro text to the same inline macro — are refused by a
search that names the path.

### The mechanics sentence

`macro.<id>.prompt` renders as the macro's `instruction` — itself rendered, over the scope of
the template that reads it — followed by a sentence that is a **constant of this format
version**, appended after the render so the read it names reaches the model as written:

> If so, write `{{ macro.<id>.content }}` verbatim and nothing else at that place; do not write
> that content yourself — it is filled in afterward.

The instruction says *when and where*; this sentence names the read. An instruction that reads
its own `macro.<id>.content` is warned (#1067): the instruction renders, so that read puts the
macro's text in the prompt — right before the sentence telling the model not to write it.

### The reply is a template

A node's reply is rendered as a Scriban template at the node's completion, over the full
scope its prompt rendered over — its inputs, the nodes it reads, snippets and folders, the
fan item, every macro, the run and profile facts — and the rendered text is the node's
output (before its instances compose around it). A `{{ macro.<id>.content }}` the model wrote
where an inline macro's instruction told it to becomes the macro's text, rendered; any other read a
template could make renders the same way. What the reply may read is exactly what a template
may read: a reply that does not parse, or reads a member the scope has no value for (a node
the prompt does not read, an undeclared input), **fails the node** — the prompt or the agent
is at fault and the record says which sentence. Nothing in a reply is sanctioned, dropped or
rewritten; the reply is hashed as it came, before the render.

There is no `[[slot:<id>]]` at 25; the marker is the ≤24 grammar.

## Deliverables

The manifest's list of deliverables is **`deliverables[]`** (`results[]` and the one-entry
`result` are refused with the replacement). The validator's sentences that began "Result '…'"
begin "Deliverable '…'" at 25; the v5–v24 sentences do not move.

```jsonc
"deliverables": [
  { "id": "consult", "node": "node.all", "label": "Consultation note",
    "check": "node.coverage", "when": "input.kind == \"new\"",
    "macros": [ { "id": "disclaimer", "at": "prepend" } ], "signature": true }
]
```

- At least one deliverable; each with a snake_case `id`, declared once, and a `label` that is
  not blank.
- **`node`** — `node.<id>`, naming a declared aggregator (a node that does not aggregate is
  refused as such); each deliverable its own (two deliverables over one aggregator are refused).
- **`check`** — `node.<id>`, naming a declared node whose format producer is `computed`. Failed
  is a third state beside produced and skipped; a check nobody's deliverable names is refused.
- **`when`** — a Scriban boolean expression (see *Conditions and references*).
- **Every deliverable must transitively include a forEach source** — through its aggregator and
  what the aggregated nodes read: a deliverable with no fan has no consult. The sentence says
  where to add one.
- Every node must transitively reach a deliverable, except a node of an enum format read only
  by conditions and a node a check names; a node that reaches none is refused naming the
  deliverable's aggregator.

A `form` input (`expectedContent: form`) may be an input of type `object` with declared
`fields`: the response's keys fill the fields, each coerced to its type.

## Conditions and references

No manifest value spells a reference in the ≤24 binding grammar (`node:x`, `data:x`,
`input:x`, `item:x`); every reference is an object read in the template's own spelling, and
every declared id — input, node, prompt, format, snippet, macro, deliverable, field, enum
value — is snake_case.

- `forEach: snippet.<folder>` | `input.<id>`; `aggregate: ["node.<id>", …]` (each source
  declared, never the aggregator itself); `deliverables[].node: node.<id>`; `check: node.<id>`;
  `with` parameters as *The node* says. A colon spelling is refused by name with the object
  spelling in the sentence.
- A **`when`** — on a node, on a node instance, on a deliverable, on a deliverable instance,
  on a folder item — is **one Scriban boolean expression** over the objects a template reads:
  `node.scope.value == "in_scope"`, `input.kind == "new"`, `item.id == "hpi"` (at a fan),
  `(input.docs | array.size) > 0`, `input.seen < date.parse "2026-01-01"`, joined by `&&`,
  `||`, `!`, grouped by parentheses, with the comparisons `==` `!=` `<` `>` `<=` `>=` and the
  arithmetic operators `+ - * /`. Any other operator (`??`, `..`, a bitwise or shift) is
  refused naming it. A template (`{{ … }}`), more than one statement, or a blank is refused.
- **Its reads are edges**: the condition is walked by the template walker, so a node's own
  `when` and its instances' whens are the node's edges (a `when` reading the node it gates is
  a cycle), a deliverable's and its instances' are the deliverable's. A `when` may read
  anything a template reads; a folder item's reads inputs only (the folder's size is known at
  job start).
- **Typed**: an enum's value (`node.<id>.value` of an enum format, an enum input) is compared
  with `==`/`!=` to one of its declared values; `item.id` to one of the folder's item ids;
  ordering operators apply to numbers and dates (both sides alike); only a boolean — an input
  of type `boolean`, a comparison, a connective — is tested for truth (a bare text, enum,
  array or object is refused with what to write instead); arithmetic takes numbers (a date
  plus or minus a number is a date). The sentence names the operand as written
  (`compares node.scope.value to 'maybe', which it does not declare (values: …)`).
- The strict render probe evaluates every condition over the probe scope and refuses one that
  yields no boolean.
- The v10 grammar (`node:scope == in_scope`, `kind == new`, `count(x) > 0`) is refused at 25
  with the 25 spelling written out in the sentence — the migration's spelling (a text or enum
  input's literal is a string; a number, `true`/`false` and a date keep their type).

## Refused at 25

Each key keeps its frozen rules below 25; at 25 each is a sentence naming the key and the
replacement.

| Refused | Replaced by |
|---|---|
| `nodes[].bindings`, `prompts[].variables` | object references; reads and edges are derived |
| `prompts[].raw` | escaping |
| `manifest.preludes`, `prompts[].prelude` | an inline `{{ snippet.<id>.content }}` read (the editor migrated preludes at 23) |
| `manifest.data` | `manifest.snippets` |
| `manifest.schemas`, `schemaRefs`, `customSchemas`, `nodes[].output` | `manifest.formats` + `nodes[].format` |
| `nodes[].output.failIfEmpty` | `nodes[].failIfEmpty` (the same sentence, on the node) |
| `nodes[].kind`, `values`, `op`, `of`, `in`, `failWith` | the format and `with` |
| `deliverables[].macros[].before` / `after` / `forItem` | a node instance |
| `deliverables[].macros[].slot` | the inline `{{ macro.<id>.prompt }}` read |
| `[[slot:<id>]]` in any text | `{{ macro.<id>.prompt }}` where the macro is read inline; the model writes `{{ macro.<id>.content }}` |
| `results`, `result` | `deliverables` |
| a node id with a hyphen | the snake_case id |
| a prompt id with a hyphen | the snake_case id |
| `forEach: snippet:<folder>` / `input:<id>` / `data:<id>` | `snippet.<folder>` / `input.<id>` |
| `aggregate: ["node:<id>"]`, `deliverables[].node: node:<id>` | `node.<id>` |
| a `when` in the v10 grammar | a Scriban boolean expression (see *Conditions and references*) |
| `{{ns:id}}` placeholders in any text | object reads |

## Validation

The sentence conventions: a retired key reads "`<key>` is retired at specVersion 25;
<replacement>."; a required member reads "… must declare … at specVersion 25"; a template
refusal opens with the template ("Prompt 'x'", "Snippet 'x'", "Macro 'x'") and names the
member or the line; a format-file refusal opens with "Format 'x'". A package naming a
catalogue format on an engine without the catalogue is refused by one sentence naming the
ids, never silently.

Every sentence above is pinned by a vector under `conformance/v25/` (one case per refusal, the
outcome recorded from the reference validator), with the below-25 gates under `conformance/v24/`
(`invalid-…-at-v24`). A 25 case resolves its catalogue formats against
`conformance/format-catalog.json`, the fixture catalogue the suite ships beside
`catalog-schemas.json`. The JSON schema (`schemas/package-format-v25.schema.json`) catches the
retired keys, the id patterns, the object spellings of `forEach`, `aggregate`, `node` and
`check`, the enums and the required members; everything cross-field — a format's file, a
reference, a template's reads, a `when` — is the validator's and is listed `SHAPE_BLIND` in the
registry's own check.

## Migration (24 → 25; the editor's upgrade — mechanical, byte-identical in what the model sees)

| At 24 | At 25 |
|---|---|
| `{{ <variable> }}` bound to `input:x` / `node:x` (`as: r`) / `data:x` / `item:name` | `{{ input.x }}` / `{{ node.x.content \| r }}` / `{{ snippet.x.content }}` / `{{ item.name }}`; `bindings` and `variables` dropped |
| `item:content` / `{{ item:content }}` | `item.content` |
| `{{run:date}}`, `{{profile:signature}}` and the other fact tokens | `{{ run.date }}`, `{{ profile.signature }}` |
| no contract | `format: prose` |
| `kind: classifier` + `values` | `format: classification`, `with: { values }`, `onInvalid: fail` |
| `kind: template` | `format: rendered` |
| `kind: check` + `op/of/in/failWith` | `format: terms_subset`, `with: { of: node.x, in: node.y, failWith }`, `onInvalid: fail`; the deliverable's `check` rewritten to `node.x` |
| `schemaRefs: { s: concept-list }` + `output.schema: s` | `format: concept_list`, `onInvalid: fail` (the ≤24 contract id stays hyphenated; the 25 format id is snake_case) |
| `customSchemas` file | `formats/<id>.json` with the schema under `schema`, `producer: custom`; `onInvalid: fail` as the migration's explicit choice, named in the notice |
| `output.failIfEmpty` | `failIfEmpty` on the node; dropped where the node's format is `rendered` or `terms_subset` (no reply to judge) |
| `data` scalar / collection | a snippet / a snippet folder, files moved under `snippets/`; `forEach: data:x` → `snippet.x`, `forEach: input:x` → `input.x` |
| a prompt-side node macro (bare / `use: prompt`) | an inline `{{ macro.x.content }}` read at the top (`before`) or bottom (`after`) of the template, wrapped in `{{ if }}` when it had a `when`; a macro never placed on any output becomes a **snippet** and the read becomes `snippet.x.content` |
| an output-side node macro `at: slot` + `instruction` | the instruction moves to the library macro; the template keeps `{{ macro.x.prompt }}` |
| `[[slot:x]]` in a prompt, standard or prelude | `{{ macro.x.prompt }}` (the model is then told to write `{{ macro.x.content }}`) |
| a deliverable macro `before/after: node:x` (± `forItem`) | a node instance `{ id, at, forItem }` |
| `raw: true` prompt | the text with `{{` escaped |
| `results` / `result` | `deliverables`; the string form `result: "node:x"` becomes the one-entry list `[{ id: x, node: node.x, label: <x's label> }]` |
| a node id with a hyphen (`identify-problem`) | `identify_problem`, in the id and in every reference (`aggregate`, `check`, `when`, `with`, templates) |
| a prompt id with a hyphen (`draft-section`) | `draft_section`, in the id and every node's `prompt` |
| `aggregate: ["node:x"]`, `results[].node: node:x` | `["node.x"]`, `node.x` |
| `when: node:scope == in_scope and kind == new` — a node's own, a node instance's, a deliverable's, a deliverable instance's | `node.scope.value == "in_scope" && input.kind == "new"`: the Scriban expression, literals typed by the input (a text or enum input compares as a string); a `when` the v10 grammar refuses is a refusal naming the site |

A library macro placed on an output somewhere *and* used prompt-side elsewhere stays one
macro: the prompt-side use is a `.content` read. Nothing is split.
