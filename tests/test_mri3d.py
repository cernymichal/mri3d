"""
Test mri3d root module
"""

# pylint: disable=redefined-outer-name

import pytest
from pylint.lint import Run
from pylint.reporters import CollectingReporter


@pytest.fixture
def linter():
    """Test codestyle for mri3d"""
    rep = CollectingReporter()

    r = Run(
        ["-sn", "./mri3d"],
        reporter=rep,
        exit=False,
    )

    return r.linter


@pytest.mark.parametrize("limit", [10])
def test_codestyle_score(linter, limit, runs=[]):  # pylint: disable=dangerous-default-value
    """Evaluate codestyle for different thresholds."""
    if len(runs) == 0:
        print("\npylint output:")
        for m in linter.reporter.messages:
            print(f"{m.path}:{m.line}:{m.column}: {m.msg_id}: {m.msg} ({m.symbol})")
    runs.append(limit)
    score = linter.stats.global_note

    print(f"\npylint score = {score:.2f}/10")
    assert score >= limit
