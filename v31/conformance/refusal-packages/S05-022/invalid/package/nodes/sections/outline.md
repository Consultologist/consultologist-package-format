---
{ "kind": "agent", "producer": "generated", "label": "Outlining the section", "description": null, "format": "plaintext", "reproducible": false, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "onInvalid": "retry", "failIfEmpty": null, "parts": null, "ordered": false }
---
Outline the section '{{ item.value.title }}' of the note as a short list of points.
{{~ snippet.title_line.content }}
