---
{ "label": "Terms as a list", "kind": "rendered", "description": null, "input": "concept_list", "format": "markdown_block" }
---
{{~ for c in value.concepts ~}}
- {{ c.term }}
{{~ end ~}}
