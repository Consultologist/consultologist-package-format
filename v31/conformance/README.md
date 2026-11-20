# specVersion 31 conformance examples (preview)

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

These rules of part 02 are left to the validator and have no invalid example here:

- every declared property is listed in `required`, and `required` lists nothing else (§ 3.3);
- a nullable scalar written with `anyOf` instead of a type array (§ 3.2);
- a `$ref` that names no format, or that reaches its own definition (§ 3.1, § 6.3);
- an `enum` value that is not snake_case, and duplicate or empty `oneOf` titles (§ 9);
- a text format missing its `contentMediaType` or `x-markdown` (§ 5.1);
- strict mode's size limits and an `anyOf` at the root of a format sent to a model (§ 3.3).
- Readings of the design: an `enum` or a labelled `oneOf` must sit beside an explicit string
  `type` (the design says "on a string" and always writes the type); a `$defs` name is any name
  without a `/`, not bound by the id pattern.

The `formats` check group does enforce the first of these on the built-in formats.

## Open points found while writing

- **`check_result`'s nullable arrays.** Part 06 § 2.1 writes `uncovered` and `untested` as
  `{ "type": ["array", "null"], "items": … }`, a type array of a non-scalar plus `null`, while
  part 02 § 3.2 keeps type arrays for scalars. The built-in keeps part 06's shape, and the
  dialect's meta-schema admits `"array"` (and `"object"`) in a type array beside `"null"`. For
  the PR's *Decisions made during build*.
- **A nullable `date`.** The dialect allows `format: "date"` only beside `"type": "string"`
  (part 02 § 3.1), so `"type": ["string", "null"]` with `format: "date"` is refused. Part 02 does
  not say whether an optional date is written some other way.
- **Nine shared flow members, not eight.** Part 04 § 1 says "Members every flow node's `index.json`
  has" and part 04 §§ 2.1, 3.1, 5.1 and 5.2 count "§ 1's eight members", but § 1's table lists nine
  (`kind`, `label`, `description`, `format`, `reproducible`, `producer`, `modelDerived`,
  `runDependent`, `profileCarrying`). All nine are required, so a `for` has seventeen members, a
  `while` fifteen, an `if` and a `case` twelve (the printed sixteen, fourteen and eleven count eight).
- **Header examples that omit members.** Part 01 § 4's agent header ends in `…`; part 05 § 7.2's
  `section_instructions` ends in `…` (it omits `if`); part 04 § 7.7's `call` ends "plus part 01's
  remaining leaf members" (it omits `if`); part 04 §§ 7.6 and 7.10's computed nodes omit
  `description`, `reproducible` and `if`; part 01 § 4's `plan` header omits `reproducible`, `if`,
  `onInvalid`, `failIfEmpty`, `parts` and `ordered`. The member tables (part 01 § 5.2, part 05 § 1.2) make
  every one required, so each valid instance writes them out: `if` and `description` as `null`,
  `reproducible` as the table's value, and, for `plan`, `onInvalid` as `"retry"` (a made-up value:
  part 05 § 1.2 says "as at version 30" and gives no value to copy).
- **An agent node carries `if`.** Part 01 § 5.1 puts `if` on every production leaf, and part 01
  § 5.2 lists it for an `agent` node, but part 05 § 1.2's table of an agent's prompt members does not
  repeat it. The schema requires it.
- **`derivedFrom`.** The brief's member list gives `derivedFrom` as `null`; part 01 § 3 types it a
  string or `null` (the `name@version` the package was copied from). The schema follows part 01 and
  accepts any string; the `name@version` shape is not stated, so it is not enforced.
- **A deliverable's `format`.** Part 06 § 6.1 allows `markdown_block`, `plaintext` or an object
  format and refuses `markdown_inline`. A schema cannot tell an object format's name from any other
  name, so the schema takes any id except `markdown_inline`; the checker holds the rest.
- **A test's value shapes.** Part 07 § 8.1 and § 8.3 type some values loosely. The schema reads
  a profile field's value as a string (part 06 § 10.1 lists them as `string` and `plaintext`), a
  `hash` as `sha256:` and 64 lowercase hex digits (the shape of every hash in the design; the
  design prints `"sha256:…"`), a `stopped` and a decision's branch id as strings, and a row key
  as a rooted key with an optional `:` and `/`-joined item path. An `inputs` value and a `values`
  value are any JSON.
- **Rules a schema cannot state** (left to the checker, no invalid example here): that `ret` names a
  direct child of its own body; that a `case` branch's `when` values belong to the subject's enum
  and appear in one branch only; that a `case` without an `else` lists every value; that `with` names
  every parameter of the function and no other; that `in` names a list and `itemLabel` a string field
  of its elements; that `channel` suits the input's format (part 02 § 8.3); that a description is at
  most 500 code points joined; and that every `reproducible`, `modelDerived`, `runDependent` and
  `profileCarrying` equals its derived value, where the schemas fix only the values the design fixes
  by kind (an agent node, a rendered node, a computed node and a check).
