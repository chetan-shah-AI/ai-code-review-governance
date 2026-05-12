from app.services.file_classifier import classify_file, should_ignore_file


def test_classifies_python_source():
    assert classify_file("app/services/user_service.py") == "source"


def test_classifies_test_file():
    assert classify_file("tests/test_user_service.py") == "test"


def test_classifies_docs():
    assert classify_file("README.md") == "docs"


def test_classifies_github_workflow_as_infrastructure():
    assert classify_file(".github/workflows/ci.yml") == "infrastructure"


def test_classifies_config():
    assert classify_file("pyproject.toml") == "config"


def test_classifies_generated_file():
    assert classify_file("package-lock.json") == "generated"


def test_should_ignore_generated_file():
    assert should_ignore_file("yarn.lock") is True


def test_does_not_ignore_source_file():
    assert should_ignore_file("app/main.py") is False