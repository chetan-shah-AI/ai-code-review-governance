from typing import List, Dict

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".lock", ".log", ".env"
}

CONFIG_FILES = {
    "pyproject.toml",
    "requirements.txt",
    "package.json",
    "Dockerfile",
    "docker-compose.yml"
}

def detect_language(filename: str) -> str:
    filename = filename.lower()

    if filename.endswith(".py"):
        return "python"
    elif filename.endswith(".js"):
        return "javascript"
    elif filename.endswith(".ts"):
        return "typescript"
    elif filename.endswith(".java"):
        return "java"
    elif filename.endswith(".go"):
        return "go"
    elif filename.endswith(".rs"):
        return "rust"
    elif filename.endswith(".md") or "readme" in filename:
        return "Readme/Documentation"
    else:
        return "unknown"
    


def classify_files(files: List[dict]) -> Dict[str, List[dict]]:
    categories = {
        "source": [],
        "tests": [],
        "config": [],
        "docs": [],
        "infra": [],
        "ignored": []
    }

    for f in files:
        filename = f.get("filename", "").lower()

        # 🔥 Add this
        f["language"] = detect_language(filename)

        # Ignore binaries / useless files
        if any(filename.endswith(ext) for ext in IGNORE_EXTENSIONS):
            categories["ignored"].append(f)
            continue

        # Config files
        if any(name in filename for name in CONFIG_FILES):
            categories["config"].append(f)
            continue

        # Test files
        if "test" in filename or filename.startswith("tests/"):
            categories["tests"].append(f)
            continue

        # Docs
        if filename.endswith(".md") or "readme" in filename:
            categories["docs"].append(f)
            continue

        # Infra
        if "docker" in filename or "k8s" in filename or "terraform" in filename:
            categories["infra"].append(f)
            continue

        # Default → source code
        categories["source"].append(f)

    return categories