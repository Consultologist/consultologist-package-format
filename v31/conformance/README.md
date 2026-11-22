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
  a valid and an invalid package for every refusal sentence. On disk, a sentence's case is two
  folders, each an `expect.json` beside a `package/`:

  ```
  refusal-packages/<sentence id>/valid/expect.json
  refusal-packages/<sentence id>/valid/package/manifest.json, nodes/index.json, …
  refusal-packages/<sentence id>/invalid/expect.json
  refusal-packages/<sentence id>/invalid/package/manifest.json, nodes/index.json, …
  ```

  `package/` holds the package's files byte for byte, as an upload gives them to a reader (the
  repository's `.gitattributes` keeps git from changing a byte-order mark or a carriage return
  there). `expect.json` has exactly three members, in this order: `about` (the rule, what the
  invalid package does to break it, and what the valid one does to keep it, in words), `valid` (a
  boolean, `true` in `valid/` and `false` in `invalid/`) and `sentences` (a list of strings: `[]` for
  a valid package; for an invalid one, every sentence the checker gives (the reader, then the type
  rules, then the expression rules), in its order). It is
  written with 2-space indentation, `\n` line ends and a final newline, and writes `'`, `≠`, `–`
  and `…` as themselves. The index lists a case as `<sentence id>/valid` and
  `<sentence id>/invalid`. **The cases are exported by the library's checker and are never written
  by hand:** the exporter runs each package through the reader and, when the reader accepts it,
  through the type rules and, when they accept it, through the expression rules, and writes what they
  said. An invalid
  package breaks its rule alone and gives that one sentence; where a rule cannot be broken without
  another sentence also being given, its `about` says so and `sentences` lists them all.
  `python3 scripts/check-v31.py` (group `refusal-packages`) holds the folders to the index, each
  `expect.json` to this shape, and, for an invalid case whose id is a row of `sentences.json`, each
  of its sentences to the row of some published id and at least one to the case's own row, each row
  read as a pattern in which each `<…>` stands for any text. The `citations` group does not read
  the `package/` folders, which are uploads as a reader receives them.
