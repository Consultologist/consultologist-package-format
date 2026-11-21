---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": null, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}

Dated {{ input.consult_draft.content | string.upcase node.today.value }}
