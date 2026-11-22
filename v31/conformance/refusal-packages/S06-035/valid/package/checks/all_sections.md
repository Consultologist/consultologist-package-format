---
{ "kind": "computed", "producer": "computed", "label": "All sections covered", "description": null, "format": "check_result", "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "===": [{ "var": "input.final_copy.value" }, true] }, "expression": { "all_pass": [{ "var": "check.section_coverage.items" }, "Not every section covers its planned terms."] } }
---
