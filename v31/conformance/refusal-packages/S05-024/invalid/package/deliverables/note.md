---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}

Run {{ input.consult_draft.content | string.upcase run.id }}
