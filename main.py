from typing import Annotated

import typer

import api.directus as directus
import src.build as build
import src.config as config
import src.download as download
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
    skip_download_editions: Annotated[
        bool, typer.Option(help="Skip download for editions, will use cached files or fail.")
    ] = False,
    skip_download_assets: Annotated[
        bool, typer.Option(help="Skip download for assets, will use cached assets or paceholders.")
    ] = False,
) -> None:
    conf = config.Config()
    api = directus.DirectusAPI(conf.question_base_url, conf.question_access_token)
    content_api = directus.DirectusAPI(conf.content_base_url, conf.content_access_token)
    dl = download.Download(api, content_api, conf)
    bd = build.Build(conf)

    if not skip_download_editions:
        # Download the text files
        for e in edition:
            dl.download_edition(e)

    if not skip_download_assets:
        # Download additional files
        # dl.download_question_metadata() # (now constant file metadata3b.json)
        dl.download_photos()
        dl.download_pictures()
        dl.download_includes()
        dl.download_snippets()
        dl.download_content()

    # Build surrounding website
    bd.build_website()
    # Build individual editions
    for e in edition:
        bd.build_edition(e)
    # Copy assets to build folder
    bd.build_assets()


if __name__ == "__main__":
    app()
