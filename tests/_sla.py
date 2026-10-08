"""Shared scaling for wall-clock / memory SLA assertions (tests marked ``perf``).

Slow shared CI runners set ``ADDRESS_STANDARDIZER_SLA_SCALE`` below 1.0 (e.g. 0.6): latency and memory ceilings are
divided by it, so a 0.6 scale allows ~67% more time than on developer hardware.
"""

import os

SLA_SCALE = float(os.environ.get("ADDRESS_STANDARDIZER_SLA_SCALE", "1.0"))
