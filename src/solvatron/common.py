from dataclasses import dataclass

KNOWN_SOLVERS: tuple[str, ...] = (
    "conda",
    "conda-libmamba-solver",
    "conda-rattler-solver",
    "libmambapy",
    "mamba",
    "pixi",
    "rattler",
)


@dataclass(frozen=True, order=True, eq=True)
class Record:
    name: str
    version: str
    build: str
    channel: str
    subdir: str

    def __str__(self):
        return f"{self.channel}/{self.subdir}::{self.name}-{self.version}-{self.build}"


class SolutionNotFound(Exception):
    pass


def solver_to_callable(solver: str):
    from functools import partial

    if solver in ("conda", "conda-libmamba-solver"):
        from .conda import solve

        return partial(solve, solver="libmamba")
    if solver == "conda-rattler-solver":
        from .conda import solve

        return partial(solve, solver="rattler")
    if solver == "libmambapy":
        from .libmambapy import solve

        return solve
    if solver == "mamba":
        from .mamba import solve

        return solve
    if solver == "rattler":
        from .rattler import solve

        return solve
    if solver == "pixi":
        from .pixi import solve

        return solve
    raise ValueError(f"Unknown solver: {solver}")


def solve(
    solver: str,
    specs: list[str],
    channels: list[str],
    subdirs: tuple[str, str],
) -> list[str]:
    solver_func = solver_to_callable(solver)
    return solver_func(specs=specs, channels=channels, subdirs=subdirs)


def report(records_or_error: list[Record] | SolutionNotFound):
    if isinstance(records_or_error, SolutionNotFound):
        print("\n💥🧨💥 Oops! Could not find a solution. This is what the solver said:\n")
        print(str(records_or_error))
        return
    print("\n✨🌟✨ Solution found!\n")
    print(*sorted(records_or_error), sep="\n")


def color_diff(*lines: str):
    from colorama import Fore, init

    init()
    for line in lines:
        if line.startswith("+"):
            yield Fore.GREEN + line + Fore.RESET
        elif line.startswith("-"):
            yield Fore.RED + line + Fore.RESET
        elif line.startswith("?"):
            yield Fore.BLUE + line + Fore.RESET
        else:
            yield line
