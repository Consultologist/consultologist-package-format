---
{ "label": "Consult", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": null, "whenEmpty": "hold" }
---
{{ for part in node.sections.items }}{{ if part.state == "completed" }}{{ part.value }}
{{ else if part.state == "skipped" }}(skipped)
{{ else }}(not run)
{{ end }}{{ end }}