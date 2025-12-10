import pytest

from solvatron.common import KNOWN_SOLVERS
from solvatron.cli import cli, main


@pytest.fixture(
    params=KNOWN_SOLVERS,
)
def solver(request):
    return request.param


def run(*args) -> int:
    return main(cli(args))


def test_success(solver):
    assert (
        run(
            "--solver",
            solver,
            "--channel",
            "conda-forge",
            "python",
        )
        == 0
    )


def test_failure(solver):
    assert (
        run(
            "--solver",
            solver,
            "--channel",
            "conda-forge",
            "python=3",
            "numpy=*=*py27*",
        )
        == 1
    )


def test_several():
    assert (
        run(
            "--solver",
            "rattler",
            "--solver",
            "pixi",
            "--channel",
            "conda-forge",
            "python",
        )
        == 0
    )


def test_compare():
    assert (
        run(
            "--solver",
            "rattler",
            "--solver",
            "pixi",
            "--compare",
            "--channel",
            "conda-forge",
            "python",
        )
        == 0
    )


def test_compare_all(solver):
    if KNOWN_SOLVERS[0] == solver:
        pytest.skip()
    assert (
        run(
            "--solver",
            KNOWN_SOLVERS[0],
            "--solver",
            solver,
            "--channel",
            "conda-forge",
            "python",
        )
        == 0
    )
