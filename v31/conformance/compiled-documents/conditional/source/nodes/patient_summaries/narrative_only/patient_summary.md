---
{ "kind": "agent", "producer": "generated", "label": "Summarising for the patient", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Summarise the section '{{ item.value.title }}' for Margaret Okafor in plain words.
