---
{ "label": "Terms as bullets", "kind": "rendered", "description": ["One bullet for each term."], "input": "concept_list", "format": "markdown_block" }
---
{{~ for c in value.concepts ~}}
- {{ c.term }}
{{~ end ~}}
