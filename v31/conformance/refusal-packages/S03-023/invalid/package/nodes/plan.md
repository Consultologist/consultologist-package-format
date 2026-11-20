---
{ "kind": "agent", "producer": "generated", "label": "Planning the sections", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "===": [{ "var": "input.note_kind.value" }, "letter"] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Plan the sections of a consultation note for the draft below.

{{ input.consult_draft.content }}
