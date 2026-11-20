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


# The registry's own files, each required, and the schema each must satisfy.
SELF = [("bounds", V31 / "bounds.json"), ("constants", V31 / "constants.json"),
        ("profile", V31 / "profile.json"), ("sentences", V31 / "sentences.json"),
        ("conformance-index", V31 / "conformance" / "index.json")]


def check_self():
    registry, failures = build_registry()
    for name, path in SELF:
        document, errors = load(path)
        failures += errors
        validator = validator_for(schema_for(name), registry, failures)
        if document is None or validator is None:
            continue
        for error in validator.iter_errors(document):
            failures.append(f"{path.relative_to(ROOT)}: /{'/'.join(map(str, error.path))}: {error.message}")
    return failures


# The renderers chapter 5 section 5.5.1 prints whole, byte for byte.
PRINTED_RENDERERS = ["concept_bullets"]


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
    document = DOCUMENT.read_text(encoding="utf-8") if DOCUMENT.exists() else ""
    for item in PRINTED_RENDERERS:
        path = V31 / "renderers" / f"{item}.md"
        if path.exists() and f"```\n{path.read_text(encoding='utf-8')}```\n" not in document:
            failures.append(f"{DOCUMENT.name}: no code block prints {path.relative_to(ROOT)} as it is")
    return failures


DOCUMENT = ROOT / "package-format-v31.md"
DIALECT_DOCUMENT = V31 / "scriban-dialect.md"
DIALECT_VERSION = "scriban-dialect@1.0.0"
CHAPTERS_WRITTEN = 12
SENTENCES_CHAPTER = 11
CONFORMANCE_CHAPTER = 12
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


def chapter_bodies(text):
    """Each chapter's text, by number: the lines under its `## N.` heading, fenced code included."""
    bodies, current, fenced = {}, None, False
    for line in text.splitlines():
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"## (\d+)\. ", line)
        if heading:
            current = int(heading.group(1))
            bodies[current] = ""
        elif current is not None:
            bodies[current] += line + "\n"
    return bodies


def heading_sections(text):
    """Every heading of the document as (chapter number, title without its number, text under it, subsections included)."""
    lines, found, fenced = text.splitlines(), [], False
    for number, line in enumerate(lines):
        if line.startswith("```"):
            fenced = not fenced
        heading = None if fenced else re.match(r"(#{2,6}) (.*)", line)
        if heading:
            found.append((number, len(heading.group(1)), heading.group(2)))
    sections, chapter = [], 0
    for position, (number, level, title) in enumerate(found):
        end = next((n for n, deeper, _ in found[position + 1:] if deeper <= level), len(lines))
        if level == 2:
            chapter = int(title.split(".")[0]) if re.match(r"\d+\. ", title) else 0
        sections.append((chapter, re.sub(r"^[\d.]+\s+", "", title), "\n".join(lines[number + 1:end])))
    return sections


def check_chapter_cells(text, table):
    """Each row's Chapter cell names a heading of that chapter, and the row's sentence is given under it."""
    failures, sections = [], heading_sections(text)
    for line in table[2:]:
        id_, cell, sentence = [c.strip() for c in table_cells(line)[:3]]
        chapter, _, title = cell.partition(" · ")
        title = re.sub(r"\\(.)", r"\1", title)
        if not any(number == int(chapter) and name == title and plain(sentence) in plain(body)
                   for number, name, body in sections):
            failures.append(f"{id_}: no heading '{title}' in chapter {chapter} gives the sentence")
    return failures


