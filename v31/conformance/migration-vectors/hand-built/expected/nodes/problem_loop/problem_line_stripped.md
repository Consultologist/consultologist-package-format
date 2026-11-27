---
{"kind":"rendered","producer":"computed","label":"Writing a problem's line","description":null,"format":"markdown_block","reproducible":true,"modelDerived":false,"runDependent":false,"profileCarrying":false,"if":{"===":[{"var":"node.problem_line.state"},"completed"]}}
---
{{ node.problem_line.content | string.strip }}