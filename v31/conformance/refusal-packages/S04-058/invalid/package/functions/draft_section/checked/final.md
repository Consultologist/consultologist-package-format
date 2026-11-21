---
{ "kind": "agent", "producer": "generated", "label": "Writing the section", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "!": [{ "blank": [{ "var": "param.draft.content" }] }] }, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Write the section for Margaret Okafor.

{{ param.draft.content }}