def table_cells(row):
    """A table row's cells: the id, the Chapter cell, and the sentence without its *\"…\"* frame."""
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", row)[1:-1]]
    return [cells[0], cells[1], cells[2][2:-2]]


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
    bodies = chapter_bodies(text)
    renderer = load_renderer()
    for entry in document["sentences"]:
        chapter = renderer.CHAPTER_OF_PART[entry["part"]]
        if plain(entry["sentence"]) not in plain(bodies.get(chapter, "")):
            failures.append(f"{entry['id']} (part {entry['part']}, {entry['section']}) is not in "
                            f"chapter {chapter}: {entry['sentence'][:70]}")
    table = [line for line in bodies.get(SENTENCES_CHAPTER, "").splitlines() if line.startswith("|")]
    expected_rows = [(e["id"], e["sentence"], e["audience"]) for e in document["sentences"]]
    if renderer.parse(renderer.render(document["sentences"])) != expected_rows:
        failures.append("scripts/render-sentences.py does not round-trip the sentences")
    if table != renderer.render(document["sentences"]).splitlines():
        failures.append(f"chapter {SENTENCES_CHAPTER}'s table is not what scripts/render-sentences.py prints")
    failures += check_chapter_cells(text, table)
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


def conformance_table_rows(chapter):
    """Chapter 12's suite table, by family id: the Lives-at cell and the Exported-by cell."""
    rows = {}
    for line in chapter.splitlines():
        cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) == 4 and re.fullmatch(r"`[a-z-]+`", cells[1]):
            rows[cells[1].strip("`")] = (cells[2], cells[3])
    return rows


def check_conformance_index():
    """Chapter 12's suite: the index names real cases, lists `schemas`' example files exactly, and follows chapter 12's table."""
    path = V31 / "conformance" / "index.json"
    document, failures = load(path)
    if document is None:
        return failures
    families = document.get("families", [])
    ids = [family.get("id") for family in families]
    if len(set(ids)) != len(ids):
        failures.append(f"{path.relative_to(ROOT)}: a family id is repeated")
    for family in families:
        for case in family.get("cases", []):
            # A case is a file (a schema's example) or a folder (a refusal package's valid/ or invalid/).
            if not (ROOT / family.get("path", "") / case).exists():
                failures.append(f"family {family.get('id')}: case {case} is not a file or folder under {family.get('path')}")
        if family.get("id") == "schemas":
            on_disk = sorted(str(file.relative_to(CONFORMANCE)) for file in CONFORMANCE.rglob("*.json"))
            expect(failures, "the schemas family's cases (the example files on disk)",
                   sorted(family.get("cases", [])), on_disk)
    if "schemas" not in ids:
        failures.append("the index has no schemas family")
    chapter = chapter_bodies(DOCUMENT.read_text(encoding="utf-8")).get(CONFORMANCE_CHAPTER, "")
    rows = conformance_table_rows(chapter)
    positions = [chapter.find(f"| `{id_}` |") for id_ in ids]
    if -1 in positions or positions != sorted(positions) or sorted(rows) != sorted(ids):
        failures.append(f"chapter {CONFORMANCE_CHAPTER}'s table does not list the index's families in order: {ids}")
    for family in families:
        lives_at, exported_by = rows.get(family.get("id"), ("", ""))
        where = family.get("path", "").rstrip("/")
        if not any(token.startswith(where) for token in re.findall(r"`([^`]+)`", lives_at)):
            failures.append(f"family {family.get('id')}: path {where} is not in chapter {CONFORMANCE_CHAPTER}'s Lives-at cell")
        expect(failures, f"family {family.get('id')}'s exportedBy against chapter {CONFORMANCE_CHAPTER}'s table",
               family.get("exportedBy"), exported_by.replace(" (here, now)", ""))
    return failures


REFUSAL_PACKAGES = V31 / "conformance" / "refusal-packages"
AREA_SENTENCE_ID = re.compile(r"^A\d{2}-\d{3}$")
EXPECT_KEYS = ["about", "valid", "sentences"]
# The one case whose package has no manifest.json: its sentence is about that absence.
WITHOUT_MANIFEST = {"A02-003/invalid"}


def sentence_pattern(id_, row):
    """A row of sentences.json as a pattern: literal text escaped; each outermost <…> (nested ones, and
    <a | b> choices, as one) any text, non-greedy. S04-009's first word may be any flow kind's, as
    chapter 4 says ("also While, If, Case")."""
    pattern, literal, depth = "", "", 0
    for character in row:
        if character == "<":
            if depth == 0:
                pattern += re.escape(literal) + ".+?"
                literal = ""
            depth += 1
        elif character == ">" and depth > 0:
            depth -= 1
        elif depth == 0:
            literal += character
    pattern += re.escape(literal)
    if id_ == "S04-009":
        pattern = "(?:Loop|While|If|Case)" + pattern[len(re.escape("Loop")):]
    return pattern


