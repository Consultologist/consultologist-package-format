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
  written, character for character; [chapter 11](#11-every-sentence) lists every one with its audience.
- **`<…>` marks a placeholder** in a sentence, a path or a key: the checker fills it with the
  package's own text, an id, a path, a count or a limit, and never with patient text.
- **Fictional examples only.** Every example person and every clinical text in this document is
  invented.
- **Section numbers** are written `N.k.j` in headings: chapter N, section k, subsection j. Inside
  a chapter a reference carries the full number (`§ 1.5.3`); from another chapter it is written
  "chapter 1 § 5.3", meaning section 5.3 of chapter 1, the heading numbered 1.5.3.
- **`jsonc` blocks** are annotated JSON, for reading only; every file in a package is strict JSON
  (RFC 8259), with no comments.

### Files that are normative beside this text

These are published beside this document in the registry and are as binding as it is, where the
text names them:

- [`v31/bounds.json`](v31/bounds.json): `SourceBounds`, `FormatBounds`, the reserved ids;
- [`v31/constants.json`](v31/constants.json): the versions, kinds, features, producers, limits and
  Markdown extensions the text names;
- [`v31/profile.json`](v31/profile.json): the closed list of profile fields;
- `v31/schemas/`: one JSON Schema (2020-12) for every kind of file and every compiled
  document, each linked where this text defines the kind;
- [`v31/dialect.schema.json`](v31/dialect.schema.json): the meta-schema of the formats dialect;
- [`v31/formats/`](v31/formats/index.json): the built-in formats, one file each, with their index;
- [`v31/renderers/`](v31/renderers/index.json): the built-in renderers, with their index;
- [`v31/sentences.json`](v31/sentences.json): every refusal, warning and recorded sentence;
- [`v31/scriban-dialect.md`](v31/scriban-dialect.md): the template dialect, version 1.0.0 (`scriban-dialect@1.0.0`), the rules of chapter 5 § 2 in reference form.

[`v31/conformance/`](v31/conformance/README.md) is the conformance suite ([chapter 12](#12-conformance)). It holds
hand-written examples of valid and invalid files for each schema, which are examples and not goldens;
every other part of the suite is exported by the library's generators, never written by hand.
`python3 scripts/check-v31.py` runs the registry's checks over all of the above.

### The chapters

| Chapter | Covers |
|---|---|
| [1 Files and scopes](#1-files-and-scopes) | the folder layout, file kinds, every member required, ids, namespaces and qualified keys, `SourceBounds`, `FormatBounds` |
| [2 Types and inputs](#2-types-and-inputs) | `kind` and `format`, the dialect, text formats, format `$id`s, inputs, enum labels |
| [3 Expressions](#3-expressions) | JSON Logic: conditions, `computed`, every operation, null rules, `run.*`, the printer, the evaluator, `matches` and `has_word` |
| [4 Loops and functions](#4-loops-and-functions) | `for`, `while`, `until`, branches, `.items`, functions and `call` |
| [5 Templates and macros](#5-templates-and-macros) | the Scriban dialect, renderers, snippets, parts, macros, whitespace, run spots |
| [6 Checks, deliverables and the profile](#6-checks-deliverables-and-the-profile) | checks and check loops, deliverables as files, gating, the profile |
| [7 The compiled documents](#7-the-compiled-documents) | `resolve.json`, `lock.json`, evidence and views, in-package tests, the publish report |
| [8 What an engine does with a package](#8-what-an-engine-does-with-a-package) | the two load paths, loading and admitting versions, scheduling, the per-job ceiling, retries and limits, the drain, where the record is written, delivery; the pages, `WorkflowPackages/Current` and the diagram are the app's and are named, not specified |
| [9 The record](#9-the-record) | what a job's record pins, keys and sub-row ids, the sentences the record holds, and the provenance contract |
| [10 Migration (30 → 31)](#10-migration-30--31) | what turns a package at 30 into a package at 31, the converter, the migration report, the snapshot test |
| [11 Every sentence](#11-every-sentence) | every refusal, warning, job-start, recorded and History sentence, in one table |
| [12 Conformance](#12-conformance) | the conformance suite: what it holds, where it lives, and which build area exports it |

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
| record storage 11, in the job's Durable entity | record storage 12: keys with roots, check, renderer, macro, decision and call rows, `producer` and model-derived on every row, run facts and run spots; rows in a table, written once, and a canonical record blob at job end | 9 |
| Mermaid 11, default layout | Mermaid 12 with ELK; renderers, macros, functions and checks drawn | 8 |

Nothing about 30 is kept by reading 31 as a delta: a package at 30 becomes a package at 31 by the
migration ([chapter 10](#10-migration-30--31)), and the engine reads only what the migration and the registry produce.

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
  dag.mmd                  derived view: committed for example packages, generated at publish ([chapter 8 § 8.14](#814-what-belongs-to-the-app))
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
| `dag.mmd` (root only) | the derived Mermaid view | — | [chapter 8 § 8.14](#814-what-belongs-to-the-app) |

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
    migration_snapshot.json written by the migration ([chapter 10 § 10.12](#1012-the-snapshot-test))
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
Each kind of file has a JSON Schema in `v31/schemas/`, applied to the file's JSON (a
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
carries no naming pointer: naming items is only a loop's business.

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
- **A package whose ids collide with a reserved word is renamed by the migration** ([chapter 10 § 10.6](#106-reserved-ids-are-renamed)):
  `example-nested-note`'s loop is `sections`, not `parts`.

### 1.7 `SourceBounds`

A spec-level object of limits on a package's source.

| Member | Value |
|---|---|
| `files` | 512 files |
| `fileBytes` | 256 KiB (262,144 bytes) per file |
| `totalBytes` | 2 MiB (2,097,152 bytes) in all |
| `pathLength` | 200 characters, counted from the package root |
| `idLength` | 64 characters |
| `jsonDepth` | 32 levels of nesting in any JSON value (a file, a header, an inline schema) |
| `expressionNodes` | 1,000 nodes (operations, `var`s and literals) in one JSON Logic expression |

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
  per-job ceiling ([chapter 8 § 8.5](#85-the-per-job-ceiling)). `maxParallel: 1` stays refused,
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
  ([chapter 9](#9-the-record)). Item paths never contain `:`.
- **Mermaid ids replace `.` with `__`:** `node__sections__paragraphs__draft_paragraph`
  ([chapter 8 § 8.14](#814-what-belongs-to-the-app)).
- **Keys are used everywhere at 31,** never only where an id repeats: one key form, no
  conditional.
- **Where a key replaces a bare id:**
  - **the record** (record storage 12): `nodeOutputs` keys, block ids, `skippedBlocks`, item-step and
    block events, item progress, collections, the concept source and the `nodes` rows ([chapter 9](#9-the-record));
  - **the engine:** scheduling keys, activity inputs, the derived edges and the walker's resolution
    ([chapter 8](#8-what-an-engine-does-with-a-package));
  - **the pages:** Mermaid ids, the Editor's selection keys and links, the rail and History;
  - **`resolve.json` and test files** (chapter 7).
- **References inside a package** stay `node.x` and resolve outward (§ 1.9.2); the resolver writes
  each resolved reference as its key in `resolve.json` (chapter 7).
- **How pages show two nodes with the same id:** the Editor's tree places each under its folder
  (`sections › paragraphs › draft`); a pane shows `id draft · path node.sections.paragraphs.draft`;
  selection and links use the key; History and the rail show the label, with the path in a muted
  line where two rows share a label.

### 1.10 Refusals

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format.

**Scopes and bounds.**
- Duplicate in an overlapping scope:
  *"Node '\<id>' in \<path> reuses the id of node '\<id>' \<at the top level | in \<other path>>, which \<path> can read: rename one. Ids may repeat only where neither can see the other (for example in two sibling loops)."*
- `FormatBounds`:
  - *"While '\<id>' declares max \<n\>; a while runs at most FormatBounds.passes (15) passes."*
  - *"Call '\<id>' reaches depth \<n\>; calls nest at most FormatBounds.depth (15) deep."*
  - *"Loop '\<id>' declares maxParallel \<n\>; the most is FormatBounds.parallel (15)."*

**Files and folders.**
- *"File '\<path>' is not listed: every file in \<folder> is named once in its index.json, or is index.json or README.md."*
- *"\<folder> has no index.json; every folder lists its members, even when it has none (\"items\": [])."*
- *"The package has no \<folder>/ folder; all nine top-level folders are always present."*
- *"\<list> lists '\<id>', but \<folder> has no \<id>.md or \<id>/."*
- *"\<list> lists '\<id>' twice."*
- *"\<list> lists '\<id>/'; list a folder by its bare id."*
- *"\<folder> holds both \<id>.md and \<id>/: an id names one file or one folder."*
- *"Delivery folder '\<path>' is inside another delivery folder; delivery folders are one level deep."*
- *"File '\<path>' starts with a byte-order mark; save it as UTF-8 without one."*
- *"File '\<path>' contains a carriage return on line \<n\> that doesn't end the line; lines end with \n."*

**Front matter.**
- *"File '\<path>' must start with a line of exactly ---, then one JSON object, then a line of exactly ---."*
- *"The header of '\<path>' is not valid JSON: \<parser message>."*
- *"The header of '\<path>' declares '\<member>' twice."*
- *"\<Kind> '\<id>' has an empty body; its \<prompt | template | text> is the body."*
- *"\<Kind> '\<id>' has a body; a \<computed node | call | check> keeps everything in its header."*

**Members.**
- *"\<Declaration> is missing '\<member>'; every member is written, and null means none."*
- *"\<Declaration> sets '\<member>' to null, which it can never be."*
- *"\<Declaration> in '\<path>' declares unknown member '\<member>'. Did you mean '\<closest>'?"*
- *"\<Declaration> has an empty description; write null for none."*
- *"\<Declaration>'s description is \<n\> characters; the most is 500."*
- *"\<Declaration> has an empty label."*
- *"\<Node> '\<key>' declares reproducible \<value>, but its \<kind | body | function> makes it \<derived>."*
- *"\<Node> '\<key>' is kind \<kind> and declares producer '\<value>'; a \<kind> node's producer is \<generated | computed>."*
- *"\<Node> '\<key>' declares \<modelDerived | runDependent | profileCarrying> \<value>, but its reads make it \<derived>: \<the read that does, or none>."*

**Ids.**
- *"'\<id>' is not a valid id: a lowercase letter, then lowercase letters, digits or underscores."*
- *"Id '\<id>' is \<n\> characters; the most is SourceBounds.idLength (64)."*
- *"Id '\<id>' is reserved on Windows (con, prn, aux, nul, com1–com9, lpt1–lpt9) and can't name a file: rename it."*
- *"Id '\<id>' is reserved: \<root | member> '\<word>' is read in references, so nothing may be called '\<id>'."*
- *"Format '\<id>' reuses the name of a \<built-in | catalogue> format: rename it."*
- *"Renderer '\<id>' reuses the name of a built-in renderer: rename it."*
- *"Node '\<id>' appears twice inside while '\<while>' (\<path> and \<path>): pass.….node.\<id> must name one node."*

**`SourceBounds`.**
- *"The package has \<n\> files; the most is SourceBounds.files (512)."*
- *"File '\<path>' is \<n\> KiB; the most is SourceBounds.fileBytes (256 KiB)."*
- *"The package is \<n\> MiB; the most is SourceBounds.totalBytes (2 MiB)."*
- *"Path '\<path>' is \<n\> characters; the most is SourceBounds.pathLength (200), counted from the package root."*
- *"File '\<path>' nests JSON more than 32 levels deep at \<JSON pointer>; the most is SourceBounds.jsonDepth (32)."*
- *"\<Site> in '\<path>' has \<n\> expression nodes; the most is SourceBounds.expressionNodes (1,000)."*

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
([chapter 9](#9-the-record)), and History, the diagram and the Editor show them.
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
(member `producer`, [chapter 9](#9-the-record)):

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
  wording (a `description`, which is what the model is told) is told apart from a change of shape ([chapter 9](#9-the-record)).
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
| `enum` | on a string, an integer or a number | the plain enum (§ 2.9); its values are all of that one kind (a nullable type may list `null`) |
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
([chapter 9](#9-the-record)). History shows them as *"Not sent to the model: …"*. The reply is still
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
**Registry and catalogue formats are exempt** from the pattern ([ruled](https://github.com/Consultologist/Consultologist-Blazor/issues/1504)): `concept_list` has `isSnomedConcept` and `isActive`. The pattern holds for a package's own formats. Making the names consistent is #1523 (Milestone 40).

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
  definition and the binding that chose it ([chapter 9](#9-the-record)).

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
  Registry and catalogue formats are exempt from the pattern (chapter 2 § 5.3; [ruled](https://github.com/Consultologist/Consultologist-Blazor/issues/1504)); making the names consistent is #1523 (Milestone 40).
  read of an enumerated string.
- **Any format may be an input's,** since formats are pure shape (§ 2.1.3), **except**
  `markdown_inline` (no widget, and an inline fragment is not something a clinician submits); a
  top-level `anyOf` (no widget can offer "one of these shapes").
- **Plain text pasted into a Markdown input** can be misread (a leading `#` becomes a heading); the
  rich-text editor shows the formatting as it is typed.

#### 2.8.2 Documents

**Documents need no member.** Any input with a text format takes typed text or a document (the
parser decides), and an array of a text format takes several items, each typed, a document, or an
earlier run's deliverable, in the order sent ([chapter 8 § 8.14](#814-what-belongs-to-the-app)). A data-format input is typed only,
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
| offered only when the input is yes | `{ "===": [ { "var": "input.<id>.value" }, true ] }` | `null === true` is false: not offered |
| offered unless the input is no | `{ "!==": [ { "var": "input.<id>.value" }, false ] }` | `null !== false` is true: offered |

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

- **The input takes the macro's id and label,** and the test is joined with `and` to any existing
  `if`: `{ "and": [ <its if>, <the test> ] }`. Where the macro's id is already an input's id, the
  migration adds a suffix to the input's ([chapter 10 § 10.3](#103-per-run-macro-choices-become-boolean-inputs)).
- **The Create page shows an optional boolean as three choices** (unset, yes, no), so "unset" keeps
  the macro's default, and **unset is sent as `null`**. A plain checkbox would show a default-on choice
  unchecked while meaning on ([chapter 8 § 8.14](#814-what-belongs-to-the-app)).

### 2.11 What the migration does to types and inputs

What the migration from 30 does to types and inputs (the format conversions, the inputs' new shape, the optional boolean inputs for per-run macro choices) is [chapter 10 § 10.1](#101-what-the-rewrite-does-mechanically).

### 2.12 `WorkflowPackages/Current`: what satellites see

The engine's `WorkflowPackages/Current` response is the engine's API to the Copilot agent and the Zoom app, not part of the package format, and is not defined here.

### 2.13 Refusals

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format.

**Sentences outside the checker.**
- *"This workflow needs the web app"* (a satellite, not the checker).
- History's *"Not sent to the model: …"* (§ 2.3.5) and *"computed from model text: \<key>"* (§ 2.1.2).

**Kinds and formats:**
- *"Node '\<id>' declares unknown kind '\<kind>' (accepted: agent, rendered, computed, for, while, if, case, call)."*
- *"Node '\<id>' declares kind let; a let is now kind computed, with its JSON Logic in expression."*
- *"Node '\<id>' is kind \<kind> and declares producer '\<value>'; a \<kind> node's producer is \<generated | computed>."*
- *"Node '\<id>' declares producer '\<value>', which is reserved for a later version (accepted at 31: generated, computed)."*
- *"Node '\<id>' declares \<modelDerived | runDependent | profileCarrying> \<value>, but its reads make it \<derived>: \<the read that does, or none>."*
- *"Node '\<id>' is kind agent and returns \<format>, which has no binding for producer \<producer> in agents/bindings.json."*
- *"Node '\<id>' is kind rendered and returns \<format>; a rendered node returns plaintext, markdown_block or markdown_inline."*
- *"Node '\<id>' is kind agent and declares an inline format; an agent's format is named, in formats/."*
- *"\<Flow> '\<id>' declares format \<declared>, but its ret gives \<derived>."*
- *"Branch \<n\> of \<if | case> '\<id>' returns \<format>, which is not in the declared union \<union>."*
- *"Format '\<name>' is not a built-in, catalogue or package format."*

**Reads:**
- *"'input.\<id>' is read bare; read input.\<id>.value, or input.\<id>.content for text."*
- *"'\<path>.title' reads the title of a plain enum, which has none; use a labelled oneOf, or read .value."*
- *"\<Condition> compares \<path>.title with '\<literal>', which is not one of its titles (\<titles>)."*

**The dialect:**
- *"\<Format | Input '\<id>'> uses keyword '\<keyword>' at \<path>, which is outside the formats dialect."*
- *"Format '\<name>' declares no $schema; every format file names the dialect (urn:consultologist:spec:31:dialect)."*
- *"Format '\<name>' declares $schema '\<value>', but the package is specVersion \<n\>, whose dialect is \<id>."*
- *"\<Format> at \<path> declares additionalProperties \<value>; every object declares additionalProperties: false."*
- *"\<Format> at \<path> lists '\<property>' in required but declares no such property."*
- *"\<Format> at \<path> leaves '\<property>' out of required; every property is listed in required, and an optional one is written as nullable."*
- *"Node '\<id>' returns \<format>, an anyOf at its root, which strict mode can't send to a model; wrap it in an object."*
- *"\<Format> at \<path> writes a nullable \<type> with anyOf; write it as \"type\": [\"\<type>\", \"null\"]."*
- *"\<Format> at \<path> declares type \<list>; a type array is one type plus \"null\"."*
- *"\<Format> at \<path> uses format '\<value>'; the only format is date, on a string."*
- *"\<Format> at \<path> has '\<keyword>' beside $ref; only title and description may sit beside a $ref."*
- *"\<Format> at \<path> refers to itself; recursive formats aren't supported."*
- *"Package format '\<id>' declares $id; a package format's $id is written at publish."*
- *"Package format '\<id>' is a \<string | number | boolean>; a package defines object and array formats, and refers to built-in and catalogue formats by name."*

**Annotations:**
- *"Format '\<name>' is a text format and declares no contentMediaType."*
- *"Format '\<name>' is Markdown and declares no x-markdown (block or inline)."*
- *"\<Format> declares \<contentMediaType | x-markdown> at \<path>, where it doesn't apply."*
- *"\<Input '\<id>' | Node '\<id>'>'s inline format declares \<contentMediaType | x-markdown>; text inside an inline format is a $ref to a text format."*

**Formats folder:**
- *"formats/index.json lists '\<id>', but formats/ has no \<id>.json."*

**Inputs:**
- *"Input '\<id>' takes markdown_inline; use plaintext or markdown_block."*
- *"Input '\<id>' takes a choice of shapes (anyOf); an input has one shape."*
- *"Input '\<id>' declares channel '\<channel>' (accepted: transcript, image, ambient-note, form)."*
- *"Input '\<id>' declares channel '\<channel>', which is only for a text input or an array of text."*
- *"Input '\<id>' declares channel 'form', which needs an object with at least one property."*
- *"Input '\<id>' field '\<property>' has no title; the Create page labels each field by its title."*
- *"Input '\<id>' declares default; inputs have no default at 31."*

**Enums:**
- *"\<Subject> declares one value; an enum with one value is a constant, not a choice."*
- *"\<Subject> declares value '\<value>' twice."*
- *"\<Subject> value '\<value>' must be snake_case (a lowercase letter, then lowercase letters, digits, or underscores)."*
- *"\<Subject> gives two values the title '\<title>'."*
- *"\<Subject> writes oneOf branch \<n\> as \<shape>; each branch is exactly { \"const\": \<value>, \"title\": \<label> }."*
- *"\<Subject> declares both enum and oneOf; write one."*
- *"\<Subject> is nullable but its enum doesn't list null; a nullable enum lists null among its values."*
- *"\<Subject> is nullable but its oneOf has no { \"const\": null } arm; a nullable labelled enum adds one."*

**Strict mode's size limits:**
- *"Format '\<name>' declares \<n\> properties; a format sent to a model declares at most \<limit>."*
- *"Format '\<name>' nests \<n\> levels deep at \<path>; a format sent to a model nests at most \<limit>."*

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
  converter ([chapter 10 § 10.9](#109-the-converter)) turns expressions into JSON Logic and back as a tool, not as the
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

`resolve.json` holds JSON Logic "in one canonical form". The canonical form is also the
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
  (chapter 4 § 5.2). The migration rewrites a node's `when` to `if` ([chapter 10 § 10.1](#101-what-the-rewrite-does-mechanically)).

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
  per run ([chapter 9](#9-the-record)).
- **No time zone, no job:** every job is refused at start until the account's time zone is set,
  whether or not the package reads `run.date` ([chapter 8 § 8.2](#82-the-load-step-by-step-31)).

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
before a job starts. Each row records it as `runDependent` ([chapter 9](#9-the-record)). **Every node header
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
- **It is recorded and shown:** each row carries `modelDerived` ([chapter 9](#9-the-record)), and History, the
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
  Each row carries `profileCarrying` ([chapter 9](#9-the-record)), and a row that is
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
(they change what `var` names inside them, which the checker's typing of § 3.7 doesn't cover; none is used by a published package at 31's release); three-operand comparisons; and Corvus's non-standard extras
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
- **Engine:** the I-Regexp pattern is translated to .NET per RFC 9485 § 5 (for example `.`
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

The conformance suite ([chapter 12](#12-conformance)) carries a vector for every row of §§ 3.5.1–3.5.5 with a `null`
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
  `lock.json`'s `builtins` (chapter 7). The converter ([chapter 10 § 10.9](#109-the-converter)) parses its output back to the
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

The record's shape is [chapter 9](#9-the-record)'s. For expressions:

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

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format.

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
count toward the per-job ceiling is stated here; the engine side is [chapter 8](#8-what-an-engine-does-with-a-package). Conditions inside
these declarations are JSON Logic, defined in [chapter 3](#3-expressions); folders, ids and scopes
are [chapter 1](#1-files-and-scopes); formats are [chapter 2](#2-types-and-inputs).

Where this chapter's rules are unchanged from specVersion 30 and the design defers to it, the text
restates them: §§ 4.2.2 (item paths, alignment and counts per instance), 4.2.4 (an empty list),
4.2.6 (`item.parent`), 4.3.2 to 4.3.4 (how a `while` runs, the pass object, reading it from
outside) and 4.4 (reading across levels).

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
never read as a field path. (`example-nested-note`'s loop is called `sections`, because `parts` is a reserved id, chapter 1 § 6; the migration renames it, [chapter 10 § 10.6](#106-reserved-ids-are-renamed).)

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

Together with § 4.1's nine members, a `for`'s `index.json` has exactly seventeen members.

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

A `for` can stop early with `until`, or run only its first items with `max`, and says how it ended through `.stopped`:

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
| `.content` | `markdown_block` | the standard rendering (`## <item name>`, then the item's text, joined by blank lines), which keeps specVersion 30's bytes (chapter 5) |
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
  (an input's own label does not name its items; the loop owns naming).
- **Retention:** a name is trimmed and cut to 120
  characters ending in "…", and is **kept in the record past the retention sweep only when it
  comes from package text** (a snippet folder's header). A name drawn from an input or a model's
  output follows 7-day retention, and History then shows the position name. **Reasons always use
  position names** (*"stopped early at Sections 3"*), never a drawn name, since a reason can land in
  a deliverable (chapter 6 § 6.2).
- **`labelField` is not a member;** [chapter 10 § 10.1](#101-what-the-rewrite-does-mechanically) covers the migration.

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

Every loop writes every member of its kind, `null` for each one it does not use. How the migration writes them is [chapter 10 § 10.1](#101-what-the-rewrite-does-mechanically).

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

With § 4.1's nine members, a `while`'s `index.json` has fifteen members. A `while` has no `parallel`,
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

A pass's `node.<id>` has that node's format, and `pass.number` is a number.

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

With § 4.1's nine members, twelve members. A body object has exactly `nodes` (at least one id) and
`ret`.

#### 4.5.2 `case`

| Member | Type | Null | Meaning |
|---|---|---|---|
| `case` | a reference string | never | the subject |
| `branches` | array, at least one, of `{ "when": [values], "nodes": [ids], "ret": full name }`; an empty branch writes `"nodes": []` and `"ret": null` | never | one branch per set of values |
| `else` | a body | `null` only when the branches list every value and the subject can't be `null` | runs when no branch's values match, and when the subject is `null` |

With § 4.1's nine members, twelve members.

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
  reads as skipped, with the reason *"case '\<id>': arm for \<value> does nothing"*. So skipping some values is written in the `case` itself, never as an `if`
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
  subject and the branch taken), its run-dependence and whether it is model-derived ([chapter 9](#9-the-record)).

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
  per-job ceiling, the call limit and the start order hold inside functions (§ 4.8; [chapter 8 § 8.5](#85-the-per-job-ceiling)).
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
  calls in flight for one job (for example 16). It is [chapter 8 § 8.5](#85-the-per-job-ceiling)'s. Function bodies run inline in
  the job's orchestration, so their calls are scheduled under the same ceiling.
- **Everything counts the same way:** agent calls in nested loops, inside function calls (at any
  depth), and in check loops.
  **Only agent calls count:** `rendered` and `computed` nodes make no model call and don't
  count.
- **Total-work limits**, engine settings beside the ceiling, starting at: **200 items
  per loop instance** (§ 4.2.4), **500 agent calls per job** (retries included as one call), and a
  **step budget per render**, starting at **100,000 steps** (chapter 5). Each is checked at run time and fails the job, or the
  node, with a sentence ([chapter 8 § 8.7](#87-retries-and-limits)); publish notes a package whose worst case can exceed one
  (§ 4.10.2).
- **Each loop's `maxParallel` still applies within it.** The effective concurrency at a point is
  the smaller of the ceiling and the product of the caps along its nesting path.
- **429 responses and other service failures** are retried with back-off and recorded as retries
  on the node's row. A node fails after 10 minutes of waiting on 429s in total, or after 5
  attempts for another failure, and a job fails if it hasn't finished 30 minutes after its
  orchestration started;
  all three are engine settings ([chapter 8 § 8.7](#87-retries-and-limits)).
- **At publish, a note rather than a refusal** when nested caps multiply past the engine's
  ceiling (§ 4.10.2). The product is taken along each nesting path of loops and calls. For the
  note's worst case, a `maxParallel: null` loop over a list whose length publish knows (a
  snippet folder) counts its length, and over any other list counts as unbounded, which the note
  says. Requiring a non-null `maxParallel` is [#1474](https://github.com/Consultologist/Consultologist-Blazor/issues/1474) (Milestone 40).

### 4.9 What the record holds

The record is [chapter 9](#9-the-record)'s. For flow and functions (storage 12 adds to 11, with qualified keys):
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

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format.

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

## 5. Templates and macros

This chapter defines every template a version 31 package holds and the one template language they
share: the Consultologist Scriban dialect, renderers as package templates, snippets, parts, and
macros with their whether and where. It states what each template may read, how placements carry
whitespace, how run facts are kept out of the comparable hash (run spots), and every refusal
sentence. The dialect's rules are stated here in full and published in their versioned form as
[`v31/scriban-dialect.md`](v31/scriban-dialect.md) (`scriban-dialect@1.0.0`). Deliverable
templates are templates too: their reads are listed here, and everything else about them is in
[chapter 6](#6-checks-deliverables-and-the-profile). Personal (account-level) macros are not in
version 31 ([#1417](https://github.com/Consultologist/Consultologist-Blazor/issues/1417), Milestone 40).

### 5.1 Templates present; headers decide

**The rule:** decisions are recorded, so they live in headers as JSON Logic
([chapter 3](#3-expressions)). Bodies only present.

- **Whether** a node runs, an item is included, a part or snippet is used, a macro is offered,
  a loop stops or a deliverable exists is a header condition, evaluated and recorded by the
  engine.
- **A body** only lays out what it's given: loops over lists, joins, formatting, and the
  choice of how a recorded fact (a skipped item, a failed check) appears.

#### 5.1.1 The template sites

| Site | Where it lives | Rendered | Its output |
|---|---|---|---|
| prompt | the body of `nodes/…/<id>.md`, `kind: agent` | before the model call, per instance | the text sent to the model |
| `rendered` node | the body of `nodes/…/<id>.md`, `kind: rendered` | per instance, no model | the node's text value |
| renderer | the body of `renderers/<id>.md` | at each pipe use | text spliced at the pipe |
| snippet body | the body of `snippets/…/<id>.md` | where it's placed, in that scope | text spliced at the placement |
| part text | `parts.<id>.text` in an agent node's header | where it's placed, when its `if` holds | text spliced at the placement |
| macro instruction | `instruction` in `macros/…/<id>.md` | where it's placed, when the macro is triggered | prompt text, with the macro's marker |
| macro body | the body of `macros/…/<id>.md` | after the model replies, before substitution | text substituted for the marker |
| deliverable | the body of `deliverables/…/<id>.md` | once, after its reads complete | the deliverable's composed text |

A `computed` node and a check have no template: their expression is JSON Logic in the header
member `expression`, and their body must be empty ([chapter 3](#3-expressions)).

#### 5.1.2 An agent node's prompt members

An agent node's header is judged by the schema [`node-agent`](v31/schemas/node-agent.schema.json).

Beside `kind`, `label`, `description`, `format`, `reproducible` (always `false` for an agent
node, [chapter 1](#1-files-and-scopes)) and `producer` (always `"generated"`,
[chapter 2 § 1.3](#213-producer)), `modelDerived` (always `true` for an agent
node) and `runDependent` (`true` when its prompt reads `run.*` or a run-dependent value) and
`profileCarrying` (`true` when its prompt places a macro whose body reads `profile.*`, or reads such a
value), all
checked against the derived values ([chapter 2 § 1.2](#212-the-contagious-flags-run-dependent-and-model-derived)), and its agent binding, chosen by format and
producer ([chapter 2](#2-types-and-inputs)),
a `kind: agent` node's header holds the members that govern its prompt and reply:

| Member | Type | Null | Meaning |
|---|---|---|---|
| `onInvalid` | `"retry"` or `"fail"` | no | what an invalid reply does: a reply that fails its format, or a macro marker check (§ 5.8.6). `retry` asks once more; `fail` fails the job. As at version 30. |
| `failIfEmpty` | string | yes: an empty value doesn't fail | the sentence the job fails with when the reply's value is empty. Carried over from version 30 unchanged, and always written (`null` when unused). |
| `parts` | object | yes: none | the node's conditional prompt text (§ 5.7) |
| `ordered` | boolean | no | whether triggered macro markers must come back in order (§ 5.8.5) |

### 5.2 The dialect

The dialect is a published, versioned spec in the package-format registry, beside the JSON
Schema dialect ([chapter 2](#2-types-and-inputs)), with conformance vectors: a valid and an
invalid template for every rule and every refusal sentence below. **Anything not listed as
allowed is refused at publish, with a sentence**.

The engine renders with **Scriban 7.2.5**, pinned exactly. The dialect's version is recorded in
`lock.json` and listed in `requires` (chapter 7).

#### 5.2.1 Statements

**Allowed:**

| Construct | Written | Notes |
|---|---|---|
| output | `{{ x }}` | `x` is an access path, optionally piped (§ 5.2.2, § 5.5) |
| member access | `node.plan.value.sections` | index access (`list[0]`) is refused (below) |
| literals | `"text"`, `12`, `true`, `false`, `null` | as arguments to built-ins and in `if` comparisons |
| `for` | `{{ for x in list }} … {{ end }}` | over a list only; position variables `for.first`, `for.last`, `for.index`, `for.even`, `for.odd` |
| `if` | `{{ if … }} … {{ else if … }} … {{ else }} … {{ end }}` | restricted to recorded facts (§ 5.2.5) |
| pipe | `x \| string.strip`, `x \| renderer.concept_bullets` | to the allowed built-ins (§ 5.2.2) and to renderers (§ 5.5) only |
| comment | `{{# a note }}` | rendered as nothing |
| raw block | `{%{ … }%}` | literal braces, not interpreted |

**Refused:**
- assignment (`x = …`) and `capture`;
- `func`, `include`, `import`, `with`, `wrap`;
- Scriban's `while`, `break` and `continue`;
- `case` / `when`;
- `tablerow`;
- arithmetic (`+`, `-`, `*`, `/`, `%`, `//`) and string concatenation by `+`. Markdown numbers a
  `1.` list itself, and a computed value belongs in a `computed` node.
- a `for` over anything but a list (a range `1..3`, an object), and the `for` options `limit:`,
  `offset:` and `reversed`: they choose which elements appear, which is a decision;
- `for.rindex`, `for.length` and `for.changed`;
- **index access** (`list[0]`, `node.plan.value.sections[2]`): a list is read whole, by
  a `for`, or by identity through `.items`, as in JSON Logic ([chapter 3 § 2.2](#322-the-canonical-form)). Pairing by position
  across the format is [#1485](https://github.com/Consultologist/Consultologist-Blazor/issues/1485).

  These `for` forms are refused; no published package uses them. Revisiting
  them is [#1475](https://github.com/Consultologist/Consultologist-Blazor/issues/1475) (Milestone 40).

**Equality in bodies.** Scriban has no `===`. A body `if` compares with Scriban's `==` and
`!=`, only within § 5.2.5's recorded facts. The `===`/`!==`-only rule is JSON Logic's
([chapter 3](#3-expressions)), which is where every value comparison lives.

#### 5.2.2 Built-ins

Built-ins are pure, and versioned like the built-in operations: each is listed in `requires`
with a caret range and in `lock.json` at its exact version.

| Built-in | Signature | Result | Null in |
|---|---|---|---|
| `string.upcase` | `(text: string \| text format) → same format` | invariant upper case | null (renders as nothing) |
| `string.downcase` | `(text: string \| text format) → same format` | invariant lower case | null |
| `string.capitalize` | `(text: string \| text format) → same format` | first character upper case, invariant | null |
| `string.strip` | `(text: string \| text format) → same format` | leading and trailing whitespace removed | null |
| `array.join` | `(list: list<string> \| list<text format>, separator: string literal) → string`, or the elements' text format | the elements joined by `separator` | null list gives null; a null element fails the node |
| `array.size` | `(list: list<any>) → number` | the element count | null |
| `date.to_string` | `(date: date, pattern: string literal) → string` | the date formatted by `pattern` | null |

- **`date.to_string` requires an explicit pattern,** a string literal (Scriban's `%` patterns,
  for example `"%d %B %Y"`). A date output without it renders as ISO `%Y-%m-%d`.
- **Refused:** `date.now`, random numbers and environment access (they break reproducibility);
  `truncate` (it cuts clinical text); `object.default` (it chooses text, which is a decision);
  every other built-in.
- **Null:** a null value output directly renders as nothing, and **a built-in given null returns
  null**, matching JSON Logic's rule that operations on null give null
  ([chapter 3](#3-expressions)). The one exception is `array.join`: a list holding a `null`
  element fails the node.

#### 5.2.3 Limits and carried-over behaviour

The limits are dialect constants, separate from `FormatBounds`
([chapter 1](#1-files-and-scopes)):

| Limit | Value | Past it |
|---|---|---|
| iterations per `for` | 1,000 | the render fails with a sentence (§ 5.11, R-L1) |
| `if` and `for` nesting | 15 deep | refused at publish (R-L2) |
| rendered output | 1 MiB (1,048,576 bytes, UTF-8) | the render fails with a sentence (R-L3) |
| steps per render | 100,000, an engine setting, [chapter 8 § 8.7](#87-retries-and-limits) | the render fails with a sentence (R-L4) |
| recursion | none possible | there's no `func` or `include`; snippet cycles are refused at publish (§ 5.3.2) |

A render failure fails the node (or the deliverable) as a definition error: no retry. A prompt
that fails to render is never sent. The failure follows the node's normal failure path, not
`onInvalid`, which is about replies.

**Carried over from version 30:**
- **strict variables:** reading a member that doesn't exist is refused at publish, and a render
  that meets one fails;
- **dates render as ISO** (`%Y-%m-%d`) unless formatted;
- **an empty list counts as false** where a truth value is read.

#### 5.2.4 The invariant culture

Every render runs in the invariant culture: English month and day names in `date.to_string`,
culture-free case mapping in `string.upcase`, `downcase` and `capitalize`, and invariant number
formatting. It's stated in the dialect and recorded in `lock.json`, so a host's culture can
never change a note's bytes or hashes.
A clinician's locale is [#1452](https://github.com/Consultologist/Consultologist-Blazor/issues/1452) (Milestone 40).

#### 5.2.5 A body `if` tests recorded facts only

A body `if`, in every template (snippet and macro bodies included), may test only facts the
engine has already decided and recorded:

| Fact | Written | Values |
|---|---|---|
| loop position | `for.first`, `for.last`, `for.index`, `for.even`, `for.odd` | as Scriban gives them |
| an item's or node's state | `s.state == "completed"` | the closed set `completed`, `skipped`, `not_run` ([chapter 6 § 6.2](#662-item-states)) |
| whether a check passed | `check.coverage.value.pass` | `true` or `false` |

- The tests combine with `!`, `&&`, `||` and parentheses.
- A `state` is compared only with a literal from the closed set.
- **Testing anything else is refused:** a data value, an input, a node's text, a run fact. The
  one exception is a renderer's body, which may test its own `value` (§ 5.5.1). The
  sentence points to the header forms: a part (§ 5.7), a snippet's `if` (§ 5.6) or a macro's `if`
  (§ 5.8). The revisit of this rule is [#1428](https://github.com/Consultologist/Consultologist-Blazor/issues/1428) (Milestone 40).
- **Completeness:** an `if` that branches on a `state` must handle every state or end with an
  `else`.
  An `else` keeps the template safe when a state is added later.

```scriban
{{~ for s in node.sections.items ~}}
{{~ if s.state == "completed" ~}}
{{ s.value }}
{{~ else if s.state == "skipped" ~}}
{{~ else ~}}
_{{ s.reason }}_
{{~ end ~}}
{{~ end ~}}
```

#### 5.2.6 Placement forms and whitespace

A **placement** is an output tag whose expression is a unit: `snippet.<id>.content`,
`part.<id>` or `macro.<id>` (each possibly qualified, `snippet.<folder>.<id>.content`).
A snippet's text is read as `.content`, like a node's or an input's (§ 5.6.3); it's a placement
because, like a part or a macro, it may be absent. Its text is entirely the
author's: no rule on how it starts or ends.

| Written | Result |
|---|---|
| `{{~ x }}` alone on its line, nothing after it | **allowed** (a block). When the unit is absent, an empty line remains. |
| `{{ x }}` anywhere inside a line, including against a word (`diabetes{{ x }}.`) | **allowed** (inline). Nothing is removed. |
| `{{ x }}` alone on its line | allowed: the indentation before it stays. The Editor writes `{{~ x }}` when inserting on an empty line. |
| `~}}` on a placement | refused: it removes the line's newline, joining two lines |
| `-` on a placement (`{{- x }}`, `{{ x -}}`) | refused: it removes blank lines between paragraphs |
| `{{~ x }}` inside a line | refused: it removes the space the author wrote before it |
| `{{~ x }}` with text after it on its line | refused: a block placement stands alone on its line |

Scriban's markers, as tested on 7.2.5: `~` removes spaces and tabs on its side, and on the right
also the one newline ending the line; `-` removes all whitespace on its side, blank lines
included.

**Statements and ordinary outputs** (`if`, `for`, `else`, `end`, `{{ node.x.content }}`) may
use `~` on either side, as the renderer templates need for byte-exact output (§ 5.5.5).
**`-` is refused on every tag,** not only placements, because it removes blank lines no preview
explains.

**The Editor** previews each placement with and without its unit, side by side. That's
information, not a warning.

### 5.3 What each template reads

#### 5.3.1 The table

| Site | Reads | Never |
|---|---|---|
| prompt | `node.*`, `input.*`, `check.*`, `item`, `pass`, `param` (in functions), `snippet.*`, `part.*` (its own node's), `macro.*`, the `renderer.` pipe, `run.*` | `profile.*`, `deliverable.*` |
| `rendered` node | `node.*`, `input.*`, `check.*`, `item`, `pass`, `param`, `snippet.*`, the `renderer.` pipe, `run.*` | `profile.*`, `part.*`, `macro.*`, `deliverable.*` |
| renderer | its piped `value` only | everything else, the `renderer.` pipe included |
| snippet body | what the template that places it reads (§ 5.3.2) | what that template may not read; and, placed in a macro body, a part's text or a macro instruction, `macro.*` and `part.*` (the guard, § 5.6.3) |
| part text | what its node's prompt reads, `macro.*` (§ 5.8.3) and `snippet.*` (under the guard) included; no `if` of its own | `profile.*`, `part.*` |
| macro instruction | what the placing prompt reads, `snippet.*` (under the guard) included, except `macro.*` and `part.*`; its own marker (§ 5.8.4) | `profile.*` |
| macro body | `node.*`, `input.*`, `check.*`, `item`, `pass`, `param`, `snippet.*`, the `renderer.` pipe, `run.*`, **plus `profile.*`** | `macro.*`, `part.*`, `deliverable.*` |
| deliverable | `node.*`, `input.*`, `snippet.*`, `check.*` (not its own), `profile.*`, `run.*`, the `renderer.` pipe | `item`/`pass` outside its own `for`, `part.*`, `macro.*`, `deliverable.*` |

The rules this table gives for macros and parts: a part's text may place a macro, which is then
offered only when both the part's `if` and the macro's own `if` hold (§ 5.8.3); snippets may be
placed in a part's text and in a macro's instruction, under the guard (§ 5.6.3); a renderer's body pipes
into no renderer, so chaining happens only at a use site (§ 5.5.2) and renderers form no graph
of their own.

- **`run.*`** is the set `run.date`, `run.id`, `run.package`, `run.engine`, read under § 5.4's run
  spot rule, piped to built-ins or renderers ([chapter 3](#3-expressions) defines the values). Inside a function, whether
  `run.*` is read directly or only as a parameter is [chapter 4](#4-loops-and-functions)'s.
- **`profile.*`** is never sent to a model, never read by a condition, and inside a function
  arrives only as a parameter that reaches macro bodies
  ([chapter 6 § 10](#610-the-profile)).
- **`check.*`** in a prompt or `rendered` node is a dependency edge like any read. A body `if`
  may test `check.x.value.pass` (§ 5.2.5).

#### 5.3.2 Snippet and macro bodies are templates

- **They're rendered in the scope where they're placed:** per item inside a loop, per pass
  inside a `while`, and in the function's sealed scope inside a function.
- **Their reads count as the placing node's reads.** They become dependency edges and are
  recorded under that node.
- **A snippet's body must check in every place it's placed.** Where a read isn't available
  (`item` outside a loop, `profile.*` in a prompt), that placement is refused with a sentence
  naming both the snippet and the place.
- **Cycles are refused at publish:** a snippet or macro that, through its reads and
  placements, reaches itself. A snippet placed in a part's text or a macro's instruction places
  no `part.*` or `macro.*` at all (the guard, § 5.6.3).
- **A macro body is rendered before literal substitution.** The model's reply is never rendered
  (§ 5.8.6).

### 5.4 Run spots and the two hashes

**The rule:** an output expression that reads `run.*` reads nothing else, for example
`{{ run.date | date.to_string "%d %B %Y" }}`. Each such expression is a **run spot**.
A body's read of a **run-dependent** value (a `computed` value or decision derived from `run.*`,
transitively, [chapter 3](#3-expressions)) is a run spot too, under the same rule.

- **A run spot may pipe to built-ins and to renderers** (`{{ run.date | renderer.long_date }}`).
  The spot covers the whole pipeline: the marker stands for its final output, and each
  renderer's sub-row is marked run-dependent.
- Run facts can't be tested in a body `if` (§ 5.2.5), can't feed a `for`, and can't be combined
  arithmetically (§ 5.2.1).

**Rendering, in three steps:**
1. Render the body with every read substituted **except the run spots**. Each spot becomes a
   marker naming its site: the literal text `{{run:<n>}}`, where `<n>` is the spot's 1-based
   position in the body's source order. It's fixed text, so the hash below is
   defined to the byte.
2. Hash that text: the **run-neutral hash**. With the same inputs, package and libraries it's
   identical across runs, whatever the date or job.
3. Put each spot's output at the **position recorded while rendering** step 1, and hash the
   result: the **sent-text hash**, which stays the body's main hash. The engine never searches
   the text for `{{run:<n>}}`: a value that happens to hold those characters is left as it is.

**Downstream text.** When a template reads a `rendered` or `computed` node, its run-neutral
render uses that node's run-neutral text (a `rendered` node) or treats the read as a run spot
(a run-dependent `computed` value). An agent's output has no neutral form: the model saw the
real values, so a template reading it is run-specific through that read.

**What a read of a run-dependent value does, by producer**:

| The value read | In the run-neutral render | Kept permanently in the record |
|---|---|---|
| a raw `run.*` fact (`run.date`) | a run spot | the spot's output |
| a run-dependent `computed` value | a run spot | its output only if it reads nothing but `run.*`; otherwise it follows 7-day retention ([chapter 9](#9-the-record)) |
| a run-dependent `rendered` node | that node's run-neutral text, its own spots kept as spots | as for that node's spots |
| a run-dependent `agent` node's output | the output itself: the model saw the real values | nothing extra; it follows 7-day retention |
| a run-dependent flow node's `ret` or call result | as its `ret`'s producer, by this table | as its `ret`'s producer |

**A body with no run spot** has one hash. The record's `runNeutralHash` is written only when the
body has a run spot, and is `null` otherwise ([chapter 9](#9-the-record)).

**The advance warning.** The Editor and publish say when a package reads `run.*` or a
run-dependent value, naming each spot. The warning text is W-1 (§ Refusals). The record side
(each spot's output and hash, the run facts kept once per run) is in [chapter 9](#9-the-record).

### 5.5 Renderers

A renderer turns a value into text. It's a package template, versioned with the package and
embedded in `resolve.json`.

#### 5.5.1 The file

`renderers/<id>.md`, listed in `renderers/index.json` ([chapter 1](#1-files-and-scopes)). Its header is judged by the schema [`renderer`](v31/schemas/renderer.schema.json).

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | no | the display name |
| `kind` | `"rendered"` | no | the mechanism; the folder gives the role |
| `description` | array of strings (lines) | yes: none | for people only, never sent to a model |
| `input` | a format name, or an inline schema | no | the format it accepts: any format, including `string` and text formats |
| `format` | `"plaintext"`, `"markdown_block"` or `"markdown_inline"` | no | what it returns: always a text format |

`description` is on every header ([chapter 1](#1-files-and-scopes)). **`input` is written like a
node's `format`:** a name, or an inline schema.

The body is a non-empty template that reads **only `value`**, the piped value (§ 5.3.1). A
renderer is reproducible by construction: the same value always gives the same bytes. Its body
pipes into no renderer (R-N7); chaining happens at a use site (§ 5.5.2).

The built-in `concept_bullets`, as the registry publishes it in
[`v31/renderers/concept_bullets.md`](v31/renderers/concept_bullets.md) (its `value` is a
`concept_list`, whose list is `value.concepts`):

```
---
{ "label": "Concepts as bullets", "kind": "rendered", "description": null,
  "input": "concept_list", "format": "markdown_block" }
---
{{~ if value.concepts.size == 0 ~}}
(none){{~ else ~}}
{{~ for c in value.concepts ~}}
{{~ if c.isSnomedConcept ~}}
- {{ c.term }} ({{ c.type }}) - {{ c.id }}{{ if !c.isActive }} [not active SNOMED concept]{{ end }}{{ if !for.last }}
{{ end ~}}
{{~ else ~}}
- {{ c.term }} [not SNOMED concept]{{ if !for.last }}
{{ end ~}}
{{~ end ~}}
{{~ end ~}}
{{~ end ~}}
```

(The first `if` above tests a list's size, which § 5.2.5 refuses in other bodies. **A renderer's
body may test its own `value` in an `if`**: a renderer decides nothing that's
recorded, since its whole output is a function of `value`, hashed as one sub-row. Without this,
the two built-in renderers can't be written. **In that test it may read a list's size as
`.size`** (`value.concepts.size == 0`), as the built-in renderers do.)

#### 5.5.2 The call: a pipe to the root `renderer.`

- **The one call form is the pipe:** `{{ node.extract_patient_concepts.value | renderer.concept_bullets }}`.
  The call form (`renderer.concept_bullets(x)`) is refused.
- **The root `renderer.`** can't collide with Scriban's built-ins or with `node.`, `check.`,
  `input.`, `snippet.` and `macro.`.
- **`.value` is the input,** the typed object: `node.x.value | renderer.concept_bullets`. What a
  specVersion 30 pipe becomes is [chapter 10 § 10.2](#102-pipes-body-tests-and-the-test-macro)'s.
- **Typed at publish:** the piped value's format must match the renderer's `input`. The
  result's format is the renderer's `format`.
- **Chaining is allowed where a template uses renderers**: `{{ node.extract.value | renderer.concept_list | renderer.bullets }}`.
  Each step's output type is checked against the next renderer's `input` at publish, and each
  step is its own sub-row (`…/render:1`, `…/render:2`, § 5.5.5).
- **`run.*` may pipe to renderers** (`{{ run.date | renderer.long_date }}`): the run spot covers
  the whole pipeline (§ 5.4).
- **Allowed in:** prompts, `rendered` nodes, snippet bodies, part text, macro instructions,
  macro bodies and deliverables. **Not in renderer bodies:** a renderer's own body may not pipe
  into another renderer (R-N7).

#### 5.5.3 Built-in renderers

`concept_bullets` and `concept_context` are written as templates.
The C# renderers (`ConceptRenderers`, `WorkflowConceptRenderers`) **stay in version 31 as the
byte-equivalence reference** and are removed in Milestone 40 ([#1404](https://github.com/Consultologist/Consultologist-Blazor/issues/1404)).

- **The proof:** a test renders each template and compares it byte for byte with the C# output,
  on the Editor's fixture and every edge case (empty, not SNOMED, inactive, with and without
  `support`). The pitfalls are booleans (`True`/`False`), line endings (no trailing newline) and
  `concept_context`'s `source` and blank `support`.
- **The built-in renderers are Scriban templates in the package-format registry**, [`v31/renderers/concept_bullets.md`](v31/renderers/concept_bullets.md) and [`v31/renderers/concept_context.md`](v31/renderers/concept_context.md): read-only, versioned and locked like the operations (in `requires`, and in
  `lock.json`'s `builtins`, chapter 7), and embedded in
  `resolve.json`. **Their ids are reserved:** a package renderer may not take one (R-N6,
  [chapter 1](#1-files-and-scopes)). Scoping between built-in, catalogue and package ids is
  [#1469](https://github.com/Consultologist/Consultologist-Blazor/issues/1469).
- **`concept_context` reads `source` on each concept,** a member the `concept_list` format does not declare: the value piped into it is the stored concept list, with `source` stamped from the producing node, so the format and the stored value differ by that one member.
- **A loop's `.content`** keeps version 30's bytes (`## label`, then the text, joined by blank
  lines) as a standard rendering typed `markdown_block`.

#### 5.5.4 Media-type warnings

Each text format carries `contentMediaType`, and Markdown carries `x-markdown: block | inline`
([chapter 2](#2-types-and-inputs)). Publish warns (W-2) when a `markdown_block` renderer is
piped inside a line.

#### 5.5.5 In the record and History

A renderer use is not a node: it isn't scheduled, waits on nothing and can't fail on its own.
It's a **sub-row of the node (or deliverable) that uses it**, one per pipe use, in source order,
per instance, **keyed by the use's position** (`node.identify_problem/render:1`); inside a loop, the item path comes
first, then the render site (`node.sections.paragraphs.draft_paragraph:2/1/render:1`).
Each holds the renderer's id, its template hash, the source read, the input hash and size, and
the output hash and length.
A chain gives one sub-row per step, in pipe order. Every key is written with its root
([chapter 1](#1-files-and-scopes)).
The text itself follows the 7-day retention sweep. History shows the sub-rows under the node
when it's expanded. The diagram draws them inside the node's frame ([chapter 8 § 8.14](#814-what-belongs-to-the-app)).

### 5.6 Snippets

A snippet is **input text: the model reads it**, and may use, paraphrase or ignore it. Its body is a
template (§ 5.3.2).

#### 5.6.1 A single snippet

`snippets/<id>.md`, whose header is judged by the schema [`snippet`](v31/schemas/snippet.schema.json):

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | no | the display name |
| `description` | array of strings | yes: none | for people only, never sent to a model |
| `if` | JSON Logic | yes: always | whether the snippet's text is placed |
| `format` | `"plaintext"`, `"markdown_block"` or `"markdown_inline"` | no | the body's text format, so a deliverable's strict reads ([chapter 6 § 6.4](#664-strict-formats)) can check it |

The body must be non-empty and suit `format`. **A snippet's header is these four members,** with
a text format ([chapter 1](#1-files-and-scopes)). Data types for snippets are [#1467](https://github.com/Consultologist/Consultologist-Blazor/issues/1467).

#### 5.6.2 Snippet folders

A snippet folder's `index.json`, judged by the schema [`snippet-folder-index`](v31/schemas/snippet-folder-index.schema.json), holds `description`, `items` (the ids, in order) and a
**`format`**: each item's header is its **value**, checked against that format,
and its body is its **content**. A header's `label` no longer names the item; the loop's
`itemLabel` does ([chapter 4](#4-loops-and-functions)).

```
snippets/standards/index.json
{ "description": [ "The nine standard sections of a consult note, in order." ],
  "items": [ "hpi", "pmh", "medications", "allergies", "social_history",
             "family_history", "exam", "investigations", "assessment_plan" ],
  "format": "standard_section" }

snippets/standards/hpi.md
---
{ "title": "History of Present Illness" }
---
Chronological prose narrative. Open with a one-sentence orientation to the patient …
```

- A folder is read by a loop (`"in": "snippet.standards"`), where `item.value.title` is the
  header and `item.content` the body, rendered in the loop's scope.
- **Folder items carry no `if`**: a folder item's header is data, so a
  folder's size is its number of files, and conditional inclusion of a folder item is an `if`
  branch in the loop body, as `example-conditional-sections` does with `applies`. Dynamic folder
  sizes are [#1468](https://github.com/Consultologist/Consultologist-Blazor/issues/1468).
- **A folder item's body may be empty**: its `item.content` is then `""`, and its header
  still carries the value. Revisiting this is [#1484](https://github.com/Consultologist/Consultologist-Blazor/issues/1484).

#### 5.6.3 Placing a snippet

- **A snippet is read as `snippet.<id>.content`**, the same member rule as
  `input.<id>.content` and `node.<id>.content`: `{{~ snippet.<id>.content }}` alone on a line, or
  `{{ snippet.<id>.content }}` inside a line (§ 5.2.6). A bare `snippet.<id>` is refused (R-S3). A
  folder item outside a loop is `snippet.<folder>.<id>.content`.
- **Its `if` is evaluated at each placement**, under that place's read rules (§ 5.3.1): a
  snippet placed in two prompts is decided twice, and its `if` must be readable at every place
  that places it (R-R3).
- When its `if` holds, its rendered body is spliced in. When it doesn't, nothing is, and the
  decision is recorded with its reason.
- **Placed in:** prompts, `rendered` nodes, other snippets, macro bodies, deliverables, **a
  part's text and a macro's instruction**.
- **The guard:** a snippet placed in a part's text or a macro's instruction may not place
  `part.*` or `macro.*`, directly or through a snippet it places (R-S4). Otherwise it reads what
  its host reads. This rules out a part inside a part and a macro inside an instruction.
  Narrowing the guard to refuse only an actual cycle is [#1476](https://github.com/Consultologist/Consultologist-Blazor/issues/1476) (Milestone 40).

### 5.7 Parts

A part is **short conditional prompt text that belongs to one agent node**.
Longer or shared conditional text is a snippet with an `if`.

#### 5.7.1 The member

`parts`, in an agent node's header, required:

| Member | Type | Null | Meaning |
|---|---|---|---|
| `parts` | object keyed by part id | yes: none | the node's parts. `{}` also means none. |
| `parts.<id>.if` | JSON Logic | yes: always | whether the part's text is placed |
| `parts.<id>.text` | array of strings | no | the lines, joined with `\n`; a blank line is `""` |

- A part id follows the one id rule (`^[a-z][a-z0-9_]*`, at most 64 characters) and the reserved
  list ([chapter 1](#1-files-and-scopes)). The member `parts` and the root `part.<id>` keep their
  names.
- `text` is always an array, never a single string. No newline is added after the last line.
- The text may use presentation templating (§ 5.3.1), may place a macro (§ 5.8.3) and snippets
  (under the guard, § 5.6.3), but has no `if` and places no `part.*`.
- Parts are allowed on `kind: agent` nodes only.

#### 5.7.2 Placing a part

The body places each part with `{{~ part.<id> }}` or `{{ part.<id> }}` (§ 5.2.6).
- A placement naming no declared part is refused (R-P1).
- A declared part the body never places is refused (R-P2).
- **Each part is placed exactly once** (R-P3): a part placed twice would
  record one decision for two texts.

```
nodes/standards/section_instructions.md
---
{ "kind": "agent", "producer": "generated", "label": "Applying section instructions", "description": null,
  "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "onInvalid": "fail", "failIfEmpty": null, "ordered": false,
  "parts": {
    "no_standard": {
      "if": { "blank": [ { "var": "item.content" } ] },
      "text": [ "No changes. Preserve the patient-updated draft's clinical content and",
                "produce polished final prose for this section." ] } },
  … }
---
Requested section:
{{ item.value.title }}

Section standard and section-specific instructions:
{{~ part.no_standard }}
{{ item.content }}
```

(A body `if` that tests `(item.content | string.strip) == ""` is refused (§ 5.2.5). The test
moves to the part's `if`, using the `blank` operation ([chapter 3](#3-expressions)), and is
recorded. How the migration from version 30 rewrites such a test is [chapter 10 § 10.2](#102-pipes-body-tests-and-the-test-macro)'s.)

### 5.8 Macros

A macro is **output text: guaranteed exact, placed by the model.** The model decides only
**where** it goes. Whether it applies is decided before the prompt is sent, by its header `if`,
and recorded.

| | Snippet | Macro |
|---|---|---|
| Side | input: the model reads it | output: it ends up in the result |
| The model | may use, paraphrase or ignore it | only places its marker |
| The text | part of the prompt | inserted verbatim, never rewritten |

#### 5.8.1 The file

`macros/<id>.md`, or `macros/<folder>/<id>.md`, whose header is judged by the schema [`macro`](v31/schemas/macro.schema.json):

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | no | the display name |
| `description` | array of strings | yes: none | for people only, never sent to a model |
| `if` | JSON Logic | yes: always triggered | whether the macro is offered |
| `format` | `"plaintext"`, `"markdown_block"` or `"markdown_inline"` | no | the body's text format |
| `instruction` | array of strings | no | where to place it, joined with `\n` |

- `layout` and `at:` placements are gone (§ 5.10).
- The body is the macro's content: non-empty, a template (§ 5.3.1), checked against `format`.

**A macro folder's `index.json`** (schema [`macro-folder-index`](v31/schemas/macro-folder-index.schema.json)) carries `description`, `items` and an **`if`**
(`null` for always). When a folder and a macro both have an `if`, **both must hold**, and the
record shows which was false. The folder is a namespace: `macro.<folder>.<id>`.

#### 5.8.2 Whether: the header `if`

- The `if` may read anything a condition reads ([chapter 3](#3-expressions)), typically a
  **classifier node**: an ordinary `kind: agent` node (`producer: "generated"`) with the built-in
  format `judgement` (`{ answer: boolean, reason: plaintext }`), read as
  `node.<id>.value.answer`; the record and History show its `reason` beside the answer.
- **It's evaluated in the scope where the macro is placed:** per item when it reads a node in
  the loop body, once when it reads a node outside. Inside a function it's the function's
  sealed scope, and the `if` may not name a `param` (R-M10).
- **Per-run choices are optional boolean inputs** the `if` reads:
  a choice that defaults off is `{ "===": [ { "var": "input.x.value" }, true ] }`; one that
  defaults on is `{ "!==": [ { "var": "input.x.value" }, false ] }`, which holds while the input
  is unset. An explicit `default` is [#1456](https://github.com/Consultologist/Consultologist-Blazor/issues/1456) (Milestone 40).
- **A per-run choice input takes the macro's id and label**, and is joined
  with `and` to any existing `if`. The Create page shows three states (unset, yes, no), and unset
  is sent as `null`. A migrated choice whose id is already an input's id gets the suffix
  `_macro` (`letrozole` → `letrozole_macro`), reported by the migration.
- One classifier per macro, per node, per item. A classifier answering several questions is
  [#1416](https://github.com/Consultologist/Consultologist-Blazor/issues/1416) (Milestone 40).

#### 5.8.3 Where: placing the instruction

- The prompt places the macro with `{{~ macro.<id> }}` or `{{ macro.<id> }}` (§ 5.2.6).
- **Only triggered macros reach the prompt.** A triggered placement renders the instruction; an
  untriggered one renders nothing.
- The instruction says only where: never "if …, otherwise nothing".
- **Only `kind: agent` nodes place macros**: in the prompt, in one of the node's parts' text, or
  through a snippet placed in the prompt. A `rendered` or `computed` node, a deliverable, a macro
  instruction, a macro body, and a snippet placed in a part's text or a macro's instruction place
  none.
- **A part's text may place a macro**. The macro is then offered only when
  both the part's `if` and the macro's own `if` hold, and its row links both decisions (§ 5.8.8).
- **The node's `producer` is `generated` and its `format` a text format** (`plaintext`,
  `markdown_block`, `markdown_inline`). A marker has no place in an object reply.
- **Format match**: Markdown content into a `plaintext` node is refused
  (R-M5); a `markdown_block` macro is refused in a `markdown_inline` node; a `plaintext`
  macro in a Markdown node is escaped as plain text is in deliverables
  ([chapter 6 § 6.4](#664-strict-formats)), and the content hash is
  taken after escaping.
- **Two nodes may place the same macro;** if both trigger it, the text appears twice. **A macro
  is placed once per template,** counting the text of the node's parts (R-M7). The same macro twice in one template is [#1457](https://github.com/Consultologist/Consultologist-Blazor/issues/1457) (Milestone 40).

#### 5.8.4 The marker

**The marker is `macro.<id>.content`** (qualified: `macro.<folder>.<id>.content`). Each
instruction contains its own macro's marker **exactly once**, in one of two forms, and no other
macro's marker:

| Form in the instruction | What the model must write |
|---|---|
| `{{~ macro.<id>.content }}` alone on a line of the instruction | the marker alone on its own line (a block) |
| `{{ macro.<id>.content }}` inside a line | the marker inside a sentence (inline) |

When the instruction is rendered, **its marker renders as its own literal source text**
(`macro.<id>.content` between its braces), so the model sees exactly the marker to write. The
dialect treats the marker as literal inside an instruction.

```
macros/letrozole_prescription_text.md
---
{ "label": "Letrozole prescription text", "description": null,
  "if": { "===": [ { "var": "node.prescribes_letrozole.value.answer" }, true ] },
  "format": "plaintext",
  "instruction": [
    "Place the following marker, alone on its own line, in the assessment and plan,",
    "after the medication discussion:",
    "{{~ macro.letrozole_prescription_text.content }}" ] }
---
Discussed side effects including: hot flashes, joint or muscle pain, fatigue, headache, nausea,
and bone thinning. Advised to monitor side effects.
```

The classifier is an ordinary node file, for example `nodes/standards/prescribes_letrozole.md`
(`kind: agent`, `producer: "generated"`, format `judgement`), and shows in the graph and the record like any node.

#### 5.8.5 Order

**`ordered`, `true` or `false`, is a required member of every `kind: agent` node header**. `true` requires the triggered markers in the reply in the order their
placements appear in the prompt; `false` accepts any order.

#### 5.8.6 Processing the reply

The reply is **never rendered**. Rendering it would run whatever the model wrote between braces
(template injection), break legitimate braces and run code no checker saw. The engine replaces
exact marker strings literally.

**1. The check:**
- every triggered macro's marker appears **exactly once**, in the form its instruction asked
  for;
- no marker of an untriggered macro appears;
- a marker naming an unknown macro is an error;
- near-misses (`{{macro.x.content}}`, `{{ macro.X.content }}`) aren't markers: the triggered
  macro then counts as missing;
- with `ordered: true`, the markers appear in order.

**2. Invalid** (each goes to the node's `onInvalid`: `retry` asks again, `fail` fails the job
naming the macro):
- a marker missing, repeated, unknown, or out of order;
- `{{~ … }}` written inside a sentence;
- `{{ … }}` written alone on a line when the block form was asked for;
- any text other than spaces after a block marker on its line.

**3. The replacement:**

| Marker in the reply | What the engine does |
|---|---|
| `{{~ macro.x.content }}` alone on its line | removes the indentation before the marker, replaces the marker with the macro's rendered body, **removes any spaces after it**, and keeps the line's newline |
| `{{ macro.x.content }}` inside a line | replaces the marker exactly where it is |

Trailing spaces after a block marker are removed, never a failure: in Markdown two spaces make a
hard line break, and in plain text they'd still be in the hashed bytes.

**4. The body** is rendered by the engine, in the placing scope, **before** substitution
(§ 5.3.2). It's the package's own text, checked at publish. **A body that reads `profile.*`
makes the node's value profile-carrying** ([chapter 3 § 4.6](#346-profile-carrying-is-contagious)): a prompt, a part or a
condition that reads that value afterwards is refused at publish (R-R6); a deliverable may read it.

**A retry message never quotes the reply**: a `retry` sends fixed engine text
naming each macro and what was wrong, since the reply may hold patient text.

#### 5.8.7 What publish checks

- **Each instruction:** its own marker exactly once, in an allowed form; no other macro's
  marker; no `macro.*` or `part.*` placement; snippets only under the guard (§ 5.6.3); no
  `profile.*`.
- **Each template:** a macro placed at most once, counting its parts' text.
- **Each body:** it suits `format` (no Markdown in a `plaintext` macro); no markers; no
  placement of `macro.*` or `part.*`; its reads within § 5.3.1's macro-body column; no cycles.

#### 5.8.8 In the record

A **macro row per macro per node instance**,
a sub-row keyed `…/macro:<id>`, with its decision at `…/if:<site>`, for example `node.standards.assessment:7/macro:letrozole_prescription_text`
and `node.standards.assessment:7/if:macro.letrozole_prescription_text`:
- whether it was **offered**, linking to its `if` decision (and the folder's, and the part's when
  a part's text placed it) and to the classifier's row;
- whether it was **placed**: its marker found exactly once;
- its **content hash** (the rendered body);
- when the marker was missing, repeated or altered, the node's `onInvalid` outcome, on the
  node's row.

Under a loop the rows are per item, and History and the lineage show them under each
item. The shape of the rows is [chapter 9](#9-the-record)'s.

### 5.9 Decisions recorded for snippets and parts

Every header `if` decision (a snippet's, a part's, a macro's, a macro folder's) is an entry in
the job's one `decisions` list ([chapter 9](#9-the-record)): its site, the printed
condition, its result, a hash of each value it read, whether it was run-dependent, and an
`expressionHash` of its canonical JSON Logic. Rows link to their decisions by id. Reasons read,
for example, *"skipped: input.kind.value = "table" is false"*; the
printer shows `=` and `≠` ([chapter 3](#3-expressions), [chapter 9](#9-the-record)). A placed unit's
text is recorded by hash under the node that placed it.

### 5.10 What changes from version 30

| At 30 | At 31 |
|---|---|
| Scriban conditions in bodies (`{{ if input.x == "y" }}`) decide what the model sees, unrecorded | a body `if` tests recorded facts only; decisions are parts, snippet `if`s and macro `if`s, recorded |
| any Scriban built-in the walker accepts, arithmetic, assignment | the dialect's closed list (§ 5.2) |
| the host's culture | the invariant culture |
| `concept_bullets`, `concept_context` are C#, piped the node: `node.x \| concept_bullets` | renderers are templates in `renderers/`, piped `.value`: `node.x.value \| renderer.concept_bullets` |
| a snippet header holds `label`, which names folder items | a single snippet has `label`, `description`, `if` and `format`; a folder item's header is typed data, with no `if`; `itemLabel` names items |
| `{{ snippet.x.content }}`, placed in prompts and deliverables | unchanged, now a placement (§ 5.2.6); also placed in parts' text and macro instructions, under the guard |
| `prose`, and the `agent_*` formats | the plain format of the same shape (`plaintext`, `markdown_block`, `markdown_inline`); the node's `producer` says a model wrote it ([chapter 2 § 1.3](#213-producer)) |
| a macro's `instruction` is one string, often "if …, otherwise nothing"; the prompt places `{{ macro.x.prompt }}` | `instruction` is lines saying only where, with the marker; `if` decides whether; `{{ macro.x }}` |
| `at: before`, `after`, `append`, item-level placements, deliverable macros | removed: fixed text is a snippet read in the deliverable template |
| optional at most once, required exactly once | triggered exactly once, untriggered never |
| prompt hashes vary with run facts and nothing says so | run spots, with a run-neutral hash beside the sent-text hash |

### 5.11 Refusals

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format. `<…>`
marks a placeholder.

**The dialect**
- R-D1: *"\<Subject\> uses \<construct\> at line \<n\>; templates present text and may not use assignment, capture, func, include, import, with, wrap, while, break, continue, case, tablerow or arithmetic."*
- R-D2: *"\<Subject\> calls \<built-in\> at line \<n\>; the allowed built-ins are string.upcase, string.downcase, string.capitalize, string.strip, array.join, array.size and date.to_string."*
- R-D3: *"\<Subject\> calls truncate at line \<n\>; truncate cuts clinical text."*
- R-D4: *"\<Subject\> calls object.default at line \<n\>; choosing text is a decision: put it in a header condition."*
- R-D5: *"\<Subject\> calls date.to_string at line \<n\> without a pattern; write the pattern, for example "%d %B %Y"."*
- R-D6: *"\<Subject\> runs a for over \<expr\> at line \<n\>; a for runs over a list."*
- R-D7: *"\<Subject\> tests \<expr\> in a body if at line \<n\>; a body if tests only loop position, state and whether a check passed. Decide it in a header: a part, a snippet's if or a macro's if."*
- R-D8: *"Deliverable 'consult' branches on part.state and handles completed and skipped, but not not_run: add it or an else."*, generalised as *"\<Subject\> branches on \<expr\> and handles \<states\>, but not \<missing\>: add it or an else."*
- R-D9: *"\<Subject\> compares \<expr\> with "\<value\>" at line \<n\>; a state is completed, skipped or not_run."*
- R-D10: *"\<Subject\> reads \<path\> at line \<n\>, which \<format or root\> doesn't have."*
- R-D11: *"\<Subject\> reads \<path\>[\<n\>] at line \<n\>, a position in a list; lists are read whole, with a for, or by identity through .items."*

**Limits**
- R-L1: *"\<Subject\> stopped rendering: the for at line \<n\> reached 1,000 iterations."*
- R-L2: *"\<Subject\> nests if and for \<n\> deep at line \<m\>; the limit is 15."*
- R-L3: *"\<Subject\> stopped rendering: its output passed 1 MiB."*
- R-L4: *"\<Subject\> stopped rendering: it took more than \<limit\> steps."*

**Placements**
- R-W1: *"\<Subject\> places \<unit\> with ~}} at line \<n\>; it removes the line's newline, joining two lines. Use {{~ \<unit\> }} alone on a line."*
- R-W2: *"\<Subject\> places \<unit\> with - at line \<n\>; it removes blank lines between paragraphs."*
- R-W3: *"\<Subject\> places {{~ \<unit\> }} inside a line at line \<n\>; it removes the space before it. Use {{ \<unit\> }}."*
- R-W4: *"\<Subject\> has text after {{~ \<unit\> }} at line \<n\>; a block placement stands alone on its line."*
- R-W5 (§ 5.2.6): *"\<Subject\> uses - at line \<n\>; it removes blank lines between paragraphs. Use ~."*

**Reads**
- R-R1: *"\<Subject\> reads \<root\> at line \<n\>; \<site\> reads \<allowed roots\>."*
- R-R2: *"Node '\<id\>' reads profile.\<field\>; the clinician's profile is never sent to a model. Read it in a deliverable or a macro body."*
- R-R3: *"Snippet '\<id\>' reads \<path\>, which isn't available where \<subject\> places it at line \<n\>."*
- R-R4: *"\<Kind\> '\<id\>' reaches itself: \<chain\>."*
- R-R6: *"\<Subject\> reads \<path\> at line \<n\>, which carries profile text through macro '\<id\>'; a prompt or a part doesn't read profile text. Read it in a deliverable."*
- R-R5: *"\<Subject\> reads \<path\> and run.\<fact\> in one output at line \<n\>; an output that reads a run fact reads nothing else."* (also for a run-dependent value: *"… reads \<path\> and the run-dependent \<value\> in one output …"*)

**Renderers**
- R-N1: *"\<Subject\> pipes \<source\> (\<format\>) into renderer.\<id\>, which renders \<input format\>."*, for example *"Node 'identify_problem' pipes node.plan.value (section_plan) into renderer.concept_bullets, which renders concept_list."*
- R-N2: *"Renderer '\<id\>' declares format \<format\>; a renderer returns plaintext, markdown_block or markdown_inline."*
- R-N3: *"Renderer '\<id\>' reads \<root\>; a renderer reads only the value piped into it."*
- R-N4: *"\<Subject\> calls renderer.\<id\> at line \<n\>; pipe into it: \<value\> | renderer.\<id\>."*
- R-N5: *"\<Subject\> pipes into renderer.\<id\>, which this package doesn't define."*
- R-N6: *"Renderer '\<id\>' takes the id of a built-in renderer."*
- R-N7: *"Renderer '\<id\>' pipes into renderer.\<other\> at line \<n\>; chain renderers where they're used, not inside a renderer."*
- R-N8: *"\<Subject\> pipes renderer.\<id\> (\<format\>) into renderer.\<next\>, which renders \<input format\>."*

**Snippets**
- R-S1: *"\<Subject\> places snippet.\<id\>, which this package doesn't define."*
- R-S2: *"Snippet '\<folder\>/\<id\>' has a header that doesn't match format \<format\>: \<schema error\>."*
- R-S3 (§ 5.6.3): *"\<Subject\> reads snippet.\<id\> at line \<n\>; read its text as snippet.\<id\>.content."*
- R-S4 (§ 5.6.3): *"Snippet '\<id\>' places \<part.\* or macro.\*\>, and \<subject\> places it in \<a part's text | a macro's instruction\>; a snippet placed there doesn't place parts or macros."*

**Parts**
- R-P1: *"Node '\<id\>' places part.\<name\>, which its header doesn't declare."*
- R-P2: *"Node '\<id\>' declares part '\<name\>' but never places it."*
- R-P3: *"Node '\<id\>' places part.\<name\> \<n\> times; place a part once."*
- R-P4: *"Node '\<id\>' declares parts, and only agent nodes have parts."*
- R-P5: *"Part '\<name\>' of node '\<id\>' uses \<if or part.\*\>; a part's text only presents."*

**Macros**
- R-M1: *"Macro '\<id\>' places macro.\<other\> in its body; a macro body is output text, written after the model replies. Put shared text in a snippet and place it in both."* (and for `part.*`: *"Macro '\<id\>' places part.\<name\> in its body; …"*, the rest unchanged)
- R-M2: *"Macro '\<id\>' places \<macro.\* or part.\*\> in its instruction; combine instructions by placing each macro in the prompt."*
- R-M3: *"Macro '\<id\>' has \<n\> markers in its instruction; it must hold {{~ macro.\<id\>.content }} or {{ macro.\<id\>.content }} exactly once."*
- R-M4: *"Macro '\<id\>' has the marker of macro '\<other\>' in its instruction."*
- R-M5: *"Node '\<id\>' places macro.\<macro\>, whose format is \<format\>; an \<node format\> node takes \<allowed\>."*
- R-M6: *"\<Subject\> places macro.\<id\>; only agent nodes place macros, in their prompt or a part's text."*
- R-M7: *"\<Subject\> places macro.\<id\> twice, counting its parts' text; place a macro once in a template."*
- R-M11: *"Node '\<id\>' places macro.\<macro\>, and returns \<format\>; macros are placed only in agent nodes returning a text format."*
- R-M8: *"Macro '\<id\>' has format \<format\>, and its body \<reason, e.g. writes Markdown at line 2\>."*
- R-M9: *"Macro '\<id\>' has a marker in its body; a body is the text that replaces the marker."*
- R-M10: *"Macro '\<id\>' reads param.\<name\> in its if; decide outside the function and pass the answer in, or classify inside it."*

**Invalid replies** (sent to `onInvalid`, recorded on the node's row)
- V-1: *"The reply has no marker for macro '\<id\>'."*
- V-2: *"The reply has the marker for macro '\<id\>' \<n\> times."*
- V-3: *"The reply has a marker for macro '\<id\>', which wasn't offered."*
- V-4: *"The reply has a marker for '\<id\>', which isn't a macro."*
- V-5: *"The reply writes the marker for macro '\<id\>' \<inside a sentence | alone on a line\>, but it was asked for \<alone on a line | inside a sentence\>."*
- V-6: *"The reply has text after the marker for macro '\<id\>' on its line."*
- V-7: *"The reply has the markers out of order: '\<id\>' before '\<other\>'."*

**Warnings** (publish and the Editor; not refusals)
- W-1: *"\<Subject\> reads \<run.fact or run-dependent value\> at line \<n\>. Its main hash differs between runs; runs are compared on the run-neutral hash."*
- W-2: *"\<Subject\> pipes renderer.\<id\>, a markdown_block, inside a line at line \<n\>."*

## 6. Checks, deliverables and the profile

This chapter defines verification and output: checks in their own folder and root, check loops
aligned with a production loop's items and the aggregate checks that gate a document, deliverables
as files with composition templates, derived sources, authored headings, `whenEmpty`, gating and
delivery, and the closed list of profile fields a template may read. The template language itself,
and what each template may read, is [chapter 5](#5-templates-and-macros). Personal macros are
[#1417](https://github.com/Consultologist/Consultologist-Blazor/issues/1417) (Milestone 40): a clinician's fixed boilerplate is a profile field (§ 6.10), not a
macro.

### 6.1 Checks: the folder and the root

A check is **verification, not production:** nothing it produces goes into a note. It has its
own folder, root, record section and History section.

```
nodes/     production: agents, rendered and computed nodes, loops, branches, calls
checks/    verification: what gates a deliverable
  index.json
  coverage.md
```

- **The root is `check.<id>`,** singular like `node.`; the folder is plural like `nodes/`.
- **Separate namespaces:** `node.coverage` and `check.coverage` may both exist. Record keys are
  rooted at `node.` or `check.`, with the qualified-key rules inside each
  ([chapter 1](#1-files-and-scopes)).
- **The folder gives the role, `kind` the mechanism, and `format` is always `check_result`.**
  In version 31 the mechanism is `kind: computed`, one JSON Logic expression in the member
  `expression`.
  A model-judged check (`kind: agent`) is left for later.
- **`op` and `with` are retired.** The operations are called inside the expression.
- **The body is empty** ([chapter 1](#1-files-and-scopes)).

#### 6.1.1 The file

`checks/<id>.md` holds the members of a `computed` node ([chapter 3](#3-expressions)), with the following; its header is judged by the schema [`check`](v31/schemas/check.schema.json):

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | no | the display name |
| `description` | array of strings | yes: none | for people only |
| `kind` | `"computed"` | no | the mechanism |
| `format` | `"check_result"` | no | always; any other value is refused (R-C2) |
| `reproducible` | `true` | no | as on every node header, checked against the derived value ([chapter 1](#1-files-and-scopes)) |
| `producer` | `"computed"` | no | as on every node header, checked against the kind ([chapter 2 § 1.3](#213-producer)) |
| `modelDerived` | boolean | no | as on every node header, checked against the derived value: `true` when the check reads model output, directly or through other values ([chapter 2 § 1.2](#212-the-contagious-flags-run-dependent-and-model-derived)) |
| `runDependent` | boolean | no | as on every node header, checked against the derived value: `true` when the check reads `run.*` or a run-dependent value ([chapter 2 § 1.2](#212-the-contagious-flags-run-dependent-and-model-derived)) |
| `profileCarrying` | boolean | no | as on every node header, checked against the derived value: `true` when the check reads a profile-carrying value ([chapter 3 § 4.6](#346-profile-carrying-is-contagious)) |
| `if` | JSON Logic | yes: always | whether the check runs; in a check loop, typically skips unrun items. **A gate check's `if`** (a check a deliverable's `check` names) **may not read a value that can be `null`** (R-C10), so a gate is never skipped by a missing value |
| `expression` | JSON Logic | no | an expression returning `check_result` (§ 6.2) |

```
checks/coverage.md
---
{ "kind": "computed", "producer": "computed", "label": "Terms covered", "description": null, "format": "check_result",
  "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null,
  "expression": { "terms_subset": [ { "var": "node.extract_input_terms.value" },
                                    { "var": "node.extract_note_terms.value" },
                                    "The note does not cover every clinical term found in the referral." ] } }
---
```

#### 6.1.2 Who reads checks, and what checks read

- **Nodes may read checks:** a prompt, a `rendered` node, a `computed` node or a condition may
  read `check.x.value`, as a dependency edge like any read.
- **Deliverables may read checks,** except a check on that deliverable (§ 6.6.3).
- **Checks may read** nodes, inputs, other checks, and **a deliverable's `.content`** (that's
  how a document is proofread before release, § 6.7). A deliverable is readable by checks only.
- **A deliverable's `check` names only a `check.*`,** never a production node.
- **`check_result` as data:** a `computed` node in `nodes/` (or inside a function) may return a
  `check_result` as data only. It gates nothing: **only a `check.*` can gate a deliverable**.
- **Scheduling is unchanged:** a check sits in the dependency graph after what it reads, and is
  recorded with its hashes. A failing check never stops production; its effect comes only
  through what reads it.

### 6.2 `check_result` and the three check operations

#### 6.2.1 The format

`check_result` is an object format in the package-format registry's built-ins
([chapter 2](#2-types-and-inputs), [`v31/formats/check_result.json`](v31/formats/check_result.json)); a check that returns it has `producer: "computed"`. Version 30's `terms_subset`
output is `{ pass, uncovered, untested }`. Version 31 has two more operations returning it, so
there's **one shape for all three, every member present**:

```jsonc
{ "type": "object", "additionalProperties": false,
  "required": [ "pass", "message", "uncovered", "untested", "passed", "total" ],
  "properties": {
    "pass":      { "type": "boolean" },
    "message":   { "type": [ "string", "null" ] },
    "uncovered": { "type": [ "array", "null" ], "items": { "type": "string" } },
    "untested":  { "type": [ "array", "null" ], "items": { "type": "string" } },
    "passed":    { "type": [ "integer", "null" ] },
    "total":     { "type": [ "integer", "null" ] } } }
```

| Member | Meaning |
|---|---|
| `pass` | whether the check passed; what a body `if` and a gate test |
| `message` | the operation's `failWith` sentence when `pass` is `false`; `null` when it passed |
| `uncovered`, `untested` | `terms_subset`'s lists, as version 30 computes them; `null` from the aggregates |
| `passed`, `total` | the aggregates' counts; `null` from `terms_subset` |

**Retention goes by where text came from, not what it says**:
- **`uncovered` and `untested`** come from inputs, so they follow the text retention rule: kept
  7 days, then deleted, with their hash kept for good. This holds for every package,
  medical or not.
- **`message`** is package text (the author's `failWith`), so it's kept, as are `pass` and the
  counts.

#### 6.2.2 Signatures

Fixed arity, versioned like the other built-in operations (in `requires` and `lock.json`):

| Operation | Arguments | Returns | Passes when |
|---|---|---|---|
| `terms_subset` | `of` (concept_list), `in` (concept_list), `failWith` (string literal) | `check_result` | every concept of `of` appears in `in`, as at version 30 |
| `all_pass` | `list` (of `check_result`), `failWith` (string literal) | `check_result` | every judged element passed; a `null` or empty list fails (below) |
| `count_pass` | `list` (of `check_result`), `min` (non-negative integer literal), `failWith` (string literal) | `check_result` | at least `min` judged elements passed |

- **`failWith` must be a literal string,** checked at publish: a failed check speaks the
  package's own sentence, never a computed one.
- **`list` may be a check loop's `.items`,** as in
  `{ "var": "check.part_coverage.items" }`.
  **Check operations judge only `completed` items**: an element is *judged*
  when its `state` is `completed`, and its `value` is the `check_result`; `skipped` and
  `not_run` elements are left out of `passed` and `total`. A plain `list<check_result>` (a
  loop's `.value`) judges every element.
- **`min` is a non-negative integer literal**, since it's the package's own
  rule, like `failWith`. With a literal, `min` is never null.
- **Null and empty lists** are [chapter 3](#3-expressions)'s (the operations' null behaviour).
  **A null or empty list fails `all_pass`**: a gate that judged nothing hasn't
  passed (JSON Logic's `all` is false on an empty array); a package that accepts nothing judged
  writes `count_pass(list, 0, …)`. The cases are revisited in [#1461](https://github.com/Consultologist/Consultologist-Blazor/issues/1461) (Milestone 40). `terms_subset` reads a null list as empty.
- **Whatever the arguments, an operation returns a `check_result`, never `null`,** so a gate
  always has a result to read.

### 6.3 Check loops

A check that runs per item of a production loop is **a loop inside `checks/`**, never a check
inside a production loop folder.

#### 6.3.1 Alignment through `.items`

A check loop **iterates the production loop's `.items`** ([chapter 4](#4-loops-and-functions)):
each element pairs a production item with its outputs **by identity**, so the check for
section 2 reads section 2's outputs. Positions are never matched up, and nothing reads into
another loop's body.

- In the check loop, `item` is the `.items` element: `item.value` (the production item's
  returned value), `item.nodes.<id>.value` (its body nodes' outputs), `item.state` and
  `item.reason`. **Check items share the production items' ids**:
  `check.part_coverage.coverage:2` lines up with `node.sections:2`.
- **Unrun items** keep their `state` (`skipped`, `not_run`). The check's header `if` skips them:
  `{ "===": [ { "var": "item.state" }, "completed" ] }`.
- The loop's `index.json` has every member of a `for` ([chapter 4](#4-loops-and-functions)):
  `parallel`, `maxParallel`, `until` and `max` apply, within `FormatBounds`. **Check items are
  named with `"itemLabel": "label"`**: the `.items` element's own `label`,
  which carries the production item's name ([chapter 4](#4-loops-and-functions)).
- **A check loop returns `list<check_result>`;** its `ret` names the check in its body.
- A check loop's body holds checks only (`kind: computed`, `format: check_result`).
  **Branches and nested loops in `checks/` follow `nodes/`'s rules**, and hold
  checks only, like a check loop's body. A `case` there is exhaustive, as everywhere
  ([chapter 4](#4-loops-and-functions)).

#### 6.3.2 Scheduling

Each item's check runs **as soon as that item's outputs are ready,** so checking overlaps
production. Checks are `computed` and make no model calls, so they take **no slot** under the
per-job ceiling ([chapter 8 § 8.5](#85-the-per-job-ceiling)), which counts agent calls only
([chapter 4 § 8](#48-concurrency-what-counts-toward-the-per-job-ceiling)).
An agent node inside a check loop's body counts like any other.

#### 6.3.3 No checks inside functions

Checks gate releases, and functions release nothing. A function may return a `check_result` as
data, and checking each call is a check loop over the calls' `.items`.

#### 6.3.4 Example (a made-up package)

`example-checked-sections`, with fictional inputs only. The production loop drafts each planned
section and extracts its terms:

```
nodes/plan.md                    kind agent, format section_plan
nodes/sections/index.json           for over node.plan.value.sections, itemLabel "title"
nodes/sections/planned_terms.md     kind agent, format concept_list   (the terms the plan names)
nodes/sections/draft.md             kind agent, format plaintext
nodes/sections/section_terms.md     kind agent, format concept_list   (the terms the draft covers)
nodes/sections/section.md           kind computed, format titled_section (the loop's ret, § 6.6.5)
checks/part_coverage/index.json
checks/part_coverage/coverage.md
checks/all_sections_covered.md
deliverables/index.json
deliverables/note.md
```

```jsonc
// checks/part_coverage/index.json
{ "kind": "for", "producer": "computed", "label": "Section coverage", "description": null,
  "format": { "type": "array", "items": { "$ref": "check_result" } }, "reproducible": true,
  "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "in": "node.sections.items", "itemLabel": "label",
  "parallel": true, "maxParallel": null, "until": null, "max": null,
  "nodes": [ "coverage" ], "ret": "check.part_coverage.coverage" }
```

```
checks/part_coverage/coverage.md
---
{ "kind": "computed", "producer": "computed", "label": "Section covers its planned terms", "description": null,
  "format": "check_result", "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false,
  "if": { "===": [ { "var": "item.state" }, "completed" ] },
  "expression": { "terms_subset": [ { "var": "item.nodes.planned_terms.value" },
                                    { "var": "item.nodes.section_terms.value" },
                                    "The section does not cover every term its plan names." ] } }
---
```

### 6.4 Aggregates and the gate

**The whole document is gated by an explicit aggregate check:** a `computed` check returning one
`check_result`, which the deliverable's `check` names. The rule is written and typed, never
implied. There's **no "partly released" state**.

```
checks/all_sections_covered.md
---
{ "kind": "computed", "producer": "computed", "label": "Every section covers its planned terms", "description": null,
  "format": "check_result", "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null,
  "expression": { "all_pass": [ { "var": "check.part_coverage.items" },
                                "Not every section covers its planned terms." ] } }
---
```

"At least 8 of 9" is `{ "count_pass": [ { "var": "check.part_coverage.items" }, 8, "Fewer than 8 sections cover their planned terms." ] }`.

**Single sections are handled in the template.** A deliverable may read checks other than its
own (§ 6.6.3), so its template chooses how a failing section appears, by a body `if` on
`check.x.value.pass` or on an item's state ([chapter 5 § 2.5](#525-a-body-if-tests-recorded-facts-only)).

### 6.5 Checks in the record and History

**The record** has a checks section apart from nodes. A top-level check's key is `check.<id>`;
a check loop's items are `check.part_coverage.coverage:2`, with the production item's id and
named by the loop's `itemLabel`, each linking to its production item (`node.sections:2`). The
row holds the check's reads and their hashes, its result (the `check_result`, with `uncovered`
and `untested` retained 7 days, then their hashes and sizes, § 6.2.1), and its effect. The
shape is [chapter 9](#9-the-record)'s.

**History** has four sections in the order the job runs:
Inputs, Nodes, Checks, Deliverables. Each check row says:

| Line | Shows |
|---|---|
| checks | what it ran on (a deliverable or a node), with that output's hash |
| reads | its other inputs, each linking to its node's row |
| result | pass or fail with its detail (*"12 of 12 terms present"*, *"7 of 9 sections passed"*) |
| effect | released, held, blocked, or read by something else |

```
 ┌ Checks ─────────────────────────────────────────────────────────────────────┐
 │ ▾ part_coverage     7 of 9 passed   for over node.sections.items            │
 │     ▸ Oncologic History           passed                                    │
 │     ▸ Surgery and Pathology       failed   2 planned terms missing          │
 │ ▾ all_sections_covered   failed   all_pass → check_result     b19e…         │
 │     reads           check.part_coverage (9 items, 7 passed)                 │
 │     result          Not every section covers its planned terms.             │
 │     effect          note blocked                                            │
 └─────────────────────────────────────────────────────────────────────────────┘
```

- **No duplication:** a deliverable row shows a one-line `Check: <id>  <passed|failed> →`
  linking to the check's row. A node a check reads gets no extra row.
- **A failed check that stops a deliverable is a banner at the top of the job:** *"Consultation
  note was blocked: check 'coverage' failed (10 of 12 terms present)."* A gate check that
  errored gives *"Consultation note was blocked: check 'coverage' could not run (\<error\>)."* A destination the account hasn't set up has its own banner line (§ 6.8).
- **The diagram** draws a Checks frame, a thick `gates` edge into the deliverable, and a check
  loop as a frame inside it with a dotted `aligned` edge to its production loop
  ([chapter 8 § 8.14](#814-what-belongs-to-the-app)).

### 6.6 Deliverables as files

#### 6.6.1 The file

**Each deliverable is `deliverables/<id>.md`**, its header judged by the schema [`deliverable`](v31/schemas/deliverable.schema.json) (or in a sub-folder, § 6.8): a JSON header, then a
non-empty body that is its **composition template**. A deliverable is a `kind: rendered` leaf;
the folder gives its role. There's no implicit template: the Editor and the command-line tool
generate the file, and the migration writes one per deliverable.

**A deliverable's id is its path, like a node's**: `deliverables/consult.md`
is `deliverable.consult`, and `deliverables/emr/note.md` is `deliverable.emr.note`. The
destination folder is part of the id, so the same file name may repeat in different folders
(`emr/note.md`, `email/note.md`), and moving a deliverable changes its key. The key, with its
root, is what the record, History and `WorkflowPackages/Current`'s `Results` use
([chapter 8 § 8.14](#814-what-belongs-to-the-app)).

| Member | Type | Null | Meaning |
|---|---|---|---|
| `label` | string | no | the display name |
| `kind` | `"rendered"` | no | the mechanism |
| `description` | array of strings | yes: none | for people only |
| `format` | `"markdown_block"`, `"plaintext"`, or an object format | no | the composed output's format (§ 6.6.4) |
| `if` | JSON Logic | yes: always | whether the deliverable exists (§ 6.6.3) |
| `check` | string, `check.<id>` | yes: ungated | the check that gates release (§ 6.7) |
| `whenEmpty` | `"release"`, `"hold"` or `"fail"` | no | what happens when the composed text is empty (§ 6.6.6) |

- **`sources` is removed.** The template's reads are the deliverable's sources: the resolver
  derives them, records them in `resolve.json` and draws them in the diagram
  (chapter 7).
- **`macros` and `signature` are removed:** deliverables don't call macros, and the
  signature is a profile field (§ 6.10).
- **`markdown_inline` is refused as a deliverable format**: a document stands
  on its own lines.

#### 6.6.2 Item states

A template reads each loop item's `state` and `reason` through `.items`:

| `state` | Meaning | `reason` |
|---|---|---|
| `completed` | the item ran | `null` |
| `skipped` | its `if` didn't hold | the condition's printed text |
| `not_run` | stopped early by `until` | *"stopped early at \<position name>"*, for example *"stopped early at Sections 3"*: reasons name items by position, never by a drawn name |

- The set is closed and checked at publish. A failed item fails the job (`onInvalid` is `fail`
  or `retry`), so it never reaches a template.
- **`reason` is never patient text:** it's built only from package text and fixed engine
  sentences, because it can land in the deliverable.
- A branch on `state` handles every state or ends with an `else`; an unknown state is refused
  ([chapter 5 § 2.5](#525-a-body-if-tests-recorded-facts-only)).

#### 6.6.3 What a deliverable reads

**The template** reads `node.*`, `input.*`, `snippet.*`, `check.*` (not its own check),
`profile.*`, the `run.*` set and the `renderer.` pipe
([chapter 5 § 3.1](#531-the-table)). Each read of `run.*` or of a
run-dependent value is a run spot ([chapter 5 § 4](#54-run-spots-and-the-two-hashes)).

**Refused:**
- other deliverables (deliverables are terminal, § 6.6.7);
- `macro.*` and `part.*`;
- **its own check:** the check runs on the deliverable, so reading it is a cycle (R-D2).

**The header `if`** decides, before composition, whether the deliverable exists. It may read
`input.*`, a node's `.value` (data) and `run.*`. It may not read `.content` (text), `check.*`
(a possible cycle), `profile.*` or deliverables.
When it doesn't hold, the deliverable is **skipped by condition**, recorded with the
condition's printed text, never the value it read.

#### 6.6.4 Strict formats

**A deliverable's reads must match its format.** Conversions happen in nodes (a `computed`
node with `plain`, or a renderer); the only automatic step is escaping.

| Deliverable `format` | May read | Refused |
|---|---|---|
| `markdown_block` | `markdown_block`; `markdown_inline` inside a line; plain-text formats (escaped); `string` and `number` data (escaped) | objects (use a renderer or a node) |
| `plaintext` | plain-text formats; `string` and `number` data | any Markdown (convert in a node) |
| an object format | exactly that format, as `{{ node.x.value }}` and nothing else | everything else |

- **Escaping:** plain text and data read into Markdown are escaped, protecting only the
  characters Markdown would misread (`*`, `#`, `_`, `[`, …), so the displayed text is exactly
  the plain text. The substitution's hash is taken **after** escaping. **The escape set is
  CommonMark's backslash escapes for ASCII punctuation,** published with test vectors in the
  conformance suite.
- **The template's own literal text is typed too:** a `plaintext` deliverable may not write
  Markdown syntax (a line starting `#`, `-`, `*` or `>`, or a `**` pair). A Markdown
  deliverable's literal text is the author's Markdown. An object deliverable allows nothing
  but its single expression.
- **An object deliverable's output** is canonical JSON (RFC 8785).
- **`profile.signature` and `profile.closing` are `plaintext`,** so a Markdown deliverable reads
  them escaped.

#### 6.6.5 Headings are the author's

**The template writes the headings,** so there are no invented
`## Paragraphs 1` headings. [#1382](https://github.com/Consultologist/Consultologist-Blazor/issues/1382) closes once this is running and verified.

**The pattern for a loop's sections: a closing `computed` node builds the pair** and is the
loop's `ret`. With the format `titled_section`:

```jsonc
// formats/titled_section.json (declared by the package; not a built-in at 31)
{ "$schema": "urn:consultologist:spec:31:dialect",
  "type": "object", "required": [ "title", "content" ], "additionalProperties": false,
  "properties": { "title": { "type": "string" }, "content": { "$ref": "plaintext" } } }
```

```
nodes/standards/section.md
---
{ "kind": "computed", "producer": "computed", "label": "Section", "description": null, "format": "titled_section",
  "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null,
  "expression": { "object": { "title":   { "var": "item.value.title" },
                              "content": { "var": "node.section_instructions.content" } } } }
---
```

- `titled_section` is **declared by the package, not a built-in at 31**.
- The loop returns `list<titled_section>`. **Formats are shape only:** `content` is `plaintext`,
  the same format the agent's text has; the node's producer is `computed`, and `reproducible`
  stays `true`. Where the text came from is the **model-derived** flag instead:
  the row is marked model-derived, and History, the diagram and the Editor say *"computed from
  model text: node.standards.section_instructions"* ([chapter 3](#3-expressions)).
- The node's row hashes prove which title went with which text.
- **`.items` is always available too,** for reaching a skipped item's `state` and `reason`.
  Zipping two lists by position is not offered.
- **A loop's `.content`** keeps version 30's bytes as a standard rendering
  ([chapter 5 § 5.3](#553-built-in-renderers)), so a migrated template can
  reproduce today's note exactly.

**`test/general`'s deliverable, after the author's edit** (the migration first writes a template
reproducing version 30's bytes, [chapter 10 § 10.1](#101-what-the-rewrite-does-mechanically)):

```
deliverables/consult.md
---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "markdown_block",
  "if": null, "check": null, "whenEmpty": "hold" }
---
{{~ for s in node.standards.value ~}}
## {{ s.title }}

{{ s.content }}

{{~ end ~}}
{{~ snippet.test.content }}
```

The last line reads the snippet `snippets/test.md` verbatim at the end of the note; how the
migration turns version 30's `test` macro into it is [chapter 10 § 10.2](#102-pipes-body-tests-and-the-test-macro)'s.

**`example-nested-note`, with headings the author chose.** The inner paragraphs get no heading.
Its loop `parts` is renamed `sections`, since `parts` is a reserved id
([chapter 1](#1-files-and-scopes)). A closing node in `sections/` builds
`{ title, paragraphs }` (a package format `titled_paragraphs`, `paragraphs` a list of
`plaintext`, model-derived), and the template reads:

```
deliverables/note.md
---
{ "label": "Nested consultation note", "kind": "rendered", "description": null,
  "format": "markdown_block", "if": null, "check": null, "whenEmpty": "fail" }
---
## Summary

{{ node.refine.content }}
{{~ for s in node.sections.value ~}}

## {{ s.title }}
{{~ for p in s.paragraphs ~}}

{{ p }}
{{~ end ~}}
{{~ end ~}}
```

Each paragraph is `plaintext`, so it's escaped into the Markdown note.

**The `whenEmpty` values above are the ones the migration writes** ([chapter 10 § 10.7](#107-whenempty-for-migrated-deliverables)).

#### 6.6.6 When a deliverable comes out empty

**Empty means** the composed text, after trimming whitespace, is empty. The template's own
fixed text (a heading) counts as content, so an author who wants nothing when there are no
sections puts the heading inside a loop or a recorded-fact `if`.

| `whenEmpty` | Effect |
|---|---|
| `release` | an empty document is released and recorded |
| `hold` | not released, recorded as *held: empty*; the other deliverables go on |
| `fail` | the job fails, naming the deliverable |

**An object-format deliverable is never empty**: its canonical JSON is never
blank, so `whenEmpty` has no effect there, but is still written.

#### 6.6.7 Deliverables are terminal

- **Nodes may not read deliverables,** and other deliverables may not either.
- **Checks may** read a deliverable's `.content`.
- Text a later node wants to reuse is made by a `rendered` node, which both read.
- **The graph:** nodes, then deliverables, then their checks, then release.

### 6.7 Gating and outcomes

**A deliverable's check is its final proofread before sending.** The check named in `check` may
read the composed deliverable (`deliverable.<id>.content`, for example
`deliverable.emr.note.content`) or only nodes. It runs after
everything it reads, and release waits for it.

**The outcomes, in order of evaluation:**

| Outcome | When | Recorded as | The job |
|---|---|---|---|
| skipped | the header `if` didn't hold | skipped by condition, with the printed condition | goes on |
| failed | composed empty with `whenEmpty: fail`, or the render failed | the deliverable's failure | fails, naming the deliverable |
| held | composed empty with `whenEmpty: hold` | *held: empty* | goes on |
| blocked | its gate check returned `pass: false`, or **errored** (failed to run) | composed, blocked: fails closed, with the check's result or error recorded, never delivered | goes on |
| released | composed, and its check passed, its check was skipped by its own `if`, or it has none | composed, released, then a delivery result per destination (§ 6.8) | goes on |

- **`blocked` is an outcome; `not sent` is a delivery result**. A deliverable is
  released, held, failed, skipped or blocked; each destination of a released deliverable is then
  sent, not sent or failed (§ 6.8).
- A deliverable that's blocked or held is **never something to dig for:** History shows the
  banner (§ 6.5).
- **A deliverable whose gating check was skipped by its own `if` is released**, recorded and shown in History as *"released: check '\<id>' didn't apply (its
  if was false)"* (H-4). A skipped gate gives no `check_result` to fail on. **An empty
  `all_pass`, by contrast, fails** (§ 6.2.2): that check ran and judged nothing.
- The record holds the outcome as the deliverable row's `state` (`released`, `held`, `failed`,
  `skipped` or `blocked`) with its reason sentence, and each destination's result in
  `delivery` ([chapter 9](#9-the-record)).

### 6.8 Delivery

**Delivery is declared on folders only**, in each folder's `index.json`, judged by the schema [`deliverables-index`](v31/schemas/deliverables-index.schema.json). The root `deliverables/index.json` is required;
routing a deliverable differently means putting it in a sub-folder.
**Delivery folders are one level deep**, and the folder is part of each
deliverable's id (§ 6.6.1): `deliverables/patient/patient_letter.md` is
`deliverable.patient.patient_letter`.

```
deliverables/
  index.json          { …, "delivery": ["emr"], "bundle": null }
  consult.md
  patient/
    index.json        { …, "delivery": ["email"], "bundle": null }
    patient_letter.md
  referral_pack/
    index.json        { …, "delivery": ["email"], "bundle": "zip" }
    gp_letter.md
    summary.md
```

| Member | Type | Null | Meaning |
|---|---|---|---|
| `description` | array of strings | yes: none | for people only |
| `items` | array of ids | no | the deliverables and sub-folders, in order ([chapter 1](#1-files-and-scopes)) |
| `delivery` | array of `"email"`, `"pdf"`, `"emr"`, `"zip"` | no | the kinds of destination; `[]` means deliberately not delivered (kept in History only) |
| `bundle` | `"zip"` | yes: none | send the folder's deliverables together, as one archive |

- **No inheritance between folders:** every `index.json` states its own delivery in full.
- **The package declares kinds, never addresses** (packages are public). **The account maps
  kinds to endpoints** in a separate account section, beside today's delivery address; templates
  never read it.
- **Delivery happens at the end, and only then**: nothing is delivered until every
  deliverable's outcome is final and the job has succeeded. A job that fails delivers nothing,
  and its released deliverables stay in History, recorded as *"not sent: the job failed"*.
- **A job that has succeeded in production enters `delivering`**, shown as
  *"Delivering…"*, with the document viewable throughout. Each attempt is a row in the one record
  ([chapter 9 § 9.2](#92-keys-with-their-roots)), and the record is sealed when delivery ends ([chapter 8 § 8.11](#811-delivery-at-the-end)).
- **A result per destination**: each kind a released deliverable goes to gets its own
  result, `sent`, `not sent` with a reason, or `failed`, so an email that went out beside an EMR that
  isn't set up reads as one of each.
- **A failed delivery is retried**: 3 times with back-off over about 15 minutes (engine
  settings, [chapter 8 § 8.11](#811-delivery-at-the-end)), each attempt recorded on the destination's result. If the last also
  fails, the result is `failed`, the operator is alerted, and History shows *"Couldn't send to
  \<destination>. Copy the note instead."* The job stays completed.
- **A kind the account hasn't configured:** the job still runs, and the deliverable is produced;
  that destination is recorded as **not sent**: *"not sent: EMR isn't set up for this account"*.
  The job doesn't fail, and the document stays in History.
- **A bundle holds released deliverables only**: a held, skipped, failed or
  blocked one is left out, and History lists what was left out and why.
- `description` and `items` follow every folder's `index.json` ([chapter 1](#1-files-and-scopes)).

### 6.9 Deliverables in the record and History

**The row's key** is the deliverable's id with its root (`deliverable.emr.note`), and a renderer
use under it is `deliverable.emr.note/render:1` ([chapter 9](#9-the-record)).

**Hashes:** the template's hash before substitution, one hash per substitution, and the hash of
the final text (`composedHash`).

- **Sites:** each expression in the template, numbered in source order, with its text and
  position (package text, safe to keep).
- **Substitutions:** each evaluation (once, or once per loop pass), naming its site, its `pass`
  (a list, one number per enclosing `for`), what it read, and its hash and size. Renderer uses
  add `renders` ([chapter 5 § 5.5](#555-in-the-record-and-history)). Profile
  reads are substitutions like any other.
- **Replay:** substituting the recorded values into the template, in site and pass order,
  reproduces `composedHash`. Escaped reads are recorded after escaping, so replay holds.
- **The template is kept by reference:** the record stores `templateHash`, and History shows the
  text from `resolve.json` of the pinned version. It's never deleted, since it holds nothing
  personal.
- **Run spots** add the run-neutral hash beside `composedHash`
  ([chapter 5 § 4](#54-run-spots-and-the-two-hashes)).
- **The outcome** (§ 6.7, the row's `state`) and each destination's delivery result (§ 6.8).

The record's shape and field names are [chapter 9](#9-the-record)'s. **History** shows the
template with its reads grouped by site, looped sites collapsed to "× N passes" and expandable
per pass named by `itemLabel`, values while retained (7 days), then hashes and sizes, and the
one-line check status.

### 6.10 The profile

`profile.*` is personal data about the clinician: not patient data, but it ends up in
deliverable text and hashes. The format says exactly what may be read, how it's typed, and how
it's recorded.

#### 6.10.1 The closed list

The list and the preview values are published as [`v31/profile.json`](v31/profile.json).

| Field | Format | Null | Preview value (fictional) |
|---|---|---|---|
| `profile.name` | `string` | never: a missing value refuses the job (§ 6.10.4) | `Dr A. Sample` |
| `profile.credentials` | `string` | never | `MD, FRCPC` |
| `profile.organisation` | `string` | never | `Sample Oncology Clinic` |
| `profile.signature` | `plaintext` | never | the chosen signature block |
| `profile.closing` | `plaintext` | never | a closing line or contact block |

- **Adding a field later is compatible;** removing or retyping one is a format change.
- `profile.closing` is the home of a clinician's fixed boilerplate. Personal macros are
  [#1417](https://github.com/Consultologist/Consultologist-Blazor/issues/1417) (Milestone 40).
- **Personal snippets are unchanged:** they're inserted into inputs on the Create page and
  recorded with the input. There are no `profile.snippets` reads.
- **Delivery endpoints aren't profile fields** (§ 6.8).

#### 6.10.2 Where reads are allowed

| Place | `profile.*` |
|---|---|
| deliverable templates | yes |
| macro bodies (rendered into the reply, never sent to a model) | yes |
| snippet bodies placed in either of those | yes |
| prompts, `rendered` nodes, parts, macro instructions, snippets placed in prompts | **no:** the clinician's details aren't sent to a model |
| conditions and `computed` expressions, the deliverable header `if` included | **no** |
| a **profile-carrying** value (text a profile-reading macro body was substituted into, and anything made from it; [chapter 3 § 4.6](#346-profile-carrying-is-contagious)) | deliverables only: a prompt, a part or a condition that reads one is refused (R-F5) |
| inside a function | only as a parameter passed in through the call's `with`, and then only to macro bodies |

**A parameter bound to a `profile.*` value carries the same restriction through the function**: reading it in a prompt, a part or a condition is refused (R-F3), just as reading
`profile.*` there would be.

#### 6.10.3 The signature

- `profile.signature` is the account's **chosen block** (`ChosenId`; an account holds up to 5
  named blocks, each up to 4,000 characters).
- **The Create page shows a signature choice only when the account has more than one block and
  the package reads `profile.signature`,** defaulting to the chosen block.
- **The record names the block's id,** never its text: `signatureBlockId`, beside
  `signatureChosen`, which is `"default"` (the account's chosen block) or `"job"` (picked on the
  Create page). Packages never name blocks. There's no signature snapshot at
  31: the signature is a profile read, recorded by hash, and its text lives in the deliverable,
  under text retention.

#### 6.10.4 A missing field refuses the job

**When the package reads a field the account hasn't set, the job is refused before it starts,**
on the Create page. There's no empty substitute. The package's needs are known in advance from
`resolve.json`'s derived `needs.profile` (for example `["name", "signature"]`,
chapter 7).

**This refusal applies to 31 jobs only**: a job on a package still at 30 keeps 30's
behaviour until its package moves. The owners' notice before the cutover says so ([chapter 10 § 10.8](#108-a-package-that-stays-at-30-and-what-its-owner-is-told)). When
the email intake refuses a job for this reason, its reply carries the same sentence (J-1, J-2).

**An empty or whitespace-only value counts as not set**, so a job that reads
it is refused at the start.

#### 6.10.5 Recording and retention

- Each `profile.*` read is a substitution recorded by hash (§ 6.9).
- The record names the signature block's id.
- The text follows produced text's retention: deleted after 7 days. A value that is
  profile-carrying (§ 6.10.2) follows the same retention.
- **A short value's hash is kept,** as every substitution's is, and the record's documentation
  says it can be reversed by guessing: a name or credentials line is short enough to test
  candidates against its hash (option c). Long texts keep their hash for verification as
  before.

#### 6.10.6 Previews

The Editor, the debugger and preview panes use **fictional sample values from the
registry** (the table in § 6.10.1), never the author's own profile.

#### 6.10.7 The Profile page and the time zone

- **Profile gains a "Letter details" card** for `credentials`, `organisation` and `closing`,
  with limits of 120, 200 and 4,000 characters (the last the same as a signature block).
- **The account time zone** (an IANA name, for `run.date`) is an **account setting, not a profile
  field:** it's never read as `profile.*`. It's a select list that starts empty, with a "Use this
  browser's zone" button that fills it only when clicked. The zone is recorded beside
  `run.date`. **Every job is refused until it's set**, whether or not the package reads
  `run.date`: *"Set your time zone in your account settings before running a workflow."* Like § 6.10.4's
refusal, it applies to 31 jobs only, is announced in the owners' notice, and is the email
intake's reply when it refuses. The pages themselves are [chapter 8 § 8.14](#814-what-belongs-to-the-app)'s.

### 6.11 What changes from version 30

| At 30 | At 31 |
|---|---|
| a check is a node in `nodes`, `op: terms_subset` with `with: { of, in, failWith }`, read as `node.coverage` | `checks/<id>.md`, `kind: computed`, `expression` with `terms_subset`, read as `check.coverage` |
| checks are top-level only | check loops over a production loop's `.items`, gated by `all_pass` or `count_pass` |
| a deliverable is a manifest entry with `sources`, `macros` and a `check` naming a node | `deliverables/<id>.md` with a composition template, its id its path (`deliverable.emr.note`); sources derived; `check` names a `check.*`; `whenEmpty` |
| the composer writes `## {item name}` over every loop item, at every depth | the template writes the headings; `.content` keeps the old bytes as a standard rendering |
| deliverable macros at `before`, `after`, `append` | snippets read in the template |
| one delivery address per account | delivery kinds per folder, mapped to endpoints by the account |
| `profile.name`, `profile.signature`; an unset value renders as empty text | five typed fields; an unset field the package reads refuses the job |
| `profile.*` readable in prompts | deliverables, macro bodies and snippets placed in them only |

### 6.12 Refusals

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format. `<…>`
marks a placeholder.

**Checks**
- R-C1: *"Deliverable '\<id\>' is checked by \<reference\>; a deliverable's check names a check.\*."*
- R-C2: *"Check '\<id\>' has format \<format\>; a check returns check_result."*
- R-C3: *"Check '\<id\>' has kind \<kind\>; a check is computed."*
- R-C4: *"\<Path\> in checks/ is \<kind\>; checks/ holds checks and the loops over them."*
- R-C5: *"Check '\<id\>' passes \<expr\> as failWith; failWith is a literal sentence."*
- R-C6: *"Check '\<id\>' passes \<expr\> as min; min is a whole number of at least 0."*
- R-C7: *"Check loop '\<id\>' runs over \<source\>; a check loop runs over a production loop's .items."*
- R-C8: *"Function '\<id\>' holds check '\<check\>'; functions hold no checks. Return a check_result as data and check the calls' .items."*
- R-C9: *"Node '\<id\>' reads deliverable.\<deliverable\>; only checks read deliverables."*
- R-C10: *"Check '\<id\>' gates deliverable '\<deliverable\>', and its if reads \<path\>, which can be null; a gate check's if reads values that are always set."*

**Deliverables**
- R-D1: *"Node '\<id\>' reads deliverable.\<deliverable\>; deliverables are the job's outputs: read the nodes it is composed from."*
- R-D2: *"Deliverable '\<id\>' reads check.\<check\>, which checks \<id\>: a deliverable can't read its own check."*
- R-D3: *"Deliverable '\<id\>' reads deliverable.\<other\>; a deliverable reads nodes, inputs, snippets, checks, the profile and run facts."*
- R-D4: *"Deliverable '\<id\>' has format \<format\>; a deliverable is markdown_block, plaintext or an object format."*
- R-D5: *"Deliverable '\<id\>' is \<format\>, and reads \<path\> (\<read format\>) at line \<n\>. \<Convert it in a node | Use a renderer or a node\>."*
- R-D6: *"Deliverable 'letter' is plaintext, and line 4 writes Markdown ('## Plan')."*, generalised as *"Deliverable '\<id\>' is plaintext, and line \<n\> writes Markdown ('\<text\>')."*
- R-D7: *"Deliverable '\<id\>' is \<object format\>; its template is {{ node.\<x\>.value }} and nothing else."*
- R-D8: *"Deliverable '\<id\>' reads \<path\> in its if; a deliverable's if reads inputs, node values and run facts."*
- R-D9: *"Deliverable '\<id\>' places \<macro.\* or part.\*\>; deliverables place snippets, and macros belong to agent nodes."*
- R-D10: *"Deliverable '\<id\>' has whenEmpty \<value\>; write release, hold or fail."*
- R-D11: *"Deliverables folder '\<path\>' has delivery kind \<kind\>; the kinds are email, pdf, emr and zip."*
- R-D12: *"deliverables/index.json is missing; the deliverables folder states its delivery."*
- R-D13 (the same sentence as [chapter 5's R-D8](#511-refusals)): *"Deliverable 'consult' branches on part.state and handles completed and skipped, but not not_run: add it or an else."*

**Profile**
- R-F1: *"\<Subject\> reads profile.\<field\>, which isn't a profile field; the fields are name, credentials, organisation, signature and closing."*
- R-F2: *"\<Condition owner\> reads profile.\<field\> in a condition; the profile is read only in deliverables and macro bodies."*
- R-F3: *"Function '\<id\>' reads param.\<name\>, which carries profile.\<field\>, in \<a prompt | a part | a condition\>; the profile is read only in deliverables and macro bodies."*
- R-F5: *"\<Subject\> reads \<path\>, which carries profile text; prompts, parts and conditions don't read profile text. Read it in a deliverable."*
- R-F4 ([chapter 5 § 11](#511-refusals), R-R2, for prompts): *"Node '\<id\>' reads profile.\<field\>; the clinician's profile is never sent to a model. Read it in a deliverable or a macro body."*

**Refused at job start** (Create page)
- J-1: *"This workflow needs your signature. Choose one in Profile."*
- J-2 (the other fields): *"This workflow needs your \<field label\>. Set it in Profile, under Letter details."*
- J-3: *"Set your time zone in your account settings before running a workflow."*

**Shown in History** (not refusals)
- H-1: *"\<Deliverable label\> was blocked: check '\<id\>' failed (\<detail\>)."*
- H-2: *"not sent: \<Kind\> isn't set up for this account"*
- H-5: *"\<Deliverable label\> was blocked: check '\<id\>' could not run (\<error\>)."*
- H-7: *"Couldn't send to \<destination\>. Copy the note instead."* (a destination whose retries ran out)
- H-6: *"not sent: the job failed"* (each destination of a released deliverable in a job that failed)
- H-3: *"stopped early at \<position name\>"* (an item's `reason` for `not_run`)
- H-4: *"released: check '\<id\>' didn't apply (its if was false)"*

## 7. The compiled documents

This chapter defines what publish produces from a version 31 package: **`resolve.json`**, the
package as checked, which is the only thing the engine loads; **`lock.json`**, the exact toolchain
that checked it; `requires` and `needs`; where each file lives, and the line between evidence and
views; **in-package tests** in `tests/` and the **publish report** that records them. Whether
`resolve.json` ever needs a `semantics` block is reviewed in Milestone 40
([#1455](https://github.com/Consultologist/Consultologist-Blazor/issues/1455)). The record that pins both documents is [chapter 9](#9-the-record).

### 7.1 Two documents, written once

| | `resolve.json` | `lock.json` |
|---|---|---|
| **Says** | what the package is, once read, resolved, typed and checked | exactly which implementations read, resolved, typed and checked it |
| **Read by** | the engine (the only file it loads for a 31 package), History, the Editor, outside tools | the engine's start check, History, the registry's upgrade checks, reviewers |
| **Media type** | `application/vnd.consultologist.resolve+json` | `application/vnd.consultologist.lock+json` |
| **Its schema** | [`resolve`](v31/schemas/resolve.schema.json), published in the format-spec release | [`lock`](v31/schemas/lock.schema.json), published in the format-spec release |

The rules common to both:

- **Data, never code.** Both are JSON; the engine reads them and never executes them.
- **Canonical by RFC 8785** (the JSON Canonicalization Scheme). The bytes stored are the canonical
  bytes, so re-deriving either document from the same source with the same toolchain gives the
  same bytes and the same hash.
- **Hashes are SHA-256 over the canonical, uncompressed bytes,** written `sha256:<64 lowercase hex>`.
  Compression (for example gzip) is only for storage and transport.
- **No timestamps in either document.** Compiling the same source with the same toolchain gives the
  same bytes. The time of publishing is in the registry and the publish report.
- **Written only by publish,** with the registry's toolchain. Never authored, never accepted from
  an upload, never in any source (§ 7.7).
- **Immutable with the version.** A published version is **never re-resolved** and **never
  re-locked**. A change of toolchain that matters is a new version of the package.
- **No backfill.** Versions below 31 never get either document; they keep today's loading path
  until they're retired ([#1450](https://github.com/Consultologist/Consultologist-Blazor/issues/1450)). Packages that must keep running are migrated to 31 ([chapter 10](#10-migration-30--31)).
- **Every member is present:** `null` means "deliberately none" and a missing key is an
  error. Embedded JSON Schema keeps JSON Schema's own rules (annotations present where they apply).
- **Every key is written with its root** (`node.sections.paragraphs.draft_paragraph`,
  `check.part_coverage.coverage`, `deliverable.emr.note`, `input.consult_draft`), as in the record,
  test files and History links.

**How they point at each other.** `lock.json` names the hash of the `resolve.json` it belongs to
(`resolve.hash`). `resolve.json` names its lock **by file name** (`lock: "lock.json"`), not by hash,
because each hash would otherwise have to contain the other. Every job's record pins both hashes
([chapter 9](#9-the-record)), which ties the pair for every job.

### 7.2 `resolve.json`

#### 7.2.1 What's in it, and what isn't

**Embedded:** every piece of package content and every catalogue format used: prompt and template
bodies inline as JSON strings, formats as one `$defs` bundle, conditions and `computed` expressions
as canonical JSON Logic, the flattened node tree, the derived graph, `requires`, `needs` and the
warnings. Packages are at most 2 MiB of source (`SourceBounds`, [chapter 1](#1-files-and-scopes)),
so one document and one hash cover everything.

**Declared, never embedded:** engine capabilities (the template engine, the evaluator, built-in
operations, built-in renderers, node kinds, features, attested agents), listed in `requires` with
ranges (§ 7.3) and locked exactly in `lock.json` (§ 7.4).

**Never in it:** a job's inputs; engine configuration (model deployments, endpoints, terminology
services, keys); records; test results (they go in the publish report, § 7.9).

**What each language holds**:
conditions and `computed` expressions are JSON Logic; templates (prompts, renderers, snippets,
parts, macro bodies and instructions, deliverables) are Scriban text in the dialect of
[chapter 5](#5-templates-and-macros); formats are JSON Schema in the dialect of
[chapter 2](#2-types-and-inputs). Everything the engine computes or decides is data.

#### 7.2.2 Top-level members

The members of `resolve.json`, as [`resolve.schema.json`](v31/schemas/resolve.schema.json) states them:

| Member | Type | Null | Meaning |
|---|---|---|---|
| `documentVersion` | integer | never | the shape of `resolve.json` itself; `1` at 31 |
| `specVersion` | integer | never | `31`. It alone identifies the rules (null handling, whitespace, escaping, culture); there is **no `semantics` block** ([#1455](https://github.com/Consultologist/Consultologist-Blazor/issues/1455)) and **no `resolvedBy`** (the toolchain is `lock.json`'s) |
| `package` | object `{ name: string, version: string }` | never | the package name and its version tag, for example `{ "name": "example-nested-note", "version": "v2026.12.1" }` |
| `title` | string | never | the manifest's title, at the top level |
| `description` | string | allowed | the manifest's description; `null` when it has none |
| `tags` | array of string | never | the manifest's tags; `[]` for none |
| `sourceHash` | string (`sha256:…`) | never | the hash of the source as published (§ 7.2.6) |
| `lock` | string | never | `"lock.json"`, the companion's file name in the same folder (§ 7.1) |
| `requires` | object | never | engine capabilities (§ 7.3.1) |
| `needs` | object | never | what the account must provide (§ 7.3.2) |
| `inputs` | object keyed by input id | never | the package's inputs (§ 7.2.3); `{}` for none |
| `inputOrder` | array of string | never | the input ids in written order, the Create page's order (§ 7.2.3); `[]` for none |
| `formats` | object (a JSON Schema with `$defs`) | never | the formats bundle (§ 7.2.4) |
| `formatHashes` | object, format id → `sha256:…` | never | each bundled format's **full** hash (§ 7.2.4) |
| `typeHashes` | object, format id → `sha256:…` | never | each bundled format's **type** hash (§ 7.2.4), beside `formatHashes` |
| `bindings` | object, format id → producer → binding | never | the attested agent serving each format and producer an agent node uses (§ 7.2.4); `{}` when the package has no agent node |
| `nodes` | object keyed by rooted key | never | every production node, flat (§ 7.2.5) |
| `checks` | object keyed by rooted key | never | every check and check loop, flat; `{}` for none |
| `functions` | object keyed by function id | never | each function, with its own flat `nodes` map (§ 7.2.5); `{}` for none |
| `renderers` | object keyed by rooted key | never | the package's renderers; `{}` for none |
| `snippets` | object keyed by rooted key | never | every snippet and snippet folder; `{}` for none |
| `macros` | object keyed by rooted key | never | every macro and macro folder; `{}` for none |
| `deliverables` | object keyed by rooted key | never | every deliverable, keyed by its path (`deliverable.emr.note`) |
| `graph` | object `{ edges, order }` | never | the derived dependency graph (§ 7.2.7) |
| `run` | array of string | never | the `run.*` facts read anywhere, sorted (`["run.date", "run.id"]`); `[]` for none |
| `warnings` | array of warning | never | every warning publish gave (§ 7.2.8); `[]` for none |

The manifest keeps identity and inputs; its old `nodes`, `macros` and `snippets` lists are the
folders' `index.json` files at 31 ([chapter 1](#1-files-and-scopes)).
Members of the manifest that only steer publish (for example a `derivedFrom` pointer) are carried
under the same names when they exist at 31.

#### 7.2.3 `inputs`

The manifest's inputs object, keyed by id, with each entry's five members as written
([chapter 2](#2-types-and-inputs)): `label` (string), `description` (lines or `null`), `format`
(a `$ref` into the bundle, `{ "$ref": "#/$defs/<id>" }`, or the inline schema), `required`
(boolean) and `channel`. Bare format ids are rewritten to `#/$defs/<id>`, as everywhere in the
document.

**The order is explicit** in `inputOrder`, since RFC 8785 sorts an object's members and the written
order is the Create page's.

#### 7.2.4 `formats` and `bindings`

**`formats` is one self-contained JSON Schema bundle:** `{ "$defs": { "<id>": <schema>, … } }`,
holding every format the package uses, from its three homes, with no shadowing between them:
- **built-ins** (`string`, `number`, `boolean`, `date`, `plaintext`, `markdown_block`,
  `markdown_inline`, `check_result`, …) from the package-format registry's definitions file;
- **catalogue formats** (`concept_list`, `classification`, …) from the formats catalogue at the
  pinned version, **only those used**;
- **package formats** from `formats/`.

Each entry keeps its `$id` URN ([chapter 2](#2-types-and-inputs)),
which names its origin and version; a package format's `$id` is derived at publish
(`urn:consultologist:package:example-nested-note@v2026.12.1:format:verdict`), never written in
source. Each entry keeps its `$schema` (`urn:consultologist:spec:31:dialect`, checked against
`specVersion` at publish) and its annotations (`contentMediaType`, `x-markdown`).
Inline schemas written on an input or a node stay inline where they're written; they carry no
`contentMediaType` or `x-markdown`.

**Formats are pure shape**: one `plaintext`, one `markdown_block`, one `boolean`,
with no producer families or prefixes. **Every node entry carries its `producer`**, as written
and checked against its kind: `"generated"` for an agent node, `"computed"` for every other
([chapter 2 § 1.3](#213-producer)). The rules for a model's output (strict
mode, the envelope, the sent-format record, a named format, a binding) apply to the output of a
node whose `producer` isn't `computed`. `kind: "agent"` is unchanged: the kind says how a node
runs; the producer says how its output can be verified.

**Two hashes per format**:
- **`formatHashes`**, the **full** hash: everything dereferenced, every keyword kept. It's what
  a model's reply is validated against.
- **`typeHashes`**, the **type** hash: references by name, sorted, annotations dropped. Type checks
  compare these: a written `format` against the derived one, `with` against parameters, branch
  results against each other.

**What a model receives** is its format with `title`, `$id` and the keywords strict mode rejects
(such as `format: "date"`) removed; the list comes from the attested agent definition, and the
reply is still validated against the full format. `resolve.json` keeps the full format; the record
holds the sent format's hash and the removed keywords ([chapter 9](#9-the-record)).

**`bindings`** records which attested agent serves each format and producer the package's agent
nodes use, keyed by format id, then producer, kept apart from the types so that a change of agent
and a change of type are distinguishable:

| Member | Type | Null | Meaning |
|---|---|---|---|
| `agentName` | string | never | the attested agent's name in the agents catalogue |
| `agentVersion` | integer | never | its version |
| `via` | string | never | the binding route: `"format"` for a registry or catalogue format bound in `agents/bindings.json`, `"custom"` for a package's own format bound to the catalogue's custom-format agent. `"producer"`, an agent chosen by producer alone, is [#1479](https://github.com/Consultologist/Consultologist-Blazor/issues/1479) (Milestone 40), added without changing the shape: **the value is reserved at 31 and refused** until then |

A binding holds no instructions: what the model should write is the format's own `description`s,
kept in the format above ([chapter 2 § 5.1](#251-the-annotations)).

A node never names an agent; its agent comes through its format's and producer's binding, and its
settings live in the attested agent definition.

#### 7.2.5 The flat maps: `nodes`, `checks`, `functions`

**The folder tree is flattened into one map per namespace, keyed by rooted key**, the same keys
the record uses.
`nodes` and `checks` are separate maps because `node.x` and `check.x` are separate roots
([chapter 1 § 9](#19-scopes-and-keys)): a node and a check may share an id. Each function's body is a `nodes` map of its own,
keyed by rooted keys local to the function (a function is a sealed scope).

Each entry holds **every header member as written** (chapters [1](#1-files-and-scopes) to
[6](#6-checks-deliverables-and-the-profile) define them per kind), canonicalised: bare format ids
rewritten to `#/$defs/<id>`, conditions and expressions in canonical JSON Logic
([chapter 3](#3-expressions)), reference strings (`in`, `ret`, a `case` subject, `with`) written
with their roots. The written `format`, `reproducible`, `producer`, `modelDerived`,
`runDependent` and `profileCarrying` are among them; publish has already checked each against the value it derives,
and refused a mismatch ([chapter 1](#1-files-and-scopes)). Publish then adds the **derived members**:

| Derived member | Type | Null | On | Meaning |
|---|---|---|---|---|
| `id` | string | never | every entry | the bare id (the file or folder name) |
| `parent` | string | allowed | every entry | the enclosing flow node's rooted key; `null` at the top level (of the package, or of a function). Not `in`, which a loop's header uses for its source |
| `nodes` | array of string | never | `for`, `while`, branches | the children's rooted keys, in order |
| `ret` | string | allowed | `for`, `while`, branches, functions | the returned node's rooted key |
| `reads` | array of string | never | every entry | every path the entry reads (header and body), canonical and sorted: `node.plan.value`, `input.consult_draft.content`, `item.value.point`, `run.date`, `profile.signature`, … Snippet and macro body reads count as the placing node's ([chapter 5](#5-templates-and-macros)) |
| `runDependent` | boolean | never | every entry | `true` when anything the entry reads is a `run.*` fact or a run-dependent value, transitively ([chapter 3](#3-expressions)). On a node or check entry it is the value the header declared, checked against this derivation; on other entries it is derived only |
| `profileCarrying` | boolean | never | every entry | `true` when the entry's value carries text a profile-reading macro body was substituted into, transitively ([chapter 3 § 4.6](#346-profile-carrying-is-contagious)). On a node or check entry it is the value the header declared, checked against this derivation; on other entries it is derived only. A condition passes none of the three flags on |
| `modelDerived` | boolean | never | every entry | `true` when the entry's value is computed from a model's output, directly or through other values: every agent node, and anything that reads a model-derived value, transitively ([chapter 3](#3-expressions)). On a node or check entry it is the value the header declared, checked against this derivation; on other entries it is derived only |
| `body` | string | allowed | templated kinds | the Scriban body inline (`\n` line endings); `null` for kinds with no body (`computed`, `for`, `while`, `if`, `case`, `call`) |
| `bodyHash` | string | allowed | templated kinds | `sha256:` over the body's UTF-8 bytes; `null` when `body` is `null` |
| `parts` | object keyed by part id | never | agent nodes | the node's parts, each with its `if` and its text (an array of lines); `{}` for none |
| `places` | array of string | never | agent nodes | the rooted ids of the macros its prompt places, its parts' text included, in order of appearance; `[]` for none |
| `renders` | array of render site | never | templated kinds | each pipe step into a `renderer.*`, in order of appearance: `{ "n": <1-based position>, "source": "<path>", "renderer": "<renderer id>" }`; a chain gives one entry per step, and a later step's `source` is the step before it. `[]` for none. Its position `n` is the record's `render:<n>` ([chapter 9](#9-the-record)). |
| `runSpots` | array of run spot | never | templated kinds | each run spot in the body ([chapter 5](#5-templates-and-macros)), the `{{run:<n>}}` marker's `n`: `{ "site": <1-based position>, "at": "<line>:<column>", "reads": "<path>" }`; `[]` for none. A run spot whose read pipes into renderers covers the whole pipeline. |
| `formatHash` | string | allowed | entries with a `format` | the resolved format's full hash, as in `formatHashes`; `null` for flow kinds that have none |
| `typeHash` | string | allowed | entries with a `format` | its type hash, as in `typeHashes`; `null` with `formatHash` |

`renderers`, `snippets`, `macros` and `deliverables` entries carry their header members the same
way, with `body`, `bodyHash`, `reads`, `runDependent`, `modelDerived`, `renders` and `runSpots`. A
deliverable's `reads` are its sources: the retired `sources` member is derived from them.

#### 7.2.6 `sourceHash`

`sourceHash` is the SHA-256 of a canonical listing of the source: a JSON array, sorted by path, of
`{ "path": "<path from the package root, / separated>", "hash": "sha256:<hash of the file's bytes>" }`
for every source file, canonicalised by RFC 8785. File hashes are taken **after line-ending
normalisation** ([chapter 1](#1-files-and-scopes)).

- **Included:** `manifest.json` and every file under `nodes/`, `checks/`, `functions/`,
  `renderers/`, `snippets/`, `macros/`, `formats/`, `deliverables/` and `tests/` (every
  `index.json` included), and any `README.md`.
- **Excluded:** `resolve.json`, `lock.json` and the publish report (evidence, never source), and
  `dag.mmd` (a view, regenerated).

So `tests/` is covered by `sourceHash`, and through it by `resolveHash`, without being embedded:
the engine never runs a test.

#### 7.2.7 `graph`

| Member | Type | Meaning |
|---|---|---|
| `edges` | array of `{ "from": string, "to": string, "kind": string }` | every dependency, from a node, check, input, `run.*` or `profile.*` read to what reads it. `kind` is one of `reads`, `if`, `for`, `ret`, `placed`, `calls`, `aligned`, `gates`, matching the diagram's edges ([chapter 8 § 8.14](#814-what-belongs-to-the-app)). Keys are rooted (`node.plan`, `check.coverage`, `input.consult_draft`, `deliverable.note`, `macro.letrozole`) |
| `order` | array of string | one topological order of the rooted keys, ties broken by source order. It's for readers and tools; the engine schedules by dataflow |

`dag.mmd` is drawn from this graph.

#### 7.2.8 `warnings`

Each warning is `{ "sentence": string, "at": string | null }`, the publish report's refusal shape:
the sentence word for word as publish gave it, and the file path it concerns
(`nodes/sections/outline.md`), or `null` for the package as a whole.
Warnings never block publish; run-spot warnings, the per-job ceiling note and
conversion hints are all here.

#### 7.2.9 An example: `example-nested-note` at 31 (abridged)

```jsonc
{
  "documentVersion": 1,
  "specVersion": 31,
  "package": { "name": "example-nested-note", "version": "v2026.12.1" },
  "title": "Nested note demo",
  "description": "A demonstration of nesting, computed values and while. Not intended for clinical use.",
  "tags": ["demo", "nested"],
  "sourceHash": "sha256:5e0c…",
  "lock": "lock.json",
  "requires": {
    "spec": "31",
    "evaluator": "^1.0.0",
    "scriban": "^7.2.5",
    "operations": { "size": "^1.0.0" },
    "kinds": ["agent", "computed", "for", "while"],
    "features": ["parallel"],
    "agents": { "consult-prose": "4", "custom-json": "1" }
  },
  "needs": { "profile": [] },
  "inputs": {
    "consult_draft": { "label": "Consult draft", "description": null,
                       "format": { "$ref": "#/$defs/markdown_block" }, "required": true, "channel": null }
  },
  "inputOrder": ["consult_draft"],
  "formats": { "$defs": {
    "markdown_block":  { "$schema": "urn:consultologist:spec:31:dialect",
                         "$id": "urn:…:format:markdown_block@…", "type": "string",
                         "contentMediaType": "text/markdown", "x-markdown": "block" },
    "plaintext":       { "$schema": "urn:consultologist:spec:31:dialect",
                         "$id": "urn:…:format:plaintext@…", "type": "string",
                         "contentMediaType": "text/plain" },
    "section_plan":    { "$schema": "urn:consultologist:spec:31:dialect",
                         "$id": "urn:consultologist:package:example-nested-note@v2026.12.1:format:section_plan",
                         "…": "…" },
    "outline": { "…": "…" }, "verdict": { "…": "…" }, "number": { "…": "…" } } },
  "formatHashes": { "plaintext": "sha256:…", "section_plan": "sha256:…", "…": "…" },
  "typeHashes":   { "plaintext": "sha256:…", "section_plan": "sha256:…", "…": "…" },
  "bindings": {
    "plaintext":    { "generated": { "agentName": "consult-prose", "agentVersion": 4, "via": "format" } },
    "section_plan": { "generated": { "agentName": "custom-json",   "agentVersion": 1, "via": "custom" } },
    "outline":      { "generated": { "…": "…", "via": "custom" } },
    "verdict":      { "generated": { "…": "…", "via": "custom" } }
  },
  "nodes": {
    "node.plan": { "id": "plan", "label": "Planning the sections", "kind": "agent", "producer": "generated", "parent": null,
                   "format": { "$ref": "#/$defs/section_plan" }, "reproducible": false,
                   "if": null, "onInvalid": "fail",
                   "reads": ["input.consult_draft.content"], "runDependent": false, "profileCarrying": false, "modelDerived": true,
                   "body": "You are planning the sections of a consultation note.\n…", "bodyHash": "sha256:…",
                   "parts": {}, "places": [], "renders": [], "runSpots": [],
                   "formatHash": "sha256:…", "typeHash": "sha256:…" },
    "node.section_count": { "id": "section_count", "label": "Counting the sections", "kind": "computed", "producer": "computed",
                            "parent": null, "format": { "$ref": "#/$defs/number" }, "reproducible": true,
                            "if": null, "onInvalid": "fail",
                            "expression": { "size": [ { "var": "node.plan.value.sections" } ] },
                            "reads": ["node.plan.value"], "runDependent": false, "profileCarrying": false, "modelDerived": true,
                            "body": null, "bodyHash": null, "renders": [], "runSpots": [],
                            "formatHash": "sha256:…", "typeHash": "sha256:…" },
    "node.sections": { "id": "sections", "label": "Sections", "kind": "for", "producer": "computed", "parent": null,
                       "format": "…", "reproducible": false,
                       "in": "node.plan.value.sections", "itemLabel": "title",
                       "parallel": true, "maxParallel": null, "until": null, "if": null,
                       "nodes": ["node.sections.outline", "node.sections.paragraphs"],
                       "ret": "node.sections.paragraphs",
                       "reads": ["node.plan.value"], "runDependent": false, "profileCarrying": false, "modelDerived": true,
                       "body": null, "bodyHash": null, "renders": [], "runSpots": [], "…": "…" },
    "node.sections.outline":    { "…": "…", "parent": "node.sections" },
    "node.sections.paragraphs": { "…": "…", "kind": "for", "producer": "computed", "parent": "node.sections",
                                  "modelDerived": true, "runDependent": false, "profileCarrying": false,
                                  "in": "node.sections.outline.value.points",
                                  "nodes": ["node.sections.paragraphs.draft_paragraph"],
                                  "ret": "node.sections.paragraphs.draft_paragraph" },
    "node.sections.paragraphs.draft_paragraph": { "…": "…", "kind": "agent", "producer": "generated",
                                  "parent": "node.sections.paragraphs",
                                  "format": { "$ref": "#/$defs/plaintext" }, "reproducible": false,
                                  "modelDerived": true, "runDependent": false, "profileCarrying": false,
                                  "reads": ["input.consult_draft.content", "item.id",
                                            "item.parent.value.title", "item.value.point"] },
    "node.refine": { "id": "refine", "label": "Refining the summary", "kind": "while", "producer": "computed", "parent": null,
                     "modelDerived": true, "runDependent": false, "profileCarrying": false,
                     "while": { "!==": [ { "var": "node.refine.judge.value.verdict" }, "good" ] }, "max": 3,
                     "nodes": ["node.refine.draft_summary", "node.refine.judge"],
                     "ret": "node.refine.draft_summary", "…": "…" },
    "node.refine.draft_summary": { "…": "…" }, "node.refine.judge": { "…": "…" }
  },
  "checks": {}, "functions": {}, "renderers": {}, "snippets": {}, "macros": {},
  "deliverables": {
    "deliverable.note": { "id": "note", "label": "Nested consultation note", "kind": "rendered",
                          "format": { "$ref": "#/$defs/markdown_block" }, "if": null, "check": null,
                          "whenEmpty": "fail",
                          "reads": ["node.refine.content", "node.sections.items"],
                          "runDependent": false, "profileCarrying": false, "modelDerived": true,
                          "body": "## Summary\n\n{{ node.refine.content }}\n…", "bodyHash": "sha256:…",
                          "renders": [], "runSpots": [] }
  },
  "graph": {
    "edges": [ { "from": "input.consult_draft", "to": "node.plan", "kind": "reads" },
               { "from": "node.plan", "to": "node.section_count", "kind": "reads" },
               { "from": "node.plan", "to": "node.sections", "kind": "for" },
               { "from": "node.sections", "to": "deliverable.note", "kind": "reads" },
               { "from": "node.refine", "to": "deliverable.note", "kind": "reads" } ],
    "order": ["input.consult_draft", "node.plan", "node.section_count", "node.sections", "…",
              "deliverable.note"]
  },
  "run": [],
  "warnings": []
}
```

The member names of loops, `while`, `until` and deliverable headers are defined in chapters
[4](#4-loops-and-functions) and [6](#6-checks-deliverables-and-the-profile); the example only
shows where they sit. `"…"` marks elision. The loop is `sections`, not 30's `parts`, since `parts`
is a reserved id at 31; the migration renames it ([chapter 10 § 10.6](#106-reserved-ids-are-renamed)).

### 7.3 `requires` and `needs`

Both are **derived, never authored,** and **minimal**: only what the package uses, so a package
without `call` runs on an engine without functions.

#### 7.3.1 `requires`: what the package needs from the engine

| Member | Type | Null | Lists |
|---|---|---|---|
| `spec` | string | never | the spec version, `"31"` |
| `evaluator` | string (caret range) | never | the JSON Logic evaluator's range. It's **our** evaluator's version, behind our own interface: our null rules, `===`/`!==` only, the canonical form. The library underneath (`Corvus.Text.Json.JsonLogic`) is pinned exactly and listed in `lock.json`. Revisiting this towards off-the-shelf components throughout, possibly the evaluator too, is [#1477](https://github.com/Consultologist/Consultologist-Blazor/issues/1477) (Milestone 40) |
| `scriban` | string (caret range) | never | Scriban's range, for example `"^7.2.5"`. With `lock.json`, this records the Scriban version that `templating` used to name in the manifest ([chapter 1](#1-files-and-scopes)) |
| `operations` | object, operation name → caret range | never | each built-in custom operation **used**: from `size`, `blank`, `words`, `lines`, `lower`, `trim`, `starts_with`, `ends_with`, `plain`, `object`, `matches`, `has_word`, `terms_subset`, `all_pass`, `count_pass`, `days_between`, `years_between`, `add_days` ([chapter 3](#3-expressions)); `{}` for none |
| `kinds` | array of string | never | the node kinds used, from `agent`, `rendered`, `computed`, `for`, `while`, `if`, `case`, `call` |
| `features` | array of string | never | behaviours not tied to one kind: `parallel` (a loop with `parallel: true`), `macro-markers`, `parts`, `run-spots`, `check-loops`; `[]` for none |
| `agents` | object, agent name → version string | never | the attested agents (name and exact version) the `bindings` name; `{}` for none |

**Not listed:** package content (prompts, snippets, renderers, formats, functions), which is
embedded and covered by the hash; catalogue versions, which are in `lock.json`; delivery kinds, since
an unsupported kind is produced and recorded as not sent.

**The value validator** (`Corvus.JsonSchema` behind our own interface) and **Markdig** are not in
`requires`. They're pinned exactly in `lock.json` and covered by the engine's break points (§ 7.4);
a change in their output reaches packages through the versions of what uses them (the evaluator,
`plain`, the Markdown escaping), which golden tests guard (§ 7.4.3).

**The engine checks `requires` before the job starts,** when the Create page asks, and again when
the job starts, and compares `lock.json`'s exact versions with its break points (§ 7.4.4).
Anything missing, out of range or locked before a break point refuses with the sentences of § 7.10.

#### 7.3.2 `needs`: what the account must provide

| Member | Type | Null | Lists |
|---|---|---|---|
| `profile` | array of string | never | the `profile.*` fields any template reads, from `name`, `credentials`, `organisation`, `signature`, `closing` ([chapter 6](#6-checks-deliverables-and-the-profile)), sorted; `[]` for none |

The Create page reads `needs` before submission and refuses, naming the field, when the account
hasn't set it (§ 7.10). An empty or whitespace-only profile value counts as not set
([chapter 6](#6-checks-deliverables-and-the-profile)).

### 7.4 `lock.json`

#### 7.4.1 Members

The members of `lock.json`, as [`lock.schema.json`](v31/schemas/lock.schema.json) states them:

| Member | Type | Null | Meaning |
|---|---|---|---|
| `documentVersion` | integer | never | the shape of `lock.json`; `1` at 31 |
| `package` | object `{ name, version }` | never | as in `resolve.json` |
| `resolve` | object `{ hash: string }` | never | the hash of the `resolve.json` this lock belongs to |
| `resolver` | object `{ packageFormat: string, dialect: string }` | never | the format library and registry release that resolved and validated it (`package-format@v2026.12.1`), and the Scriban dialect spec's version |
| `libraries` | object, package id → exact version | never | the third-party libraries whose change could alter a rendered prompt, a validation verdict, a composed document or a hash, each **exact**: `Scriban`, `Markdig`, `Corvus.Text.Json.JsonLogic`, `Corvus.JsonSchema` |
| `evaluator` | string | never | our evaluator's exact version (`"1.0.0"`) |
| `operations` | object, operation name → exact version | never | each built-in operation the package uses (the same names as `requires.operations`), exact; `{}` for none |
| `builtins` | object, name → exact version | never | the built-in machinery that isn't an operation: `markdown_escape` (escaping plain text into Markdown), `plain_conversion` (Markdown to plain text), `formats` (the built-in format definitions), `printer` (the condition printer, [chapter 3](#3-expressions)), and each built-in renderer the package uses (`concept_bullets`, `concept_context`, [chapter 5](#5-templates-and-macros)). |
| `culture` | string | never | `"invariant"`: every render and operation runs in the invariant culture |
| `runtime` | object `{ dotnet: string, unicode: string }` | never | the exact .NET runtime that published the package (`"10.0.3"`) and the Unicode version its text handling follows (`"16.0"`). `lower`, `trim`, `words` and `has_word` depend on both; the conformance suite carries vectors for each ([chapter 12](#12-conformance)) |
| `catalogues` | object | never | `formats` (the formats catalogue, `formats@v…`: types), `agents` (the agents catalogue, `agents@v…`: bindings and attested agent definitions), `outputContracts` (`output-contracts@v…`, or `null` when the package uses none), as **separate entries** |

**Recorded, not locked as a range:** the .NET runtime and its Unicode version (`runtime`), so a
change in case mapping or word characters is visible between two records. **Not locked:** the
JSON and HTTP libraries, Durable Functions, the Azure SDKs. The engine's
commit and release stay on the job's record.
**No time stamp** is written (§ 7.1).

```jsonc
{
  "documentVersion": 1,
  "package": { "name": "example-nested-note", "version": "v2026.12.1" },
  "resolve": { "hash": "sha256:9b41…" },
  "resolver": { "packageFormat": "package-format@v2026.12.1", "dialect": "scriban-dialect@1.0.0" },
  "libraries": { "Corvus.JsonSchema": "4.3.17", "Corvus.Text.Json.JsonLogic": "5.8.11",
                 "Markdig": "0.41.3", "Scriban": "7.2.5" },
  "evaluator": "1.0.0",
  "operations": { "size": "1.0.0" },
  "builtins": { "formats": "1.0.0", "markdown_escape": "1.0.0", "plain_conversion": "1.0.0",
                "printer": "1.0.0" },
  "culture": "invariant",
  "runtime": { "dotnet": "10.0.3", "unicode": "16.0" },
  "catalogues": { "agents": "agents@v2026.12.1", "formats": "formats@v2026.12.1", "outputContracts": null }
}
```
(Library versions are illustrative.)

#### 7.4.2 Lock exactly, refuse by compatible range

- **`lock.json` records the exact version that checked the package;** `requires` states a
  compatible range; **the engine refuses only outside the range;** the record names the exact
  versions that ran ([chapter 9](#9-the-record)). A package locked at Scriban 7.2.5 runs on 7.2.6, and the record says
  so.
- **Ranges are caret only:** `^7.2.5` means at least 7.2.5 and below 8.0.0, so only a major version
  leaves the range.
- **The registry sets each range at publish,** from the locked version and the component's version
  policy. Authors never write ranges.
- **A library pinned exactly in `Directory.Packages.props`** (Markdig, both Corvus libraries, and
  Scriban) moves only by a deliberate upgrade under § 7.4.4.

#### 7.4.3 Versioning built-in operations and machinery

- **Semantic versions, with any change to output bytes a major version.** Additions are minor;
  internal fixes with identical output are patch.
- **Each version is declared in the package-format registry** beside the built-in formats, in
  [`v31/constants.json`](v31/constants.json): each operation's under `operations`, the evaluator's
  under `evaluator`, and each piece of built-in machinery's (the built-in renderers included) under
  `builtins`.
- **Golden tests** per operation and per piece of built-in machinery (fixed inputs, fixed expected
  bytes) are part of the conformance suite and **fail CI** if output changes without a major bump.
- **Package renderers** are package templates covered by `resolve.json`'s hash, and need
  no version of their own. **Built-in renderers** (`concept_bullets`, `concept_context`) are
  Scriban templates in the registry, versioned like operations and locked in `builtins`; their ids
  are reserved ([chapter 5](#5-templates-and-macros)).

#### 7.4.4 Upgrading a locked library: the corpus re-render

**Before any upgrade of a locked library, the registry re-renders a test corpus** under the current
and the candidate version: every published 31 package's templates and operations on fictional
values, its in-package tests, and the conformance suite's golden tests. **Any byte difference blocks
the upgrade** until it's understood. If the upgrade is adopted anyway, it counts as **major** for
our purposes, whatever the library calls it, and packages locked to the old version are refused
until republished.

**How "counts as major" reaches the engine** when the library's own version stays inside the caret
range. `requires` has no per-component floor: the caret range's lower bound is already
the package's floor, and a published document never changes. Instead:
- **The engine keeps a list of break points per locked component,** each the version at which
  output changed (for example *"Scriban output changed at 7.3.0"*).
- **At job start it compares them with the exact versions in the package's `lock.json`,** and
  refuses a package locked before a break point with the sentence of § 7.10, as for a version
  outside the range.
- **The list is engine configuration,** changed only by an upgrade that went through the corpus
  re-render above.

Swapping either Corvus library for json-everything ([#1458](https://github.com/Consultologist/Consultologist-Blazor/issues/1458), [#1459](https://github.com/Consultologist/Consultologist-Blazor/issues/1459)) follows the same rule: byte-identical
golden tests and corpus re-render, or it counts as major.

### 7.5 The publish pipeline

Publish runs the same steps whatever starts it: CI from a tag in `consultologist-workflows`, or the
engine's `WorkflowPackages/Publish` endpoint (the Editor, the API, the operator's bulk migration).
In order:

0. **Receive.** Any `resolve.json`, `lock.json` or publish report in the upload is **dropped
   unread** (§ 7.7). Line endings are normalised (`\r\n` to `\n`; a lone `\r` is refused) and each
   normalised file is noted for the report ([chapter 1](#1-files-and-scopes)). Every
   `SourceBounds` bound is checked. A version that already exists is refused, as today.
1. **Resolve.** Read the file model; compute **`sourceHash`** (§ 7.2.6); flatten the tree into
   rooted keys; resolve every `$ref` against the built-ins and the pinned catalogues, rewriting
   bare ids; embed every body; derive `reads`, `runDependent`, `modelDerived`, `profileCarrying`, `renders`,
   `runSpots`, the graph, `requires` and `needs`; compile `resolve.json` **in memory**.
2. **Validate.** Every rule of chapters [1](#1-files-and-scopes) to
   [6](#6-checks-deliverables-and-the-profile): the file model, types, JSON Logic typing, the Scriban
   dialect, scopes, macros, checks, deliverables, and the written `format`, `reproducible`,
   `producer`, `modelDerived`, `runDependent` and `profileCarrying` against the derived ones. **Any refusal stops publish** with every refusal sentence found, each
   with its file path. Warnings are collected.
3. **Test.** Run every `tests/<id>.json` offline against the in-memory `resolve.json` (§ 7.8). **A
   failing test stops publish** with the test's id and its first mismatch.
4. **Compute, then write.** The order is:
   1. compute `sourceHash` (done in step 1);
   2. compile `resolve.json` in memory (step 1) and take **`resolveHash`** from its canonical bytes;
   3. build `lock.json` in memory with `resolveHash`, and take **`lockHash`**;
   4. build the publish report with all three hashes, the time and the test results;
   5. write into the registry's `{name}/{version}/`: the source files and the regenerated `dag.mmd`,
      then `lock.json`, then the publish report, then **`resolve.json` last**.

   6. write the version's **"published" stamp last**, recording `resolveHash` and `lockHash`.

   Every hash is taken from final bytes. **A version exists only once stamped:** the engine and
   the registry ignore a folder without the stamp, so a publish that dies partway can be retried
   from step 0, overwriting the unstamped folder. **A stamped version folder is immutable**;
   nothing writes to it again. At load the engine checks `resolve.json`'s hash, `lock.json`'s
   hash and `lock.json`'s `resolve.hash` against the stamp ([chapter 8 § 8.2](#82-the-load-step-by-step-31)).

Validation and tests run against `resolve.json`, the document the engine will run, never against the
source a second time. The Editor's "Run tests" and CI run steps 0–3 without writing.

### 7.6 Where the files live

| | Example and demo packages | Account packages |
|---|---|---|
| **Source lives** | the public `consultologist-workflows` repository | the registry only (written by the Editor or `WorkflowPackages/Publish`) |
| **Published by** | CI, from a tag | the engine's publish endpoint |
| **`resolve.json`, `lock.json`** | the registry's `{name}/{version}/`, and **GitHub Release assets** on the version's tag, byte-identical so their hashes match the records | the registry's `{name}/{version}/`; **"Download package"** in the Editor includes them for a published version; the Editor and History show the compiled document and its toolchain for versions the account owns |
| **Publish report** | the registry, and a Release asset | the registry; shown in the Editor after publish |
| **`dag.mmd`** | committed beside the source, regenerated by the tools and checked by CI; regenerated at publish | generated at publish into the version's folder; shown in the Editor's Graph pane |

The Serverless Workflow export (`workflow.sw.json`) is a view too, and follows `dag.mmd`'s rule when
it ships in Milestone 40 ([#1422](https://github.com/Consultologist/Consultologist-Blazor/issues/1422)).

```
{name}/{version}/                    in the registry
  manifest.json
  nodes/ checks/ functions/ renderers/ snippets/ macros/ formats/ deliverables/ tests/
                                     all nine, always, each with its index.json
  dag.mmd                            view
  resolve.json                       evidence: what the engine runs
  lock.json                          evidence: what checked it
  publish-report.json                the publish's outcome, tests included
```

### 7.7 Evidence and views

**The rule: evidence is publish-only; views may be committed**.

| | Evidence: `resolve.json`, `lock.json` | Views: `dag.mmd` (and `workflow.sw.json`, M40) |
|---|---|---|
| **Claims** | what the package is and what checked it; records pin their hashes | nothing; for readers |
| **Written by** | publish only | the tools, CI and publish |
| **In source** | never: not in the repository, not in an account's working copy | example packages: committed and CI-checked; account packages: generated at publish |

**Never trust an uploaded copy:**
- **Importing a package** (a .zip) that contains `resolve.json` or `lock.json` ignores them, and
  the Editor says so once (§ 7.10). Publishing always regenerates both.
- A `resolve.json` or `lock.json` **committed to the examples repository** is ignored by publish, and
  CI warns that it shouldn't be there (§ 7.10).
- A committed `dag.mmd` that differs from a fresh one **fails CI**.

### 7.8 In-package tests (`tests/`)

Packages carry their own tests, run **offline**: a test makes no model calls. It runs on the
engine's deterministic harness, the one the migration builds for byte-equivalence ([chapter 10 § 10.12](#1012-the-snapshot-test)), with
every agent node's output stubbed.
Tests against live models are Milestone 40 ([#1402](https://github.com/Consultologist/Consultologist-Blazor/issues/1402), [#1415](https://github.com/Consultologist/Consultologist-Blazor/issues/1415)).

**Where they run:** CI in the public repository; "Run tests" in the Editor; and **at publish, where a
failing test blocks publish** (§ 7.5, step 3). **Results go in the publish report, never in job
records**.

#### 7.8.1 The file: `tests/<id>.json`

One test per file, described by [`test.schema.json`](v31/schemas/test.schema.json); the file name is the id (`^[a-z][a-z0-9_]*$`, as every id). Pure JSON, no front
matter. Every member is present.

| Member | Type | Null | Meaning |
|---|---|---|---|
| `description` | array of string (lines) | allowed | what the test pins; `null` for none |
| `inputs` | object keyed by input id | never | a **fictional** value for **every** declared input, valid against its format, or `null` for an optional input left unset. The value is the raw value, as `input.<id>.value` reads it. Never patient text. Document-filled inputs take their text form here; file fixtures are Milestone 40 ([#1442](https://github.com/Consultologist/Consultologist-Blazor/issues/1442)) |
| `profile` | object keyed by profile field | never | a fixed fictional value for **exactly** the fields in `needs.profile`; `{}` when it's empty |
| `run` | object keyed by run fact | never | a fixed value for **exactly** the facts in `resolve.json`'s `run`: `"date": { "value": "2026-11-16", "timeZone": "America/Toronto" }`, `"id"`, `"package"`, `"engine"` as strings; `{}` when none is read |
| `outputs` | object keyed by stub key | never | a stubbed value for every agent node instance that runs, valid against the node's format (§ 7.8.2) |
| `expect` | object | never | the expectations (§ 7.8.3); `{}` checks only that the run completes |

#### 7.8.2 Stub keys

A stub key is the node's **rooted key**, then, for an instance inside a loop or a `while`, `:` and
its path: item ids and pass numbers from the outermost inward, joined by `/`, exactly the record's
row key ([chapter 9](#9-the-record)): `node.plan`, `node.sections.outline:2`,
`node.sections.paragraphs.draft_paragraph:2/1`, `node.refine.judge:3`. Inside a function the key
goes through the call node: `node.hpi_section.standard_draft`.

- A text format's stub is a JSON string; a data or object format's stub is the JSON value.
- **A node that runs with no stub** is an error (§ 7.10). **A stub for a node that doesn't run** is a
  warning. **A stub invalid against its format** is an error, validated as an agent reply would be.
- Classifiers (agent nodes returning `judgement` or `classification`) are stubbed like any agent node, so every
  condition that reads them is decided by the test.

#### 7.8.3 Expectations

`expect` lists what is checked. **An omitted expectation means "not checked",** which is distinct
from `null` (the rule that every member is present applies to members of declarations, not to the expectations listed). Its
members, each optional:

| Member | Type | Checks |
|---|---|---|
| `ran` | array of row key | these instances completed |
| `skipped` | array of row key | these instances were skipped (by condition, or not run by `until` or `max`) |
| `decisions` | object, decision id → boolean or branch id | each listed condition's result ([chapter 9 § 9.3](#93-sub-row-ids)'s ids) |
| `loops` | object, row key → `{ "count": integer }` or `{ "passes": integer, "stopped": string }` | loop counts, `while` passes and how a `while` or `until` stopped |
| `values` | object, row key → JSON value | `computed` values, compared as canonical JSON |
| `prompts` | object, row key → `{ "text": string }` or `{ "hash": string }` | the sent text of an agent node's prompt, exactly or by its sent-text hash |
| `checks` | object, check row key → `{ "pass": boolean }` | check results, named as `check_result`'s `pass` |
| `deliverables` | object, deliverable key → `{ "state": string, "text": string }` or `{ "state": string, "hash": string }` | each deliverable's state (`released`, `held`, `failed`, `skipped`, `blocked`) and its composed text or hash |

**A test passes** when the run completes (or fails exactly where `expect` says, through a
deliverable's `fail`) and every listed expectation holds. Only the **first mismatch** is reported:
the first failing expectation in the order of the table above, then by key.

#### 7.8.4 Limits and the migration's snapshot test

- Test files count against `SourceBounds` like any source file. **At publish, all tests together
  have 60 seconds;** past it, publish stops with a sentence.
- **The migration writes one snapshot test per package,** `tests/migration_snapshot.json`, from
  its migrated run: fictional inputs, stubs generated from the formats, and the resulting prompts
  and deliverables as expectations **by hash**, so every migrated package starts with one test
  pinning its behaviour ([chapter 10 § 10.12](#1012-the-snapshot-test)).

#### 7.8.5 Example (made-up package `example-checks`, fictional values)

```jsonc
// tests/two_sections.json
{
  "description": ["Two planned sections; the second fails coverage; the note is held."],
  "inputs": { "referral": "Margaret Okafor, 58, referred for fatigue and a raised TSH (fictional)." },
  "profile": { "signature": "Dr A. Fictional\nInternal Medicine" },
  "run": { "date": { "value": "2026-11-16", "timeZone": "America/Toronto" } },
  "outputs": {
    "node.plan": { "sections": [ { "title": "History" }, { "title": "Plan" } ] },
    "node.sections.draft:1": "Fatigue for three months; no weight change.",
    "node.sections.draft:2": "Repeat thyroid tests in six weeks."
  },
  "expect": {
    "checks": { "check.part_coverage.coverage:1": { "pass": true },
                "check.part_coverage.coverage:2": { "pass": false },
                "check.all_covered": { "pass": false } },
    "deliverables": { "deliverable.note": { "state": "held", "hash": "sha256:…" } }
  }
}
```

### 7.9 The publish report

Built at step 4 (§ 7.5) and written into the version's folder, as canonical JSON; returned in full by
the publish endpoint and printed by CI whether publish succeeds or not. **Not evidence:** records
never pin it, and it says nothing about a job. It's `publish-report.json`, media type
`application/vnd.consultologist.publish-report+json`, in the version's folder and, for example
packages, a Release asset. It holds the time, each test's result with its hashes, any line-ending
normalisation, the warnings, and the per-job ceiling note. Its schema is
[`publish-report.schema.json`](v31/schemas/publish-report.schema.json).

| Member | Type | Null | Meaning |
|---|---|---|---|
| `documentVersion` | integer | never | `1` |
| `package` | object `{ name, version }` | never | the version published |
| `outcome` | `"published"` or `"refused"` | never | a written report always says `published`; a refused publish returns the report without writing it |
| `publishedAtUtc` | string (RFC 3339) | allowed | when it was written; `null` when refused |
| `publishedBy` | string | never | `ci` with the tag, `editor`, `api` or `operator-migration` |
| `sourceHash` | string | never | as in `resolve.json` |
| `resolveHash` | string | allowed | `null` when publish stopped before step 4 |
| `lockHash` | string | allowed | `null` when publish stopped before step 4 |
| `normalised` | array of string | never | the paths whose line endings were normalised at step 0; `[]` for none |
| `refusals` | array of `{ sentence, at }` | never | every refusal sentence, with its file path; `[]` when published |
| `warnings` | array of `{ sentence, at }` | never | as `resolve.json`'s `warnings`, the per-job ceiling note included |
| `tests` | array of test result | never | one per test, in id order; `[]` for none |

**A test result:**

| Member | Type | Null | Meaning |
|---|---|---|---|
| `id` | string | never | the test's id |
| `fileHash` | string | never | `sha256:` of the test file's bytes |
| `result` | `"pass"` or `"fail"` | never | named as a check's verdict; `passed` only ever means a count |
| `outcomeHash` | string | never | `sha256:` over the harness's canonical outcome (row keys, decisions, values, sent-text hashes, deliverable states and hashes), so two runs of the same test can be compared |
| `firstMismatch` | object `{ expectation: string, key: string, expected: string, actual: string }` | allowed | `null` when passed. `expected` and `actual` are hashes for text, values for everything else |
| `durationMs` | integer | never | the test's run time |

### 7.10 Refusals

Every sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this format. `<…>`
marks a placeholder.

**At start** (the Create page, then the engine), from `requires`, `needs` and the engine's break
points (§ 7.4.4):
- *"This workflow (\<package\>@\<version\>) needs \<component\> \<range\>; this engine runs \<component\> \<engine version\>. Publish a new version of the workflow to run it on this engine."*
  (`<component>` is `Scriban`, `the evaluator` or an operation's name). The same sentence covers a
  package locked before one of the engine's break points (§ 7.4.4).
- *"This workflow (\<package\>@\<version\>) needs \<kind or feature\> '\<name\>', which this engine doesn't support. Publish a new version of the workflow to run it on this engine."*
- *"This workflow (\<package\>@\<version\>) needs agent \<agent name\> version \<version\>, which this engine doesn't have. Publish a new version of the workflow to run it on this engine."*
- *"This workflow needs your signature. Choose one in Profile."*; for other fields,
  *"This workflow needs your \<field label\>. Set it in Profile, under Letter details."*
- *"Set your time zone in your account settings before running a workflow."* Every 31 job, until the account's time zone is set (31 jobs only).
  No `needs` member is required, since every 31 job needs the zone.

**At load** (the engine refuses a document whose bytes don't match):
- *"Workflow \<package\>@\<version\> can't run: its compiled document doesn't match the hash published for it."*
- *"Workflow \<package\>@\<version\> can't run: its lock doesn't match the hash published for it, or doesn't belong to its compiled document."*

**At publish, from tests** (§ 7.8):
- *"Test '\<test id\>' failed: \<expectation\> for \<key\> expected \<expected\>, got \<actual\>. Publish stopped."* The refusal names the test and its first mismatch.
- *"Test '\<test id\>' has no stub for \<row key\>, which runs. Add it to outputs."*
- *"Test '\<test id\>' stubs \<row key\> with a value that isn't \<format\>: \<first validation error\>."*
- *"Test '\<test id\>' gives no value for input '\<input id\>'. List every input; use null for an optional input left unset."*
- *"Test '\<test id\>' must give exactly the profile fields the workflow reads: \<fields\>."* and *"Test '\<test id\>' must give exactly the run facts the workflow reads: \<facts\>."*
- *"Tests took longer than 60 seconds in all. Publish stopped."*

**Warnings** (never blocking):
- *"Test '\<test id\>' stubs \<row key\>, which doesn't run."*
- CI, in the examples repository: *"\<path\> is evidence written only by publish; it is ignored and shouldn't be committed."*
- The Editor, on import: *"This package's resolve.json and lock.json were ignored; publishing writes new ones."*

## 8. What an engine does with a package

This chapter says what an engine does with a package at 31: which load path it takes, how it checks
what it loads, which versions it admits, how it schedules a job, what it limits, where it writes the
record and how it delivers. What the engine reads is only [`resolve.json`](#72-resolvejson) and the
checked [`lock.json`](#74-lockjson) beside it ([chapter 7](#7-the-compiled-documents)); the record
it writes is [chapter 9](#9-the-record). The sentences the engine shows are in § 8.13. The pages,
`WorkflowPackages/Current` and the diagram are the app's (§ 8.14), and the sentences the pages show
close the chapter (§ 8.15).

### 8.1 Two load paths, chosen by `specVersion`

| Spec version | What the engine reads | Until |
|---|---|---|
| 5–30 | today's path: `manifest.json` and the source files, materialised and validated per load (`WorkflowPackageStore`) | retirement, [#1450](https://github.com/Consultologist/Consultologist-Blazor/issues/1450) (Milestone 40) |
| 31 | **only `resolve.json`** from the published version's folder in the registry | — |

- **No backfill.** Versions published before 31 never get a `resolve.json`; they keep today's path
  until they are retired. Packages that must keep running are migrated, which gives them a real
  `resolve.json` and `lock.json` ([chapter 10](#10-migration-30--31)).
- **The engine never reads a 31 package's source tree** at job time. Bodies are inline in
  `resolve.json`, so one document and one hash cover everything.
- **`lock.json` is not needed to run,** but it is checked at load: its hash, and its link to
  `resolve.json` (§ 8.2, step 3). The exact versions it holds are for the record, for the break
  points of step 4, and for the library-upgrade rule
  ([chapter 7 § 7.4.4](#744-upgrading-a-locked-library-the-corpus-re-render)).

### 8.2 The load, step by step (31)

1. **Resolve the pin** to a `name@version`, as today (`WorkflowPackagePinResolver`).
2. **Read `resolve.json`** and **`lock.json`** from the version's folder.
3. **Check integrity.** The SHA-256 of `resolve.json`'s bytes (canonical, RFC 8785) must equal the
   hash published for that version; `lock.json`'s hash must equal its published hash; and the link
   between them must hold (`resolve.json`'s pointer to its lock names that `lockHash`,
   [chapter 7](#7-the-compiled-documents)). A mismatch of any of the three refuses the load. The
   published hashes are in the version's stamp ([chapter 7 § 7.5](#75-the-publish-pipeline)), and
   **a version without the "published" stamp doesn't exist** for the engine: publish writes the
   stamp last, so a publish that died partway is never loaded, and stamped folders are never
   changed.
4. **Check `requires`** against this engine: `spec`, `evaluator`, `scriban`, each operation's range,
   `kinds`, `features` and `agents`. Ranges are caret ranges set by the registry
   ([chapter 7 § 7.3.1](#731-requires-what-the-package-needs-from-the-engine)); the engine refuses
   only outside a range. An unknown kind or feature is outside every range. Then **compare
   `lock.json`'s exact versions with the engine's break points:** the engine keeps, per locked
   component, the versions at which output changed (*"Scriban output changed at 7.3.0"*), as
   configuration changed only by an upgrade that went through the corpus re-render, and refuses a
   package locked before a break point with the sentence of
   [chapter 7 § 7.10](#710-refusals) ([§ 7.4.4](#744-upgrading-a-locked-library-the-corpus-re-render)).
5. **Build the in-memory plan:** the parsed graph, the compiled JSON Logic, the parsed Scriban
   templates and the resolved formats. **The plan is never stored;** it is derived
   deterministically from `resolve.json` and cached in memory per `name@version`, keyed also by
   the `resolveHash`.
6. **At job start,** check `needs.profile` and the account's time zone, which every 31 job needs
   ([chapter 6 § 6.10.4](#6104-a-missing-field-refuses-the-job) and
   [§ 6.10.7](#6107-the-profile-page-and-the-time-zone)). Then record `resolveHash` and `lockHash`
   beside the package name and version, before any node runs.

A refusal at steps 3 or 4 is a start failure: no node runs, and the job's record holds the
sentence. The app's Create page checks steps 4 and 6 before submission (§ 8.14), so in practice the
clinician sees the sentence there first.

### 8.3 Which spec versions an engine admits

#### 8.3.1 The compiled-in lists

- **The compiled-in list** stays `WorkflowPackageValidator.AcceptedSpecVersions` (publish) and
  `WorkflowPackageStore.SupportedSpecVersions` (load), 5–30 today. **31 joins both lists only at
  the bump,** the release that makes 31 accepted, made after a drain (§ 8.9).
- **Before the bump, the preview setting admits 31 on dev alone** (§ 8.3.2).
- **Production without the setting** answers a 31 publish or load with today's sentence:
  *"specVersion 31 is not supported: this engine accepts specVersion \<list\> (pre-v5 packages are archived; see registry-operations.md)."*

#### 8.3.2 `WorkflowPackages__PreviewSpecVersions`

Version 31 is proven on `canada-east-ai-function-dev` first, with dev's own package registry, and
production's registry never sees a 31 package until the bump.

| | |
|---|---|
| **Type** | a comma-separated list of integers, for example `31` |
| **Unset or empty** | no preview versions: only the compiled-in list is admitted. This is production's value, always |
| **Effect** | each listed version is admitted **beside** the compiled-in list, everywhere a version is checked: publish, import, load, job start, `WorkflowPackages/Current` |
| **Allowed values** | only versions this build implements but has not yet released. In Milestone 39 that is `31` alone |
| **Set on** | `canada-east-ai-function-dev` only |
| **Removed** | at the bump, when 31 joins the compiled-in list |

- **A listed version this build doesn't implement** stops the host at startup, naming the setting
  and the value: a typo must not silently admit nothing, and an unimplemented version must never
  be admitted.
- **The engine attestation** (`EngineAttestation`) lists preview versions separately, as
  `PreviewSpecVersions`, beside `AcceptedSpecVersions` and `SupportedSpecVersions`, so an
  attestation never presents a preview version as released.

### 8.4 Scheduling

#### 8.4.1 What runs when

The orchestrator runs the plan's graph as today: a node is ready when everything it reads has
settled, loops fan out per item, `while` runs pass by pass, branches decide before their bodies.
What changes at 31:

- **The order comes from `resolve.json`** (`graph.order` and the edges), not from walking the
  manifest.
- **`computed` nodes, conditions and checks** run in the orchestrator through the JSON Logic
  evaluator ([chapter 3](#3-expressions)), with no activity and no model call. They are evaluated
  inline in the orchestrator, as a deterministic function of recorded values, so replay reproduces
  them; `rendered` nodes and deliverables render in an activity, as templates do today.
- **A `call`'s function body runs inline** in the job's orchestration, never as a Durable
  sub-orchestration: its nodes are scheduled by the same loop as every other node, so the per-job
  ceiling, the total-work limits and the dispatch order of § 8.5 hold inside functions. Its rows
  are keyed under the call ([chapter 9 § 9.2](#92-keys-with-their-roots)). Sub-orchestrations with
  a shared ceiling are [#1493](https://github.com/Consultologist/Consultologist-Blazor/issues/1493)
  (Milestone 40).
- **`matches` reads no clock:** there is no wall-clock time-out; the bounds that keep it linear
  are [chapter 3 § 3.5.3](#353-matches-and-has_word)'s. Every time the orchestrator records (a
  decision's `decidedAtUtc`) comes from the orchestration's replay-safe clock.
- **Check loops** are scheduled per item, as soon as their production item settles, not after the
  whole production loop.

### 8.5 The per-job ceiling

- **An engine setting, not part of the format.** At most *N* agent calls are in flight for one
  job at any moment. The default is **16**.
- **Setting name: `ConsultGeneration__MaxAgentCallsPerJob`**, an integer from 1 upward; unset means
  16.
- **What counts:** only agent calls: every node of kind `agent`, including a classifier that
  decides a macro's `if`. Calls inside nested loops, inside function calls
  ([chapter 4 § 4.8](#48-concurrency-what-counts-toward-the-per-job-ceiling)) and inside check
  loops all count the same way. A repair retry (`onInvalid: retry`) and a 429 retry occupy the same
  slot as the call they repeat. `computed`, `rendered`, conditions and deliverables take no slot:
  they call no model.
- **With `maxParallel`:** each loop's `maxParallel` still limits its own items, **per loop
  instance**, so nested caps multiply. The effective limit on any one call is the smaller of the
  caps along its nesting path and the per-job ceiling. `maxParallel` is 2–15, or `null` for no cap
  of its own (`FormatBounds.parallel`, [chapter 1 § 1.8](#18-formatbounds)), in which case only the
  ceiling applies.
- **Which call waits when the ceiling is reached.** Ready calls are dispatched in a fixed order: by
  the node's position in `graph.order`, then by item path (outer items first, then list order),
  then by pass. A freed slot goes to the first waiting call in that order. This keeps dispatch
  deterministic, so Durable replay and the record agree. The order of completion still depends on
  the model.
- **Implementation:** a counter of in-flight agent calls kept in the orchestrator's state, checked
  before each dispatch. Durable fan-out today dispatches every ready activity at once
  (`ConsultGenerationEngine`'s pending-task loop); at 31 it dispatches only up to the free slots
  and waits on `Task.WhenAny` for the next free one.
- **The record** holds the ceiling in force at job start, once, in the job header's `limits`
  beside the other limits of § 8.7 ([chapter 9 § 9.1](#91-what-a-31-jobs-record-pins)); the peak
  concurrency actually reached is kept in telemetry only.
- **Applies to 31 only.** Packages at 5–30 keep today's scheduling, so the old path is unchanged
  until it retires.

### 8.6 Deployment-wide limits

There is **no shared counter** across jobs. Deployment-wide limits come from host configuration,
sized to the model deployment's quota:

- `host.json` gains `extensions.durableTask.maxConcurrentActivityFunctions` (today unset, so the
  default applies per instance);
- the Flex Consumption app's maximum instance count is set so that instances × activities stays
  within the quota.

The values are deployment configuration, recorded beside the deployment notes, not in this
document. A per-deployment Durable entity counting calls across jobs is kept for later, if
fairness across accounts needs exact control.

### 8.7 Retries and limits

A job at 31 is never kept waiting without end: a throttled job is slower, but it fails when its
limits pass.

- **A 429 from the model deployment is retried** after the response's `retry-after` (or
  `retry-after-ms`) when present; otherwise with back-off from 5 seconds, doubling, capped at
  60 seconds, with jitter. **The node fails after 10 minutes** of waiting on 429s in total.
- **Other service failures** (a 5xx response, a timeout, no connection) are retried with the same
  back-off, **5 attempts** in all; then the node fails. The record keeps the last error's kind,
  never its content. This replaces the activity's three attempts today
  (`AgentActivityRetryOptions`) for agent calls at 31.
- **A job fails if it hasn't finished 30 minutes after its orchestration started**
  (`startedAtUtc`), not after its creation or scheduling, so time spent queued or waiting behind a
  drain doesn't count. Real jobs took about 2 minutes at the median and 12 at the longest (22 jobs
  over 30 days). **Activities still running at the limit** are recorded with the row state
  `cancelled`, and their late results are ignored.
- **Total-work limits,** starting at: **200 items per loop instance**, **500 agent calls per job**
  (a retry is part of its call), and **100,000 steps per render**. Each is checked at run time and
  fails the node or the job with a sentence (§ 8.13), and is noted at publish when the package's
  worst case can exceed it (§ 8.8).
- **Delivering has its own window:** **`deliveryMinutes` (15)**, outside the 30-minute production
  limit. Production's 30 minutes ends when the last node finishes; the job then enters
  `delivering` (§ 8.11), so slow deliveries never fail the job for time.
- **All of these are engine settings,** not part of the format, recorded in the job header's
  `limits` at job start ([chapter 9](#91-what-a-31-jobs-record-pins)):

  | `limits` member | Starting value | What it limits |
  |---|---|---|
  | `maxAgentCalls` | 16 | agent calls in flight for one job (§ 8.5) |
  | `capacityWaitMinutes` | 10 | the minutes a node may wait on 429s in all |
  | `serviceAttempts` | 5 | the attempts for another service failure |
  | `jobMinutes` | 30 | the minutes a job may run, from `startedAtUtc` |
  | `deliveryMinutes` | 15 | the minutes delivery may take |
  | `deliveryAttempts` | 3 | the attempts each destination gets |
  | `loopItems` | 200 | items per loop instance |
  | `jobAgentCalls` | 500 | agent calls per job |
  | `renderSteps` | 100,000 | steps per render |

- **Every retry is recorded on the node's row** ([chapter 9](#9-the-record)): its time, the wait
  applied, whether it was for capacity or a service failure, and the error's kind. No model text is
  involved.
- **A failed node fails its job;** nothing is half-delivered. The sentences are in § 8.13.

### 8.8 The publish note

At publish, when a package's nested caps multiply past the engine's per-job ceiling, the publish
report ([chapter 7 § 7.9](#79-the-publish-report)) carries a **note**, never a refusal. The worst
case is computed from `resolve.json`: the product of `maxParallel` along each nesting path, summed
over branches that can run at the same time. **A `maxParallel: null` loop counts its list's length
when publish knows it** (a snippet folder), **and otherwise counts as unbounded,** which the note
says. Requiring a non-null `maxParallel` is
[#1474](https://github.com/Consultologist/Consultologist-Blazor/issues/1474) (Milestone 40).

*"Up to \<n\> agent calls could run at once; this engine runs at most \<ceiling\> per job, so the rest wait their turn."*

For an unbounded worst case:

*"An unbounded number of agent calls could run at once, since \<loop key\> has no maxParallel and reads a list of unknown length; this engine runs at most \<ceiling\> per job, so the rest wait their turn."*

The ceiling quoted is the publishing engine's setting. A package valid on one deployment is valid
on every deployment; only the note's numbers differ.

**The total-work limits and the job limit are noted the same way:** when a loop's list could be
longer than the items limit, when the package's worst case could make more agent calls than the job
allows, and when its estimated worst case passes the job limit. Each is a note, never a refusal
([chapter 4 § 4.10](#410-refusals)). The note for the job limit reads:

*"\<package\> could run for about \<n\> minutes in the worst case; this engine stops a job after \<limit\> minutes."*

### 8.9 Every deploy is preceded by a drain

**No job spans two builds.** The drain is defined as follows:

- **The release workflow calls `POST Admin/Drain` before deploying and `POST Admin/Resume` after.**
- **New jobs are accepted and queued.** The HTTP starter answers `202` with a job id and holds the
  job, shown as *"Waiting for an update to finish"*; it starts after resume. **Scheduled and email
  jobs wait the same way.**
- **Running jobs finish.** The deploy proceeds once no orchestration is producing or delivering,
  so a job in `delivering` (§ 8.11) is waited for too.
- **The hard cap is 60 minutes:** a job can legitimately take 45 (the 30-minute production limit,
  then the 15-minute delivery window), and the rest is margin. After it the deploy fails and stays
  undeployed; the operator investigates.

So rows don't record a build: the job header's `engineCommit` and `engineRelease` hold for every
row, and `versionsRan` takes exactly `lock.json`'s shape
([chapter 9 § 9.1](#91-what-a-31-jobs-record-pins)). Time a job spends waiting behind a drain
doesn't count towards its job limit (§ 8.7).

### 8.10 Where the record is written

The record moves out of the Durable entity:

- **Each record row is written once, to a table, when it finishes,** keyed by the job id and the
  escaped rooted key, and never rewritten. **The write is insert-if-absent:** an identical second
  write (a Durable replay) is a no-op; a differing one is refused and recorded as an engine fault.
- **The entity keeps only the job header and progress.** Events carry keys, not row contents; the
  browser fetches a finished row by its key.
- **A job that finishes producing and has deliveries to make is `delivering`** (§ 8.11); its
  delivery attempts are rows too ([chapter 9 § 9.2](#92-keys-with-their-roots)).
- **The record is sealed when delivery ends.** On every terminal state (completed, failed,
  cancelled or timed out) the engine assembles the canonical record document from the rows into a
  blob, noting the end state, and writes its hash, `recordHash`, on the header. History's download
  and the export serve that blob.

### 8.11 Delivery at the end

**Nothing is delivered until every deliverable's outcome is final and the job has succeeded**
([chapter 6 § 6.8](#68-delivery)). The job then enters **`delivering`**, shown as
*"Delivering…"*, with the document viewable throughout. Delivery runs once per destination of each
released deliverable, and each attempt is written to **a delivery row in the one record**,
`delivery:<deliverable>/<destination>` ([chapter 9 § 9.2](#92-keys-with-their-roots)). **The
record, its blob and `recordHash`, is sealed when delivery ends,** not before. A job that fails
delivers nothing and goes straight to its terminal state.

**Delivering has its own 15-minute window** (`deliveryMinutes`, § 8.7), outside the 30-minute
production limit; a destination still unsent when it closes is `failed`.

**A failed delivery is retried:** **3 times** (`deliveryAttempts`), **with back-off inside the
15-minute window** (engine settings, § 8.7), each attempt recorded on the destination's result.
After the last, the result is marked `failed`, the operator is alerted (§ 8.12), and History shows
*"Couldn't send to \<destination\>. Copy the note instead."* The job stays completed.

### 8.12 Monitoring and alerts

Minimal, on Application Insights, **lengths and hashes only, never text.** Alerts are emailed to
the operator:

- **Any failed job.**
- **429 waiting** passing 5 minutes in one job (§ 8.7).
- **A job reaching 80% of the 30-minute limit** (24 minutes).
- **A failed publish or an exporter warning.**
- **A delivery marked `failed`** (§ 8.11).

**A weekly summary** is emailed too: jobs, failures, p50 and p90 duration, the largest record, and
outstanding migration hand edits.

### 8.13 Sentences the engine shows

Sentences the engine shows, and the pages show for it. The grammar's refusals at publish are in
chapters 1 to 7. Every sentence below is used as written; [chapter 11](#11-every-sentence) lists
every sentence of this format with its audience. `<…>` marks a placeholder.

- Requires, and a package locked before a break point, at load and on the Create page, written
  with placeholders:
  *"This workflow (\<package\>@\<version\>) needs \<component\> \<range\>; this engine runs \<component\> \<engine version\>. Publish a new version of the workflow to run it on this engine."*
  Example: *"This workflow (example-nested-note@v2026.11.2) needs Scriban ^7.2; this engine runs Scriban 8.0.1. Publish a new version of the workflow to run it on this engine."*
- A `lock.json` whose hash, or whose link to `resolve.json`, doesn't match:
  *"The compiled workflow \<package\>@\<version\> doesn't match its lock, so it can't be run. Tell the operator."*
- A compiled package whose hash doesn't match the version's published hash:
  *"The compiled workflow \<package\>@\<version\> doesn't match its published hash, so it can't be run. Tell the operator."*
- 31 not admitted (production before the bump), today's sentence:
  *"specVersion 31 is not supported: this engine accepts specVersion \<list\> (pre-v5 packages are archived; see registry-operations.md)."*
- A node that waited on 429s for `capacityWaitMinutes` (10) in all fails, and its job with it
  (§ 8.7), recorded on the node's row and shown in History:
  *"The model service stayed busy for \<n\> minutes. Run the workflow again later."*
- A node whose call failed `serviceAttempts` (5) times for another reason (§ 8.7), recorded on the
  node's row with the error's kind and shown in History:
  *"The model service \<timed out | returned an error | couldn't be reached\> \<n\> times in a row. Run the workflow again later."*
- A job not finished `jobMinutes` (30) after its orchestration started (§ 8.7), shown in History:
  *"The job didn't finish within \<n\> minutes. Run the workflow again later."* Each row still
  running is recorded *"cancelled: the job didn't finish within \<n\> minutes"*.
- The total-work limits (§ 8.7), recorded and shown in History:
  *"Loop '\<id\>' was given \<n\> items; this engine runs at most \<limit\> per loop."*,
  *"The job reached \<limit\> agent calls, the most this engine runs for one job."* and
  *"\<Subject\> stopped rendering: it took more than \<limit\> steps."*
- A destination whose delivery failed after its retries (§ 8.11), shown in History; the job stays
  completed:
  *"Couldn't send to \<destination\>. Copy the note instead."*
- The publish note, never a refusal (§ 8.8):
  *"Up to \<n\> agent calls could run at once; this engine runs at most \<ceiling\> per job, so the rest wait their turn."*
- A job held behind a drain (§ 8.9): *"Waiting for an update to finish"*; a job delivering
  (§ 8.11): *"Delivering…"*.

### 8.14 What belongs to the app

The Create page, History, the Profile page, the Editor (which shows 31 packages read-only until
Milestone 41), the `WorkflowPackages/Current` contract the satellites read (which changes by
addition only, and always sends `Macros` as `[]` for a 31 package) and the diagram are the app's, not the
format's, and are specified in [part 09 of the design](https://github.com/Consultologist/Consultologist-Blazor/blob/def6f6cf/docs/customizable-workflow/package-format-v31/09-engine-and-pages.md).
They read what this document defines (`resolve.json`, the record, the profile) and show it; the
engine repeats the checks the Create page makes before submission (§ 8.2, step 6), so a job sent
another way is refused with the same sentences. One of the diagram's files is part of a package
folder: **`dag.mmd` is a view,** drawn from the same graph model as the Editor's Graph pane and the
run diagram, regenerated rather than authored, and never pinned by a record
([chapter 7 § 7.7](#77-evidence-and-views)). Its ids follow one rule: **a box's id is its key with
root, with every `.` replaced by `__`** (`node.sections.paragraphs.draft_paragraph` becomes
`node__sections__paragraphs__draft_paragraph`, `input.consult_draft` becomes
`input__consult_draft`, `deliverable.consult_note` becomes `deliverable__consult_note`;
[chapter 1 § 1.9.3](#193-keys)).

### 8.15 Sentences the pages show

The sentences below belong to the app's pages. Each is used as written.

- The Create page checks `requires` and `needs.profile` before the clinician can start a job, and
  shows each failing sentence above the Start button, which stays disabled until all pass. The
  engine's sentences of § 8.13 are shown there too, with these:
  *"This workflow needs your signature. Choose one in Profile."*; for any other profile field,
  *"This workflow needs your \<field label\>. Set it in Profile, under Letter details."*, with
  `<field label>` one of `name`, `credentials`, `organisation`, `closing line`; and, for every 31
  job until the account's time zone is set (31 only; the email intake's reply is the same):
  *"Set your time zone in your account settings before running a workflow."*
- A satellite that meets an input it can't render doesn't start a job. It shows, with a link to the
  Create page for that package: *"This workflow needs the web app"*.
- History's job header, for a migrated version, carries the publish record's line:
  *"migrated by the operator from \<old version\>"*.
- History shows one banner per deliverable that was held, failed or blocked:
  *"\<deliverable label\> was blocked: check '\<check id\>' failed (\<check detail\>)."* A gate
  check that errored gives *"\<deliverable label\> was blocked: check '\<check id\>' could not run (\<error\>)."*
- History's Run facts section shows each run spot's formatted output, for example, for a spot that
  reads `run.date` with the zone `America/Toronto`: *"16 November 2026"*.
- The Editor shows, in a bar above the panes on each 31 package:
  *"This package uses the new format. You can view and download it; editing returns in a later release."*

## 9. The record

A job at 31 writes **record storage 12**. This chapter is one page: what the job's record pins of the
package that ran, how every row is keyed, and which sentences the record holds. **The record's full
contract is `consultologist-provenance`'s:** its `provenance-record.md`, section "Storage 12", holds
every member of the job header and of every row, with its type and its null rule, the retention
rules and the hash definitions (`hash-definitions.md`). This document does not repeat it; where the
two meet, the keys, the pins and the sentences below are the format's. Names are written in the
record's JSON form (camelCase).

### 9.1 What a 31 job's record pins

- **A 31 job is stamped `schemaVersion` 12 from its creation,** on every path, as 30 jobs are
  stamped 11. **History keeps reading storage 2–11 records exactly as today:** nothing is
  converted, and jobs that ran before 31 carry no `resolveHash` or `lockHash`.
- **The job header pins the documents the job ran,** each written once, at job start, beside the
  package name and version, before any node runs ([chapter 8 § 8.2](#82-the-load-step-by-step-31)):

  | Member | Type | Null | Meaning |
  |---|---|---|---|
  | `resolveHash` | string (`sha256:…`) | null below 31 | the SHA-256 of the canonical `resolve.json` bytes the job ran |
  | `lockHash` | string (`sha256:…`) | null below 31 | the SHA-256 of the canonical `lock.json` bytes |
  | `versionsRan` | object | null below 31 | **the exact versions that actually ran,** which can differ from the lock within its range. It takes **exactly `lock.json`'s shape,** so the two compare member by member: `resolver` (`packageFormat`, `dialect`), `libraries` (`Scriban`, `Markdig`, `Corvus.Text.Json.JsonLogic`, `Corvus.JsonSchema`), `evaluator`, `operations` (those the package uses), `builtins`, `culture` (`"invariant"`) and `runtime` (`dotnet`, the .NET runtime, and `unicode`, its Unicode version), each as `lock.json` defines it ([chapter 7 § 7.4.1](#741-members)). Whether `lock.json`'s `documentVersion`, `package`, `resolve` and `catalogues` appear in it is not yet stated. The member's shape is the provenance contract's (`provenance-record.md` § 6.3, [§ 9.5](#95-the-provenance-contract)) |
  | `recordHash` | string (`sha256:…`) | allowed | the hash of the canonical record document, sealed when delivery ends ([chapter 8 § 8.10](#810-where-the-record-is-written)); `null` until then, and below 31 |
  | `limits` | object `{ maxAgentCalls, capacityWaitMinutes, serviceAttempts, jobMinutes, deliveryMinutes, deliveryAttempts, loopItems, jobAgentCalls, renderSteps }`, each an integer | null below 31 | every engine limit in force at job start, recorded once ([chapter 8 § 8.7](#87-retries-and-limits)): the per-job ceiling on agent calls in flight, the minutes a node may wait on 429s in all, the attempts allowed for another service failure, the minutes a job may run from orchestration start, the minutes delivery may take and the attempts each destination gets, and the total-work limits: items per loop instance, agent calls per job, and steps per render |
  | `runFacts` | object | null below 31 | the raw value of each run fact the package reads, once per run; `{}` when it reads none |
  | `startedAtUtc` | string | never | when the job's orchestration started; the job limit is timed from here, not from creation or scheduling, so time queued or waiting behind a drain doesn't count |
  | `signatureBlockId` | string | allowed | the profile signature block the job used, by **id**, never its text; `null` when the package doesn't read `profile.signature` |
  | `signatureChosen` | `"default"` or `"job"` | allowed | whether the block was the account's chosen block (`ChosenId`) or picked on the Create page for this job; `null` with `signatureBlockId` |
  | `decisions` | array of decision | never | every condition decision of the job; `[]` for none. Each decision is stored as its own table row and gathered here in the canonical record document ([chapter 8 § 8.10](#810-where-the-record-is-written)) |

- **Unchanged and still recorded:** `packageSpecVersion` (31), `workflowPackage`, `packageFormatRef`,
  `provenanceRef`, `formatsRef`, `catalogRef`, `engineCommit`, `engineRelease`, `apiHost`, the
  terminology snapshot. `formatsRef` and the agents catalogue version now also appear in `lockHash`'s
  document; the header keeps them for readers of older records.
- **Retired at 12** (never written by a 31 job; older records are read exactly as today):
  `macroChoices` and `excludedMacros`, since per-run macro choices are boolean inputs at 31 and their
  effect is recorded as decisions, and `classifications`, since every classifier is an ordinary
  agent node with its own row.
- **Everything storage 11 holds keeps its meaning:** paths for item keys, `loopInstances`, `while`
  rows with `passes` and `stopped`, the not-run state, item progress per loop, the 120-character item
  name. The `let` row of storage 11 is the `computed` row at 12, with `producer: computed` as before.
  At 12 **every row records the node's `producer`.**
- **A row's `producer`, `modelDerived`, `runDependent` and `profileCarrying`** are the node's own,
  as written and checked ([chapter 2 § 2.1.3](#213-producer), [chapter 3](#3-expressions)); every row
  records its `producer`.
- **The record holds hashes, ids, counts, reasons and names, never element values,** with the
  exceptions the provenance contract lists: an item name drawn from a field, run facts and run spot
  outputs, and printed conditions, which are package text.
- **Rows don't record a build:** every deploy is preceded by a drain ([chapter 8 § 8.9](#89-every-deploy-is-preceded-by-a-drain)),
  so the header's `engineCommit` and `engineRelease` hold for every row.

### 9.2 Keys, with their roots

Wherever a record names a node, it names it by its **rooted key:** the root (`node`, `check`,
`deliverable`), then the ids of its enclosing flow folders and its own, joined by `.`
([chapter 1 § 1.9.3](#193-keys)). The same keys are used in `resolve.json`, test files and
History's links.

```
node.plan                                     a top-level node
node.sections.paragraphs.draft_paragraph      a node two loops down
node.hpi_section.standard_draft               a node inside a function, through its call node
node.standards.section.standard_draft         a call node inside a loop, then the function's node
check.part_coverage.coverage                  a check inside a check loop
deliverable.emr.note                          deliverables/emr/note.md
```

- **A row key** is the rooted key, then `:` and the item path for an instance inside a loop or a
  `while`: `node.sections.paragraphs.draft_paragraph:2/1`, `node.refine.judge:3`,
  `node.standards.section.standard_draft:3`, `check.part_coverage.coverage:2`. `.` separates
  scopes, `/` separates path segments and `:` separates the key from the path; no id or item id
  contains any of the three, and item paths never contain `:`.
- **Function calls:** inner rows are keyed through the call node's rooted key, never the function's
  name. The function's name is on the call's row. Two calls to the same function get different keys
  from their call nodes.
- **A delivery row** is keyed `delivery:<deliverable>/<destination>`, one per destination of a
  released deliverable ([chapter 8 § 8.11](#811-delivery-at-the-end)).
- **Every key carries its root,** so a node, a check and a deliverable may share an id and their
  keys never collide. Checks are kept in their own section of the record and deliverables in their
  own list.
- **What is keyed this way:** each row's `nodeId` and the keys of `nodeOutputs`; block ids,
  `skippedBlocks` and `blocks`; item-step and block events, `itemProgress` and `collections`; the
  concept source, the `nodes` descriptor rows, `loopInstances` and `unresolvedLoops`; deliverable
  ids, which are paths like node ids (`deliverables/emr/note.md` is `deliverable.emr.note`, so
  moving a deliverable changes its key); and the run diagram's Mermaid ids (with `.` replaced by
  `__`, [chapter 8 § 8.14](#814-what-belongs-to-the-app)), the rail, and History and Editor links.

### 9.3 Sub-row ids

Some rows have sub-rows that live **inside** their row, not in `nodeOutputs`. Each has an id for
History's links and test expectations, formed as `<row key>/<sub kind>:<n or id>`. A sub-row id is
never parsed as a row key; a segment holding `:` is always a sub-row, since item paths never
contain `:`.

| Sub-row | Id |
|---|---|
| a renderer use | `<row key>/render:<n>`, `n` its 1-based position in the body: `node.identify_problem/render:1`, `node.sections.paragraphs.draft_paragraph:2/1/render:1` |
| a macro row | `<row key>/macro:<macro id>`: `node.assessment/macro:letrozole_prescription_text` |
| a run spot | `<row key>/spot:<n>` |
| a decision | `<owner key>/if:<site>`: `node.standards.assessment:7/if:macro.letrozole_prescription_text` |

A chain of renderers gives one sub-row per step (`…/render:1`, `…/render:2`). A decision's `site`
is one of `self`, `case`, `pass.<n>`, `until.<i>`, `macro.<id>`, `macro-folder.<folder id>`,
`part.<id>` and `snippet.<id>`, and its owner is the row key, check row key or deliverable key the
decision concerns.

### 9.4 What the record never holds

- **In-package test results.** Tests run at publish, not in jobs; their results are in the publish
  report ([chapter 7 § 7.9](#79-the-publish-report)).
- **`resolve.json` or `lock.json` themselves.** The record pins their hashes; History fetches the
  documents from the registry by version and checks them against the hashes.
- **Element values,** apart from the exceptions in § 9.1.
- **The peak concurrency a job reached,** which goes to telemetry only ([chapter 8 § 8.5](#85-the-per-job-ceiling)).

### 9.5 The provenance contract

The record's contract is published by `consultologist-provenance`, in `provenance-record.md`,
storage 12, with the hash definitions (`hash-definitions.md`) and the registry layout
(`registry-layout.md`) it adds. The engine stamps the provenance contract's version as
`provenanceRef` on every 31 job, and a provenance version lists storage 12 among its
`recordStorageVersions`.

### 9.6 Sentences the record holds

The record refuses nothing itself; the refusals at start and load are in
[chapter 7 § 7.10](#710-refusals) and [chapter 8 § 8.13](#813-sentences-the-engine-shows). Every
sentence below is used as written; [chapter 11](#11-every-sentence) lists every sentence of this
format with its audience. `<…>` marks a placeholder. A row that didn't complete reads its
sentence in `stateReason`, and a deliverable's row does the same; the sentences the record holds:

- *skipped: …* is the form of a skip, built from the printed condition:
  *"skipped: \<printed condition\> is false"* (a decision's reason; a row skipped by a decision has
  this sentence as its `stateReason`, and the decision's id links the two). On a deliverable's row
  the same form reads *"skipped: \<condition\> is false"* (its header `if`).
- *"not run: beyond max \<n\>"* (an item past a loop's `max`; the loop's `.stopped` is `"bound"`).
- *"case '\<id\>': arm for \<value\> does nothing"* (a `case` whose subject took an explicitly empty
  branch, [chapter 4 § 4.5](#45-branches-if-and-case)).
- *"held: empty"* (a deliverable with `whenEmpty: hold`).
- *"released: check '\<id\>' didn't apply (its if was false)"* (a deliverable whose gating check was
  skipped).
- *"not sent: \<kind\> isn't set up for this account"* (an unconfigured delivery kind), for example
  *not sent: EMR isn't set up for this account*.
- *"not sent: the job failed"* (each destination of a released deliverable in a job that failed;
  nothing is delivered until the job has succeeded).
- *"failed: \<kind\>"* (a destination whose delivery was retried and still didn't go, with each
  attempt on the result; the job stays completed).
- *"blocked: check '\<id\>' failed (\<detail\>)"* and *"blocked: check '\<id\>' could not run (\<error\>)"*
  (a deliverable whose gate check failed or errored).
- *"cancelled: the job didn't finish within \<n\> minutes"* (a row still running at the job limit;
  the row state is `cancelled`).
- History's banner, built from the record:
  *"\<deliverable label\> was blocked: check '\<check id\>' failed (\<detail\>)."*, for example
  *Consultation note was blocked: check 'coverage' failed (10 of 12 terms present).*
- History, for a sent format with keywords removed: *"Not sent to the model: \<pointers\>"*.
- A node's `invalid.reason` for the macro check: *"macro \<id\>: missing"*, *"macro \<id\>: repeated"*,
  *"macro \<id\>: altered"*; and the failure when `onInvalid` is `fail`:
  *"Node '\<row key\>' failed: macro '\<id\>' was \<missing | repeated | altered\> in the reply."*
- A deliverable failed by `whenEmpty: fail`:
  *"Deliverable '\<id\>' was empty, and the workflow fails an empty \<label\>."*
- A node failed by the model service's limits ([chapter 8 § 8.7](#87-retries-and-limits)):
  *"The model service stayed busy for \<n\> minutes."*, or
  *"The model service \<timed out | returned an error | couldn't be reached\> \<n\> times in a row."*;
  and a job past its time limit: *"The job didn't finish within \<n\> minutes."* History adds
  *"Run the workflow again later."* ([chapter 8 § 8.13](#813-sentences-the-engine-shows)).

## 10. Migration (30 → 31)

This chapter is where "At 30 … At 31" lives: what turns a package at 30 into a package at 31, and
what the migration reports. The migration is **one library rewrite from 30, chained from older
versions:** a package older than 30 is first raised through the existing chain in the same run. It
reads specVersion 30, never writes an unknown member ([chapter 1](#1-files-and-scopes)), and
produces the migrated package as a folder ([chapter 1 § 1.2](#12-the-folder-layout)), a list of
notices, a migration report (§ 10.11) and a snapshot test (§ 10.12). Byte-equivalence with 30 is
reported, never a gate. The operator's procedure and the project's schedule are not part of the
format and are not in this document.

### 10.1 What the rewrite does mechanically

Every rewrite the format defines is listed here, with the chapter that defines the 31 form.

| At 30 | At 31 | Chapter |
|---|---|---|
| one `manifest.json` with every node, prompts as files | files and folders. **All nine top-level folders are written, each with its `index.json`, even when empty** (`"items": []`): `nodes/`, `checks/`, `functions/`, `renderers/`, `snippets/`, `macros/`, `formats/`, `deliverables/`, `tests/`; each function folder gets its `snippets/`, `macros/`, `formats/` and `renderers/`. Flow folders get their `index.json` | [1](#1-files-and-scopes) |
| the manifest's `nodes`, `macros` and `snippets` lists | moved into `nodes/index.json`, `macros/index.json` and `snippets/index.json`, members by bare id; the manifest keeps identity and inputs | [1](#1-files-and-scopes) |
| `templating` in the manifest | dropped; `lock.json` and `requires` record the Scriban version | [1](#1-files-and-scopes) |
| optional members omitted | every member written, `null` for none | [1](#1-files-and-scopes) |
| `\r\n` line endings | normalised to `\n`, as import and publish do | [1](#1-files-and-scopes) |
| node headers | **`reproducible` written on every node**, from the derived value (`rendered` and `computed` `true`, `agent` `false`, a flow node from its body, a `call` from its function), and the migration report lists each node whose 30 claim differed; **`producer` written on every node and check**, from its kind (`"generated"` for `agent`, `"computed"` for every other); **`modelDerived`, `runDependent` and `profileCarrying` written on every node and check**, from the values the resolver derives; `format` written on flow nodes, from `ret` | [1](#1-files-and-scopes), [2](#2-types-and-inputs) |
| an id now reserved (`parts`, `items`, `value`, …) | renamed, with every reference rewritten (§ 10.6) | [1](#1-files-and-scopes) |
| `format` with `producer` | `kind` and `format` on every node | [2](#2-types-and-inputs) |
| `prose` and `agent_*` formats; `x-generated` | **the plain format of the same shape:** `prose` and `agent_plaintext` → `plaintext`, `agent_markdown_block` → `markdown_block`, `agent_markdown_inline` → `markdown_inline`; object formats keep their names. `x-generated` is dropped: the node's `producer` says who wrote the value | [2](#2-types-and-inputs), [7](#7-the-compiled-documents) |
| a format file | **`$schema` written** as `urn:consultologist:spec:31:dialect` | [2](#2-types-and-inputs) |
| an object format (catalogue or package) whose `required` lists only some properties | every property listed in `required`, the optional ones made nullable (§ 10.5) | [2](#2-types-and-inputs) |
| inputs as an array with `type`, `values`, `fields`, `items`, `expectedContent` | an object keyed by id: `text` → `markdown_block`; `enum` + `values` → **a plain `enum`, with no invented titles**; `date` → `"date"`; `fields` → `properties` + `required` listing every field, optional ones made nullable; `expectedContent` → `channel`; `description: null` added | [2](#2-types-and-inputs) |
| 30's "one or many" union inputs | **their array form**, since inputs refuse a top-level `anyOf` | [2](#2-types-and-inputs) |
| a long free-text `string` field | unchanged; a notice **suggests** a text format, never applied automatically | [2](#2-types-and-inputs) |
| bare `input.x` reads, in conditions, expressions and templates | **`input.x.value`**, or **`input.x.content`** for a text-format input, since a bare `input.<id>` is refused | [2](#2-types-and-inputs) |
| `labelField` on an input | `itemLabel` on **each loop** that iterates the input (several loops get the same value) | [4](#4-loops-and-functions) |
| a node's `when` gate | `if`; a `case` branch keeps `when` | [3](#3-expressions) |
| a `case` with no `else` whose branches miss some values (which 30 skipped) | **an explicitly empty branch for the missing values**, `{ "when": [<values>], "nodes": [], "ret": null }`, so every `case` is exhaustive and those values still read as skipped, with the reason *"case '\<id\>': arm for \<value\> does nothing"*. The `case` keeps its shape and keys: `example-conditional-sections`' `route` gains `{ "when": ["omit"], "nodes": [], "ret": null }` | [4](#4-loops-and-functions) |
| string conditions (Scriban) | JSON Logic, by the converter (§ 10.9); `==`/`!=` written `===`/`!==`; `!x` on text → `blank(x)`, each listed in the migration report (§ 10.10) | [3](#3-expressions) |
| `let` (a Scriban expression) | `kind: computed` with JSON Logic in `expression`, by the converter | [3](#3-expressions) |
| a `terms_subset` check node | a file in `checks/`, `kind: computed`, `format: check_result`, `failWith` a literal; every reader of `node.x` rewritten to `check.x` | [6](#6-checks-deliverables-and-the-profile) |
| deliverables with `sources`, composed by the engine | a file in `deliverables/` whose generated template **reproduces today's composer bytes**, with `whenEmpty` chosen as § 10.7 says | [6](#6-checks-deliverables-and-the-profile) |
| the deliverable header's signature | `{{ profile.signature }}` in the template | [6](#6-checks-deliverables-and-the-profile) |
| built-in renderers in C# (`concept_bullets`, `concept_context`) | **built-in Scriban renderers in the registry**, versioned and locked, their ids reserved; piped as `\| renderer.concept_bullets` | [5](#5-templates-and-macros) |
| whitespace forms version 31 refuses, `-` on a tag | rewritten to the accepted forms | [5](#5-templates-and-macros) |
| simple `{{ if }}…{{ end }}` blocks in prompts | lifted into parts | [5](#5-templates-and-macros) |
| `failIfEmpty` on agent nodes | the failure sentence, or null (chapter 5 § 1.2); 30's true, false or absent is what the migration converts from | [5](#5-templates-and-macros) |
| optional macros: per-run choices with a `default` | **boolean inputs** (§ 10.3) | [2](#2-types-and-inputs), [5](#5-templates-and-macros) |
| no tests | one snapshot test (§ 10.12) | [7](#7-the-compiled-documents) |

### 10.2 Pipes, body tests and the `test` macro

Three rewrites in templates are stated here because the chapters that define the 31 form point to
this one.

- **A version 30 pipe becomes a pipe into a renderer.** 30's `node.x | concept_bullets` (the node)
  and `node.x.content | …` become **`node.x.value | renderer.concept_bullets`**: the piped value is
  the node's typed `.value`, and the renderer is a built-in Scriban renderer of the registry
  ([chapter 5 § 5.5](#55-renderers)).
- **A body `if` becomes a part.** A simple `{{ if }}…{{ end }}` block in a prompt is lifted into a
  part ([chapter 5 § 5.7](#57-parts)); a body `if` too complex to lift is a hand edit (§ 10.4).
  30's `test/general` tests `(item.content | string.strip) == ""` in a body `if`, which 31 refuses:
  the test moves to the part's `if`, written with the `blank` operation
  ([chapter 3](#3-expressions)), and is recorded as a decision.
- **The `test` macro becomes a snippet.** 30's `test` macro (`at: append`, "the last line of the
  note") becomes `snippets/test.md`, which the deliverable's template reads verbatim at the end of
  the note, `{{ snippet.test.content }}`; the template itself is first written to reproduce 30's
  bytes ([chapter 6 § 6.6.5](#665-headings-are-the-authors)).

### 10.3 Per-run macro choices become boolean inputs

Inputs have no `default` member, so each optional macro at 30 becomes an optional boolean input, and
the macro's offer condition reads it so that a run that doesn't answer gets 30's default:

| 30's `default` | The macro's `if` at 31 | Unanswered (`null`) means |
|---|---|---|
| `false` | `{ "===": [ { "var": "input.<id>.value" }, true ] }` | not offered |
| `true` | `{ "!==": [ { "var": "input.<id>.value" }, false ] }` | offered |

When 30's macro already had an `if`, the two are joined with `and`. **The input takes the macro's
id and label.** An id that's already an input's id gets the suffix `_macro` (`letrozole` →
`letrozole_macro`), and the rename is in the migration report. An optional boolean input is shown
in three states (unset, yes, no), and unset is sent as `null`
([chapter 2 § 2.10](#210-per-run-macro-choices-become-optional-boolean-inputs)). The new input is
written:

```jsonc
"include_billing_note": {               // the macro's id
  "label": "Include the billing note",  // the macro's label
  "description": null,
  "format": "boolean",
  "required": false,
  "channel": null
}
```

Re-evaluating a `default` member is
[#1456](https://github.com/Consultologist/Consultologist-Blazor/issues/1456) (Milestone 40).

### 10.4 Hand edits, with notices

When the rewrite can't decide, it still writes the package, with **one notice per edit**, and
validation fails with sentences until each is made. The cases:
- a body `if` too complex to lift into a part;
- macros placed on deliverables with conditions or model judgement;
- a condition or `let` the converter can't map (§ 10.10);
- **a 30 prompt that reads `profile.*`:** at 31 a prompt never reads the profile
  ([chapter 5](#5-templates-and-macros)), so the read is a hand edit, and the owner is told about
  it in the after-notice (§ 10.8), with what replaced it.

Notices that need no edit (a renamed id, a `!x` converted to `blank(x)`, a suggested text format)
are listed in the migration report and block nothing.

The script exits **0** when the package migrated cleanly, **1** with *"written; hand edits remain"*,
and **2** when it refused, writing no package (unreadable input, or a version below 5).

Each notice reads:

*"Hand edit needed in \<file\>, \<member\>: \<reason\>."*

The reason for a prompt that reads the profile is:

*"the prompt reads profile.\<field\>, which a 31 prompt doesn't read; move it to a deliverable or a macro body."*

### 10.5 Every property required

At 31 every property of every format is listed in `required`, and an optional one is nullable
([chapter 2 § 2.3](#23-the-dialect)). The migration rewrites today's formats to match:
- **package formats and inputs' object fields** in each migrated package;
- **the catalogue's formats,** released as new versions with the contracts.

Agents then return explicit `null`s for optional fields where they used to leave the key out.
**The record and History treat an explicit `null` as absent,** and the byte-equivalence report
(§ 10.11) notes the difference rather than failing on it.

### 10.6 Reserved ids are renamed

An id that 31 reserves (`input(s)`, `node(s)`, `check(s)`, `function(s)`, `test(s)`, `snippet(s)`,
`macro(s)`, `part(s)`, `renderer(s)`, `format(s)`, `deliverable(s)`, `param(s)`, `item(s)`,
`pass(es)`, `run(s)`, `profile(s)`, `value(s)`, `content(s)`) is renamed by the migration
([chapter 1 § 1.6](#16-ids)). **Object field names are never renamed:** they have no reserved list,
since a field is always read after `.value`, so 30's `title` fields keep their name:

- **In example packages each rename is hand-chosen:** `example-nested-note`'s loop `parts` becomes
  **`sections`**, so `nodes/parts/…` becomes `nodes/sections/…` and `node.parts.…` becomes
  `node.sections.…` everywhere, `ret` values included.
- **In account packages the kind is added as a suffix:** a `for` loop `parts` becomes `parts_for`.
- **A rename that collides** with an existing id gets a numeric suffix (`_2`, `_3`, …), the id
  shortened first so the whole stays within 64 characters, and is listed in the report:
  *"Renamed '\<id\>' to '\<new id\>'; '\<id\>\_\<kind\>' was already taken."*
- **Every rename is reported,** and every reference to it is rewritten: reads, `ret`, `in`,
  conditions, templates, test keys.

### 10.7 `whenEmpty` for migrated deliverables

- **Account packages:** `"release"`, which keeps 30's behaviour (30 produces an empty deliverable
  as is).
- **Example packages, hand-chosen:** `"hold"` for `test/general`, `"fail"` for
  `example-nested-note`, and `"release"` for the rest.

### 10.8 A package that stays at 30, and what its owner is told

- **A package that can't be migrated faithfully may stay at 30:** its pin is unchanged, and its
  owner is told why, until the Milestone 41 Editor lets them migrate it themselves. It keeps 30's
  load path until the old spec versions retire
  ([#1450](https://github.com/Consultologist/Consultologist-Blazor/issues/1450)); old versions
  stay readable and old records keep their meaning ([chapter 8 § 8.1](#81-two-load-paths-chosen-by-specversion)).
  The owner's notice reads:

  *"\<package\> stays at version 30 for now: \<reason\>. Its pin is unchanged; you can migrate it in the Editor when Milestone 41 arrives."*

- **A migrated version is recorded as a migration:** its publish record says
  *"migrated by the operator from \<old version\>"*, with the byte-equivalence report and the list
  of hand edits attached.
- **Owners are told** before the migration that their packages will be migrated and that editing
  returns with Milestone 41, and after it what changed, with the report and the hand edits. **The
  notice also says that 31 jobs are refused until the account's time zone is set, and when a
  profile field the package reads is missing** ([chapter 6 §§ 6.10.4 and 6.10.7](#6104-a-missing-field-refuses-the-job));
  those refusals apply to 31 jobs only.

### 10.9 The converter

The conversion logic is a library, not part of the format: the format and the checker only ever
see JSON Logic. It takes 30's conditions, which are Scriban boolean expressions, and 30's `let`s,
which are single Scriban expressions over pure builtins, and maps the subset that has a counterpart
in 31's operation set ([chapter 3 § 3.5](#35-the-operations)), **using the table below as written;**
the operations themselves, their signatures and their null rules are chapter 3's. The reverse
direction, JSON Logic to text, is the printer ([chapter 3 § 3.8](#38-the-printer)), which the
converter reuses; there is one printer.

| At 30 (Scriban) | At 31 (JSON Logic) |
|---|---|
| a read: `node.x.value.y`, `node.x.content`, `item.id`, `item.value.y`, `pass.number`, `run.x` | `{ "var": "<the same path, with its root>" }` |
| a read of an input: `input.x`, `input.x.y` | `{ "var": "input.x.value" }` (or `input.x.content` for a text-format input), `{ "var": "input.x.value.y" }` |
| `a == b`, `a != b` | `{ "===": [a, b] }`, `{ "!==": [a, b] }` |
| `a < b`, `a <= b`, `a > b`, `a >= b` | the same operators, two operands |
| `a && b`, `a \|\| b` | `and`, `or` (flattened: `a && b && c` is one `and`) |
| `!a`, with `a` boolean | `{ "!": [a] }` |
| `!a`, with `a` text | `{ "blank": [a] }` (§ 10.10) |
| `+ - * / %` on numbers | the same operators |
| `(x \| array.size)`, `x.size` on a list | `{ "size": [x] }` |
| `string.downcase x`, `string.strip x` | `{ "lower": [x] }`, `{ "trim": [x] }` |
| `string.starts_with x "p"`, `string.ends_with x "p"` | `starts_with`, `ends_with` |
| `string.contains x "p"` | `{ "in": ["p", x] }` |
| `date.parse "YYYY-MM-DD"` | the literal string, typed `date` by its comparison |
| a number, `true`, `false`, a quoted string | the JSON literal |
| `{ a: x, b: y }` (a `let`'s object) | the `object` operation ([chapter 3](#3-expressions)) |
| `[x, y]` | a JSON array |

- **Equality is always written strict** (`===`/`!==`); `==`/`!=` are never written.
- **A 30 classifier gate keeps its format:** today's catalogue `classification`
  (`{ value: string }`) is unchanged, so a macro gated on a classifier's *yes* reads
  `{ "===": [ { "var": "node.<id>.value.value" }, "yes" ] }`. The built-in `judgement`
  ([chapter 2 § 2.4](#24-built-in-and-catalogue-formats)) is for classifiers written at 31; the
  migration doesn't rewrite a `classification` into it.
- **The output is canonical:** the same input always gives the same bytes (RFC 8785 ordering for
  any object), so migrated packages diff cleanly and the round-trip fixtures are stable.

### 10.10 What the converter refuses, and `!x` on text

Anything outside the table gives no logic and one notice per reason, which the migration turns into
a hand edit (§ 10.4), with a notice. In particular:
- a builtin or pipe with no 31 operation;
- a comparison the 31 checker refuses by type (for example `<` on text), using **the checker's own
  sentence** ([chapter 3](#3-expressions));
- a read of `profile.*` in a condition, which 31 refuses;
- an assignment, a template, or more than one statement.

For anything but a refusal on type, the notice reads:

*"The condition '\<expression\>' uses \<construct\>, which has no JSON Logic form at 31: rewrite it by hand."*

**`!x` on text converts to `blank(x)`.** It differs from 30 only for whitespace-only text (30's
truthiness treats it as present; `blank` counts it as blank), so **the migration report lists every
such conversion.** For every condition in the public packages and the fixture set, 30's evaluator on
the Scriban string and 31's evaluator on the converted JSON Logic agree on generated fictional
inputs, including `null` and absent values, except this whitespace case, which is listed as an
expected difference in the byte-equivalence report, never silently accepted.

### 10.11 The migration report

- **Reported, never a gate.** Each difference between the 30 package's prompts and deliverables and
  the migrated package's, rendered on fixed fictional inputs with model outputs stubbed, is listed
  with its file, its site and both texts' hashes, and marked **expected** where the rewrite
  declares and explains it (for example a whitespace form version 31 refuses, or a `!x` converted
  to `blank(x)`). An optional field that 30 left out and 31 sends as `null` (§ 10.5) is noted,
  never counted as a failure. The report **never blocks publish,** for public or account
  packages.
- **What it also lists:** every renamed id (§ 10.6), every `_macro` suffix (§ 10.3), every `!x`
  converted to `blank(x)` (§ 10.10), and every suggestion made.
- **It notes a package whose estimated worst case passes the job limit** (30 minutes, or a
  total-work limit, [chapter 8 § 8.7](#87-retries-and-limits)), with the estimate, in the
  sentence of [chapter 8 § 8.8](#88-the-publish-note):
  *"\<package\> could run for about \<n\> minutes in the worst case; this engine stops a job after \<limit\> minutes."*
- **Its shape:** one JSON document, `migration-report.json`, beside the publish report in the
  version's folder ([`migration-report.schema.json`](v31/schemas/migration-report.schema.json)).
  Like the other derived files, it never lives in source.

  | Member | Type | Meaning |
  |---|---|---|
  | `oldVersion` | string | the version migrated from |
  | `newVersion` | string | the version migrated to |
  | `handEdits` | array of string | the hand edits made; `[]` for none |
  | `texts` | array of entry | one entry per compared text; `[]` for none |

  **An entry of `texts`** is `{ "site", "oldHash", "newHash", "equal", "expected", "explanation" }`:

  | Member | Type | Null | Meaning |
  |---|---|---|---|
  | `site` | string | never | the compared text's site: the file and the place in it |
  | `oldHash` | string (`sha256:…`) | never | the hash of the text at 30 |
  | `newHash` | string (`sha256:…`) | never | the hash of the text at 31 |
  | `equal` | boolean | never | whether the two texts are equal |
  | `expected` | boolean | never | whether the rewrite declares and explains the difference |
  | `explanation` | string | allowed | why the difference is expected; `null` unless `expected` is true |

### 10.12 The snapshot test

**The migration writes one test per package** from its migrated run, so every migrated package
starts with one test pinning its behaviour. It follows the grammar of in-package tests
([chapter 7 § 7.8](#78-in-package-tests-tests)): fictional `inputs`, every input listed; fixed
`profile` and `run` values for exactly what the package reads; `outputs` stubbed per agent node,
item and pass, keyed by key with root; and `expect` holding the resulting prompts and deliverables
**by hash,** since exact text would put a whole note into the package and a hash pins the same
bytes. The stubs are generated from each node's format, deterministically, seeded by the node's
key, item path and pass, so the same package and inputs always give the same stubs.

- **Its id is `migration_snapshot`, at `tests/migration_snapshot.json`.**
- Like every test, it runs offline in CI, and at publish, where a failure blocks publish. Its
  result goes in the publish report, never in a job's record.

## 11. Every sentence

Every refusal, warning, job-start, recorded and History sentence of this format, in one table. The
table is printed by [`scripts/render-sentences.py`](scripts/render-sentences.py) from
[`v31/sentences.json`](v31/sentences.json), which is normative beside this text; each sentence is
also given, as written, in the chapter and under the heading named in its row. The sentence cell is
the sentence between quotation marks and in italics, with `<`, `>`, `|` and `*` written as escapes (a
quotation mark is not escaped); `<…>` marks a placeholder. The chapter cell is the number of the
chapter that gives the sentence and the title of the heading of that chapter under which it is
given. The audience is `author` (a person writing or publishing a package) or `clinician` (a person
running a workflow).

| Id | Chapter | Sentence | Audience |
|---|---|---|---|
| S01-001 | 1 · Members: every one written | *"Did you mean 'label'?"* | author |
| S01-002 | 1 · Refusals | *"Node '\<id\>' in \<path\> reuses the id of node '\<id\>' \<at the top level \| in \<other path\>\>, which \<path\> can read: rename one. Ids may repeat only where neither can see the other (for example in two sibling loops)."* | author |
| S01-003 | 1 · Refusals | *"While '\<id\>' declares max \<n\>; a while runs at most FormatBounds.passes (15) passes."* | author |
| S01-004 | 1 · Refusals | *"Call '\<id\>' reaches depth \<n\>; calls nest at most FormatBounds.depth (15) deep."* | author |
| S01-005 | 1 · Refusals | *"Loop '\<id\>' declares maxParallel \<n\>; the most is FormatBounds.parallel (15)."* | author |
| S01-006 | 1 · Refusals | *"File '\<path\>' is not listed: every file in \<folder\> is named once in its index.json, or is index.json or README.md."* | author |
| S01-007 | 1 · Refusals | *"\<folder\> has no index.json; every folder lists its members, even when it has none ("items": [])."* | author |
| S01-008 | 1 · Refusals | *"The package has no \<folder\>/ folder; all nine top-level folders are always present."* | author |
| S01-009 | 1 · Refusals | *"\<list\> lists '\<id\>', but \<folder\> has no \<id\>.md or \<id\>/."* | author |
| S01-010 | 1 · Refusals | *"\<list\> lists '\<id\>' twice."* | author |
| S01-011 | 1 · Refusals | *"\<list\> lists '\<id\>/'; list a folder by its bare id."* | author |
| S01-012 | 1 · Refusals | *"\<folder\> holds both \<id\>.md and \<id\>/: an id names one file or one folder."* | author |
| S01-013 | 1 · Refusals | *"Delivery folder '\<path\>' is inside another delivery folder; delivery folders are one level deep."* | author |
| S01-014 | 1 · Refusals | *"File '\<path\>' starts with a byte-order mark; save it as UTF-8 without one."* | author |
| S01-015 | 1 · Refusals | *"File '\<path\>' contains a carriage return on line \<n\> that doesn't end the line; lines end with \n."* | author |
| S01-016 | 1 · Refusals | *"File '\<path\>' must start with a line of exactly ---, then one JSON object, then a line of exactly ---."* | author |
| S01-017 | 1 · Refusals | *"The header of '\<path\>' is not valid JSON: \<parser message\>."* | author |
| S01-018 | 1 · Refusals | *"The header of '\<path\>' declares '\<member\>' twice."* | author |
| S01-019 | 1 · Refusals | *"\<Kind\> '\<id\>' has an empty body; its \<prompt \| template \| text\> is the body."* | author |
| S01-020 | 1 · Refusals | *"\<Kind\> '\<id\>' has a body; a \<computed node \| call \| check\> keeps everything in its header."* | author |
| S01-021 | 1 · Refusals | *"\<Declaration\> is missing '\<member\>'; every member is written, and null means none."* | author |
| S01-022 | 1 · Refusals | *"\<Declaration\> sets '\<member\>' to null, which it can never be."* | author |
| S01-023 | 1 · Refusals | *"\<Declaration\> in '\<path\>' declares unknown member '\<member\>'. Did you mean '\<closest\>'?"* | author |
| S01-024 | 1 · Refusals | *"\<Declaration\> has an empty description; write null for none."* | author |
| S01-025 | 1 · Refusals | *"\<Declaration\>'s description is \<n\> characters; the most is 500."* | author |
| S01-026 | 1 · Refusals | *"\<Declaration\> has an empty label."* | author |
| S01-027 | 1 · Refusals | *"\<Node\> '\<key\>' declares reproducible \<value\>, but its \<kind \| body \| function\> makes it \<derived\>."* | author |
| S01-028 | 1 · Refusals | *"\<Node\> '\<key\>' is kind \<kind\> and declares producer '\<value\>'; a \<kind\> node's producer is \<generated \| computed\>."* | author |
| S01-029 | 1 · Refusals | *"\<Node\> '\<key\>' declares \<modelDerived \| runDependent \| profileCarrying\> \<value\>, but its reads make it \<derived\>: \<the read that does, or none\>."* | author |
| S01-030 | 1 · Refusals | *"'\<id\>' is not a valid id: a lowercase letter, then lowercase letters, digits or underscores."* | author |
| S01-031 | 1 · Refusals | *"Id '\<id\>' is \<n\> characters; the most is SourceBounds.idLength (64)."* | author |
| S01-032 | 1 · Refusals | *"Id '\<id\>' is reserved on Windows (con, prn, aux, nul, com1–com9, lpt1–lpt9) and can't name a file: rename it."* | author |
| S01-033 | 1 · Refusals | *"Id '\<id\>' is reserved: \<root \| member\> '\<word\>' is read in references, so nothing may be called '\<id\>'."* | author |
| S01-034 | 1 · Refusals | *"Format '\<id\>' reuses the name of a \<built-in \| catalogue\> format: rename it."* | author |
| S01-035 | 1 · Refusals | *"Renderer '\<id\>' reuses the name of a built-in renderer: rename it."* | author |
| S01-036 | 1 · Refusals | *"Node '\<id\>' appears twice inside while '\<while\>' (\<path\> and \<path\>): pass.….node.\<id\> must name one node."* | author |
| S01-037 | 1 · Refusals | *"The package has \<n\> files; the most is SourceBounds.files (512)."* | author |
| S01-038 | 1 · Refusals | *"File '\<path\>' is \<n\> KiB; the most is SourceBounds.fileBytes (256 KiB)."* | author |
| S01-039 | 1 · Refusals | *"The package is \<n\> MiB; the most is SourceBounds.totalBytes (2 MiB)."* | author |
| S01-040 | 1 · Refusals | *"Path '\<path\>' is \<n\> characters; the most is SourceBounds.pathLength (200), counted from the package root."* | author |
| S01-041 | 1 · Refusals | *"File '\<path\>' nests JSON more than 32 levels deep at \<JSON pointer\>; the most is SourceBounds.jsonDepth (32)."* | author |
| S01-042 | 1 · Refusals | *"\<Site\> in '\<path\>' has \<n\> expression nodes; the most is SourceBounds.expressionNodes (1,000)."* | author |
| S02-001 | 2 · The contagious flags: run-dependent and model-derived | *"computed from model text: node.draft"* | author |
| S02-002 | 2 · Reading a value | *"Medical oncology"* | author |
| S02-003 | 2 · What a model receives | *"Not sent to the model: …"* | author |
| S02-004 | 2 · An example: `example-conditional-sections`' inputs at 31 | *"Narrative"* | author |
| S02-005 | 2 · Refusals | *"This workflow needs the web app"* | clinician |
| S02-006 | 2 · Refusals | *"computed from model text: \<key\>"* | author |
| S02-007 | 2 · Refusals | *"Node '\<id\>' declares unknown kind '\<kind\>' (accepted: agent, rendered, computed, for, while, if, case, call)."* | author |
| S02-008 | 2 · Refusals | *"Node '\<id\>' declares kind let; a let is now kind computed, with its JSON Logic in expression."* | author |
| S02-009 | 2 · Refusals | *"Node '\<id\>' is kind \<kind\> and declares producer '\<value\>'; a \<kind\> node's producer is \<generated \| computed\>."* | author |
| S02-010 | 2 · Refusals | *"Node '\<id\>' declares producer '\<value\>', which is reserved for a later version (accepted at 31: generated, computed)."* | author |
| S02-011 | 2 · Refusals | *"Node '\<id\>' declares \<modelDerived \| runDependent \| profileCarrying\> \<value\>, but its reads make it \<derived\>: \<the read that does, or none\>."* | author |
| S02-012 | 2 · Refusals | *"Node '\<id\>' is kind agent and returns \<format\>, which has no binding for producer \<producer\> in agents/bindings.json."* | author |
| S02-013 | 2 · Refusals | *"Node '\<id\>' is kind rendered and returns \<format\>; a rendered node returns plaintext, markdown_block or markdown_inline."* | author |
| S02-014 | 2 · Refusals | *"Node '\<id\>' is kind agent and declares an inline format; an agent's format is named, in formats/."* | author |
| S02-015 | 2 · Refusals | *"\<Flow\> '\<id\>' declares format \<declared\>, but its ret gives \<derived\>."* | author |
| S02-016 | 2 · Refusals | *"Branch \<n\> of \<if \| case\> '\<id\>' returns \<format\>, which is not in the declared union \<union\>."* | author |
| S02-017 | 2 · Refusals | *"Format '\<name\>' is not a built-in, catalogue or package format."* | author |
| S02-018 | 2 · Refusals | *"'input.\<id\>' is read bare; read input.\<id\>.value, or input.\<id\>.content for text."* | author |
| S02-019 | 2 · Refusals | *"'\<path\>.title' reads the title of a plain enum, which has none; use a labelled oneOf, or read .value."* | author |
| S02-020 | 2 · Refusals | *"\<Condition\> compares \<path\>.title with '\<literal\>', which is not one of its titles (\<titles\>)."* | author |
| S02-021 | 2 · Refusals | *"\<Format \| Input '\<id\>'\> uses keyword '\<keyword\>' at \<path\>, which is outside the formats dialect."* | author |
| S02-022 | 2 · Refusals | *"Format '\<name\>' declares no $schema; every format file names the dialect (urn:consultologist:spec:31:dialect)."* | author |
| S02-023 | 2 · Refusals | *"Format '\<name\>' declares $schema '\<value\>', but the package is specVersion \<n\>, whose dialect is \<id\>."* | author |
| S02-024 | 2 · Refusals | *"\<Format\> at \<path\> declares additionalProperties \<value\>; every object declares additionalProperties: false."* | author |
| S02-025 | 2 · Refusals | *"\<Format\> at \<path\> lists '\<property\>' in required but declares no such property."* | author |
| S02-026 | 2 · Refusals | *"\<Format\> at \<path\> leaves '\<property\>' out of required; every property is listed in required, and an optional one is written as nullable."* | author |
| S02-027 | 2 · Refusals | *"Node '\<id\>' returns \<format\>, an anyOf at its root, which strict mode can't send to a model; wrap it in an object."* | author |
| S02-028 | 2 · Refusals | *"\<Format\> at \<path\> writes a nullable \<type\> with anyOf; write it as "type": ["\<type\>", "null"]."* | author |
| S02-029 | 2 · Refusals | *"\<Format\> at \<path\> declares type \<list\>; a type array is one type plus "null"."* | author |
| S02-030 | 2 · Refusals | *"\<Format\> at \<path\> uses format '\<value\>'; the only format is date, on a string."* | author |
| S02-031 | 2 · Refusals | *"\<Format\> at \<path\> has '\<keyword\>' beside $ref; only title and description may sit beside a $ref."* | author |
| S02-032 | 2 · Refusals | *"\<Format\> at \<path\> refers to itself; recursive formats aren't supported."* | author |
| S02-033 | 2 · Refusals | *"Package format '\<id\>' declares $id; a package format's $id is written at publish."* | author |
| S02-034 | 2 · Refusals | *"Package format '\<id\>' is a \<string \| number \| boolean\>; a package defines object and array formats, and refers to built-in and catalogue formats by name."* | author |
| S02-035 | 2 · Refusals | *"Format '\<name\>' is a text format and declares no contentMediaType."* | author |
| S02-036 | 2 · Refusals | *"Format '\<name\>' is Markdown and declares no x-markdown (block or inline)."* | author |
| S02-037 | 2 · Refusals | *"\<Format\> declares \<contentMediaType \| x-markdown\> at \<path\>, where it doesn't apply."* | author |
| S02-038 | 2 · Refusals | *"\<Input '\<id\>' \| Node '\<id\>'\>'s inline format declares \<contentMediaType \| x-markdown\>; text inside an inline format is a $ref to a text format."* | author |
| S02-039 | 2 · Refusals | *"formats/index.json lists '\<id\>', but formats/ has no \<id\>.json."* | author |
| S02-040 | 2 · Refusals | *"Input '\<id\>' takes markdown_inline; use plaintext or markdown_block."* | author |
| S02-041 | 2 · Refusals | *"Input '\<id\>' takes a choice of shapes (anyOf); an input has one shape."* | author |
| S02-042 | 2 · Refusals | *"Input '\<id\>' declares channel '\<channel\>' (accepted: transcript, image, ambient-note, form)."* | author |
| S02-043 | 2 · Refusals | *"Input '\<id\>' declares channel '\<channel\>', which is only for a text input or an array of text."* | author |
| S02-044 | 2 · Refusals | *"Input '\<id\>' declares channel 'form', which needs an object with at least one property."* | author |
| S02-045 | 2 · Refusals | *"Input '\<id\>' field '\<property\>' has no title; the Create page labels each field by its title."* | author |
| S02-046 | 2 · Refusals | *"Input '\<id\>' declares default; inputs have no default at 31."* | author |
| S02-047 | 2 · Refusals | *"\<Subject\> declares one value; an enum with one value is a constant, not a choice."* | author |
| S02-048 | 2 · Refusals | *"\<Subject\> declares value '\<value\>' twice."* | author |
| S02-049 | 2 · Refusals | *"\<Subject\> value '\<value\>' must be snake_case (a lowercase letter, then lowercase letters, digits, or underscores)."* | author |
| S02-050 | 2 · Refusals | *"\<Subject\> gives two values the title '\<title\>'."* | author |
| S02-051 | 2 · Refusals | *"\<Subject\> writes oneOf branch \<n\> as \<shape\>; each branch is exactly { "const": \<value\>, "title": \<label\> }."* | author |
| S02-052 | 2 · Refusals | *"\<Subject\> declares both enum and oneOf; write one."* | author |
| S02-053 | 2 · Refusals | *"\<Subject\> is nullable but its enum doesn't list null; a nullable enum lists null among its values."* | author |
| S02-054 | 2 · Refusals | *"\<Subject\> is nullable but its oneOf has no { "const": null } arm; a nullable labelled enum adds one."* | author |
| S02-055 | 2 · Refusals | *"Format '\<name\>' declares \<n\> properties; a format sent to a model declares at most \<limit\>."* | author |
| S02-056 | 2 · Refusals | *"Format '\<name\>' nests \<n\> levels deep at \<path\>; a format sent to a model nests at most \<limit\>."* | author |
| S03-001 | 3 · The printer | *"skipped: input.kind.value = "table" is false"* | clinician |
| S03-002 | 3 · Refusals at publish | *"\<site\> compares \<path\> (\<format\>) with a literal; text is tested by whether it is blank, its size, or in."* | author |
| S03-003 | 3 · Refusals at publish | *"\<site\> compares \<path\> (\<format\>) with \<path\> (\<format\>); text is tested by whether it is blank, its size, or in."* | author |
| S03-004 | 3 · Refusals at publish | *"\<site\> uses ==; equality is written === (shown as =)."* | author |
| S03-005 | 3 · Refusals at publish | *"\<site\> uses !=; inequality is written !== (shown as ≠)."* | author |
| S03-006 | 3 · Refusals at publish | *"\<site\> uses \<operation\>, which is not a JSON Logic operation of this format (\<the allowed list\>)."* | author |
| S03-007 | 3 · Refusals at publish | *"\<site\> uses substr; text is cut with trim or plain, and measured with size."* | author |
| S03-008 | 3 · Refusals at publish | *"\<site\> orders \<path\> (\<format\>); \<, \>, ≤ and ≥ compare numbers or dates."* | author |
| S03-009 | 3 · Refusals at publish | *"\<site\> tests \<path\> (\<format\>) with not; not takes a boolean — test text with blank."* | author |
| S03-010 | 3 · Refusals at publish | *"\<site\> gives \<operation\> \<n\> operands; it takes \<m\>."* | author |
| S03-011 | 3 · Refusals at publish | *"\<site\> writes \<operation\> with a bare operand; operands are written as an array."* | author |
| S03-012 | 3 · Refusals at publish | *"\<site\> reads var with a default; every read is one path."* | author |
| S03-013 | 3 · Refusals at publish | *"\<site\> reads \<path\>, a position in a list; lists are read whole, or by identity through .items."* | author |
| S03-014 | 3 · Refusals at publish | *"\<site\> reads \<path\>, which doesn't exist here."* | author |
| S03-015 | 3 · Refusals at publish | *"\<site\> reads input.\<id\>; an input is read as input.\<id\>.value, .content or .title."* | author |
| S03-016 | 3 · Refusals at publish | *"\<site\> reads \<path\>.title, but \<format\> is a plain enum with no titles; read .value, or give the format oneOf with const and title."* | author |
| S03-017 | 3 · Refusals at publish | *"\<site\> compares \<path\>.title with "\<text\>", which is not one of its titles (\<titles\>)."* | author |
| S03-018 | 3 · Refusals at publish | *"\<site\> reads profile.\<field\>; profile fields are read only in deliverable templates and macro bodies, never in conditions or computed expressions."* | author |
| S03-019 | 3 · Refusals at publish | *"\<site\> reads \<root\>.\<rest\>; JSON Logic reads input, node, check, item, pass, param and run."* | author |
| S03-020 | 3 · Refusals at publish | *"Deliverable '\<id\>' if reads node.\<id\>.content; a deliverable's if reads data (.value), not text."* | author |
| S03-021 | 3 · Refusals at publish | *"Deliverable '\<id\>' if reads check.\<id\>; a deliverable's existence can't depend on a check."* | author |
| S03-022 | 3 · Refusals at publish | *"Macro '\<id\>' if reads param.\<name\>; a macro's if is shared, so it can't depend on one function's parameter."* | author |
| S03-023 | 3 · Refusals at publish | *"\<site\> compares \<path\> with "\<value\>", which is not one of its values (\<values\>)."* | author |
| S03-024 | 3 · Refusals at publish | *"\<site\> reads \<path\>.value.\<field\>, which not every member of \<format\> declares."* | author |
| S03-025 | 3 · Refusals at publish | *"\<site\> \<member\> yields \<format\>; a condition yields a boolean."* | author |
| S03-026 | 3 · Refusals at publish | *"Computed node '\<id\>' yields \<format\>; it declares \<format\>."* | author |
| S03-027 | 3 · Refusals at publish | *"Computed node '\<id\>' builds \<format\> without \<field\>; object must give every property of the format."* | author |
| S03-028 | 3 · Refusals at publish | *"Computed node '\<id\>' builds \<format\> with \<field\>, which the format doesn't declare."* | author |
| S03-029 | 3 · Refusals at publish | *"\<site\> gives \<operation\> a computed \<operand\>; \<operand\> must be written as a literal."* | author |
| S03-030 | 3 · Refusals at publish | *"\<site\> gives count_pass a min of \<n\>; min is a whole number, 0 or more."* | author |
| S03-031 | 3 · Refusals at publish | *"\<site\> pattern "\<pattern\>" is not I-Regexp (RFC 9485): \<reason\>."* | author |
| S03-032 | 3 · Refusals at publish | *"\<site\> pattern "\<pattern\>" is \<n\> characters long; the most is 200."* | author |
| S03-033 | 3 · Refusals at publish | *"\<site\> gives has_word a blank word; has_word finds one word or phrase."* | author |
| S03-034 | 3 · Refusals at publish | *"\<site\> uses if without an else; write the else."* | author |
| S03-035 | 3 · Refusals at publish | *"\<site\> cats \<path\> (\<format\>); convert Markdown with plain first."* | author |
| S03-036 | 3 · Refusals at publish | *"Node '\<id\>' declares \<modelDerived \| runDependent \| profileCarrying\> \<value\>, but its reads make it \<derived\>: \<the read that does, or none\>."* | author |
| S03-037 | 3 · Warnings at publish and in the Editor | *"\<site\> \<member\> reads run.\<fact\>; its decision can differ between runs with the same inputs."* | author |
| S03-038 | 3 · Warnings at publish and in the Editor | *"Computed node '\<id\>' reads \<run.fact or path\>, which is run-dependent; its value can differ between runs with the same inputs."* | author |
| S03-039 | 3 · Warnings at publish and in the Editor | *"computed from model text: node.\<id\>"* | author |
| S03-040 | 3 · Failures at run time | *"\<site\> \<member\> could not be decided: matches was given \<n\> MiB of text; the most is 1 MiB."* | author |
| S03-041 | 3 · Failures at run time | *"\<site\> \<member\> yields \<a value kind\>; a condition yields a boolean."* | author |
| S03-042 | 3 · Refusals at publish | *"\<site\> pattern "\<pattern\>" repeats \<n\> times; a counted repetition is at most 100."* | author |
| S03-043 | 3 · Refusals at publish | *"\<site\> pattern "\<pattern\>" doesn't compile with the engine's options: \<reason\>."* | author |
| S03-044 | 3 · Refusals at publish | *"\<site\> reads \<path\>, which carries profile text; prompts, parts and conditions don't read profile text."* | author |
| S04-001 | 4 · `until`, `max` and `.stopped` | *"stopped early at \<position name\>"* | clinician |
| S04-002 | 4 · `until`, `max` and `.stopped` | *"not run: beyond max \<n\>"* | clinician |
| S04-003 | 4 · `item` and the `.items` element | *"skipped: item.value.kind = "narrative" is false"* | clinician |
| S04-004 | 4 · `itemLabel`: naming items | *"Sections 2"* | author |
| S04-005 | 4 · How it runs | *"stopped at its bound of 3; the check never stopped holding"* | clinician |
| S04-006 | 4 · `case` | *"case '\<id\>': arm for \<value\> does nothing"* | author |
| S04-007 | 4 · Examples (migrated) | *"case 'route': arm for omit does nothing"* | author |
| S04-008 | 4 · Examples (migrated) | *"skipped: item.id ≠ "billing" or input.include_billing.value = true is false"* | clinician |
| S04-009 | 4 · Refusals at publish | *"Loop '\<id\>' declares label null; a loop's or branch's label is what the rail, History and the diagram show: write one."* | author |
| S04-010 | 4 · Refusals at publish | *"\<Kind\> '\<id\>' declares \<member\>, which belongs to \<a for \| a while \| an if \| a case\>."* | author |
| S04-011 | 4 · Refusals at publish | *"\<subject\> returns nothing; name the body node the outside reads with ret."* | author |
| S04-012 | 4 · Refusals at publish | *"\<subject\> returns \<ret\>, which is not one of its own children (\<full names\>): write the child's full name, for example node.sections.paragraphs."* | author |
| S04-013 | 4 · Refusals at publish | *"\<subject\> lists node '\<id\>' twice; a body is a set."* | author |
| S04-014 | 4 · Refusals at publish | *"\<Kind\> '\<id\>' declares format \<format\>; its ret makes it \<format\>."* | author |
| S04-015 | 4 · Refusals at publish | *"\<Kind\> '\<id\>' declares reproducible \<true \| false\>; its body makes it \<false \| true\>."* | author |
| S04-016 | 4 · Refusals at publish | *"\<Kind\> '\<id\>' declares \<modelDerived \| runDependent \| profileCarrying\> \<true \| false\>; its body makes it \<false \| true\>."* | author |
| S04-017 | 4 · Refusals at publish | *"\<Kind\> '\<id\>' \<in \| case \| with \<param\>\> is an expression; it names one readable thing: compute the value in a computed node and name that."* | author |
| S04-018 | 4 · Refusals at publish | *"Loop '\<id\>' has no body; name the nodes that run per item in nodes."* | author |
| S04-019 | 4 · Refusals at publish | *"Loop '\<id\>' declares parallel true with maxParallel 1, which runs one item at a time; declare "parallel": false and "maxParallel": null instead."* | author |
| S04-020 | 4 · Refusals at publish | *"Loop '\<id\>' declares maxParallel \<n\>; the most is FormatBounds.parallel (15)."* | author |
| S04-021 | 4 · Refusals at publish | *"Loop '\<id\>' declares maxParallel \<n\>; the least is 2, or null for no cap of its own."* | author |
| S04-022 | 4 · Refusals at publish | *"Loop '\<id\>' declares maxParallel \<n\> with parallel false; a sequential loop runs one item at a time: write "maxParallel": null."* | author |
| S04-023 | 4 · Refusals at publish | *"Loop '\<id\>' declares until with parallel true; until stops after the item where it holds, which needs items in order: declare "parallel": false and "maxParallel": null."* | author |
| S04-024 | 4 · Refusals at publish | *"Loop '\<id\>' declares max 0; the least is 1."* | author |
| S04-025 | 4 · Refusals at publish | *"Loop '\<id\>' iterates \<reference\>, which is \<format\>; only a list can be iterated."* | author |
| S04-026 | 4 · Refusals at publish | *"Loop '\<id\>' iterates item.value.\<field\>, but it runs inside no loop; item.value names the enclosing loop's item."* | author |
| S04-027 | 4 · Refusals at publish | *"Loop '\<id\>' iterates node.\<y\>.value.\<z\>; \<y\> runs inside loop '\<l\>' — a loop iterates a node outside it, or in an enclosing loop's body."* | author |
| S04-028 | 4 · Refusals at publish | *"Loop '\<id\>' itemLabel '\<field\>' is not a field of the elements of \<reference\> (fields: \<fields\>)."* | author |
| S04-029 | 4 · Refusals at publish | *"Loop '\<id\>' itemLabel '\<field\>' may be missing or null; itemLabel names a field every element has as a string."* | author |
| S04-030 | 4 · Refusals at publish | *"Loop '\<id\>' itemLabel '\<field\>' is \<format\>; itemLabel names a string field."* | author |
| S04-031 | 4 · Refusals at publish | *"While '\<id\>' declares max null; a while must declare its bound (1 to 15)."* | author |
| S04-032 | 4 · Refusals at publish | *"While '\<id\>' declares max \<n\>; a while runs at most FormatBounds.passes (15) passes."* | author |
| S04-033 | 4 · Refusals at publish | *"While '\<id\>' declares max \<n\>; the least is 1."* | author |
| S04-034 | 4 · Refusals at publish | *"While '\<id\>' has no body; name the nodes that run per pass in nodes."* | author |
| S04-035 | 4 · Refusals at publish | *"Node '\<id\>' in while '\<w\>' is neither returned nor read; name it with ret, read it from a body node or from the check."* | author |
| S04-036 | 4 · Refusals at publish | *"\<site\> reads pass.number, but it runs inside no while; pass is a while's pass."* | author |
| S04-037 | 4 · Refusals at publish | *"\<site\> reads pass.parent, but its while runs inside no while; pass.parent is the enclosing while's pass."* | author |
| S04-038 | 4 · Refusals at publish | *"\<site\> reads pass.previous.node.\<id\>, which is not in while '\<w\>'; a pass reads the while's own nodes."* | author |
| S04-039 | 4 · Refusals at publish | *"\<site\> reads node '\<id\>', which runs inside loop '\<l\>'; read node.\<l\>."* | author |
| S04-040 | 4 · Refusals at publish | *"\<site\> reads item.parent, but its loop runs inside no loop; item.parent is the enclosing loop's item."* | author |
| S04-041 | 4 · Refusals at publish | *"If '\<id\>' declares then null; an if runs a then body."* | author |
| S04-042 | 4 · Refusals at publish | *"Case '\<id\>' has no branches; a case runs one branch per set of values."* | author |
| S04-043 | 4 · Refusals at publish | *"Case '\<id\>' branch \<n\> lists no value; a branch's when names one or more values."* | author |
| S04-044 | 4 · Refusals at publish | *"Case '\<id\>' switches on \<reference\>, which is \<format\>; a case switches on an enumerated string."* | author |
| S04-045 | 4 · Refusals at publish | *"Case '\<id\>' branch \<n\> lists "\<value\>", which is not one of \<reference\>'s values (\<values\>)."* | author |
| S04-046 | 4 · Refusals at publish | *"Case '\<id\>' lists "\<value\>" in branches \<n\> and \<m\>; a value belongs to one branch."* | author |
| S04-047 | 4 · Refusals at publish | *"Case '\<id\>' doesn't list \<values\> and has no else; a case has a branch for every value: add a branch, an empty branch, or an else."* | author |
| S04-048 | 4 · Refusals at publish | *"Case '\<id\>' branch \<n\> writes nodes \<[] \| ids\> with ret \<ret\>; an empty branch writes nodes [] and ret null together."* | author |
| S04-049 | 4 · Refusals at publish | *"case '\<id\>': arm for \<value\> does nothing"* | author |
| S04-050 | 4 · Refusals at publish | *"Node '\<id\>' in function '\<f\>' reads input.\<name\>; a function reads only its parameters: add a parameter and pass it in with."* | author |
| S04-051 | 4 · Refusals at publish | *"Node '\<id\>' in function '\<f\>' reads \<reference\>; a function reads only its parameters: add a parameter and pass it in with."* | author |
| S04-052 | 4 · Refusals at publish | *"Function '\<f\>' uses \<snippet \| macro \| format \| renderer\> '\<id\>' but doesn't list it in uses."* | author |
| S04-053 | 4 · Refusals at publish | *"Function '\<f\>' has its own \<snippet \| macro \| format \| renderer\> '\<id\>' and also uses the package's: rename one."* | author |
| S04-054 | 4 · Refusals at publish | *"Function '\<a\>' calls '\<b\>', which calls '\<a\>': functions may not call themselves."* | author |
| S04-055 | 4 · Refusals at publish | *"Function '\<a\>' calls '\<a\>': functions may not call themselves."* | author |
| S04-056 | 4 · Refusals at publish | *"Call '\<id\>' reaches depth \<n\>; calls nest at most FormatBounds.depth (15) deep."* | author |
| S04-057 | 4 · Refusals at publish | *"Function '\<f\>' returns node.\<id\>, an if with no else: add an else, or return a node that always runs."* | author |
| S04-058 | 4 · Refusals at publish | *"Function '\<f\>' returns node.\<id\>, which runs inside if '\<b\>' and may be skipped: return a node that always runs."* | author |
| S04-059 | 4 · Refusals at publish | *"Function '\<f\>' returns node.\<id\>, a case with an empty branch for \<values\>: return a node that always runs."* | author |
| S04-060 | 4 · Refusals at publish | *"Function '\<f\>' returns node.\<id\>, whose branches return \<format\> and \<format\>: a function returns one format. Wrap them in an object format."* | author |
| S04-061 | 4 · Refusals at publish | *"Function '\<f\>' declares format \<format\>; its ret '\<id\>' returns \<format\>."* | author |
| S04-062 | 4 · Refusals at publish | *"Function '\<f\>' holds a \<checks \| deliverables\> folder; checks and deliverables live only at the package's top level: return a check_result or a value instead."* | author |
| S04-063 | 4 · Refusals at publish | *"Macro '\<m\>' is placed in function '\<f\>', where its if reads node.\<id\>, which doesn't exist there: add a classifier with that id (pattern A), or pass the decision in and hold it in a computed node (pattern B)."* | author |
| S04-064 | 4 · Refusals at publish | *"Call '\<id\>' names function '\<f\>', which the package doesn't define."* | author |
| S04-065 | 4 · Refusals at publish | *"Call '\<id\>' passes no \<param\>; function '\<f\>' takes \<params\>."* | author |
| S04-066 | 4 · Refusals at publish | *"Call '\<id\>' passes \<param\>, which function '\<f\>' doesn't take (\<params\>)."* | author |
| S04-067 | 4 · Refusals at publish | *"Function '\<f\>' parameter '\<param\>' declares \<required \| channel\>; a parameter has label, description and format, and every one is passed."* | author |
| S04-068 | 4 · Refusals at publish | *"Call '\<id\>' passes \<reference\> (\<format\>) as \<param\>; function '\<f\>' takes \<format\>."* | author |
| S04-069 | 4 · Refusals at publish | *"Function '\<id\>' reads param.\<name\>, which carries profile.\<field\>, in \<a prompt \| a part \| a condition\>; the profile is read only in deliverables and macro bodies."* | author |
| S04-070 | 4 · Refusals at publish | *"Call '\<id\>' declares format \<format\>; function '\<f\>' returns \<format\>."* | author |
| S04-071 | 4 · Refusals at publish | *"Call '\<id\>' has a body; a call is a header only."* | author |
| S04-072 | 4 · Notes and warnings at publish | *"Up to \<n\> agent calls could run at once; this engine runs at most \<N\> per job, so the rest wait their turn."* | author |
| S04-073 | 4 · Notes and warnings at publish | *"An unbounded number of agent calls could run at once (loop '\<id\>' has no cap over a list known only at run time); this engine runs at most \<N\> per job, so the rest wait their turn."* | author |
| S04-074 | 4 · Notes and warnings at publish | *"Function '\<f\>' lists \<snippet \| macro \| format \| renderer\> '\<id\>' in uses but never uses it."* | author |
| S04-075 | 4 · Refusals at publish | *"Case '\<id\>' switches on \<reference\>, which can be null, and has no else; a null subject goes to the else: add one."* | author |
| S04-076 | 4 · Refusals at publish | *"Case '\<id\>' branch \<n\> lists null; a null subject goes to the else."* | author |
| S04-077 | 4 · `until`, `max` and `.stopped` | *"0 items: \<reference\> is null"* | clinician |
| S04-078 | 4 · `until`, `max` and `.stopped` | *"Loop '\<id\>' was given \<n\> items; this engine runs at most \<limit\> per loop."* | clinician |
| S04-079 | 4 · Notes and warnings at publish | *"Loop '\<id\>' iterates \<reference\>, which could hold more than \<limit\> items; this engine runs at most \<limit\> per loop, and fails the loop beyond that."* | author |
| S04-080 | 4 · Notes and warnings at publish | *"Up to \<n\> agent calls could run in one job; this engine runs at most \<limit\> per job, and fails the job beyond that."* | author |
| S05-001 | 5 · Refusals | *"\<Subject\> uses \<construct\> at line \<n\>; templates present text and may not use assignment, capture, func, include, import, with, wrap, while, break, continue, case, tablerow or arithmetic."* | author |
| S05-002 | 5 · Refusals | *"\<Subject\> calls \<built-in\> at line \<n\>; the allowed built-ins are string.upcase, string.downcase, string.capitalize, string.strip, array.join, array.size and date.to_string."* | author |
| S05-003 | 5 · Refusals | *"\<Subject\> calls truncate at line \<n\>; truncate cuts clinical text."* | author |
| S05-004 | 5 · Refusals | *"\<Subject\> calls object.default at line \<n\>; choosing text is a decision: put it in a header condition."* | author |
| S05-005 | 5 · Refusals | *"\<Subject\> calls date.to_string at line \<n\> without a pattern; write the pattern, for example "%d %B %Y"."* | author |
| S05-006 | 5 · Refusals | *"\<Subject\> runs a for over \<expr\> at line \<n\>; a for runs over a list."* | author |
| S05-007 | 5 · Refusals | *"\<Subject\> tests \<expr\> in a body if at line \<n\>; a body if tests only loop position, state and whether a check passed. Decide it in a header: a part, a snippet's if or a macro's if."* | author |
| S05-008 | 5 · Refusals | *"Deliverable 'consult' branches on part.state and handles completed and skipped, but not not_run: add it or an else."* | author |
| S05-009 | 5 · Refusals | *"\<Subject\> branches on \<expr\> and handles \<states\>, but not \<missing\>: add it or an else."* | author |
| S05-010 | 5 · Refusals | *"\<Subject\> compares \<expr\> with "\<value\>" at line \<n\>; a state is completed, skipped or not_run."* | author |
| S05-011 | 5 · Refusals | *"\<Subject\> reads \<path\> at line \<n\>, which \<format or root\> doesn't have."* | author |
| S05-012 | 5 · Refusals | *"\<Subject\> stopped rendering: the for at line \<n\> reached 1,000 iterations."* | author |
| S05-013 | 5 · Refusals | *"\<Subject\> nests if and for \<n\> deep at line \<m\>; the limit is 15."* | author |
| S05-014 | 5 · Refusals | *"\<Subject\> stopped rendering: its output passed 1 MiB."* | author |
| S05-015 | 5 · Refusals | *"\<Subject\> places \<unit\> with ~}} at line \<n\>; it removes the line's newline, joining two lines. Use {{~ \<unit\> }} alone on a line."* | author |
| S05-016 | 5 · Refusals | *"\<Subject\> places \<unit\> with - at line \<n\>; it removes blank lines between paragraphs."* | author |
| S05-017 | 5 · Refusals | *"\<Subject\> places {{~ \<unit\> }} inside a line at line \<n\>; it removes the space before it. Use {{ \<unit\> }}."* | author |
| S05-018 | 5 · Refusals | *"\<Subject\> has text after {{~ \<unit\> }} at line \<n\>; a block placement stands alone on its line."* | author |
| S05-019 | 5 · Refusals | *"\<Subject\> uses - at line \<n\>; it removes blank lines between paragraphs. Use ~."* | author |
| S05-020 | 5 · Refusals | *"\<Subject\> reads \<root\> at line \<n\>; \<site\> reads \<allowed roots\>."* | author |
| S05-021 | 5 · Refusals | *"Node '\<id\>' reads profile.\<field\>; the clinician's profile is never sent to a model. Read it in a deliverable or a macro body."* | author |
| S05-022 | 5 · Refusals | *"Snippet '\<id\>' reads \<path\>, which isn't available where \<subject\> places it at line \<n\>."* | author |
| S05-023 | 5 · Refusals | *"\<Kind\> '\<id\>' reaches itself: \<chain\>."* | author |
| S05-024 | 5 · Refusals | *"\<Subject\> reads \<path\> and run.\<fact\> in one output at line \<n\>; an output that reads a run fact reads nothing else."* | author |
| S05-025 | 5 · Refusals | *"… reads \<path\> and the run-dependent \<value\> in one output …"* | author |
| S05-026 | 5 · Refusals | *"\<Subject\> pipes \<source\> (\<format\>) into renderer.\<id\>, which renders \<input format\>."* | author |
| S05-027 | 5 · Refusals | *"Node 'identify_problem' pipes node.plan.value (section_plan) into renderer.concept_bullets, which renders concept_list."* | author |
| S05-028 | 5 · Refusals | *"Renderer '\<id\>' declares format \<format\>; a renderer returns plaintext, markdown_block or markdown_inline."* | author |
| S05-029 | 5 · Refusals | *"Renderer '\<id\>' reads \<root\>; a renderer reads only the value piped into it."* | author |
| S05-030 | 5 · Refusals | *"\<Subject\> calls renderer.\<id\> at line \<n\>; pipe into it: \<value\> \| renderer.\<id\>."* | author |
| S05-031 | 5 · Refusals | *"\<Subject\> pipes into renderer.\<id\>, which this package doesn't define."* | author |
| S05-032 | 5 · Refusals | *"Renderer '\<id\>' takes the id of a built-in renderer."* | author |
| S05-033 | 5 · Refusals | *"Renderer '\<id\>' pipes into renderer.\<other\> at line \<n\>; chain renderers where they're used, not inside a renderer."* | author |
| S05-034 | 5 · Refusals | *"\<Subject\> pipes renderer.\<id\> (\<format\>) into renderer.\<next\>, which renders \<input format\>."* | author |
| S05-035 | 5 · Refusals | *"\<Subject\> places snippet.\<id\>, which this package doesn't define."* | author |
| S05-036 | 5 · Refusals | *"Snippet '\<folder\>/\<id\>' has a header that doesn't match format \<format\>: \<schema error\>."* | author |
| S05-037 | 5 · Refusals | *"\<Subject\> reads snippet.\<id\> at line \<n\>; read its text as snippet.\<id\>.content."* | author |
| S05-038 | 5 · Refusals | *"Node '\<id\>' places part.\<name\>, which its header doesn't declare."* | author |
| S05-039 | 5 · Refusals | *"Node '\<id\>' declares part '\<name\>' but never places it."* | author |
| S05-040 | 5 · Refusals | *"Node '\<id\>' places part.\<name\> \<n\> times; place a part once."* | author |
| S05-041 | 5 · Refusals | *"Node '\<id\>' declares parts, and only agent nodes have parts."* | author |
| S05-042 | 5 · Refusals | *"Macro '\<id\>' places macro.\<other\> in its body; a macro body is output text, written after the model replies. Put shared text in a snippet and place it in both."* | author |
| S05-043 | 5 · Refusals | *"Macro '\<id\>' places part.\<name\> in its body; …"* | author |
| S05-044 | 5 · Refusals | *"Macro '\<id\>' has \<n\> markers in its instruction; it must hold {{~ macro.\<id\>.content }} or {{ macro.\<id\>.content }} exactly once."* | author |
| S05-045 | 5 · Refusals | *"Macro '\<id\>' has the marker of macro '\<other\>' in its instruction."* | author |
| S05-046 | 5 · Refusals | *"Node '\<id\>' places macro.\<macro\>, whose format is \<format\>; an \<node format\> node takes \<allowed\>."* | author |
| S05-047 | 5 · Refusals | *"\<Subject\> places macro.\<id\>; only agent nodes place macros, in their prompt or a part's text."* | author |
| S05-048 | 5 · Refusals | *"\<Subject\> places macro.\<id\> twice, counting its parts' text; place a macro once in a template."* | author |
| S05-049 | 5 · Refusals | *"Node '\<id\>' places macro.\<macro\>, and returns \<format\>; macros are placed only in agent nodes returning a text format."* | author |
| S05-050 | 5 · Refusals | *"Macro '\<id\>' has format \<format\>, and its body \<reason, e.g. writes Markdown at line 2\>."* | author |
| S05-051 | 5 · Refusals | *"Macro '\<id\>' has a marker in its body; a body is the text that replaces the marker."* | author |
| S05-052 | 5 · Refusals | *"Macro '\<id\>' reads param.\<name\> in its if; decide outside the function and pass the answer in, or classify inside it."* | author |
| S05-053 | 5 · Refusals | *"The reply has no marker for macro '\<id\>'."* | author |
| S05-054 | 5 · Refusals | *"The reply has the marker for macro '\<id\>' \<n\> times."* | author |
| S05-055 | 5 · Refusals | *"The reply has a marker for macro '\<id\>', which wasn't offered."* | author |
| S05-056 | 5 · Refusals | *"The reply has a marker for '\<id\>', which isn't a macro."* | author |
| S05-057 | 5 · Refusals | *"The reply writes the marker for macro '\<id\>' \<inside a sentence \| alone on a line\>, but it was asked for \<alone on a line \| inside a sentence\>."* | author |
| S05-058 | 5 · Refusals | *"The reply has text after the marker for macro '\<id\>' on its line."* | author |
| S05-059 | 5 · Refusals | *"The reply has the markers out of order: '\<id\>' before '\<other\>'."* | author |
| S05-060 | 5 · Refusals | *"\<Subject\> reads \<run.fact or run-dependent value\> at line \<n\>. Its main hash differs between runs; runs are compared on the run-neutral hash."* | author |
| S05-061 | 5 · Refusals | *"\<Subject\> pipes renderer.\<id\>, a markdown_block, inside a line at line \<n\>."* | author |
| S05-062 | 5 · Refusals | *"\<Subject\> stopped rendering: it took more than \<limit\> steps."* | author |
| S05-063 | 5 · Refusals | *"\<Subject\> reads \<path\>[\<n\>] at line \<n\>, a position in a list; lists are read whole, with a for, or by identity through .items."* | author |
| S05-064 | 5 · Refusals | *"\<Subject\> reads \<path\> at line \<n\>, which carries profile text through macro '\<id\>'; a prompt or a part doesn't read profile text. Read it in a deliverable."* | author |
| S06-001 | 6 · Checks in the record and History | *"12 of 12 terms present"* | author |
| S06-002 | 6 · Checks in the record and History | *"7 of 9 sections passed"* | author |
| S06-003 | 6 · Checks in the record and History | *"Consultation note was blocked: check 'coverage' failed (10 of 12 terms present)."* | clinician |
| S06-004 | 6 · Item states | *"stopped early at \<position name\>"* | clinician |
| S06-005 | 6 · Headings are the author's | *"computed from model text: node.standards.section_instructions"* | author |
| S06-006 | 6 · Gating and outcomes | *"released: check '\<id\>' didn't apply (its if was false)"* | clinician |
| S06-007 | 6 · Delivery | *"not sent: EMR isn't set up for this account"* | clinician |
| S06-008 | 6 · The Profile page and the time zone | *"Set your time zone in your account settings before running a workflow."* | clinician |
| S06-009 | 6 · Refusals | *"Check '\<id\>' has format \<format\>; a check returns check_result."* | author |
| S06-010 | 6 · Refusals | *"Check '\<id\>' has kind \<kind\>; a check is computed."* | author |
| S06-011 | 6 · Refusals | *"\<Path\> in checks/ is \<kind\>; checks/ holds checks and the loops over them."* | author |
| S06-012 | 6 · Refusals | *"Check '\<id\>' passes \<expr\> as failWith; failWith is a literal sentence."* | author |
| S06-013 | 6 · Refusals | *"Check '\<id\>' passes \<expr\> as min; min is a whole number of at least 0."* | author |
| S06-014 | 6 · Refusals | *"Check loop '\<id\>' runs over \<source\>; a check loop runs over a production loop's .items."* | author |
| S06-015 | 6 · Refusals | *"Function '\<id\>' holds check '\<check\>'; functions hold no checks. Return a check_result as data and check the calls' .items."* | author |
| S06-016 | 6 · Refusals | *"Node '\<id\>' reads deliverable.\<deliverable\>; only checks read deliverables."* | author |
| S06-017 | 6 · Refusals | *"Node '\<id\>' reads deliverable.\<deliverable\>; deliverables are the job's outputs: read the nodes it is composed from."* | author |
| S06-018 | 6 · Refusals | *"Deliverable '\<id\>' reads check.\<check\>, which checks \<id\>: a deliverable can't read its own check."* | author |
| S06-019 | 6 · Refusals | *"Deliverable '\<id\>' reads deliverable.\<other\>; a deliverable reads nodes, inputs, snippets, checks, the profile and run facts."* | author |
| S06-020 | 6 · Refusals | *"Deliverable '\<id\>' has format \<format\>; a deliverable is markdown_block, plaintext or an object format."* | author |
| S06-021 | 6 · Refusals | *"Deliverable '\<id\>' is \<format\>, and reads \<path\> (\<read format\>) at line \<n\>. \<Convert it in a node \| Use a renderer or a node\>."* | author |
| S06-022 | 6 · Refusals | *"Deliverable '\<id\>' is plaintext, and line \<n\> writes Markdown ('\<text\>')."* | author |
| S06-023 | 6 · Refusals | *"Deliverable '\<id\>' is \<object format\>; its template is {{ node.\<x\>.value }} and nothing else."* | author |
| S06-024 | 6 · Refusals | *"Deliverable '\<id\>' reads \<path\> in its if; a deliverable's if reads inputs, node values and run facts."* | author |
| S06-025 | 6 · Refusals | *"Deliverable '\<id\>' has whenEmpty \<value\>; write release, hold or fail."* | author |
| S06-026 | 6 · Refusals | *"Deliverables folder '\<path\>' has delivery kind \<kind\>; the kinds are email, pdf, emr and zip."* | author |
| S06-027 | 6 · Refusals | *"deliverables/index.json is missing; the deliverables folder states its delivery."* | author |
| S06-028 | 6 · Refusals | *"\<Subject\> reads profile.\<field\>, which isn't a profile field; the fields are name, credentials, organisation, signature and closing."* | author |
| S06-029 | 6 · Refusals | *"\<Condition owner\> reads profile.\<field\> in a condition; the profile is read only in deliverables and macro bodies."* | author |
| S06-030 | 6 · Refusals | *"Function '\<id\>' reads param.\<name\>, which carries profile.\<field\>, in \<a prompt \| a part \| a condition\>; the profile is read only in deliverables and macro bodies."* | author |
| S06-031 | 6 · Refusals | *"This workflow needs your signature. Choose one in Profile."* | clinician |
| S06-032 | 6 · Refusals | *"This workflow needs your \<field label\>. Set it in Profile, under Letter details."* | clinician |
| S06-033 | 6 · Refusals | *"\<Deliverable label\> was blocked: check '\<id\>' failed (\<detail\>)."* | author |
| S06-034 | 6 · Refusals | *"not sent: \<Kind\> isn't set up for this account"* | clinician |
| S06-035 | 6 · Refusals | *"Check '\<id\>' gates deliverable '\<deliverable\>', and its if reads \<path\>, which can be null; a gate check's if reads values that are always set."* | author |
| S06-036 | 6 · Refusals | *"\<Subject\> reads \<path\>, which carries profile text; prompts, parts and conditions don't read profile text. Read it in a deliverable."* | author |
| S06-037 | 6 · Refusals | *"\<Deliverable label\> was blocked: check '\<id\>' could not run (\<error\>)."* | clinician |
| S06-038 | 6 · Refusals | *"not sent: the job failed"* | clinician |
| S07-001 | 7 · Upgrading a locked library: the corpus re-render | *"Scriban output changed at 7.3.0"* | author |
| S07-002 | 7 · Where the files live | *"Download package"* | author |
| S07-003 | 7 · Refusals | *"This workflow (\<package\>@\<version\>) needs \<component\> \<range\>; this engine runs \<component\> \<engine version\>. Publish a new version of the workflow to run it on this engine."* | clinician |
| S07-004 | 7 · Refusals | *"This workflow (\<package\>@\<version\>) needs \<kind or feature\> '\<name\>', which this engine doesn't support. Publish a new version of the workflow to run it on this engine."* | clinician |
| S07-005 | 7 · Refusals | *"This workflow (\<package\>@\<version\>) needs agent \<agent name\> version \<version\>, which this engine doesn't have. Publish a new version of the workflow to run it on this engine."* | clinician |
| S07-006 | 7 · Refusals | *"Workflow \<package\>@\<version\> can't run: its compiled document doesn't match the hash published for it."* | author |
| S07-007 | 7 · Refusals | *"Test '\<test id\>' failed: \<expectation\> for \<key\> expected \<expected\>, got \<actual\>. Publish stopped."* | author |
| S07-008 | 7 · Refusals | *"Test '\<test id\>' has no stub for \<row key\>, which runs. Add it to outputs."* | author |
| S07-009 | 7 · Refusals | *"Test '\<test id\>' stubs \<row key\> with a value that isn't \<format\>: \<first validation error\>."* | author |
| S07-010 | 7 · Refusals | *"Test '\<test id\>' gives no value for input '\<input id\>'. List every input; use null for an optional input left unset."* | author |
| S07-011 | 7 · Refusals | *"Test '\<test id\>' must give exactly the profile fields the workflow reads: \<fields\>."* | author |
| S07-012 | 7 · Refusals | *"Test '\<test id\>' must give exactly the run facts the workflow reads: \<facts\>."* | author |
| S07-013 | 7 · Refusals | *"Tests took longer than 60 seconds in all. Publish stopped."* | author |
| S07-014 | 7 · Refusals | *"Test '\<test id\>' stubs \<row key\>, which doesn't run."* | author |
| S07-015 | 7 · Refusals | *"\<path\> is evidence written only by publish; it is ignored and shouldn't be committed."* | author |
| S07-016 | 7 · Refusals | *"This package's resolve.json and lock.json were ignored; publishing writes new ones."* | author |
| S07-017 | 7 · Refusals | *"Workflow \<package\>@\<version\> can't run: its lock doesn't match the hash published for it, or doesn't belong to its compiled document."* | clinician |
| S08-001 | 9 · Sentences the record holds | *"skipped: …"* | clinician |
| S08-002 | 9 · Sentences the record holds | *"not run: beyond max \<n\>"* | clinician |
| S08-003 | 9 · Sentences the record holds | *"held: empty"* | clinician |
| S08-004 | 9 · Sentences the record holds | *"skipped: \<condition\> is false"* | clinician |
| S08-005 | 9 · Sentences the record holds | *"skipped: \<printed condition\> is false"* | clinician |
| S08-006 | 9 · Sentences the record holds | *"not sent: \<kind\> isn't set up for this account"* | clinician |
| S08-007 | 9 · Sentences the record holds | *"blocked: check '\<id\>' failed (\<detail\>)"* | clinician |
| S08-008 | 9 · Sentences the record holds | *"blocked: check '\<id\>' could not run (\<error\>)"* | clinician |
| S08-009 | 9 · Sentences the record holds | *"cancelled: the job didn't finish within \<n\> minutes"* | clinician |
| S09-001 | 8 · Which spec versions an engine admits | *"specVersion 31 is not supported: this engine accepts specVersion \<list\> (pre-v5 packages are archived; see registry-operations.md)."* | author |
| S09-002 | 8 · The publish note | *"Up to \<n\> agent calls could run at once; this engine runs at most \<ceiling\> per job, so the rest wait their turn."* | author |
| S09-003 | 8 · The publish note | *"An unbounded number of agent calls could run at once, since \<loop key\> has no maxParallel and reads a list of unknown length; this engine runs at most \<ceiling\> per job, so the rest wait their turn."* | author |
| S09-004 | 8 · Sentences the pages show | *"migrated by the operator from \<old version\>"* | author |
| S09-005 | 8 · Sentences the pages show | *"\<deliverable label\> was blocked: check '\<check id\>' failed (\<check detail\>)."* | author |
| S09-006 | 8 · Sentences the pages show | *"16 November 2026"* | author |
| S09-007 | 8 · Sentences the pages show | *"This package uses the new format. You can view and download it; editing returns in a later release."* | author |
| S09-008 | 8 · Sentences the engine shows | *"This workflow (example-nested-note@v2026.11.2) needs Scriban ^7.2; this engine runs Scriban 8.0.1. Publish a new version of the workflow to run it on this engine."* | clinician |
| S09-009 | 8 · Sentences the engine shows | *"The compiled workflow \<package\>@\<version\> doesn't match its published hash, so it can't be run. Tell the operator."* | clinician |
| S09-010 | 8 · Sentences the engine shows | *"The model service stayed busy for \<n\> minutes. Run the workflow again later."* | clinician |
| S09-011 | 8 · Sentences the engine shows | *"The model service \<timed out \| returned an error \| couldn't be reached\> \<n\> times in a row. Run the workflow again later."* | clinician |
| S09-012 | 8 · Sentences the engine shows | *"The job didn't finish within \<n\> minutes. Run the workflow again later."* | clinician |
| S09-013 | 8 · Sentences the engine shows | *"Up to \<n\> agent calls could run at once; this engine runs at most \<ceiling\> per job, so the rest wait their turn."* | author |
| S09-014 | 8 · Sentences the engine shows | *"The compiled workflow \<package\>@\<version\> doesn't match its lock, so it can't be run. Tell the operator."* | clinician |
| S09-015 | 8 · Sentences the engine shows | *"The job reached \<limit\> agent calls, the most this engine runs for one job."* | clinician |
| S09-016 | 8 · The publish note | *"\<package\> could run for about \<n\> minutes in the worst case; this engine stops a job after \<limit\> minutes."* | author |
| S09-017 | 8 · Delivery at the end | *"Couldn't send to \<destination\>. Copy the note instead."* | clinician |
| S09-018 | 8 · Every deploy is preceded by a drain | *"Waiting for an update to finish"* | clinician |
| S09-019 | 8 · Delivery at the end | *"Delivering…"* | clinician |
| S10-001 | 10 · Hand edits, with notices | *"written; hand edits remain"* | author |
| S10-002 | 10 · Hand edits, with notices | *"Hand edit needed in \<file\>, \<member\>: \<reason\>."* | author |
| S10-003 | 10 · What the converter refuses, and `!x` on text | *"The condition '\<expression\>' uses \<construct\>, which has no JSON Logic form at 31: rewrite it by hand."* | author |
| S10-004 | 10 · Hand edits, with notices | *"the prompt reads profile.\<field\>, which a 31 prompt doesn't read; move it to a deliverable or a macro body."* | author |
| S10-005 | 10 · A package that stays at 30, and what its owner is told | *"\<package\> stays at version 30 for now: \<reason\>. Its pin is unchanged; you can migrate it in the Editor when Milestone 41 arrives."* | clinician |
| S10-006 | 10 · Reserved ids are renamed | *"Renamed '\<id\>' to '\<new id\>'; '\<id\>_\<kind\>' was already taken."* | author |

## 12. Conformance

The conformance suite is released with this document in `consultologist-package-format`, under
[`v31/conformance/`](v31/conformance/README.md), so that an implementation outside this repository
can be checked against the format. **Its expectations are exported by the library's generators,
as for every spec bump, and are never written by hand:** a golden, a vector or an expected
document is a byte sequence that code produced, and a hand-typed one would be a guess. The hand-written
files of the suite are the schemas' example instances, which are examples and not goldens
([`v31/conformance/README.md`](v31/conformance/README.md)).

### 12.1 The index

[`v31/conformance/index.json`](v31/conformance/index.json), judged by
[`conformance-index.schema.json`](v31/schemas/conformance-index.schema.json), lists the suite by
family:

| Member | Type | Meaning |
|---|---|---|
| `specVersion` | integer | `31` |
| `families` | array of family | one per kind of case, in § 12.2's order |

**A family** is `{ "id", "path", "about", "exportedBy", "cases" }`, every member written:

| Member | Type | Meaning |
|---|---|---|
| `id` | string | the family's id, as named in § 12.2 |
| `path` | string | where its cases live, from the root of the repository |
| `about` | string | what it holds |
| `exportedBy` | string | the build area that exports it, by number and name |
| `cases` | array of string | the cases, by path within the family; `[]` until the area that exports the family has exported them |

Each family is **empty until its area exports it,** except `schemas`, whose `cases` are the
example files of this release. The `constants` family and the sentences of `refusal-packages` are
published as the files named in § 12.2, and carry no case files of their own. An implementation
reads a family's cases from its `path`, never from this chapter.

### 12.2 What the suite holds

Each item of the suite, where it lives under `v31/`, and the build area that exports it:

| Item | Family `id` | Lives at | Exported by |
|---|---|---|---|
| **The schemas** of the 31 file kinds, of `resolve.json` and `lock.json` (with their media types, `application/vnd.consultologist.resolve+json` and `application/vnd.consultologist.lock+json`), of the publish report (`application/vnd.consultologist.publish-report+json`), and the dialect's meta-schema (`urn:consultologist:spec:31:dialect`); each with hand-written example instances, valid and invalid | `schemas` | `v31/schemas/`, `v31/dialect.schema.json`; the examples in `v31/conformance/schemas/` | area 00, the contracts (here, now) |
| **The published constants:** `FormatBounds`, `SourceBounds` (as `bounds.json`, [chapter 1](#1-files-and-scopes)), the reserved ids, the producer values (with those reserved for Milestone 40), the Markdig extension list for the pinned Markdig version, and the profile fields | `constants` | `v31/bounds.json`, `v31/constants.json`, `v31/profile.json`: files, not cases | area 00, the contracts (here, now) |
| **A valid and an invalid package for every refusal sentence;** each invalid package carries the exact sentence it must produce. The sentences themselves are [chapter 11](#11-every-sentence) | `refusal-packages` | `v31/sentences.json` (here, now); the packages in `v31/conformance/refusal-packages/` | the sentences: area 00, the contracts (here, now); the packages: areas 02 to 08, each for the sentences of the chapters it builds (area 02, parser and file model; area 03, types; area 04, JSON Logic; area 05, resolver and lock; area 06, engine loading and scheduling; area 07, prompts and macros; area 08, checks, deliverables and the profile) |
| **Golden tests, operations:** every built-in operation's output; any change to output bytes is a major version ([chapter 7 § 7.4.3](#743-versioning-built-in-operations-and-machinery)) | `operation-goldens` | `v31/conformance/operation-goldens/` | area 04, JSON Logic |
| **Golden tests, the printer:** the printer's text for every operation, with `=` and `≠` ([chapter 3 § 3.8](#38-the-printer)) | `printer-goldens` | `v31/conformance/printer-goldens/` | area 04, JSON Logic |
| **Golden tests, the built-in renderers** ([chapter 5 § 5.5](#55-renderers)) | `renderer-goldens` | `v31/conformance/renderer-goldens/` | area 07, prompts and macros, and area 08, checks, deliverables and the profile |
| **Golden tests, Scriban dialect features** ([chapter 5 § 5.2](#52-the-dialect)) | `dialect-goldens` | `v31/conformance/dialect-goldens/` | area 07, prompts and macros |
| **Null and absence vectors** for every JSON Logic operation, one per rule in chapter 3's table ([§ 3.6.3](#363-each-operations-null-behaviour-is-a-conformance-vector)) | `null-vectors` | `v31/conformance/null-vectors/` | area 04, JSON Logic |
| **Text-handling vectors** for `lower`, `trim`, `words` and `has_word`, pinned to the .NET runtime and Unicode version `lock.json` records ([chapter 7 § 7.4.1](#741-members)), so a runtime change that moves case mapping or word characters is caught | `text-vectors` | `v31/conformance/text-vectors/` | area 04, JSON Logic |
| **Number vectors:** IEEE doubles, non-finite results giving `null`, and `integer` as a kind of `number` ([chapter 3 § 3.7](#37-typing)) | `number-vectors` | `v31/conformance/number-vectors/` | area 04, JSON Logic |
| **Date vectors** for the date operations ([chapter 3 § 3.5.5](#355-date-operations)) | `date-vectors` | `v31/conformance/date-vectors/` | area 04, JSON Logic |
| **Markdown escape vectors:** CommonMark's backslash escapes for ASCII punctuation ([chapter 6](#6-checks-deliverables-and-the-profile)) | `markdown-escape-vectors` | `v31/conformance/markdown-escape-vectors/` | area 07, prompts and macros, and area 08, checks, deliverables and the profile |
| **Fixtures for the compiled documents:** fixture packages with their expected `resolve.json` and `lock.json` bytes and hashes, `requires` and `needs`, and the publish report (including the ceiling note and test results) | `compiled-documents` | `v31/conformance/compiled-documents/` | area 05, resolver and lock, and area 11, registry and publish |
| **Migration vectors:** 30 packages with their expected 31 output and notices, so an outside implementation of the migration ([chapter 10](#10-migration-30--31)) can be checked too | `migration-vectors` | `v31/conformance/migration-vectors/` | area 10, migration |

### 12.3 A case

What a case looks like is fixed by the area that exports its family, in the same release as the
cases. Three things are fixed here. A case of `refusal-packages` is a package folder with an
`expect.json` holding `valid` and, for an invalid package, the sentences the checker must produce,
exactly as [chapter 11](#11-every-sentence) prints them. A golden or a vector holds an input and
the bytes a generator produced for it. A `schemas` case is a hand-written instance of one schema,
`{ "about", "instance" }`, which is valid or invalid by its file name
([`v31/conformance/README.md`](v31/conformance/README.md)).
