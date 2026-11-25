---
{"kind":"agent","producer":"generated","label":"Agent draft","description":null,"format":"plaintext","reproducible":false,"modelDerived":true,"runDependent":true,"profileCarrying":false,"if":null,"onInvalid":"retry","failIfEmpty":null,"parts":{"close":{"if":{"!":[{"blank":[{"var":"node.classify.value.reason"}]}]},"text":["Close the history.","{{~ macro.section_notes.hpi }}"]}},"ordered":false}
---
Draft the history for Margaret Okafor.
{{ node.stamp.content }}
{{~ part.close }}
