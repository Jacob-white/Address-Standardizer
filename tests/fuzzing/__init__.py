"""
Property-Based Generative Fuzzing Suite for Address Standardizer.
==================================================================
Dual-mode validation suite (Hypothesis + deterministic fallback matrix):
  - test_fuzz_crash_resilience.py: Crash prevention on arbitrary inputs
  - test_fuzz_idempotence.py: Mathematical idempotence S(S(A)) == S(A)
  - test_fuzz_key_determinism.py: Bit-for-bit key invariance across repetitions/threads
  - test_fuzz_key_ascii_purity.py: ASCII purity (isascii == True) across all keys
"""
