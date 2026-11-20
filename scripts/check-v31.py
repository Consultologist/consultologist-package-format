#!/usr/bin/env python3
"""Checks the specVersion 31 preview files. Exits 0 when every group passes, 1 otherwise.

Each group is a function check_<group>() -> list[str] of failures, registered in CHECKS.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
V31 = ROOT / "v31"

# Part 01 section 7, "bounds.json's shape", exactly.
BOUNDS = {
    "specVersion": 31,
    "sourceBounds": {"files": 512, "fileBytes": 262144, "totalBytes": 2097152,
                     "pathLength": 200, "idLength": 64, "jsonDepth": 32,
                     "expressionNodes": 1000},
    "formatBounds": {"passes": 15, "depth": 15, "parallel": 15},
    "windowsReservedIds": ["con", "prn", "aux", "nul",
                           "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
                           "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"],
    "reservedIds": ["input", "inputs", "node", "nodes", "check", "checks", "function", "functions",
                    "test", "tests", "snippet", "snippets", "macro", "macros", "part", "parts",
                    "renderer", "renderers", "format", "formats", "deliverable", "deliverables",
                    "param", "params", "item", "items", "pass", "passes", "run", "runs",
                    "profile", "profiles", "value", "values", "content", "contents"],
}

# Part 07 section 3.1: the built-in custom operations.
OPERATIONS = ["size", "blank", "words", "lines", "lower", "trim", "starts_with", "ends_with",
              "plain", "object", "matches", "has_word", "terms_subset", "all_pass", "count_pass",
              "days_between", "years_between", "add_days"]

# Part 05 section 2.2: the template built-ins.
TEMPLATE_BUILTINS = ["string.upcase", "string.downcase", "string.capitalize", "string.strip",
                     "array.join", "array.size", "date.to_string"]

CONSTANTS_KEYS = ["specVersion", "dialects", "evaluator", "operations", "builtins",
                  "templateBuiltins", "standardOperations", "kinds", "features", "producers",
                  "runFacts", "channels", "deliveryKinds", "whenEmpty", "states",
                  "deliverableStates", "edgeKinds", "limits", "mediaTypes", "markdig"]
LIMITS_KEYS = ["descriptionCodePoints", "matchesPatternCodePoints", "matchesRepetition",
               "matchesTextBytes", "templateForIterations", "templateNesting",
               "templateOutputBytes", "testsSeconds", "itemNameCharacters"]
BUILTINS_KEYS = ["concept_bullets", "concept_context", "formats", "markdown_escape",
                 "plain_conversion", "printer"]

# Constants' list and object members, value for value (parts 01 to 09).
CONSTANT_MEMBERS = {
    "standardOperations": ["var", "missing", "if", "===", "!==", "<", "<=", ">", ">=", "and", "or",
                           "!", "in", "cat", "+", "-", "*", "/", "%", "min", "max"],
    "kinds": ["agent", "rendered", "computed", "for", "while", "if", "case", "call"],
    "features": ["parallel", "macro-markers", "parts", "run-spots", "check-loops"],
    "producers": {"accepted": ["generated", "computed"],
                  "reserved": ["grounded", "extracted", "attention"]},
    "runFacts": ["date", "id", "package", "engine"],
    "channels": ["transcript", "image", "ambient-note", "form"],
    "deliveryKinds": ["email", "pdf", "emr", "zip"],
    "whenEmpty": ["release", "hold", "fail"],
    "states": ["completed", "skipped", "not_run"],
    "deliverableStates": ["released", "held", "failed", "skipped", "blocked"],
    "edgeKinds": ["reads", "if", "for", "ret", "placed", "calls", "aligned", "gates"],
    "mediaTypes": {"resolve": "application/vnd.consultologist.resolve+json",
                   "lock": "application/vnd.consultologist.lock+json",
                   "publishReport": "application/vnd.consultologist.publish-report+json"},
    "limits": {"descriptionCodePoints": 500, "matchesPatternCodePoints": 200,
               "matchesRepetition": 100, "matchesTextBytes": 1048576,
               "templateForIterations": 1000, "templateNesting": 15,
               "templateOutputBytes": 1048576, "testsSeconds": 60, "itemNameCharacters": 120},
}

PROFILE_FIELDS = {  # field -> (format, label), part 06 section 10.1 and part 09 section 9
    "name": ("string", "name"),
    "credentials": ("string", "credentials"),
    "organisation": ("string", "organisation"),
    "signature": ("plaintext", "signature"),
    "closing": ("plaintext", "closing line"),
}


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except FileNotFoundError:
        return None, [f"{path.relative_to(ROOT)}: missing"]
    except json.JSONDecodeError as error:
        return None, [f"{path.relative_to(ROOT)}: not JSON ({error})"]


def expect(failures, what, actual, expected):
    if actual != expected:
        failures.append(f"{what}: expected {expected!r}, found {actual!r}")


def check_constants():
    failures = []

    bounds, errors = load(V31 / "bounds.json")
    failures += errors
    if bounds is not None:
        expect(failures, "v31/bounds.json", bounds, BOUNDS)

    constants, errors = load(V31 / "constants.json")
    failures += errors
    if constants is not None:
        expect(failures, "v31/constants.json keys", list(constants), CONSTANTS_KEYS)
        expect(failures, "constants.specVersion", constants.get("specVersion"), 31)
        expect(failures, "constants.operations", constants.get("operations"),
               {name: "1.0.0" for name in OPERATIONS})
        expect(failures, "constants.templateBuiltins", constants.get("templateBuiltins"),
               {name: "1.0.0" for name in TEMPLATE_BUILTINS})
        expect(failures, "constants.builtins", constants.get("builtins"),
               {name: "1.0.0" for name in BUILTINS_KEYS})
        expect(failures, "constants.evaluator", constants.get("evaluator"), "1.0.0")
        expect(failures, "constants.limits keys", list(constants.get("limits", {})), LIMITS_KEYS)
        for name, expected in CONSTANT_MEMBERS.items():
            expect(failures, f"constants.{name}", constants.get(name), expected)
        markdig = constants.get("markdig", {})
        expect(failures, "constants.markdig keys", list(markdig), ["version", "extensions"])
        if not re.fullmatch(r"0\.41\.\d+", str(markdig.get("version"))):
            failures.append(f"constants.markdig.version: expected 0.41.x, found {markdig.get('version')!r}")
        if not markdig.get("extensions"):
            failures.append("constants.markdig.extensions: empty")

    profile, errors = load(V31 / "profile.json")
    failures += errors
    if profile is not None:
        expect(failures, "v31/profile.json keys", list(profile),
               ["specVersion", "fields", "previewTimeZone"])
        expect(failures, "profile.previewTimeZone", profile.get("previewTimeZone"),
               "America/Toronto")
        fields = profile.get("fields", {})
        expect(failures, "profile.fields", list(fields), list(PROFILE_FIELDS))
        for name, (fmt, label) in PROFILE_FIELDS.items():
            field = fields.get(name, {})
            expect(failures, f"profile.fields.{name} keys", list(field),
                   ["format", "label", "preview"])
            expect(failures, f"profile.fields.{name}.format", field.get("format"), fmt)
            expect(failures, f"profile.fields.{name}.label", field.get("label"), label)
            preview = field.get("preview")
            if not isinstance(preview, str) or not preview:
                failures.append(f"profile.fields.{name}.preview: expected a non-empty string, found {preview!r}")

    versions, errors = load(ROOT / "spec-versions.json")
    failures += errors
    if versions is not None:
        expect(failures, "spec-versions.json preview", versions.get("preview", {}).get("31"),
               {"document": "package-format-v31.md", "directory": "v31"})
        if 31 in versions.get("supported", []):
            failures.append("spec-versions.json: 31 is in supported")
        if "31" in versions.get("documents", {}):
            failures.append("spec-versions.json: 31 is in documents")
    return failures


# Rows of each part of the design's refusal-sentences.md (the table, not its totals).
SENTENCE_COUNTS = {"01": 42, "02": 56, "03": 44, "04": 80, "05": 64,
                   "06": 38, "07": 17, "08": 9, "09": 19, "10": 6}
SENTENCE_ID = re.compile(r"^S(0[1-9]|10)-\d{3}$")


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_sentences",
                                                  ROOT / "scripts" / "render-sentences.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sentences():
    document, failures = load(V31 / "sentences.json")
    if document is None:
        return failures
    expect(failures, "sentences.json keys", list(document), ["specVersion", "sentences"])
    expect(failures, "sentences.specVersion", document.get("specVersion"), 31)
    sentences = document.get("sentences", [])
    seen = set()
    last_in_part = {}
    counts = {}
    for entry in sentences:
        id_ = entry.get("id", "")
        expect(failures, f"{id_} keys", list(entry),
               ["id", "part", "section", "sentence", "audience"])
        if not SENTENCE_ID.match(id_):
            failures.append(f"{id_!r}: not an id of the form S<part>-<number>")
            continue
        if id_ in seen:
            failures.append(f"{id_}: duplicate id")
        seen.add(id_)
        part = id_[1:3]
        expect(failures, f"{id_}.part", entry.get("part"), part)
        if id_ <= last_in_part.get(part, ""):
            failures.append(f"{id_}: not ascending within part {part}")
        last_in_part[part] = id_
        counts[part] = counts.get(part, 0) + 1
        if entry.get("audience") not in ("author", "clinician"):
            failures.append(f"{id_}.audience: {entry.get('audience')!r}")
        text = entry.get("sentence")
        if not isinstance(text, str) or not text:
            failures.append(f"{id_}.sentence: expected a non-empty string")
            continue
        if re.search(r"\\[<>|]", text):
            failures.append(f"{id_}.sentence: a backslash before <, > or |")
        if not entry.get("section"):
            failures.append(f"{id_}.section: empty")
    expect(failures, "sentences per part", dict(sorted(counts.items())), SENTENCE_COUNTS)

    renderer = load_renderer()
    parsed = renderer.parse(renderer.render(sentences))
    expect(failures, "sentences rendered and parsed back",
           parsed, [(e["id"], e["sentence"], e["audience"]) for e in sentences])
    return failures

DIALECT_ID = "urn:consultologist:spec:31:dialect"
BUILT_IN_FORMATS = ["string", "number", "boolean", "date", "plaintext", "markdown_block",
                    "markdown_inline", "check_result", "judgement"]
# Part 02 section 5: the annotations each built-in carries at its root.
ANNOTATIONS = {"plaintext": ("text/plain", None),
               "markdown_block": ("text/markdown", "block"),
               "markdown_inline": ("text/markdown", "inline")}
SCHEMAS = V31 / "schemas"
CONFORMANCE = V31 / "conformance" / "schemas"


def schema_files():
    """The dialect and every file-kind schema. Built-in formats are data, never loaded here."""
    return [V31 / "dialect.schema.json"] + sorted(SCHEMAS.glob("*.schema.json"))


def build_registry():
    registry, failures = Registry(), []
    for path in schema_files():
        document, errors = load(path)
        failures += errors
        if document is not None:
            registry = registry.with_resource(document.get("$id", path.name),
                                              Resource.from_contents(document))
    return registry, failures


def schema_for(name):
    return V31 / "dialect.schema.json" if name == "dialect" else SCHEMAS / f"{name}.schema.json"


def validator_for(path, registry, failures):
    schema, errors = load(path)
    failures += errors
    if schema is None:
        return None
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as error:
        failures.append(f"{path.relative_to(ROOT)}: not a 2020-12 schema ({error.message})")
        return None
    return Draft202012Validator(schema, registry=registry)


def check_examples():
    registry, failures = build_registry()
    folders = sorted(path for path in CONFORMANCE.glob("*") if path.is_dir())
    if not folders:
        failures.append("v31/conformance/schemas: no schema directories")
    for folder in folders:
        valid = sorted(folder.glob("valid-*.json"))
        invalid = sorted(folder.glob("invalid-*.json"))
        if not valid:
            failures.append(f"{folder.relative_to(ROOT)}: no valid example")
        if not invalid:
            failures.append(f"{folder.relative_to(ROOT)}: no invalid example")
        validator = validator_for(schema_for(folder.name), registry, failures)
        if validator is None:
            continue
        schema_id = validator.schema["$id"]
        for path, expected in [(p, True) for p in valid] + [(p, False) for p in invalid]:
            example, errors = load(path)
            failures += errors
            if example is None:
                continue
            name = path.relative_to(ROOT)
            if list(example) not in (["about", "instance"], ["about", "against", "instance"]) \
                    or not example["about"]:
                failures.append(f"{name}: expected {{ about, [against,] instance }} with a non-empty about")
                continue
            judge = validator
            if "against" in example:
                judge = Draft202012Validator({"$ref": schema_id + example["against"]}, registry=registry)
            accepted = judge.is_valid(example["instance"])
            if accepted != expected:
                failures.append(f"{name}: expected the schema to "
                                f"{'accept' if expected else 'refuse'} it")
    return failures


def declared_but_not_required(schema, where):
    """Part 02 section 3.3, which a meta-schema cannot state: required lists every property."""
    failures = []
    if isinstance(schema, dict):
        properties = schema.get("properties")
        if isinstance(properties, dict) and sorted(schema.get("required", [])) != sorted(properties):
            failures.append(f"{where}: required must list exactly the declared properties")
        for key, value in schema.items():
            if key in ("properties", "$defs") and isinstance(value, dict):
                for name, child in value.items():
                    failures += declared_but_not_required(child, f"{where}/{key}/{name}")
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    failures += declared_but_not_required(child, f"{where}/{key}/{index}")
            elif isinstance(value, dict):
                failures += declared_but_not_required(value, f"{where}/{key}")
    return failures


def check_common(registry, constants, bounds):
    failures = []
    common, errors = load(SCHEMAS / "common.schema.json")
    failures += errors
    if common is None:
        return failures
    definitions = common.get("$defs", {})
    expect(failures, "common.schema.json $id", common.get("$id"),
           "urn:consultologist:spec:31:schema:common")
    expect(failures, "common.schema.json $defs", list(definitions),
           ["id", "label", "description", "formatRef", "textFormat", "sha256", "rootedKey",
            "jsonLogic", "condition", "referenceString"])
    operation = definitions.get("jsonLogic", {}).get("$defs", {}).get("operationName", {})
    expect(failures, "common jsonLogic operation names", operation.get("enum"),
           constants["standardOperations"] + list(constants["operations"]))
    expect(failures, "common id not-enum", definitions.get("id", {}).get("not", {}).get("enum"),
           bounds["reservedIds"] + bounds["windowsReservedIds"])

    def accepts(name, value):
        schema = {"$ref": f"urn:consultologist:spec:31:schema:common#/$defs/{name}"}
        return Draft202012Validator(schema, registry=registry).is_valid(value)

    cases = [
        ("id", "hpi_section", True), ("id", "Hpi", False), ("id", "node", False),
        ("id", "con", False), ("id", "a" * 65, False), ("id", "a" * 64, True),
        ("label", "Planning", True), ("label", "  ", False),
        ("description", None, True), ("description", ["a"], True), ("description", [], False),
        ("description", "a", False),
        ("formatRef", "plaintext", True), ("formatRef", {"type": "string"}, True),
        ("formatRef", {"$schema": DIALECT_ID, "type": "string"}, False),
        ("textFormat", "markdown_inline", True), ("textFormat", "string", False),
        ("sha256", "sha256:" + "0" * 64, True), ("sha256", "sha256:" + "G" * 64, False),
        ("rootedKey", "node.draft", True), ("rootedKey", "check.a.b", True),
        ("rootedKey", "draft", False), ("rootedKey", "run.date", False),
        ("jsonLogic", {"var": "input.kind.value"}, True), ("jsonLogic", {"var": ["a"]}, False),
        ("jsonLogic", {"!": [True]}, True), ("jsonLogic", {"!": True}, False),
        ("jsonLogic", {"object": {"a": 1}}, True), ("jsonLogic", {"object": [1]}, False),
        ("jsonLogic", {"eval": [1]}, False), ("jsonLogic", {"+": [1], "-": [1]}, False),
        ("jsonLogic", [1, {"size": [{"var": "node.a.value"}]}], True),
        ("jsonLogic", {"==": [1, 2]}, False),
        ("condition", None, True), ("condition", {"in": ["a", {"var": "node.a.value"}]}, True),
        ("referenceString", "item.value.title", True), ("referenceString", "pass", True),
        ("referenceString", "param.x", True), ("referenceString", "other.x", False),
    ]
    for name, value, expected in cases:
        if accepts(name, value) != expected:
            failures.append(f"common {name}: expected {value!r} to be "
                            f"{'accepted' if expected else 'refused'}")
    return failures


def check_formats():
    registry, failures = build_registry()
    constants, errors = load(V31 / "constants.json")
    failures += errors
    bounds, errors = load(V31 / "bounds.json")
    failures += errors
    if constants is not None and bounds is not None:
        failures += check_common(registry, constants, bounds)

    folder = V31 / "formats"
    index, errors = load(folder / "index.json")
    failures += errors
    items = []
    if index is not None:
        expect(failures, "formats/index.json keys", list(index), ["description", "items"])
        items = index.get("items", [])
        expect(failures, "formats/index.json items", items, BUILT_IN_FORMATS)
        description = index.get("description")
        if description is not None and not (isinstance(description, list) and description
                                            and all(isinstance(line, str) for line in description)):
            failures.append("formats/index.json: description is null or a list of lines")
    files = sorted(path.stem for path in folder.glob("*.json") if path.name != "index.json")
    expect(failures, "formats/ files", files, sorted(items))

    validator = validator_for(V31 / "dialect.schema.json", registry, failures)
    for name in files:
        path = folder / f"{name}.json"
        document, errors = load(path)
        failures += errors
        if document is None:
            continue
        label = f"formats/{name}.json"
        if validator is not None:
            for error in validator.iter_errors(document):
                failures.append(f"{label}: outside the dialect at /{'/'.join(map(str, error.path))}: "
                                f"{error.message}")
        expect(failures, f"{label} $id", document.get("$id"),
               f"urn:consultologist:spec:31:format:{name}")
        expect(failures, f"{label} $schema", document.get("$schema"), DIALECT_ID)
        media, markdown = ANNOTATIONS.get(name, (None, None))
        expect(failures, f"{label} contentMediaType", document.get("contentMediaType"), media)
        expect(failures, f"{label} x-markdown", document.get("x-markdown"), markdown)
        if not isinstance(document.get("description"), str) or not document["description"]:
            failures.append(f"{label}: no description")
        if document.get("type") == "object":
            for key, child in document["properties"].items():
                if not child.get("description"):
                    failures.append(f"{label}: property {key} has no description")
        failures += declared_but_not_required(document, label)
    return failures


# The registry's own files and the schema each must satisfy. The conformance index is written by a
# later task, so it is judged only once it exists.
SELF = [("bounds", V31 / "bounds.json", True), ("constants", V31 / "constants.json", True),
        ("profile", V31 / "profile.json", True), ("sentences", V31 / "sentences.json", True),
        ("conformance-index", V31 / "conformance" / "index.json", False)]


def check_self():
    registry, failures = build_registry()
    for name, path, required in SELF:
        if not required and not path.exists():
            continue
        document, errors = load(path)
        failures += errors
        validator = validator_for(schema_for(name), registry, failures)
        if document is None or validator is None:
            continue
        for error in validator.iter_errors(document):
            failures.append(f"{path.relative_to(ROOT)}: /{'/'.join(map(str, error.path))}: {error.message}")
    return failures


def check_renderers():
    """Part 05 section 5.1: each renderer file is a header, then a non-empty body of its own."""
    registry, failures = build_registry()
    validator = validator_for(schema_for("renderer"), registry, failures)
    index, errors = load(V31 / "renderers" / "index.json")
    failures += errors
    listed = index["items"] if index else []
    for path in sorted((V31 / "renderers").glob("*.md")):
        where = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        parts = text.split("\n---\n", 1) if text.startswith("---\n") else None
        if parts is None:
            failures.append(f"{where}: does not start with a --- line")
            continue
        header_text, body = parts[0][4:], parts[1] if len(parts) > 1 else ""
        try:
            header = json.loads(header_text)
        except json.JSONDecodeError as error:
            failures.append(f"{where}: the header is not JSON ({error})")
            continue
        if validator:
            for error in validator.iter_errors(header):
                failures.append(f"{where}: header /{'/'.join(map(str, error.path))}: {error.message}")
        if path.stem not in listed:
            failures.append(f"{where}: not listed in renderers/index.json")
        if not body.strip():
            failures.append(f"{where}: the body is empty")
        if "renderer." in body:
            failures.append(f"{where}: the body pipes into a renderer")
    for item in listed:
        if not (V31 / "renderers" / f"{item}.md").exists():
            failures.append(f"renderers/index.json: {item} has no file")
    return failures


DOCUMENT = ROOT / "package-format-v31.md"
DIALECT_DOCUMENT = V31 / "scriban-dialect.md"
DIALECT_VERSION = "scriban-dialect@1.0.0"
CHAPTERS_WRITTEN = 7
LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")


def github_slug(heading):
    """GitHub's anchor for a heading: lower case, punctuation dropped, spaces to hyphens."""
    heading = re.sub(r"[`*]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")


