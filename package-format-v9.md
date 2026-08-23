# Workflow Package Format — specVersion 9 (Structured Inputs, Caller-Data Fans, Package Metadata)

Normative specification for `specVersion: 9` packages, as implemented by
the #419 ladder (#421–#429), #432, #434 and #453 (design and rationale:
[package-format-v9-design.md](https://github.com/Consultologist/Consultologist-Blazor/blob/d738210414a8d0bec1104d1c735c19912ee798b9/docs/customizable-workflow/package-format-v9-design.md),
including the dated amendments where the design changed in the doing).
Everything not stated here is unchanged from
[package-format-v8.md](package-format-v8.md): typed inputs with `values`,
conditional deliverables, the result set and its reachability, delivery,
CalVer, immutability, `derivedFrom`.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9}**. v5–v8 packages keep validating and executing
under their frozen rules. A package needs 9 only when it uses what 9 opens
— with one exception: `tags` is **required** at 9, so the minimal migration
is **two** edits (see *Migration*), not one.

## `type` — three more shapes

`type` still defaults to `text`, so a v8 `inputs` block is a valid v9 one.
The vocabulary grows to `text`, `date`, `enum`, `boolean`, `number`,
`object`, `array`:

```yaml
inputs:
  - id: length_of_stay
    label: Length of stay (days)
    type: number
    required: false

  - id: patient
    label: Patient record
    type: object
    required: false
    fields:
      - id: family_name
        label: Family name
      - id: age
        label: Age
        type: number

  - id: prior_notes
    label: Prior notes
    type: array
    items: text
    required: false

  - id: medications
    label: Medications
    type: array
    items: object
    required: false
    fields:
      - id: name
        label: Drug
      - id: dose
        label: Dose
```

- `items` is **required for `array` and forbidden otherwise**; its value is
  one of `text`, `date`, `enum`, `boolean`, `number`, `object`.
- `fields` is **required when the declared shape is an object** — either
  `type: object` or `items: object` — and forbidden otherwise. A field is
  declared with the vocabulary an input uses: `id` (snake_case), `label`,
  optional `type`, optional `required`, and `values` when its type is
  `enum`.
- `values` belongs to `enum` — on an input, on an array of enums, and on an
  enum field — with the v8 rules unchanged: at least two entries, unique,
  each matching `^[a-z][a-z0-9_]*$`.
- **Structure is exactly one level deep.** A field's type may not be
  `object` or `array`, and `items: array` is refused. This keeps
  canonicalisation finite, the intake form a repeating row rather than a
  tree, and a condition path two segments.

Declaring `number`, `object` or `array` — or `items`, or `fields` — on a
manifest below 9 is an error naming the version, never an ignored field.

### Wire form (normative)

| type | wire form | rejected |
|---|---|---|
| `text` | JSON string, within the 256 KB cap | a boolean, a number, a structure |
| `date` | JSON string, ISO 8601 calendar date `YYYY-MM-DD` | any other spelling, including valid-but-different (`2026-8-1`) |
| `enum` | JSON string, exactly one of the declared `values` | anything outside the set |
| `boolean` | JSON `true` / `false` | a string, including `"true"` |
| `number` | JSON number, plain decimal | a string, including `"3"`; exponent form (`1e3`); a leading `+`; a leading zero (`007`) |
| `object` | JSON object whose keys are exactly the declared field ids | a missing required field; any undeclared key; a nested object or array |
| `array` | JSON array, every element satisfying `items` | a null element; an element of the wrong kind |

**A number is a decimal, not a float.** Values are carried and compared as
decimals, so `0.1` is the value the caller sent rather than the nearest
double, and two callers who sent the same digits hash identically. A value
outside decimal range is refused rather than rounded. The canonical
spelling is **the digits as sent, minus nothing**: `1.50` is not trimmed to
`1.5`, because trimming would mean provenance records a value nobody sent.

**An empty array is present and empty**, not absent. Supplied for a
required input it is refused at start, naming the slot; absent optionals
stay absent.

The 400-versus-422 rule is unchanged: a token JSON cannot carry at all is a
400; a well-formed value disagreeing with the declaration is a 422 naming
the slot.

### Rendering

Structured values enter the template engine as their own kinds:

```
{{ for note in prior_notes }}
--- prior note ---
{{ note }}
{{ end }}

{{ patient.family_name }}, age {{ patient.age }}
{{ if length_of_stay > 7 }}Prolonged admission.{{ end }}
```

- An **object** enters as a script object with exactly its declared
  fields, each rendering as its own type — a `date` field formats as a
  date does.
- An **array** enters as a script array, in the order the caller sent.
- A **number** renders as its canonical spelling — no thousands
  separators, no locale.
- An **absent optional array renders as an empty array**, an absent
  optional object as an **empty object**, and an absent optional number as
  null. **An empty array is falsy** in this engine's templates, so
  `{{ if x }}`, `{{ if x.size > 0 }}`, `{{ for … }}` and `{{ x.field }}`
  behave alike on absence and on emptiness, and agree with `when:`.

