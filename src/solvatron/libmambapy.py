import os
import sys
from functools import cache
from pathlib import Path

from conda.base.context import context
from conda.core.index import Index
from conda.core.subdir_data import SubdirData
from conda.models.channel import Channel
from libmambapy import Context, ContextOptions, Repo
from libmambapy.solver import ProblemsMessageFormat, Request, Solution
from libmambapy.solver.libsolv import (
    Database,
    PackageTypes,
    PipAsPythonDependency,
    Priorities,
    RepodataOrigin,
    UnSolvable,
)
from libmambapy.solver.libsolv import Solver as LibsolvSolver
from libmambapy.specs import (
    ChannelResolveParams,
    CondaURL,
    PackageInfo,
)
from libmambapy.specs import MatchSpec as LibmambaMatchSpec

from .common import Record, SolutionNotFound


def _load_channel(db: Database, channel: str, subdir: str) -> Repo:
    channel_id = f"{channel}/{subdir}"
    channel_obj = Channel(channel_id)
    sd = SubdirData(channel=channel_obj)
    json_path, state = sd.repo_fetch.fetch_latest_path()
    json_path = Path(json_path)
    solv_path = json_path.with_suffix(".solv")

    try_solv = sys.platform == "win32"
    if try_solv:
        repodata_origin = RepodataOrigin(url=channel_obj.url(), etag=state.etag, mod=state.mod)
        try:
            return db.add_repo_from_native_serialization(
                path=str(solv_path),
                expected=repodata_origin,
                channel_id=channel_id,
                add_pip_as_python_dependency=PipAsPythonDependency(
                    context.add_pip_as_python_dependency
                ),
            )
        except Exception:
            pass
    repo = db.add_repo_from_repodata_json(
        path=str(json_path),
        url=channel_obj.url(),
        channel_id=channel_id,
        add_pip_as_python_dependency=PipAsPythonDependency(context.add_pip_as_python_dependency),
        package_types=(
            PackageTypes.TarBz2Only if context.use_only_tar_bz2 else PackageTypes.CondaOrElseTarBz2
        ),
    )
    if try_solv:
        db.native_serialize_repo(
            repo=repo,
            path=str(solv_path),
            metadata=repodata_origin,
        )
    return repo


def _setup_priorities(db: Database, repos: list[Repo]) -> None:
    has_priority = True

    def canonical_name(repo) -> str:
        return "/".join(repo.name.split("/")[:-1])

    subprio_index = len(repos)
    if has_priority:
        # max channel priority value is the number of unique channels
        channel_prio = len({canonical_name(repo) for repo in repos})
        current_channel_name = canonical_name(repos[0])

    for repo in repos:
        if has_priority:
            if canonical_name(repo) != current_channel_name:
                channel_prio -= 1
                current_channel_name = canonical_name(repo)
            priority = channel_prio
        else:
            priority = 0
        if has_priority:
            # NOTE: -- This was originally 0, but we need 1.
            # Otherwise, conda/conda @ test_create::test_force_remove fails :shrug:
            subpriority = 1
        else:
            subpriority = subprio_index
            subprio_index -= 1
        db.set_repo_priority(repo, Priorities(priority, subpriority))


def setup_database(channels: list[str], subdirs: tuple[str, str]) -> Database:
    params = ChannelResolveParams(
        platforms=set(subdirs),
        channel_alias=CondaURL.parse("https://conda.anaconda.org"),
        custom_channels=ChannelResolveParams.ChannelMap({}),
        custom_multichannels=ChannelResolveParams.MultiChannelMap({}),
        home_dir=str(Path.home()),
        current_working_dir=os.getcwd(),
    )
    db = Database(params)

    repos = []
    for channel in channels:
        for subdir in subdirs:
            repos.append(_load_channel(db, channel, subdir))

    # Add virtual packages
    virtual = [
        PackageInfo(name=pkg.name, version=pkg.version, build_string=pkg.build)
        for pkg in Index().system_packages
    ]
    repo = db.add_repo_from_packages(
        packages=virtual,
        name="virtual",
        add_pip_as_python_dependency=PipAsPythonDependency.No,
    )
    repos.append(repo)
    db.set_installed_repo(repo)

    _setup_priorities(db, repos)

    return db


@cache
def setup_context(target_prefix: str | None = None) -> Context:
    ctx = Context(
        ContextOptions(
            enable_signal_handling=False,
            enable_logging=True,
        )
    )
    ctx.prefix_params.conda_prefix = context.conda_prefix
    ctx.prefix_params.root_prefix = context.root_prefix
    ctx.prefix_params.target_prefix = str(
        target_prefix if target_prefix is not None else context.target_prefix
    )
    return ctx


def process_outcome(db: Database, outcome: Solution | UnSolvable) -> list[Record]:
    if isinstance(outcome, UnSolvable):
        raise SolutionNotFound(outcome.explain_problems(db, ProblemsMessageFormat()))
    items = []
    for action in outcome.actions:
        pkg = action.install
        items.append(
            Record(
                name=pkg.name,
                version=pkg.version,
                build=pkg.build_string,
                channel="/".join(pkg.channel.split("/")[:-1]),
                subdir=pkg.platform,
            )
        )
    return items


def solve(specs: list[str], channels: list[str], subdirs: list[str] | None) -> list[Record]:
    db = setup_database(channels, subdirs or [context.subdir, "noarch"])
    request = Request(
        jobs=[Request.Install(LibmambaMatchSpec.parse(spec)) for spec in specs],
        flags=Request.Flags(
            allow_downgrade=False,
            allow_uninstall=True,
            force_reinstall=False,
            keep_dependencies=True,
            keep_user_specs=True,
            order_request=True,
            strict_repo_priority=True,
        ),
    )
    solver = LibsolvSolver()
    outcome = solver.solve(db, request)
    return process_outcome(db, outcome)
