---
{ "kind": "agent", "producer": "generated", "label": "Judging the summary", "description": null, "format": "verdict", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Say whether the summary is good or needs another pass.

{{ node.draft_summary.content }}
