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

## Reading it from the registry

Every version is published to the public registry and is fetchable with no
credential:

```
https://consultologistpublic.blob.core.windows.net/package-format/latest.json
https://consultologistpublic.blob.core.windows.net/package-format/v2026.08.1/spec-versions.json
https://consultologistpublic.blob.core.windows.net/package-format/v2026.08.1/package-format-v8.md
https://consultologistpublic.blob.core.windows.net/package-format/v2026.08.1/LICENSE
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
