import asyncio


from rattler import MatchSpec, VirtualPackage, VirtualPackageOverrides, solve as rattler_solve
from rattler.exceptions import SolverError

from .common import Record, SolutionNotFound


def solve(specs: list[str], channels: list[str], subdirs: list[str]) -> list[Record]:
    return asyncio.run(_solve(specs, channels, subdirs))


async def _solve(specs: list[str], channels: list[str], subdirs: list[str]) -> list[Record]:
    try:
        solved_records = await rattler_solve(
            # Channels to use for solving
            channels=channels,
            platforms=subdirs,
            # The specs to solve for
            specs=[MatchSpec(spec, strict=False) for spec in specs],
            # Virtual packages define the specifications of the environment
            virtual_packages=VirtualPackage.detect(overrides=VirtualPackageOverrides.from_env()),
        )
    except SolverError as exc:
        raise SolutionNotFound(str(exc))
    return [
        Record(
            name=r.name.normalized,
            version=str(r.version),
            build=r.build,
            channel=r.channel.replace("https://conda.anaconda.org/", "").rstrip("/"),
            subdir=r.subdir,
        )
        for r in solved_records
    ]
