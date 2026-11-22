---
{ "kind": "computed", "producer": "computed", "label": "Proofreading the note", "description": null, "format": "check_result", "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "expression": { "object": { "pass": { "and": [{ "!": [{ "blank": [{ "var": "deliverable.note.content" }] }] }, { "var": "check.all_sections_covered.value.pass" }] }, "message": null, "uncovered": null, "untested": null, "passed": null, "total": null } } }
---
