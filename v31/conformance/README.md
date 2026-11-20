# specVersion 31 conformance suite (preview)

This folder is the conformance suite of specVersion 31, described by
[chapter 12](../../package-format-v31.md#12-conformance) of the normative document: what the suite
holds, where each part lives and which build area exports it. Only one part of it is written by
hand, the schemas' example instances (below). **Every other expectation is exported by the
library's generators and is never written by hand:** a golden, a vector or an expected document is
a byte sequence that code produced, and a hand-typed one would be a guess.
[`index.json`](index.json) lists the suite by family; an implementation reads a family's cases from
its `path`, never from this file.

## Layout

One family per kind of case, in the order of
[chapter 12 § 12.2](../../package-format-v31.md#122-what-the-suite-holds). A family's folder is empty
(and absent) until the area that exports it has exported its cases.

| Family `id` | Lives at | Exported by |
|---|---|---|
| `schemas` | `v31/schemas/`, `v31/dialect.schema.json`; the examples in `v31/conformance/schemas/<name>/` | area 00, the contracts |
| `constants` | `v31/bounds.json`, `v31/constants.json`, `v31/profile.json` (files, not cases) | area 00, the contracts |
| `refusal-packages` | `v31/sentences.json`; the packages in `v31/conformance/refusal-packages/` | the sentences: area 00; the packages: areas 02 to 08, each for its chapters' sentences |
| `operation-goldens` | `v31/conformance/operation-goldens/` | area 04, JSON Logic |
| `printer-goldens` | `v31/conformance/printer-goldens/` | area 04, JSON Logic |
| `renderer-goldens` | `v31/conformance/renderer-goldens/` | areas 07 and 08 |
| `dialect-goldens` | `v31/conformance/dialect-goldens/` | area 07, prompts and macros |
| `null-vectors` | `v31/conformance/null-vectors/` | area 04, JSON Logic |
| `text-vectors` | `v31/conformance/text-vectors/` | area 04, JSON Logic |
| `number-vectors` | `v31/conformance/number-vectors/` | area 04, JSON Logic |
| `date-vectors` | `v31/conformance/date-vectors/` | area 04, JSON Logic |
| `markdown-escape-vectors` | `v31/conformance/markdown-escape-vectors/` | areas 07 and 08 |
| `compiled-documents` | `v31/conformance/compiled-documents/` | areas 05 and 11 |
| `migration-vectors` | `v31/conformance/migration-vectors/` | area 10, migration |

## What a case looks like

The exporting area fixes the exact files in the release that carries the cases
([chapter 12 § 12.3](../../package-format-v31.md#123-a-case)). The level fixed here:

- **`refusal-packages`:** a case is a folder holding a package and an `expect.json` with `valid`
  (a boolean) and, for an invalid package, the sentences the checker must produce, exactly as
  [chapter 11](../../package-format-v31.md#11-every-sentence) prints them (`<…>` filled in). There is
  a valid and an invalid package for every refusal sentence.
- **Goldens and vectors** (`operation-goldens`, `printer-goldens`, `renderer-goldens`,
  `dialect-goldens`, `null-vectors`, `text-vectors`, `number-vectors`, `date-vectors`,
  `markdown-escape-vectors`): a case holds an input and the bytes a generator produced for it.
- **`compiled-documents`:** a fixture package with its expected `resolve.json` and `lock.json`
  bytes and hashes, its `requires` and `needs`, and its publish report.
- **`migration-vectors`:** a package at 30 with its expected package at 31 and its notices.
- **`schemas`:** a hand-written instance of one schema, valid or invalid by its file name (next
  section). These are examples, not goldens.

## The schemas' examples

`schemas/<name>/` holds hand-written instance files for the schema `<name>` (`dialect` is
`v31/dialect.schema.json`; any other name is `v31/schemas/<name>.schema.json`). Each file is
`{ "about": "<the rule, in words>", "instance": <the JSON> }`, with an optional
`"against": "<a pointer>"` member (written between `about` and `instance`) that judges the instance against
that part of the schema instead of its root, for example `"#/$defs/inline"` for the dialect. A `valid-*.json` instance must
validate and an `invalid-*.json` instance must not; `python3 scripts/check-v31.py` runs them
(group `examples`). They are examples, not goldens.

For `dialect`, the instance is a format document, judged by the dialect's meta-schema. The
meta-schema judges shape only and never dereferences a `$ref`, so `{ "$ref": "plaintext" }` is
data in an instance.

## What the meta-schema cannot state

These rules of [chapter 2](../../package-format-v31.md#2-types-and-inputs) are left to the validator
and have no invalid example here:

- every declared property is listed in `required`, and `required` lists nothing else
  ([§ 2.3.3](../../package-format-v31.md#233-required-additionalproperties-and-the-root));
- a nullable scalar written with `anyOf` instead of a type array
  ([§ 2.3.2](../../package-format-v31.md#232-one-way-to-write-nullable));
- a `$ref` that names no format, or that reaches its own definition
  ([§ 2.3.1](../../package-format-v31.md#231-the-keywords),
  [§ 2.6.3](../../package-format-v31.md#263-references-by-bare-id-no-shadowing));
- an `enum` value that is not snake_case, and duplicate or empty `oneOf` titles
  ([§ 2.9](../../package-format-v31.md#29-enum-labels));
- a text format missing its `contentMediaType` or `x-markdown`
  ([§ 2.5.1](../../package-format-v31.md#251-the-annotations));
- strict mode's size limits and an `anyOf` at the root of a format sent to a model
  ([§ 2.3.3](../../package-format-v31.md#233-required-additionalproperties-and-the-root)).

Two readings the text makes: an `enum` or a labelled `oneOf` must sit beside an explicit string
`type` (the text says "on a string" and always writes the type), and a `$defs` name is any name
without a `/`, not bound by the id pattern.

The `formats` check group does enforce the first of these on the built-in formats.

## Open points found while writing

Each is a place where the source design disagrees with itself or leaves a shape open, and what the
document and the schemas did about it. The design is
[`package-format-v31/`](https://github.com/Consultologist/Consultologist-Blazor/blob/def6f6cf/docs/customizable-workflow/package-format-v31/index.md)
in the engine repository; "the design's table" below means its member tables and sentence table.
Chapters are those of [`package-format-v31.md`](../../package-format-v31.md).

- **`concept_context` reads `source`.** The built-in `concept_context`
  ([chapter 5 § 5.5.3](../../package-format-v31.md#553-built-in-renderers)) reads `source` on each
  concept, which the catalogue's `concept_list` format does not declare (its objects are closed).
  So the value an engine pipes into this renderer is the stored concept list, with `source`
  stamped from the producing node; the format and the stored value disagree by that one member.
  The area that builds renderers (07) inherits the question of whether `concept_list` gains
  `source` or the renderer loses it.
- **`concept_context` pipes inside an `if`.** The built-in `concept_context` tests blank support as
  `{{ if c.support != null && (c.support | string.strip) != "" }}`, a pipe inside an `if`'s test.
  [Chapter 5 § 5.2.1](../../package-format-v31.md#521-statements) lists the pipe (`x | string.strip`)
  and the output tag "optionally piped", and
  [§ 5.2.5](../../package-format-v31.md#525-a-body-if-tests-recorded-facts-only) combines a test's
  facts "with `!`, `&&`, `||` and parentheses"; neither says a pipe may stand inside a test, and
  anything not listed as allowed is refused. So the registry's own renderer needs a construct the
  dialect as published refuses. The renderer's bytes are proven against the C# renderer and are not
  changed; whether the dialect allows a pipe to a built-in inside a renderer body's `if` is to be
  settled before the dialect checker is built (area 07).
- **Chapter 5's printed renderer.** The design prints `renderers/concept_bullets.md` testing
  `value.size == 0`, with `(none)` on a line of its own. The registry's file
  ([`v31/renderers/concept_bullets.md`](../renderers/concept_bullets.md)) tests
  `value.concepts.size == 0`, since a `concept_list` value is an object whose list is `concepts`,
  and writes `(none){{~ else ~}}`, which gives the C# renderer's bytes.
  [Chapter 5 § 5.5.1](../../package-format-v31.md#551-the-file) prints the registry's file, and
  `scripts/check-v31.py` holds the two equal.
- **`check_result`'s nullable arrays.**
  [Chapter 6 § 6.2.1](../../package-format-v31.md#621-the-format) writes `uncovered` and `untested`
  as `{ "type": ["array", "null"], "items": … }`, a type array of a non-scalar plus `null`, while
  [chapter 2 § 2.3.2](../../package-format-v31.md#232-one-way-to-write-nullable) keeps type arrays
  for scalars. The built-in keeps chapter 6's shape, and the dialect's meta-schema admits `"array"`
  (and `"object"`) in a type array beside `"null"`.
- **A nullable `date`.** The dialect allows `format: "date"` only beside `"type": "string"`
  ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)), so `"type": ["string", "null"]`
  with `format: "date"` is refused. Chapter 2 does not say whether an optional date is written some
  other way.
- **Nine shared flow members, not eight.**
  [Chapter 4 § 4.1](../../package-format-v31.md#41-flow-nodes-are-folders) says "Members every flow
  node's `index.json` has", and the design's sections for `for`, `while`, `if` and `case`
  ([§ 4.2.1](../../package-format-v31.md#421-members), [§ 4.3.1](../../package-format-v31.md#431-members),
  [§ 4.5.1](../../package-format-v31.md#451-if), [§ 4.5.2](../../package-format-v31.md#452-case))
  count "§ 1's eight members", totalling sixteen (`for`), fourteen (`while`), eleven (`if`) and
  eleven (`case`), but § 4.1's table lists nine (`kind`, `label`, `description`, `format`,
  `reproducible`, `producer`, `modelDerived`, `runDependent`, `profileCarrying`), all required. The
  text and the schemas follow the nine-row table, so a `for` has seventeen members, a `while`
  fifteen, an `if` and a `case` twelve.
- **Header examples that omit members.** [Chapter 1 § 1.4](../../package-format-v31.md#14-front-matter)'s
  agent header ends in `…`; [chapter 5 § 5.7.2](../../package-format-v31.md#572-placing-a-part)'s
  `section_instructions` ends in `…` (it omits `if`);
  [chapter 4 § 4.7.7](../../package-format-v31.md#477-the-call-node)'s `call` ends "plus chapter 1's
  remaining leaf members" (it omits `if`);
  [§ 4.7.6](../../package-format-v31.md#476-one-ret-always-valued-one-format) and
  [§ 4.7.10](../../package-format-v31.md#4710-macros-inside-functions)'s computed nodes omit
  `description`, `reproducible` and `if`; chapter 1 § 1.4's `plan` header omits `reproducible`,
  `if`, `onInvalid`, `failIfEmpty`, `parts` and `ordered`. The member tables
  ([chapter 1 § 1.5.2](../../package-format-v31.md#152-the-members-by-file),
  [chapter 5 § 5.1.2](../../package-format-v31.md#512-an-agent-nodes-prompt-members)) make every one
  required, so each valid instance writes them out: `if` and `description` as `null`,
  `reproducible` as the table's value, and, for `plan`, `onInvalid` as `"retry"` (a made-up value:
  § 5.1.2 says "as at version 30" and gives no value to copy).
- **An agent node carries `if`.**
  [Chapter 1 § 1.5.1](../../package-format-v31.md#151-the-members-every-header-shares) puts `if` on
  every production leaf, and [§ 1.5.2](../../package-format-v31.md#152-the-members-by-file) lists it
  for an `agent` node, but
  [chapter 5 § 5.1.2](../../package-format-v31.md#512-an-agent-nodes-prompt-members)'s table of an
  agent's prompt members does not repeat it. The schema requires it.
- **`derivedFrom`.** [Chapter 1 § 1.3](../../package-format-v31.md#13-the-manifest) types it a string
  or `null` (the `name@version` the package was copied from). The schema accepts any string; the
  `name@version` shape is not stated, so it is not enforced.
- **A deliverable's `format`.**
  [Chapter 6 § 6.6.1](../../package-format-v31.md#661-the-file) allows `markdown_block`, `plaintext`
  or an object format and refuses `markdown_inline`, while
  [chapter 1 § 1.5.1](../../package-format-v31.md#151-the-members-every-header-shares) says every
  `format` is "a format name or an inline schema". A schema cannot tell an object format's name from
  any other name, so the schema takes a name, any id except `markdown_inline`; the validator holds
  the rest.
- **A test's value shapes.**
  [Chapter 7 § 7.8.1](../../package-format-v31.md#781-the-file-testsidjson) and
  [§ 7.8.3](../../package-format-v31.md#783-expectations) type some values loosely. The schema reads
  a profile field's value as a string
  ([chapter 6 § 6.10.1](../../package-format-v31.md#6101-the-closed-list) lists them as `string` and
  `plaintext`), a `hash` as `sha256:` and 64 lowercase hex digits (the shape of every hash in the
  design; the design prints `"sha256:…"`), a `stopped` and a decision's branch id as strings, and a
  row key as a rooted key with an optional `:` and `/`-joined item path. An `inputs` value and a
  `values` value are any JSON.
- **Rules a schema cannot state** (left to the validator, no invalid example here): that `ret`
  names a direct child of its own body; that a `case` branch's `when` values belong to the
  subject's enum and appear in one branch only; that a `case` without an `else` lists every value;
  that `with` names every parameter of the function and no other; that `in` names a list and
  `itemLabel` a string field of its elements; that `channel` suits the input's format
  ([chapter 2 § 2.8.3](../../package-format-v31.md#283-channel)); that a description is at most 500
  code points joined; and that every `reproducible`, `modelDerived`, `runDependent` and
  `profileCarrying` equals its derived value, where the schemas fix only the values the design
  fixes by kind (an agent node, a rendered node, a computed node and a check).
- **A `description`'s 500-code-point limit is not expressible in the schemas.** A description is
  limited to 500 code points, its lines joined. JSON Schema's `maxLength` counts the same units for
  one string, but a description is written as lines (an array of strings) and the limit is on the
  lines joined, which no keyword can add up. The schemas state the lines' shape only; the limit
  (`descriptionCodePoints` in `constants.json`) is left to the validator.
- **`failIfEmpty`.** [Chapter 5 § 5.1.2](../../package-format-v31.md#512-an-agent-nodes-prompt-members)
  types it a string or `null` (the sentence the job fails with); the design's migration part says it
  is "written true, false or null" (carried into
  [chapter 10 § 10.1](../../package-format-v31.md#101-what-the-rewrite-does-mechanically)). The
  schema follows chapter 5's member table.
- **`macro.instruction`'s `minItems: 1`** follows from the marker having to appear exactly once in
  the instruction (S05-044), not from
  [chapter 5 § 5.8.1](../../package-format-v31.md#581-the-file)'s member table.
- **Patterns that are the schemas' reading.** The row-key, stub-key and `check.` / `deliverable.`
  key patterns in `test.schema.json` are not sentences of the text. The `itemLabel` pattern is the id
  pattern, taken from
  [chapter 2 § 2.5.3](../../package-format-v31.md#253-object-schemas-are-fully-typed-nested-text-references-a-text-format)
  (field names follow the id pattern);
  [chapter 4 § 4.2.1](../../package-format-v31.md#421-members) says only "a field name (string)".
- **An input's `format` beside
  [chapter 2 § 2.8.1](../../package-format-v31.md#281-which-formats-an-input-may-take-and-its-widget).**
  The schema refuses the name `markdown_inline` and an inline schema whose root has `anyOf`. It does
  not refuse `{ "$ref": "markdown_inline" }` written inline; the validator does.
- **The compiled documents' schemas read from the member tables.**
  [Chapter 7 § 7.2.9](../../package-format-v31.md#729-an-example-example-nested-note-at-31-abridged)'s
  `resolve.json` example is abridged and cannot be a valid instance as printed (its `deliverable.note`
  also leaves out `parent`, which
  [§ 7.2.5](../../package-format-v31.md#725-the-flat-maps-nodes-checks-functions)'s table marks
  "every entry"); `resolve/valid-minimal.json` is a hand-made smallest package instead. Where the
  tables leave a member's inner shape open, the schemas add nothing: `requires.agents` values are
  strings (written as version strings, `"4"`), `lock.libraries` and `lock.runtime` values are
  strings, `lock.catalogues` entries are strings (`outputContracts` also `null`), `warnings` and
  `refusals` entries are `{ sentence, at }`. The entries of `nodes`, `checks`, `renderers`,
  `snippets`, `macros` and `deliverables` fix only the derived members § 7.2.5 marks "every entry"
  (`id`, `parent`, `reads`, `runDependent`, `profileCarrying`, `modelDerived`) and stay open to the
  header members, whose shape is the source schemas', applied by the resolver; `formats.$defs`
  entries are any object (the dialect is checked on the registry's formats, not on the bundle).
- **Readings the compiled-document schemas make.** `lock.package` and `publish-report.package` share
  `resolve`'s `package` (version `vYYYY.MM.N`, as in the manifest). Carets: `requires` ranges are
  `^x.y.z` ([chapter 7 § 7.4.2](../../package-format-v31.md#742-lock-exactly-refuse-by-compatible-range):
  "caret only"); `lock` versions of the evaluator, operations and built-ins are `x.y.z`
  ([§ 7.4.3](../../package-format-v31.md#743-versioning-built-in-operations-and-machinery): semantic
  versions), library and runtime versions are any string. `resolve.bindings` takes the producer
  `generated` only ([chapter 2 § 2.7](../../package-format-v31.md#27-agent-bindings): "at 31 the only
  producer with bindings is `generated`"), and `via` is `format` or `custom`, so the reserved
  `producer` is refused. A function's entry requires its `nodes` map (§ 7.2.5: "each function, with
  its own flat `nodes` map") and is otherwise open, since chapter 4 owns its other members. An
  input's `description` is the manifest's written form (lines or `null`), where
  [§ 7.2.3](../../package-format-v31.md#723-inputs) says "lines or `null`" and the abridged example
  shows only `null`.
- **Readings the design's tables do not list.** `publish-report.schema.json` gives a test's
  `durationMs` `"minimum": 0` (a duration is not negative; the member table says only
  "milliseconds"). `resolve.schema.json` gives `needs.profile` `"uniqueItems": true` (a field is
  named once, and the table says "sorted"), and `bounds.schema.json` does the same for the id arrays
  `windowsReservedIds` and `reservedIds` (they are sets). `resolve.schema.json` gives
  `package.version` the pattern `^v\d{4}\.(0[1-9]|1[0-2])\.[1-9]\d*$`, the shape of the manifest's
  `vYYYY.MM.N` (the design shows examples and does not print a pattern).
- **Four sentences of the member tables are coupled in the schemas:** `publishedAtUtc` is `null`
  when `outcome` is `refused`; `refusals` is `[]` when it is `published`; a test's `firstMismatch`
  is `null` when its `result` is `pass`; a migration text's `explanation` is `null` unless
  `expected` is true. The tables do not say the converse (that a published report has a time, or
  that a failing test has a mismatch), so the schemas do not.
- **`migration-report.json`'s top level.**
  [Chapter 10 § 10.11](../../package-format-v31.md#1011-the-migration-report) names four things (the
  old and new versions, the hand edits, the compared texts) and fixes only the entry's members. The
  members `oldVersion`, `newVersion`, `handEdits` and `texts` are this repository's names; the two
  versions are strings with no pattern, since the design does not say whether they are package
  versions or spec versions.
- **The registry's own files.** The schemas of `bounds.json`, `constants.json`, `profile.json`,
  `sentences.json` fix shape, not values: the `constants` and `sentences` check groups pin the
  values and the rows. `agents.json` and `bindings.json` live in the agents catalogue; their
  schemas are here and are shown by copies of the catalogue's files. A binding's producer key is
  `generated` only (as for `resolve`); an attested version key is digits; `agentVersion` is an
  integer where `requires.agents` writes the same version as a string.
- **`conformance/index.json`'s schema**
  ([`conformance-index.schema.json`](../schemas/conformance-index.schema.json)) is this
  repository's (`{ specVersion, families: [{ id, path, about, exportedBy, cases }] }`); the `self`
  group of `scripts/check-v31.py` judges the file, and the `conformance` group compares it with
  chapter 12's table.
- **Rules the design hands to "v30 §".** The design's expressions and loops parts say several rules
  are "as v30 § 2.2", "§ 2.4", "§ 2.5", "§ 3.1", "§ 3.2" and "§ 3.4" (alignment by path,
  `item.parent`, an empty list, how a `while` runs, the pass object, `until` and `max`) and give
  `pass`'s type as "as v30 § 3.2". The normative text has no 30 to lean on, so
  [chapter 4](../../package-format-v31.md#4-loops-and-functions) restates them from
  `package-format-v30.md` (the pass object's members, item paths, one count per loop instance,
  `pass.….node.<id>` at any depth, no edge for an earlier pass), and
  [chapter 3](../../package-format-v31.md#3-expressions) types `pass.node.<id>` as the named node's
  format. These are the text's readings of v30, not words of the design.
- **A call's `producer`.** The design's member table for a `call`
  ([chapter 4 § 4.7.7](../../package-format-v31.md#477-the-call-node)) lists no `producer`, while its
  own example writes `"producer": "computed"` and
  [chapter 1 § 1.5.2](../../package-format-v31.md#152-the-members-by-file) lists it for a `call`. The
  text follows chapter 1 (every node writes it).
- **Refusals the dialect names without a sentence.**
  [Chapter 5 § 5.2.1](../../package-format-v31.md#521-statements) refuses the `for` options
  `limit:`, `offset:` and `reversed`, and `for.rindex`, `for.length` and `for.changed`, but its
  refusals list ([§ 5.11](../../package-format-v31.md#511-refusals)) gives them no sentence (R-D1
  names the statements it refuses, R-D6 a `for` over a non-list). Chapter 5 and
  [`scriban-dialect.md`](../scriban-dialect.md) state the refusal and mark the sentence as missing.
- **Refusal labels repeat across chapters.** Chapters 5 and 6 both label sentences `R-D1` and onward
  (chapter 5's dialect sentences, chapter 6's deliverable sentences); chapter 6's R-D13 is chapter
  5's R-D8. The text writes a label alone inside its own chapter and with the chapter ("chapter 5
  § 5.11, R-D8") from the other; the sentence ids in `sentences.json` (`S05-…`, `S06-…`) are
  unambiguous.
- **Chapter 7's publish order.**
  [Chapter 7 § 7.5](../../package-format-v31.md#75-the-publish-pipeline) step 4 lists six writes: the
  source files and `dag.mmd`, then `lock.json`, then the publish report, then `resolve.json` last
  (item 5), and then the "published" stamp last (item 6). Both are called "last"; the text keeps
  both as the design has them, `resolve.json` last of the files and the stamp last of all.
- **The publish note is worded twice (S04-072 and S04-073 beside S09-002 and S09-003).**
  [Chapter 4 § 4.10.2](../../package-format-v31.md#4102-notes-and-warnings-at-publish) words the
  publish note "…could run at once; this engine runs at most \<N\> per job…", and its unbounded note
  "(loop '\<id\>' has no cap over a list known only at run time)", while
  [chapter 8 § 8.8](../../package-format-v31.md#88-the-publish-note) says "\<ceiling\>" and "since
  \<loop key\> has no maxParallel and reads a list of unknown length". Both are published, each under
  its own id. Which wording is the sentence an engine writes is not settled.
- **`versionsRan` is given three shapes.** The design's record part says `versionsRan` takes
  "exactly `lock.json`'s shape" and lists its members flat (`packageFormat`, `dialect`, …,
  `runtime` "(the .NET runtime)" and `unicode` "(its Unicode version)"); its record example writes
  `packageFormat` and `dialect` flat and has no `runtime`; and `lock.json`'s member table
  ([chapter 7 § 7.4.1](../../package-format-v31.md#741-members)) nests them as
  `resolver: { packageFormat, dialect }` and `runtime: { dotnet, unicode }`.
  [Chapter 9 § 9.1](../../package-format-v31.md#91-what-a-31-jobs-record-pins) and the provenance
  contract (`provenance-record.md` §§ 6.3 and 6.14) follow "exactly `lock.json`'s shape", with
  `resolver` and `runtime` nested as the lock nests them. Whether `lock.json`'s `documentVersion`,
  `package`, `resolve` and `catalogues` appear in `versionsRan` is not stated.
- **`publishedBy`'s "`ci` with the tag".**
  [Chapter 7 § 7.9](../../package-format-v31.md#79-the-publish-report)'s member table gives
  `publishedBy` as "`ci` with the tag, `editor`, `api` or `operator-migration`" and does not say how
  the tag is written (inside the string, or beside it). `publish-report.schema.json` admits the four
  bare values, `"ci"` among them, and holds no tag; the shape of a CI publish's value is not settled.
- **A manifest `title` of `null` has no compiled form.**
  [Chapter 1 § 1.3](../../package-format-v31.md#13-the-manifest) lets the manifest's `title` be `null`
  ("`null` shows the ref"), while
  [chapter 7 § 7.2.2](../../package-format-v31.md#722-top-level-members) makes `resolve.json`'s `title`
  "the manifest's title", a string that is never `null`. A package with `title: null` is valid as
  source but cannot compile to a valid `resolve.json`; neither chapter says what the compiled title
  is then.
- **A skipped deliverable's state cannot be expected alone.**
  [Chapter 7 § 7.8.3](../../package-format-v31.md#783-expectations)'s `deliverables` expectation is
  `{ state, text }` or `{ state, hash }`, so every expected deliverable names its composed text or its
  hash. A deliverable skipped by its condition composes nothing, and the text does not say what its
  `text` or `hash` is, so a test cannot expect the state `skipped` on its own.
- **Whether a `markdown_block` renderer escapes what it reads.**
  [Chapter 6 § 6.6.4](../../package-format-v31.md#664-strict-formats) escapes plain text and `string`
  data read into a Markdown deliverable, and
  [chapter 5 § 5.8.3](../../package-format-v31.md#583-where-placing-the-instruction) escapes a
  `plaintext` macro placed in a Markdown node. Neither says whether a renderer whose `format` is `markdown_block` escapes the
  `string` members it reads (`c.term` in `concept_bullets`). The built-in renderers are proven byte
  for byte against the C# renderers on raw Scriban output, with no escaping.
