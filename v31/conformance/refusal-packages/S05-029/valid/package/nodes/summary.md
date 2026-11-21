---
{ "kind": "agent", "producer": "generated", "label": "Summarising the concepts", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Summarise these concepts for Dr A. Sample:
{{ node.extract.value | renderer.concept_bullets }}
