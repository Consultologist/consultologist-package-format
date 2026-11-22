---
{ "kind": "computed", "producer": "computed", "label": "Proofreading the note", "description": null, "format": "check_result", "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": null, "expression": { "object": { "pass": { "and": [{ "!": [{ "blank": [{ "var": "deliverable.emr.consult.content" }] }] }, { "var": "check.consult_words.value.pass" }, { "var": "check.all_sections.value.pass" }] }, "message": null, "uncovered": null, "untested": null, "passed": null, "total": null } } }
---
