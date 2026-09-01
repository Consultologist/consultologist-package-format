# consultologist-package-format

The normative specifications for the Consultologist workflow **package format**,
published as a versioned registry.

A package declares `"specVersion": N`. The engine accepts a fixed set of those
numbers and refuses the rest. This repo is where both facts live: the documents
that define each format, and `spec-versions.json`, the machine-readable set the
engine accepts.

| File | Defines |
| --- | --- |
| `spec-versions.json` | which `specVersion` values the engine accepts, and the document defining each |
| `package-format-v5.md` | derivedFrom fork lineage, data collections, one node kind with forEach, the result contract, per-item provenance |
| `package-format-v6.md` | multiple collections, aggregator nodes, one assembled document |
| `package-format-v7.md` | declared inputs and the result set — multiple deliverables |
| `package-format-v8.md` | typed inputs with values, and deliverables conditional on them |
| `package-format-v9.md` | structured inputs (number, object, array), fans over caller data, the widened condition grammar, several documents per slot, and package metadata — title, description, required tags |
| `package-format-v10.md` | the classifying node and the boundary it decides at, expression conditions (and/or/not, grouping, arithmetic, `node:`), and structure nested to any depth |
| `package-format-v11.md` | package-owned macros with their closed placeholder grammar, the signed deliverable (the block is the profile’s), and the reproducible claim |

## Checking a package against it

Prose says what a package must be; `conformance/` lets you find out whether
yours is one.

Each case is self-contained — the manifest, every file the bundle would carry,
and the outcome the engine produces:

```json
{
  "id": "invalid-values-without-enum",
  "specVersion": 8,
  "description": "values declared on an input that is not an enum…",
  "expect": {
    "valid": false,
    "errors": ["Input 'seen_on' is type 'date' and may not declare values."]
  },
  "manifest": { … },
  "files": { "prompts/…": "…" }
}
```

`conformance/index.json` lists them; `conformance/catalog-schemas.json` carries
the output-contract schemas a case may reference. Cases about one format sit
under `v5`–`v11`; a case about the accepted set itself sits under `any`.

**The expectations are not written by hand.** Every case is produced by running
the engine's own validator and recording what it said, so a fixture can never
claim an error the engine does not actually produce. The engine replays the
published suite in its own tests, which is what keeps these documents and the
code that enforces them from drifting apart.

Of the 167 cases, 140 are invalid ones. That ratio is deliberate: a rejected
package that names its reason proves more than an accepted one — and the v9,
v10 and v11 releases each added a rejection case for every publish-time
refusal their design records name, refusal by refusal. Five v10 cases carry a second
error that follows from the first (a node of no known kind references no
prompt) and say so in their description; every other invalid case carries
exactly one.

**Where the schemas stop.** `schemas/package-format-v{N}.schema.json` is the
machine-readable half — what an editor or a linter reads. Run the conformance
suite against them and the boundary is exact: every valid case passes, and the
invalid cases split three ways. Fifty-five are rejected by their version's
schema. Eighty-four fail for reasons no schema can see — the condition grammar
lives inside one string, a macro's placeholder grammar lives inside its file,
a fan's target is a cross-reference, a classifier's
rules are relations between nodes, trim and case-insensitive-distinctness
rules are semantic — and the validation
workflow's `SHAPE_BLIND` list names each one with its reason, so the boundary
is a list somebody chose (`invalid-missing-prompt-file` is the oldest member:
its manifest is byte-identical to a valid one and only its bundle differs).
`invalid-spec-version-unsupported` is about the accepted set, which
`spec-versions.json` owns and no per-version schema covers.

So the schema catches shape. Whether every referenced file exists, whether the
node graph is acyclic and each deliverable reachable, whether a declared schema
welds to a catalog contract, whether the template compiles — none of those are
shape, and the suite is what covers them.

The schemas are generated from the engine's own manifest type and asserted
byte-for-byte there, so the published shape cannot drift from the one the engine
reads. They set `additionalProperties: false`, which is what these documents say
— *"a section the version does not have is never a silently ignored field"* —
and, since the engine was brought into line, what it enforces too: a manifest
carrying a property the format does not have is refused at load, at publish, and
by the offline validator, naming the property.

## Reading it from the registry

Every version is published to the public registry and is fetchable with no
credential:

```
https://consultpubcaeast.blob.core.windows.net/package-format/latest.json
https://consultpubcaeast.blob.core.windows.net/package-format/v2026.08.10/spec-versions.json
https://consultpubcaeast.blob.core.windows.net/package-format/v2026.08.10/package-format-v11.md
https://consultpubcaeast.blob.core.windows.net/package-format/v2026.08.10/LICENSE
```

`latest.json` is the only mutable blob — `{"version": "vYYYY.MM.N"}`. Published
versions are **immutable**: the publish script refuses to overwrite one.

## Publishing a change

`spec-versions.json` carries its own CalVer version (`vYYYY.MM.N`, zero-padded
month, counter ≥ 1). Bump it in the same commit as whatever you changed, and
merging to `main` publishes — there is no tag. Forgetting the bump fails the
publish rather than overwriting a published version.

Documents upload before `spec-versions.json`, so a partial upload is never
visible as a complete version.

## Two conventions worth knowing

**Outbound links are commit-pinned.** These documents cite design records that
live in the engine repo. Those links point at a specific commit rather than at
`main`, so a published spec version resolves to the same words forever. A
rationale link going stale is the price of a specification that does not move
under a package published against it.

**A package name is a path.** Since `v2026.08.6` a name may nest —
`oncology/breast` — up to four segments, each the flat grammar
(`[a-z0-9][a-z0-9-]*`); a flat name is a one-segment path, so nothing already
published changes. The path is the identity: the registry address is
`{name}/{version}/…`, and `derivedFrom` may name a nested parent on every
format version (the schemas say so). The engine's account packages nest
under their `acct-<12 hex>` root.

**The accepted set is a published fact, not a code constant.** The engine's own
list and this document are checked against each other by a test in the engine
repo, which vendors this repo as a submodule. They cannot silently disagree.

## Licence

These documents are licensed **[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/)**
— © 2026 Tauheed Elahee. Read them, cite them, and share them unchanged with
attribution.

What that does and does not reach:

- **Implementing the format is unaffected.** An implementation is not a
  derivative work of this prose, so conformance needs no permission — which is
  the point of publishing a specification at all.
- **NoDerivatives** covers this text: no translations, and no redistribution of
  the documents in modified form. Quoting them — a sentence, a rule, a worked
  example — within fair dealing is fine and is what "cite them" means.
- **NonCommercial** covers redistribution of the documents, not use of the
  format. Reproducing them inside commercial documentation needs permission.

The licence covers the documents and `spec-versions.json` only. It grants no
rights to the Consultologist engine, which is separately licensed, and no
patent or trademark rights.

**Consultologist clients hold a licence that goes beyond this one.** Every
client may use these documents, the schemas and the conformance suite commercially — inside the app, and in their own
environment outside it — and holds the copyright in what they author. That
permission is part of the client agreement, not this file; this licence is
the public default for everyone else. Anyone who needs more than it grants
can ask.
The permission that matters most is one nobody needs to ask for: implementing
the format, and running packages that conform to it in your own harness, is
not a derivative work of this prose.

## Related registries

- [consultologist-workflows](https://github.com/Consultologist/consultologist-workflows) — the packages themselves
- [consultologist-agents](https://github.com/Consultologist/consultologist-agents) — agent definitions and the output-contract catalog
- [Consultologist-Blazor](https://github.com/Consultologist/Consultologist-Blazor) — the engine, and the design records these specs cite
