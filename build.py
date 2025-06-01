import api.directus as directus
import src.build as build
import src.config as config
import src.download as download

conf = config.Config()
api = directus.DirectusAPI(conf)
dl = download.Download(api, conf)
bd = build.Build()

# Download the text files:
dl.download_edition("N")

# Download additional files:
dl.download_question_metadata()
dl.download_pictures()
dl.download_photos()
dl.download_includes()

# Build edition:
bd.build_edition("N")

# Build assets:
bd.build_assets()
