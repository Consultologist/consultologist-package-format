# Workflow Package Format — specVersion 31 (a folder of typed files, compiled)

*specVersion 31 — preview. Published as part of `package-format@vYYYY.MM.N`; see `spec-versions.json`. 31 is listed under `preview` until the engine accepts it.*

Normative specification for `specVersion: 31` packages. 31 is a preview: it is listed under
`preview` in `spec-versions.json` until the engine's accepted versions include it, and a package at
31 is not yet accepted anywhere that accepts only the versions listed under `supported`. Unlike
versions 5 to 30, which refine one `manifest.json` version by version, 31 is a new package
format, and this document is **a full grammar**: it restates everything a package at 31 is, and
what the registry and the engine must do with it. A reader who has only this document and the
files named below can build a conforming implementation.

**One-line model.** Up to 30, a package is one `manifest.json` plus prompt files, read by an
engine that interprets each version's rules. At 31 a package is **a folder of small, typed
files** that the registry compiles at publish into **one checked document** (`resolve.json`) and
**the toolchain that checked it** (`lock.json`); the engine runs only that document, and every
job's record proves both.
- **Files:** nodes are files, flows are folders, and every member of every declaration is written
  (`null` means "deliberately none").
- **Types:** every node declares its `kind` (how it runs), its `format` (the shape it returns, in
  one JSON Schema dialect that Azure OpenAI's strict mode accepts) and its `producer` (what makes
  its output: `computed`, or `generated` by a model).
- **Lineage:** whether a value came from a model's output, or depends on a run fact, is worked
  out before any run, written on every node header and checked, and recorded on every row.
- **Decisions:** every condition and computed value is JSON Logic, written directly, checked
  against those types, and shown to people as ordinary text (`input.kind = "narrative"`).
- **Text:** every prompt, renderer, snippet, part, macro and deliverable is a template in one
  published Scriban dialect.
- **Verification:** checks live apart from production, can run per item, and gate deliverables;
  packages carry their own offline tests, and a failing test blocks publish.

## How to read this document

- **Every rule is a statement.** The words "must", "should" and "may" carry no special weight:
  where the text says what a package, a publisher or the engine does, that is the rule, and a
  package or an implementation that does otherwise does not conform.
- **Every refusal has its sentence.** A rule that a checker enforces is followed by the sentence
  the checker says, written between quotation marks and in italics. Sentences are used as
  written, character for character; chapter 11 lists every one with its audience.
- **`<…>` marks a placeholder** in a sentence, a path or a key: the checker fills it with the
  package's own text, an id, a path, a count or a limit, and never with patient text.
- **Fictional examples only.** Every example person and every clinical text in this document is
  invented.
- **Section numbers** are written `N.k.j`: chapter N, section k, subsection j. `§ 5.3` inside
  chapter 1 means section 1.5.3; from another chapter it is written "chapter 1 § 5.3". Chapters
  not yet linked are named in plain text.
- **`jsonc` blocks** are annotated JSON, for reading only; every file in a package is strict JSON
  (RFC 8259), with no comments.

### Files that are normative beside this text

These are published beside this document in the registry and are as binding as it is, where the
text names them:

- [`v31/bounds.json`](v31/bounds.json): `SourceBounds`, `FormatBounds`, the reserved ids;
- [`v31/constants.json`](v31/constants.json): the versions, kinds, features, producers, limits and
  Markdown extensions the text names;
- [`v31/profile.json`](v31/profile.json): the closed list of profile fields;
- [`v31/schemas/`](v31/schemas): one JSON Schema (2020-12) for every kind of file and every compiled
  document, each linked where this text defines the kind;
- [`v31/dialect.schema.json`](v31/dialect.schema.json): the meta-schema of the formats dialect;
- [`v31/formats/`](v31/formats): the built-in formats, one file each, with their index;
- [`v31/renderers/`](v31/renderers): the built-in renderers, with their index;
- [`v31/sentences.json`](v31/sentences.json): every refusal, warning and recorded sentence;
- `v31/scriban-dialect.md`: the template dialect, version 1.0.0 (written beside chapter 5).

[`v31/conformance/`](v31/conformance) holds hand-written examples of valid and invalid files for each
schema. They are examples, not goldens. `python3 scripts/check-v31.py` runs the registry's
checks over all of the above.

### The chapters

