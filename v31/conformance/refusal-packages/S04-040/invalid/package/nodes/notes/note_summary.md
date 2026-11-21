---
{ "kind": "agent", "producer": "generated", "label": "Summarising a prior note", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "item.parent.value" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Summarise the prior note below in one sentence for Dr A. Sample.
