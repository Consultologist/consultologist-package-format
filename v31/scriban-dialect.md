# The Consultologist Scriban dialect, version 1.0.0 (`scriban-dialect@1.0.0`)

The template language of specVersion 31 packages: the one dialect of Scriban in which every
prompt, `rendered` node, renderer, snippet body, part text, macro instruction, macro body and
deliverable of a package is written. This document is the versioned, reference form of the rules in
[chapter 5 § 2](../package-format-v31.md#52-the-dialect) of the normative text and of its placement, marker and
body-`if` rules ([§ 2.5](../package-format-v31.md#525-a-body-if-tests-recorded-facts-only),
[§ 2.6](../package-format-v31.md#526-placement-forms-and-whitespace), [§ 8.4](../package-format-v31.md#584-the-marker)); the chapter states
them in full and this document gathers them. Its version, `scriban-dialect@1.0.0`, is recorded in a
compiled package's `lock.json` and listed in its `requires` ([chapter 7](../package-format-v31.md)).

**Anything not listed as allowed is refused at publish, with a sentence.** Each rule below names
the design's label for its sentence (`R-D1` and so on) beside the sentence's id in
[`sentences.json`](sentences.json) (`S05-001` and so on), and the sentence itself, used as written.
`<…>` marks a placeholder. The last section is the whole dialect as one table: feature, allowed or
refused, sentence.

## 1. The engine

- **Scriban 7.2.5,** pinned exactly.
- **The invariant culture.** Every render runs in it: English month and day names in
  `date.to_string`, culture-free case mapping in `string.upcase`, `string.downcase` and
  `string.capitalize`, and invariant number formatting. It is recorded in `lock.json`, so a host's
  culture never changes a note's bytes or hashes.
- **Strict variables.** Reading a member that does not exist is refused at publish, and a render
  that meets one fails.
  - R-D10 (S05-011): *"\<Subject\> reads \<path\> at line \<n\>, which \<format or root\> doesn't have."*
- **Dates render as ISO** (`%Y-%m-%d`) unless formatted.
- **An empty list counts as false** where a truth value is read.
- **Decisions are not made in bodies.** Decisions are recorded, so they live in headers as JSON
  Logic; a body only presents.

## 2. Statements

### 2.1 Allowed

| Construct | Written | Notes |
|---|---|---|
| output | `{{ x }}` | `x` is an access path, optionally piped (§ 3, § 6) |
| member access | `node.plan.value.sections` | index access (`list[0]`) is refused |
| literals | `"text"`, `12`, `true`, `false`, `null` | as arguments to built-ins and in `if` comparisons |
| `for` | `{{ for x in list }} … {{ end }}` | over a list only; position variables `for.first`, `for.last`, `for.index`, `for.even`, `for.odd` |
| `if` | `{{ if … }} … {{ else if … }} … {{ else }} … {{ end }}` | restricted to recorded facts (§ 4) |
| pipe | `x \| string.strip`, `x \| renderer.concept_bullets` | to the allowed built-ins (§ 3) and to renderers only |
| comment | `{{# a note }}` | rendered as nothing |
| raw block | `{%{ … }%}` | literal braces, not interpreted |

### 2.2 Refused

- Assignment (`x = …`) and `capture`; `func`, `include`, `import`, `with`, `wrap`; Scriban's
  `while`, `break` and `continue`; `case` / `when`; `tablerow`; arithmetic (`+`, `-`, `*`, `/`,
  `%`, `//`) and string concatenation by `+`. Markdown numbers a `1.` list itself, and a computed
  value belongs in a `computed` node.
  - R-D1 (S05-001): *"\<Subject\> uses \<construct\> at line \<n\>; templates present text and may not use assignment, capture, func, include, import, with, wrap, while, break, continue, case, tablerow or arithmetic."*
- A `for` over anything but a list (a range `1..3`, an object).
  - R-D6 (S05-006): *"\<Subject\> runs a for over \<expr\> at line \<n\>; a for runs over a list."*
- The `for` options `limit:`, `offset:` and `reversed` (they choose which elements appear, which
  is a decision), and `for.rindex`, `for.length` and `for.changed`. These forms have no sentence
  of their own: they are refused by the rule that anything not listed as allowed is refused.
- **Index access** (`list[0]`, `node.plan.value.sections[2]`): a list is read whole, by a `for`, or
  by identity through `.items`.
  - R-D11 (S05-063): *"\<Subject\> reads \<path\>[\<n\>] at line \<n\>, a position in a list; lists are read whole, with a for, or by identity through .items."*
- **The call form of a renderer** (`renderer.concept_bullets(x)`); the one call form is the pipe
  (§ 6).
  - R-N4 (S05-030): *"\<Subject\> calls renderer.\<id\> at line \<n\>; pipe into it: \<value\> \| renderer.\<id\>."*

These `for` forms are refused and no published package uses them; revisiting them is
[#1475](https://github.com/Consultologist/Consultologist-Blazor/issues/1475) (Milestone 40).

**Equality in bodies.** Scriban has no `===`. A body `if` compares with Scriban's `==` and `!=`,
only within the recorded facts of § 4. The `===`/`!==`-only rule is JSON Logic's
([chapter 3](../package-format-v31.md#3-expressions)), which is where every value comparison lives.

## 3. Built-ins

Built-ins are pure, and versioned like the built-in operations: each is listed in `requires` with a
caret range and in `lock.json` at its exact version.

| Built-in | Signature | Result | Null in |
|---|---|---|---|
| `string.upcase` | `(text: string \| text format) → same format` | invariant upper case | null (renders as nothing) |
| `string.downcase` | `(text: string \| text format) → same format` | invariant lower case | null |
| `string.capitalize` | `(text: string \| text format) → same format` | first character upper case, invariant | null |
| `string.strip` | `(text: string \| text format) → same format` | leading and trailing whitespace removed | null |
| `array.join` | `(list: list<string> \| list<text format>, separator: string literal) → string`, or the elements' text format | the elements joined by `separator` | null list gives null; a null element fails the node |
| `array.size` | `(list: list<any>) → number` | the element count | null |
| `date.to_string` | `(date: date, pattern: string literal) → string` | the date formatted by `pattern` | null |

- **`date.to_string` requires an explicit pattern,** a string literal (Scriban's `%` patterns, for
  example `"%d %B %Y"`). A date output without it renders as ISO `%Y-%m-%d`.
- **Null:** a null value output directly renders as nothing, and **a built-in given null returns
  null**, matching JSON Logic's rule that operations on null give null. The one exception is
  `array.join`: a list holding a `null` element fails the node.
- **Refused:** `date.now`, random numbers and environment access (they break reproducibility);
  `truncate` (it cuts clinical text); `object.default` (it chooses text, which is a decision);
  every other built-in.

- R-D2 (S05-002): *"\<Subject\> calls \<built-in\> at line \<n\>; the allowed built-ins are string.upcase, string.downcase, string.capitalize, string.strip, array.join, array.size and date.to_string."*

- R-D3 (S05-003): *"\<Subject\> calls truncate at line \<n\>; truncate cuts clinical text."*

- R-D4 (S05-004): *"\<Subject\> calls object.default at line \<n\>; choosing text is a decision: put it in a header condition."*

- R-D5 (S05-005): *"\<Subject\> calls date.to_string at line \<n\> without a pattern; write the pattern, for example "%d %B %Y"."*

## 4. A body `if` tests recorded facts only

A body `if`, in every template (snippet and macro bodies included), may test only facts the engine
has already decided and recorded:

| Fact | Written | Values |
|---|---|---|
| loop position | `for.first`, `for.last`, `for.index`, `for.even`, `for.odd` | as Scriban gives them |
| an item's or node's state | `s.state == "completed"` | the closed set `completed`, `skipped`, `not_run` |
| whether a check passed | `check.coverage.value.pass` | `true` or `false` |

- The tests combine with `!`, `&&`, `||` and parentheses.
- A `state` is compared only with a literal from the closed set.
- **Testing anything else is refused:** a data value, an input, a node's text, a run fact. The one
  exception is a renderer's body, which may test its own `value`: a renderer decides nothing that
  is recorded, since its whole output is a function of `value`. The sentence points to the header
  forms: a part, a snippet's `if` or a macro's `if`.
- **Completeness:** an `if` that branches on a `state` must handle every state or end with an
  `else`, which keeps the template safe when a state is added later.

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

- R-D7 (S05-007): *"\<Subject\> tests \<expr\> in a body if at line \<n\>; a body if tests only loop position, state and whether a check passed. Decide it in a header: a part, a snippet's if or a macro's if."*

- R-D8 (S05-009): *"\<Subject\> branches on \<expr\> and handles \<states\>, but not \<missing\>: add it or an else."*

- R-D8, for example (S05-008): *"Deliverable 'consult' branches on part.state and handles completed and skipped, but not not_run: add it or an else."*

- R-D9 (S05-010): *"\<Subject\> compares \<expr\> with "\<value\>" at line \<n\>; a state is completed, skipped or not_run."*

## 5. Limits

The limits are dialect constants, separate from `FormatBounds`
([`bounds.json`](bounds.json)).

| Limit | Value | Past it |
|---|---|---|
| iterations per `for` | 1,000 | the render fails with a sentence (R-L1) |
| `if` and `for` nesting | 15 deep | refused at publish (R-L2) |
| rendered output | 1 MiB (1,048,576 bytes, UTF-8) | the render fails with a sentence (R-L3) |
| steps per render | 100,000, an engine setting | the render fails with a sentence (R-L4) |
| recursion | none possible | there is no `func` or `include`; snippet cycles are refused at publish |

A render failure fails the node (or the deliverable) as a definition error: no retry. A prompt that
fails to render is never sent. The failure follows the node's normal failure path, not `onInvalid`,
which is about replies.

- R-L1 (S05-012): *"\<Subject\> stopped rendering: the for at line \<n\> reached 1,000 iterations."*

- R-L2 (S05-013): *"\<Subject\> nests if and for \<n\> deep at line \<m\>; the limit is 15."*

- R-L3 (S05-014): *"\<Subject\> stopped rendering: its output passed 1 MiB."*

- R-L4 (S05-062): *"\<Subject\> stopped rendering: it took more than \<limit\> steps."*

## 6. Renderers in a template

The one call form is the pipe to the root `renderer.`: `{{ node.x.value | renderer.concept_bullets }}`.
Chaining is allowed where a template uses renderers, and each step is checked against the next
renderer's `input`. A renderer's own body may not pipe into another renderer.

- R-N4 (S05-030): *"\<Subject\> calls renderer.\<id\> at line \<n\>; pipe into it: \<value\> \| renderer.\<id\>."*

- R-N7 (S05-033): *"Renderer '\<id\>' pipes into renderer.\<other\> at line \<n\>; chain renderers where they're used, not inside a renderer."*

## 7. Placements and whitespace

A **placement** is an output tag whose expression is a unit: `snippet.<id>.content`, `part.<id>` or
`macro.<id>` (each possibly qualified, `snippet.<folder>.<id>.content`). A snippet's text is read as
`.content`; it is a placement because, like a part or a macro, it may be absent. Its text is
entirely the author's: no rule on how it starts or ends.

| Written | Result |
|---|---|
| `{{~ x }}` alone on its line, nothing after it | **allowed** (a block). When the unit is absent, an empty line remains. |
| `{{ x }}` anywhere inside a line, including against a word (`diabetes{{ x }}.`) | **allowed** (inline). Nothing is removed. |
| `{{ x }}` alone on its line | allowed: the indentation before it stays. The Editor writes `{{~ x }}` when inserting on an empty line. |
| `~}}` on a placement | refused: it removes the line's newline, joining two lines (R-W1) |
| `-` on a placement (`{{- x }}`, `{{ x -}}`) | refused: it removes blank lines between paragraphs (R-W2) |
| `{{~ x }}` inside a line | refused: it removes the space the author wrote before it (R-W3) |
| `{{~ x }}` with text after it on its line | refused: a block placement stands alone on its line (R-W4) |

Scriban's markers, as tested on 7.2.5: `~` removes spaces and tabs on its side, and on the right also
the one newline ending the line; `-` removes all whitespace on its side, blank lines included.

**Statements and ordinary outputs** (`if`, `for`, `else`, `end`, `{{ node.x.content }}`) may use `~`
on either side, as the renderer templates need for byte-exact output. **`-` is refused on every
tag,** not only placements, because it removes blank lines no preview explains (R-W5).

- R-W1 (S05-015): *"\<Subject\> places \<unit\> with ~}} at line \<n\>; it removes the line's newline, joining two lines. Use {{~ \<unit\> }} alone on a line."*

- R-W2 (S05-016): *"\<Subject\> places \<unit\> with - at line \<n\>; it removes blank lines between paragraphs."*

- R-W3 (S05-017): *"\<Subject\> places {{~ \<unit\> }} inside a line at line \<n\>; it removes the space before it. Use {{ \<unit\> }}."*

- R-W4 (S05-018): *"\<Subject\> has text after {{~ \<unit\> }} at line \<n\>; a block placement stands alone on its line."*

- R-W5 (S05-019): *"\<Subject\> uses - at line \<n\>; it removes blank lines between paragraphs. Use ~."*

**A snippet is read as `snippet.<id>.content`;** a bare `snippet.<id>` is refused.

- R-S3 (S05-037): *"\<Subject\> reads snippet.\<id\> at line \<n\>; read its text as snippet.\<id\>.content."*

## 8. The marker

**The marker is `macro.<id>.content`** (qualified: `macro.<folder>.<id>.content`). Each macro
instruction contains its own macro's marker **exactly once**, in one of two forms, and no other
macro's marker:

| Form in the instruction | What the model must write |
|---|---|
| `{{~ macro.<id>.content }}` alone on a line of the instruction | the marker alone on its own line (a block) |
| `{{ macro.<id>.content }}` inside a line | the marker inside a sentence (inline) |

When the instruction is rendered, **its marker renders as its own literal source text**
(`macro.<id>.content` between its braces), so the model sees exactly the marker to write. The
dialect treats the marker as literal inside an instruction. A macro body holds no marker. The
model's reply is never rendered: the engine replaces exact marker strings literally.

- R-M3 (S05-044): *"Macro '\<id\>' has \<n\> markers in its instruction; it must hold {{~ macro.\<id\>.content }} or {{ macro.\<id\>.content }} exactly once."*

- R-M4 (S05-045): *"Macro '\<id\>' has the marker of macro '\<other\>' in its instruction."*

- R-M9 (S05-051): *"Macro '\<id\>' has a marker in its body; a body is the text that replaces the marker."*

The reply is checked against the markers it was asked for; each of these goes to the node's
`onInvalid`:

- V-1 (S05-053): *"The reply has no marker for macro '\<id\>'."*

- V-2 (S05-054): *"The reply has the marker for macro '\<id\>' \<n\> times."*

- V-3 (S05-055): *"The reply has a marker for macro '\<id\>', which wasn't offered."*

- V-4 (S05-056): *"The reply has a marker for '\<id\>', which isn't a macro."*

- V-5 (S05-057): *"The reply writes the marker for macro '\<id\>' \<inside a sentence \| alone on a line\>, but it was asked for \<alone on a line \| inside a sentence\>."*

- V-6 (S05-058): *"The reply has text after the marker for macro '\<id\>' on its line."*

- V-7 (S05-059): *"The reply has the markers out of order: '\<id\>' before '\<other\>'."*

## 9. Run spots

An output expression that reads `run.*` reads nothing else, for example
`{{ run.date | date.to_string "%d %B %Y" }}`; each such expression is a **run spot**, which may pipe
to built-ins and to renderers. A body's read of a run-dependent value is a run spot too. Run facts
cannot be tested in a body `if`, cannot feed a `for` and cannot be combined arithmetically. The
rendering of run spots and the two hashes are in [chapter 5 § 4](../package-format-v31.md#54-run-spots-and-the-two-hashes).

- R-R5 (S05-024): *"\<Subject\> reads \<path\> and run.\<fact\> in one output at line \<n\>; an output that reads a run fact reads nothing else."*

The advance warning, which is not a refusal:

- W-1 (S05-060): *"\<Subject\> reads \<run.fact or run-dependent value\> at line \<n\>. Its main hash differs between runs; runs are compared on the run-neutral hash."*

## 10. Feature, allowed or refused, sentence

| Feature | Allowed or refused | Sentence |
|---|---|---|
| output `{{ x }}`, member access, literals | allowed | none |
| `for` over a list, with `for.first`, `for.last`, `for.index`, `for.even`, `for.odd` | allowed | none |
| `for` over a range or an object | refused | R-D6 (S05-006) |
| `for` options `limit:`, `offset:`, `reversed`; `for.rindex`, `for.length`, `for.changed` | refused | none of their own |
| `if`, `else if`, `else` on loop position, state and check pass | allowed | none |
| `if` on anything else | refused | R-D7 (S05-007) |
| a state compared with a value outside `completed`, `skipped`, `not_run` | refused | R-D9 (S05-010) |
| an `if` on a state that misses a state and has no `else` | refused | R-D8 (S05-009) |
| pipe to an allowed built-in or to a renderer | allowed | none |
| renderer call form `renderer.x(v)` | refused | R-N4 (S05-030) |
| a renderer's body piping into a renderer | refused | R-N7 (S05-033) |
| comment `{{# … }}`, raw block `{%{ … }%}` | allowed | none |
| assignment, `capture`, `func`, `include`, `import`, `with`, `wrap`, `while`, `break`, `continue`, `case`, `tablerow` | refused | R-D1 (S05-001) |
| arithmetic and string concatenation by `+` | refused | R-D1 (S05-001) |
| index access `list[0]` | refused | R-D11 (S05-063) |
| reading a member the format or root does not have | refused | R-D10 (S05-011) |
| `string.upcase`, `string.downcase`, `string.capitalize`, `string.strip`, `array.join`, `array.size`, `date.to_string` | allowed | none |
| any other built-in, `date.now`, random numbers, environment access | refused | R-D2 (S05-002) |
| `truncate` | refused | R-D3 (S05-003) |
| `object.default` | refused | R-D4 (S05-004) |
| `date.to_string` without a pattern | refused | R-D5 (S05-005) |
| more than 1,000 iterations of a `for` | the render fails | R-L1 (S05-012) |
| `if` and `for` nested deeper than 15 | refused | R-L2 (S05-013) |
| output past 1 MiB | the render fails | R-L3 (S05-014) |
| more than the step limit | the render fails | R-L4 (S05-062) |
| `{{~ x }}` alone on a line; `{{ x }}` inline or alone on a line | allowed | none |
| `~}}` on a placement | refused | R-W1 (S05-015) |
| `-` on a placement | refused | R-W2 (S05-016) |
| `{{~ x }}` inside a line | refused | R-W3 (S05-017) |
| text after `{{~ x }}` on its line | refused | R-W4 (S05-018) |
| `-` on any other tag | refused | R-W5 (S05-019) |
| `~` on a statement or an ordinary output | allowed | none |
| bare `snippet.<id>` | refused | R-S3 (S05-037) |
| the marker as literal text in an instruction, exactly once | allowed | none |
| a macro instruction with other than one marker | refused | R-M3 (S05-044) |
| another macro's marker in an instruction | refused | R-M4 (S05-045) |
| a marker in a macro body | refused | R-M9 (S05-051) |
| an output that reads a run fact and another value | refused | R-R5 (S05-024) |
| a run spot | allowed, with a warning | W-1 (S05-060) |
