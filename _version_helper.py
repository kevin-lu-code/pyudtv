"""
this module is a hack only in place to allow for setuptools
to use the attribute for the versions

it works only if the backend-path of the build-system section
from pyproject.toml is respected
"""
from __future__ import annotations

import logging
from typing import Callable

from setuptools import build_meta as build_meta  # noqa
from setuptools_scm import Configuration, get_version, git, hg
from setuptools_scm.fallbacks import parse_pkginfo
from setuptools_scm.version import (
    SEMVER_MINOR,
    ScmVersion,
    get_no_local_node,
    guess_next_simple_semver,
    guess_next_version,
)

log = logging.getLogger("setuptools_scm")
# todo: take fake entrypoints from pyproject.toml
try_parse: list[Callable[[str, Configuration], ScmVersion | None]] = [
    parse_pkginfo,
    git.parse,
    hg.parse,
    git.parse_archival,
    hg.parse_archival,
]


def parse(root: str, config: Configuration) -> ScmVersion | None:
    for maybe_parse in try_parse:
        try:
            parsed = maybe_parse(root, config)
        except OSError as e:
            log.info("parse with %s failed with: %s", maybe_parse, e)
        else:
            if parsed is not None:
                return parsed

fmt = "{guessed}rc{distance}" # align with PEP440 public version that has no dot before rc

def custom_version(version: ScmVersion) -> str:
    if version.exact:
        return version.format_with("{tag}")
    # We're in a development branch, next is a minor bump:
    return version.format_next_version(guess_next_simple_semver, retain=SEMVER_MINOR, fmt=fmt)


def scm_version() -> str:
    return get_version(
        relative_to=__file__,
        parse=parse,
        version_scheme=custom_version,
        local_scheme=get_no_local_node,
    )


version: str


def __getattr__(name: str) -> str:
    if name == "version":
        global version
        version = "26.0.0"
        return version
    raise AttributeError(name)
