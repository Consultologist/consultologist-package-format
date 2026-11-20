---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": { "!": [{ "blank": [{ "var": "input.consult_draft.content" }] }] }, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}
