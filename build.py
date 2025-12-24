import api.directus as directus
import src.build as build
import src.config as config
import src.download as download

conf = config.Config()
api = directus.DirectusAPI(conf.question_base_url, conf.question_access_token)
content_api = directus.DirectusAPI(conf.content_base_url, conf.content_access_token)
dl = download.Download(api, content_api, conf)
bd = build.Build(conf)

# Download the text files:
dl.download_edition("N")
dl.download_edition("E")
dl.download_edition("A")
dl.download_edition("NE")
dl.download_edition("EA")
dl.download_edition("NEA")

# Download additional files:
# dl.download_question_metadata() # (now constant file metadata3b.json)
dl.download_photos()
dl.download_pictures()
dl.download_includes()
dl.download_snippets()
dl.download_content()

# Build Everything:
bd.build_website()
bd.build_edition("N")
bd.build_edition("E")
bd.build_edition("A")
bd.build_edition("NE")
bd.build_edition("EA")
bd.build_edition("NEA")
bd.build_assets()
