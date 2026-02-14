from typing import Annotated

import typer

import src.build as build
import src.config as config
from src.edition import Edition

app = typer.Typer()


@app.command()
def main(
    edition: Annotated[list[Edition], typer.Option(help="Edition to build, can be specified multiple times.")] = [  # noqa: B006 -- default value is required for typer
        Edition.n,
        Edition.e,
        Edition.a,
        Edition.ne,
        Edition.ea,
        Edition.nea,
    ],
    source: Annotated[str | None, typer.Option(help="Content source directory.")] = None,
    destination: Annotated[str | None, typer.Option(help="Destination directory to build to.")] = None,
) -> None:
    conf = config.Config(content_path=source, build_path=destination)
    bd = build.Build(conf)

    # Build surrounding website
    bd.build_website()
    # Build individual editions
    for e in edition:
        bd.build_edition(e)
    # Copy assets to build folder
    bd.build_assets()


if __name__ == "__main__":
    app()
