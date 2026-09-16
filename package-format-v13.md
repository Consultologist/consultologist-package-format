# Workflow Package Format — specVersion 13 (Declarable Content: the Transcript Slot, the Form Slot)

Normative specification for `specVersion: 13` packages (design and rationale:
[#728](https://github.com/Consultologist/Consultologist-Blazor/issues/728)).
Everything not stated here is unchanged from
[package-format-v12.md](package-format-v12.md): the value types, the macro
grammar, the check and template nodes, and everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13}**. v5–v12 packages keep validating
and executing under their frozen rules. A v12 package is a v13 package with
**one** edit (see *Migration*): nothing v13 opens is required.

What 13 opens, in one sentence: an input slot may declare the **content
channel** it expects — a **transcript** or a **form** — beside its value
`type`, so the package states intent, the client renders the right control,
and a declared transcript stamps its provenance origin from the declaration
itself.

## `inputs[].expectedContent` — the declared channel

An input slot may carry `expectedContent`, a string from the closed set
**`transcript`** | **`form`**. It is **distinct from `type`**, which stays
the value kind: `expectedContent` names the *medium or source*, not the
shape of the value.

```yaml
inputs:
  - { id: meeting_transcript, label: Meeting transcript, type: text,
      expectedContent: transcript }
  - { id: encounter_kind, label: Encounter kind, type: enum,
      values: [new_patient, follow_up], expectedContent: form }
```

**`transcript`** — the slot expects an uploaded document that is a meeting
transcript. Its value is the document's extracted text, so the slot's `type`
must be **`text`** (or an **array of text**, for several transcripts); any
other type is refused by name. A transcript is read exactly as any document —
same extractor, same digests — and only its provenance origin differs: a slot
declaring `expectedContent: transcript` stamps the `transcript` origin for the
documents supplied to it, with **no caller assertion required**. As under v12,
transcript-ness is a declaration, never read from the bytes: a transcript and
a document carrying identical text have equal `effectiveInputHash`.

**`form`** — the slot's value is meant to be filled from a held form response,
coerced to the slot's declared value `type` and stamped the `form-response`
origin (the v12 mechanism). Because the answer coerces to a value, the slot's
`type` may be any value type **except `object`** (and not an array of
objects); those are refused by name. A `form` slot may still be typed by hand,
in which case the value is ordinary typed text and carries no `form-response`
origin — the declaration expresses intent, it does not compel the source.

Both `transcript` and `form` are refused by name on a manifest below 13, the
way any section a version does not have is an error rather than a silently
ignored field.

## Provenance (normative bytes)

**No hash definition moves.** `expectedContent` never enters
`effectiveInputHash`, and the transcript origin stays outside it exactly as
v12's rule says. What changes is only *who* drives the `transcript` origin: a
declared transcript slot does, in addition to the caller's runtime assertion.
No new origin kind is introduced — `transcript` and `form-response` are the
kinds v12 already defined; the provenance registry entry for `inputOrigins`
is clarified, not versioned.

**The control:** a v13 package using nothing v13 opens renders and hashes
**byte-identically** to its v12 self — no slot declares a channel, no origin
moves. The conformance case `v13-minimal-is-v12-plus-a-line` is that statement
as a fixture.

## Migration

A v12 package becomes a v13 package with one edit: `specVersion: 13`. Nothing
v13 opens is required. `general` is the control — published at 12 and at 13
with no other change, byte-identical output and hashes across the step. A slot
adopts a channel by adding `expectedContent` to an otherwise unchanged input.
