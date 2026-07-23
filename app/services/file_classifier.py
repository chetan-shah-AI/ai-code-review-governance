
from pathlib import Path


# Source code file extensions
SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rs",
    ".cs",
    ".php",
}


# Documentation file extensions
DOC_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
}


# Config file extensions
CONFIG_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".env.example",
}


# Common generated / lock files
GENERATED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "pipfile.lock",
}


# Infrastructure-related folders
INFRA_PREFIXES = (
    ".github/",
    "docker/",
    "infra/",
    "terraform/",
    "k8s/",
)


def classify_file(filename: str) -> str:
    """
    Classify a file into a review category.

    Returns:
        - source
        - test
        - docs
        - config
        - infrastructure
        - generated
        - unknown
    """

    # Convert path to lowercase for safer matching
    path = filename.lower()

    # Extract filename only
    name = Path(path).name

    # Extract extension
    suffix = Path(path).suffix

    # Check generated files first
    if is_generated_file(path):
        return "generated"

    # Infrastructure folders
    if path.startswith(INFRA_PREFIXES):
        return "infrastructure"

    # Test files
    if is_test_file(path):
        return "test"

    # Documentation files
    if suffix in DOC_EXTENSIONS:
        return "docs"

    # Config files
    if suffix in CONFIG_EXTENSIONS:
        return "config"

    # Source code files
    if suffix in SOURCE_EXTENSIONS:
        return "source"

    # Unknown file type
    return "unknown"


def is_test_file(filename: str) -> bool:
    """
    Detect whether a file is a test file.
    """

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
    """
    Detect generated files that should usually be ignored.
    """

    name = Path(filename).name

    # Exact generated file names
    if name in GENERATED_FILES:
        return True

    # Minified frontend assets
    if filename.endswith(".min.js") or filename.endswith(".min.css"):
        return True

    # Build output folders
    if "dist/" in filename or "build/" in filename:
        return True

    return False


def should_ignore_file(filename: str) -> bool:
    """
    Determine if a file should be ignored entirely.
    """

    return classify_file(filename) == "generated"

