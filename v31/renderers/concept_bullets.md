---
{ "label": "Concepts as bullets", "kind": "rendered", "description": null,
  "input": "concept_list", "format": "markdown_block" }
---
{{~ if value.concepts.size == 0 ~}}
(none){{~ else ~}}
{{~ for c in value.concepts ~}}
{{~ if c.isSnomedConcept ~}}
- {{ c.term }} ({{ c.type }}) - {{ c.id }}{{ if !c.isActive }} [not active SNOMED concept]{{ end }}{{ if !for.last }}
{{ end ~}}
{{~ else ~}}
- {{ c.term }} [not SNOMED concept]{{ if !for.last }}
{{ end ~}}
{{~ end ~}}
{{~ end ~}}
{{~ end ~}}
