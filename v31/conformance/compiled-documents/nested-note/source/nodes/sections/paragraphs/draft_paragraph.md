---
{ "kind": "agent", "producer": "generated", "label": "Drafting a paragraph", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "item.parent.value.title" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Write one paragraph of the section '{{ item.parent.value.title }}' about this point: {{ item.value }}
