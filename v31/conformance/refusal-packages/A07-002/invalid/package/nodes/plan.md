---
{ "kind": "agent", "producer": "generated", "label": "Planning the sections", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": { "closing": { "if": null, "text": ["{{ if for.first }}Close the plan with a line for Dr A. Sample.{{ end }}"] } }, "ordered": false }
---
Plan the sections of a consultation note for the draft below.

{{ input.consult_draft.content }}
{{~ part.closing }}
