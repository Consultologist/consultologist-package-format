---
{ "label": "Consult note", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": "check.all_sections", "whenEmpty": "hold" }
---
Sections

{{ for s in node.standards.value }}{{ s }}

{{ end }}
