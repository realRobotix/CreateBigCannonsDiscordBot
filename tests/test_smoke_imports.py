"""Basic smoke test to catch packaging/import regressions in CI and local dev."""

import importlib

MODULES = [
    "cbcbot.bot",
    "cbcbot.utils.settings",
    "cbcbot.extensions.base.manager",
    "cbcbot.extensions.github.github",
    "cbcbot.extensions.curseforge.curseforge",
    "cbcbot.extensions.moderator.moderator",
    "cbcbot.extensions.moderator.quicksand",
    "cbcbot.extensions.stars.stars",
    "cbcbot.extensions.addonsquared.tanktussle",
    "cbcbot.extensions.addonsquared.nuclear",
    "cbcbot.extensions.addonsquared.cbc_modernwarfare",
    "cbcbot.extensions.addonsquared.advancedtechnologies",
]


def test_smoke_imports() -> None:
    for module in MODULES:
        importlib.import_module(module)
