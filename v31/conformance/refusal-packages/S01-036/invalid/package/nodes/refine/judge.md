---
{ "kind": "agent", "producer": "generated", "label": "Judging the summary", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Say what the summary below still needs; write nothing when it is good.

{{ node.draft_summary.content }}

{{ node.brief.content }}
{{ node.detailed.content }}