The publish-time probe renders every prompt with typed probes — a number as
a number, an object carrying its declared fields, an array as a
**two-element** array of its element probe, so a template that assumes a
singleton fails the probe rather than the job.

### Reachability by email (warning)

Email supplies text, so a required `number` or `object` input is
unreachable by email the way a required `boolean` already was, and
publishing warns on the same terms. A required **array of `text` is
reachable**: attachments fill it, as numbered stems (below).

## `title`, `description` and `tags` — package metadata

Three top-level manifest fields, all arriving at 9. On a v8-or-earlier
manifest each is refused by name — a section the version does not have is
never a silently ignored field.

```json
"title": "Breast oncology consults",
"description": "Referral triage and consult notes for the breast clinic.",
"tags": ["oncology", "Breast", "new-patient"]
```

- `title`: optional; when present, non-empty, a single line, at most 80
  UTF-16 code units. `description`: optional; when present, non-empty, at
  most 500. **The fallback is the ref, stated rather than assumed**: every
  surface that shows a title shows the ref when there is none. No
  uniqueness rule; surfaces disambiguate by showing the ref beside the
  title.
- `tags`: **required** — an array of labels the package is found by, and
  `[]` is how a package says it has none. `null` is never a spelling of
  "none" on a v9 manifest: every v9 manifest states its tags, so a reader
  never wonders whether absence was a choice. Each tag is trimmed,
  non-empty, a single line, at most 32 UTF-16 code units; at most 20 tags;
  **distinct ignoring case** (a filter treats `Oncology` and `oncology` as
  one); **order as authored, never sorted**. Validation names the position
  (`tags[2] must not be empty.`), never the text.
- All three are **authored package content**, the safety class of a label:
  written at publish, never per consult, so safe on every surface.
- **A fork across names starts with no metadata**: the registry clears
  `title` and `description`, and clears `tags` to `[]` — a v9 manifest must
  state them. A republish of the same package keeps all three.
- The title and tags a job ran under are stamped on its record at start
  (`packageTitle`, `packageTags`); the ref remains the provenance.

Lengths count UTF-16 code units (`string.Length`), the count the validator
enforces; the published schema's `maxLength` counts code points and is
looser only for astral characters. The engine is the authority.

## `forEach` over an input

`forEach` accepts `data:<id>` as before, and now `input:<id>` where the
named input is declared `type: array`:

```yaml
nodes:
  - id: summarise-note
    label: Summarising a prior note
    forEach: input:prior_notes
    prompt: summarise-note
    bindings:
      note: item:value
```

- **One item shape for every caller element — `{ id, name, value }`.**
  `id` is the element's zero-based index, minted by the engine — never a
  declared field. `name` is the input's label and the element's ordinal
  ("Prior notes 2"), never the element's text, because a block name
  reaches history events and progress payloads and an element is patient
  data. `value` is the element: a scalar's canonical string, or an object
  element, which the renderer materialises — a node binds `item:value` for
  either kind and writes `{{ m.dose }}`.
- Binding any other `item:` field under an input fan is refused: an input
  fan's items carry `id`, `name`, `value` and nothing else.
- Fanning an undeclared input, or a non-array input, is refused at
  publish. Below 9, `forEach` must be a `data:` collection reference.
- **Array order is the caller's, is significant, and is recorded**: it is
  the order the elements hash in, so an item's identity is stable across a
  replay for the same reason the hash is.
- **The empty fan**: a job whose fanned input has no entries produces no
  items, no blocks, no document — v8's empty-fire-set case in different
  clothes. It is refused at start, naming the input, and leaves a job
  record born Failed carrying every declared deliverable as not produced
  with the fan's sentence as its reason. Because an *absent* optional
  array fans to nothing too, a fanned input should be required, and
  publishing a fanned optional input **warns**.
- `TotalBlockCount` stays a stored scalar, stamped once at start: a
  caller-supplied array arrives with the request, so the item count is
  knowable before anything runs. Per-result reachability is unchanged, and
  an input fan is a fan for that rule's purposes.

## `when` — the widened grammar

The closed grammar grows once, and is still not an expression language:

```
when     := <operand> | <operand> <op> <literal>
operand  := <input-id> | <input-id>.<field-id> | count(<input-id>)
op       := == | != | > | < | >= | <=
literal  := true | false | <enum-value> | <number> | YYYY-MM-DD
```

- **Ordering operators are for ordered types only** — `number` and `date`.
  Applied to an enum or a boolean they are refused at publish, naming the
  type. `date` gains ordering, which v8's erratum anticipated:
  `when: seen_on >= 2026-01-01` is a choice.
- **Text is still not comparable**, on an input or on a field.
- **A path reads one field of one object**, and the field is a scalar —
  which the declaration rules guarantee, since fields cannot nest.
