# Workflow Package Format — specVersion 23 (Node Macros)

Normative specification for `specVersion: 23` packages (design and rationale:
[#955](https://github.com/Consultologist/Consultologist-Blazor/issues/955)).
Everything not stated here is unchanged from
[package-format-v22.md](package-format-v22.md): the content channels, the value
types, the macro grammar and placement on deliverables, the classifier, check and
template nodes, the node- and deliverable-level `when`, the inline macro slots,
schema references and custom schemas.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}**.
v5–v22 packages keep validating and executing under their frozen rules. A v22
package is a v23 package with **one** edit (see *Migration*): nothing v23 opens is
required.

What 23 opens, in one sentence: a node may carry a `macros` list — a library macro
(`manifest.macros`) **composed into that node's prompt**, before or after the
rendered template, each gated by the node-level `when`.

## The problem it solves

A macro (`manifest.macros`, v11) is reusable, token-templated, conditionally-placed
text. Until v23 a macro could only be attached to a **deliverable**
(`results[].macros[]`), where it shapes the **output** a reader receives. There was
no first-class way to attach reusable, conditional text to the **prompt a node sends
the model**. A **prelude** (the verbatim text prepended to a prompt) was the closest
tool, but it is single, always-on, verbatim and prompt-scoped.

v23 gives the existing macro a **second attachment site**: the node. A macro
attached to a node shapes the prompt the model sees, exactly as a macro attached to
a deliverable shapes the output the reader sees — one library, one token grammar,
one `when` grammar, two attachment sites. A prelude becomes the trivial node macro:
a bare entry, placed before, always.

## `nodes[].macros`

A node may declare a `macros` list. Each entry references a macro id from
`manifest.macros` and is, on the wire, either a **bare id string** (placed before
the prompt, always) or a **placement object**:

```jsonc
{
  "specVersion": 23,
  "macros": { "tool_guidance": "macros/tool_guidance.md" },
  "nodes": [
    { "id": "draft-section", "prompt": "draft-section",
      "macros": [
        "tool_guidance",
        { "id": "ap_guardrails", "at": "after", "when": "node:scope == in_scope" }
      ] }
  ]
}
```

A placement object carries:

- **`id`** *(required)* — a macro id declared in `manifest.macros`.
- **`at`** — `"before"` or `"after"` the rendered prompt. Omitted means **before**.
- **`when`** — an optional condition in the **node-level grammar** (identical to a
  node's own `when`: `input:` operands and `node:<classifier>` operands). Omitted
  means the macro always applies. A `when` that names a classifier makes that
  classifier a prerequisite of the node (see *Execution*).
- **`optional`** — reserved; a node macro is composed whenever its `when` holds.

The macro's text is token-substituted with the same grammar a deliverable macro
uses — `{{input:…}}`, `{{data:…}}`, `{{classification:…}}`, `{{run:…}}`,
`{{profile:…}}` — and composed around the prompt: `before` blocks precede the
rendered template, `after` blocks follow it, one blank line between each. The
composed prompt is what the engine hashes and attests for the node.

## Execution

A node macro is resolved when the node's activity is dispatched: its `when` is
judged (an `input:` operand against the supplied inputs, a `node:` operand against
the classifier's answer), and if it holds the macro text is substituted and
composed. Because a classifier-gated node macro reads a classifier's answer, that
classifier is a **scheduling dependency** of the node — the node does not run until
the classifier has answered, so the gate is judged against a known value.

## Validation

A v23 package is refused when:

- a node's `macros` list is present and `specVersion` < 23;
- a node macro's `id` is not declared in `manifest.macros`;
- a node macro's `at` is a value other than `before` or `after`;
- a node macro declares `macros` on a node that has **no prompt** to compose into;
- the same macro is listed more than once in the same place on one node;
- a node macro's `when` is not a valid node-level condition;
- a declared library macro is referenced by **no result and no node** (the orphan
  rule, which now counts node attachments).

All v5–v22 closures continue to hold. A prelude is still valid at v23; a package
may carry both preludes and node macros.

## Migration

A v22 package becomes a v23 package by setting `specVersion: 23`. No `macros` entry
on a node is required; a v23 package with none behaves exactly as the v22 package it
was. To compose a macro into a node's prompt, declare it in `manifest.macros` (or
reuse one) and add its id to the node's `macros` list.
