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
| 2 Types and inputs | `kind` and `format`, the dialect, text formats, format `$id`s, inputs, enum labels |
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
| `manifest.json` | name, version, title, description, tags, inputs | — | § 1.3; inputs in chapter 2 |
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
| `formats/<id>.json` | one of the package's own formats, as JSON Schema | `formats/index.json` | chapter 2 |
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
  (chapter 2 § 6). The JSON Schema
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
| `inputs` | object | no | the inputs, keyed by id, in Create page order (chapter 2 § 8); `{}` when none |

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
names have no reserved list (chapter 2 § 5.3).)

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
| `kind` | string, one of the kinds (chapter 2 § 1) | no | every node and check header, every flow `index.json`, renderers (`rendered`), deliverables (`rendered`) |
| `label` | string, not empty or whitespace | no | every node, check, flow node, function, renderer, snippet, macro, deliverable and input. It is the display name everywhere |
| `description` | array of strings | yes | every `index.json`, every header, input and function input, and the manifest (§ 1.2.3) |
| `format` | a format name or an inline schema (chapter 2 § 2) | no | every node, check, function, renderer, deliverable, snippet, macro and input; a snippet folder's `index.json` |
| `reproducible` | boolean | no | every node, checked against the derived value (chapter 2 § 1.1) |
| `producer` | string: `"generated"` or `"computed"` at 31 | no | every node and check, checked against its kind (chapter 2 § 1.3) |
| `modelDerived` | boolean | no | every node and check, checked against the derived value (chapter 2 § 1.2) |
| `runDependent` | boolean | no | every node and check, checked against the derived value (chapter 2 § 1.2) |
| `profileCarrying` | boolean | no | every node and check, checked against the derived value (chapter 3 § 4.6) |
| `if` | a JSON Logic condition (chapter 3) | yes: always | every production leaf (`agent`, `rendered`, `computed`, `call`), check, snippet, macro, macro folder and deliverable. A node's own condition is spelled `if`, replacing 30's `when`; a `case` branch keeps `when` for its values (chapter 4) |

- **`label` may not be empty or whitespace**.
  A loop's item naming is `itemLabel`, never `label`;
  `labelField` is gone.
- **Flow nodes write `format`,** and publish refuses one that differs from the format derived from
  the node's `ret` (chapter 2 § 2.2).
- **`reproducible` is written on every node and checked against the derived value;** a mismatch is
  refused. Revisiting the member is [#1466](https://github.com/Consultologist/Consultologist-Blazor/issues/1466) (Milestone 40)
  (the rule is chapter 2 § 1.1).
- **`producer` is written on every node and checked against its kind,** like `reproducible`:
  `"generated"` for `kind: "agent"`, `"computed"` for every other kind. A mismatch, or a value
  reserved for Milestone 40 (`"grounded"`, `"extracted"`, `"attention"`), is refused
  (the rule is chapter 2 § 1.3).
- **`modelDerived`, `runDependent` and `profileCarrying` are written on every node and checked against the values the
  resolver derives,** like `reproducible` and `producer`: an agent node is always
  `modelDerived: true`, any node reading model output, directly or through other values, is
  `true`, and a node whose reads include `run.*` or a run-dependent value is
  `runDependent: true`. `profileCarrying` is written and checked the same way: `true` for an
  agent node whose prompt places a macro whose body reads `profile.*`, or a node reading such a
  value. A mismatch is refused. The flags are node members; formats stay pure shape
  (the rule is chapter 2 § 1.2).

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
  (chapter 2 § 5.3).
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
| inputs | `input.<id>.value`, `.content`, `.title` (chapter 2 § 2.1) | inputs |
| snippets | `snippet.<id>.content`, `snippet.<folder>.<item>` | snippets; items within their folder |
| macros | `macro.<id>`, `macro.<folder>.<item>` | macros; items within their folder |
| renderers | `renderer.<id>` | renderers |
| formats | a `format` name, a bare-id `$ref` | every owner together: a package format may not reuse a built-in or catalogue name (chapter 2 § 6) |
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
