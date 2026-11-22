---
{ "kind": "agent", "producer": "generated", "label": "Applying the instructions", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Combine the two drafts into one section.

{{ node.standard_draft.content }}

{{ node.patient_draft.content }}
