"""The documentation lists exactly the rule ids the engine can emit."""

from pathlib import Path

from address_standardizer.explain import RULES
from address_standardizer.service.review import ENABLE_ENV

DOCS = Path(__file__).resolve().parent.parent / "docs"


def test_every_rule_id_is_documented_with_its_meaning():
    text = (DOCS / "api_reference.md").read_text(encoding="utf-8")
    for rule, meaning in RULES.items():
        assert f"| `{rule}` | {meaning} |" in text, rule


def test_documented_rule_ids_are_all_real():
    text = (DOCS / "api_reference.md").read_text(encoding="utf-8")
    start = text.index("Rule ids:")
    end = text.index("**Per-field confidence.**")
    documented = {line.split("`")[1] for line in text[start:end].splitlines() if line.startswith("| `")}
    assert documented == set(RULES)


def test_review_env_var_and_endpoints_are_documented():
    text = (DOCS / "api_reference.md").read_text(encoding="utf-8")
    for needle in (ENABLE_ENV, "GET /review", "/v1/audit", "include_explanation", "`alternatives`"):
        assert needle in text
