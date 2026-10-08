"""Behavior-preservation checks for hot-path optimizations (fast exits / memoization)."""

import random

import pytest

from address_standardizer._patterns import clean_repetitive_cycles


def _build_reference():
    """Original implementation without the all-distinct-tokens fast exit."""
    import address_standardizer._patterns as p
    import inspect

    src = inspect.getsource(p.clean_repetitive_cycles)
    start = src.index("        # Fast exit")
    end = src.index("        def _is_prefix_seq")
    ns = dict(vars(p))
    exec(src[:start] + src[end:], ns)  # noqa: S102 - test-only: rebuild the function without the fast exit
    return ns["clean_repetitive_cycles"]


_reference_clean_repetitive_cycles = _build_reference()


WORDS = ["MAIN", "ST", "100", "STE", "4075", "CALLE", "75", "8-77", "OF.301", "A", "B", "-", ",", "AVE", "n", "N"]


@pytest.mark.parametrize("seed", range(5))
def test_cycle_cleaner_fast_exit_matches_reference(seed):
    rng = random.Random(seed)
    for _ in range(600):
        n = rng.randint(1, 9)
        text = " ".join(rng.choice(WORDS) for _ in range(n))
        if rng.random() < 0.3:
            text = text + ", " + text
        assert clean_repetitive_cycles(text) == _reference_clean_repetitive_cycles(text), text
