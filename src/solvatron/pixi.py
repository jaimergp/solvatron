import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent

from .common import Record, SolutionNotFound

from rattler import Platform


def solve(specs: list[str], channels: list[str], subdirs: list[str]) -> list[Record]:
    if subdirs:
        platform = [next(s for s in subdirs if s != "noarch")]
    else:
        platform = [str(Platform.current())]

    with TemporaryDirectory(delete=False) as tmp:
        Path(tmp, "pixi.toml").write_text(
            dedent(
                f"""
                [workspace]
                authors = []
                channels = {channels}
                name = "UNUSED"
                platforms = {platform}
                version = "0.1.0"

                [tasks]

                [dependencies]
                """
            )
        )
        input_file = Path(tmp, "input.yml")
        input_file.write_text(
            dedent(
                f"""
                name: default
                channels: {channels}
                platforms: {platform}
                dependencies: {specs}
                """
            )
        )
        subprocess.check_output(
            [
                "pixi",
                "import",
                "--format",
                "conda-env",
                input_file,
                "--manifest-path",
                tmp,
            ],
            stderr=subprocess.PIPE,
        )
    p = subprocess.run(
        [
            "pixi",
            "lock",
            "--json",
            "--manifest-path",
            tmp,
        ],
        capture_output=True,
        text=True,
    )
    if p.returncode:
        raise SolutionNotFound(p.stderr)
    data = json.loads(p.stdout)
    items = []
    for r in data["environment"]["default"][platform[0]]:
        url = r["after"]["conda"]
        channel, subdir, fn = url.rsplit("/", 2)
        channel = channel.replace("https://conda.anaconda.org/", "")
        for ext in ".conda", ".tar.bz2":
            if fn.endswith(ext):
                fn = fn[: -len(ext)]
                break
        name, version, build = fn.rsplit("-", 2)
        items.append(
            Record(
                name=name,
                version=version,
                build=build,
                channel=channel,
                subdir=subdir,
            )
        )
    return items
