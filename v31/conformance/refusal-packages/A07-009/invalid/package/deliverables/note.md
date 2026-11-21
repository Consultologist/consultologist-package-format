---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}
{{ if node.plan.state == "completed" }}
{{~ snippet.tone.content }}
{{ else }}
{{ end }}
