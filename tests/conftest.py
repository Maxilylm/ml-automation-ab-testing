"""Shared pytest fixtures for ml-automation-ab-testing."""
from __future__ import annotations
import pytest
from pathlib import Path


@pytest.fixture
def mock_llm_response():
    """Deterministic LLM response for evaluation/integration tests.

    Returns a dict shaped like a typical LLM API response, with predictable
    content to make assertions easy.
    """
    return {
        "id": "test-completion-001",
        "model": "claude-opus-4-7",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": "test response content"},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


@pytest.fixture
def sample_dataset():
    """Small in-memory dataset for ML pipeline tests.

    Returns a list of dicts. Each row has: id, feature_a, feature_b, label.
    Deterministic — first 10 rows of a synthetic distribution.
    """
    return [
        {"id": i, "feature_a": float(i), "feature_b": float(i * 2), "label": i % 2}
        for i in range(10)
    ]


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Isolated tmpdir for plugin filesystem operations.

    Returns a Path. pytest's tmp_path already isolates per-test; this fixture
    is a thin wrapper that gives the fixture a project-canonical name.
    """
    return tmp_path
