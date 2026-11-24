---
{ "label": "Letter to the patient", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": null, "whenEmpty": "hold" }
---
Dear Margaret Okafor,

This is what we talked about at your visit.

{{ for s in node.sections.value }}{{ s }}

{{ end }}Dr A. Sample
