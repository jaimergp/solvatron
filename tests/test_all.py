import sys

import pytest

from solvatron.common import KNOWN_SOLVERS
from solvatron.cli import ArgumentError, cli, main


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


@pytest.mark.skipif(sys.platform.startswith("linux"), reason="Only not Linux")
def test_cross_solve_linux(monkeypatch):
    with pytest.raises(ArgumentError):
        run("--platform", "linux-64", "--solver", "rattler", "-c", "conda-forge", "python")
    monkeypatch.setenv("CONDA_OVERRIDE_UNIX", "1")
    monkeypatch.setenv("CONDA_OVERRIDE_LINUX", "5")
    monkeypatch.setenv("CONDA_OVERRIDE_GLIBC", "2.34")
    assert run("--platform", "linux-64", "--solver", "rattler", "-c", "conda-forge", "python") == 0


@pytest.mark.skipif(sys.platform == "darwin", reason="Only not macOS")
def test_cross_solve_osx(monkeypatch):
    with pytest.raises(ArgumentError):
        run("--platform", "osx-64", "--solver", "rattler", "-c", "conda-forge", "python")
    monkeypatch.setenv("CONDA_OVERRIDE_UNIX", "1")
    monkeypatch.setenv("CONDA_OVERRIDE_OSX", "11.0")
    assert run("--platform", "osx-64", "--solver", "rattler", "-c", "conda-forge", "python") == 0


@pytest.mark.skipif(sys.platform == "win32", reason="Only not Windows")
def test_cross_solve_win(monkeypatch):
    with pytest.raises(ArgumentError):
        run("--platform", "win-64", "--solver", "rattler", "-c", "conda-forge", "python")
    monkeypatch.setenv("CONDA_OVERRIDE_WIN", "10")
    assert run("--platform", "win-64", "--solver", "rattler", "-c", "conda-forge", "python") == 0
