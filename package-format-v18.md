# Workflow Package Format — specVersion 18 (Node Condition Gates: `when` on a node)

Normative specification for `specVersion: 18` packages (design and rationale:
[#822](https://github.com/Consultologist/Consultologist-Blazor/issues/822)).
Everything not stated here is unchanged from
[package-format-v17.md](package-format-v17.md): the content channels, the value
types, the macro grammar, the classifier, check and template nodes, the
deliverable-level `when`, and everything those carried forward.

A manifest declares the rule set it was validated under; the engine accepts
exactly **{5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}**. v5–v17 packages
keep validating and executing under their frozen rules. A v17 package is a v18
package with **one** edit (see *Migration*): nothing v18 opens is required.

What 18 opens, in one sentence: a **node** may declare **`when:`** — the same
condition grammar a deliverable's `when` speaks — and the node runs only when it
holds.

## `nodes[].when`

`when` on a node is the deliverable-level condition grammar (v8/v9/v10 §§ 5–6),
written on a node instead of a deliverable. Its operands are the ones every
condition reads — a declared input (`input:<id>`, with the v9/v10 path, `count()`
and arithmetic forms) and a classifier's answer (`node:<id>`, compared with `==`
/ `!=` against a declared value) — and it composes with `and` / `or` / `not`.
Its three-valued semantics are unchanged: a `when` that is absent always holds, and
an operand nobody supplied is *absent*, which never holds.

**When to decide.** A node `when` that reads only inputs is decided at **start**,
like a deliverable's. A node `when` that reads a classifier is decided at the
**boundary**, after the classifier answers — automatically, because referencing
`node:<id>` requires that classifier node to exist, and any classifier present
already moves the fire-set decision to the boundary.

### Cascade

A node whose `when` does not hold is **dropped**, and the drop **cascades**:

- A **content** node (a node another node consumes through a `node:<id>` binding
  or an `aggregate` list) that is dropped removes every deliverable whose
  aggregator transitively reaches it — the deliverable's content would otherwise
  have a hole. That deliverable is **skipped** (it does not fire), and any node
  that fed only it is pruned with it.
- A dropped **check** node simply **does not run**; the deliverable it gated
  **still fires**. A check is an assertion hung off a deliverable, not content the
  deliverable consumes, so gating it out cannot hole anything — it only removes the
  check (and any node that fed only that check).

This is why cascade is the whole of the semantics: it preserves the invariant that
a surviving node never has a missing `node:<id>` input. There is **no `else`, no
default, and no branch routing** — a node `when` gates inclusion, exactly as a
deliverable `when` does; it is not control flow. (The engine's `dag-improvements`
§3 doctrine: a decision that must *route* is a classifier's output read as data,
never format control flow. A node `when` adds no routing and no dangling-consumer
hole, so it stays within that doctrine.)

## Allowed node kinds

`when` may be declared on a **prompt**, **template**, **aggregate**, or **check**
node. It is **refused on a `classifier`**: a classifier always runs to make its
decision (the fire-set closure keeps a classifier even when it reaches no
deliverable), so gating one is meaningless.

**Refused by name:** `when` on a node in a manifest below 18; `when` on a
`classifier` node; a `when` whose condition is malformed or whose operand is an
undeclared input or a `node:<id>` that is not a classifier (the deliverable-`when`
rules, verbatim).

## No hash definition moves

A v18 package using nothing v18 opens validates, renders, and hashes
**byte-identically** to its v17 self — no node declares `when`. When a node `when`
does gate a node out, the run is the same as an equivalent package that had
replicated the condition on the affected deliverables: the fire set and the pruned
node set are what already governed which blocks are produced (v8 §5, #355). The
conformance case `v18-minimal-is-v17-plus-a-line` is the no-op statement as a
fixture.

## Migration

A v17 package becomes a v18 package with one edit: `specVersion: 18`. Nothing v18
opens is required. A node adopts a gate by adding `when: <condition>` (on any node
but a classifier); every other node is unchanged.
