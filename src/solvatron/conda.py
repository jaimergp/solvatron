import json
import sys
import subprocess

from .common import Record, SolutionNotFound


def solve(specs: list[str], channels: list[str], subdirs: list[str], solver: str) -> list[Record]:
    if subdirs:
        platform = (f"--platform={next(s for s in subdirs if s != 'noarch')}",)
    else:
        platform = ()
    p = subprocess.run(
        [
            sys.executable,
            "-m",
            "conda",
            "create",
            "--dry-run",
            "--json",
            f"--solver={solver}",
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
        raise SolutionNotFound(data["message"])
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
                subdir=r["platform"],
            )
        )
    return items
