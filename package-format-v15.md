# Workflow Package Format — specVersion 15 (Plain-Text Prompts: the Raw Toggle)

Normative specification for `specVersion: 15` packages (design and rationale:
[#731](https://github.com/Consultologist/Consultologist-Blazor/issues/731)).
Everything not stated here is unchanged from
[package-format-v14.md](package-format-v14.md): the union types, the content
channels, the value types, the macro grammar, the check and template nodes, and
everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}**. v5–v14 packages keep
validating and executing under their frozen rules. A v14 package is a v15
package with **one** edit (see *Migration*): nothing v15 opens is required.

What 15 opens, in one sentence: a prompt may declare **`raw: true`**, and its
text is then sent **verbatim** — no Scriban parse, no render, no strict variable
check.

## `prompts[].raw`

A prompt may carry `raw: true`. The engine emits the prompt's text **exactly as
written**: `{{ … }}` / `{% … %}`, JSON, math, and braces in clinical phrasing
all pass through untouched, where a rendered prompt would fail to parse or be
mangled. There is no templating, so:

- A raw prompt **declares no variables** (`variables: []` or omitted); a raw
  prompt naming variables is refused by name. Its referencing nodes therefore
  declare no bindings.
- The prompt's **prelude**, if any, still prepends (it is verbatim text, not a
  template).

`raw` is a property of the prompt's **text**, so it governs every node that
renders that prompt: a **prompt** or **classifier** node sends the verbatim text
to the model; a **template** node emits it verbatim as a deliverable block, with
no model call — the case where raw is most useful (a static letter or notice
with literal braces).

**Refused by name:** `raw` on a manifest below 15; a raw prompt declaring
variables.

## Provenance (normative bytes)

**No hash definition moves, and no record field is added.** A prompt's rawness
is part of the pinned package; the node's `outputHash` is over the rendered text
exactly as before — for a raw prompt that text is the verbatim source, hashed
the same way.

**The control:** a v15 package using nothing v15 opens renders and hashes
**byte-identically** to its v14 self — no prompt is raw. The conformance case
`v15-minimal-is-v14-plus-a-line` is that statement as a fixture.

## Migration

A v14 package becomes a v15 package with one edit: `specVersion: 15`. Nothing
v15 opens is required. A prompt adopts verbatim rendering by adding `raw: true`
(and dropping its variables); every other prompt keeps rendering through Scriban
exactly as before.
