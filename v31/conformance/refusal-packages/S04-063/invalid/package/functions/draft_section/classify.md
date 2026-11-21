---
{ "kind": "agent", "producer": "generated", "label": "Classifying the draft", "description": null, "format": "judgement", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Does the consult draft below call for a follow-up?

{{ param.draft.content }}
