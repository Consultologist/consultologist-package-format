---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": { "!": [{ "blank": [{ "var": "node.plan.content" }] }] }, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}
