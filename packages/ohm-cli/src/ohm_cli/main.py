from typing import Annotated

import ohm_builder.config as config
import typer
from ohm_builder.builder import build_zip as build_zip_archive
from ohm_builder.builder import progress_display
from ohm_builder.edition import Edition
from ohm_builder.output_format import BUILDERS, OutputFormat

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
    format: Annotated[
        list[OutputFormat],
        typer.Option("--format", "-f", help="Output format to build, can be specified multiple times."),
    ] = [OutputFormat.html],  # noqa: B006 -- default value is required for typer
    input: Annotated[str | None, typer.Option("--input", "-i", help="Content source directory.")] = None,
    output: Annotated[str | None, typer.Option("--output", "-o", help="Destination directory to build to.")] = None,
    render_editions: Annotated[bool, typer.Option(help="Skip building editions.")] = True,
    render_solutions: Annotated[bool, typer.Option(help="Skip building solutions.")] = True,
    build_zip: Annotated[bool, typer.Option(help="Whether to build a zip file of the output.")] = False,
) -> None:
    conf = config.Config(content_path=input, build_path=output)

    # A format that does not support a step implements it as a no-op, so the sequence of steps is
    # the same for every format.
    for output_format in format:
        bd = BUILDERS[output_format](conf)

        # Build surrounding website
        bd.build_website()

        if render_editions:
            # Build individual editions, sharing one progress display across all of them
            with progress_display() as progress:
                for e in edition:
                    bd.build_edition(e, progress)

        if render_solutions:
            # Build solution pages
            bd.build_solutions()

        # Copy assets to build folder
        bd.build_assets()
        bd.build_question_index()
        bd.build_index()

    if build_zip:
        # Build zip file of the whole output, regardless of how many formats went into it
        build_zip_archive(conf)


if __name__ == "__main__":
    app()