- **`count()` is the only function, and it is named in the grammar.** Its
  operand is an array input, its value a non-negative integer, and it
  composes with the six operators against a whole-number literal.
- **The bare form is a truthiness test**, admitted for a `boolean` and for
  an `array` (non-empty); refused for every other type, which must compare
  explicitly.
- **Still no `and`/`or`, and no arithmetic.**
- Literals are held to the operand's type: a number literal is a plain
  decimal, a date literal is `YYYY-MM-DD`, a boolean compares to `true` or
  `false`, an enum literal must be a declared value. A whole object or
  array is not compared; its fields, or its count, are.

Evaluation is unchanged: **once, at job start, against the supplied
inputs**. Absence is three-valued — a condition on an absent input does
not hold, and a path into an absent object does not hold rather than
erroring — with one stated exception: **`count()` of an absent optional
array is zero**, because "no entries supplied" and "an empty list
supplied" answer the same clinical question, so
`when: count(prior_notes) == 0` holds when the slot was left empty.

When no document applies, the job is refused at start and **leaves a job
record born Failed**, carrying the deliverables that did not apply and the
condition each wanted. The explanation prints only what is safe on every
surface — a declared enum value, `true`/`false`, the condition's own
literal, a count of entries. A number, a date, or a field's value is the
patient's and is never printed: the sentence says what was needed and that
it was not met, never what was supplied.

## Several documents for one slot (request contract)

These rules bind the request, not the manifest — they are enforced at the
doors, at start time.

- **A slot maps to a list of documents.** A slot declared
  `type: array, items: text` may be filled by several documents; each is
  extracted and becomes one element, in the order supplied. A `text` slot
  given several documents is **refused, not concatenated** — declare an
  array of text to supply several.
- **Payloads carry no filename**, deliberately: a filename can itself be
  patient data.
- **Provenance is per document, positionally**: `origins[id][i]` describes
  element `i`, and a job's record shows one row per document. Ordinals in
  sentences count from one ("document 2 of 4"); indexes stay 0-based.
- **Two caps compose**: each extracted document is bounded as before, and
  the slot's total is bounded by an **aggregate cap** checked after
  extraction. Over the cap is refused, never truncated — a consult written
  from most of a referral with nothing saying so is the worst available
  outcome.
- **The content floor applies to the slot**, not the element, and measures
  an array of text however it was supplied.
- **Order is the caller's** and the intake preserves it. By email, order
  is written as numbered stems — `prior_notes-1.pdf`, `prior_notes-2.docx`
  — numbered 1 to n with no gaps or repeats.
- Archives are out of scope, deliberately.

## Provenance (normative bytes)

**Effective-input hash, definition 5** — SHA-256 of the canonical JSON of
the supplied inputs, where canonical means, byte for byte:

- **UTF-8 written as-is**, with only what JSON itself requires escaped.
  This is where definition 5 parts from 2–4, which use a default encoder
  that escapes non-ASCII and `<`, `>`, `&`, `'`, `+` as `\uXXXX`; 4 and 5
  agree byte for byte on an ASCII map of scalars and on nothing wider,
  which is fine — definitions are never compared across versions.
- Top-level slot ids **ordinal-sorted**; object field keys
  **ordinal-sorted at every level**. Ordinal means UTF-16 code-unit order.
- **Array elements in supplied order**, which is significant and is the
  caller's.
- **Numbers in their canonical spelling** — the digits as sent.
- Absent optionals omitted.

Definition 5 is therefore **not RFC 8785 (JCS)-conformant** — JCS
normalises numbers, and this definition deliberately keeps the caller's
spelling — and this document says so rather than letting "canonical JSON"
imply it. (Its ordinal sort is RFC 8785's rule; the number rule is not.)

v9 jobs stamp `effectiveInputHashVersion: 5`; v8 keeps 4, v7 keeps 3,
v5/v6 keep 2. Definition 4 refuses structure outright: its domain is v8's
scalars, so a structured value reaching it fails the start rather than
producing a record that is wrong and says it is right.

**Workflow-output hash: unchanged** (`ResultSetHashVersion` 3 covers v9 —
documents produced from caller-supplied items are documents like any
other). **No new hash for the item set**: the items are derivable from the
supplied inputs and the pinned package, both already recorded. The node
input hash is unchanged and quietly does more work — it is SHA-256 of the
rendered prompt, so two items that rendered identically are visibly
identical.

## Migration

A v8 package becomes a v9 package by changing `specVersion` **and adding
`"tags": []`** — two edits, nothing else. Tags are required at 9, so the
one-line migration of earlier rungs gains exactly one more line; the
editor's *Upgrade to specVersion 9* writes both. `general` did exactly
this, which is what makes it the control: its rendered output is
byte-identical to its v8 predecessor's, the effective-input hash version
moves 4 → 5, and the output hash does not — the assertion that inputs were
re-defined and outputs were not.
