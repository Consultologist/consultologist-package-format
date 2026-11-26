---
{ "kind": "agent", "producer": "generated", "label": "Planning the sections", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "and": [{ ">": [{ "*": [{ "words": [{ "var": "input.consult_draft.content" }] }, 2] }, 5000] }, { "in": [{ "var": "input.consult_draft.content" }, { "var": "input.prior_notes.value" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Plan the sections of a consultation note for the draft below.

{{ input.consult_draft.content }}
