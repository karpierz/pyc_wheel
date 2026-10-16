# flake8-in-file-ignores: noqa: F401,F403,F821

# Copyright (c) 2016 Grant Patten
# Copyright (c) 2019 Adam Karpierz
# SPDX-License-Identifier: MIT

from __future__ import annotations

from .__about__ import * ; del __about__  # type: ignore[name-defined]

from ._pyc_wheel import * ; del _pyc_wheel  # type: ignore[name-defined]
