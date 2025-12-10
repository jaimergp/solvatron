import argparse
import os
from difflib import ndiff
from pathlib import Path


class ArgumentError(Exception): ...


def cli(args: list[str] | None = None):
    from typing import get_args

    from rattler.platform import PlatformLiteral

    from .common import KNOWN_SOLVERS

    p = argparse.ArgumentParser(
        prog="solvatron",
        description="Compare conda solves across different implementations.",
        epilog="""
            Example:
            python -m solvatron -s rattler -c conda-forge python
            """,
    )
    p.add_argument(
        "--compare",
        action="store_true",
        help="Compare solutions. Must pass two solvers.",
    )
    p.add_argument(
        "-c",
        "--channel",
        action="append",
        help="Where to pull packages from. Can be used several times. "
        "First ones will have higher priority.",
    )
    p.add_argument(
        "-s",
        "--solver",
        action="append",
        choices=KNOWN_SOLVERS,
        help="Which solver to use. Can be used several times.",
    )
    p.add_argument(
        "--platform",
        choices=[p for p in get_args(PlatformLiteral) if p not in ("unknown", "noarch")],
        help="Platform (or subdir) to run solves for; e.g. 'linux-64'. "
        "If cross-solving, make sure to set appropriate CONDA_OVERRIDE_* environment variables.",
    )
    p.add_argument(
        "-f",
        "--file",
        help="Path to file with one requirement per line. #-comments will be ignored.",
    )
    p.add_argument("specs", nargs="*", help="Requirements to solve for.")
    return p.parse_args(args)


def main(args: argparse.Namespace) -> int:
    import time
    from datetime import timedelta

    from rattler import MatchSpec, Platform

    from .common import SolutionNotFound, color_diff, report, solve

    specs = args.specs
    if args.file:
        specs.extend(
            [
                line
                for line in Path(args.file).read_text().splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
        )
    if not specs:
        raise ArgumentError("One or more specs are required.")
    if not args.solver:
        raise ArgumentError("One or more solvers are required.")
    if not args.channel:
        raise ArgumentError("One or more channels are required.")
    if args.compare and not len(args.solver):
        raise ArgumentError(
            args.compare,
            f"With --compare, two solvers MUST be passed, but you passed {len(args.solver)}.",
        )
    if args.platform:
        subdirs = [args.platform, "noarch"]
        target_os = args.platform.split("-")[0]
        if not str(Platform.current()).startswith(target_os):
            if target_os == "linux" and not all(
                os.environ.get(f"CONDA_OVERRIDE_{var}") for var in ("LINUX", "GLIBC", "UNIX")
            ):
                raise ArgumentError(
                    "When cross-solving for linux, you must set __glibc, __unix and __linux; e.g.\n"
                    "CONDA_OVERRIDE_GLIBC=2.17 CONDA_OVERRIDE_LINUX=5 CONDA_OVERRIDE_UNIX=1 "
                    "python -m solvatron ..."
                )
            elif target_os == "osx" and not all(
                os.environ.get(f"CONDA_OVERRIDE_{var}") for var in ("OSX", "UNIX")
            ):
                raise ArgumentError(
                    "When cross-solving for macOS, you must set the OSX version; e.g.:\n"
                    "CONDA_OVERRIDE_OSX=11.0 python -m solvatron ..."
                )
            elif target_os == "win" and not os.environ.get("CONDA_OVERRIDE_WIN"):
                raise ArgumentError(
                    "When cross-solving for Windows, you must set the Windows version; e.g.:\n"
                    "CONDA_OVERRIDE_WIN=10 python -m solvatron ..."
                )
    else:
        subdirs = None

    exit_code = 0
    results = []
    timings = []
    if args.compare:
        title = f"Comparing {args.solver[0]} vs {args.solver[1]}"
        print("-" * len(title))
        print(title)
        print("-" * len(title))

    requested_names = [MatchSpec(spec, strict=False).name.normalized for spec in specs]
    for solver in args.solver:
        t0 = time.perf_counter()
        try:
            outcome = solve(
                solver=solver,
                specs=specs,
                channels=args.channel,
                subdirs=subdirs,
            )
        except SolutionNotFound as exc:
            outcome = exc
            exit_code = 1
        t1 = time.perf_counter()
        if exit_code == 0 and args.compare:
            results.append(sorted(outcome))
            timings.append(t1 - t0)
        else:
            title = f"Solving for {solver}"
            print("-" * len(title))
            print(title)
            print("-" * len(title))
            report(outcome)
            print()
            print(f"⏱️ Took {timedelta(seconds=t1 - t0)}s")
            print()

    if args.compare and len(results) == 2:
        if results[0] != results[1]:
            print()
            print("⚠️  Different solutions observed!")
            print()
            print(
                *color_diff(
                    "Legend:",
                    "  same in both",
                    f"- only in {args.solver[0]}",
                    f"+ only in {args.solver[1]}",
                    "",
                    "Requested specs diff:",
                    *ndiff(
                        [str(r) for r in results[0] if r.name in requested_names],
                        [str(r) for r in results[1] if r.name in requested_names],
                    ),
                    "All packages diff:",
                    *ndiff(
                        list(map(str, results[0])),
                        list(map(str, results[1])),
                    ),
                ),
                sep="\n",
            )
            print()
            exit_code = 1
        else:
            report(results[0])
            print()
            exit_code = 0
        print(f"⏱️  {args.solver[0]} took {timedelta(seconds=timings[0])}s")
        print(f"⏱️  {args.solver[1]} took {timedelta(seconds=timings[1])}s")

    return exit_code
