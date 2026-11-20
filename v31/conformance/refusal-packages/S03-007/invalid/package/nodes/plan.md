---
{ "kind": "agent", "producer": "generated", "label": "Planning the sections", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "in": ["letrozole", { "substr": [{ "var": "input.consult_draft.content" }, 0, 500] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Plan the sections of a consultation note for the draft below.

{{ input.consult_draft.content }}
