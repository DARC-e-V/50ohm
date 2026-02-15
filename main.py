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
    input: Annotated[str | None, typer.Option("--input", "-i", help="Content source directory.")] = None,
    output: Annotated[str | None, typer.Option("--output", "-o", help="Destination directory to build to.")] = None,
    render_editions: Annotated[bool, typer.Option(help="Skip building editions.")] = True,
    render_solutions: Annotated[bool, typer.Option(help="Skip building solutions.")] = True,
) -> None:
    conf = config.Config(content_path=input, build_path=output)
    bd = build.Build(conf)

    # Build surrounding website
    bd.build_website()

    if render_editions:
        # Build individual editions
        for e in edition:
            bd.build_edition(e)

    if render_solutions:
        # Build solution pages
        bd.build_solutions()

    # Copy assets to build folder
    bd.build_assets()


if __name__ == "__main__":
    app()
