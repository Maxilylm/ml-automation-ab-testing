"""Smoke tests for ml-automation-ab-testing — validate plugin layout invariants."""
from __future__ import annotations
import json
import re
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def test_plugin_manifest_parses_and_has_required_fields():
    """The .cortex-plugin/plugin.json manifest is valid JSON with required metadata fields."""
    manifest_path = PLUGIN_ROOT / ".cortex-plugin" / "plugin.json"
    assert manifest_path.exists(), f"manifest missing at {manifest_path.relative_to(PLUGIN_ROOT)}"

    manifest = json.loads(manifest_path.read_text())
    for field in ("name", "version", "description"):
        assert field in manifest, f"manifest missing required field: {field}"
    assert manifest["name"].startswith("spark-"), f"manifest name '{manifest['name']}' does not match spark-<domain>"


def test_agents_md_lists_all_agents_and_skills():
    """AGENTS.md references every file in agents/ and every dir in skills/ — no orphans."""
    agents_md = PLUGIN_ROOT / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md missing"
    text = agents_md.read_text()

    agents_dir = PLUGIN_ROOT / "agents"
    if agents_dir.exists():
        for f in agents_dir.glob("*.md"):
            name = f.stem
            assert re.search(rf"\b{re.escape(name)}\b", text), \
                f"agents/{name}.md exists but is not referenced in AGENTS.md (orphan)"

    skills_dir = PLUGIN_ROOT / "skills"
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir():
                name = d.name
                assert re.search(rf"\b/?{re.escape(name)}\b", text), \
                    f"skills/{name}/ exists but is not referenced in AGENTS.md (orphan)"