- **Goldens and vectors** (`operation-goldens`, `printer-goldens`, `renderer-goldens`,
  `dialect-goldens`, `null-vectors`, `text-vectors`, `number-vectors`, `date-vectors`,
  `markdown-escape-vectors`): a case holds an input and the bytes a generator produced for it.
  Chapter 3's six families (`operation-goldens`, `printer-goldens`, `null-vectors`,
  `text-vectors`, `number-vectors`, `date-vectors`) are described in
  [The goldens and vectors of JSON Logic (area 04)](#the-goldens-and-vectors-of-json-logic-area-04),
  and the dialect's three (`dialect-goldens`, `renderer-goldens`, `markdown-escape-vectors`) in
  [The dialect's goldens (area 07)](#the-dialects-goldens-area-07).
- **`compiled-documents`:** a fixture package with its expected `resolve.json` and `lock.json`
  bytes and hashes, its `requires` and `needs`, and its publish report. Area 05 exports the
  first four; each case is a folder holding the package under `source/`, the `toolchain.json` it is
  compiled with, `resolve.json`, `lock.json` and an `about.txt`
  ([The compiled documents (area 05)](#the-compiled-documents-area-05)). The publish report is
  area 11's.
- **`migration-vectors`:** a package at 30 with its expected package at 31 and its notices.
- **`schemas`:** a hand-written instance of one schema, valid or invalid by its file name (next
  section). These are examples, not goldens.

## The refusal packages of the file model (area 02)

Area 02, the parser and file model, exports the cases of the sentences its reader gives: those of
[chapter 1](../../package-format-v31.md#1-files-and-scopes) (`S01-…`), chapter 2's unknown kind
(`S02-007`), and the sentences of [chapter 4](../../package-format-v31.md#4-loops-and-functions)
that a flow node's or a function's own members give, which the file model judges before any type is
known: `S04-009`, `S04-010`, `S04-011`, `S04-012`, `S04-013`, `S04-018`, `S04-019`, `S04-021`,
`S04-022`, `S04-023`, `S04-024`, `S04-031`, `S04-033`, `S04-034`, `S04-041`, `S04-042`, `S04-043`,
`S04-048`, `S04-062`, `S04-067` and `S04-076`: 65 cases, 130 packages. Each invalid package gives
its one sentence. Each side is the smallest package (a manifest, the nine folders, one agent node
and one deliverable) plus only the construct its rule needs (a loop, a while, an if, a case, a
function and its call, a snippet folder, a delivery folder, a computed node, a format or a
renderer), and the invalid side is its valid side with one change.

- **`S01-037` to `S01-039` ship no files.** Their packages would be 513 files, a file of 257 KiB and
  a package over 2 MiB; the library's tests prove them, and the suite does not carry megabytes to
  say three sentences. `S01-040` (a path of 201 characters) and `S01-041` (JSON nested 33 deep) are
  small and ship.
- **Chapter 1's other rows have no case here.** `S01-001` (*"Did you mean 'label'?"*) is the hint
  that ends `S01-023`'s sentence, not a sentence of its own; `S01-004` and `S01-029` need reads or
  the call graph and are later areas' cases; `S01-027` needs only the node's kind and is area 03's.
- **A valid package was valid by the file model only** when area 02 exported it. From area 03 on it
  passes the type rules too (none needed correcting), and it is still not judged on expressions,
  reads or the call graph. A later area
  that finds a `valid` package of area 02 invalid by its own rules corrects the package, and the
  cases are exported again.
- **`S01-017`'s `<parser message>` is this implementation's `line <n>, column <m>`**: the 1-based
  line of the file (a header's first line is the file's line 2) and the 1-based column in
  characters where the JSON stops being valid (where it ends, for an empty or truncated header), as
  in *"The header of 'nodes/plan.md' is not valid JSON: line 2, column 305."* The text does not say
  what the message is, so an outside implementation may word it otherwise; compare that sentence by
  its row, as the check script does.

**This implementation's sentences.** The text gives no sentence for eight rules the reader holds,
so it says its own, under `A02-…` ids that are not rows of `sentences.json`. They are this
implementation's, not [chapter 11](../../package-format-v31.md#11-every-sentence)'s, and each is an
open point for the text, which should give the rule a sentence:

| Id | Sentence | Rule |
|---|---|---|
| `A02-001` | *"\<Declaration> declares '\<member>' as \<what it is>; it is \<what it must be>."* | a member of the wrong JSON type ([chapter 1 § 1.5](../../package-format-v31.md#15-members-every-one-written)) |
| `A02-002` | *"File '\<path>' is not valid UTF-8; save it as UTF-8."* | a file is UTF-8 ([chapter 1 § 1.2.4](../../package-format-v31.md#124-encoding-and-line-endings)) |
| `A02-003` | *"The package has no manifest.json; it holds the package's name, version and inputs."* | the manifest is at the root ([chapter 1 § 1.3](../../package-format-v31.md#13-the-manifest)); this case's invalid package is the one without a `manifest.json` |
| `A02-004` | *"The manifest declares specVersion \<n>; this reader reads 31."* | `specVersion` is 31 ([chapter 1 § 1.3](../../package-format-v31.md#13-the-manifest)) |
| `A02-005` | *"File '\<path>' must hold one JSON object."* | an `index.json`, the manifest, a format and a test are each one JSON object ([chapter 1 § 1.2.1](../../package-format-v31.md#121-which-file-holds-what)) |
| `A02-006` | *"Node '\<id>' is kind \<kind> in a file; a \<kind> is a folder with an index.json."* | a flow node is a folder ([chapter 4 § 4.1](../../package-format-v31.md#41-flow-nodes-are-folders)) |
| `A02-007` | *"Node '\<id>' is kind \<kind> in a folder; a \<kind> node is a file, \<id>.md."* | a leaf node is a file ([chapter 1 § 1.2.1](../../package-format-v31.md#121-which-file-holds-what)) |
| `A02-008` | *"\<subject> has no body; name the nodes that run in nodes."* | a `then`, an `else`, a non-empty branch or a function lists at least one node; `S04-018` and `S04-034` name loops and whiles only ([chapter 4 § 4.5](../../package-format-v31.md#45-branches-if-and-case)) |

## The refusal packages of the types (area 03)

From area 03 on, every case, area 02's included, is held to the type rules of
[chapter 2](../../package-format-v31.md#2-types-and-inputs) as well as the reader. Area 02's 65
cases came out unchanged, their valid packages passing the type rules as well.
Area 03 adds 52 cases, 104 packages, built as area 02's are (the smallest package plus one
construct, here a format file, a second input, a while or an if, and an invalid side that is its
valid side with one change): one for each chapter 2 sentence a package can reach, `S01-027` (a
leaf's `reproducible`, which needs the node's kind) among them, and for ten sentences of this
implementation, `A03-001` to `A03-008`, `A03-010` and `A03-011`, which, like the `A02-…` ones, are
not rows of `sentences.json` and are open points for the text. These chapter 2 sentences have no
package: `S02-018`, `S02-019` and `S02-020`, because finding the reads they judge (a JSON Logic
`var`, a template, a reference string) belongs to the areas that follow; `S02-027`, `S02-035` and
`S02-036`, and this implementation's `A03-009` (an annotation's value), because only a registry or
catalogue format can reach them (a package format whose root is an `anyOf` is refused before any
agent returns it, and the annotations in a package's own or an inline format are `S02-037` and
`S02-038`); `S02-009`, whose words are `S01-028`'s, which has its case; and `S02-011`, because the
three flags follow from what a node reads.

**This implementation's sentences for the types.** The text gives no sentence for eleven rules the
type rules hold, so they say their own, under `A03-…` ids that are not rows of `sentences.json`.
Like the `A02-…` ones, they are this implementation's and each is an open point for the text:

| Id | Sentence | Rule |
|---|---|---|
| `A03-001` | *"Package format '\<id>' is neither an object nor a list; a package defines object and array formats, and refers to built-in and catalogue formats by name."* | a package format whose root is neither an object, a list nor a scalar ([chapter 2 § 2.4](../../package-format-v31.md#24-built-in-and-catalogue-formats)) |
| `A03-002` | *"\<Format> at \<path> refers to #/$defs/\<name>, which the file doesn't define."* | a `#/$defs` reference names a definition of the file ([chapter 2 § 2.6.3](../../package-format-v31.md#263-references-by-bare-id-no-shadowing)) |
| `A03-003` | *"\<Format> at \<path> writes '\<keyword>' as \<what it is>; it is \<what it must be>."* | a keyword of the wrong JSON type ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)) |
| `A03-004` | *"\<Format> at \<path> uses '\<keyword>', which belongs on \<an object \| a list \| a string>."* | a keyword on a schema of another type ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)) |
| `A03-005` | *"\<Format> at \<path> declares no type; write type, $ref or anyOf."* | every schema declares its type ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)) |
| `A03-006` | *"\<Format> at \<path> is an object without '\<keyword>'; every object writes properties, required and additionalProperties: false."* | an object writes all three ([chapter 2 § 2.3.3](../../package-format-v31.md#233-required-additionalproperties-and-the-root)) |
| `A03-007` | *"\<Format> at \<path> is a list without items; write the one schema its items follow."* | a list writes `items` ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)) |
| `A03-008` | *"\<Format> at \<path> writes anyOf with \<n> member; a union has two or more."* | a union has two or more members ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)) |
| `A03-009` | *"\<Format> declares \<keyword> '\<value>' (accepted: \<list>)."* | `contentMediaType` is `text/plain` or `text/markdown`, `x-markdown` is `block` or `inline` ([chapter 2 § 2.5.1](../../package-format-v31.md#251-the-annotations)); no package reaches it, so it has no case |
| `A03-010` | *"\<Subject> lists null but is not nullable; write "type": ["string", "null"], or remove null."* | an enum lists `null` only on a nullable string ([chapter 2 § 2.3.2](../../package-format-v31.md#232-one-way-to-write-nullable)) |
| `A03-011` | *"Format '\<id>' expands to more than 10,000 schemas through the formats it refers to; refer to fewer."* | a format's full form, every reference inlined, can be built ([chapter 2 § 2.3.1](../../package-format-v31.md#231-the-keywords)) |

The count `A03-011` makes is this implementation's: each schema object visited while the references
are inlined, a referenced format counted at each place it is referenced. Another implementation may
count otherwise, so only the far side of the limit is meant by its case: its invalid package is past
10,000 by this count, and its valid package is under the limit, not on it.

## The refusal packages of the expressions (area 04)

From area 04 on, every case, areas 02 and 03's included, is held to the expression rules of
[chapter 3](../../package-format-v31.md#3-expressions) as well: every JSON Logic rule a package writes (a condition, a
`while`, an `until`, a computed node's `expression`) is checked against its written form, what its
site may read and the types of what it reads. Five earlier cases changed, and only in one
expression: the valid and invalid packages of `A02-008`, `S01-036`, `S02-013`, `S02-016` and
`S04-041` tested an `if` by comparing the input `consult_draft`'s Markdown with a literal (`!==` or
`===` with `""`, or `===` with `"full"`), which `S03-002` refuses; they now test it with `blank`.
Their sentences are unchanged, and every other earlier package is byte for byte as it was.

Area 04 adds 46 cases, 92 packages, built as the earlier areas' are (the smallest package plus only
what the rule needs, here a second input of the needed format, a package format, a computed node,
a check or a check loop, or a macro, and an invalid side that is its valid side with one change):
one for each chapter 3 sentence a package can reach, `S03-002` to `S03-035`, `S03-042` and
`S03-043`, and one for each of this implementation's `A04-001` to `A04-010`, which, like the
`A02-…` and `A03-…` ones, are not rows of `sentences.json` and are open points for the text. Each
invalid package gives its one sentence. Most rules are written as the agent node `plan`'s `if`,
reading the inputs; `S03-020` and `S03-021` are a deliverable's `if`, `S03-022` a macro's,
`S03-030` a check's.

- **Reads through `node`, `check`, `item`, `pass` and `param` are not judged yet.** Which nodes,
  checks, items, passes and parameters a site can see, and their types, are the compiled package's
  (area 05), so until then such a read is accepted with no type, and only chapter 3's own site rules
  are said of it (a deliverable's `if` reading a node's `.content` or a check, a macro's `if`
  reading `param`). So the cases build their rules on inputs and run facts, whose types are known.
  A few valid packages read through those roots (`S03-020`'s `node.plan.value`, `S03-030`'s check
  loop over `item.value` and `check.notes_checked.items`); area 05, judging them, corrects any it
  finds invalid, and the cases are exported again.
- **These chapter 3 sentences have no package.** `S03-001` (*"skipped: … is false"*) is the reason
  a decision's record gives, not a refusal. (`S03-036` and `S03-044`, which follow from the three
  flags of [§ 3.4.4 to § 3.4.6](../../package-format-v31.md#344-run-dependence-is-contagious), are said by the
  resolver, area 05, and have their cases there.) `S03-037` and `S03-038` are warnings and `S03-039` a note: a package that gets them is
  accepted, and `expect.json` lists refusals only. `S03-040` and `S03-041`, and this
  implementation's `A04-011`, are failures at run time
  ([§ 3.11.3](../../package-format-v31.md#3113-failures-at-run-time)), said when a rule is evaluated, never at publish.
- **Words the text leaves to the implementation.** Where a sentence shows `<path> (<format>)` and the
  operand is not a `var`, this implementation writes the operand's printed text
  ([§ 3.8](../../package-format-v31.md#38-the-printer)) for `<path>`, as in *"… compares size(input.consult_draft.content)
  (integer) with "0" (string); …"*. `S03-031`'s `<reason>` is one of this implementation's fixed
  phrases (*"'\\d' at character 1 is not an escape of I-Regexp"*), and `S03-043`'s is *"it needs too
  large an automaton"* when .NET refuses the automaton's size, else *".NET does not accept it"*,
  never .NET's own message, which is localised. `S03-043`'s pattern, `(a{100}){100}`, is within
  the other bounds and refused by .NET's non-backtracking engine as too large; an implementation on
  another engine may word the reason otherwise: compare that sentence by its row, as the check
  script does.

**This implementation's sentences for the expressions.** The text gives no sentence for eleven
rules the expression checker holds, so it says its own, under `A04-…` ids that are not rows of
`sentences.json`. Like the `A02-…` and `A03-…` ones, they are this implementation's and each is an
open point for the text:

| Id | Sentence | Rule |
|---|---|---|
| `A04-001` | *"\<site> gives \<operation> \<operand> (\<format>); \<operation> takes \<expected>."* | each operand is of a type its operation takes ([chapter 3 § 3.5.1](../../package-format-v31.md#351-standard-json-logic-operations), [§ 3.7](../../package-format-v31.md#37-typing)); `<expected>` is one of `numbers`, `booleans`, `a condition`, `text`, `text or a list`, `a list of its type, or text`, `a string to find`, `strings, numbers and plain text`, `dates`, `a date and a number`, `two concept_list values`, `a list of check results` |
| `A04-002` | *"\<site> compares \<a> (\<format>) with \<b> (\<format>); = and ≠ compare two values of one type."* | `===` and `!==` compare two data values of one type, or either `null` ([chapter 3 § 3.5.1](../../package-format-v31.md#351-standard-json-logic-operations)) |
| `A04-003` | *"\<site> mixes \<format> and \<format> in \<the branches of an if \| a list>; they have one type."* | an `if`'s branches, and a list's elements, have one type ([chapter 3 § 3.7](../../package-format-v31.md#37-typing)) |
| `A04-004` | *"\<site> writes an object with \<n> members where a rule is expected; an operation is an object with one member, and object builds an object."* | an operation is an object with exactly one member ([chapter 3 § 3.2.1](../../package-format-v31.md#321-shape)) |
| `A04-005` | *"\<site> writes var with \<what it is>; var takes one path, written as text."* | `var` takes one string, the path ([chapter 3 § 3.2.2](../../package-format-v31.md#322-the-canonical-form)) |
| `A04-006` | *"\<site> reads '\<path>', which is not a path; a path is a root, then names joined by dots."* | a path is dot-separated non-empty segments ([chapter 3 § 3.2.2](../../package-format-v31.md#322-the-canonical-form)) |
| `A04-007` | *"\<site> writes object with \<what it is>; object takes one object, from field names to rules."* | `object` takes one object ([chapter 3 § 3.2.2](../../package-format-v31.md#322-the-canonical-form)) |
| `A04-008` | *"\<site> builds an object where no format gives its fields; object builds the value of a computed node."* | `object`'s fields are checked against the computed node's format, so it is written where a format is expected: a computed node's value, through an `if`'s branches, a list's elements and its own fields ([chapter 3 § 3.5.4](../../package-format-v31.md#354-custom-structural-and-check-operations)) |
| `A04-009` | *"Computed node '\<id>' builds \<format> with \<field> as \<format>; the format declares it \<format>."* | each field of an `object` fits its property, and is `null` only where the property is nullable ([chapter 3 § 3.5.4](../../package-format-v31.md#354-custom-structural-and-check-operations)) |
| `A04-010` | *"\<site> gives \<operation> a \<operand> that is \<what it is>; \<operand> is written as text."* | a `pattern`, a `word`, a `failWith` and a `missing` path are literal strings ([chapter 3 § 3.5.3](../../package-format-v31.md#353-matches-and-has_word), [§ 3.5.4](../../package-format-v31.md#354-custom-structural-and-check-operations), [§ 3.5.1](../../package-format-v31.md#351-standard-json-logic-operations)) |
| `A04-011` | *"\<site> \<member> could not be evaluated: \<detail>."* | the evaluator declines a rule outside the format and never throws ([chapter 3 § 3.9](../../package-format-v31.md#39-the-evaluator)); said at run time, so it has no case |

## The refusal packages of the resolver (area 05)

From area 05 on, every case is held to the resolver as well: before its expressions are checked,
every read through `node`, `check`, `item`, `pass` and `param` is resolved to the one thing its place
can see ([chapter 1 § 1.9](../../package-format-v31.md#19-scopes-and-keys),
[chapter 4 § 4.4](../../package-format-v31.md#44-reading-across-levels)) and typed by it, so a read
that area 04 accepted with no type is now judged. Fourteen earlier cases changed, and only in what
they read:

- the valid and invalid packages of `A02-007`, `S01-003`, `S01-012`, `S01-036`, `S02-015`, `S04-009`
  to `S04-013`, `S04-031`, `S04-033` and `S04-034` hold the while `refine`, whose `while` compared
  its judge's `plaintext` value with `"good"`, which `S03-002` refuses once the judge is typed; it
  now runs again while the judge has something to say (`! blank(node.judge.content)`), and the
  judge's prompt asks for that;
- the packages of `S01-020` hold a computed node that counted `node.plan.value.sections`, which the
  smallest package's `plaintext` plan does not have (`S03-014`); it now measures the plan's text.

Their sentences are unchanged. The valid packages of `S03-020` and `S03-030`, which read through
those roots, resolve as they are.

Area 05 adds 7 cases, 14 packages, built as the earlier areas' are: one for each sentence of the
reads across levels a package can reach, `S04-036` to `S04-040` (what a pass reads, a node inside a
loop read from outside it, `item.parent` in an outermost loop) and `S04-050` and `S04-051` (a
function reads only its parameters). Each invalid package gives its one sentence.

The resolver then types each loop's source and its `itemLabel`
([chapter 4 § 4.2.2](../../package-format-v31.md#422-what-a-loop-iterates),
[§ 4.2.7](../../package-format-v31.md#427-itemlabel-naming-items)). Ten earlier cases changed, and only
in what their loop iterates: the valid and invalid packages of `S01-002`, `S01-005`, `S01-011`,
`S04-018`, `S04-019` and `S04-021` to `S04-024` hold the for `sections`, and those of `S01-040` two
nested loops, which iterated `node.plan.value.sections` (and the inner one `item.value.points`), which
the smallest package's `plaintext` plan does not have (`S03-014`). They now iterate a new required
input, `sections`, a list of sections each with a `title` and its `points`; `S04-023`'s `until`, which
read the section's `kind`, reads its `title`. Their sentences are unchanged.

It adds 10 cases, 20 packages: `S04-025` to `S04-030` (a source that is not a list, `item.value` with
no loop around it, a node inside another loop, and an `itemLabel` that is not a field, may be null, or
is not a string), `S04-017` (an `in` written as an expression, said in place of `A02-001`), `S02-018`
(an input read bare, which no case reached before), `S04-035` (a while's body node that is neither
returned nor read; judged only when no node in the while is an agent or a rendered node, whose
templates' reads are this implementation's area 07's), and one for this implementation's `A05-001`,
which, like the `A04-…` ones, is not in `sentences.json`:

| Id | Sentence | Rule |
|---|---|---|
| `A05-001` | *"\<Kind> '\<id>' \<member> '\<text>' is not a reference; a reference is a root, then names joined by dots."* | a loop's `in` is a reference string, a root then names joined by dots, with no position ([chapter 4 § 4.2.2](../../package-format-v31.md#422-what-a-loop-iterates)) |

There is no `A05-002`: a reference naming a member its thing does not have is `S03-014`, as it is in
an expression, so one fault has one sentence wherever it is written. The area's sentences are
`A05-001` and `A05-003` to `A05-005`, each in a table of this section.

The resolver then types each `case`'s subject as a loop's source is, and holds the branches' values to
it ([chapter 4 § 4.5.2](../../package-format-v31.md#452-case)). Four earlier cases changed, and only in
what their case switches on: the valid and invalid packages of `S04-042`, `S04-043`, `S04-048` and
`S04-076` hold the case `route`, which switched on `node.plan.value.kind`, which the smallest
package's `plaintext` plan does not have (`S03-014`). It now switches on a new required input,
`note_kind`, an enum of `narrative` and `omit`. Their sentences are unchanged.

It adds 5 cases, 10 packages: `S04-044` (a subject that is not an enumerated string), `S04-045` (a value
that is not one of the subject's), `S04-046` (a value in two branches), `S04-047` (a value no branch
lists, with no `else`) and `S04-075` (a subject that can be null, with no `else`). An `A05-001` or
`S04-017` written in a `case` is said as it is for an `in`, and has no case of its own.

The resolver then binds every `call` to its function, types each argument against its parameter,
holds each function's `ret` and `uses`, refuses recursion and measures call depth
([chapter 4 § 4.7.3](../../package-format-v31.md#473-uses-declared-definitions),
[§ 4.7.6](../../package-format-v31.md#476-one-ret-always-valued-one-format),
[§ 4.7.7](../../package-format-v31.md#477-the-call-node),
[§ 4.7.8](../../package-format-v31.md#478-depth-and-recursion)). Two earlier cases changed, and only in
which node reads: the valid and invalid packages of `S04-050` and `S04-051` gave the function's `ret`,
`patient_draft`, an `if`, which may skip it (`S04-058`); the `if` is now on a second node of the
function, `draft_note`. Their sentences are unchanged but for the node they name.

It adds 17 cases, 34 packages: `S04-064` to `S04-066`, `S04-068` and `S04-070` (a call naming no
function, leaving out a parameter or passing one the function does not take, an argument of another
type, a call's format that is not its function's), `S04-069` (a parameter bound to `profile.signature`
read by a condition inside the function), `S04-057` to `S04-061` (a function's `ret` that is an `if`
with no `else`, that may be skipped inside an `if`, that is a `case` with an empty branch, whose
branches return two formats, or whose format is not the function's), `S04-052` and `S04-053` (a
package snippet a function reads without listing it in `uses`, and an own snippet that shares its id
with a listed one), `S04-054` to `S04-056` (a ring of functions, a function calling itself, and a chain
of calls sixteen deep), and one for this implementation's `A05-005`:

| Id | Sentence | Rule |
|---|---|---|
| `A05-005` | *"Call '\<id>' with \<param> is \<what it is>; an argument is a reference, written as text, or null."* | each argument of a `call` is a reference string or the literal `null` ([chapter 4 § 4.7.7](../../package-format-v31.md#477-the-call-node)) |

A `with` value written as an object or a list is `S04-017`, said in place of `A02-001` as for an `in`;
a call's body stays the reader's `S01-020`. `S04-074` (a format a function lists in `uses` and never
names) is a warning, and a package that gets it is accepted, so it has no case.

The resolver then works out what each value is made from, and from that `reproducible` and the three
flags ([chapter 2 § 2.1.1](../../package-format-v31.md#211-reproducible),
[chapter 3 § 3.4.4 to § 3.4.6](../../package-format-v31.md#344-run-dependence-is-contagious),
[chapter 4 § 4.1](../../package-format-v31.md#41-flow-nodes-are-folders)), and holds each header to them. A flag
passes along what a value is made from (a computed node's expression, a body's reads, a call's
arguments and its function's result, a flow node's `ret`, a loop's source), never through a condition
or from an earlier pass. What a Scriban body reads is this implementation's area 07's: until it is
known a body's reads are unknown, not empty, and a flag that depends on one is not judged, so an
agent's `runDependent` and `profileCarrying` are taken as written.

It adds 5 cases, 10 packages: `S03-036` (a computed node that declares `modelDerived` false but reads
an agent's output), `S04-015` (a while of computed nodes that declares `reproducible` false),
`S04-016` (a loop that returns an agent's output and declares `modelDerived` false), `S03-044` (a
condition that reads the result of a call passed `profile.signature`), and one for this
implementation's `A05-003`:

| Id | Sentence | Rule |
|---|---|---|
| `A05-003` | *"Node '\<a>' reads node '\<b>', which reads node '\<a>': nodes can't read each other in a circle. Break the circle."* | what a node reads is computed before it, so nodes cannot read each other in a circle ([chapter 4 § 4.4](../../package-format-v31.md#44-reading-across-levels)); a longer circle is named in full |

A read of this pass's node, `pass.node.<id>`, is a dependency edge as `node.<id>` is
([chapter 4 § 4.3.3](../../package-format-v31.md#433-what-a-pass-reads)), so publish refuses what the
engine could not load: two nodes of one `while` body that read each other through it, or a node that
reads through it the flow node enclosing it, are a circle (`A05-003`); a node inside an inner loop of
the body, read through it from outside that loop, is a list from there (`S04-039`). One pass back
(`pass.previous.node.<id>`, `pass.history`) is no edge. Both sentences keep their cases.

`S04-063` (a macro placed in a function whose `if` reads a node the function does not have), and the
rules of `S04-035`, `S04-052`, `S04-069` and `S04-074` for what bodies read, need what a body places
and reads, so no package reaches them through the checker yet; `S04-035`, `S04-052` and `S04-069`
have their cases from what headers read.

The formats bundle of `resolve.json` adds one case, 2 packages, for this implementation's `A05-004`:
a function's own format is bundled under `<function>__<format>`, and the resolver refuses a function
whose own format would take a key the package already uses:

| Id | Sentence | Rule |
|---|---|---|
| `A05-004` | *"Function '\<f>' format '\<id>' is compiled as '\<f>__\<id>', which the package already uses: rename one."* | a function's own format is bundled as `<function>__<format>`, a key no other format the package uses may have ([chapter 7 § 7.2.4](../../package-format-v31.md#724-formats-and-bindings)) |

The notes of [chapter 4 § 4.10.2](../../package-format-v31.md#4102-notes-and-warnings-at-publish)
(`S04-072`, `S04-073`, `S04-079`, `S04-080`) are measured against an engine's limits and never
refuse, so they have no package.

## The goldens and vectors of JSON Logic (area 04)

Area 04, JSON Logic, exports six families for [chapter 3](../../package-format-v31.md#3-expressions):
22 files of goldens and 16 of vectors, 606 cases. Each holds a rule written as a package writes it
and what this implementation's evaluator or printer gave for it.

| Family | Files (cases) | Holds |
|---|---|---|
| `operation-goldens` | one per custom operation of [§ 3.5.2 to § 3.5.5](../../package-format-v31.md#352-custom-text-operations), `<name>.json` (18 files, 154 cases) | every branch of each operation's meaning, and a value of the wrong kind; `plain.json` holds the Markdown conversion's cases |
| `printer-goldens` | `operations.json` (39), `precedence.json` (26), `literals.json` (28), `refused.json` (7) | every operation printed once; precedence and parentheses; every literal form, and the forms that keep the tree ([§ 3.8](../../package-format-v31.md#38-the-printer)); what the printer writes for a rule the written form refuses (an operand count its form cannot show, an operation outside [§ 3.5](../../package-format-v31.md#35-the-operations), a bare operand, `var` of a number, an object that is not a rule) |
| `null-vectors` | `standard.json` (62), `text.json` (16), `structural.json` (8), `dates.json` (10), `absence.json` (27) | a `null` operand in each position of every row of [§ 3.5.1 to § 3.5.5](../../package-format-v31.md#35-the-operations); `absence.json` holds every row of [§ 3.6.1](../../package-format-v31.md#361-what-a-read-gives), the pitfall of [§ 3.6.2](../../package-format-v31.md#362-the-null-rules) and the truthiness of [§ 3.6.4](../../package-format-v31.md#364-truthiness) |
| `text-vectors` | `lower.json` (15), `trim.json` (30), `words.json` (30), `has_word.json` (41) | case pairs outside ASCII (`Ω`, `İ`, `ẞ`, `Ǆ`, Cherokee, the Deseret letter U+10400) for `lower`; every `White_Space` character, and four look-alikes that are not, for `trim` and `words`; each category of word character beside the word, and ten that are not, for `has_word` |
| `number-vectors` | `arithmetic.json` (25), `non-finite.json` (13), `integers.json` (13) | IEEE results (`0.1 + 0.2`), overflow and division by zero giving `null`, a whole result written without a fraction, `1.0 === 1` ([§ 3.7](../../package-format-v31.md#37-typing)) |
| `date-vectors` | `days_between.json` (17), `years_between.json` (15), `add_days.json` (16), `comparisons.json` (14) | every 29 February case of [§ 3.5.5](../../package-format-v31.md#355-date-operations), the bounds of years 0001 and 9999, malformed dates |

**A file** is `{ "about", "cases" }`: what the group pins, and its cases. **A case** is, by family:

- a vector (`null-vectors`, `text-vectors`, `number-vectors`, `date-vectors`):
  `{ "about", "rule", "data", "result" }`. Evaluate `rule` on `data` and compare the value with
  `result` as JSON (a number by its value: `1` and `1.0` are one number).
- an operation golden: `{ "about", "rule", "data", "output" }`. `output` is a string, the result's
  canonical JSON ([RFC 8785](https://www.rfc-editor.org/rfc/rfc8785): members sorted, numbers in
  their shortest form): write the value canonically and compare the bytes.
- a printer golden: `{ "about", "rule", "text" }`. Print `rule` and compare the text exactly; the
  text parses back to exactly `rule` ([§ 3.8](../../package-format-v31.md#38-the-printer)), which the
  library's tests check for every case but those of `refused.json`. Those rules have a fault of the
  written form: the printer still writes them (it is total), the text is shown in refusals, and it
  is not parsed back.

`data` is one object whose members are the roots a rule reads (`input`, `node`, `check`, `pass`,
`run`, …), as an engine builds them: an unsupplied input is
`{ "value": null, "content": null, "title": null }`, a node that did not complete
`{ "value": null, "content": null, "state": "skipped" }`; `{}` when the rule reads nothing. Every
`plain` in a case converts, as for an operand that is Markdown: whether an operand is plain text,
returned unchanged, is known from its format at publish, not from the rule and its data, so that
branch has no vector. A case's `about` names the row it pins (*"§ 3.5.1 `<`: false when the first
operand is null."*), by this document's sections; a `D<n>` is one of this implementation's
decisions, below. Each file is written with 2-space indentation, `\n` line ends and a final newline,
and writes every character outside ASCII as itself, one outside the Basic Multilingual Plane too
(`😀`, `𐐀`); ASCII control characters are JSON escapes (`\t`, `\u000B`). The index lists a
family's cases as its file names. **The cases are exported by the library's evaluator and printer
and are never written by hand:** the exporter runs each rule and writes what it gave.
`python3 scripts/check-v31.py` (group `vectors`) holds each family's files to the index (and the
operation goldens to the custom operations, one file each), each file to `{ about, cases }` and each
case to its family's members, in that order.

**What an outside implementation must match.** The text leaves these to the implementation; the
vectors pin this implementation's choices, and an implementation that chooses otherwise fails them:

| Decision | What the vectors pin |
|---|---|
| D11, `matches` | the pattern is translated to .NET's non-backtracking engine so that it counts code points (`.`, a class, a quantifier, `{n}` each take one character outside the Basic Multilingual Plane); `^` and `$` are literals; a Unicode category is judged on Basic Multilingual Plane code points only, so `𐐀` (U+10400) is in no `\p{L}` and in every `\P{L}` |
| D13, `plain` | `plain_conversion` 1.0.0 is Markdig's `Markdown.ToPlainText` with the `UseAdvancedExtensions` pipeline, then `\r\n` and `\r` turned to `\n`, and spaces, tabs and line breaks at the very end removed. Everything else is Markdig's: a table's cells run together, separated by spaces |
| D18, run data that escaped validation | an operand of a kind its operation does not take is read as `null` by that operation (`"3" + 1` is `null`, `lower(5)` is `null`, `blank(5)` is `true`, `5 < "a"` is `false`); nothing is coerced; `<`, `>`, `<=`, `>=` compare two numbers, or two strings that are both dates, and are `false` otherwise; a date that is not `YYYY-MM-DD` in years 0001 to 9999 is `null` |
| D19, numbers | `cat` writes a number in its RFC 8785 form (`1e+21`, `1e-7`, `2.0` as `2`); a result that is not finite is `null`; `%` has the sign of the dividend |
| D20, Unicode | whitespace is Unicode `White_Space`; `lower` is .NET's `ToLowerInvariant`, the invariant culture's simple mapping, which leaves `İ` (U+0130) as it is and lowers `Σ` to `σ` wherever it stands; `size` counts code points; a word character is a letter, a mark, a decimal digit or connector punctuation, judged per code point (so `𐐀` beside a word is a word character for `has_word`). The vectors carry no runtime or Unicode version of their own: `lock.json` records them |
| D21, check operations | `terms_subset`'s operands are `concept_list` values; `null`, or anything else, is an empty list; `uncovered` and `untested` are `null` when empty. For `all_pass` and `count_pass`, an element with a `state` is judged when its `state` is `completed`, on its `value`; an element without one is judged as it is; an element that is not an object, or whose judged value has no boolean `pass`, is not judged |
| D23, the printer | one-operand `-` on a number literal prints `-(1)` (a negative literal prints `-1`); a child of a function form, an array or an `object` is never parenthesised; a `var` path that is not dot-joined identifiers, or whose first segment is a printer word (`true`, `false`, `null`, `not`, `and`, `or`, `in`, `if`, `then`, `else`), prints as `var("<path>")`; an `object` field that is not an identifier prints as a JSON string; an empty `object` prints `{}`; the printer is total: an operation whose operand count its form cannot show, an operation outside § 3.5, or one with a bare operand, prints as `name(a, b)`, and an object that is not a rule as its canonical JSON |

**What has no vector.** `matches` over text of more than 1 MiB fails the node that owns the
condition (`S03-040`), and a condition that yields no boolean fails it too (`S03-041`): both are
run-time failures, said as sentences ([§ 3.11.3](../../package-format-v31.md#3113-failures-at-run-time)), and a vector
holds a value, so neither has one; nor has this implementation's `A04-011` (a rule the evaluator
declines). The typing of [§ 3.7](../../package-format-v31.md#37-typing) is judged at publish, and its refusals are
`refusal-packages` cases, above.

## The compiled documents (area 05)

Area 05, the resolver and the lock, exports 3 cases of the `compiled-documents` family
([chapter 7](../../package-format-v31.md#7-the-compiled-documents)), each built after an example of
chapter 4, not the example itself: `nested-note` (two nested loops and a while, after
[chapter 4 § 4.2.8](../../package-format-v31.md#428-examples-migrated) and
[§ 4.3.5](../../package-format-v31.md#435-example-migrated)), `conditional` (a `case` with an empty
branch and two `if`s inside loops, after [§ 4.5.4](../../package-format-v31.md#454-examples-migrated))
and `functions` (a function called in a loop over a snippet folder, a check loop over the loop's
`.items`, and the deliverable `deliverable.emr.consult` gated by a check, in a delivery folder that
delivers to two kinds as one zip, after [§ 4.7.11](../../package-format-v31.md#4711-example-a-made-up-package),
with two agents the example does not have). Area 08 adds a fourth, `checked-note` (a check loop over a
production loop's `.items`, an aggregate over it, and a gate check that reads the composed note's
`.content`, beside an ungated patient letter in a delivery folder delivered by email and PDF, after
[chapter 6 § 6.3.4](../../package-format-v31.md#634-example-a-made-up-package), cut down; see
[The checks (area 08)](#the-checks-area-08)). A case is a folder:

```
compiled-documents/<case>/source/manifest.json, nodes/index.json, …
compiled-documents/<case>/toolchain.json
compiled-documents/<case>/resolve.json
compiled-documents/<case>/lock.json
compiled-documents/<case>/about.txt
```

`source/` holds the package's files byte for byte, as an upload gives them. `toolchain.json` is the
toolchain that publishes it, in `lock.json`'s names (`packageFormat`, `dialect`, `libraries`,
`evaluator`, `runtime`, `catalogues`), written by hand so that no machine's patch level moves a case:
Scriban 7.2.5, Markdig 0.41.3, both Corvus libraries 5.8.12, .NET 10.0.0 and Unicode 16.0.
`resolve.json` and `lock.json` are the bytes publish gives for that source with that toolchain and
no publish limits (so no ceiling note): canonical by RFC 8785, UTF-8, one line, no final newline.
`about.txt` says what the package holds and gives the two documents' hashes. The index lists a case by
its folder's name. **The cases are exported by the library's publish step and are never written by
hand;** the library's tests hold the same bytes as goldens. `python3 scripts/check-v31.py` (group
`compiled-documents`) holds the folders to the index, each folder to its five entries, `resolve.json`
to [`resolve.schema.json`](../schemas/resolve.schema.json) and `lock.json` to
[`lock.schema.json`](../schemas/lock.schema.json), and recomputes `lock.json`'s `resolve.hash` from
`resolve.json`'s bytes.

**What the cases pin that the text leaves open.** An outside implementation that chooses otherwise
gives other bytes:

- **What a Scriban body reads** is what the dialect ([`scriban-dialect.md`](../scriban-dialect.md))
  finds in it as written (`{{ item.value.title }}` reads `item.value.title`), with the reads of what it
  places (a part's text, a snippet's body, a macro's instruction and body) counted as its own
  ([chapter 5 § 5.3.2](../../package-format-v31.md#532-snippet-and-macro-bodies-are-templates)), so
  every body is known and the documents are complete (area 07; see
  [The dialect (area 07)](#the-dialect-area-07)).
- **`reads`** of a read through `node`, `check`, `input` or `param` is the key and its first member
  (`node.plan.value`, `input.consult_draft.content`), and so is a check's read of a deliverable
  (`deliverable.note.content`, the key the longest that names one); one through `item`, `pass`, `run`, `profile` or
  a snippet is the path as written (`item.value.title`, `snippet.standards`); distinct, sorted. A flow
  node's `reads` are its header's (its source, its conditions), not its `ret`'s.
- **Keys.** A `node.<id>` or `check.<id>` at the start of a reference or a `var` path is written with
  the key it resolves to where it is read (`node.judge.value.verdict` in the while `refine` is
  `node.refine.judge.value.verdict`); inside a function keys are the function's own
  (`node.apply_instructions`). A flow node's `nodes` lists its children's keys; an `if`'s `then` and
  `else` and a `case`'s `branches` keep their written shape with keys inside, and the node's own `ret`
  is `null`.
- **Functions** are entries of `functions` with their index's members as written, `inputOrder`,
  `ret`, `body` (the top-level keys), their own `nodes`, `renderers`, `snippets` and `macros` maps,
  `formatHash` and `typeHash`, and the members
  [§ 7.2.5](../../package-format-v31.md#725-the-flat-maps-nodes-checks-functions) puts on every
  entry: `id` (the function's id), `parent` (`null`), `reads` (what its own entries read from outside
  its nodes: its `param.*` reads and its definitions', sorted) and the three flags of its `ret` with
  its parameters reading nothing (what a call takes from the function before its arguments'). It has
  no `reproducible`: a call's is held against its `ret`'s, which is in `nodes`.
- **`graph`.** `order` is level by level: a flow node comes before its body, each level in a
  topological order of the edges lifted to it, ties by source order (inputs, `nodes/`, `checks/`,
  deliverables). The order is topological over every edge but `gates`, since a gate check may read the
  deliverable it gates ([chapter 6 § 6.7](../../package-format-v31.md#67-gating-and-outcomes)): a gate that reads it
  comes after it, by the `reads` edge from the deliverable, and a gate that reads only nodes keeps its place. There are no edges between a function's own nodes, only `calls` from
  `function.<id>` to each call; a loop over another loop's `.items` has a `for` and an `aligned`
  edge from it.
- **Deliverables** carry their folder's `delivery` and `bundle`, as the `index.json` of the folder
  that holds them writes them (`[]` and `null` when it writes none): delivery is declared on folders
  only, with no inheritance ([chapter 6 § 6.8](../../package-format-v31.md#68-delivery)), and the
  text embeds "every piece of package content" in `resolve.json`
  ([chapter 7 § 7.2.1](../../package-format-v31.md#721-whats-in-it-and-what-isnt)), the only file the
  engine loads; its tables
  ([§ 7.2.2](../../package-format-v31.md#722-top-level-members),
  [§ 7.2.5](../../package-format-v31.md#725-the-flat-maps-nodes-checks-functions)) give these
  members no place. An entry per delivery folder, as snippet folders have, was not chosen: the root
  `deliverables/` folder has no rooted key, so its settings could not be held. A delivery folder's
  `description`, for people only, is not carried. A deliverable's header that writes either member
  itself is refused by the reader, so the folder's are never overwritten.
- **`lock.json`'s `operations`** are those `requires.operations` names; `builtins` the four pieces of
  machinery, and each built-in renderer an entry renders through.

## The engine's rules at publish (area 06)

Area 06, the engine's loading and scheduling, adds one rule at publish, ruled by the project's owner
([Consultologist-Blazor#1507](https://github.com/Consultologist/Consultologist-Blazor/issues/1507), item 4):
a `while` with `checkFirst: true` whose check reads one of the loop's own body nodes, as this pass's
(`node.<id>` or `pass.node.<id>`), is refused, since such a check has no value before the first pass.
One pass back (`pass.previous.node.<id>`, `null` on the first pass,
[chapter 4 § 4.3.3](../../package-format-v31.md#433-what-a-pass-reads)) is allowed. It adds 1 case, 2
packages, built as the earlier areas' are: the while `refine` of the resolver's cases, whose check reads
its judge, declared `checkFirst` false (valid) and `true` (invalid). Its sentence is this
implementation's `A06-002`; with it, the area's sentences are:

| Id | Sentence | Rule |
|---|---|---|
| `A06-001` | *"\<site> \<member> could not be decided: \<matches \| has_word> took longer than \<n> seconds on this text. Use a simpler pattern."* | each evaluation of `matches` and `has_word` has a time limit, the engine's setting; past it the condition or computed value fails ([chapter 3 § 3.5.3](../../package-format-v31.md#353-matches-and-has_word)). Said at run time, never at publish, so it has no package |
| `A06-002` | *"While '\<id>' declares checkFirst true, but its check reads node '\<n>' of its own body, which has no value before the first pass: declare "checkFirst": false, or read something that runs before the while."* | a `while` checked before each pass reads nothing of its own body but one pass back ([chapter 4 § 4.3.1](../../package-format-v31.md#431-members), [§ 4.3.3](../../package-format-v31.md#433-what-a-pass-reads)) |
| `A06-003` | *"Node '\<id>' computed a value that isn't \<format>."* | a computed value is held to its node's format at run time, `null` excepted, which the null rules allow ([chapter 3 § 3.6.2](../../package-format-v31.md#362-the-null-rules)); `<format>` is the format's name in the compiled bundle. Said at run time, never at publish, so it has no package |
| `A06-004` | *"Workflow \<package>@\<version> isn't published."* | a version is loaded from its stamp, `resolve.json` and `lock.json` alone ([chapter 8 § 8.2](../../package-format-v31.md#82-the-load-step-by-step-31)); a version stamped 31 whose folder lacks either document was not published whole, and is refused at the job's start. Said at load, never at publish, so it has no package |
| `A06-005` | *"Node '\<id>' gave a reply that isn't \<format>."* | an agent's reply is validated against its full format ([chapter 2 § 2.3.4](../../package-format-v31.md#234-validating-values)); an invalid one is asked again once under `onInvalid: "retry"`, and fails the node when it is invalid again or under `"fail"` ([chapter 5 § 5.1.2](../../package-format-v31.md#512-an-agent-nodes-prompt-members)). `<format>` is the format's name in the compiled bundle; the sentence never quotes the reply. Said at run time, never at publish, so it has no package |
| `A06-006` | *"Loop '\<id>' was given \<reference>, which isn't a list."* | a loop's source is held to being a list at run time: publish refuses a source not typed as one (`S04-025`), so this meets only a value that escaped its format, and fails the loop ([chapter 4 § 4.2.2](../../package-format-v31.md#422-what-a-loop-iterates)); `null` is not this, but 0 items (`S04-077`). `<reference>` is the loop's `in` as written; the sentence never quotes the value. Said at run time, never at publish, so it has no package |
| `A06-007` | *"Case '\<id>' was given \<reference>, which no branch lists, and it has no else."* | a `case` with no `else` lists every value of its subject's enum, and its subject cannot be `null` ([chapter 4 § 4.5.2](../../package-format-v31.md#452-case)), so this meets only a value that escaped its format, and fails the case. `<reference>` is the subject as written; the sentence never quotes the value. Said at run time, never at publish, so it has no package |
| `A06-008` | *"\<Subject> couldn't be rendered."* | a rendered node's, a deliverable's or an agent's body is rendered over exactly what it reads ([chapter 8 § 8.4](../../package-format-v31.md#84-scheduling)); a body that fails at run time for another reason than its step limit fails its node, and the sentence never quotes a value or the template engine's message. `<Subject>` is `Node '<id>'`, `Check '<id>'` or `Deliverable '<id>'`, with ` in function '<f>'` inside one. Said at run time, never at publish, so it has no package |
| `A06-009` | *"This job's inputs are no longer held, so it can't run. Run the workflow again."* | a job's inputs are held by reference and deleted by the retention policy once the job is over ([chapter 8 § 8.2](../../package-format-v31.md#82-the-load-step-by-step-31)); a job that finds them gone when it starts fails, and runs no node. Said at run time, never at publish, so it has no package |
| `A06-010` | *"The engine couldn't finish this job. Tell the operator."* | a fault of the engine itself, not of the package or the model service, fails the job with this sentence and never with the fault's message, which can carry a service's response ([chapter 8 § 8.4](../../package-format-v31.md#84-scheduling)). Said at run time, never at publish, so it has no package |
| `A06-011` | *"Input '\<id>' is required; fill it in to run this workflow."* | a required input is supplied at the job's start ([chapter 2 § 2.8](../../package-format-v31.md#28-inputs)): one left out, `null`, or, of any format, a string of nothing but white space (as `blank()` judges) is refused, and no node runs. Said at the job's start, never at publish, so it has no package |
| `A06-012` | *"Input '\<id>' was given a value that isn't \<format>."* | a supplied input is held to its format at the job's start ([chapter 2 § 2.3.4](../../package-format-v31.md#234-validating-values)), an `enum` of numbers included; an empty list is a value, never refused there. `<format>` is the format's name in the compiled bundle, or `its format` for an inline one; the sentence never quotes the value. Said at the job's start, never at publish, so it has no package |
| `A06-013` | *"Unknown input(s) \<ids> (declared: \<ids>)."* | a job's start names only inputs the package declares ([chapter 2 § 2.8](../../package-format-v31.md#28-inputs)); the sentence is the one a 5 to 30 start says, each id quoted, the declared ones sorted. It quotes the caller's own ids, so the email intake never replies with it. Said at the job's start, never at publish, so it has no package |

The compiled documents are exported again: every entry of `nodes`, `checks`, `deliverables` and of a
function's `nodes` gains `plainConverts`, which keeps in `resolve.json` what publish knew of each `plain`
([chapter 3 § 3.5.2](../../package-format-v31.md#352-custom-text-operations): a plain-text operand is
returned unchanged, and at run time a value has no format to tell). It maps each of the entry's `if`,
`expression`, `while` and `until` that is not `null` to a list of booleans, one for each `plain` of that
rule in the order the evaluator numbers them (a `plain` before those inside its operand, operands left
to right): `true` where the operand is Markdown or of a type not known, `false` where it is plain text
or a string; `[]` for a rule with no `plain`, and `{}` for an entry with none of the four. The three
cases changed in that member alone, and so in their `resolve.json` hash and `lock.json`'s
`resolve.hash`.

## The dialect (area 07)

Area 07, prompts and macros, holds every Scriban body of a package to the dialect at publish
([chapter 5](../../package-format-v31.md#5-templates-and-macros),
[`scriban-dialect.md`](../scriban-dialect.md)): its statements and built-ins, what each site reads, its
body `if`s, placement forms, run spots, renderers, snippets, parts and macros. The dialect is the sixth
step of the check, after the expressions and before the derived values, and what it finds in each body
is what the resolver is told that body reads.

Three earlier cases changed, and only so that their bodies are valid templates:

- the packages of `S01-007` and `S04-052` hold the snippet folder `standards`, whose `format` was
  `plaintext` while its item's header is an object with a title (`S05-036`); the folder's format is now
  that object;
- the valid package of `S01-036` holds the while `refine` with two `if`s, `brief` and `detailed`, which
  nothing read (`S04-035`, now judged through the bodies); the judge's prompt reads both.

It adds 60 cases, 120 packages, built as the earlier areas' are, one for each publish sentence of
chapter 5: `S05-001` to `S05-007`, `S05-009` to `S05-011`, `S05-013`, `S05-015` to `S05-026`,
`S05-028` to `S05-031`, `S05-033` to `S05-040`, `S05-042` to `S05-051`, `S05-063` and `S05-064`; and
three of other chapters that only a template reaches: `S02-019` (a template reading the title of a
plain enum), `S06-028` (a template reading a field outside the profile's five) and `S04-063` (a macro a
function's agent places, whose `if` reads a node outside the function; the macro is the function's own,
which a placement in a function finds first). `S05-009`'s case is the package of its worked example,
`S05-008` (the deliverable `consult` branching on `part.state` with no `else`), and `S05-026`'s that of
`S05-027` (`identify_problem` piping a `section_plan` into `renderer.concept_bullets`): each says the
example's sentence word for word.

No package reaches `S05-041` (a node that is no agent declaring parts): the reader refuses a `parts`
member on any other kind first. `S05-060` (W-1, a run spot) and `S05-061` (W-2, a `markdown_block`
renderer piped inside a line) are warnings: a package that gets them is accepted, and they are in
`resolve.json`'s `warnings`. `S05-012`, `S05-014`, `S05-053` to `S05-059`, `S05-062` and `A07-006`
are said at run time, while a body renders or a reply is read, never at publish, so they have no
package. The area's own sentences, which are not in `sentences.json`, are:

| Id | Sentence | Rule |
|---|---|---|
| `A07-001` | *"Snippet '\<id>' places \<part.\* or macro.\*>, and \<subject> places it in \<a part's text \| a macro's instruction>; a snippet placed there doesn't place parts or macros."* | a snippet placed in a part's text or a macro's instruction places no part or macro, itself or through a snippet it places (the guard, [chapter 5 § 5.6.3](../../package-format-v31.md#563-placing-a-snippet)) |
| `A07-002` | *"Part '\<name>' of node '\<id>' uses \<if or part.\*>; a part's text only presents."* | a part's text has no `if` of its own and places no part; its header `if` decides it ([chapter 5 § 5.7.1](../../package-format-v31.md#571-the-member)) |
| `A07-003` | *"Macro '\<id>' places \<macro.\* or part.\*> in its instruction; combine instructions by placing each macro in the prompt."* | a macro's instruction holds its own marker and places no macro or part ([chapter 5 § 5.8.3](../../package-format-v31.md#583-where-placing-the-instruction)) |
| `A07-004` | *"\<Subject> uses \<form> at line \<n>; a for runs over a whole list in order and reads only for.first, for.last, for.index, for.even and for.odd."* | a `for` takes no `limit:`, `offset:`, `reversed` or `else`, and reads no other loop position ([chapter 5 § 5.2.1](../../package-format-v31.md#521-statements)) |
| `A07-005` | *"\<Subject> can't be read as a template at line \<n>: close every tag and every if and for."* | a body is one Scriban reads; the sentence never quotes Scriban's own message ([chapter 5 § 5.2](../../package-format-v31.md#52-the-dialect)) |
| `A07-006` | *"\<Subject> stopped rendering: array.join met a list with an empty element."* | at run time `array.join` over a list holding `null` fails its node ([chapter 5 § 5.2.2](../../package-format-v31.md#522-built-ins)). Said at run time, never at publish, so it has no package |
| `A07-007` | *"\<Subject> writes \<path> at line \<n>, which is \<an object \| a list>; read a member, loop over it or pipe it into a renderer."* | an output writes text, never a whole object or list ([chapter 5 § 5.2.2](../../package-format-v31.md#522-built-ins)) |
| `A07-008` | *"\<Subject> reads \<path> at line \<n>; read \<.value \| .content \| .title> of it."* | a node, an input, a check or a parameter is read through a member, never bare ([chapter 5 § 5.3.1](../../package-format-v31.md#531-the-table)) |
| `A07-009` | *"\<Subject> places \<unit> at line \<n> inside \<an if \| a for>; a part, a snippet or a macro is placed at the top level of its template, and its own if decides it."* | a placement's decision is recorded once, so it is not made inside an `if` or a `for` ([chapter 5 § 5.2.6](../../package-format-v31.md#526-placement-forms-and-whitespace)) |
| `A07-010` | *"Snippet '\<id>' declares format \<format>; a snippet's text is plaintext, markdown_block or markdown_inline."* | a single snippet's `format` is a text format ([chapter 5 § 5.6.1](../../package-format-v31.md#561-a-single-snippet)) |
| `A07-011` | *"\<Subject> places more than \<limit> parts, snippets and macros, counting what its parts and snippets place; place fewer."* | a template places at most 1,000 units, counting what each places in turn, so publish never expands without bound (this implementation's limit) |
| `A07-012` | *"Snippet '\<id>' \<places \<unit> \| pipes into \<renderer> \| reads \<path>>, and \<subject> reads it as \<path> at line \<n>; a folder item's body read in a loop places no part, macro or snippet, pipes into no renderer and reads no run.\* or run-dependent value."* | a loop over a snippet folder reads each item's body as `item.content`, rendered where it is read, so one tag stands for a different body per item: that body is checked at each place that reads it and only presents ([chapter 5 § 5.6.2](../../package-format-v31.md#562-snippet-folders); this implementation's rule) |
| `A07-013` | *"Snippet '\<id>' holds a tag at line \<n>, and \<subject> \<passes it to function '\<f>' as param.\<p> \| reads it in its expression>, where it isn't rendered; keep a folder item's body plain text, or read it as item.content in its loop."* | a folder item's body is rendered only where a template reads it as `item.content` in its loop; carried out of the loop as text, by a `call`'s `with` (the item, a folder item, a loop's `.items`) or a `computed` node's `expression`, nothing renders it, so there every body of that folder is plain text, no tag and no raw block ([chapter 5 § 5.6.2](../../package-format-v31.md#562-snippet-folders); [chapter 4 § 4.7.7](../../package-format-v31.md#477-the-call-node); this implementation's rule) |
| `A07-014` | *"Nodes '\<a>' and '\<b>' bind agent '\<name>' at versions \<m> and \<n>; a package binds one version of an agent."* | `requires.agents` names one integer version of each agent, so a package whose agent nodes are bound to two versions of one agent is refused at publish ([chapter 7 § 7.3.1](../../package-format-v31.md#731-requires-what-the-package-needs-from-the-engine)). The published agents catalogue binds each agent at one version and a package does not choose its agents' versions, so no package reaches it against the published registry: it has no package |
| `A07-015` | *"MacroChoices names '\<id>', which is not a boolean input of the package."* | a per-run choice is an optional boolean input that takes the macro's id ([chapter 5 § 5.8.2](../../package-format-v31.md#582-whether-the-header-if)), so at the job start each entry of the request's `MacroChoices` is the value of the package's boolean input of that id, exactly as if the request had sent it; an id that is no input, or an input that is not `boolean`, refuses the start. Said at the job start, never at publish, so it has no package |
| `A07-016` | *"Input '\<id>' is given one value in Inputs and another in MacroChoices; send it once."* | an input sent both ways, as an input (other than `null`) and in `MacroChoices`, with different values refuses the start. Said at the job start, so it has no package |

The compiled documents are exported again from the dialect's reading, in place of the reads the
exporter stated. Every agent, `rendered` node and deliverable entry gains `placements` (each unit its
body places, in order, placed units expanded in place: `site`, `within`, its `if` with keys rooted for
the entry's place, that rule's `plainConverts`, and a macro's marker `form`; a macro in a folder
preceded once by its folder's `macro-folder.<id>`) and `names` (each `node.<id>` or `check.<id>` the
body writes, mapped to the rooted key it names there, where the two differ). Each run spot gains `unit`
(the placed unit whose text holds it, `null` for the body) and `neutral` (`marker` or `text`, what
stands for it in the run-neutral render). A built-in renderer a package pipes into is embedded in
`renderers` as a package renderer is, with its formats bundled. The reads the dialect found are the
ones the exporter had stated, so the three cases changed in `names` and `placements` alone (each `{}`
and `[]` but the nested note's judge, whose `node.draft_summary` names `node.refine.draft_summary`),
and so in their `resolve.json` hash and `lock.json`'s `resolve.hash`.

## The dialect's goldens (area 07)

Area 07 exports three families for [chapter 5](../../package-format-v31.md#5-templates-and-macros)
and the escape of [chapter 6 § 6.6.4](../../package-format-v31.md#664-strict-formats): 40 dialect
cases (43 with area 08's three deliverables), 26 renderer cases and one file of 42 escape vectors. Each holds its inputs and the bytes
this implementation's code gave for them; every text file is UTF-8 with no byte-order mark, and
every JSON file is written with 2-space indentation, `\n` line ends and a final newline, every
character outside ASCII as itself.

| Family | Cases | Holds |
|---|---|---|
| `dialect-goldens` | one folder per allowed feature of [`scriban-dialect.md`](../scriban-dialect.md) § 10 (40), and area 08's three deliverables (43) | an output (`output-text`, `output-values`); each built-in with and without `null` (`string-upcase`, `string-upcase-null`, …, `date-to-string-null`); a `for` with each position variable (`for-first`, `for-last`, `for-index`, `for-even`, `for-odd`); a body `if` over states and a check's pass (`if-state`, `if-check-pass`); `~` on statements (`tilde-statements`); each placement form of [§ 5.2.6](../../package-format-v31.md#526-placement-forms-and-whitespace), placed and absent (`placement-block-placed`, `placement-block-absent`, `placement-inline-…`, `placement-alone-…`); a part, a snippet placing a snippet, a folder item read in its loop (`part`, `snippet`, `folder-item`); a macro's instruction with each marker form and the reply it is finished with (`macro-block`, `macro-inline`); a raw block, a comment (`raw-block`, `comment`); a pipe into renderers and an `if` in a renderer's body (`pipe-renderer`, `renderer-if-value`); two run spots (`run-spot`); and, from area 08, a deliverable of each kind of format composed as the run composes it (`deliverable-escaped`, `deliverable-plaintext`, `deliverable-object`) |
| `renderer-goldens` | `<renderer>/<case>`, each built-in renderer over 13 concept lists (26) | `concept_bullets` and `concept_context` over an empty list, one active, inactive or not SNOMED concept, a `support` present, absent, empty, of spaces and tabs, or of a tab and a line break, another or an empty `source`, three mixed concepts, and Markdown characters in every member |
| `markdown-escape-vectors` | `vectors.json` (47 vectors) | each of the 32 ASCII punctuation characters alone, then ten sentences of fictional clinical text, then area 08's five: a line led by one space, lines led by a tab, a run of spaces mid-line, a line of white space only, and a text of white space only |

**A dialect case** is a folder:

```
dialect-goldens/<case>/about.txt
dialect-goldens/<case>/template.md          or   package/manifest.json, nodes/index.json, … and entry.txt
dialect-goldens/<case>/scope.json
dialect-goldens/<case>/placed.json
dialect-goldens/<case>/expected.txt
dialect-goldens/<case>/expected.neutral.txt      (a case with a run spot)
dialect-goldens/<case>/reply.txt, expected.reply.txt   (a macro case)
```

`template.md` is a case whose feature is one body: the prompt of an agent node, in a package whose
reads are typed as `scope.json`'s values are (`about.txt` names them). A case that needs headers
(a snippet, a part, a macro, a folder, a renderer) holds the whole upload under `package/`, byte for
byte, and `entry.txt` names the entry composed, its rooted key on one line (`node.golden`,
`node.standards.section`, `deliverable.note`). `scope.json` is the data the body is given, keys rooted as the run holds
them (`input.<id>.content`, `node.<id>.value`, `item.value`, `run.date`); `placed.json` maps each
decided site of the entry's `placements` (`snippet.<id>`, `part.<id>`, `macro.<id>`,
`macro-folder.<id>`) to its decision, and a site it does not name is not placed. Composing the body
over `scope.json` with those decisions gives `expected.txt`, the text sent, byte for byte;
`expected.neutral.txt` is the run-neutral text of the same render, each run spot the marker
`{{run:<n>}}` ([chapter 5 § 5.4](../../package-format-v31.md#54-run-spots-and-the-two-hashes)). In a
macro case `reply.txt` is the model's reply and `expected.reply.txt` that reply with each offered
marker replaced ([chapter 5 § 5.8.6](../../package-format-v31.md#586-processing-the-reply)); the
reply is never rendered. **A renderer case** holds `value.json`, the `concept_list` value piped in,
and `expected.txt`, what a prompt piping it into the renderer gives; the C# renderers of version 30
give the same bytes, which the library's tests hold. **The escape vectors** are a list of
`{ "plain", "escaped" }`: escaping `plain` gives `escaped`. The index lists a dialect case by its
folder, a renderer case as `<renderer>/<case>`, and the escape family as `vectors.json`. **The cases
are exported by the library's composer, its reply step and its escape, and are never written by
hand;** the library's tests hold the same bytes as goldens. `python3 scripts/check-v31.py` (groups
`dialect-goldens`, `renderer-goldens`, `markdown-escape-vectors`) holds each family to the index
and each case to its files; the escape group also recomputes each vector. **The three families are
shared by areas 07 and 08, so the export adds to them and never rewrites them**
(Consultologist-Blazor#1505, ruling R11): a case it produces is written afresh, a case already here
that it does not produce is kept with its index entry, and an escape vector is kept unless the
export writes one with the same `plain`. The library's tests fail when a case of
`renderer-goldens` or a vector of `markdown-escape-vectors` present before area 08's escape change
(bdc1ee6), or one of area 07's 40 dialect cases, is no longer exported.

**What the cases pin that the text leaves open.** An outside implementation that chooses otherwise
gives other bytes:

| Decision | What the cases pin |
|---|---|
| D7, the escape | `markdown_escape` 1.0.0 writes a backslash before each of the 32 ASCII punctuation characters and changes nothing else but a line's first leading space or tab: letters, digits, other white space, line breaks and every character outside ASCII stay. Since Consultologist-Blazor#1505's ruling R9 (the owner, 2026-11-22), the first space or tab leading each line (at the text's start and after each `\n` or `\r`) is written `&#32;` or `&#9;`, so a line led by four spaces or a tab is not a code block. A line of white space only is no exception (`"  "` escapes to `"&#32; "`): a reader judging escaped Markdown empty counts `&#32;` and `&#9;` as white space; the version stays 1.0.0, as it is not yet frozen |
| D13, values | an output writes a number in its canonical JSON form (`7.5`), a boolean as `true` or `false`, a date as `%Y-%m-%d`, and `null` as nothing; a built-in given `null` gives `null`; `string.upcase` and `string.downcase` are the invariant culture's simple case mapping (`ß` and `ﬁ` stay, `İ` stays, `Σ` lowers to `σ`); `string.capitalize` upper-cases the first character only; `for.index` counts from 0 |
| D17, the marker | inside its instruction the macro's own marker tag renders as its source text, its `~` included, and a block marker keeps the indentation before it on its line |
| a macro's body | is rendered in the prompt's scope, less its file's final line ending (one `\n`), then substituted; a snippet it places is decided after the macro. In the reply a block marker's line loses the indentation before the marker and the spaces after it and keeps its newline |
| a snippet's and a folder item's body | are the author's to the byte, a file's final newline included: a block placement of a snippet ending in a newline leaves an empty line after it. A folder item's body read as `item.content` is rendered in its loop's scope |
| the built-in renderers | write booleans as `True` and `False` and end with no newline, as the C# renderers of version 30 do ([chapter 5 § 5.5.3](../../package-format-v31.md#553-built-in-renderers)) |

## The checks (area 08)

Area 08, checks, deliverables and the profile, holds `checks/` to its rules at publish
([chapter 6 § 6.1](../../package-format-v31.md#61-checks-the-folder-and-the-root),
[§ 6.3](../../package-format-v31.md#63-check-loops), [§ 6.4](../../package-format-v31.md#64-aggregates-and-the-gate)).
What `checks/` holds is judged with the type rules, before them: a leaf there is `kind: computed` with
`format: check_result`, and a flow node is a `for`, an `if` or a `case`; a `while` or a `call` there is
refused. Once the resolver has read the package's references, a `for` in `checks/` runs over a loop's
`.items` (`node.<loop>.items` or `check.<loop>.items`), a deliverable's `check` names a check at the top
of `checks/`, and that check's `if` reads nothing that can be `null` (a node that may be skipped, an
input that is not required, a nullable field).

One earlier case changed, so that its check loop runs over a production loop's `.items`: the packages of
`S03-030` hold the loop `notes`, which takes each prior note as it is, and the check loop
`notes_checked` now runs over `node.notes.items` and judges `item.item.value`, the prior note, in place
of running over the input itself.

It adds 6 cases, 12 packages, built on the resolver's `example-functions` package (its production loop
`standards`, the check loop `section_coverage` over its `.items`, the check `all_sections` and the
deliverable `consult` it gates): `S06-009`, `S06-010`, `S06-011`, `S06-014`, `S06-035` and `A08-001`.
Where a check's kind changes, and the members of the kind with it (`S06-010`, `S06-011`), the invalid
side writes that one file again. Part 06's other rules of checks are said under the ids of the parts
that already say them, so they have no case here: a `failWith` that is no literal is `S03-029`
(`A04-010`), a `min` that is no whole number of at least 0 `S03-029` or `S03-030`, a check in a
function `S04-062`, and a read of `deliverable.*` outside `checks/` `S03-019` (`S05-020` in a template).

It also holds a deliverable's header and its delivery folder to their rules at publish
([chapter 6 § 6.6.1](../../package-format-v31.md#661-the-file),
[§ 6.6.3](../../package-format-v31.md#663-what-a-deliverable-reads), [§ 6.8](../../package-format-v31.md#68-delivery)).
With the type rules, once every format name is known: a deliverable's `format` is `markdown_block`,
`plaintext` or a format whose shape is an object (`markdown_inline`, a list, a string or any other scalar is
refused; a name that is no format stays `S02-017`), its `whenEmpty` is `release`, `hold` or `fail`, and
each delivery folder's `delivery` lists only `email`, `pdf`, `emr` and `zip`, and its `bundle` is
`"zip"` or `null`. Once the dialect has typed the bodies: a deliverable reads no `check.<id>` that its own
`check` names, in its body or in a snippet it places (a placed snippet's reads are the deliverable's).
It adds 5 cases, 10 packages, on the same package: `S06-018`, `S06-020`, `S06-025`, `S06-026` and
`A08-002`; each invalid side is one text replacement.

A check reads a deliverable ([chapter 6 § 6.1.2](../../package-format-v31.md#612-who-reads-checks-and-what-checks-read),
[§ 6.6.7](../../package-format-v31.md#667-deliverables-are-terminal), [§ 6.7](../../package-format-v31.md#67-gating-and-outcomes)):
a rule of a node under `checks/` reads `deliverable.<id>.content` (the composed text, a `string` that can be
`null`), `.value` (an object format's value, else the text; can be `null`) and `.state` (`released`, `held`,
`skipped` or `blocked`), the id the longest key path that names a deliverable (`deliverable.emr.note`).
[Chapter 3 § 3.4.1](../../package-format-v31.md#341-the-roots) lists `deliverable` among the roots JSON Logic never
reads; chapter 6, which owns checks, says three times that checks read one, so this implementation reads it
under `checks/` only: everywhere else (a node in `nodes/`, a function, a deliverable's `if`, a macro's `if`) it
stays `S03-019`, and in a template `S05-020`. The read is a `reads` edge from the deliverable to the check, and the
check takes the deliverable's three flags as it takes any value's. A deliverable's *gate set* is its `check` and
every check that check depends on, through checks only (their reads and conditions, a check loop's source, its
`ret` and its body): a check in the gate set reads the deliverable as soon as it is composed, and may not read its
`.state`, which it decides (`A08-003`); every other check reading it waits for its outcome, so waits for its gate.
Circles are searched over the nodes, the checks and the deliverables together with those waits, and said as
`A05-003`, which names each by its bare id (a deliverable by its key without the root) and passes through the
deliverable a check waits for: two gates that each read the other's deliverable wait for each other, said as
*"Node 'gate_a' reads node 'emr.summary', which reads node 'gate_b', which reads node 'emr.consult', which reads
node 'gate_a': …"* (the row's words name every step a node). It adds 1 case, 2 packages, on the same package with the consult
note gated instead by the check `proofread`, which reads the note and the check `consult_words`: `A08-003`, its
invalid side `consult_words` reading the note's state, its valid side counting the note's words; and the
`compiled-documents` case `checked-note`.

A deliverable's reads fit its format ([chapter 6 § 6.6.4](../../package-format-v31.md#664-strict-formats)), held
once the dialect has typed each output: a `markdown_block` deliverable writes no object or list (`S06-021`, *Use a
renderer or a node*); a `plaintext` one writes no Markdown, read (`S06-021`, *Convert it in a node*: a Markdown
node, a renderer's Markdown, a Markdown snippet it places) or in its own text (`S06-022`: a line whose first
non-space character outside a tag is `#`, `-`, `*` or `>`, or that holds two `**`, quoted trimmed and cut to 40
characters), and no object or list (`S06-021`); an object one is exactly one tag writing `node.<x>.value` of its
format by type equality, with nothing before it and at most a final line end after it (`S06-023`, its sentence
keeping `<x>` as written). For a deliverable these stand where `A07-007` stands for every other template. Each
`deliverables` entry of `resolve.json` gains `escapes`, the output tags composition escapes: in a `markdown_block`
deliverable, each output of a plain-text format, a string, an enum, a date, a number or a boolean, in its body or
in a Markdown snippet it places (with that snippet's site as `unit`), and a plain-text snippet it places, once, at
its placement; never a renderer's output; `[]` for a `plaintext` or object deliverable. It adds 3 cases, 6
packages, on the same package: `S06-021` (the consult note writing the draft's terms), `S06-022` (the note made
`plaintext`, its heading written `## Sections`) and `S06-023` (the note a `concept_list`, the terms written with
text before them); each invalid side is one text replacement. Two earlier cases changed so that a plain-text
note does not also read the Markdown draft: the invalid sides of `S05-024` and `S05-025` pipe the plan, not the
draft, into `string.upcase`. The four `compiled-documents` cases gain `escapes` on every deliverable.

A deliverable composes with its plain reads escaped ([chapter 6 § 6.6.4](../../package-format-v31.md#664-strict-formats),
[§ 6.9](../../package-format-v31.md#69-deliverables-in-the-record-and-history)): each output its entry's `escapes` lists
(matched by its `unit` and its `at`, as `runSpots` are) is written through `markdown_escape` where it is written, so each
pass of a `for` escapes its own item, a `null` still writes nothing, and a line end in a value stays a line end; a
placed plain-text snippet listed at its placement is escaped whole, once, and its unit is recorded by the hash of its
text as spliced, escaped. The composed hash and each substitution's are taken after escaping, so replay holds, and the
1 MiB output limit is held after escaping too; a run spot it escapes is recorded escaped, in the sent text and in the run-neutral
text, whose `{{run:<n>}}` markers stay as they are. An object deliverable's text is its one value's RFC 8785 JSON, with no
final line end (the template's own is not written), held to the same 1 MiB limit, and a `null` value composes `null`. It adds three `dialect-goldens`
cases, each a `package/` and an `entry.txt` naming `deliverable.note`: `deliverable-escaped` (a `markdown_block` note
reading a plain-text summary, a list of plain lines holding `# 1`, `*bold*`, a line end and a `null`, a Markdown
assessment, a renderer's output and a placed plain-text snippet), `deliverable-plaintext` (a `plaintext` note, which
escapes nothing) and `deliverable-object` (a `section_plan` note, its value's members sorted). Area 07's 40 cases are
unchanged, byte for byte; `entry.txt` may now name a deliverable.

Three rulings of the owner on area 07's dialect ([#1505](https://github.com/Consultologist/Consultologist-Blazor/issues/1505)) are
held too, and add no case. A folder item's `.content` is `markdown_block`, whatever the folder's `format`, which types
its header only ([chapter 5 § 5.6.2](../../package-format-v31.md#562-snippet-folders)): a `markdown_block` deliverable
writes `snippet.<folder>.<id>.content` as it is, never in its `escapes`, and a `plaintext` one refuses it (`S06-021`).
`A07-013` holds at every depth: in a loop over a loop's `.items`, however many loops below the folder's, the `item` and
every read along the chain to the folder item (`item.item` one loop down, `item.item.value.item` two, and so on)
carries its body, so a `call`'s `with` or a `computed` node's `expression` reading one is refused when a body holds a
tag; a read that leaves the chain (an element's `content`, the folder item's `value`) carries none. Its case stays
area 07's, one per sentence. And a template the engine fails to read in a way no text explains (an exception other
than Scriban's own for unreadable text) is `A08-006`, the engine's fault, not `A07-005`, the author's; no package
produces it, so it has no case.

The area's own sentences, which are not in `sentences.json`, are:

| Id | Sentence | Rule |
|---|---|---|
| `A08-001` | *"Deliverable '\<id>' is checked by \<reference>; a deliverable's check names a check.\*."* | a deliverable's `check` is `check.<id>` of a check at the top of `checks/`: never a production node, nothing at all, a check inside a check loop or a check loop itself ([chapter 6 § 6.1.2](../../package-format-v31.md#612-who-reads-checks-and-what-checks-read); the chapter's own wording, which has no row in `sentences.json`) |
| `A08-002` | *"Deliverables folder '\<path>' has bundle \<value>; write "zip" or null."* | a delivery folder's `bundle` is `"zip"` or `null` ([chapter 6 § 6.8](../../package-format-v31.md#68-delivery)) |
| `A08-003` | *"Check '\<id>' reads deliverable.\<deliverable>.state, and deliverable '\<deliverable>' waits for check '\<id>' through its check '\<gate>': read its .content, or read the state in a check it doesn't wait for."* | a check in a deliverable's gate set (its `check` and every check that check depends on) reads the composed deliverable, never its `.state`, which waits for that check ([chapter 6 § 6.7](../../package-format-v31.md#67-gating-and-outcomes); this implementation's rule, from the chapter's "a deliverable is readable by checks only" and its outcomes) |
| `A08-006` | *"\<Subject> couldn't be checked: the engine failed reading its template. This is a fault in the engine, not in the package; report it."* | reading a template failed in a way no text explains: a fault of the engine, never said as the author's `A07-005` ([chapter 5 § 5.2](../../package-format-v31.md#52-the-dialect); ruled by the owner on [#1505](https://github.com/Consultologist/Consultologist-Blazor/issues/1505); no package produces it, so it has no case) |

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

Two readings the text makes: an `enum` must sit beside an explicit `string`, `integer` or `number`
`type` (values of that one kind; mixed kinds are refused) and a labelled `oneOf` beside an explicit
string `type` (the text says "on a string" and always writes the type), and a `$defs` name is any name
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
  The table of [§ 7.2.2](../../package-format-v31.md#722-top-level-members) has no `derivedFrom` row,
  but its text carries the manifest's members that only steer publish "under the same names when
  they exist at 31", and `derivedFrom` does: `resolve.json` requires it, a string or `null`.
  A `functions` entry is held to the same derived members as every other entry (§ 7.2.5's table
  marks them "every entry"), beside its own `nodes` map: `resolve/valid-function.json` holds one,
  and `resolve/invalid-function-missing-reads.json` leaves out its `reads`.
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
- **"The header of" for a plain JSON file.** `S01-017` and `S01-018` say *"The header of
  '\<path>' …"*, written for a `.md` file's front matter, and the text gives no other sentence for
  a plain JSON file (`index.json`, `manifest.json`, a format, a test) that is not JSON or writes a
  member twice. The reader uses the two sentences as written for those files too, so they say "the
  header of 'nodes/index.json'".
- **Two sentences for a call's body.** `S01-020` (*"… has a body; a \<computed node | call |
  check> keeps everything in its header."*) and `S04-071` (*"Call '\<id>' has a body; a call is a
  header only."*) both refuse a `call` with a body. The reader gives `S01-020`, which names the call;
  `S04-071` is not given.
- **One sentence under two ids.** `S04-020` and `S01-005` (a `maxParallel` above 15), `S04-032` and
  `S01-003` (a while's `max` above 15), and `S02-009` and `S01-028` (a producer the kind does not
  have) are the same words. The reader gives the `S01-…` id, and the cases are filed under it.
- **`S04-009` is printed for `Loop` only.** Its row in `sentences.json` and in
  [chapter 11](../../package-format-v31.md#11-every-sentence) reads *"Loop '\<id>' declares label
  null; …"*, while [chapter 4 § 4.10.1](../../package-format-v31.md#4101-refusals-at-publish) prints
  the sentence with "(also `While`, `If`, `Case`)". The reader writes the flow kind's word, and the
  check script reads the row's first word as any of the four.
- **A snippet folder item's body.** [Chapter 1 § 1.4](../../package-format-v31.md#14-front-matter)'s
  table requires a snippet folder item's text, while
  [chapter 5 § 5.6.2](../../package-format-v31.md#562-snippet-folders) lets a folder item's body be
  empty (its `item.content` is then `""`). Chapter 5's is the later decision, and the reader follows
  it: an empty folder item body is not refused.
- **Templates that read awkwardly when filled in.** `S01-028`'s *"a \<kind> node's producer"* gives
  "a agent node's producer", and this implementation's `A02-007` gives "a agent node is a file" the
  same way; `S01-025`'s *"\<Declaration>'s description"* gives "Node 'plan''s description". The
  sentences are used as written.
- **`S04-024` says "max 0" whatever was written.** Its row, *"Loop '\<id>' declares max 0; the
  least is 1."*, has no `<n>`, so a `max` of `-3` is also reported as "max 0". The other bounds'
  rows (`S04-021`, `S04-033`) print the number as written.
- **`S01-028` prints the rooted key where other node sentences print the id.** Its row reads
  *"\<Node | Check> '\<key>' is kind …"*, so it says "Node 'node.plan' is kind agent …", while
  `S01-021` to `S01-026`, `S02-007` and the rest say "Node 'plan'".
- **A publish report in an upload is dropped, though chapter 1 names two files.**
  [Chapter 7 § 7.5](../../package-format-v31.md#75-the-publish-pipeline) step 0 drops *"any
  `resolve.json`, `lock.json` or publish report in the upload"* unread, and § 7.6 names that report
  `publish-report.json`; [chapter 1 § 1.2](../../package-format-v31.md#12-the-folder-layout) and
  [§ 1.7](../../package-format-v31.md#17-sourcebounds) name only `resolve.json` and `lock.json`. The
  reader drops all three at the root before counting.
