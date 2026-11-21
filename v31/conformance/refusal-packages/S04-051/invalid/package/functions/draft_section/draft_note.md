---
{ "kind": "agent", "producer": "generated", "label": "Noting the draft", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "node.plan.content" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Note in one line what the consult draft says about Margaret Okafor.

{{ param.draft.content }}
