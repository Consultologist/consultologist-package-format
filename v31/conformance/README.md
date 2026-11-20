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
