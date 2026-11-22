---
{ "kind": "agent", "producer": "generated", "label": "Drafting from the standard", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "param.standard.value.title" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Draft the section '{{ param.standard.value.title }}' following these instructions.

{{ param.standard.content }}
