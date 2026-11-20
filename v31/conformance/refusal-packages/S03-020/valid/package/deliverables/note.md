---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": { "!": [{ "blank": [{ "var": "node.plan.value" }] }] }, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}
