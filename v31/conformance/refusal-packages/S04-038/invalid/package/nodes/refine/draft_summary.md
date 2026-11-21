---
{ "kind": "agent", "producer": "generated", "label": "Drafting the summary", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "pass.previous.node.plan.content" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Summarise the note in two sentences for Dr A. Sample.
