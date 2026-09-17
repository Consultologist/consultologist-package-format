# Workflow Package Format — specVersion 17 (Ambient Notes: the `ambient-note` Channel)

Normative specification for `specVersion: 17` packages (design and rationale:
[#673](https://github.com/Consultologist/Consultologist-Blazor/issues/673)).
Everything not stated here is unchanged from
[package-format-v16.md](package-format-v16.md): the image channel, the raw prompt
toggle, the union types, the content channels, the value types, the macro
grammar, the check and template nodes, and everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}**. v5–v16 packages keep
validating and executing under their frozen rules. A v16 package is a v17
package with **one** edit (see *Migration*): nothing v17 opens is required.

What 17 opens, in one sentence: a slot may declare
**`expectedContent: ambient-note`**, a fourth content channel beside
`transcript`, `form` (v13), and `image` (v16).

## `inputs[].expectedContent: ambient-note`

`ambient-note` joins the closed set of content channels a slot may expect. Like
`transcript`, it is a **text** channel and a submitter assertion: the submitter
uploads a clinical note produced by an ambient scribe (e.g. Dragon Copilot), the
engine reads its text like any document, and that text fills the slot. So
`ambient-note` is accepted **only on a text slot or an array of text**; on any
other value type it is refused by name.

It is a **distinct channel from `transcript`** on purpose: an ambient note is an
AI-summarized visit draft, not the speaker turns of a meeting transcript, and
keeping them separate keeps the SaMD/anti-ambient boundary legible in the record.

`expectedContent` remains **intent, label, and publish-time validation** — it
does not gate extraction. A package that does not declare it still accepts an
uploaded note into a text slot (stamped `document`); a caller may also assert the
`ambient-note` origin per submission without any declaration. The channels are
otherwise independent: a slot declares at most one.

**Refused by name:** `expectedContent: ambient-note` on a manifest below 17 (the
channel is absent from the accepted set before 17); `ambient-note` on a slot that
is not a text slot or an array of text.

## Provenance (asserted, not observed)

An element read from a slot declaring `ambient-note` (or a submission the caller
marked as such) is stamped with the input origin `kind` **`ambient-note`** — an
**assertion** (the package's or the caller's), like `transcript` and unlike the
server-observed `image`, because whether a text is an ambient-scribe note cannot
be read from its bytes. Its server-observed fields are a `document`'s. This is
recorded in the provenance record (`inputOrigins`, provenance `v2026.09.11`) and,
like every origin kind, is **out of the effectiveInputHash** — an ambient-note
and a document carrying identical text have equal `effectiveInputHash` and differ
only in the origin `kind`.

**No hash definition moves.** A v17 package using nothing v17 opens validates,
renders, and hashes **byte-identically** to its v16 self — no slot declares
`ambient-note`. The conformance case `v17-minimal-is-v16-plus-a-line` is that
statement as a fixture.

## Migration

A v16 package becomes a v17 package with one edit: `specVersion: 17`. Nothing
v17 opens is required. A slot adopts the ambient-note hint by adding
`expectedContent: ambient-note` (on a text slot or an array of text); every other
slot is unchanged.
