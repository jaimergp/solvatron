import json
import subprocess

from .common import Record, SolutionNotFound


def solve(specs: list[str], channels: list[str], subdirs: list[str]) -> list[Record]:
    if subdirs:
        platform = (f"--platform={next(s for s in subdirs if s != 'noarch')}",)
    else:
        platform = ()
    p = subprocess.run(
        [
            "mamba",
            "create",
            "--dry-run",
            "--prefix=UNUSED",
            "--json",
            "--override-channels",
            *([f"--channel={c}" for c in channels]),
            *platform,
            *specs,
        ],
        capture_output=True,
        text=True,
    )
    data = json.loads(p.stdout)
    if p.returncode:
        raise SolutionNotFound("\n".join(data["solver_problems"]))
    items = []
    for r in data["actions"]["LINK"]:
        if not r:
            continue
        items.append(
            Record(
                name=r["name"],
                version=r["version"],
                build=r["build_string"],
                channel=r["channel"],
                subdir=r["subdir"],
            )
        )
    return items
