---
{"label":"Urgent copy","kind":"rendered","description":null,"format":"markdown_block","if":"(input.consult_draft | string.upcase) == \"URGENT\"","check":null,"whenEmpty":"release"}
---
{{ node.problem_loop.content }}