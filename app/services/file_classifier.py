from pathlib import Path


SOURCE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cs", ".php"
}

DOC_EXTENSIONS = {
    ".md", ".txt", ".rst"
}

CONFIG_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env.example"
}

GENERATED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pipfile.lock",
}

INFRA_PREFIXES = (
    ".github/",
    "docker/",
    "infra/",
    "terraform/",
    "k8s/",
)


def classify_file(filename: str) -> str:
    path = filename.lower()
    name = Path(path).name
    suffix = Path(path).suffix

    if is_generated_file(path):
        return "generated"

    if path.startswith(INFRA_PREFIXES):
        return "infrastructure"

    if is_test_file(path):
        return "test"

    if suffix in DOC_EXTENSIONS:
        return "docs"

    if suffix in CONFIG_EXTENSIONS:
        return "config"

    if suffix in SOURCE_EXTENSIONS:
        return "source"

    return "unknown"


def is_test_file(filename: str) -> bool:
    name = Path(filename).name

    return (
        filename.startswith("tests/")
        or "/tests/" in filename
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.js")
        or name.endswith(".test.ts")
        or name.endswith(".spec.js")
        or name.endswith(".spec.ts")
    )


def is_generated_file(filename: str) -> bool:
    name = Path(filename).name

    if name in GENERATED_FILES:
        return True

    if filename.endswith(".min.js") or filename.endswith(".min.css"):
        return True

    if "dist/" in filename or "build/" in filename:
        return True

    return False


def should_ignore_file(filename: str) -> bool:
    return classify_file(filename) == "generated"