def check_refusal_packages():
    """Chapter 12 § 12.3's refusal packages: the family lists exactly the case folders on disk; each
    expect.json is { about, valid, sentences }, valid as its folder says; an invalid case's sentence
    is its row of sentences.json, as a pattern (an A<area>-<n> case is this implementation's sentence,
    judged by shape only); every package has its manifest.json."""
    index, failures = load(V31 / "conformance" / "index.json")
    document, errors = load(V31 / "sentences.json")
    failures += errors
    if index is None or document is None:
        return failures
    rows = {entry["id"]: entry["sentence"] for entry in document.get("sentences", [])}
    family = next((f for f in index.get("families", []) if f.get("id") == "refusal-packages"), None)
    if family is None:
        return failures + ["the index has no refusal-packages family"]

    on_disk = sorted(f"{case.name}/{side.name}"
                     for case in (REFUSAL_PACKAGES.iterdir() if REFUSAL_PACKAGES.is_dir() else [])
                     if case.is_dir() for side in case.iterdir() if side.is_dir())
    expect(failures, "the refusal-packages family's cases (the case folders on disk)",
           sorted(family.get("cases", [])), on_disk)
    for case in on_disk:
        id_, side = case.split("/")
        where = f"refusal-packages/{case}"
        if side not in ("valid", "invalid"):
            failures.append(f"{where}: a case folder is valid/ or invalid/")
            continue
        if id_ not in rows and not AREA_SENTENCE_ID.match(id_):
            failures.append(f"{where}: {id_} is neither a row of sentences.json nor an area's sentence")
        if case not in WITHOUT_MANIFEST and not (REFUSAL_PACKAGES / case / "package" / "manifest.json").is_file():
            failures.append(f"{where}: no package/manifest.json")
        expected, errors = load(REFUSAL_PACKAGES / case / "expect.json")
        failures += errors
        if expected is None:
            continue
        if not isinstance(expected, dict) or list(expected) != EXPECT_KEYS:
            failures.append(f"{where}/expect.json: expected exactly {EXPECT_KEYS}")
            continue
        about, valid, sentences = (expected[key] for key in EXPECT_KEYS)
        if not isinstance(about, str) or not about.strip():
            failures.append(f"{where}/expect.json: about is not a non-empty string")
        if valid is not (side == "valid"):
            failures.append(f"{where}/expect.json: valid is {valid!r} in a {side}/ folder")
        if not isinstance(sentences, list) or not all(isinstance(s, str) for s in sentences):
            failures.append(f"{where}/expect.json: sentences is not a list of strings")
            continue
        if (side == "valid") == bool(sentences):
            failures.append(f"{where}/expect.json: a valid package says no sentence, an invalid one at least one")
        # A case that cannot break its rule alone lists every sentence the parser gives; one is its own.
        if side == "invalid" and id_ in rows and sentences:
            pattern = sentence_pattern(id_, rows[id_])
            if not any(re.fullmatch(pattern, sentence, re.DOTALL) for sentence in sentences):
                failures.append(f"{where}/expect.json: no sentence is {id_}'s row: {sentences[0][:70]}")
    return failures


PART_CITATION = re.compile(r"\b[Pp]arts? \d{2}\b")


def check_citations():
    """A reader has the document's chapters, not the design's parts: no JSON under v31/ cites a part."""
    failures = []
    for path in sorted(V31.rglob("*.json")):
        for match in PART_CITATION.finditer(path.read_text(encoding="utf-8")):
            failures.append(f"{path.relative_to(ROOT)}: cites '{match.group(0)}'; cite the chapter")
    return failures


CHECKS = [("constants", check_constants), ("sentences", check_sentences),
          ("examples", check_examples), ("formats", check_formats),
          ("renderers", check_renderers), ("self", check_self),
          ("conformance", check_conformance_index), ("refusal-packages", check_refusal_packages),
          ("document", check_document), ("citations", check_citations)]


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