| Chapter | Covers |
|---|---|
| [1 Files and scopes](#1-files-and-scopes) | the folder layout, file kinds, every member required, ids, namespaces and qualified keys, `SourceBounds`, `FormatBounds` |
| [2 Types and inputs](#2-types-and-inputs) | `kind` and `format`, the dialect, text formats, format `$id`s, inputs, enum labels |
| 3 Expressions | JSON Logic: conditions, `computed`, every operation, null rules, `run.*`, the printer, the evaluator, `matches` and `has_word` |
| 4 Loops and functions | `for`, `while`, `until`, branches, `.items`, functions and `call` |
| 5 Templates and macros | the Scriban dialect, renderers, snippets, parts, macros, whitespace, run spots |
| 6 Checks, deliverables and the profile | checks and check loops, deliverables as files, gating, the profile |
| 7 The compiled documents | `resolve.json`, `lock.json`, evidence and views, in-package tests, the publish report |
| 8 The record | record storage 12 and the provenance contract |
| 9 The engine and the pages | loading and scheduling, the per-job ceiling, the satellites' contract, the pages |
| 10 Migration and tools | the migration from 30, the converter, byte-equivalence, the conformance suite |
| 11 Refusal sentences | every refusal, warning, job-start and History sentence, in one table |

## What changes from 30

| At 30 | At 31 | Chapter |
|---|---|---|
| one `manifest.json` with every node, plus prompt files | a folder: `nodes/<id>.md` (JSON header between `---` lines, then a Scriban body), a folder with `index.json` per flow, and nine top-level folders (nodes, checks, functions, renderers, snippets, macros, formats, deliverables, tests), **always present**, each with its `index.json` | 1 |
| optional members with implied defaults | every member written, `reproducible` included; `null` means deliberately none; a missing key is an error | 1 |
| node ids unique across the package | ids may repeat in disjoint scopes; every key is written with its root (`node.sections.paragraphs.draft_paragraph`, `check.…`, `deliverable.emr.note`) | 1 |
| `type` and output contracts, `prose`, `agent_*` formats | `kind`, `format` and `producer` on every node; formats are **pure shape** in a JSON Schema dialect (`plaintext`, `markdown_block`, `boolean`…); `producer` is `computed` or `generated` | 2 |
| `input.x` reads the value | inputs read like nodes: `input.x.value`, `input.x.content`, `input.x.title` (a `oneOf` label); a bare `input.x` is refused | 2 |
| a node's `when` gate | `if`; a `case` arm keeps `when` for its values, and every `case` is exhaustive | 1, 4 |
| object formats list some properties in `required` | every property in `required`, optional ones nullable; strict mode's other rules apply to a model's output | 2 |
| (none) | **model-derived**, **run-dependent** and, **profile-carrying** values, worked out before a run, written on every node header as `modelDerived`, `runDependent` and `profileCarrying` and checked against the derived values and recorded; the flags follow content only, never a condition | 2, 3 |
| string conditions parsed by the engine; `let` and operations with `op`/`with` | JSON Logic for every condition and every `computed` value, with typed custom operations; equality is `===`/`!==` only | 3 |
| `labelField` names an item | the loop's `itemLabel`; `label` is always the display name | 4 |
| (none) | functions: named, typed sub-flows called by a `call` node, their bodies run inline in the job's orchestration | 4 |
| renderers written in C# | renderers are Scriban templates: built-in ones in the registry, a package's own in `renderers/`; renderers may be chained | 5 |
| macro placements (`at: before/after/append`) | macros only inline in agent prompts; whether a macro is offered is a recorded decision | 5 |
| a check is a node | checks in `checks/` with their own root `check.x`; check loops; aggregate checks gate deliverables | 6 |
| deliverables declared in the manifest with `sources` | `deliverables/<id>.md` with a composition template; sources are what the template reads | 6 |
| `profile.name`, `profile.signature` | a closed, typed list of profile fields, read only in deliverables and macro bodies | 6 |
| the engine reads the manifest | the engine reads only `resolve.json`; `lock.json` pins the toolchain | 7 |
| (none) | `tests/<id>.json`, run offline at publish; a failing test blocks publish | 7 |
| record storage 11, in the job's Durable entity | record storage 12: keys with roots, check, renderer, macro, decision and call rows, `producer` and model-derived on every row, run facts and run spots; rows in a table, written once, and a canonical record blob at job end | 8 |
| Mermaid 11, default layout | Mermaid 12 with ELK; renderers, macros, functions and checks drawn | 9 |

Nothing about 30 is kept by reading 31 as a delta: a package at 30 becomes a package at 31 by the
migration (chapter 10), and the engine reads only what the migration and the registry produce.

## Libraries

The format is built on these libraries, each pinned as shown.

| Library | Use | Pin |
|---|---|---|
| Scriban | every template | locked, caret range from the registry (`lock.json`, chapter 7) |
| Markdig, with its advanced extensions | the Markdown formats | **exact** (it floats at `0.41.*` today) |
| `Corvus.Text.Json.JsonLogic` (Apache-2.0) | evaluating JSON Logic, with our custom operations and **our null rules overriding its defaults** | **exact**, behind our own interface |
| `Corvus.JsonSchema` (Apache-2.0) | validating values against formats; **our own checker** enforces the dialect | **exact**, behind our own interface |

Moving either Corvus library to json-everything later (paying its maintenance fee) is tracked in
[#1458](https://github.com/Consultologist/Consultologist-Blazor/issues/1458) and
[#1459](https://github.com/Consultologist/Consultologist-Blazor/issues/1459); the swap must leave
golden tests and a corpus re-render byte-identical.

## 1. Files and scopes

This chapter defines what a version 31 package is on disk: the folders and files, which file holds
what, the front matter, the rule that every member is written (`null` for none), ids and the
limits on them, namespaces and the keys the record uses, and the two sets of format constants,
`SourceBounds` and `FormatBounds`. What each kind of file's own members mean is defined in the
chapter that owns the kind; this chapter says where each file lives and which members every file
shares.

### 1.1 The model in one paragraph

A package is a folder. **A leaf is a file** (`<id>.md`): a JSON header between `---` lines, then a
body. **A flow node is a folder** (`<id>/`) described by its `index.json`. **The file or folder
name is the id.** **All nine top-level folders are always present, each with its `index.json`,**
and every folder lists its members, in order, exactly once; a file nobody lists is refused. Every
member of every declaration is written; `null` means "deliberately none" and a missing key is an
error. Ids may repeat only where neither node can see the other, and **every key is written with
its root**, its path of ids joined by `.` (`node.sections.paragraphs.draft_paragraph`,
`check.part_coverage.coverage`, `deliverable.emr.note`).

### 1.2 The folder layout

```
<package>/
  manifest.json            identity and inputs (§ 1.3)
  README.md                optional, documentation only (§ 1.2.3)
  dag.mmd                  derived view: committed for example packages, generated at publish (chapter 9)
  nodes/                   production
    index.json             the top level, in order
    <id>.md                a leaf: agent, rendered, computed or call
    <id>/                  a flow node: for, while, if or case
      index.json
      <child>.md | <child>/
  checks/                  verification, read as check.<id> (chapter 6)
    index.json
    <id>.md                a check (kind computed)
    <id>/index.json        a check loop
  functions/               named sub-flows (chapter 4)
    index.json
    <id>/
      index.json           inputs, uses, nodes, ret, format
      <child>.md | <child>/
      snippets/ macros/ formats/ renderers/     the function's own definitions, each with index.json
  renderers/               presentation templates (chapter 5)
    index.json
    <id>.md
  snippets/                prompt input text (chapter 5)
    index.json
    <id>.md
    <folder>/
      index.json
      <item>.md
  macros/                  verbatim output text (chapter 5)
    index.json
    <id>.md
    <folder>/
      index.json
      <item>.md
  formats/                 the package's own formats (chapter 2)
    index.json
    <id>.json
  deliverables/            composition templates, in delivery folders (chapter 6)
    index.json
    <id>.md
    <folder>/
      index.json
      <id>.md
  tests/                   offline tests (chapter 7)
    index.json
    <id>.json
```

- **All nine top-level folders are always present, each with its `index.json`,** even when empty
  (`"items": []`): `nodes/`, `checks/`, `functions/`, `renderers/`, `snippets/`, `macros/`,
  `formats/`, `deliverables/`, `tests/`. **Inside each function folder, `snippets/`, `macros/`,
  `formats/` and `renderers/` are always present too,** each with its `index.json`. An empty folder
  says, visibly, that the author defined nothing there.
- **The id lists live in the folders:** `nodes/index.json`, `macros/index.json` and
  `snippets/index.json` list the nodes, macros and snippets. The manifest keeps identity and inputs.

`resolve.json` and `lock.json` are **evidence**, written only at publish into the published
version's folder, never into any source. A copy found in an upload is ignored at import and at
publish.
`workflow.sw.json` is not part of 31: the export moved to Milestone 40 with [#1422](https://github.com/Consultologist/Consultologist-Blazor/issues/1422).

#### 1.2.1 Which file holds what

| File | Holds | Listed by | Members defined in |
|---|---|---|---|
| `manifest.json` | name, version, title, description, tags, inputs | — | § 1.3; inputs in [chapter 2](#28-inputs) |
| `<folder>/index.json` (the nine top-level folders and a function's four) | `description` and `items`, the folder's members in order | — | § 1.5.2; `deliverables/index.json` adds delivery settings (chapter 6) |
| `nodes/<id>.md` | an `agent`, `rendered`, `computed` or `call` node: header, then its prompt or template | `nodes/index.json`, or the enclosing flow node's `index.json` | `kind`, `format` in chapter 2; `computed` in chapter 3; `call` in chapter 4; an agent's prompt members (`parts`, `onInvalid`) in chapter 5 |
| `nodes/<id>/index.json` | a `for`, `while`, `if` or `case`: its members and its children | as above | chapter 4 |
| `checks/<id>.md`, `checks/<id>/index.json` | checks, check loops, aggregate checks | `checks/index.json`, or the check loop's `index.json` | chapter 6 |
| `functions/<id>/index.json` and its children | a function's signature (`inputs`, `uses`, `ret`, `format`) and body | `functions/index.json` | chapter 4 |
| `renderers/<id>.md` | a renderer: header (`input`, `format`), then its template | `renderers/index.json` | chapter 5 |
| `snippets/<id>.md` | a snippet: header, then its text | `snippets/index.json` | chapter 5 |
| `snippets/<folder>/index.json`, `<item>.md` | a typed folder: `items`, `format`; each item's header is its value, its body its content | `snippets/index.json`; the folder's `items` | § 1.5.3 here; reads in chapter 5 |
| `macros/<id>.md` | a macro: header (`if`, `instruction`, `format`), then its verbatim text | `macros/index.json` | chapter 5 |
| `macros/<folder>/index.json`, `<item>.md` | a macro folder: `items` and a shared `if` | `macros/index.json`; the folder's `items` | chapter 5 |
| `formats/<id>.json` | one of the package's own formats, as JSON Schema | `formats/index.json` | [chapter 2](#26-format-files-ids-and-references) |
| `deliverables/<id>.md`, `<folder>/index.json`, `<folder>/<id>.md` | delivery settings per folder; each deliverable's header and composition template | the folder's `index.json` | chapter 6 |
| `tests/<id>.json` | one offline test | `tests/index.json` | chapter 7 |
| `README.md` (any folder) | documentation | — | § 1.2.3 |
| `dag.mmd` (root only) | the derived Mermaid view | — | chapter 9 |

#### 1.2.2 Children: every member listed exactly once

- **A folder's children** are exactly: its `index.json`, the members its list names, and an
  optional `README.md`. A member is `<id>.md` (a leaf), `<id>.json` (in `formats/` and `tests/`),
  or `<id>/` (a folder). **Every child is listed exactly once.**
- **A stray file is refused,** with a sentence naming it.
  So is a listed member with no file, and a member listed twice.
- **Dot-files are stray files and are refused** (`.DS_Store`, `.gitkeep`): one rule, no exceptions.
- **One id, one child:** a folder may not hold both `<id>.md` and `<id>/`.
- **Lists name ids, never paths. Members are listed by bare id, with no trailing `/`:** `"standards"`,
  never `"standards/"`, since one id can't name both a file and a folder.
- **Order:** a list's order is meaningful: `nodes/index.json`'s `items` is the top level's order,
  a flow node's `nodes` its body's order, a snippet folder's `items` the order a loop or a join
  sees.
- **Inside a function folder,** the names `snippets`, `macros`, `formats` and `renderers` hold the
  function's own definitions.
  No node can take one of them, since they are reserved ids everywhere (§ 1.6).
- **Folder depth:** snippet and macro folders hold items only (one level). **Delivery
  folders are one level deep,** directly under `deliverables/`.
  Flow folders nest as deep as `FormatBounds` and `pathLength` allow (§ 1.7, § 1.8).

#### 1.2.3 Descriptions and READMEs

- **One `description` rule:** an array of strings joined with `"\n"`, or `null` for none; at most
  500 Unicode code points joined (as JSON Logic's `size` counts, chapter 3); `[]` is refused. It
  applies on every `index.json`, every header, every input, every function input and the manifest.
- **It is for people only:** the Editor, tooltips and the diagram show it, and it is **never sent
  to a model**.
- **`formats/index.json` follows the same rule:** it is a plain index, not a JSON Schema document
  ([chapter 2 § 6](#26-format-files-ids-and-references)). The JSON Schema
  `description` keyword *inside* a format file keeps JSON Schema's convention (a string, or
  omitted).
- **`README.md` is allowed in any folder.** It is documentation only: published with the package,
  but outside `resolve.json`'s compiled content, and never read by the engine. It is covered by
  `sourceHash` (chapter 7). Packages are public, so a README follows the fictional-examples-only rule,
  which the checker cannot verify.

#### 1.2.4 Encoding and line endings

- **Every file is UTF-8 with no byte-order mark.**
- **`\r\n` is normalised to `\n` at import and at publish,** so a checkout's line-ending setting
  never changes a body's bytes or its hash. **A lone `\r` is refused.** The publish report notes
  every file it normalised (chapter 7). Normalising to Windows `\r\n` instead is [#1465](https://github.com/Consultologist/Consultologist-Blazor/issues/1465)
  (Milestone 40).

### 1.3 The manifest

`manifest.json` is a plain JSON object, judged by [`v31/schemas/manifest.schema.json`](v31/schemas/manifest.schema.json).
Every member is present. **It holds identity and inputs only.**

| Member | Type | `null` allowed | Meaning |
|---|---|---|---|
| `name` | string | no | the package's name (`example-nested-note`, `test/general`) |
| `version` | string | no | `vYYYY.MM.N` |
| `specVersion` | integer | no | `31` |
| `derivedFrom` | string | yes | the `name@version` this package was copied from; `null` if none |
| `title` | string | yes | the display title; `null` shows the ref |
| `description` | array of strings | yes | lines, at most 500 code points joined (§ 1.2.3) |
| `tags` | array of strings | no | `[]` when none |
| `inputs` | object | no | the inputs, keyed by id, in Create page order ([chapter 2 § 8](#28-inputs)); `{}` when none |

**Gone from the manifest:**
- **`nodes`, `macros`, `snippets`:** `nodes/index.json`, `macros/index.json` and
  `snippets/index.json` list them (§ 1.2).
- **`formats`:** `formats/index.json` lists them.
- **`deliverables`**: `deliverables/` (chapter 6).
- **`templating`:** `lock.json` and `resolve.json`'s `requires` record the Scriban version
  (chapter 7), so a hand-written copy could only disagree.
- **`prompts`, `schemas`, `schemaRefs`, `customSchemas`, `preludes`, `data`, `result`:** members of
  earlier versions, not written at 31.
- **`requires` and `needs`** are derived at publish into `resolve.json`, never written (chapter 7).

**The manifest of `example-nested-note` at 31** (the description shortened here):

```json
{
  "name": "example-nested-note",
  "version": "v2026.12.1",
  "specVersion": 31,
  "derivedFrom": null,
  "title": "Nested note demo",
  "description": [
    "A demonstration of nesting: a node plans the note's sections, a loop outlines each",
    "section and drafts one paragraph per point, and a while redrafts the opening summary",
    "until a judge calls it good. Not intended for clinical use."
  ],
  "tags": ["demo", "nested"],
  "inputs": {
    "consult_draft": {
      "label": "Consult draft",
      "description": null,
      "format": "markdown_block",
      "required": true,
      "channel": null
    }
  }
}
```

`nodes/index.json`:

```json
{
  "description": null,
  "items": ["plan", "section_count", "sections", "refine"]
}
```

The loop is called `sections`, not `parts`, since `parts` is reserved (§ 1.6).
Its tree:

```
example-nested-note/
  manifest.json
  dag.mmd
  nodes/
    index.json              ["plan", "section_count", "sections", "refine"]
    plan.md                 agent, section_plan
    section_count.md        computed, number
    sections/               for, over the plan's sections
      index.json
      outline.md            agent, outline
      paragraphs/           for, over the outline's points
        index.json
        draft_paragraph.md  agent, plaintext
    refine/                 while, at most 3 passes
      index.json
      draft_summary.md      agent, plaintext
      judge.md              agent, verdict
  checks/
    index.json              "items": []
  functions/
    index.json              "items": []
  renderers/
    index.json              "items": []
  snippets/
    index.json              "items": []
  macros/
    index.json              "items": []
  formats/
    index.json              ["section_plan", "outline", "verdict"]
    section_plan.json  outline.json  verdict.json
  deliverables/
    index.json
    note.md                 deliverable.note
  tests/
    index.json
    migration_snapshot.json written by the migration (chapter 10)
```

`test/general` at 31:

```
test/general/
  manifest.json                  identity and inputs
  nodes/
    index.json                   ["extract_patient_concepts", "identify_problem",
                                  "create_typical_trajectory", "create_patient_trajectory",
                                  "prescribes_letrozole", "standards"]
    extract_patient_concepts.md  …  create_patient_trajectory.md
    prescribes_letrozole.md      agent, judgement: the macro's classifier (chapter 5)
    standards/                   for, over snippet.standards, itemLabel "title"
      index.json
      section_instructions.md  patient_section_draft.md  standard_section_draft.md
  checks/
    index.json                   "items": []
  functions/
    index.json                   "items": []
  snippets/
    index.json                   ["snomed_tool_guidance", "standards"]
    snomed_tool_guidance.md
    standards/
      index.json                 { "description": null, "items": ["hpi", "pmh", …], "format": "standard_section" }
      hpi.md  pmh.md  …  assessment_plan.md
  macros/
    index.json                   ["letrozole_prescription_text"]
    letrozole_prescription_text.md
  formats/
    index.json  standard_section.json
  renderers/                     package renderers only; the built-ins are the registry's (chapter 5)
    index.json                   "items": []
  deliverables/
    index.json  consult.md
  tests/
    index.json  migration_snapshot.json
```

(Which of its 30 constructs the migration rewrites into these files, the classifier node and the
`test` macro's move into the deliverable template among them, is
chapter 10. Its `standard_section` field keeps its name `title`: field
names have no reserved list ([chapter 2 § 5.3](#253-object-schemas-are-fully-typed-nested-text-references-a-text-format)).)

### 1.4 Front matter

Every `.md` file with a header (nodes, checks, renderers, snippets, folder items, macros,
deliverables) has the same shape:

```
---
{ "kind": "agent", "producer": "generated", "label": "Planning the sections", "description": null, "format": "section_plan", "modelDerived": true, "runDependent": false, "profileCarrying": false, … }
---
Plan the sections of a consultation note for the draft below. …
```

- **Line 1 is exactly `---`.** Then **one JSON object**, then a line of exactly `---`.
- **The body starts on the line after the closing `---`.** A blank line there is part of the body,
  and of the prompt's bytes. The Editor and the migration write none.
- **A file may end right after the closing `---`:** a header-only file.
- **A body that is only whitespace is empty.** A body with content is kept byte for byte, after
  line-ending normalisation (§ 1.2.4).
- **The header is strict JSON (RFC 8259), never YAML:** no duplicate keys, no comments, no trailing
  commas.
  The `jsonc` in this document is for annotation only.
- **Header and body stay separate:** the header is data (and JSON Logic, chapter 3); the body is
  Scriban (chapter 5).

**Bodies, per file:**

| File | Body |
|---|---|
| `agent` node | required: its prompt |
| `rendered` node, renderer, deliverable | required: its template |
| `computed` node, `call` node, check (`computed`) | must be empty: the expression and arguments are header members |
| snippet, snippet folder item, macro, macro folder item | required: the text |

`index.json`, `formats/*.json`, `tests/*.json` and `manifest.json` are plain JSON with no front
matter, held to the same strict JSON.

### 1.5 Members: every one written

**Every member of every declaration is required; `null` means "deliberately none"; a missing key
is an error.**

- **Empty values are values:** `""`, `[]` and `{}` are not "none".
- **Members that can never be "none"** are never `null`: an id, a `kind`, a `format`, a loop's
  `in`, `nodes` and `ret`, and a loop's or branch's `label`.
  The registry's schemas say which members are nullable.
- **It covers our own declarations:** the manifest, inputs, every header, every `index.json`,
  deliverables, `resolve.json` and `lock.json`.
- **It does not cover embedded standards:** JSON Schema keywords inside formats follow JSON
  Schema's convention (present where they apply, omitted otherwise, never `null`), and JSON Logic
  follows its own operator forms, canonicalised as chapter 3 defines.
- **An unknown member is refused at publish,** naming the file and the closest valid member
  (*"Did you mean 'label'?"*). Every declaration is closed, as the formats'
  `additionalProperties: false` is. The Editor and import offer to rename or remove it, shown to
  the author and never done silently. The migration never writes one.

#### 1.5.1 The members every header shares

| Member | Type | `null` | On |
|---|---|---|---|
| `kind` | string, one of the kinds ([chapter 2 § 1](#21-kind)) | no | every node and check header, every flow `index.json`, renderers (`rendered`), deliverables (`rendered`) |
| `label` | string, not empty or whitespace | no | every node, check, flow node, function, renderer, snippet, macro, deliverable and input. It is the display name everywhere |
| `description` | array of strings | yes | every `index.json`, every header, input and function input, and the manifest (§ 1.2.3) |
| `format` | a format name or an inline schema ([chapter 2 § 2](#22-format)) | no | every node, check, function, renderer, deliverable, snippet, macro and input; a snippet folder's `index.json` |
| `reproducible` | boolean | no | every node, checked against the derived value ([chapter 2 § 1.1](#211-reproducible)) |
| `producer` | string: `"generated"` or `"computed"` at 31 | no | every node and check, checked against its kind ([chapter 2 § 1.3](#213-producer)) |
| `modelDerived` | boolean | no | every node and check, checked against the derived value ([chapter 2 § 1.2](#212-the-contagious-flags-run-dependent-and-model-derived)) |
| `runDependent` | boolean | no | every node and check, checked against the derived value ([chapter 2 § 1.2](#212-the-contagious-flags-run-dependent-and-model-derived)) |
| `profileCarrying` | boolean | no | every node and check, checked against the derived value (chapter 3 § 4.6) |
| `if` | a JSON Logic condition (chapter 3) | yes: always | every production leaf (`agent`, `rendered`, `computed`, `call`), check, snippet, macro, macro folder and deliverable. A node's own condition is spelled `if`, replacing 30's `when`; a `case` branch keeps `when` for its values (chapter 4) |

- **`label` may not be empty or whitespace**.
  A loop's item naming is `itemLabel`, never `label`;
  `labelField` is gone.
- **Flow nodes write `format`,** and publish refuses one that differs from the format derived from
  the node's `ret` ([chapter 2 § 2.2](#222-which-formats-each-kind-may-return)).
- **`reproducible` is written on every node and checked against the derived value;** a mismatch is
  refused. Revisiting the member is [#1466](https://github.com/Consultologist/Consultologist-Blazor/issues/1466) (Milestone 40)
  (the rule is [chapter 2 § 1.1](#211-reproducible)).
- **`producer` is written on every node and checked against its kind,** like `reproducible`:
  `"generated"` for `kind: "agent"`, `"computed"` for every other kind. A mismatch, or a value
  reserved for Milestone 40 (`"grounded"`, `"extracted"`, `"attention"`), is refused
  (the rule is [chapter 2 § 1.3](#213-producer)).
- **`modelDerived`, `runDependent` and `profileCarrying` are written on every node and checked against the values the
  resolver derives,** like `reproducible` and `producer`: an agent node is always
  `modelDerived: true`, any node reading model output, directly or through other values, is
  `true`, and a node whose reads include `run.*` or a run-dependent value is
  `runDependent: true`. `profileCarrying` is written and checked the same way: `true` for an
  agent node whose prompt places a macro whose body reads `profile.*`, or a node reading such a
  value. A mismatch is refused. The flags are node members; formats stay pure shape
  (the rule is [chapter 2 § 1.2](#212-the-contagious-flags-run-dependent-and-model-derived)).

#### 1.5.2 The members by file

The table names each file's members; the owning chapter gives their types, null rules and sentences.
Each kind of file has a JSON Schema in [`v31/schemas/`](v31/schemas), applied to the file's JSON (a
leaf's header, an `index.json`, a plain JSON file). The members every schema shares are in
[`common.schema.json`](v31/schemas/common.schema.json).

| File | Schema |
|---|---|
| `manifest.json` | [`manifest`](v31/schemas/manifest.schema.json) |
| `index.json` of `nodes/`, `checks/`, `functions/`, `renderers/`, `snippets/`, `macros/`, `formats/`, `tests/` and a function's four definition folders | [`index`](v31/schemas/index.schema.json) |
| `deliverables/index.json`, a delivery folder's `index.json` | [`deliverables-index`](v31/schemas/deliverables-index.schema.json) |
| a snippet folder's `index.json` | [`snippet-folder-index`](v31/schemas/snippet-folder-index.schema.json) |
| a macro folder's `index.json` | [`macro-folder-index`](v31/schemas/macro-folder-index.schema.json) |
| a function's `index.json` | [`function-index`](v31/schemas/function-index.schema.json) |
| `agent`, `rendered`, `computed` and `call` node headers | [`node-agent`](v31/schemas/node-agent.schema.json), [`node-rendered`](v31/schemas/node-rendered.schema.json), [`node-computed`](v31/schemas/node-computed.schema.json), [`node-call`](v31/schemas/node-call.schema.json) |
| a `for`, `while`, `if` or `case` `index.json` | [`flow-for`](v31/schemas/flow-for.schema.json), [`flow-while`](v31/schemas/flow-while.schema.json), [`flow-if`](v31/schemas/flow-if.schema.json), [`flow-case`](v31/schemas/flow-case.schema.json) |
| a check header | [`check`](v31/schemas/check.schema.json) |
| a renderer header | [`renderer`](v31/schemas/renderer.schema.json) |
| a snippet header | [`snippet`](v31/schemas/snippet.schema.json) |
| a macro header | [`macro`](v31/schemas/macro.schema.json) |
| a deliverable header | [`deliverable`](v31/schemas/deliverable.schema.json) |
| a test file | [`test`](v31/schemas/test.schema.json) |

The schemas of the compiled documents and reports (`resolve`, `lock`, `publish-report`,
`migration-report`) are linked in chapters 7 and 10; the registry's own files have schemas too
(`bounds`, `constants`, `profile`, `sentences`).

| File | Members | Part |
|---|---|---|
| `agent` node | `kind`, `producer`, `label`, `description`, `format`, `reproducible`, `modelDerived`, `runDependent`, `profileCarrying`, `if`, and the prompt members (`onInvalid`, `parts`, `ordered`, `failIfEmpty`, …) | 05 |
| `rendered` node | `kind`, `producer`, `label`, `description`, `format`, `reproducible`, `modelDerived`, `runDependent`, `profileCarrying`, `if` | 05 |
| `computed` node, check | `kind`, `producer`, `label`, `description`, `format`, `reproducible`, `modelDerived`, `runDependent`, `profileCarrying`, `if`, `expression` | 03, 06 |
| `call` node | `kind`, `producer`, `label`, `description`, `reproducible`, `modelDerived`, `runDependent`, `profileCarrying`, `if`, `function`, `with`, `format` | 04 |
| `for` / `while` / `if` / `case` `index.json` | `kind`, `producer`, `label`, `description`, `format`, `reproducible`, `modelDerived`, `runDependent`, `profileCarrying`, the flow members, `nodes`, `ret` | 04 |
| function `index.json` | `label`, `description`, `inputs`, `uses`, `nodes`, `ret`, `format` | 04 |
| renderer | `kind`, `label`, `description`, `input`, `format` | 05 |
| snippet | `label`, `description`, `if`, `format` (a text format) | 05 |
| snippet folder `index.json` | `description`, `items`, `format` | § 1.5.3 |
| snippet folder item | its value: exactly the folder's format | § 1.5.3 |
| macro | `label`, `description`, `if`, `instruction`, `format` | 05 |
| macro folder `index.json` | `description`, `items`, `if` | 05 |
| deliverable | `kind`, `label`, `description`, `format`, `if`, `check`, `whenEmpty` | 06 |
| `deliverables/index.json`, delivery folder `index.json` | `description`, `items`, `delivery`, `bundle` | 06 |
| `nodes/`, `checks/`, `functions/`, `renderers/`, `snippets/`, `macros/`, `formats/`, `tests/` `index.json`, and a function's four | `description`, `items` | § 1.2 |
| test | `description`, `inputs`, `profile`, `run`, `outputs`, `expect` | 07 |

**Snippet headers are `label`, `description`, `if` and `format`,** with a text format.
Data types for snippets are [#1467](https://github.com/Consultologist/Consultologist-Blazor/issues/1467).

#### 1.5.3 Snippet folders are typed

A snippet folder's `index.json` declares the `format` its items' headers are checked against, and
carries no naming pointer: naming items is only a loop's business
business.

```json
{
  "description": [
    "The nine standard sections of a consult note, in order.",
    "Each item's header holds its title; its body holds the section's instructions."
  ],
  "items": ["hpi", "pmh", "medications", "allergies", "social_history",
            "family_history", "exam", "investigations", "assessment_plan"],
  "format": "standard_section"
}
```

```
---
{ "title": "History of Present Illness" }
---
Chronological prose narrative. …
```

- **The item's header is its value,** checked against the folder's `format` (an object format, so
  every field it declares is present). Its body is its content.
- **A header member called `label` has no special meaning** and an item
  has no `name`/`label`/id fallback.
- **A folder item has no `if`,** so a folder's size is its number of files. An item is gated by an
  `if` node in the body of the loop over the folder, as `example-conditional-sections` already
  does. Dynamic folder sizes are [#1468](https://github.com/Consultologist/Consultologist-Blazor/issues/1468).

### 1.6 Ids

An id names a file or folder, or a member of a keyed object.

- **The pattern:** `^[a-z][a-z0-9_]*$`. So ids are lowercase, with no case
  collisions, and contain neither `.`, `/` nor `:`.
- **At most 64 characters** (`SourceBounds.idLength`, § 1.7).
- **One id rule for every id:** nodes, checks, functions, renderers, snippets, snippet and macro
  folders and their items, macros, formats, deliverables, delivery folders, tests, inputs,
  function inputs and parts, including the ones that never become file names.
- **Windows names are refused:** `con`, `prn`, `aux`, `nul`, `com1`–`com9`, `lpt1`–`lpt9`. Windows
  reserves them with or without an extension.
- **Reserved words are refused anywhere, in singular and plural forms:** `input(s)`, `node(s)`,
  `check(s)`, `function(s)`, `test(s)`, `snippet(s)`, `macro(s)`, `part(s)`, `renderer(s)`,
  `format(s)`, `deliverable(s)`, `param(s)`, `item(s)`, `pass(es)`, `run(s)`, `profile(s)`,
  `value(s)`, `content(s)`.
  They are the roots and members a reference reads, so a node called `check`, `value` or `items`
  could never be named without ambiguity. The list is published beside `SourceBounds` (§ 1.7).
- **Object field names have no reserved list:** they follow the id pattern only. A field is always
  read after `.value` (`item.value.title`), never beside a member, and `.title` as a label applies
  only to an enumerated string, which has no fields. So a field may be called `title`
  ([chapter 2 § 5.3](#253-object-schemas-are-fully-typed-nested-text-references-a-text-format)).
- **`parts` and `part.<id>` keep their names:** `parts` is an agent node's header member and
  `part.` a root, neither of them an id (chapter 5).
- **The migration renames reserved ids,** reports every rename and rewrites every reference to it.
  In example packages each rename is hand-chosen: `example-nested-note`'s loop `parts` becomes
  `sections`. In account packages the kind is added as a suffix (`parts` → `parts_for`)
  (chapter 10).

### 1.7 `SourceBounds`

A spec-level object of limits on a package's source.

| Member | Value | Largest package when this was written |
|---|---|---|
| `files` | 512 files | 31 |
| `fileBytes` | 256 KiB (262,144 bytes) per file | 7 KB |
| `totalBytes` | 2 MiB (2,097,152 bytes) in all | 15.7 KB |
| `pathLength` | 200 characters, counted from the package root | — |
| `idLength` | 64 characters | — |
| `jsonDepth` | 32 levels of nesting in any JSON value (a file, a header, an inline schema) | — |
| `expressionNodes` | 1,000 nodes (operations, `var`s and literals) in one JSON Logic expression | — |

- **Published in the format-spec release as [`v31/bounds.json`](v31/bounds.json).** The library, the Editor, publish,
  import and CI all read them from there. **They are not deployment settings:** a package's
  validity is the same on every deployment, a package can't set them, and raising one is a spec
  change.
- **Publish and import each check every bound,** each with its own sentence.
- **No folder-depth bound:** the file model fixes where every file goes, so folder depth follows
  from nesting depth (capped by `FormatBounds.depth` for calls and by `pathLength` before parsing,
  since each folder level takes at least two characters).
- **What counts**:
  - `files` counts every file, `index.json` included (and so every empty folder's index);
  - `fileBytes` and `totalBytes` count bytes after line-ending normalisation (§ 1.2.4);
  - `pathLength` counts characters from the package root, with `/` separators and the extension
    (`nodes/sections/paragraphs/draft_paragraph.md` is 44).
- **Before counting**: ignored `resolve.json` and `lock.json` copies are dropped first;
  `totalBytes` is measured uncompressed; the bounds are checked before anything is parsed, in the
  order of the table, and every exceeded bound is reported.
- **`jsonDepth` and `expressionNodes` are checked before any other parsing**: the JSON
  reader stops at depth 32, and each expression's nodes are counted as it is read, before the
  file model, the types or the evaluator see it. A hostile or mistaken file can't exhaust the
  parser or the evaluator.
- **`bounds.json`'s shape** (schema: [`v31/schemas/bounds.schema.json`](v31/schemas/bounds.schema.json)):
  ```json
  {
    "specVersion": 31,
    "sourceBounds": { "files": 512, "fileBytes": 262144, "totalBytes": 2097152,
                      "pathLength": 200, "idLength": 64, "jsonDepth": 32,
                      "expressionNodes": 1000 },
    "formatBounds": { "passes": 15, "depth": 15, "parallel": 15 },
    "windowsReservedIds": ["con", "prn", "aux", "nul",
                           "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
                           "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"],
    "reservedIds": ["input", "inputs", "node", "nodes", "check", "checks", "function", "functions",
                    "test", "tests", "snippet", "snippets", "macro", "macros", "part", "parts",
                    "renderer", "renderers", "format", "formats", "deliverable", "deliverables",
                    "param", "params", "item", "items", "pass", "passes", "run", "runs",
                    "profile", "profiles", "value", "values", "content", "contents"]
  }
  ```

### 1.8 `FormatBounds`

Constants of the format, one member per kind of limit.

| Member | Value | Limits |
|---|---|---|
| `passes` | 15 | a `while`'s `max`: 1 to 15 |
| `depth` | 15 | nested function calls, measured by the checker: 0 to 15 |
| `parallel` | 15 | a loop's `maxParallel`: 2 to 15, or `null` |

- **Defined in the spec and the format library,** covered by the dialect version, and
  published in `bounds.json` (§ 1.7). **Never written in a package:** packages declare their own
  `max` and `maxParallel` within them.
- **Every member starts at 15** (`0xF`) and can be **raised alone** later, which is always
  compatible. Lowering one would break packages.
- **`maxParallel: null`** means "no cap of its own": the loop is limited only by the engine's
  per-job ceiling (chapter 9). `maxParallel: 1` stays refused,
  pointing to `parallel: false` (chapter 4). Requiring a non-null
  `maxParallel` is [#1474](https://github.com/Consultologist/Consultologist-Blazor/issues/1474) (Milestone 40).

### 1.9 Scopes and keys

#### 1.9.1 Roots and namespaces

Each kind of definition has its own namespace, named by its root:

| Namespace | Read as | Unique among |
|---|---|---|
| nodes | `node.<id>` | visible scope (§ 1.9.2) |
| checks | `check.<id>` | visible scope within `checks/` (§ 1.9.2) |
| functions | `"function": "<id>"` in a `call` | functions |
| inputs | `input.<id>.value`, `.content`, `.title` ([chapter 2 § 2.1](#221-reading-a-value)) | inputs |
| snippets | `snippet.<id>.content`, `snippet.<folder>.<item>` | snippets; items within their folder |
| macros | `macro.<id>`, `macro.<folder>.<item>` | macros; items within their folder |
| renderers | `renderer.<id>` | renderers |
| formats | a `format` name, a bare-id `$ref` | every owner together: a package format may not reuse a built-in or catalogue name ([chapter 2 § 6](#26-format-files-ids-and-references)) |
| deliverables | `deliverable.<path>` (§ 1.9.3) | their folder |
| tests | file names | tests |

- **A node and a check may share an id** (`node.coverage`, `check.coverage`), since their roots
  differ. So may a
  function and a node.
- **Deliverable ids are paths, like node ids:** `deliverables/emr/note.md` is
  `deliverable.emr.note`, and `deliverables/note.md` is `deliverable.note`. The destination is part
  of the id, so the same file name may repeat in different delivery folders, and moving a
  deliverable changes its key.
- **A package renderer may not reuse a built-in renderer's name.**
  Scoping between built-in, catalogue and package ids is [#1469](https://github.com/Consultologist/Consultologist-Blazor/issues/1469) (Milestone 40).

#### 1.9.2 Disjoint scopes: ids repeat only where neither can see the other

- **A node may read** its siblings, the nodes of the bodies that enclose it (aligned by path), and
  the top level. That is lexical scope, so **`node.x` resolves outward, with no new syntax**, and
  nothing is ever written `node.folder.x` in a reference.
- **An id may repeat only where the two nodes are never both visible from the same place.** Two
  sibling loops may each hold a `draft`. A body node may **not** reuse the id of a node its
  enclosing bodies, or the top level, make visible to it. So every `node.x` has exactly one
  candidate, and nothing is resolved by "nearest wins".
- **In terms of folders:** two nodes with the same id are refused when the folder of one encloses,
  or is, the folder of the other. Siblings can't share an id anyway, and the branches of an `if` or
  `case` sit flat in one folder, so they can't either.
- **Within one `while`, ids are unique at any depth,** since a pass (`pass.….node.<id>`) reaches
  into the `while` at any depth.
- **Functions are sealed scopes:** inside a function, ids are free, even repeating top-level ids or
  another function's, since nothing sees both. Within it these rules apply, with `node.x` resolving
  outward only up to the function's root.
  A function's own definitions may not shadow what it lists in `uses` (chapter 4).
- **Checks** follow the same rules within `checks/`.
- **Compatible:** a package whose ids are all unique is already valid, and its templates read the
  same.

#### 1.9.3 Keys

**A key is its root, then the ids of its enclosing flow nodes from the top level inward, then its
own id, joined by `.`.** Inside a function, the path goes through the **call node**, not the
function's name.
**Every key is written with its root** (`node.`, `check.`, `deliverable.`), in the record,
`resolve.json`, test files and History links.

| Where | Key |
|---|---|
| a top-level node | `node.plan` |
| inside two loops | `node.sections.paragraphs.draft_paragraph` |
| the same, one instance | `node.sections.paragraphs.draft_paragraph:2/1` |
| a renderer step in that instance | `node.sections.paragraphs.draft_paragraph:2/1/render:1` |
| a top-level call's inner node | `node.hpi_section.standard_draft` |
| a call inside a loop, item 3 | `node.standards.section.standard_draft:3` |
| a nested call | `node.hpi_section.refine_call.judge` |
| a check inside a check loop, item 2 | `check.part_coverage.coverage:2` (lines up with `node.sections:2`) |
| a deliverable in the `emr` folder | `deliverable.emr.note` |

- **`.` separates scopes;** `:` separates the key from the instance's item path; `/` separates the
  path's item ids. No id or item id contains any of them.
- **Sub-rows** extend an instance's key with `/`: `…/render:<n>`, `…/macro:<id>`, `…/spot:<n>` and
  `…/if:<site>`, for example
  `node.standards.assessment:7/if:macro.letrozole_prescription_text`
  (chapter 8). Item paths never contain `:`.
- **Mermaid ids replace `.` with `__`:** `node__sections__paragraphs__draft_paragraph`
  (chapter 9).
- **Keys are used everywhere at 31,** never only where an id repeats: one key form, no
  conditional.
- **Where a key replaces a bare id:**
  - **the record** (record storage 12): `nodeOutputs` keys, block ids, `skippedBlocks`, item-step and
    block events, item progress, collections, the concept source and the `nodes` rows (chapter 8);
  - **the engine:** scheduling keys, activity inputs, the derived edges and the walker's resolution
    (chapter 9);
  - **the pages:** Mermaid ids, the Editor's selection keys and links, the rail and History;
  - **`resolve.json` and test files** (chapter 7).
- **References inside a package** stay `node.x` and resolve outward (§ 1.9.2); the resolver writes
  each resolved reference as its key in `resolve.json` (chapter 7).
- **How pages show two nodes with the same id:** the Editor's tree places each under its folder
  (`sections › paragraphs › draft`); a pane shows `id draft · path node.sections.paragraphs.draft`;
  selection and links use the key; History and the rail show the label, with the path in a muted
  line where two rows share a label.

### 1.10 Refusals

Every sentence below is used as written; chapter 11 lists every sentence of this format.

**Scopes and bounds.**
- Duplicate in an overlapping scope:
  *"Node '<id>' in <path> reuses the id of node '<id>' <at the top level | in <other path>>, which <path> can read: rename one. Ids may repeat only where neither can see the other (for example in two sibling loops)."*
- `FormatBounds`:
  - *"While '<id>' declares max <n>; a while runs at most FormatBounds.passes (15) passes."*
  - *"Call '<id>' reaches depth <n>; calls nest at most FormatBounds.depth (15) deep."*
  - *"Loop '<id>' declares maxParallel <n>; the most is FormatBounds.parallel (15)."*

**Files and folders.**
- *"File '<path>' is not listed: every file in <folder> is named once in its index.json, or is index.json or README.md."*
- *"<folder> has no index.json; every folder lists its members, even when it has none (\"items\": [])."*
- *"The package has no <folder>/ folder; all nine top-level folders are always present."*
- *"<list> lists '<id>', but <folder> has no <id>.md or <id>/."*
- *"<list> lists '<id>' twice."*
- *"<list> lists '<id>/'; list a folder by its bare id."*
- *"<folder> holds both <id>.md and <id>/: an id names one file or one folder."*
- *"Delivery folder '<path>' is inside another delivery folder; delivery folders are one level deep."*
- *"File '<path>' starts with a byte-order mark; save it as UTF-8 without one."*
- *"File '<path>' contains a carriage return on line <n> that doesn't end the line; lines end with \n."*

**Front matter.**
- *"File '<path>' must start with a line of exactly ---, then one JSON object, then a line of exactly ---."*
- *"The header of '<path>' is not valid JSON: <parser message>."*
- *"The header of '<path>' declares '<member>' twice."*
- *"<Kind> '<id>' has an empty body; its <prompt | template | text> is the body."*
- *"<Kind> '<id>' has a body; a <computed node | call | check> keeps everything in its header."*

**Members.**
- *"<Declaration> is missing '<member>'; every member is written, and null means none."*
- *"<Declaration> sets '<member>' to null, which it can never be."*
- *"<Declaration> in '<path>' declares unknown member '<member>'. Did you mean '<closest>'?"*
- *"<Declaration> has an empty description; write null for none."*
- *"<Declaration>'s description is <n> characters; the most is 500."*
- *"<Declaration> has an empty label."*
- *"<Node> '<key>' declares reproducible <value>, but its <kind | body | function> makes it <derived>."*
- *"<Node> '<key>' is kind <kind> and declares producer '<value>'; a <kind> node's producer is <generated | computed>."*
- *"<Node> '<key>' declares <modelDerived | runDependent | profileCarrying> <value>, but its reads make it <derived>: <the read that does, or none>."*

**Ids.**
- *"'<id>' is not a valid id: a lowercase letter, then lowercase letters, digits or underscores."*
- *"Id '<id>' is <n> characters; the most is SourceBounds.idLength (64)."*
- *"Id '<id>' is reserved on Windows (con, prn, aux, nul, com1–com9, lpt1–lpt9) and can't name a file: rename it."*
- *"Id '<id>' is reserved: <root | member> '<word>' is read in references, so nothing may be called '<id>'."*
- *"Format '<id>' reuses the name of a <built-in | catalogue> format: rename it."*
- *"Renderer '<id>' reuses the name of a built-in renderer: rename it."*
- *"Node '<id>' appears twice inside while '<while>' (<path> and <path>): pass.….node.<id> must name one node."*

**`SourceBounds`.**
- *"The package has <n> files; the most is SourceBounds.files (512)."*
- *"File '<path>' is <n> KiB; the most is SourceBounds.fileBytes (256 KiB)."*
- *"The package is <n> MiB; the most is SourceBounds.totalBytes (2 MiB)."*
- *"Path '<path>' is <n> characters; the most is SourceBounds.pathLength (200), counted from the package root."*
- *"File '<path>' nests JSON more than 32 levels deep at <JSON pointer>; the most is SourceBounds.jsonDepth (32)."*
- *"<Site> in '<path>' has <n> expression nodes; the most is SourceBounds.expressionNodes (1,000)."*

## 2. Types and inputs

This chapter defines the type system of version 31: every node's `kind` (how it runs) and `format`
(what it returns), `reproducible` and the contagious flags, the JSON Schema dialect formats are
written in, the built-in, catalogue and package formats with their `$id` URNs, the split between
data and text, the annotations (`contentMediaType`, `x-markdown`), each node's `producer`, how a
model's output reaches its attested agent, the input grammar and how inputs are read, enum labels,
and per-run macro choices as optional boolean inputs. JSON Logic's typed operations are
chapter 3; where each kind's file lives is [chapter 1](#1-files-and-scopes).

### 2.1 Kind

**Every node declares its `kind`,** the mechanism that makes its value. Kinds are `agent`,
`rendered`, `computed`, `for`, `while`, `if`, `case` and `call`; `let` is not a kind.

| `kind` | Runs | File | Body | Defined in |
|---|---|---|---|---|
| `agent` | a model call, through the attested agent bound to its format (§ 2.7) | `<id>.md` | its prompt | chapter 5 |
| `rendered` | a template, no model | `<id>.md` | its template | chapter 5 |
| `computed` | one JSON Logic expression (member `expression`), no model | `<id>.md`, header only | empty | chapter 3 |
| `call` | a function, its body run inline in the caller's orchestration | `<id>.md`, header only | empty | chapter 4 |
| `for`, `while` | a body per item, or per pass | `<id>/index.json` | — | chapter 4 |
| `if`, `case` | one branch | `<id>/index.json` | — | chapter 4 |

**The folder gives the role, `kind` the mechanism**:
a check is `kind: computed` in `checks/`, a renderer and a deliverable are `kind: rendered` in
`renderers/` and `deliverables/`. `op` and `with` are retired: `terms_subset`, `all_pass` and
`count_pass` are operations called inside an expression (chapter 3).

**`kind: "agent"` says how a node runs; its `producer` says how its output can be verified**
(§ 2.1.3). The two are separate facts, and the kind keeps its name.

#### 2.1.1 Reproducible

**`reproducible` is written on every node and checked against the derived value;** a mismatch is
refused:

| Node | `reproducible` |
|---|---|
| `rendered`, `computed` | `true` |
| `agent` | `false` |
| a flow node (`for`, `while`, `if`, `case`) | `true` only if everything in its body that its result depends on is `true` |
| `call` | the function's `ret` value |

- **Run-dependence is recorded separately** and doesn't make a node `false`: a body reading
  `run.*` records a run-neutral hash beside the sent-text hash, on which runs are compared.
- Revisiting the member is [#1466](https://github.com/Consultologist/Consultologist-Blazor/issues/1466) (Milestone 40).

#### 2.1.2 The contagious flags: run-dependent and model-derived

Three flags spread through the graph: run-dependent, model-derived and profile-carrying. The resolver works out all three from `resolve.json`'s edges
before any run, records them on each row as `runDependent`, `modelDerived` and `profileCarrying`
(chapter 8), and History, the diagram and the Editor show them.
**Every node header also writes all three, `modelDerived: true | false`,
`runDependent: true | false` and `profileCarrying: true | false`, checked against the derived values** as `reproducible` and
`producer` are; a mismatch is refused. The flags are node members, never formats.

- **Run-dependent:** the value depends on a `run.*` fact, directly or through anything it is made
  from (chapter 3).
- **Model-derived:** the value came from a model's output somewhere upstream. It starts at the
  output of every node whose `producer` isn't `computed` (§ 2.1.3) and at an input element
  taken from a previous run's deliverable; typed text and uploaded documents start clean.
  It spreads through `computed` and `rendered` nodes, `call` results, flow nodes' `ret` and loop
  items. History shows it as, for example, *"computed from model text: node.draft"*.
- **Profile-carrying:** the value's text had a profile-reading macro substituted into it
  (chapter 3 § 4.6). It spreads the same way, is written on every node header as `profileCarrying` and checked,
  and is recorded on each row.
  A prompt, a part or a condition may not read a profile-carrying value; a deliverable may.
- **The flags describe content only**. They pass along what a value is made from, never
  through a condition: a node chosen by a model-derived `if` isn't model-derived for that. The
  decision has its own row.
- **Formats are shape, never the flags.** `trim` of a model's `plaintext` returns `plaintext`,
  the same format as its operand; its node's producer is `computed`, it stays model-derived, and
  it is `reproducible: true`. Model-derived is a flag on values, never a format.
- Requiring a model-derived or run-dependent value in a read is [#1478](https://github.com/Consultologist/Consultologist-Blazor/issues/1478) (Milestone 40).

#### 2.1.3 Producer

**Every node header writes `producer`,** how its output can be verified. Like `reproducible`, it
is checked against the node's kind, a mismatch is refused, and it is recorded on every row
(member `producer`, chapter 8):

| Node | `producer` at 31 |
|---|---|
| `agent` | `"generated"`: a model wrote it, so it may vary between runs |
| every other kind (`rendered`, `computed`, `call`, `for`, `while`, `if`, `case`), and every check | `"computed"`: no model at this node |

- **Reserved for Milestone 40** ([#1439](https://github.com/Consultologist/Consultologist-Blazor/issues/1439)), and refused at 31: `"grounded"` (model text verified
  against the input; [#1439](https://github.com/Consultologist/Consultologist-Blazor/issues/1439)'s narrowed `agent`), `"extracted"` (OCR and extraction; [#1438](https://github.com/Consultologist/Consultologist-Blazor/issues/1438)),
  `"attention"` (attention readings; [#1440](https://github.com/Consultologist/Consultologist-Blazor/issues/1440)), and a name for [#1440](https://github.com/Consultologist/Consultologist-Blazor/issues/1440)'s `adata`, to be settled there.
- **Formats are pure shape.** There is one `plaintext`, one `markdown_block`, one `boolean`, with
  no producer families and no prefixes; the producer is the node's, never the format's (§ 2.5.1).
- **The rules for a model's output apply to the output of a node whose `producer` isn't
  `computed`:** its format is always named (§ 2.2), its root is no `anyOf` and the engine's envelope
  supplies the top-level object (§ 2.3.3), the sent format is recorded (§ 2.3.5), and its agent is
  chosen by its format and producer (§ 2.7). "Every property in `required`, the optional ones
  nullable" applies to every format.
- **A `call` or flow node is `computed`** even when its body holds an agent node: the agent node is
  `generated`, and what spreads from it is the model-derived flag (§ 2.1.2).
- **Input elements have no `producer`.** They keep their `origin` (`typed`, `document`,
  `previous-run`, `transcript`). The engine always knows an element's origin and a node's
  producer, so `null` is never written for either.

### 2.2 Format

**Every `format` member is a format name or an inline schema** in the dialect (§ 2.3), for nodes and
inputs alike; an inline schema may `$ref` named formats.

```jsonc
"format": "plaintext"                                                 // a name
"format": { "type": "array", "items": { "$ref": "markdown_block" } }  // an inline schema
```

- **A name** is resolved package-local first, then catalogue, then built-in (§ 2.6.3).
- **An inline schema** is an anonymous format: one-off shapes (an input's object, a computed
  node's small object) need no file. Revisiting "name or inline" is [#1426](https://github.com/Consultologist/Consultologist-Blazor/issues/1426) (Milestone 40).
- **The output of a node whose `producer` isn't `computed` always has a named format,** never
  inline: it needs a binding (§ 2.7) and its hashes in the record, which a named file gives.
- **An inline schema carries no `contentMediaType` or `x-markdown`,** and one written is refused:
  text inside an inline schema is a `$ref` to a named text format (§ 2.5.3).

#### 2.2.1 Reading a value

**Nodes, inputs and snippets are read the same way:**

| Read | Gives | On |
|---|---|---|
| `.value` | the raw value (`"medical_oncology"`, `72`, an object) | every node and every input |
| `.content` | the text; an object's `.content` is its canonical JSON | text formats (`node.draft_summary.content`, `input.consult_draft.content`, `snippet.<id>.content`) |
| `.title` | the chosen `oneOf` arm's title (*"Medical oncology"*), at any depth (`item.value.kind.title`) | a labelled enum (§ 2.9); refused on a plain `enum` |

- **A bare `input.<id>` is refused,** as a bare `node.<id>` is. A condition reads
  `{ "var": "input.visit_type.value" }`; a template reads `{{ input.consult_draft.content }}`.
- **`const` and `title` live in the format;** the stored and recorded value is always the raw
  string.
- A node that didn't complete reads `null` for `.value` and `.content` (chapter 3).

#### 2.2.2 Which formats each kind may return

| `kind` | May return | Defined in |
|---|---|---|
| `agent` | a named format with a binding for it and the producer `generated` (§ 2.7): a registry or catalogue format (`plaintext`, `markdown_block`, `markdown_inline`, `judgement`, `concept_list`, `classification`, …), or a package's own object or array format through the custom-format agent; sent in strict mode (§ 2.3.3) | chapter 5 |
| `rendered` (node) | a text format: `plaintext`, `markdown_block`, `markdown_inline` | chapter 5 |
| `rendered` (renderer) | a text format; its `input` may be any format, written like a node's `format` | chapter 5 |
| `rendered` (deliverable) | `markdown_block`, `plaintext`, or an object format; never `markdown_inline` | chapter 6 |
| `computed` | any format, equal to what its expression returns, checked through each operation's typed return; `lower`, `trim` and the like return their operand's format unchanged | chapter 3 |
| `computed` (check) | `check_result` | chapter 6 |
| `call` | the function's `format` | chapter 4 |
| `for` | `list<T>`, where `T` is its `ret`'s format: `{ "type": "array", "items": T }` | chapter 4 |
| `while` | exactly its `ret`'s format (the last pass) | chapter 4 |
| `if`, `case` | the union of what its branches return; one format when every branch returns the same | chapter 4 |

- **A union** is `{ "anyOf": [ A, B ] }`. Each branch's `ret` must be a member, and every member
  must be returned by some branch. An untaken `if` with no `else` reads as skipped through
  `.skipped`, so it is not a union member.
- **The union is the result itself,** a top-level `anyOf` with no wrapper object: only the
  output of a node whose `producer` isn't `computed` is sent to a model (§ 2.3.3), and the condition's row in the record says
  which branch ran.
- **Reading a union:** `.content` always; `.value` only if every member has a value;
  `.value.<field>` only if every member declares that field compatibly.
- **Nested loops nest:** `list<list<plaintext>>`. A loop's value holds only the items that
  completed, in order; items that didn't run are absent, never `null`, and are seen with their
  state and reason through `.items` (chapter 4 § 2.5).
- **A macro's `format`** is `plaintext`, `markdown_block` or `markdown_inline`.
- **Flow nodes write `format`** in their `index.json`, and publish refuses one that differs from
  the derived format.

#### 2.2.3 Comparing formats: two equalities, two hashes

There are two comparisons, each with its own hash:

| Comparison | How | Used for | Hash |
|---|---|---|---|
| **type equality** | references compared by name (never dereferenced), `anyOf` members and `properties` sorted by name, annotations (`title`, `description`) dropped | type checks: a written `format` against the derived one (a flow node's, a `computed` node's), `with` against a function's parameters, branch results against each other, a piped value against a renderer's `input` | `typeHash` |
| **full equality** | everything dereferenced, every keyword kept | hashes, and what a model receives | `formatHash` |

- **`formatHash` leaves out `$id`**, so the same shape published under two ids hashes
  the same.
- **A built-in format's name equals its schema** under type equality: `date` and
  `{ "type": "string", "format": "date" }` are one type.
- **`integer` is a kind of `number`**: an `integer` value fits where a `number` is
  expected, not the reverse. Numbers are IEEE doubles; chapter 3 § 7 gives the rules.
- **The record carries both hashes for each format** (`typeHash`, `formatHash`), so a change of
  wording (a `description`, which is what the model is told) is told apart from a change of shape (chapter 8).
- **A text format fits where `string` is expected:** annotated strings are compatible with
  `string`; the annotations drive warnings and conversion, never type errors.
  The reverse does not hold, and the typed operations still treat text as text (chapter 3).

#### 2.2.4 Display: type strings

People see formats as **type strings**, printed from the schema; pickers write the schema.

| In the file | Displayed |
|---|---|
| `"plaintext"` or `{ "$ref": "plaintext" }` | `plaintext` |
| `{ "type": "number" }` | `number` |
| `{ "type": "array", "items": { "$ref": "plaintext" } }` | `list<plaintext>` |
| `{ "type": "array", "items": { "type": "array", "items": … } }` | `list<list<…>>` |
| `{ "anyOf": [ { "$ref": "plaintext" }, { "$ref": "classification" } ] }` | `plaintext \| classification` |
| `{ "type": ["string", "null"] }`, `{ "anyOf": [ { "$ref": "x" }, { "type": "null" } ] }` | `string \| null`, `x \| null` |
| an inline object | `{ title: string, notes: plaintext \| null }` |
| an `enum`, or a labelled `oneOf` | `string {narrative, table, omit}` |

The Editor's picker also says what a format is, for example "plain text";
who wrote it ("written by a model") is the node's `producer`, shown beside it (§ 2.1.3).

### 2.3 The dialect

Formats are written in **one JSON Schema 2020-12 dialect that matches Azure OpenAI's strict
structured outputs**, so the format of every node whose `producer` isn't `computed` can be sent
in strict mode.
The format publishes the dialect's 2020-12 meta-schema ([`v31/dialect.schema.json`](v31/dialect.schema.json)), so any 2020-12 tool can check a package's
formats. **The dialect's id is `urn:consultologist:spec:31:dialect`.**

#### 2.3.1 The keywords

| Keyword | Allowed | Rule |
|---|---|---|
| `$schema` | **required** at the root of every format file | the dialect's id, `urn:consultologist:spec:31:dialect`; a mismatch with `specVersion` is refused |
| `type` | anywhere | `string`, `number`, `integer`, `boolean`, `object`, `array` or `null`; or an array of exactly one of those plus `"null"` (§ 2.3.2) |
| `properties`, `required` | on an object | `required` lists **every** declared property, and nothing else (§ 2.3.3) |
| `additionalProperties` | on every object | must be `false` |
| `items` | on an array | one schema |
| `enum` | on a string | the plain enum (§ 2.9) |
| `oneOf`, `const` | on a string, only in the labelled-enum form (§ 2.9) | every branch is exactly `{ "const": …, "title": … }` |
| `anyOf` | unions and nullable references | not at the root of a format sent to a model (§ 2.3.3) |
| `$ref` | anywhere | a bare format id, or `#/$defs/<name>` within the file (§ 2.6.3); beside it, only `title` and `description` |
| `$defs` | at a format file's root | sub-definitions used inside the file |
| `$id` | at a published format's root | the format's URN (§ 2.6.2) |
| `title`, `description` | anywhere | annotations: `title` for people, `description` for people and the model (§ 2.5.1) |
| `format` | only `"date"`, only beside `"type": "string"` | the built-in `date` (§ 2.4) |
| `contentMediaType` | at a text format's root | `text/plain` or `text/markdown` (§ 2.5) |
| `x-markdown` | as § 2.5 says | our annotation |

**A keyword outside the dialect is refused** at publish, with a sentence. The rest of JSON Schema
(`pattern`, `allOf`, `if`/`then`, the length and count bounds, `patternProperties`, …) is not
adopted.

- **`$schema` is written in every format file** (the registry's, the catalogue's and a package's),
  so any 2020-12 tool finds the dialect, and publish refuses one whose dialect isn't the
  `specVersion`'s. An inline schema is part of its file and carries none.
- **Recursive formats are refused** (a `$ref` that reaches its own definition): the comparisons
  (§ 2.2.3) and the printer (§ 2.2.4) are defined for finite shapes.
- **Strict mode's size limits** (the property count and the nesting depth Azure OpenAI
  documents) are checked at publish at 31, on every format sent to a model.

#### 2.3.2 One way to write "nullable"

- **Scalars:** a type array, `"type": ["string", "null"]`.
- **References and objects:** `"anyOf": [ { "$ref": "…" }, { "type": "null" } ]`, the only way to
  make a reference nullable.
- **Enums**: a nullable plain enum lists `null` among its values as well,
  `"type": ["string", "null"], "enum": ["new_patient", "follow_up", null]`; a nullable labelled
  enum gains a `{ "const": null }` arm in its `oneOf`, with no `title`. The `null` value and arm
  don't count towards § 2.9's two values.
- **Refused:** an `anyOf` with a `null` branch around a plain scalar, and a type array holding
  anything other than one type plus `"null"`.

#### 2.3.3 `required`, `additionalProperties` and the root

Strict mode requires every property in `required`, `additionalProperties: false` on every object,
and an object, not an `anyOf`, at the root:
- **in every format,** whoever produces the value: every property of every object is listed in
  `required`, and an optional property has a nullable type (§ 2.3.2), for example
  `"type": ["integer", "null"]`. Every value then carries every key, with `null` when there is
  none, as every declaration does. A format whose object leaves a property out of
  `required` is refused (Refusals);
- **in every format:** `additionalProperties: false` on every object;
- **in the format of a node whose `producer` isn't `computed` only** (sent to a model): the root
  is not an `anyOf`. Its root
  need not be an object: the engine's envelope supplies the top-level object strict mode needs
  when it sends the format (§ 2.3.5);
- **in every other format** (an input's, a computed value's, a flow node's): the root may be a
  string, a list or an `anyOf`. An `if` or `case` whose branches return different formats keeps
  the `anyOf` as its result, with no wrapper (§ 2.2.2).

#### 2.3.4 Validating values

- **Values are validated with Corvus.JsonSchema** (Apache-2.0): inputs, model outputs and format
  examples. **Our own checker enforces the dialect's restrictions,** since Corvus can neither refuse
  keywords outside a dialect nor register our annotations.
- Corvus sits behind our own interface, pinned exactly, and listed in `lock.json`. Moving to
  JsonSchema.Net later is [#1459](https://github.com/Consultologist/Consultologist-Blazor/issues/1459).
- **A reply is validated against the full format,** including what was not sent (§ 2.3.5).
- **`format: "date"` is validated as an assertion** when a reply is checked against its full
  format: a string `YYYY-MM-DD` naming a real calendar date, so `2026-02-30` is refused.

#### 2.3.5 What a model receives

When a node whose `producer` isn't `computed` sends its format to the model provider, the engine
prepares a copy;
`resolve.json` keeps the original:
1. each `description` is **kept:** it is the instruction to the model, at the top of the format
   and on each property, and strict mode accepts it; a field `$ref`ing a text format sends that
   text format's `description` first, then its own;
2. every `x-` annotation and `contentMediaType` is stripped;
3. a referenced text format resolves to `{ "type": "string" }`;
4. a labelled enum (`oneOf` of `const`/`title`) becomes a plain `enum` of the `const`s;
5. `title`, `$id` and **the keywords strict mode rejects** (such as `format: "date"`) are removed.
   **The list of rejected keywords comes from the attested agent definition,** not from the
   format, so a provider that accepts more is a new agent version, not a format change;
6. the result is sent inside the engine's envelope, which supplies the top-level object strict
   mode requires, so a text or list format can be sent too.

**The sent format is recorded:** the row holds `formatHash` (the full format), `sentFormatHash`
(what the model received) and the removed keywords as JSON pointers
(chapter 8). History shows them as *"Not sent to the model: …"*. The reply is still
validated against the full format (§ 2.3.4).

### 2.4 Built-in and catalogue formats

| Owner | Formats | Where |
|---|---|---|
| **The package-format registry** (`consultologist-package-format`), versioned with the spec | data: `string`, `number`, `boolean`, `date`; text: `plaintext`, `markdown_block`, `markdown_inline`; objects: `check_result`, `judgement` | `formats/index.json` + `formats/<id>.json` beside the dialect's meta-schema |
| **The formats catalogue** (`consultologist-agents`) | object formats: `concept_list`, `classification`, … | `agents/formats/index.json` + `<id>.json` |
| **A package** | its own object and array formats | `formats/index.json` + `formats/<id>.json` |

- **Formats are pure shape,** with no producer families and no prefixes: a model's plain text and a
  template's plain text are both `plaintext`, and a yes or no is `boolean` wherever it sits (an
  input, a computed value, a `judgement`'s `answer`). Who produced a
  value is its node's `producer` (§ 2.1.3).
- **`rendered` and `terms_subset` stop being formats:** they are `kind: rendered` and an operation
  returning `check_result`.
- **`date`** is `{ "type": "string", "format": "date" }` (with its `$schema` and `$id`), so
  `"format": "date"` works.
- **A classifier returns `judgement`,** the built-in `{ answer: boolean, reason: plaintext }`,
  with every property required and `reason` never `null`. A macro's `if` reads
  `node.<id>.value.answer`, and the record and History show the reason beside the answer. The catalogue's `classification` is `{ value: string }`.
- **`check_result`**'s members are chapter 6.
- **`titled_section`** is not a built-in at 31; a package declares it in
  `formats/`. Adding a built-in later is compatible.
- **Packages define only object and array formats.** Scalar data and text formats come from the
  registry and the catalogue: a package references `markdown_block` or `plaintext` rather than
  declaring its own text format, since text a model writes needs a catalogue binding (§ 2.7).

`formats/markdown_block.json` in the registry ([`v31/formats/markdown_block.json`](v31/formats/markdown_block.json)):

```json
{
  "$schema": "urn:consultologist:spec:31:dialect",
  "$id": "urn:consultologist:spec:31:format:markdown_block",
  "type": "string",
  "contentMediaType": "text/markdown",
  "x-markdown": "block",
  "description": "Markdown text that stands on its own lines (a paragraph, a list or a table)."
}
```

`formats/judgement.json` in the registry ([`v31/formats/judgement.json`](v31/formats/judgement.json); descriptions illustrative):

```json
{
  "$schema": "urn:consultologist:spec:31:dialect",
  "$id": "urn:consultologist:spec:31:format:judgement",
  "type": "object",
  "description": "A yes-or-no answer to the question asked, with the reason for it.",
  "required": ["answer", "reason"],
  "additionalProperties": false,
  "properties": {
    "answer": { "type": "boolean", "description": "true for yes, false for no." },
    "reason": { "$ref": "plaintext", "description": "Why, in a sentence or two, from the text given." }
  }
}
```

### 2.5 Data and text

**`string` is data:** a value, not content (an id, a code, an enum value, a label). **Text formats
are content** meant to be read or composed, and always carry a media type.

| Format | Is | `contentMediaType` | `x-markdown` |
|---|---|---|---|
| `string`, `number`, `boolean`, `date` | data | omitted | omitted |
| `plaintext` | text | `text/plain` | omitted |
| `markdown_block` | text | `text/markdown` | `block` |
| `markdown_inline` | text | `text/markdown` | `inline` |
| object formats | structured data | omitted | omitted |

Each is the same format whether a model or a template wrote the value (§ 2.1.3). A `block` Markdown text stands on its own lines; an `inline` one sits inside a
line.

#### 2.5.1 The annotations

They follow JSON Schema's convention: **present where they apply, omitted otherwise, never `null`.**
The checker refuses one missing where it applies, and one present where it doesn't.

| Annotation | Where | Meaning |
|---|---|---|
| `contentMediaType` | at the root of every text format | the text's media type |
| `x-markdown` | at the root of every Markdown format | `block` or `inline` |
| `description` | anywhere | what the value **is** and what the model should write: sent to the model (strict mode accepts it, § 2.3.5) and shown in the Editor, the checker's sentences and the docs |

- **A format file is plain JSON Schema plus our layout annotations** (`contentMediaType`,
  `x-markdown`), with no producer annotation or prefix: the producer is the node's (§ 2.1.3).
- **A format's instructions to the model are standard JSON Schema `description` keywords,** at the
  top of the format and on each property, in the catalogue and in packages alike. Bindings hold no instructions (§ 2.7).
- **Our annotations sit at the top of each format,** the format as a return type, not on every
  nested field.
- **`title` and `description` are part of the format,** so changing either changes its `formatHash` (not its
  `typeHash`, § 2.2.3): type equality ignores them, and full equality includes them, since a
  `description` changes what the model is told.

#### 2.5.2 Markdown means Markdig's advanced extensions

`markdown_block` and `markdown_inline` mean **Markdig with `UseAdvancedExtensions`** (pipe and grid
tables, footnotes, task lists, emphasis extras, auto-links and the rest of that set). The spec lists
the extensions by name as of the pinned Markdig version; Markdig is pinned **exactly** and listed in
`lock.json`.
Escaping plain text into Markdown, `plain()` and composing to HTML or PDF are defined against that
list. Flavours (CommonMark, GFM) are [#1451](https://github.com/Consultologist/Consultologist-Blazor/issues/1451).

#### 2.5.3 Object schemas are fully typed; nested text references a text format

Every nested field has its complete type, a `required` list naming every property (§ 2.3.3) and
`additionalProperties: false`,
defined inline or by `$ref` to a definition. **A nested field is data unless it references a text
format**.
A field that is text meant to be read or composed is written `{ "$ref": "plaintext" }`, which gives
it its media type, so the typed operations, escaping and plain-text conversion treat it as text.

**Field names follow the id pattern** of chapter 1 § 6, **with no reserved names**. A field never sits at the same level as a member: it is always read after
`.value` (`item.value.title`), and `.title` as a label applies only to an enumerated string, which
has no fields. So a field may be called `title`, `label` or `value`; ids keep their reserved list.

`example-nested-note`'s `formats/verdict.json` at 31:

```json
{
  "$schema": "urn:consultologist:spec:31:dialect",
  "type": "object",
  "description": "A judgement of a draft summary: good, or revise with what to change.",
  "required": ["verdict", "feedback"],
  "additionalProperties": false,
  "properties": {
    "verdict":  { "type": "string", "enum": ["good", "revise"] },
    "feedback": { "$ref": "plaintext" }
  }
}
```

### 2.6 Format files, ids and references

#### 2.6.1 `formats/index.json` and one file per format

**Every owner** (the registry, the catalogue, a package) writes its formats as
`formats/<id>.json`, one format per file, listed by **`formats/index.json`, a plain index** ([`index.schema.json`](v31/schemas/index.schema.json)) like
every other `index.json`: `description` (lines or `null`) and `items`:

```json
{
  "description": null,
  "items": ["section_plan", "outline", "verdict"]
}
```

- **The file name is the id;** `items` lists every file in the folder exactly once, in order
  (chapter 1 § 2.2).
- **Types only:** no agent names, versions or producers; bindings live apart (§ 2.7). The
  instructions to the model are the format's own `description`s (§ 2.5.1).
- **A format file is a JSON Schema in the dialect,** with no wrapper: the schema is the file, starting with
  its `$schema` (§ 2.3.1).
- **A function's own formats** sit in `functions/<id>/formats/`, shaped the same (chapter 4).

#### 2.6.2 `$id`s are URNs

Every published format has a `$id`, a URN that doesn't depend on where anything is hosted:

| Owner | `$id` | Example |
|---|---|---|
| the formats catalogue | `urn:consultologist:format:<name>@<catalogue-version>` | `urn:consultologist:format:concept_list@v2026.12.1` |
| a package | `urn:consultologist:package:<package>@<version>:format:<id>` | `urn:consultologist:package:example-nested-note@v2026.12.1:format:verdict` |
| the registry's built-ins | `urn:consultologist:spec:<specVersion>:format:<name>` | `urn:consultologist:spec:31:format:markdown_block` |

- **A package format's `$id` is derived at publish** from the package's name and version, **never
  written in source**; a `$id` found there is refused, since it would have to be rewritten at
  every version.
- A package name may hold `/` (`test/general`), which a URN's specific string allows.
- Within a format, `$id` follows JSON Schema's own rules.

#### 2.6.3 References by bare id; no shadowing

- **In source, a format is named by its bare id:** `"format": "plaintext"`,
  `{ "$ref": "plaintext" }`. The resolver looks it up **package-local first, then catalogue,
  then built-in**, and rewrites it to `#/$defs/<id>` in `resolve.json`'s single inline bundle.
- **No shadowing:** a package format may not reuse a catalogue or built-in name. So the lookup order never changes which format a name means.
- **Inside a format file,** `#/$defs/<name>` refers to that file's own `$defs`.
- **In a function,** a name resolves to the function's own formats, then the package formats its
  `uses` lists, then catalogue and built-in; built-in and catalogue formats need no listing.
- **`resolve.json`** holds exactly the formats the package uses, each inline with its origin, its
  `$id` and its hashes (chapter 7).

### 2.7 Agent bindings

**What a value is and who produces it are two facts in two files**:

| File | Holds |
|---|---|
| `formats/index.json` and the format files (every owner) | types only |
| `agents/bindings.json` (the agents catalogue) | which attested agent serves which format for which producer, and the custom-format agent; no instructions |

```json
{
  "version": "v2026.12.1",
  "formats": {
    "plaintext": {
      "generated": { "agentName": "consult-prose", "agentVersion": 4 }
    },
    "markdown_block": {
      "generated": { "agentName": "consult-prose", "agentVersion": 4 }
    },
    "judgement": {
      "generated": { "agentName": "classification", "agentVersion": 1 }
    },
    "concept_list": {
      "generated": { "agentName": "concept-extraction", "agentVersion": 1 }
    }
  },
  "custom": {
    "generated": { "agentName": "custom-json", "agentVersion": 1 }
  }
}
```

(Names and versions illustrative.)

- **The agent is chosen by format and producer:** a registry or catalogue format through
  `formats.<format>.<producer>`, a package's own format through `custom.<producer>`. At 31 the only
  producer with bindings is `generated` (§ 2.1.3).
- **`resolve.json`'s bindings record the route as `via`:** `"format"` for a binding in
  `formats`, `"custom"` for a package's own format bound to the custom-format agent. `"producer"`,
  an agent chosen by producer alone, is [#1479](https://github.com/Consultologist/Consultologist-Blazor/issues/1479) (Milestone 40): **the value is reserved at 31 and
  refused** until then (chapter 7).
- **Bindings hold no instructions.** What the model should write is the format's own
  `description`s (§ 2.5.1), so a catalogue format and a package's own format carry their
  instructions the same way, and a package format needs no binding of its own to have them.
- **No agent settings per node.** Model, reasoning effort and instructions live in the attested
  agent definitions; different behaviour means a format bound to a different agent. A node can't
  name an agent.
- **The attested agent definition also lists the keywords its provider's strict mode rejects**
  (§ 2.3.5).
- **The checks:** publishing the agents catalogue checks that every binding names an existing
  format, a producer in use and an attested agent; publishing a package refuses an agent node
  whose format and producer have no binding.
- **`resolve.json`** records the bundle and a separate `bindings` section; `lock.json` pins the
  agents catalogue beside the formats catalogue (chapter 7). Agent rows in the record name the attested
  definition and the binding that chose it (chapter 8).

### 2.8 Inputs

**Inputs are an object keyed by id in `manifest.json`** (the `inputs` member of [`manifest.schema.json`](v31/schemas/manifest.schema.json))**.** The written order is the Create page's
order. Every member is present.

| Member | Type | `null` | Meaning |
|---|---|---|---|
| `label` | string, not empty or whitespace | no | the Create page label |
| `description` | array of strings | yes | help text on the Create page; chapter 1's one `description` rule |
| `format` | a format name or an inline schema | no | the input's type, which picks the widget |
| `required` | boolean | no | whether the user must supply it; one that isn't required reads `null` when left blank |
| `channel` | string | yes | the content channel (§ 2.8.3); replaces `expectedContent` |

- **There is no `default` member;** an explicit default is [#1456](https://github.com/Consultologist/Consultologist-Blazor/issues/1456) (Milestone 40).
- **There is no `labelField`:** a loop over the input names its items with `itemLabel` (chapter 4).
- **Input ids** follow chapter 1's id rules and reserved list.
- **Inputs are read like nodes:** `input.<id>.value`, `.content` for a text format, `.title` for a
  labelled choice; a bare `input.<id>` is refused (§ 2.2.1).
- **A top-level input keeps `required: true | false`**: it says whether the
  user must supply it, not what the format's `required` list says. An optional input left blank
  reads `null`, in JSON Logic and in templates, and the null rules of chapter 3 apply.
- **What a blank optional input reads**: one rule for every format.

  | Read | Supplied | Left blank |
  |---|---|---|
  | `input.<id>.value` | its value | `null` |
  | `input.<id>.content` (text formats) | its text | `null` |
  | `input.<id>.title` (labelled choices) | the chosen arm's title | `null` |
  | in a template, any of the three | the value, text or title | nothing |
  | in JSON Logic | the value | `null`, under chapter 3 § 6.2's null rules |

  A blank text input is `null`, not `""`.
- **Fields inside an object input follow the format rule** (§ 2.3.3): every field is listed in
  `required`, an optional field has a nullable type, and a field whose type is not nullable must
  be filled in.
- **Order matters:** the object's member order is the Create page's, and **`resolve.json` carries
  the inputs' order explicitly**, since canonical JSON (RFC 8785) sorts members (chapter 7).
- **Function inputs** are `{ label, description, format }`, all required, with no `required` or
  `channel`; a caller passes the literal `null` through `with` for an optional value
  (chapter 4).

#### 2.8.1 Which formats an input may take, and its widget

| Format | Create page widget |
|---|---|
| `string` | a single-line field |
| `string` with a labelled `oneOf` (§ 2.9) | a select, showing each value's `title` |
| `string` with a plain `enum` (§ 2.9) | a select, showing each bare value |
| `number`, `boolean` | a number field; a checkbox (an optional boolean: three choices, § 2.10) |
| `date` | a date picker |
| `plaintext` | a multi-line text area |
| `markdown_block` | a rich-text editor (toolbar, preview), **stored as Markdown, not HTML** |
| an object (inline or a package format) | a field group, one field per property, labelled by its `title` |
| an array | repeating rows, whose `items` take the same formats |

- **Object fields are JSON Schema `properties`:** every field is in the `required` list, an
  optional field is nullable (§ 2.8), and fields nest to any depth.
- **Every property of an object input requires a `title`,** its label on the Create page, so no
  field is shown by its bare id.
- **Field names follow the id pattern, with no reserved names** (§ 2.5.3): a field is always read
  after `.value` (`item.value.title`), so a field called `title` never collides with the `.title`
  read of an enumerated string.
- **Any format may be an input's,** since formats are pure shape (§ 2.1.3), **except**
  `markdown_inline` (no widget, and an inline fragment is not something a clinician submits); a
  top-level `anyOf` (no widget can offer "one of these shapes").
- **Plain text pasted into a Markdown input** can be misread (a leading `#` becomes a heading); the
  rich-text editor shows the formatting as it is typed.

#### 2.8.2 Documents

**Documents need no member.** Any input with a text format takes typed text or a document (the
parser decides), and an array of a text format takes several items, each typed, a document, or an
earlier run's deliverable, in the order sent (chapter 9). A data-format input is typed only,
except an object filled from a `form`. An element from an earlier run's deliverable starts out
model-derived (§ 2.1.2), and its record links to the job it came from.

- **A document uploaded to a Markdown input is converted to Markdown:** headings, lists and tables
  preserved from docx; best effort from PDF and OCR.
- A document uploaded to a `plaintext` input gives its extracted text.

#### 2.8.3 `channel`

| `channel` | On |
|---|---|
| `null` | any input |
| `transcript`, `image`, `ambient-note` | a text-format input, or an array of a text format |
| `form` | an object with at least one property; never an array of objects |

Revisiting the name is [#1427](https://github.com/Consultologist/Consultologist-Blazor/issues/1427) (Milestone 40).

#### 2.8.4 An example: `example-conditional-sections`' inputs at 31

```json
"inputs": {
  "consult_draft": {
    "label": "Consult draft",
    "description": null,
    "format": "markdown_block",
    "required": true,
    "channel": null
  },
  "sections": {
    "label": "Sections to produce",
    "description": null,
    "format": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["title", "kind", "notes"],
        "properties": {
          "title": { "type": "string", "title": "Title" },
          "kind": {
            "type": "string",
            "title": "Kind",
            "oneOf": [
              { "const": "narrative", "title": "Narrative" },
              { "const": "table",     "title": "Table" },
              { "const": "omit",      "title": "Leave out" }
            ]
          },
          "notes": {
            "anyOf": [ { "$ref": "markdown_block" }, { "type": "null" } ],
            "title": "Notes for this section"
          }
        }
      }
    },
    "required": true,
    "channel": null
  },
  "include_billing": {
    "label": "Include the billing section",
    "description": null,
    "format": "boolean",
    "required": false,
    "channel": null
  }
}
```

`notes` is optional, so it is nullable and a blank one is sent as `null`. The field called `title`
is allowed: fields have no reserved names (§ 2.5.3).

The loops over `input.sections.value` say `"itemLabel": "title"` (chapter 4). A condition reads
`{ "===": [ { "var": "item.value.kind" }, "narrative" ] }`, displayed
`item.value.kind = "narrative"`; a template may show the label with `{{ item.value.kind.title }}`
(*"Narrative"*). The billing section's `if` reads `{ "var": "input.include_billing.value" }`.

### 2.9 Enum labels

- **`enum` and `oneOf` are the author's choice, everywhere.** `enum` means bare values with no
  labels. **Labelled values** are JSON Schema's standard form, `oneOf` of `const` with `title`:
  ```json
  { "type": "string", "oneOf": [
      { "const": "new_patient", "title": "New patient" },
      { "const": "follow_up",   "title": "Follow-up" } ] }
  ```
  The Editor's suggestion to switch from one to the other is [#1470](https://github.com/Consultologist/Consultologist-Blazor/issues/1470) (Milestone 41).
- **The rules:** at least two values; values unique, and titles unique (and non-empty); in inputs
  and package formats, every value is snake_case (`^[a-z][a-z0-9_]*$`), so
  values stay printable in conditions and reasons; a field has `enum` or the labelled `oneOf`,
  never both.
- **The value is stored, compared and recorded,** always the raw string. Conditions, skip reasons
  and the record name the value.
- **The label is read as `.title`** (§ 2.2.1): `input.visit_type.title`, `item.value.kind.title`, at
  any depth. `.title` on a plain `enum` is refused. The Create page's select, the Editor and
  History show it.
- **`.title` may be compared in conditions and computed expressions,** for example
  `{ "===": [ { "var": "input.visit_type.title" }, "Follow-up" ] }`. Publish checks that the
  literal is one of the format's titles. **The record prints such a condition with both the raw
  value and the title**, so a decision reads the same whichever was compared.
- **Classification answers get their labels the same way** (`classification`).
- **For a model provider,** the schema becomes a plain `enum` of the `const`s (§ 2.3.5).

### 2.10 Per-run macro choices become optional boolean inputs

A macro that is offered as a per-run choice on the Create page is **an optional boolean input that
the macro's `if` reads**, with no member of its own on the macro:

| The macro is | Test in the macro's `if` | While the input is unset |
|---|---|---|
| offered only when the input is yes | `{ "===: [ { "var": "input.<id>.value" }, true ] }` | `null === true` is false: not offered |
| offered unless the input is no | `{ "!==: [ { "var": "input.<id>.value" }, false ] }` | `null !== false` is true: offered |

The input:

```json
"include_safety_netting": {
  "label": "Safety-netting advice",
  "description": null,
  "format": "boolean",
  "required": false,
  "channel": null
}
```

- **A macro's own `if` and the test** are joined with `and`: `{ "and": [ <its if>, <the test> ] }`.
- **The Create page shows an optional boolean as three choices** (unset, yes, no), so "unset" keeps
  the macro's default, and **unset is sent as `null`**. A plain checkbox would show a default-on choice
  unchecked while meaning on (chapter 9).

### 2.11 What the migration does to types and inputs

What the migration from 30 does to types and inputs (the format conversions, the inputs' new shape, the optional boolean inputs for per-run macro choices) is chapter 10.

### 2.12 `WorkflowPackages/Current`: what satellites see

The engine's `WorkflowPackages/Current` response is the engine's API to the Copilot agent and the Zoom app, not part of the package format, and is not defined here.

### 2.13 Refusals

Every sentence below is used as written; chapter 11 lists every sentence of this format.

**Sentences outside the checker.**
- *"This workflow needs the web app"* (a satellite, not the checker).
- History's *"Not sent to the model: …"* (§ 2.3.5) and *"computed from model text: <key>"* (§ 2.1.2).

**Kinds and formats:**
- *"Node '<id>' declares unknown kind '<kind>' (accepted: agent, rendered, computed, for, while, if, case, call)."*
- *"Node '<id>' declares kind let; a let is now kind computed, with its JSON Logic in expression."*
- *"Node '<id>' is kind <kind> and declares producer '<value>'; a <kind> node's producer is <generated | computed>."*
- *"Node '<id>' declares producer '<value>', which is reserved for a later version (accepted at 31: generated, computed)."*
- *"Node '<id>' declares <modelDerived | runDependent | profileCarrying> <value>, but its reads make it <derived>: <the read that does, or none>."*
- *"Node '<id>' is kind agent and returns <format>, which has no binding for producer <producer> in agents/bindings.json."*
- *"Node '<id>' is kind rendered and returns <format>; a rendered node returns plaintext, markdown_block or markdown_inline."*
- *"Node '<id>' is kind agent and declares an inline format; an agent's format is named, in formats/."*
- *"<Flow> '<id>' declares format <declared>, but its ret gives <derived>."*
- *"Branch <n> of <if | case> '<id>' returns <format>, which is not in the declared union <union>."*
- *"Format '<name>' is not a built-in, catalogue or package format."*

**Reads:**
- *"'input.<id>' is read bare; read input.<id>.value, or input.<id>.content for text."*
- *"'<path>.title' reads the title of a plain enum, which has none; use a labelled oneOf, or read .value."*
- *"<Condition> compares <path>.title with '<literal>', which is not one of its titles (<titles>)."*

**The dialect:**
- *"<Format | Input '<id>'> uses keyword '<keyword>' at <path>, which is outside the formats dialect."*
- *"Format '<name>' declares no $schema; every format file names the dialect (urn:consultologist:spec:31:dialect)."*
- *"Format '<name>' declares $schema '<value>', but the package is specVersion <n>, whose dialect is <id>."*
- *"<Format> at <path> declares additionalProperties <value>; every object declares additionalProperties: false."*
- *"<Format> at <path> lists '<property>' in required but declares no such property."*
- *"<Format> at <path> leaves '<property>' out of required; every property is listed in required, and an optional one is written as nullable."*
- *"Node '<id>' returns <format>, an anyOf at its root, which strict mode can't send to a model; wrap it in an object."*
- *"<Format> at <path> writes a nullable <type> with anyOf; write it as \"type\": [\"<type>\", \"null\"]."*
- *"<Format> at <path> declares type <list>; a type array is one type plus \"null\"."*
- *"<Format> at <path> uses format '<value>'; the only format is date, on a string."*
- *"<Format> at <path> has '<keyword>' beside $ref; only title and description may sit beside a $ref."*
- *"<Format> at <path> refers to itself; recursive formats aren't supported."*
- *"Package format '<id>' declares $id; a package format's $id is written at publish."*
- *"Package format '<id>' is a <string | number | boolean>; a package defines object and array formats, and refers to built-in and catalogue formats by name."*

**Annotations:**
- *"Format '<name>' is a text format and declares no contentMediaType."*
- *"Format '<name>' is Markdown and declares no x-markdown (block or inline)."*
- *"<Format> declares <contentMediaType | x-markdown> at <path>, where it doesn't apply."*
- *"<Input '<id>' | Node '<id>'>'s inline format declares <contentMediaType | x-markdown>; text inside an inline format is a $ref to a text format."*

**Formats folder:**
- *"formats/index.json lists '<id>', but formats/ has no <id>.json."*

**Inputs:**
- *"Input '<id>' takes markdown_inline; use plaintext or markdown_block."*
- *"Input '<id>' takes a choice of shapes (anyOf); an input has one shape."*
- *"Input '<id>' declares channel '<channel>' (accepted: transcript, image, ambient-note, form)."*
- *"Input '<id>' declares channel '<channel>', which is only for a text input or an array of text."*
- *"Input '<id>' declares channel 'form', which needs an object with at least one property."*
- *"Input '<id>' field '<property>' has no title; the Create page labels each field by its title."*
- *"Input '<id>' declares default; inputs have no default at 31."*

**Enums:**
- *"<Subject> declares one value; an enum with one value is a constant, not a choice."*
- *"<Subject> declares value '<value>' twice."*
- *"<Subject> value '<value>' must be snake_case (a lowercase letter, then lowercase letters, digits, or underscores)."*
- *"<Subject> gives two values the title '<title>'."*
- *"<Subject> writes oneOf branch <n> as <shape>; each branch is exactly { \"const\": <value>, \"title\": <label> }."*
- *"<Subject> declares both enum and oneOf; write one."*
- *"<Subject> is nullable but its enum doesn't list null; a nullable enum lists null among its values."*
- *"<Subject> is nullable but its oneOf has no { \"const\": null } arm; a nullable labelled enum adds one."*

**Strict mode's size limits:**
- *"Format '<name>' declares <n> properties; a format sent to a model declares at most <limit>."*
- *"Format '<name>' nests <n> levels deep at <path>; a format sent to a model nests at most <limit>."*
