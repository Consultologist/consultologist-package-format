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
| [3 Expressions](#3-expressions) | JSON Logic: conditions, `computed`, every operation, null rules, `run.*`, the printer, the evaluator, `matches` and `has_word` |
| [4 Loops and functions](#4-loops-and-functions) | `for`, `while`, `until`, branches, `.items`, functions and `call` |
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

(Its `standard_section` field is called `title`: field
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
| `profileCarrying` | boolean | no | every node and check, checked against the derived value ([chapter 3 § 4.6](#346-profile-carrying-is-contagious)) |
| `if` | a JSON Logic condition (chapter 3) | yes: always | every production leaf (`agent`, `rendered`, `computed`, `call`), check, snippet, macro, macro folder and deliverable. A node's own condition is spelled `if`; a `case` branch keeps `when` for its values (chapter 4) |

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
- **A package whose ids collide with a reserved word is renamed by the migration** (chapter 10):
  `example-nested-note`'s loop is `sections`, not `parts`.

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
[chapter 3](#3-expressions); where each kind's file lives is [chapter 1](#1-files-and-scopes).

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

## 3. Expressions

This chapter defines the one language a version 31 package uses to **decide** (every header
condition) and to **compute** (a `kind: computed` node's `expression`): JSON Logic, written
directly in the header, with a fixed set of standard and custom operations, typed against the
format dialect of [chapter 2](#2-types-and-inputs). It covers where expressions appear and what
each site may read, `run.*` reads and the contagious flags, the date operations, null semantics,
strict equality, the printer, and the evaluator. Scriban, the presentation language, is chapter 5.

### 3.1 The rule: JSON Logic decides and computes; Scriban presents

| Purpose | Language | Where |
|---|---|---|
| decide | JSON Logic | every header condition (§ 3.3) |
| compute | JSON Logic, plus the custom operations (`object` among them) | a `kind: computed` node's `expression` |
| present | Scriban (chapter 5) | prompt bodies, `rendered` bodies, renderers, deliverable templates, snippet and macro bodies |
| describe types | the JSON Schema dialect (chapter 2) | formats |

- **Authors write JSON Logic directly.** What is written in the header is what `resolve.json`
  stores and what the engine runs. There is no expression-string syntax in the spec. The
  converter (chapter 10) turns expressions into JSON Logic and back as a tool, not as the
  format.
- **Decisions live in headers; bodies only present.** Whether a node runs, an item is included, a
  part or macro is used or a loop stops is a header condition, evaluated and recorded by the
  engine.
- **`let` is gone.** One no-model kind, `computed`, holds one JSON Logic expression in its member
  `expression`; `op` and `with` are retired.

### 3.2 The written form

#### 3.2.1 Shape

A JSON Logic **rule** is one of:

- a **literal**: a JSON string, number, `true`, `false` or `null`;
- an **array** of rules, which evaluates each element and yields the list (lists are native);
- an **operation**: a JSON object with exactly one member, whose name is the operation and whose
  value is its operands.

#### 3.2.2 The canonical form

`resolve.json` holds JSON Logic "in one canonical form" The canonical form is also the
only form an author may write, so what is written is byte-for-byte what is stored:

- **`var` takes one string**, the path: `{ "var": "input.kind.value" }`. The array form and the
  default second operand are refused (fixed arity). An empty path (the whole data) is
  refused.
- **`object` takes one object**, a map from field names to rules (§ 3.5.4).
- **Every other operation takes an array**, even with one operand: `{ "!": [ … ] }`,
  `{ "size": [ { "var": "input.prior_notes.value" } ] }`.
- **Paths** are dot-separated segments: a root (§ 3.4), then member and field names, each matching
  `^[a-z_][a-z0-9_]*$` or a format's declared property name. Numeric segments (list indexes) are
  refused: a positional read of a list is the zip the format rules out; a loop's `.items` pairs by
  identity instead.

The serialisation in `resolve.json` (member order, number form, RFC 8785) is
chapter 7's.

#### 3.2.3 Example

The `applies` branch of `example-conditional-sections`, a section kept unless it is the billing one and billing was not asked for:

```json
{ "or": [
    { "!==": [ { "var": "item.id" }, "billing" ] },
    { "===": [ { "var": "input.include_billing.value" }, true ] } ] }
```

Printed (§ 3.8): `item.id ≠ "billing" or input.include_billing.value = true`.

### 3.3 Where expressions appear

| Site | Member | Defined in | Must type as |
|---|---|---|---|
| an `if` flow node | `if` | chapter 4 § 5 | condition |
| a `while` | `while` | chapter 4 § 3 | condition |
| a `for` or `while` | `until` (or `null`) | chapter 4 §§ 2–3 | condition |
| a check | `if` (or `null`) | chapter 6 | condition |
| a deliverable | `if` (or `null`) | chapter 6 | condition |
| a part (a node's `parts`) | `if` (or `null`) | chapter 5 | condition |
| a macro, and a macro folder | `if` (or `null`) | chapter 5 | condition |
| a production leaf (`agent`, `rendered`, `computed`, `call`) | `if` (or `null`) | chapter 1 | condition (see below) |
| a `computed` node | `expression` | chapter 1; § 3.5 here | the node's declared `format` |

- **A condition** must type as `boolean` (or `boolean | null`), or as the list `missing`
  returns (§ 3.5.1). It is tested by truthiness (§ 3.6.4).
- **A `computed` expression** must type as the node's declared `format`, checked through each
  operation's typed result (§ 3.7). A computed node's header is judged by
  [`v31/schemas/node-computed.schema.json`](v31/schemas/node-computed.schema.json).
- **Not expressions:** a `for`'s source (`in`), a `case` subject and a `call`'s `with` arguments
  are **reference strings** (chapter 4), never JSON Logic expressions.
  Each names one readable thing. A list, subject or argument that has to be computed is a
  `computed` node, which the reference then names: compute, then name. Author documentation for
  this pattern is [#1473](https://github.com/Consultologist/Consultologist-Blazor/issues/1473).
- **Snippet folder items have no `if`**,
  so a folder's size is its number of files and there is no folder-item condition to read
  anything. Dynamic folder sizes are [#1468](https://github.com/Consultologist/Consultologist-Blazor/issues/1468) (Milestone 40).
- **A production leaf's own condition is spelled `if`,** a required member that is a condition or
  `null`, so every header gate has one name. A `case` branch keeps `when` for its list of values
  (chapter 4 § 5.2).

### 3.4 What each site may read

#### 3.4.1 The roots

| Root | Means | Typed by |
|---|---|---|
| `input.<id>` | a package input, read like a node: `.value` (the raw value, every input), `.content` (a text-format input's text), `.title` (the chosen `oneOf` arm's title, at any depth); a bare `input.<id>` is refused | the input's `format` (chapter 2) |
| `node.<id>` | a visible node: `.value`, `.content`, `.state`, and per kind `.items`, `.passes`, `.stopped`, `.history` (chapter 4) | the node's `format` |
| `check.<id>` | a visible check: `.value` (a `check_result`), `.state`; a check loop's `.items` | chapter 6 |
| `item` | the innermost loop's item: `.id`, `.value`, `.parent` (chapter 4 § 2.6) | the loop source's element |
| `pass` | the enclosing `while`'s pass: `.number`, `.node.<id>`, `.previous`, `.parent`, `.history` (chapter 4 § 3.3) | the format of the node it names (chapter 4 § 3.3) |
| `param.<id>` | a function's parameter, inside a function only: `.value`, `.content` (chapter 4 § 7) | the parameter's `format` |
| `run.<fact>` | a run fact (§ 3.4.3) | § 3.4.3 |

**Never readable by JSON Logic:** `profile.*` (no condition and no computed expression reads the
profile),
`snippet.*`, `part.*`, `macro.*`, `renderer.*` and `deliverable.*`. A snippet folder's item data
is read through the loop that iterates it (`item.value.title`).

**`.title` may be compared** in conditions and computed expressions, as a `string`: publish
checks that the literal is one of the format's titles, and `.title` on a plain `enum` is refused.
The stored and recorded value is always the raw value; the record prints the condition with both
the raw value and the title (§ 3.10).

Visibility (which `node.<id>` a site can see, alignment by path, reading into a loop's body) is
the rule of chapter 1 § 9, and the same for JSON Logic as for templates.
Every `var` is a dependency edge, as every template read is, except reads of earlier passes
(`pass.previous…`, `pass.history`).

#### 3.4.2 Per site

| Site | May read | Refused |
|---|---|---|
| `if` flow node | everything visible at its place: `input`, `node`, `check`, `item`, `pass`, `param`, `run` | `profile` and the others of § 3.4.1 |
| `while` | its body's nodes by bare id (this pass), `pass`, and anything that runs before the loop; `item`, `param`, `run` | as above |
| `until` on a `for` | the item's body nodes by bare id, `item`, anything that runs before the loop; `pass`, `param`, `run` | as above |
| `until` on a `while` | as the `while` | as above |
| check `if` | as chapter 6 says; in a check loop, `item` is the `.items` element (`item.state`) | as above |
| deliverable `if` | `input`, a node's **`.value`** (data), `run` | `.content` (text), `check.*` (a possible cycle), `profile`, deliverables |
| part `if` | what the node's prompt reads, data roots only | as above |
| macro `if`, macro folder `if` | evaluated **where the macro is placed**: what the placing node's prompt reads, data roots only | `param.*` (a shared macro must not depend on one function's parameter) |
| production leaf `if` (§ 3.3) | what a template at its place reads, data roots only | as above |
| `computed` `expression` | everything visible at its place: `input`, `node`, `check`, `item`, `pass`, `param`, `run` | as above |

**Inside a function** every site reads only `param.*` and the function's own nodes; `input.*`,
outer nodes, an outer `item` or `pass`, `run.*`, `check.*` and `profile.*` are refused
(chapter 4 § 7.4).

#### 3.4.3 Run facts

JSON Logic may read the same `run.*` set as bodies: `run.date`, `run.id`,
`run.package`, `run.engine`.

| Fact | Type | Value |
|---|---|---|
| `run.date` | `date` (`string`, `format: date`) | the job's start date in the account's time zone, an IANA name recorded beside it |
| `run.id` | `string` | the job's id |
| `run.package` | `string` | `<name>@<version>` of the package version run |
| `run.engine` | `string` | the engine's release version, in the `v2026.11.5` form |

- **Recorded like any read:** the raw value of each run fact the package reads is recorded once
  per run (chapter 8).
- **No time zone, no job:** every job is refused at start until the account's time zone is set,
  whether or not the package reads `run.date` (chapter 9).

#### 3.4.4 Run-dependence is contagious

- **A value is run-dependent** when its expression reads `run.*`, directly or through any value
  that is itself run-dependent.
- **A decision is run-dependent** when its condition reads `run.*` or a run-dependent value. The
  record marks it so, and History can say a branch differed because a run fact differed.
- **A decision doesn't pass the flag on** to what it chooses: the flags describe content only.
  A node that runs because a run-dependent `if` was true isn't run-dependent for that; the
  decision has its own row.
- **The run-neutral hash of a run-dependent computed value** covers its recipe (the expression
  and its other reads), not the value, so two runs with the same inputs share it even when the
  dates differ.
- **A body's read of a run-dependent value is a run spot** (chapter 5): a marker in the
  run-neutral render, filled afterwards at the position recorded while rendering (chapter 5 § 4).
- **The advance warning** (Editor and publish) names every run-dependent value and decision,
  not only direct `run.*` reads (§ 3.11.2).

**How far it spreads**.
Run-dependence passes through everything a value is made from:

- `computed` and `rendered` nodes that read a run-dependent value;
- `agent` nodes whose prompt reads `run.*` or a run-dependent value;
- a `call`'s result when any argument is run-dependent (the parameter bound to it is
  run-dependent inside the function);
- a flow node whose `ret` is run-dependent;
- a loop's items when its source is.

It never passes through a condition: a branch's `if`, a `case` subject or a `while` condition
decides which content exists, not what it is made from.

It is worked out from `resolve.json`'s edges before any run, so the warning can name each value
before a job starts. Each row records it as `runDependent` (chapter 8). **Every node header
writes it too, as `runDependent: true | false`, checked against the derived value** like
`reproducible`; a mismatch is refused. Requiring a run-dependent value in a read is [#1478](https://github.com/Consultologist/Consultologist-Blazor/issues/1478)
(Milestone 40).

#### 3.4.5 Model-derived is contagious

**Model-derived** is a second contagious flag, beside run-dependence and worked out the same
way. It says a value came from a model's output somewhere upstream.

- **Where it starts:**
  - the output of every node whose `producer` isn't `computed` (chapter 2 § 1.3), so every
    `agent` node's output is model-derived (the reverse doesn't hold: a `computed` value can be
    model-derived too);
  - an input element from a previous run's deliverable, whose record links to the job it
    came from (chapter 4 § 4).

  Typed text and uploaded documents start clean. Other machine sources (OCR, transcription) are
  producers reserved for Milestone 40 (`extracted`; chapter 2 § 1.3).
- **How it spreads:** exactly as run-dependence does (§ 3.4.4): through `computed` and `rendered`
  nodes, `agent` prompts, `call` arguments and results, a flow node's `ret`, and a loop's items.
  A decision whose condition reads a model-derived value is model-derived; as with
  run-dependence, the decision doesn't pass the flag on to what it chooses.
- **Formats are shape only.** `lower`, `trim` and any other `computed` expression return their
  operand's format unchanged, so `trim` of an agent's `plaintext` is `plaintext`; the node's
  producer is `computed` and its `reproducible` stays `true`. The value keeps its lineage through
  the flag, never through its format.
- **It is recorded and shown:** each row carries `modelDerived` (chapter 8), and History, the
  diagram and the Editor show it: *"computed from model text: node.draft"*.
- **It is worked out, and written on every node header:** the resolver computes it from
  `resolve.json`'s edges before any run, and each header declares `modelDerived: true | false`,
  checked against that value; a mismatch is refused. It stays a node member, never a
  format's. Requiring a model-derived value in a read is [#1478](https://github.com/Consultologist/Consultologist-Blazor/issues/1478) (Milestone 40).

Example, fictional: a `computed` node that checks whether a model's draft names a drug:

```json
{ "in": [ "letrozole", { "lower": [ { "var": "node.draft.content" } ] } ] }
```

It returns `boolean`, its producer is `computed`, it is reproducible, and it is model-derived,
because `node.draft` is an `agent` node's output: its header writes `modelDerived: true` and
`runDependent: false`. A macro's `if` that reads it is a model-derived
decision.

#### 3.4.6 Profile-carrying is contagious

**Profile-carrying** is a third contagious flag, beside run-dependence and the model-derived
flag, worked out the same way from `resolve.json`'s edges and describing content only.

- **Where it starts:** any value whose text had a profile-reading macro substituted into it
  (chapter 5 § 8). No JSON Logic expression reads `profile.*` (§ 3.4.1), so it starts only in text.
- **How it spreads:** as the other two do (§ 3.4.4): through `computed` and `rendered` nodes,
  `agent` prompts, `call` arguments and results, a flow node's `ret`, and a loop's items. A
  condition doesn't pass it on.
- **Where it may be read:** deliverables may read a profile-carrying value. A prompt, a part or
  a condition that reads one is refused at publish (§ 3.11.1), so a clinician's signature or
  credentials never reach a model or decide a branch.
- **It is written and recorded:** every node header writes `profileCarrying: true | false`,
  checked against the derived value like `runDependent`; a mismatch is refused.
  Each row carries `profileCarrying` (chapter 8), and a row that is
  profile-carrying follows the profile's retention.

### 3.5 The operations

#### 3.5.1 Standard JSON Logic operations

The allowed standard operations are `var`, `missing`; `if` (with an else); `===`, `!==`, and
`<`, `<=`, `>`, `>=` with two operands; `and`, `or`, `!`, `in`, `cat`; `+`, `-`, `*`, `/`, `%`,
`min`, `max`. Every operation not in this table or §§ 3.5.2–3.5.5 is refused at publish (§ 3.11.1).
Reviewing the whole set is [#1471](https://github.com/Consultologist/Consultologist-Blazor/issues/1471) (Milestone 40).

"data" is `string`, `number`, `boolean` and `date`, plus `null` where the operand's type is
nullable; "text" is any text format (`plaintext`, `markdown_block`, `markdown_inline`).

| Operation | Operands | Operand types | Result | Null behaviour | Notes |
|---|---|---|---|---|---|
| `var` | one path string | n/a | the path's type | absent or null reads as `null` | § 3.2.2 |
| `missing` | one array of literal path strings | paths of the site's roots | `list<string>` (the absent paths) | a path is missing when its value is `null`, absent or `""` (as json-logic-js does, so an unsupplied text input counts as missing) | tested by truthiness (empty list is false) |
| `if` | 3 or more, odd count: `[c1, a1, c2, a2, …, else]` | conditions, then branches of one type | the branches' type | a `null` condition is false | lazy; an even count (no else) is refused, since every member is explicit |
| `and`, `or` | 2 or more | `boolean` (nullable allowed) | `boolean` | `null` is false | short-circuits; standard JSON Logic returns an operand, which is a boolean here because operands are typed boolean |
| `!` | 1 | `boolean` (nullable allowed) | `boolean` | `!null` is `true` | refused on text, numbers, lists and objects (not a blank test) |
| `===`, `!==` | 2 | two data values of one type, or either `null` | `boolean` | `null` is compared as a value: `null === null` is true | refused on text, lists and objects; an enum literal must be a value of the enum |
| `<`, `>`, `<=`, `>=` | exactly 2 | two `number`s, or two `date`s | `boolean` | **false** when either operand is `null` (no coercion to 0) | dates compare chronologically; the 3-operand "between" form is refused (one spelling: `and` of two comparisons) |
| `+`, `*` | 2 or more | `number` | `number` | `null` if any operand is `null` | strings are never coerced |
| `-` | 1 (negation) or 2 | `number` | `number` | `null` if any operand is `null` | |
| `/`, `%` | 2 | `number` | `number` | `null` if any operand is `null`; division or remainder by zero gives `null` | |
| `min`, `max` | 1 or more | `number` | `number` | `null` if any operand is `null` | part of arithmetic |
| `in` (list) | 2: `[needle, list]` | data needle; a `list` of the same data type | `boolean` | `null` needle: true only if the list holds `null`; `null` list: false | membership: `input.note_type.value in ["consult", "follow_up"]` |
| `in` (text) | 2: `[needle, haystack]` | a `string` needle; a text or `string` haystack | `boolean` | either `null`: false | exact, case-sensitive substring search (ordinal); on Markdown it searches the source |
| `cat` | 2 or more | `string`, `number`, plain-text formats | `string` when every operand is `string`; `plaintext` otherwise | a `null` operand contributes `""` (json-logic-js writes `"null"`) | Markdown operands refused (convert with `plain` first, so one result has one media type); numbers in the invariant culture |

**Refused standard operations** (§ 3.11.1): `==` and `!=` (strict equality only);
`substr`;
`!!` (with `!` limited to booleans it only repeats its operand) and `?:` (a second spelling of
`if`); `missing_some`, `merge` and `log`; `map`, `filter`, `reduce`, `all`, `some` and `none`
(they change what `var` names inside them, which the checker's typing of § 3.7 doesn't cover); three-operand comparisons; and Corvus's non-standard extras
(`asDouble`, `asLong`, …).

#### 3.5.2 Custom text operations

Every custom operation has a **fixed arity with no optional operands**, runs in the
**invariant culture**,
and is **versioned** with a semantic version where any change to output bytes is a major
version, pinned by golden tests and listed in `lock.json` (chapter 7). All are version
`1.0.0` at 31.

"Text-like" below means a text format or `string`. Characters are **Unicode scalar values**
(code points), never UTF-16 units. Whitespace is Unicode `White_Space`.

| Operation | Signature | Result | Meaning | Null behaviour |
|---|---|---|---|---|
| `size` | `size(x)` | `number` | text-like: the count of code points; a list: its element count | `null` |
| `blank` | `blank(x)` | `boolean` | true if `x` is empty or only whitespace | `true` |
| `words` | `words(x)` | `number` | the count of maximal runs of non-whitespace characters | `null` |
| `lines` | `lines(x)` | `number` | `0` for `""`; otherwise 1 plus the count of line breaks (`\r\n`, `\n`, `\r`), not counting one at the very end | `null` |
| `lower` | `lower(x)` | text-like (see below) | lower-cased by the invariant culture's simple case mapping | `null` |
| `trim` | `trim(x)` | text-like (see below) | leading and trailing whitespace removed | `null` |
| `starts_with` | `starts_with(x, prefix)` | `boolean` | ordinal, case-sensitive prefix test; on Markdown, of the source | `false` if either is `null` |
| `ends_with` | `ends_with(x, suffix)` | `boolean` | ordinal, case-sensitive suffix test | `false` if either is `null` |
| `plain` | `plain(x)` | `plaintext` | Markdown converted to plain text by the same conversion as plain-text output (Markdig with the listed extensions); a plain-text operand is returned unchanged | `null` |
| `matches` | `matches(x, pattern)` | `boolean` | § 3.5.3 | `false` if `x` is `null` |
| `has_word` | `has_word(x, word)` | `boolean` | § 3.5.3 | `false` if `x` is `null` |

- **`lower` and `trim` return their operand's format unchanged:** `plaintext` stays `plaintext`, `markdown_block` stays `markdown_block`,
  `markdown_inline` stays `markdown_inline`, `string` stays `string`. A computed node that trims
  an agent's text has producer `computed`, and its value stays **model-derived** (§ 3.4.5).
- **Case-insensitive search** is written by lowering the haystack:
  `{ "in": [ "letrozole", { "lower": [ { "var": "node.draft.content" } ] } ] }`. `in` stays
  standard.
- **Text searched as read** is written with `plain`:
  `"letrozole" in plain(input.consult_draft.content)`.

#### 3.5.3 `matches` and `has_word`

**`matches(x, pattern)`**
- **Dialect: I-Regexp (RFC 9485), with search semantics:** true if the pattern occurs
  **anywhere** in `x` (JSONPath's `search()`, not its whole-string `match()`).
- **I-Regexp has no `\b`, no `\d`/`\w`/`\s`, and no `^`/`$` anchors.** A start or end is tested
  with `starts_with`/`ends_with`; a whole word with `has_word`.
- **`pattern` is a literal string** in the package, never computed, checked against RFC 9485's
  grammar at publish, at most **200** characters long (counted in code points).
- **No flags:** always case-sensitive. Case-insensitive matching lowers the text and writes the
  pattern in lower case: `matches(lower(x), "letrozole|femara")`.
- **Typing:** `x` is a text format or `string` data. On Markdown it searches the source.
- **Engine:** the I-Regexp pattern is translated to .NET per RFC 9485 § 3.5 (for example `.`
  becomes `[^\n\r]`) and run with `RegexOptions.NonBacktracking | RegexOptions.CultureInvariant`.
- **`matches` doesn't depend on the clock**: there is no wall-clock time-out, so a
  replay gives the same decision. Each pattern is compiled at publish with the engine's exact
  options; a counted repetition (`{n,m}`) is at most **100**; the text searched is at most
  **1 MiB** (longer text fails the node that owns the condition, § 3.11.3). .NET's non-backtracking
  matching is linear in the text, so these bounds bound the work. Decision times come from the
  orchestration's replay-safe clock. (.NET matches UTF-16
  units, so the conformance suite carries vectors with characters outside the Basic
  Multilingual Plane to prove the translation counts code points.)
- **The record** keeps the pattern (package text, part of the printed condition) and the true or
  false result. **The matched text is never recorded.**

**`has_word(x, word)`**
- True if `word` occurs in `x` (ordinal, case-sensitive) with a **word boundary** on each side:
  the character before the occurrence, if any, and the character after it, if any, are not word
  characters. Word characters are .NET's: Unicode letters (`L*`), marks (`M*`), decimal digits
  (`Nd`) and connector punctuation (`Pc`, which includes `_`).
  `has_word(input.draft.content, "pain")` is false for "painful" and "Spain".
- **`word` is a literal, non-blank string,** checked at publish like a pattern, so it is package
  text in the record. It may contain spaces (`"chest pain"`).
- **Typing** as `matches`.
- A broader `has_word` is [#1472](https://github.com/Consultologist/Consultologist-Blazor/issues/1472) (Milestone 40).

#### 3.5.4 Custom structural and check operations

| Operation | Signature | Operand types | Result | Null behaviour |
|---|---|---|---|---|
| `object` | `{ "object": { "<field>": rule, … } }` | each field's rule typed against the target format's property | an object | a field's rule may yield `null` only where the property is nullable (checked at publish) |
| `terms_subset` | `terms_subset(of, in, failWith)` | `concept_list`, `concept_list`, literal `string` | `check_result` | a `null` list reads as empty |
| `all_pass` | `all_pass(list, failWith)` | a check loop's `.value` or `.items`, literal `string` | `check_result` | elements that did not complete are ignored; a `null` or empty list (nothing judged) **fails**, with `failWith` |
| `count_pass` | `count_pass(list, min, failWith)` | as `all_pass`; `min` a non-negative integer **literal** | `check_result` | counts passed elements among those that completed |

**Check operations judge only `completed` items, and always return a `check_result`, never
`null`**.
The `check_result` shape (`pass`, `message`, `uncovered`, `untested`, `passed`, `total`, every
member present) is chapter 6's.

- **`object` builds objects.** Lists are native arrays; a JSON object in a rule is read as an
  operation, so `object` is the one way to build one. Its operand is one map; each field may use
  any allowed operation, including a nested `object`. Fields are checked at publish against the
  computed node's `format`, field by field: every property present (every property is in
  `required`, chapter 2 § 3.3; a nullable one may be `null`), no other field.
- **`failWith` is a literal string,** checked at publish: a failed check speaks the package's
  own sentence, never a computed one.
- **`terms_subset`** passes when every codable concept in `of` (an active SNOMED CT concept with
  an id) has the same concept id in `in`; uncovered and untested terms are reported in the `check_result`.
  The `check_result` shape is chapter 6's.
- **The `list` operand of `all_pass` and `count_pass` is a check loop's `.value` or its
  `.items`;** both are accepted, and chapter 6's rule that check operations judge only `completed` items reads
  the same either way. A `.value` is
  `list<check_result>` of the items that completed (chapter 4 § 2.5); with `.items`, each
  element's `value` is used and an element whose `state` is not `completed` is ignored. Ignoring
  unrun items lets a check loop's `if` skip sections that weren't produced without failing the
  aggregate.

Migrated check example (chapter 6 owns checks; shown for the expression):

```json
{ "kind": "computed", "producer": "computed", "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "format": "check_result",
  "expression": { "terms_subset": [ { "var": "node.extract_input_terms.value" },
                                    { "var": "node.extract_note_terms.value" },
                                    "The note does not cover every clinical term found in the referral." ] } }
```

#### 3.5.5 Date operations

All take and give `date` values (`string` with `format: date`, `YYYY-MM-DD`, no time of day),
in the proleptic Gregorian calendar, with no time zone arithmetic (`run.date` is already a date
in the account's zone).

| Operation | Signature | Result | Meaning | Null behaviour |
|---|---|---|---|---|
| `days_between` | `days_between(a, b)` | `number` (integer) | whole days from `a` to `b`; negative if `b` is earlier | `null` if either is `null` |
| `years_between` | `years_between(a, b)` | `number` (integer) | **completed** years from `a` to `b`: a year counts once its anniversary is reached; negative if `b` is earlier (the same rule mirrored) | `null` if either is `null` |
| `add_days` | `add_days(date, n)` | `date` | `date` plus `n` days | `null` if either is `null` |

- **29 February:** in a year with no 29 February, an anniversary of 29 February is reached on
  **1 March**. Someone born on 2008-02-29 is 0 on 2009-02-28 and 1 on 2009-03-01.
- **`n` in `add_days`:** a `number`; a non-integer, or a result outside years 0001–9999, gives
  `null`.
- **A malformed date at run time** gives `null`. It can only arise from data that escaped
  validation, since date inputs and date fields are validated against `format: date`.
- **Comparing dates** uses `<`, `>`, `<=`, `>=` and `===` on two `date`s (§ 3.5.1).

Example, fictional: *a reminder about bone density screening, for patients 65 or older at the
date of the run.*

```json
{ ">=": [ { "years_between": [ { "var": "input.date_of_birth.value" }, { "var": "run.date" } ] }, 65 ] }
```

Printed: `years_between(input.date_of_birth.value, run.date) ≥ 65`. It reads `run.date`, so the
decision is run-dependent (§ 3.4.4).

### 3.6 Values, absence and null

#### 3.6.1 What a read gives

| Read | Gives |
|---|---|
| `input.<id>.value` (or `.content`, `.title`) of a supplied input | its raw value (its text, the chosen arm's title), typed by its format |
| an unsupplied or blank optional input | `null` for `.value`, `.content` and `.title`, whatever its format; a template renders it as nothing (chapter 2 § 8's table) |
| `node.<id>.value` of a node that completed | its value |
| `node.<id>.value`, `.content` of a node that did not complete (skipped, not run) | `null`; `.state` says why |
| `node.<id>.state` | `"completed"`, `"skipped"` or `"not_run"` |
| a nullable field holding `null` | `null` |
| `pass.previous…` on the first pass | `null` |

#### 3.6.2 The null rules

Milestone 39 implements **runtime semantics**: nullable operands are not refused at publish, and
`null` behaves as each operation's row in § 3.5 says.
In summary:

- **comparisons** (`<`, `>`, `<=`, `>=`) with a `null` operand are **false**; `null` is never
  coerced to `0`;
- **`===` and `!==` compare `null` as a value;**
- **arithmetic and the date operations give `null`** when any operand is `null`;
- **the text operations:** `size`, `words`, `lines`, `lower`, `trim` and `plain` give `null`;
  `blank` gives `true`; `starts_with`, `ends_with`, `matches` and `has_word` give `false`;
- **`cat`** reads `null` as `""`; **`missing`** counts `null` and `""` as missing;
- **truthiness:** `null` is false (§ 3.6.4);
- **evaluation never throws;** division by zero gives `null`.

**The pitfall stated for authors:** under these rules `{ "!": [ { ">": [ { "var": "input.age.value" }, 65 ] } ] }`
is **true** when the age is missing: "not over 65" includes "unknown". An author who means
"known and not over 65" writes the `null` test:
`{ "and": [ { "!==": [ { "var": "input.age.value" }, null ] }, { "<=": [ { "var": "input.age.value" }, 65 ] } ] }`.

Revisiting the rule (required guards, or a library's default behaviour) is
[#1453](https://github.com/Consultologist/Consultologist-Blazor/issues/1453), Milestone 40. It does not change 31.

#### 3.6.3 Each operation's null behaviour is a conformance vector

The conformance suite (chapter 10) carries a vector for every row of §§ 3.5.1–3.5.5 with a `null`
operand, and for every absence case of § 3.6.1.

#### 3.6.4 Truthiness

A condition's result is tested by truthiness: `false`, `null` and the empty list are false;
`true` and a non-empty list are true. Because conditions must type as `boolean` or as `missing`'s
list (§ 3.3), the other cases of JSON Logic's truthiness (`0`, `""`, objects) never reach a
decision.

### 3.7 Typing

The checker types every rule against the dialect (chapter 2), reading formats as they are,
`$ref`s and `anyOf` included.

- **Data and text are separate types**:
  - **data** (`string`, `number`, `boolean`, `date`) supports `===`, `!==`, `in` (membership),
    and orderings on numbers and dates;
  - **text** supports `blank`, `size`, `words`, `lines`, `in` (search), `starts_with`,
    `ends_with`, `matches`, `has_word`, `lower`, `trim`, `plain` and `cat` (plain text only).
- **Refused on text:** `===`/`!==` against a literal or another text; `<`, `>`, `<=`, `>=`;
  `substr`; `!` as a blank test.
- **Numbers** are IEEE doubles. An operation whose result isn't finite (an overflow,
  `NaN`) gives `null`. `integer` is a kind of `number`: an `integer` value may go where a
  `number` is expected, not the reverse. A built-in format name equals its schema under type
  equality (chapter 2).
- **A nested field is data unless it `$ref`s a text format:** `verdict.verdict` (a
  `string` enum) is data; `verdict.feedback` (`$ref: plaintext`) is text.
- **Enums:** a literal compared with an enum-typed value (a `string` with `enum`, or `oneOf` of
  `const`) must be one of its values; `in` against a literal list checks each element. A literal
  compared with a `.title` must be one of the `oneOf`'s titles; `.title` on a plain `enum` is
  refused (chapter 2).
- **Unions:** a read of `.value` is allowed only if every member of the union has a value;
  `.value.<field>` only if every member declares that field compatibly.
- **`if`:** the branches must have one type. A `null` branch makes the result nullable.
- **`object`:** checked field by field against the computed node's format.
- **A computed node's result** must match its `format` (type equality, chapter 2). Its producer is
  `computed`, whatever it reads; where its value came from is the model-derived flag's job
  (§ 3.4.5), not its format's.
- **Reads must exist** at the site, with the visibility rules of chapter 1 and the per-site rules
  of § 3.4.

### 3.8 The printer

**One printer** turns JSON Logic into text for the Editor, History, the record's reason
sentences, the validator's sentences and the diagram's labels.
It writes ordinary infix, functions as `name(args)`, and strict equality as **`=`** and **`≠`**.
Its other rules: `and`, `or` and `not` as words; `≤` and `≥`; standard precedence, with
parentheses only where needed, so the printed text parses back to exactly the tree written.

| Rule | Printed |
|---|---|
| `{ "var": "a.b" }` | `a.b` |
| a string literal | JSON text: double quotes, JSON escapes (`"table"`) |
| a number | its RFC 8785 form (`65`, `0.5`) |
| `true`, `false`, `null` | `true`, `false`, `null` |
| an array | `[a, b, c]` |
| `===`, `!==` | `a = b`, `a ≠ b` |
| `<`, `>`, `<=`, `>=` | `a < b`, `a > b`, `a ≤ b`, `a ≥ b` |
| `in` | `a in b` |
| `and`, `or` | `a and b and c`, `a or b` |
| `!` | `not a` |
| `+`, `-`, `*`, `/`, `%` | infix; one-operand `-` as `-a` |
| `if` | `if c then a else b`; more pairs as `if c1 then a else if c2 then b else d` |
| `object` | `{ title: a, content: b }`, fields in written order |
| every other operation | `name(a, b)`: `size(input.prior_notes.value)`, `missing(["input.age.value"])` |

- **Precedence**, tightest first: function forms and literals; `not` and unary `-`;
  `*`, `/`, `%`; `+`, `-`; the comparisons and `in`; `and`; `or`; `if … then … else`.
- **Parentheses** only where needed to keep the tree: a child operation is parenthesised when its
  precedence is lower than **or equal to** its parent's (an `and` inside an `and` prints
  `(a and b) and c`, since a flat `and` of three is a different tree), so the printed text maps
  back to exactly one tree.
- **Spacing:** one space either side of an infix operator, `, ` between arguments, none inside
  brackets.
- **Byte-stable and versioned:** printed text is recorded (reasons, decisions), so the printer is
  versioned like a custom operation (any change to its output is a major version) and locked in
  `lock.json`'s `builtins` (chapter 7). The converter (chapter 10) parses its output back to the
  identical tree, and the conformance suite tests the round trip.
- **`.title` reads** print as written (`input.specialty.title = "Medical oncology"`); the record
  shows the raw value beside the title (§ 3.10).

**Reason sentences** are built from the printed condition:
*"skipped: input.kind.value = "table" is false"*.

### 3.9 The evaluator

- **The evaluator is `Corvus.Text.Json.JsonLogic` (Apache-2.0)**, pinned exactly and listed in
  `lock.json`.
  The research found version 5.8.11; the build pins the version current when it starts.
- **`requires.evaluator` names our evaluator's version,** not Corvus's: packages depend on our
  behaviour (the custom operations, the null rules, `===`/`!==` only), with Corvus underneath.
  Moving towards standard components, possibly including the evaluator, is [#1477](https://github.com/Consultologist/Consultologist-Blazor/issues/1477)
  (Milestone 40).
- **Behind our own interface** in `Consultologist.PackageFormat`: `IJsonLogicEvaluator`, with one implementation, `CorvusJsonLogicEvaluator`. The engine, the
  validator's probe, the Editor and the in-package tests (chapter 7) all evaluate through it.
- **Our custom operations** (§§ 3.5.2–3.5.5) are registered through Corvus's `IOperatorCompiler`.
- **Our null rules override Corvus's defaults** wherever they differ, by registering our own
  compilers for the affected built-ins (custom operators are checked before built-ins):
  `<`, `>`, `<=`, `>=`, the arithmetic, `min`, `max`, `in` and `cat`, per § 3.5.1's null column.
  Strict `===`/`!==` is standard and needs no override.
- **Refused operations are refused twice:** at publish by the checker, and at run time by the
  evaluator, which declines a rule naming any operation outside § 3.5, so a hand-edited
  or corrupted `resolve.json` can never fall through to Corvus's defaults.
- **Invariant culture**, always.
- **Compiled once:** each rule in a `resolve.json` is compiled to Corvus's cached delegate tree
  once per package version and cached.
- **A condition that yields no boolean at run time fails its node**, with the
  reason recorded: impossible after the checker, except through data that escaped validation; the
  node that owns the condition fails with § 3.11.3's sentence.
- **Eventually** json-everything's `JsonLogic`, paying its maintenance fee, is [#1458](https://github.com/Consultologist/Consultologist-Blazor/issues/1458) (no
  milestone); a swap must give byte-identical golden tests and corpus re-render.

### 3.10 What the record holds

The record's shape is chapter 8's. For expressions:

- **A decision for every condition**,
  in the job's one `decisions` list:
  its site, the printed condition, its result, a hash of each value it read, whether it was
  run-dependent and model-derived, and an `expressionHash` of its canonical JSON Logic. A
  condition reading `.title` is printed with both the raw value and the title.
- **A computed node's row:** the input hash (over the canonical expression and the values it
  read), the value as canonical JSON, the output hash (its producer is `computed`),
  `reproducible: true`, `modelDerived` (§ 3.4.5), and `runDependent` with the run-neutral hash of
  its recipe (§ 3.4.4).
- **`matches`:** the pattern (in the printed condition) and the result; never the matched text.
- **Run facts:** each one read, once per run, `run.date` with its time zone.
- **`lock.json`'s hash** (`lockHash`) ties every decision to the evaluator and operation
  versions that made it.

### 3.11 Refusals

Every sentence below is used as written; chapter 11 lists every sentence of this format.

#### 3.11.1 Refusals at publish

Placeholders: `<site>` names the declaration as its sentences do elsewhere: `Node 'x'`,
`Loop 'x'`, `While 'x'`, `Check 'x'`, `Deliverable 'x'`, `Macro 'x'`, `Part 'p' of node 'x'`,
`Computed node 'x'`, and inside a function
`Node 'x' in function 'f'`. `<member>` is `if`, `while`, `until` or `expression`. `<path>` is a
`var` path; `<format>` a format's type string (chapter 2).

| Sentence |
|---|
| *"\<site\> compares \<path\> (\<format\>) with a literal; text is tested by whether it is blank, its size, or in."* |
| *"\<site\> compares \<path\> (\<format\>) with \<path\> (\<format\>); text is tested by whether it is blank, its size, or in."* |
| *"\<site\> uses ==; equality is written === (shown as =)."* |
| *"\<site\> uses !=; inequality is written !== (shown as ≠)."* |
| *"\<site\> uses \<operation\>, which is not a JSON Logic operation of this format (\<the allowed list\>)."* |
| *"\<site\> uses substr; text is cut with trim or plain, and measured with size."* |
| *"\<site\> orders \<path\> (\<format\>); \<, \>, ≤ and ≥ compare numbers or dates."* |
| *"\<site\> tests \<path\> (\<format\>) with not; not takes a boolean — test text with blank."* |
| *"\<site\> gives \<operation\> \<n\> operands; it takes \<m\>."* |
| *"\<site\> writes \<operation\> with a bare operand; operands are written as an array."* |
| *"\<site\> reads var with a default; every read is one path."* |
| *"\<site\> reads \<path\>, a position in a list; lists are read whole, or by identity through .items."* |
| *"\<site\> reads \<path\>, which doesn't exist here."* |
| *"\<site\> reads input.\<id\>; an input is read as input.\<id\>.value, .content or .title."* |
| *"\<site\> reads \<path\>.title, but \<format\> is a plain enum with no titles; read .value, or give the format oneOf with const and title."* |
| *"\<site\> compares \<path\>.title with "\<text\>", which is not one of its titles (\<titles\>)."* |
| *"\<site\> reads profile.\<field\>; profile fields are read only in deliverable templates and macro bodies, never in conditions or computed expressions."* |
| *"\<site\> reads \<root\>.\<rest\>; JSON Logic reads input, node, check, item, pass, param and run."* (for `snippet`, `part`, `macro`, `renderer`, `deliverable`) |
| *"Deliverable '\<id\>' if reads node.\<id\>.content; a deliverable's if reads data (.value), not text."* |
| *"Deliverable '\<id\>' if reads check.\<id\>; a deliverable's existence can't depend on a check."* |
| *"Macro '\<id\>' if reads param.\<name\>; a macro's if is shared, so it can't depend on one function's parameter."* |
| *"\<site\> compares \<path\> with "\<value\>", which is not one of its values (\<values\>)."* |
| *"\<site\> reads \<path\>.value.\<field\>, which not every member of \<format\> declares."* |
| *"\<site\> \<member\> yields \<format\>; a condition yields a boolean."* |
| *"Computed node '\<id\>' yields \<format\>; it declares \<format\>."* |
| *"Computed node '\<id\>' builds \<format\> without \<field\>; object must give every property of the format."* |
| *"Computed node '\<id\>' builds \<format\> with \<field\>, which the format doesn't declare."* |
| *"\<site\> gives \<operation\> a computed \<operand\>; \<operand\> must be written as a literal."* |
| *"\<site\> gives count_pass a min of \<n\>; min is a whole number, 0 or more."* |
| *"\<site\> pattern "\<pattern\>" is not I-Regexp (RFC 9485): \<reason\>."* |
| *"\<site\> pattern "\<pattern\>" is \<n\> characters long; the most is 200."* |
| *"\<site\> pattern "\<pattern\>" repeats \<n\> times; a counted repetition is at most 100."* |
| *"\<site\> pattern "\<pattern\>" doesn't compile with the engine's options: \<reason\>."* |
| *"\<site\> reads \<path\>, which carries profile text; prompts, parts and conditions don't read profile text."* |
| *"\<site\> gives has_word a blank word; has_word finds one word or phrase."* |
| *"\<site\> uses if without an else; write the else."* |
| *"\<site\> cats \<path\> (\<format\>); convert Markdown with plain first."* |
| *"Node '\<id\>' declares \<modelDerived \| runDependent \| profileCarrying\> \<value\>, but its reads make it \<derived\>: \<the read that does, or none\>."* |

In the sentence about a computed operand, `<operand>` is `pattern`, `word`, `failWith` or `count_pass`'s `min`.

#### 3.11.2 Warnings at publish and in the Editor

- **Run-dependence**,
  one line per value or decision:
  *"\<site\> \<member\> reads run.\<fact\>; its decision can differ between runs with the same inputs."*
  and *"Computed node '\<id\>' reads \<run.fact or path\>, which is run-dependent; its value can differ between runs with the same inputs."*
- **Model-derived** is shown, not warned: History, the diagram and the Editor mark each
  model-derived value and decision (§ 3.4.5); the Editor shows:
  *"computed from model text: node.\<id\>"*.

#### 3.11.3 Failures at run time

The rules are in § 3.5.3 (text over 1 MiB fails the node), § 3.6.2 (evaluation never
throws) and § 3.9 (a condition that yields no boolean fails its node).

- *"\<site\> \<member\> could not be decided: matches was given \<n\> MiB of text; the most is 1 MiB."* The node that
  owns the condition fails, recorded with this reason.
- *"\<site\> \<member\> yields \<a value kind\>; a condition yields a boolean."* The node that owns
  the condition fails (§ 3.9).

## 4. Loops and functions

This chapter defines the flow nodes of version 31 (`for`, `while`, `if`, `case`) as folders with an
`index.json`, every member with its type and null rule; how a loop runs (`parallel`,
`maxParallel`, `until`, `max`), how it names its items (`itemLabel`), and how it is read from
outside (`.value`, `.items`, `.stopped`); the `FormatBounds` that limit them; and functions:
named, sealed sub-workflows in `functions/`, run by a `call` node with `with`. How loops and calls
count toward the per-job ceiling is stated here; the engine side is chapter 9. Conditions inside
these declarations are JSON Logic, defined in [chapter 3](#3-expressions); folders, ids and scopes
are [chapter 1](#1-files-and-scopes); formats are [chapter 2](#2-types-and-inputs).

### 4.1 Flow nodes are folders

A `for`, `while`, `if` or `case` is a folder, `nodes/…/<id>/`, described by its `index.json`.
The folder's children are the files and folders its `index.json` lists; a child listed
nowhere is a stray and is refused (chapter 1).

Each kind's `index.json` is judged by its schema:
[`flow-for`](v31/schemas/flow-for.schema.json), [`flow-while`](v31/schemas/flow-while.schema.json),
[`flow-if`](v31/schemas/flow-if.schema.json) and [`flow-case`](v31/schemas/flow-case.schema.json).

**Members every flow node's `index.json` has** (every member present, `null` only where stated):

| Member | Type | Null | Meaning |
|---|---|---|---|
| `kind` | `"for"` \| `"while"` \| `"if"` \| `"case"` | never | what the node is |
| `label` | string | **never** | the display name: the rail, History, the diagram |
| `description` | array of strings (lines) | `null` = none | for people only, at most 500 characters joined |
| `format` | a format name or an inline schema (chapter 2) | never | the node's return type, written, and checked against the type its `ret` gives it (§§ 4.2.5, 4.3.4, 4.5.3) by type equality; a mismatch is refused |
| `reproducible` | boolean | never | written, and checked against the derived value: `true` only if everything in its body that its result depends on is `true`; a mismatch is refused |
| `producer` | `"computed"` | never | written, and checked against the kind: a flow node is `computed` even when its body holds agent nodes; a mismatch is refused (chapter 2 § 1.3) |
| `modelDerived` | boolean | never | written, and checked against the derived value: `true` when its `ret`, or anything its result is made from, is model-derived, as when its body holds an agent node; a mismatch is refused (chapter 3 § 4.5) |
| `runDependent` | boolean | never | written, and checked against the derived value: `true` when its source or its `ret` is run-dependent (a condition passes no flag on, chapter 3 § 4.4); a mismatch is refused (chapter 3 § 4.4) |
| `profileCarrying` | boolean | never | written, and checked against the derived value: `true` when its source or its `ret` is profile-carrying; a mismatch is refused (chapter 3 § 4.6) |

Each kind adds its own members, below. A member of another kind is refused (§ 4.10).
Run-dependence, the model-derived flag and the profile-carrying flag are worked out from the body
(chapter 3 §§ 4.4–4.6), and written as `runDependent`, `modelDerived` and `profileCarrying`,
checked against those values.

**`ret` is the child's full name:** the root and the
qualified key of one of that body's **own** children, as the record keys it (chapter 1):
`"ret": "node.sections.paragraphs"` in `nodes/sections/index.json`,
`"ret": "node.sections.paragraphs.draft_paragraph"` in `nodes/sections/paragraphs/index.json`,
`"ret": "check.part_coverage.coverage"` in `checks/part_coverage/index.json` (a check loop).
Inside a function the key is counted from the function's root (`"ret": "node.apply_instructions"`).
The root says which namespace the child is in (`node.` or `check.`), and the whole name can be
read without knowing which folder the file sits in. The resolver checks that `ret` names a direct
child of that body and refuses anything else (§ 4.10). `ret` is the only member that takes this
qualified form: references elsewhere still resolve outward by bare id (chapter 1 § 9), and a
node's fields are always reached through `.value` or `.items`, so `node.sections.paragraphs` is
never read as a field path. (`example-nested-note`'s loop is called `sections`, because `parts` is a reserved id, chapter 1 § 6.)

### 4.2 `for`

#### 4.2.1 Members

| Member | Type | Null | Meaning |
|---|---|---|---|
| `in` | a reference string (§ 4.2.2) | never | the list the loop iterates |
| `parallel` | boolean | never | `true`: items run at the same time; `false`: one at a time, in list order |
| `maxParallel` | integer, 2 to `FormatBounds.parallel` (15) | `null` = no cap of its own | how many items run at once; must be `null` when `parallel` is `false` |
| `until` | a JSON Logic condition (chapter 3) | `null` = runs every item | stops after the item where it holds; non-null requires `"parallel": false` |
| `max` | integer, at least 1 | `null` = no cap | runs the first `max` items in list order |
| `itemLabel` | a field name (string) | `null` = position names | names each item (§ 4.2.7) |
| `nodes` | array of ids, at least one | never | the body, in order |
| `ret` | the child's full name (§ 4.1) | never | the body node whose value is each item's value |

Together with § 4.1's eight members, a `for`'s `index.json` has exactly sixteen members.

#### 4.2.2 What a loop iterates

`in` is a **reference string** naming a list, never a JSON Logic expression.
A list that has to be computed is a `computed` node, which `in` then names (compute, then name):

| Source | Example | Its items are known |
|---|---|---|
| an array input | `"input.sections.value"` | at start |
| a snippet folder | `"snippet.standards"` | at start: a folder's items have no `if`, so its size is its number of files (chapter 1; dynamic sizes are [#1468](https://github.com/Consultologist/Consultologist-Blazor/issues/1468)) |
| a list in a visible node's value | `"node.plan.value.sections"` | when that node completes, for this loop instance |
| a list field of the outer item | `"item.value.paragraphs"` | when the outer item is known |
| a loop's `.items` | `"node.sections.items"` | item by item, as each completes (§ 4.2.6) |
| inside a function, a parameter's list | `"param.sections.value"` | at the call |

- A node in an enclosing body is read by id and aligned on the common path:
  `"node.outline.value.points"` inside `sections` is *this* section's outline. A loop nests in a
  `for`'s or a `while`'s body, or in a branch, to any depth; a body may not hold the node that
  holds it.
- **Any loop may iterate `.items`**, a production loop as well as a check loop (chapter 6),
  with the same rules: for example to write one line per section, skipped sections included,
  each naming its state.
- The source must be typed as a list (a JSON Schema array). Item ids keep their source's form: array
  inputs 0-based, a node's list 1-based, folder items their file stems. No id holds `/` or `:`.
- **An item path** is the item ids from the outermost loop inward, joined by `/`. At one level a
  path is the item id; deeper, an item is `2/1` (`node.sections.paragraphs.draft_paragraph:2/1`).
- **One count per loop instance.** A loop instance is an inner loop under one outer path. Each
  instance settles its own count, once. An instance is *not yet known* until its outer item exists
  and its source has completed.

#### 4.2.3 `parallel` and `maxParallel`

- **`"parallel": true`** schedules every item at once, or at most `maxParallel` at a time; when
  one completes the next starts, in list order.
- **`"parallel": false`** runs the items one at a time, in list order; item *n*+1 starts when
  item *n* completes. It is the only form that allows `until`.
- **One way to say "one at a time":** `"parallel": true, "maxParallel": 1` is refused, pointing
  to `"parallel": false`.
  The Editor offers 2 and up (or "none") when `parallel` is on, and a loaded package holding 1
  shows the sentence with a one-click "Make sequential" fix.
- **Per loop instance:** an inner loop's cap applies within each outer item, so caps multiply
  across nesting (§ 4.8).
- **`maxParallel: null`** means the loop wants no cap of its own; it is limited only by the
  engine's per-job ceiling (§ 4.8). The package says how much parallelism a loop wants; the
  deployment decides how much it gets.

#### 4.2.4 `until`, `max` and `.stopped`

`until`, `max` and `.stopped`:

- **`until` is checked after each item**, over that item's body nodes by bare id, `item`, and
  anything that runs before the loop (chapter 3 § 4.2). The loop stops after the item where it
  holds, so which items ran is the same on every run.
- **The items it didn't run stay** in the loop's count and `.items`, with state `not_run` and
  the reason *"stopped early at \<position name\>"* (§ 4.2.6).
- **`max`** runs the first `max` items in list order; the rest are `not_run`, with the reason
  *"not run: beyond max \<n\>"*, and the loop's `.stopped` is `"bound"`.
- **`.stopped`** is `"until"` (its `until` held), `"bound"` (its `max` was reached) or `"end"` (it
  ran out of items), typed by those values.
- **An empty list** settles at 0 items, with `.stopped` `"end"`, never a failure. For an inner
  loop, that instance settles at zero items, with its reason, and the outer item still completes.
- **A `null` source** (a nullable list, or a read of a node that was skipped) settles the same
  way, at 0 items with `.stopped` `"end"`, and the loop's row records the reason
  *"0 items: \<reference\> is null"*.
- **At most 200 items per loop instance**: an engine setting, checked at run time. A
  list longer than that fails the loop's node with *"Loop '\<id\>' was given \<n\> items; this
  engine runs at most \<limit\> per loop."*, and publish notes a loop whose list could be longer
  (§ 4.10.2).

Example, fictional: reading prior letters in order until one answers the referral question.

```json
{ "kind": "for", "producer": "computed", "label": "Prior letters", "description": null,
  "format": { "type": "array", "items": { "$ref": "plaintext" } },
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "input.prior_letters.value",
  "parallel": false, "maxParallel": null,
  "until": { "===": [ { "var": "node.read_letter.value.answers_question" }, true ] },
  "max": null, "itemLabel": null,
  "nodes": ["read_letter", "letter_summary"], "ret": "node.letters.letter_summary" }
```

#### 4.2.5 Reading a loop from outside

| Member | Type | Means |
|---|---|---|
| `.value` | `list<T>`, `T` its `ret`'s format | the values of the items that **completed**, in item order |
| `.items` | a list of the element of § 4.2.6 | every item, in item order, each paired with its outputs by identity |
| `.content` | `markdown_block` | the standard rendering (`## <item name>`, then the item's text, joined by blank lines), so a reader of the loop gets one document (chapter 5) |
| `.state` | `"completed"` \| `"skipped"` \| `"not_run"` | the loop node's own state (inside an untaken branch, a loop is `skipped`) |
| `.stopped` | `"until"` \| `"bound"` \| `"end"` | § 4.2.4 |

- **A loop's `format`** is `list<T>`, in JSON Schema `{ "type": "array", "items": T }`;
  nested loops nest (`list<list<plaintext>>`).
- **`.value` holds completed items only.** Items that didn't run are absent, never `null`
  placeholders; they are seen, with their `state` and `reason`, through `.items`. `.value` stays a clean
  `list<T>` that templates and `all_pass` can read without a `null` test (chapter 3 § 5.4).
- **No zipping by position.** Pairing two lists by index isn't offered: an `if`, an `until` or a
  reordered `index.json` would put a heading over the wrong text. `.items` pairs by identity.

#### 4.2.6 `item` and the `.items` element

**Inside the body, `item`** is the innermost loop's current item; `item.parent` the enclosing
loop's, outward (`item.parent.parent`), skipping any `while` between. A paragraph reads its section's title as `item.parent.value.title`.

| Member | Type | Means |
|---|---|---|
| `item.id` | string | the item id (§ 4.2.2) |
| `item.value` | the source's element type | the element: a row, a folder item's header data, an element of a node's list |
| `item.content` | text | for a snippet folder item only: its body |
| `item.parent` | an item | the enclosing loop's item; refused in an outermost loop |

**Each element of `.items`:**

| Member | Type | Null | Means |
|---|---|---|---|
| `item` | an item, as above | never | the source element this row came from |
| `label` | string | never | the item's name (§ 4.2.7) |
| `state` | `"completed"` \| `"skipped"` \| `"not_run"` | never | the state of the item's `ret`, so an item whose `ret` is an untaken `if` is `skipped` |
| `reason` | string | `null` when completed | package text and fixed engine sentences only, never patient text: the printed condition for `skipped` (*"skipped: item.value.kind = "narrative" is false"*), *"stopped early at \<position name\>"* or *"not run: beyond max \<n\>"* for `not_run` |
| `value` | `T` | `null` unless completed | the `ret`'s value |
| `content` | text | `null` unless completed | the text of the item's `ret` |
| `nodes` | an object keyed by body id | never | each body node for this item: `.value`, `.content`, `.state` |

- **The states are a closed set.** A template that branches on `state` must handle every state
  or end with an `else` (chapter 5). `onInvalid` is `fail` or `retry`, so a failed item fails the
  job and never reaches a reader.
- **A loop over `.items`** (a check loop, or a production loop, § 4.2.2) has the element above as
  its `item`, so it reads `item.state`, `item.value` and `item.nodes.<id>` for the same item.
- **Check items share the production items' ids**, so `check.part_coverage.coverage:2` lines up
  with `node.sections:2`.

#### 4.2.7 `itemLabel`: naming items

- **`itemLabel` names a field of each element,** or is `null` for position names. It names items
  in the rail, progress, History and the record. `label` stays the loop's display name.
- **The field must be guaranteed** to be a non-null string on every element:
  - a node's list: listed in the element schema's `required` and typed a non-nullable `string`;
  - an array input: a required `string` property of each row (`example-conditional-sections` uses `title`);
  - a snippet folder: required in the folder's `format`. A folder item's header is typed data
    with no `if` (chapter 5); fields have no reserved names (chapter 2 § 5.3), so `test/general`'s
    field keeps its name `title` and its snippet loop writes `"itemLabel": "title"`;
  - a loop over `.items`: `"itemLabel": "label"`, the element's own `label`, which carries the
    production loop's item name; check loops name their items the same way.
- **At run time,** a value that is empty after trimming falls back to the position name, marked
  in the record.
- **Position names:** with `"itemLabel": null`, items are named `<loop label> <n>`, the loop's
  `label` and the 1-based position: *"Sections 2"*
  (the loop owns naming).
- **Retention:** a name is trimmed and cut to 120
  characters ending in "…", and is **kept in the record past the retention sweep only when it
  comes from package text** (a snippet folder's header). A name drawn from an input or a model's
  output follows 7-day retention, and History then shows the position name. **Reasons always use
  position names** (*"stopped early at Sections 3"*), never a drawn name, since a reason can land in
  a deliverable (chapter 6 § 6.2).
- **`labelField` is not a member;** chapter 10 covers the migration.

#### 4.2.8 Examples (migrated)

`example-nested-note`, `nodes/sections/index.json` and `nodes/sections/paragraphs/index.json`
(the loop is `sections`, chapter 1 § 6):

```json
{ "kind": "for", "producer": "computed", "label": "Sections", "description": null,
  "format": { "type": "array", "items": { "type": "array", "items": { "$ref": "plaintext" } } },
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "node.plan.value.sections",
  "parallel": true, "maxParallel": null, "until": null, "max": null,
  "itemLabel": "title",
  "nodes": ["outline", "paragraphs"], "ret": "node.sections.paragraphs" }
```

```json
{ "kind": "for", "producer": "computed", "label": "Paragraphs", "description": null,
  "format": { "type": "array", "items": { "$ref": "plaintext" } },
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "node.outline.value.points",
  "parallel": true, "maxParallel": null, "until": null, "max": null,
  "itemLabel": null,
  "nodes": ["draft_paragraph"], "ret": "node.sections.paragraphs.draft_paragraph" }
```

`example-conditional-sections`, `nodes/sections_draft/index.json`:

```json
{ "kind": "for", "producer": "computed", "label": "Sections — drafting each requested section by its kind", "description": null,
  "format": { "type": "array", "items": { "$ref": "plaintext" } },
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "input.sections.value",
  "parallel": true, "maxParallel": null, "until": null, "max": null,
  "itemLabel": "title",
  "nodes": ["route"], "ret": "node.sections_draft.route" }
```

`test/general`, `nodes/standards/index.json`:

```json
{ "kind": "for", "producer": "computed", "label": "Standards", "description": null,
  "format": { "type": "array", "items": { "$ref": "plaintext" } },
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "snippet.standards",
  "parallel": true, "maxParallel": null, "until": null, "max": null,
  "itemLabel": "title",
  "nodes": ["section_instructions", "patient_section_draft", "standard_section_draft"],
  "ret": "node.standards.section_instructions" }
```

Every loop writes every member of its kind, `null` for each one it does not use. How the migration writes them is chapter 10.

### 4.3 `while`

#### 4.3.1 Members

| Member | Type | Null | Meaning |
|---|---|---|---|
| `while` | a JSON Logic condition | never | the check; the body runs again while it holds |
| `max` | integer, 1 to `FormatBounds.passes` (15) | never | the bound; there is no default |
| `until` | a JSON Logic condition | `null` = none | checked after each pass; whichever of `while` and `until` stops first wins |
| `checkFirst` | boolean | never | `false`: the check runs after each pass (at least one pass); `true`: before each pass (zero passes possible) |
| `nodes` | array of ids, at least one | never | the body, in order |
| `ret` | the child's full name (§ 4.1) | never | the body node whose last pass's value the while returns |

With § 4.1's eight members, a `while`'s `index.json` has fourteen members. A `while` has no `parallel`,
`maxParallel` or `itemLabel`: it is sequential by definition and its passes are numbered.
`checkFirst` is required.

#### 4.3.2 How it runs

A `while` runs as follows:
- the body runs, then again for as long as `while` holds and `until` doesn't, at most `max`
  passes;
- **reaching the bound is a named state**: *"stopped at its bound of 3; the check never stopped
  holding"*; the run continues with the last pass's output;
- with `checkFirst: true` and a check that fails at once, zero passes run: `.passes` is 0,
  `.stopped` is `"check"`, and the returned node reads as skipped.

#### 4.3.3 What a pass reads

A pass is an object with one shape everywhere: `pass`, `pass.previous`, `pass.parent` and each
element of `pass.history` have `.number` (from 1), `.node.<id>`, `.previous`, `.parent` and
`.history`. In JSON Logic:

| Read | Means | Dependency edge |
|---|---|---|
| `node.judge` or `pass.node.judge` | this pass's node | yes |
| `pass.number` | this pass's number, from 1 | no |
| `pass.previous.node.judge` | one pass back; `null` on the first pass | no |
| `pass.parent.number` | the enclosing while's pass, skipping any `for` between | this pass: yes |
| `pass.history` | every earlier pass, oldest first | no |

In conditions, `pass.history` is readable only through `size`; templates may loop over it
(chapter 5)
(positional reads are refused, chapter 3 § 2.2).

`pass.….node.<id>` names a node under that pass's `while` at any depth. Reading an earlier pass
adds no dependency edge, so a redraft and its judge form no cycle.

#### 4.3.4 Reading a while from outside

`.value` and `.content` are the last pass's `ret`; `.passes` is the pass count; `.stopped` is
`"check"`, `"until"` or `"bound"`; `.history` is every pass, each element giving `.number` and `.node.<id>` for the `while`'s direct body nodes, in pass order; `.state` as § 4.2.5. A
`while`'s `format` is exactly its `ret`'s.

#### 4.3.5 Example (migrated)

`example-nested-note`, `nodes/refine/index.json`, from `node.judge.value.verdict != "good"`:

```json
{ "kind": "while", "producer": "computed", "label": "Refining the summary", "description": null,
  "format": "plaintext",
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "while": { "!==": [ { "var": "node.judge.value.verdict" }, "good" ] },
  "max": 3, "until": null, "checkFirst": false,
  "nodes": ["draft_summary", "judge"], "ret": "node.refine.draft_summary" }
```

Printed: `node.judge.value.verdict ≠ "good"`. `verdict` is a `string` with an enum, so it is data
and strict equality applies; `"good"` is checked against the enum.

### 4.4 Reading across levels

The scope rules of chapter 1 § 9 hold:

- A body node reads its siblings, the nodes of the bodies that enclose it (aligned by path), and
  the top level. `node.x` resolves outward; nothing is resolved by "nearest wins".
- **A node inside a body is a list from outside it**: read the loop (`node.paragraphs`), never
  its body node.
- **Siblings across instances are not readable:** `node.draft_paragraph` always aligns to the
  reader's own path.
- Inside a function, resolution stops at the function's root (§ 4.7.4).

**The contagious flags cross levels too** (chapter 3 §§ 4.4–4.6). Run-dependence, the model-derived flag and the profile-carrying flag pass
into a loop's items when its source has them, out through a flow node's `ret`, and through a
call's arguments and result. A condition (an `if`, a `case` subject, a `while`, an `until`)
passes none of them on to what it chooses.

- **The output of every node whose `producer` isn't `computed` is model-derived,** so every
  agent node's output is; the reverse doesn't hold (§ 4.7.10's pattern B is a computed
  `judgement` that is model-derived).
- **An input element from a previous run's deliverable** starts out model-derived, and the
  record links to the job it came from. In a mixed array input, only those elements are; typed
  text and uploaded documents start clean. Other machine sources (OCR, transcription) are
  producers reserved for Milestone 40 (`extracted`; chapter 2 § 1.3).

### 4.5 Branches: `if` and `case`

#### 4.5.1 `if`

| Member | Type | Null | Meaning |
|---|---|---|---|
| `if` | a JSON Logic condition | never | the decision |
| `then` | a body: `{ "nodes": [ids], "ret": full name }` | never | runs when the condition holds |
| `else` | a body | `null` = no else | runs when it doesn't |

With § 4.1's eight members, eleven members. A body object has exactly `nodes` (at least one id) and
`ret`.

#### 4.5.2 `case`

| Member | Type | Null | Meaning |
|---|---|---|---|
| `case` | a reference string | never | the subject |
| `branches` | array, at least one, of `{ "when": [values], "nodes": [ids], "ret": full name }`; an empty branch writes `"nodes": []` and `"ret": null` | never | one branch per set of values |
| `else` | a body | `null` only when the branches list every value and the subject can't be `null` | runs when no branch's values match, and when the subject is `null` |

With § 4.1's eight members, eleven members.

- **The subject** is a reference string, never a JSON Logic expression (chapter 3 § 3); a subject
  that has to be computed is a `computed` node the `case` names. It must be typed as an
  enumerated `string`: `enum`, or `oneOf` with `const` (chapter 2):
  `"item.value.kind"`, `"node.triage.value.category"`, `"input.encounter_kind.value"`.
- **Each `when` lists one or more values** of the subject's enum (the raw values, never titles);
  a value may appear in at most one branch, once.
- **Every `case` is exhaustive:** if the branches don't list every value, an `else` is required,
  and publish refuses a `case` that could match nothing. A `case` therefore always runs a
  branch for every value.
- **A subject that can be `null`** (a nullable enum, chapter 2 § 3.2, or a read of a node that may
  be skipped) **requires an `else`**, and `null` goes there. A `when` never lists `null`.
- **A branch may be explicitly empty:** `{ "when": ["omit"], "nodes": [], "ret": null }`, the one
  body whose `nodes` is empty and whose `ret` is `null`, both together. For those values the `case`
  reads as skipped, with the reason *"case '<id>': arm for <value> does nothing"*. So skipping some values is written in the `case` itself, never as an `if`
  around it (§ 4.5.4).

#### 4.5.3 Format, state and exhaustiveness

- **The format of an `if` or `case` is the union of what its bodies return**
  (`plaintext | classification`; in JSON Schema `anyOf`). Each body's `ret` must be a
  member, and each member returned by some body. When every body returns one
  format, the union is that format. The `anyOf` is the result itself, with no wrapper object,
  and the condition's row records which branch ran
  (chapter 2 § 3.3).
- **A reader of a union:** `.content` always; `.value` only if every member has a value;
  `.value.<field>` only if every member declares it compatibly.
- **An untaken `if` with no `else`,** and a `case` whose subject took an empty branch, have state
  `skipped`; their `.value` and `.content` read as `null` in JSON Logic (chapter 3 § 6.1). Skipped is
  a state, not a union member, so an empty branch adds nothing to the union.
- **Exhaustive** means every value of the subject has a branch, or an `else`, which every `case`
  is (§ 4.5.2). **Always runs a body** is stronger: an `if` with an `else`, or a `case` with no
  empty branch. An `if` with no `else`, or a `case` with an empty branch, is allowed except where
  a value must always exist: a function's `ret` (§ 4.7.6).
- **The decision is recorded** in the job's `decisions` list with the printed condition (or the
  subject and the branch taken), its run-dependence and whether it is model-derived (chapter 8).

#### 4.5.4 Examples (migrated)

`example-conditional-sections`. The input's `kind` enum is `narrative`, `table`, `omit`. `route`
is a `case` with a branch for `narrative`, one for `table` and an explicitly empty one for `omit`,
so every value is listed and no `else` is needed.

`nodes/sections_draft/route/index.json`:

```json
{ "kind": "case", "producer": "computed", "label": "Routing a section by its kind", "description": null,
  "format": "plaintext",
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "case": "item.value.kind",
  "branches": [
    { "when": ["narrative"], "nodes": ["narrative_draft"], "ret": "node.sections_draft.route.narrative_draft" },
    { "when": ["table"],     "nodes": ["table_draft"],     "ret": "node.sections_draft.route.table_draft" },
    { "when": ["omit"],      "nodes": [],                  "ret": null } ],
  "else": null }
```

An omitted section's `route` reads as skipped, with the reason *"case 'route': arm for omit does
nothing"*.

`nodes/patient_summaries/narrative_only/index.json`:

```json
{ "kind": "if", "producer": "computed", "label": "Narrative sections only", "description": null,
  "format": "plaintext",
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "if": { "===": [ { "var": "item.value.kind" }, "narrative" ] },
  "then": { "nodes": ["patient_summary"], "ret": "node.patient_summaries.narrative_only.patient_summary" },
  "else": null }
```

`nodes/standing_sections/applies/index.json`:

```json
{ "kind": "if", "producer": "computed", "label": "Holding the billing section back unless asked", "description": null,
  "format": "plaintext",
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "if": { "or": [ { "!==": [ { "var": "item.id" }, "billing" ] },
                  { "===": [ { "var": "input.include_billing.value" }, true ] } ] },
  "then": { "nodes": ["standing_draft"], "ret": "node.standing_sections.applies.standing_draft" },
  "else": null }
```

When a fictional section "Billing" is skipped, its reason reads *"skipped: item.id ≠ "billing"
or input.include_billing.value = true is false"*.

### 4.6 `FormatBounds`

| Member | Value | Limits |
|---|---|---|
| `passes` | 15 | a `while`'s `max`: 1 to 15 |
| `depth` | 15 | nested function calls: 0 to 15 (§ 4.7.8) |
| `parallel` | 15 | a loop's `maxParallel`: 2 to 15, or `null` |

- **Constants of the format,** defined in the spec and in `Consultologist.PackageFormat`, covered
  by the dialect version, and **never written in a package**.
- **Each can be raised alone later,** which is always compatible; lowering one would break
  packages.
- **Messages name the limit** (§ 4.10).
- A `for`'s `max` has no format bound: at least 1, no cap.

### 4.7 Functions

A function is a **named, reusable sub-workflow**: a group of nodes behind declared, typed inputs
and one typed result, run by a `call` node from anywhere.
Functions are within a package; imports from other packages are [#1420](https://github.com/Consultologist/Consultologist-Blazor/issues/1420) (Milestone 40).

#### 4.7.1 The definition folder

```
functions/
  index.json                     (the folder's own index: chapter 1)
  draft_section/
    index.json                   (the definition, § 4.7.2)
    standard_draft.md
    patient_draft.md
    apply_instructions.md
    snippets/ formats/ renderers/ macros/     (always present, each with its index.json: its own definitions, § 4.7.3)
```

- **`functions/<id>/`** holds one function; the folder name is its id.
- **Its nodes are its direct children** (files and flow folders), listed in `nodes` as in any
  body.
- **Its own definitions** live in sub-folders shaped like a package's. `snippets/`, `macros/`,
  `formats/` and `renderers/` are **always present**, each with its `index.json`, even when empty
  (`"items": []`), so an empty folder says visibly that the function defines nothing there.
  Their names can't collide with a node's id: `snippet(s)`, `macro(s)`, `format(s)` and
  `renderer(s)` are reserved ids everywhere (chapter 1).
- **Function ids are their own namespace,** named only by a `call`'s `function`, never by
  `node.x`; a function and a node may share an id. Function ids are unique among functions.

#### 4.7.2 `functions/<id>/index.json`

Judged by [`v31/schemas/function-index.schema.json`](v31/schemas/function-index.schema.json).

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | never | the display name |
| `description` | array of strings | `null` = none | for people only |
| `inputs` | an object keyed by parameter id (§ 4.7.2.1) | never (`{}` = no parameters) | the parameters, in written order |
| `uses` | `{ "snippets", "macros", "formats", "renderers" }`, each an array of ids | never; `[]` = none | the package definitions it uses (§ 4.7.3) |
| `nodes` | array of ids, at least one | never | its top-level body, in order |
| `ret` | the child's full name, counted from the function's root (§ 4.1) | never | the body node it returns (§ 4.7.6) |
| `format` | a format name or inline schema | never | the function's result type; must equal its `ret`'s format |

##### 4.7.2.1 Parameters: typed, and all required

Each member of `inputs` is:

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | never | shown in the Editor and History |
| `description` | array of strings | `null` = none | for people only |
| `format` | a format name or inline schema | never | the parameter's type |

- **Parameters are `{ label, description, format }`, all three required**:
  the package inputs' shape without `required` and `channel`. `description` follows
  chapter 1's one rule (lines or `null`, at most 500 code points). **Every parameter is required:**
  a call passes every one (§ 4.7.7); `required` would always be true, and `channel` concerns how a
  person supplies an input, which a call never does.
- **A parameter that may be empty** declares a nullable format, and the caller passes `null`
  explicitly for an optional value; a parameter is never left out. `null` is written as the
  argument itself (`"with": { "prior_letter": null }`), the one literal `with` accepts (§ 4.7.7).
- **Read as `param.<id>`,** with `.value` and `.content` as for a node.

#### 4.7.3 `uses`: declared definitions

- A function may use the package's snippets, macros, formats and renderers **only if it lists
  them** in `uses`, and may hold its own (§ 4.7.1).
- **Built-in formats** (the package-format registry's) and **catalogue formats**
  (`concept_list`, `classification`, …) are always available without listing.
- **A snippet passed as data** (`"with": { "standard": "snippet.standards.hpi" }`) is an
  argument, read as `param.standard`, and isn't listed. **A snippet a prompt places as text**
  (`{{~ snippet.snomed_tool_guidance.content }}`) is a definition and is listed.
- **No shadowing:** a function's own definition may not share an id with one it lists in `uses`.
- **A listed definition never used** is a warning, not a refusal.

#### 4.7.4 Sealed: what a function reads

Inside a function, every template, condition and computed expression may read:
- **`param.<id>`**, its parameters;
- **`node.<id>`** for nodes inside the function, at any depth within it, resolved outward only up
  to the function's root;
- `item` and `pass` of loops and whiles **inside** the function;
- its own and its listed definitions (`snippet.*`, `macro.*`, `renderer.*`, `part.*` of its own
  nodes).

**Refused inside a function:** `input.*`; nodes outside it; a caller's `item` or `pass`;
`run.*` and `profile.*` read directly (pass them in, § 4.7.7); `check.*`; `deliverable.*`.

So everything a function uses is visible at the call site: data through `with`, definitions
through `uses`. A function's result depends only on its arguments, which makes it testable alone
(chapter 7).

#### 4.7.5 What a function may contain

- **Allowed:** every kind a package's `nodes/` may hold: `agent`, `rendered`, `computed`, `for`,
  `while`, `if`, `case`, and `call` (of **other** functions); parts and macros (§ 4.7.10).
- **Refused:**
  - **recursion,** direct or through other functions: the checker builds the call graph at
    publish and refuses any cycle;
  - **deliverables:** top-level and terminal; a function returns a value and a top-level
    deliverable composes it;
  - **checks:** checks gate releases and functions release nothing. A function may compute a
    `check_result` **as data** (a `computed` node with `terms_subset`) and return it. Checking
    each call's output is a check loop over the calls' `.items` (chapter 6).

#### 4.7.6 One `ret`, always valued, one format

- **`ret` names one node** of the function's top-level body. The function's `format` is that
  node's format, checked at publish.
- **`ret` must always have a value:** a node that always runs; or an `if` with an `else`; or a
  `case` with no empty branch (§§ 4.5.2–4.5.3). A `ret` that may be skipped is refused.
- **One format:** when `ret` is an `if` or `case`, every body must return the **same** format;
  no unions as function results. A function that returns different shapes wraps them in an
  object format, built by a closing computed node on each body.
- **Several values** are one object format, built by a closing computed node with `object`:

  ```
  ---
  { "kind": "computed", "producer": "computed", "label": "Result", "format": "drafted_section",
    "modelDerived": true, "runDependent": false, "profileCarrying": false,
    "expression": { "object": {
        "title":    { "var": "param.standard.value.title" },
        "text":     { "var": "node.apply_instructions.content" },
        "concepts": { "var": "node.extract.value" } } } }
  ---
  ```

  (other leaf members as chapter 1). `text` is text through the nested-text rule (chapter 2 § 5.3), and the
  result is model-derived, since it is built from agents' output (chapter 3 § 4.5).
- **A loop as `ret`** is allowed; the function returns `list<…>`.
- **`.content` of an object result** is its canonical JSON, as for any object-valued node.

#### 4.7.7 The `call` node

A `call` is a leaf, `<id>.md`, **header only** (its body must be empty), judged by
[`v31/schemas/node-call.schema.json`](v31/schemas/node-call.schema.json). Its members, besides
chapter 1's leaf members (`kind`, `label`, `description`, `format`, `reproducible`, `modelDerived`,
`runDependent`, `profileCarrying`, and the node's own condition, `if`):

| Member | Type | Null | Meaning |
|---|---|---|---|
| `kind` | `"call"` | never | |
| `format` | a format name or inline schema | never | written, as on every node, and equal to the function's `format` by type equality |
| `reproducible` | boolean | never | written, and checked against the function's `ret`'s value; a mismatch is refused |
| `modelDerived` | boolean | never | written, and checked against the derived value: `true` when the function's `ret` is model-derived, or an argument is; a mismatch is refused |
| `runDependent` | boolean | never | written, and checked against the derived value: `true` when the function's `ret` is run-dependent, or an argument is; a mismatch is refused |
| `profileCarrying` | boolean | never | written, and checked against the derived value: `true` when the function's `ret` is profile-carrying, or an argument is; a mismatch is refused |
| `function` | a function id | never | the function to run |
| `with` | an object keyed by parameter id; each value a reference string, or the literal `null` | never (`{}` for a function with no parameters) | the arguments |

- **`with` names every parameter, and only those.** A missing or extra parameter is refused.
- **Each argument is a reference string,** as `in` is, never a JSON Logic expression:
  `input.<id>.value`, `.content` or `.title` (a bare `input.<id>` is refused, chapter 2),
  `node.<id>`, `check.<id>`, `item`, `item.parent`, `snippet.<folder>.<item>`, `param.<id>`
  (inside a function), `run.<fact>`, `profile.<field>` (see below), or a field path under one of
  these (`node.plan.value.sections`). The literal `null` is the one literal (§ 4.7.2.1): a constant or
  computed argument is a `computed` node that the argument names (compute, then name).
- **Each argument is type-checked** against its parameter's format at publish.
- **`profile.*` may be passed in through `with`** (`"with": { "signature": "profile.signature" }`),
  and then only to reach deliverables and macro bodies. The parameter
  **carries the profile's restriction** through the function: reading it in a prompt, a part or a
  condition is refused (chapter 6 § 10.2, R-F3), and it may be read in a macro body or passed on
  through `with`.
- **`run.*` may be passed in:** `"with": { "today": "run.date" }`. The parameter is then
  run-dependent (chapter 3 § 4.4). In the same way, a parameter bound to a model-derived argument
  is model-derived (chapter 3 § 4.5).
- **Its value is the function's `ret`,** read like any node (`node.hpi_section.value`,
  `.content`).
- **A whole reference passed to `with`** (`node.<id>`, `item`, `check.<id>`) gives the function
  only its `.value` and `.content`, typed against the parameter's format; the function
  reads `param.<id>.value` and `.content`, never the caller's `.state` or `.items`.
- **Its body runs inline** in the caller's orchestration, never as a sub-orchestration: the call's inner nodes are scheduled by the same orchestrator as its siblings, so the
  per-job ceiling, the call limit and the start order hold inside functions (§ 4.8; chapter 9 § 3).
- **Its dependency edges are its arguments.** A call's input hashes are exactly its arguments'
  hashes.

Inside a loop, one call per item:

```json
{ "kind": "for", "producer": "computed", "label": "Standards", "description": null,
  "format": { "type": "array", "items": { "$ref": "plaintext" } },
  "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "snippet.standards",
  "parallel": true, "maxParallel": 4, "until": null, "max": null,
  "itemLabel": "title",
  "nodes": ["section"], "ret": "node.standards.section" }
```

```jsonc
// nodes/standards/section.md (header only)
---
{ "kind": "call", "producer": "computed", "label": "Drafting the section", "description": null,
  "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "function": "draft_section",
  "with": { "standard": "item", "draft": "input.consult_draft.content" } }
  // plus chapter 1's remaining leaf members
---
```

Loop bodies stay inline and anonymous; a function is the named, reusable form, and a `call` is
the one way to run it, at the top level, in a loop body or inside another function.

#### 4.7.8 Depth and recursion

- **Recursion is refused** at publish, so nesting is already finite; the bound is about
  readability and cost.
- **Depth is measured,** not written: the deepest chain of nested calls, from a top-level node,
  against `FormatBounds.depth` (15).
- **Counting**:
  a `call` outside every function is at depth 0; a `call` inside a function reached at depth *d*
  is at depth *d*+1. "0 means no nested calls" then holds, and `FormatBounds.depth` 15 allows
  sixteen function frames on one chain.

#### 4.7.9 Ids and record keys

- **Ids inside a function are free:** a function may use any node id, even one at the package's
  top level or in another function. Within the function, the disjoint-scope rules of chapter 1 § 9.2 apply.
- **Record keys go through the call node,** joined with `.` and written with their root
  (chapter 1 § 9.3); the function's name is recorded on the call's row, not in the key:

  | Where | Key |
  |---|---|
  | a top-level call | `node.hpi_section` |
  | its inner node | `node.hpi_section.standard_draft` |
  | a call inside a loop, item 3 | `node.standards.section.standard_draft:3` |
  | a nested call | `node.hpi_section.refine_call.judge` |

#### 4.7.10 Macros inside functions

- A function places a macro only if it lists it in `uses` or holds its own.
- **A macro's `if` is evaluated where the macro is placed,** in the function's sealed scope;
  the checker verifies every name it reads exists there. A macro folder's shared `if` is
  evaluated in the same scope. The decision is recorded within the call.
- **Pattern A (the default):** the function holds its own classifier with the id the macro's
  `if` reads, so each call decides on its own arguments.
- **Pattern B (the decision is made once):** the caller decides, passes the answer in, and a computed node
  inside the function, with the classifier's id, holds it:

  ```
  ---
  { "kind": "computed", "producer": "computed", "label": "Prescribes letrozole (passed in)", "format": "judgement",
    "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false,
    "expression": { "var": "param.letrozole.value" } }
  ---
  ```

  saved as `functions/draft_section/prescribes_letrozole.md`. **Pattern B needs no exception**:
  the computed node returns `judgement`, the same format the classifier returns, with producer `computed`; its expression passes the parameter's value
  through, so the parameter is a `judgement` too, and the macro's `if` reads
  `node.prescribes_letrozole.value.answer` under either pattern. It is
  **model-derived** (chapter 3 § 4.5), because the caller's classifier, an agent, wrote the
  answer. Where the value came from is carried by the flag, not the format, so the macro's
  decision is shown as model-derived in History, as it is under pattern A.
- **A macro's `if` naming a parameter is refused** (chapter 3 § 4.2).

#### 4.7.11 Example: a made-up package

`example-functions` is made up for this document; the patient is fictional (Margaret Okafor).

```
example-functions/
  manifest.json            identity, and inputs: consult_draft (markdown_block)
  snippets/
    index.json
    standards/             index.json (format standard_section), hpi.md, plan.md, …
  formats/                 index.json, standard_section.json
  renderers/               index.json ("items": [])
  macros/                  index.json ("items": [])
  functions/
    index.json
    draft_section/
      index.json           inputs: standard (standard_section), draft (markdown_block)
      standard_draft.md    agent · plaintext
      patient_draft.md     agent · plaintext
      apply_instructions.md agent · plaintext
      snippets/ macros/ formats/ renderers/    each index.json ("items": [])
  nodes/
    index.json             items: standards, extract_input_terms
    standards/
      index.json           for … in snippet.standards, maxParallel 4, itemLabel "title"
      section.md           call draft_section, with standard ← item, draft ← input.consult_draft.content
    extract_input_terms.md agent · concept_list
  checks/
    index.json
    section_coverage/
      index.json           for … in node.standards.items, itemLabel "label"
      coverage.md          computed · check_result (terms_subset per section)
    all_sections.md        computed · check_result (all_pass)
  deliverables/
    index.json
    emr/
      consult.md           check: check.all_sections
  tests/                   index.json, and the package's tests
```

All nine top-level folders are present, each with its `index.json`, and the function's four
definition folders likewise, empty ones included (chapter 1).

`functions/draft_section/index.json`:

```json
{ "label": "Draft a section",
  "description": ["Drafts one consult section from a standard, then applies the patient's facts."],
  "inputs": {
    "standard": { "label": "Standard", "description": null, "format": "standard_section" },
    "draft":    { "label": "Consult draft", "description": null, "format": "markdown_block" } },
  "uses": { "snippets": [], "macros": [], "formats": ["standard_section"], "renderers": [] },
  "nodes": ["standard_draft", "patient_draft", "apply_instructions"],
  "ret": "node.apply_instructions",
  "format": "plaintext" }
```

`checks/section_coverage/index.json` (check loops are chapter 6's; shown for `.items`):

```json
{ "kind": "for", "producer": "computed", "label": "Section coverage", "description": null,
  "format": { "type": "array", "items": { "$ref": "check_result" } },
  "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "node.standards.items",
  "parallel": true, "maxParallel": null, "until": null, "max": null,
  "itemLabel": "label",
  "nodes": ["coverage"], "ret": "check.section_coverage.coverage" }
```

Its `coverage` check's `if` skips sections that didn't complete:
`{ "===": [ { "var": "item.state" }, "completed" ] }`. `checks/all_sections.md`'s expression:
`{ "all_pass": [ { "var": "check.section_coverage.items" }, "Not every section covers its planned terms." ] }`.

The record's keys for the third standard: `node.standards.section:3` (the call),
`node.standards.section.patient_draft:3`; and `check.section_coverage.coverage:3`, which shares
the production item's id (chapter 6). The deliverable is `deliverable.emr.consult`.

### 4.8 Concurrency: what counts toward the per-job ceiling

- **The ceiling is not in the format.** The engine holds a per-job ceiling: at most *N* agent
  calls in flight for one job (for example 16). It is chapter 9's. Function bodies run inline in
  the job's orchestration, so their calls are scheduled under the same ceiling.
- **Everything counts the same way:** agent calls in nested loops, inside function calls (at any
  depth), and in check loops.
  **Only agent calls count:** `rendered` and `computed` nodes make no model call and don't
  count.
- **Total-work limits**, engine settings beside the ceiling, starting at: **200 items
  per loop instance** (§ 4.2.4), **500 agent calls per job** (retries included as one call), and a
  **step budget per render**, starting at **100,000 steps** (chapter 5). Each is checked at run time and fails the job, or the
  node, with a sentence (chapter 9 § 3.4); publish notes a package whose worst case can exceed one
  (§ 4.10.2).
- **Each loop's `maxParallel` still applies within it.** The effective concurrency at a point is
  the smaller of the ceiling and the product of the caps along its nesting path.
- **429 responses and other service failures** are retried with back-off and recorded as retries
  on the node's row. A node fails after 10 minutes of waiting on 429s in total, or after 5
  attempts for another failure, and a job fails if it hasn't finished 30 minutes after its
  orchestration started;
  all three are engine settings (chapter 9 § 3.4).
- **At publish, a note rather than a refusal** when nested caps multiply past the engine's
  ceiling (§ 4.10.2). The product is taken along each nesting path of loops and calls. For the
  note's worst case, a `maxParallel: null` loop over a list whose length publish knows (a
  snippet folder) counts its length, and over any other list counts as unbounded, which the note
  says. Requiring a non-null `maxParallel` is [#1474](https://github.com/Consultologist/Consultologist-Blazor/issues/1474) (Milestone 40).

### 4.9 What the record holds

The record is chapter 8's. For flow and functions (storage 12 adds to 11, with qualified keys):
- **loop rows** carry `parallel`, `maxParallel`, `itemLabel`'s field, the count, `.stopped` and
  its reason; one loop-instance row per inner instance;
- **item rows** keyed by their key with its root and path (`node.sections:2`), named per § 4.2.7,
  with state and reason;
- **pass rows** for a `while`, its `passes` and `stopped`;
- **a decision** in the job's one `decisions` list for every `if`, `case`, `while`, `until` and
  item condition: its site, the printed condition (or the subject and the branch taken), its
  result, a hash of each value read, whether it was run-dependent, and an `expressionHash`;
  rows link to their decisions by id;
- **a call row** with the function's id, its arguments' hashes, its result's hash and its
  `depth`, expanding to its inner rows like a loop item;
- **`modelDerived`, `runDependent` and `profileCarrying`** on every row (chapter 3 §§ 4.4–4.6).

### 4.10 Refusals

Every sentence below is used as written; chapter 11 lists every sentence of this format.

#### 4.10.1 Refusals at publish

Placeholders: `<id>` a node, loop, function or call id; `<n>`, `<m>` numbers; `<format>` a type
string (chapter 2).

**Every flow node**

| Sentence |
|---|
| *"Loop '\<id\>' declares label null; a loop's or branch's label is what the rail, History and the diagram show: write one."* (also `While`, `If`, `Case`) |
| *"\<Kind\> '\<id\>' declares \<member\>, which belongs to \<a for \| a while \| an if \| a case\>."* |
| *"\<subject\> returns nothing; name the body node the outside reads with ret."* (`ret` null) |
| *"\<subject\> returns \<ret\>, which is not one of its own children (\<full names\>): write the child's full name, for example node.sections.paragraphs."* |
| *"\<subject\> lists node '\<id\>' twice; a body is a set."* |
| *"\<Kind\> '\<id\>' declares format \<format\>; its ret makes it \<format\>."* |
| *"\<Kind\> '\<id\>' declares reproducible \<true \| false\>; its body makes it \<false \| true\>."* (also `Call`) |
| *"\<Kind\> '\<id\>' declares \<modelDerived \| runDependent \| profileCarrying\> \<true \| false\>; its body makes it \<false \| true\>."* (also `Call`) |
| *"\<Kind\> '\<id\>' \<in \| case \| with \<param\>\> is an expression; it names one readable thing: compute the value in a computed node and name that."* |

`<subject>` is `Loop 'x'`, `While 'x'`, `If 'x' then`, `If 'x' else`, `Case 'x' branch <n>`,
`Case 'x' else`, or `Function 'x'`.

**`for`**

| Sentence |
|---|
| *"Loop '\<id\>' has no body; name the nodes that run per item in nodes."* |
| *"Loop '\<id\>' declares parallel true with maxParallel 1, which runs one item at a time; declare "parallel": false and "maxParallel": null instead."* |
| *"Loop '\<id\>' declares maxParallel \<n\>; the most is FormatBounds.parallel (15)."* |
| *"Loop '\<id\>' declares maxParallel \<n\>; the least is 2, or null for no cap of its own."* (0, negative, not an integer) |
| *"Loop '\<id\>' declares maxParallel \<n\> with parallel false; a sequential loop runs one item at a time: write "maxParallel": null."* |
| *"Loop '\<id\>' declares until with parallel true; until stops after the item where it holds, which needs items in order: declare "parallel": false and "maxParallel": null."* |
| *"Loop '\<id\>' declares max 0; the least is 1."* |
| *"Loop '\<id\>' iterates \<reference\>, which is \<format\>; only a list can be iterated."* |
| *"Loop '\<id\>' iterates item.value.\<field\>, but it runs inside no loop; item.value names the enclosing loop's item."* |
| *"Loop '\<id\>' iterates node.\<y\>.value.\<z\>; \<y\> runs inside loop '\<l\>' — a loop iterates a node outside it, or in an enclosing loop's body."* |
| *"Loop '\<id\>' itemLabel '\<field\>' is not a field of the elements of \<reference\> (fields: \<fields\>)."* |
| *"Loop '\<id\>' itemLabel '\<field\>' may be missing or null; itemLabel names a field every element has as a string."* |
| *"Loop '\<id\>' itemLabel '\<field\>' is \<format\>; itemLabel names a string field."* |

**`while`**

| Sentence |
|---|
| *"While '\<id\>' declares max null; a while must declare its bound (1 to 15)."* |
| *"While '\<id\>' declares max \<n\>; a while runs at most FormatBounds.passes (15) passes."* |
| *"While '\<id\>' declares max \<n\>; the least is 1."* |
| *"While '\<id\>' has no body; name the nodes that run per pass in nodes."* |
| *"Node '\<id\>' in while '\<w\>' is neither returned nor read; name it with ret, read it from a body node or from the check."* |
| *"\<site\> reads pass.number, but it runs inside no while; pass is a while's pass."* |
| *"\<site\> reads pass.parent, but its while runs inside no while; pass.parent is the enclosing while's pass."* |
| *"\<site\> reads pass.previous.node.\<id\>, which is not in while '\<w\>'; a pass reads the while's own nodes."* |

**Reads across levels**

| Sentence |
|---|
| *"\<site\> reads node '\<id\>', which runs inside loop '\<l\>'; read node.\<l\>."* |
| *"\<site\> reads item.parent, but its loop runs inside no loop; item.parent is the enclosing loop's item."* |

**`if` and `case`**

| Sentence |
|---|
| *"If '\<id\>' declares then null; an if runs a then body."* |
| *"Case '\<id\>' has no branches; a case runs one branch per set of values."* |
| *"Case '\<id\>' branch \<n\> lists no value; a branch's when names one or more values."* |
| *"Case '\<id\>' switches on \<reference\>, which is \<format\>; a case switches on an enumerated string."* |
| *"Case '\<id\>' branch \<n\> lists "\<value\>", which is not one of \<reference\>'s values (\<values\>)."* |
| *"Case '\<id\>' lists "\<value\>" in branches \<n\> and \<m\>; a value belongs to one branch."* |
| *"Case '\<id\>' doesn't list \<values\> and has no else; a case has a branch for every value: add a branch, an empty branch, or an else."* |
| *"Case '\<id\>' switches on \<reference\>, which can be null, and has no else; a null subject goes to the else: add one."* |
| *"Case '\<id\>' branch \<n\> lists null; a null subject goes to the else."* |
| *"Case '\<id\>' branch \<n\> writes nodes \<[] \| ids\> with ret \<ret\>; an empty branch writes nodes [] and ret null together."* |
| skip reason *"case '\<id\>': arm for \<value\> does nothing"* |

**Functions and calls**

| Sentence |
|---|
| *"Node '\<id\>' in function '\<f\>' reads input.\<name\>; a function reads only its parameters: add a parameter and pass it in with."* |
| *"Node '\<id\>' in function '\<f\>' reads \<reference\>; a function reads only its parameters: add a parameter and pass it in with."* (outer `node.*`, a caller's `item` or `pass`, `run.*`, `check.*`, `profile.*`) |
| *"Function '\<f\>' uses \<snippet \| macro \| format \| renderer\> '\<id\>' but doesn't list it in uses."* |
| *"Function '\<f\>' has its own \<snippet \| macro \| format \| renderer\> '\<id\>' and also uses the package's: rename one."* |
| *"Function '\<a\>' calls '\<b\>', which calls '\<a\>': functions may not call themselves."* (for a longer cycle the chain is named in full) |
| *"Function '\<a\>' calls '\<a\>': functions may not call themselves."* |
| *"Call '\<id\>' reaches depth \<n\>; calls nest at most FormatBounds.depth (15) deep."* |
| *"Function '\<f\>' returns node.\<id\>, an if with no else: add an else, or return a node that always runs."* |
| *"Function '\<f\>' returns node.\<id\>, which runs inside if '\<b\>' and may be skipped: return a node that always runs."* |
| *"Function '\<f\>' returns node.\<id\>, a case with an empty branch for \<values\>: return a node that always runs."* |
| *"Function '\<f\>' returns node.\<id\>, whose branches return \<format\> and \<format\>: a function returns one format. Wrap them in an object format."* |
| *"Function '\<f\>' declares format \<format\>; its ret '\<id\>' returns \<format\>."* |
| *"Function '\<f\>' holds a \<checks \| deliverables\> folder; checks and deliverables live only at the package's top level: return a check_result or a value instead."* |
| *"Macro '\<m\>' is placed in function '\<f\>', where its if reads node.\<id\>, which doesn't exist there: add a classifier with that id (pattern A), or pass the decision in and hold it in a computed node (pattern B)."* |
| *"Call '\<id\>' names function '\<f\>', which the package doesn't define."* |
| *"Call '\<id\>' passes no \<param\>; function '\<f\>' takes \<params\>."* (a parameter left out, even an optional one: pass null) |
| *"Call '\<id\>' passes \<param\>, which function '\<f\>' doesn't take (\<params\>)."* |
| *"Function '\<f\>' parameter '\<param\>' declares \<required \| channel\>; a parameter has label, description and format, and every one is passed."* |
| *"Call '\<id\>' passes \<reference\> (\<format\>) as \<param\>; function '\<f\>' takes \<format\>."* |
| *"Function '\<id\>' reads param.\<name\>, which carries profile.\<field\>, in \<a prompt \| a part \| a condition\>; the profile is read only in deliverables and macro bodies."* (chapter 6 R-F3) |
| *"Call '\<id\>' declares format \<format\>; function '\<f\>' returns \<format\>."* |
| *"Call '\<id\>' has a body; a call is a header only."* |

#### 4.10.2 Notes and warnings at publish

| Sentence | Kind |
|---|---|
| *"Up to \<n\> agent calls could run at once; this engine runs at most \<N\> per job, so the rest wait their turn."* | note |
| *"An unbounded number of agent calls could run at once (loop '\<id\>' has no cap over a list known only at run time); this engine runs at most \<N\> per job, so the rest wait their turn."* | note |
| *"Loop '\<id\>' iterates \<reference\>, which could hold more than \<limit\> items; this engine runs at most \<limit\> per loop, and fails the loop beyond that."* | note |
| *"Up to \<n\> agent calls could run in one job; this engine runs at most \<limit\> per job, and fails the job beyond that."* | note |
| *"Function '\<f\>' lists \<snippet \| macro \| format \| renderer\> '\<id\>' in uses but never uses it."* | warning |
