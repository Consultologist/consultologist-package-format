---
{ "label": "Terms as a list", "kind": "rendered", "description": null, "input": "concept_list", "format": "concept_list" }
---
{{~ for c in value.concepts ~}}
- {{ c.term }}
{{~ end ~}}