def prose_lines(text):
    """The document's lines outside fenced code blocks, as (line number, line)."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield number, line


def plain(text):
    """Text as a reader sees it: no emphasis markers, no backslash escapes, one space between words."""
    text = text.replace("*", "")
    text = re.sub(r"\\(.)", r"\1", text)
    return re.sub(r"\s+", " ", text)


def parses(text):
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return False
    return True


def unescaped_tags(text, name):
    """GitHub drops an unknown <tag> from prose: a placeholder outside code is written \\<…\\>."""
    failures = []
    for number, line in prose_lines(text):
        if re.search(r"(?<!\\)<[A-Za-z]", re.sub(r"`[^`]*`", "", line)):
            failures.append(f"{name} line {number}: unescaped < before a letter: {line.strip()[:60]}")
    return failures


def check_document():
    if not DOCUMENT.exists():
        return [f"{DOCUMENT.name}: missing"]
    text = DOCUMENT.read_text(encoding="utf-8")
    failures = []
    if "specVersion 31" not in text:
        failures.append("the document never says 'specVersion 31'")
    chapters = [int(m.group(1)) for _, line in prose_lines(text)
                if (m := re.match(r"## (\d+)\. ", line))]
    if chapters != list(range(1, CHAPTERS_WRITTEN + 1)):
        failures.append(f"chapter headings are {chapters}, expected 1 to {CHAPTERS_WRITTEN} in order")
    slugs, seen = set(), {}
    for _, line in prose_lines(text):
        heading = re.match(r"#{1,6} (.*)", line)
        if heading:
            slug = github_slug(heading.group(1))
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            slugs.add(slug if count == 0 else f"{slug}-{count}")
    for marker in ("/blob/main/", "/tree/main/"):
        if marker in text:
            failures.append(f"a link contains {marker}")
    for number, line in prose_lines(text):
        stripped = line.strip()
        if (re.match(r"[.,;:](\s|$)", stripped) or (stripped and not stripped.startswith("```")
                and not re.fullmatch(r"[-|: ]+|[-*+]|\d+\.", stripped)
                and re.fullmatch(r"[^\w{}\[\]()…]+", stripped))):
            failures.append(f"line {number}: a line of orphaned punctuation: {stripped[:40]}")
    for number, line in prose_lines(text):
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, fragment = target.partition("#")
            if path and not (ROOT / path).exists():
                failures.append(f"line {number}: link to {path}, which does not exist")
            elif not path and fragment not in slugs:
                failures.append(f"line {number}: anchor #{fragment} matches no heading")
    failures += unescaped_tags(text, DOCUMENT.name)
    for block in re.finditer(r"(?ms)^```json\n(.*?)^```", text):
        if not parses(block.group(1)) and not parses("{" + block.group(1) + "}"):
            line = text[:block.start()].count("\n") + 1
            failures.append(f"line {line}: a json block does not parse")
    document, load_failures = load(V31 / "sentences.json")
    if document is None:
        return failures + load_failures
    body = plain(text)
    for entry in document["sentences"]:
        if int(entry["part"]) <= len(chapters) and plain(entry["sentence"]) not in body:
            failures.append(f"{entry['id']} (part {entry['part']}, {entry['section']}) "
                            f"is not in the document: {entry['sentence'][:70]}")
    return failures + check_dialect_document({e["sentence"] for e in document["sentences"]})


def check_dialect_document(known_sentences):
    """The versioned dialect: it names its version, its links resolve, every sentence it quotes is the design's."""
    if not DIALECT_DOCUMENT.exists():
        return [f"{DIALECT_DOCUMENT.relative_to(ROOT)}: missing"]
    text = DIALECT_DOCUMENT.read_text(encoding="utf-8")
    where = DIALECT_DOCUMENT.relative_to(ROOT)
    failures = []
    if DIALECT_VERSION not in text:
        failures.append(f"{where}: never names {DIALECT_VERSION}")
    for number, line in prose_lines(text):
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, fragment = target.partition("#")
            if path and not (DIALECT_DOCUMENT.parent / path).resolve().exists():
                failures.append(f"{where} line {number}: link to {path}, which does not exist")
    for marker in ("/blob/main/", "/tree/main/"):
        if marker in text:
            failures.append(f"{where}: a link contains {marker}")
    failures += unescaped_tags(text, str(where))
    known = {plain(sentence) for sentence in known_sentences}
    quoted = re.findall(r'\*"(.*?)"\*', text)
    if not quoted:
        failures.append(f"{where}: quotes no sentence")
    for sentence in quoted:
        if plain(sentence) not in known:
            failures.append(f"{where}: quotes a sentence that is not in sentences.json: {sentence[:70]}")
    return failures


CHECKS = [("constants", check_constants), ("sentences", check_sentences),
          ("examples", check_examples), ("formats", check_formats),
          ("renderers", check_renderers), ("self", check_self),
          ("document", check_document)]


def main():
    failed = False
    for name, check in CHECKS:
        failures = check()
        if failures:
            failed = True
            print(f"FAIL {name}")
            for failure in failures:
                print(f"  {failure}")
        else:
            print(f"ok   {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
