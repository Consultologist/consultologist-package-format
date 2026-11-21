---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}

Dated {{ run.date | date.to_string }}
