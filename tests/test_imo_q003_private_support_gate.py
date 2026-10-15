#!/usr/bin/env python3
"""Run the synthetic Q003 TEST support gate in the normal IMO research CI suite.

The protected original Q003 is never loaded or reconstructed here.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_SCOPED_TEST = (
    Path(__file__).resolve().parents[1]
    / "TEST/imo-research/core2-q003/test_private_support_gate.py"
)
_spec = spec_from_file_location("imo_q003_private_support_gate_scoped", _SCOPED_TEST)
_scoped = module_from_spec(_spec)
_spec.loader.exec_module(_scoped)

Q003PrivateSupportGate = _scoped.Q003PrivateSupportGate
