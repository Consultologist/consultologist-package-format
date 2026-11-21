---
{ "kind": "agent", "producer": "generated", "label": "Judging the summary", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { ">": [{ "var": "pass.number" }, 1] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Say what the summary below still needs; write nothing when it is good.

{{ node.draft_summary.content }}
