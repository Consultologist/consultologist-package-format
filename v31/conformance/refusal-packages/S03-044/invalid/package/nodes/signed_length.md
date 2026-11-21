---
{ "kind": "computed", "producer": "computed", "label": "Measuring the draft", "description": null, "format": "number", "reproducible": true, "modelDerived": false, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "node.signed.content" }] }] }, "expression": { "size": [{ "var": "input.consult_draft.content" }] } }
---
