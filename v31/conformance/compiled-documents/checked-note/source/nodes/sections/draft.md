---
{ "kind": "agent", "producer": "generated", "label": "Drafting the section", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Write the section '{{ item.value.title }}' of the note for Dr A. Sample.

{{ input.consult_draft.content }}
