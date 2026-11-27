---
{"label":"Clinic letter","kind":"rendered","description":null,"format":"markdown_block","if":null,"check":null,"whenEmpty":"release"}
---
{{ node.problem_loop.content | string.strip }}

{{ node.letter.content | string.strip }}