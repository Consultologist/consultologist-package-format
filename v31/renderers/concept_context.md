---
{ "label": "Concepts with their state", "kind": "rendered", "description": null,
  "input": "concept_list", "format": "markdown_block" }
---
{{~ if value.concepts.size == 0 ~}}
(none){{~ else ~}}
{{~ for c in value.concepts ~}}
- {{ c.term }} ({{ c.type }}) - {{ c.id }}; active: {{ if c.isActive }}True{{ else }}False{{ end }}; source: {{ if c.support != null && (c.support | string.strip) != "" }} support: {{ c.support }}{{ end }}{{ if !for.last }}
{{ end ~}}
{{~ end ~}}
{{~ end ~}}
