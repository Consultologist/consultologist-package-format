---
{ "kind": "agent", "producer": "generated", "label": "Whether a follow-up applies", "description": null, "format": "judgement", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
{{ input.consult_draft.content }}

Does the draft plan a follow-up visit?
