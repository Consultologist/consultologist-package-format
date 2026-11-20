---
{ "kind": "agent", "producer": "generated", "label": "Planning the sections", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "===": [{ "size": [{ "var": "input.prior_notes.value" }] }, 0] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Plan the sections of a consultation note for the draft below.

{{ input.consult_draft.content }}
