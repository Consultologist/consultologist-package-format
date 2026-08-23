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
under `v5`–`v9`; a case about the accepted set itself sits under `any`.

**The expectations are not written by hand.** Every case is produced by running
the engine's own validator and recording what it said, so a fixture can never
claim an error the engine does not actually produce. The engine replays the
published suite in its own tests, which is what keeps these documents and the
code that enforces them from drifting apart.

Of the 92 cases, 80 are invalid ones. That ratio is deliberate: a rejected
package that names its reason proves more than an accepted one — and the v9
release added a rejection case for every publish-time refusal its design
record names, refusal by refusal.

**Where the schemas stop.** `schemas/package-format-v{N}.schema.json` is the
machine-readable half — what an editor or a linter reads. Run the conformance
suite against them and the boundary is exact: every valid case passes, and the
invalid cases split three ways. Thirty-seven are rejected by their version's
schema. Forty-two fail for reasons no schema can see — the condition grammar
lives inside one string, a fan's target is a cross-reference, trim and
case-insensitive-distinctness rules are semantic — and the validation
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
https://consultologistpublic.blob.core.windows.net/package-format/latest.json
https://consultologistpublic.blob.core.windows.net/package-format/v2026.08.5/spec-versions.json
https://consultologistpublic.blob.core.windows.net/package-format/v2026.08.5/package-format-v9.md
https://consultologistpublic.blob.core.windows.net/package-format/v2026.08.5/LICENSE
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
- **NoDerivatives** covers this text: no translations, no modified or excerpted
  redistributions of the documents themselves.
- **NonCommercial** covers redistribution of the documents, not use of the
  format. Reproducing them inside commercial documentation needs permission.

The licence covers the documents and `spec-versions.json` only. It grants no
rights to the Consultologist engine, which is separately licensed, and no
patent or trademark rights. Ask if you need something it does not cover.

## Related registries

- [consultologist-workflows](https://github.com/Consultologist/consultologist-workflows) — the packages themselves
- [consultologist-agents](https://github.com/Consultologist/consultologist-agents) — agent definitions and the output-contract catalog
- [Consultologist-Blazor](https://github.com/Consultologist/Consultologist-Blazor) — the engine, and the design records these specs cite
