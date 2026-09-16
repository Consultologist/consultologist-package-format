# Workflow Package Format — specVersion 16 (Image Inputs: the `image` Channel)

Normative specification for `specVersion: 16` packages (design and rationale:
[#730](https://github.com/Consultologist/Consultologist-Blazor/issues/730)).
Everything not stated here is unchanged from
[package-format-v15.md](package-format-v15.md): the raw prompt toggle, the union
types, the content channels, the value types, the macro grammar, the check and
template nodes, and everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}**. v5–v15 packages keep
validating and executing under their frozen rules. A v15 package is a v16
package with **one** edit (see *Migration*): nothing v16 opens is required.

What 16 opens, in one sentence: a slot may declare **`expectedContent: image`**,
a third content channel beside `transcript` and `form` (added in v13).

## `inputs[].expectedContent: image`

`image` joins the closed set of content channels a slot may expect. Like
`transcript`, it is a **text** channel: the submitter uploads a raw image
(PNG/JPEG/TIFF), the engine reads it into text by OCR, and that text fills the
slot. So `image` is accepted **only on a text slot or an array of text**; on any
other value type it is refused by name.

`expectedContent` remains **intent, label, and publish-time validation** — it
does not gate extraction. The engine OCRs any uploaded image by its bytes
whether or not a slot declared `image`, exactly as it extracts a PDF without a
declaration; a slot that declares `image` states what it expects and renders the
matching hint, and a package that does not declare it still accepts an uploaded
image into a text slot. The three channels are otherwise independent: a slot
declares at most one.

**Refused by name:** `expectedContent: image` on a manifest below 16 (the image
channel is absent from the accepted set before 16); `image` on a slot that is
not a text slot or an array of text.

## Provenance (observed, not asserted)

An element read from an uploaded image is stamped with the input origin `kind`
**`image`** — a **server-observed** fact (the OCR extractor is the witness),
unlike `transcript`, which the submitter asserts. Precedence is
**image > transcript > document**: an OCR'd image stamps `image` whatever the
slot declared. This is recorded in the provenance record (`inputOrigins`,
provenance `v2026.09.10`) and, like the other origin kinds, is **out of the
effectiveInputHash** — it describes provenance, not the effective input.

**No hash definition moves.** A v16 package using nothing v16 opens validates,
renders, and hashes **byte-identically** to its v15 self — no slot declares
`image`. The conformance case `v16-minimal-is-v15-plus-a-line` is that statement
as a fixture.

## Migration

A v15 package becomes a v16 package with one edit: `specVersion: 16`. Nothing
v16 opens is required. A slot adopts the image hint by adding
`expectedContent: image` (on a text slot or an array of text); every other slot
is unchanged.
