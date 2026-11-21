---
{ "kind": "agent", "producer": "generated", "label": "Drafting from the patient's facts", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Using the consult draft below, write what it says about Margaret Okafor.

{{ param.draft.content }}
