---
{ "label": "Consultation note", "kind": "rendered", "description": null, "format": "plaintext", "if": { "===": [{ "var": "check.draft_written.value.pass" }, true] }, "check": null, "whenEmpty": "hold" }
---
{{ node.plan.content }}
