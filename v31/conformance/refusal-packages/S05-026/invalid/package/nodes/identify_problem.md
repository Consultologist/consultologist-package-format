---
{ "kind": "agent", "producer": "generated", "label": "Identifying the problem", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Name the main problem for Dr A. Sample from these concepts:
{{ node.plan.value | renderer.concept_bullets }}
