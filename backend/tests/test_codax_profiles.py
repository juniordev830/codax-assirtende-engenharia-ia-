"""Validation for inert repository-specific review profiles."""
import base64
import json

from app.github_readonly import _decode_profile, PROFILE_MAX_BYTES


def wrap(payload):
    raw = json.dumps(payload).encode("utf-8")
    return {"type": "file", "size": len(raw), "encoding": "base64",
            "content": base64.b64encode(raw).decode("ascii")}


def test_valid_profile_is_presented_without_extra_fields():
    data = wrap({
        "schema_version": 1,
        "project_kind": "Python CLI",
        "entry_points": ["src/main.py"],
        "test_commands": ["pytest -q"],
        "review_focus": ["Validação", "Dados sensíveis"],
        "untrusted_execution": {"run": "rm -rf /"},
    })
    assert _decode_profile(data) == {
        "schema_version": 1,
        "project_kind": "Python CLI",
        "entry_points": ["src/main.py"],
        "test_commands": ["pytest -q"],
        "review_focus": ["Validação", "Dados sensíveis"],
    }


def test_wrong_schema_and_non_json_are_ignored():
    assert _decode_profile(wrap({"schema_version": 2, "project_kind": "x"})) is None
    assert _decode_profile({"type": "file", "encoding": "base64", "size": 5, "content": "garbage"}) is None
    assert _decode_profile(None) is None


def test_rejects_oversized_and_nonregular_documents():
    assert _decode_profile({"type": "symlink", "size": 10, "encoding": "base64", "content": "e30="}) is None
    assert _decode_profile({"type": "file", "size": PROFILE_MAX_BYTES + 1,
                            "encoding": "base64", "content": "e30="}) is None


def test_filters_large_or_invalid_list_elements():
    data = wrap({
        "schema_version": 1,
        "project_kind": "Go service",
        "entry_points": ["main.go", 123, "", "x" * 400],
        "test_commands": ["go test ./..."],
        "review_focus": list(range(10)),
    })
    profile = _decode_profile(data)
    assert profile["entry_points"] == ["main.go"]
    assert profile["test_commands"] == ["go test ./..."]
    assert profile["review_focus"] == []
