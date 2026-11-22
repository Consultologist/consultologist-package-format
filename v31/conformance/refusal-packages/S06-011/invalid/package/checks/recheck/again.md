---
{ "kind": "computed", "producer": "computed", "label": "Terms covered again", "description": null, "format": "check_result", "reproducible": true, "modelDerived": true, "runDependent": false, "profileCarrying": false, "if": { "===": [{ "var": "item.state" }, "completed"] }, "expression": { "terms_subset": [{ "var": "node.extract_input_terms.value" }, { "var": "node.extract_note_terms.value" }, "The note does not cover every clinical term found in the draft."] } }
---
