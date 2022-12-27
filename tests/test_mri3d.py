"""
Test mri3d root module
"""

import pytest
from pylint.lint import Run
from pylint.reporters import CollectingReporter


@pytest.fixture
def linter():
    """Test codestyle for mri3d"""
    rep = CollectingReporter()

    # disabled warnings:
    # 0301 line too long
    # 0103 variables name (does not like shorter than 2 chars)
    # R0913 Too many arguments (6/5) (too-many-arguments)
    # R0914 Too many local variables (18/15) (too-many-locals)
    r = Run(
        ["--disable=C0301,C0103,R0913,R0914", "-sn", "./mri3d"],
        reporter=rep,
        exit=False,
    )

    return r.linter


@pytest.mark.parametrize("limit", [10])
def test_codestyle_score(linter, limit, runs=[]):
    """Evaluate codestyle for different thresholds."""
    if len(runs) == 0:
        print("\npylint output:")
        for m in linter.reporter.messages:
            print(f"{m.path}:{m.line}:{m.column}: {m.msg_id}: {m.msg} ({m.symbol})")
    runs.append(limit)
    score = linter.stats.global_note

    print(f"\npylint score = {score:.2f}/10")
    assert score >= limit
