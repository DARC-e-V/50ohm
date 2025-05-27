import api.directus as directus
import src.build as build
import src.config as config
import src.download as download

conf = config.Config()
api = directus.DirectusAPI(conf.question_base_url, conf.question_access_token)
content_api = directus.DirectusAPI(conf.content_base_url, conf.content_access_token)
dl = download.Download(api, content_api, conf)
bd = build.Build()

# Download the text files:
dl.download_edition("N")

# Download additional files:
dl.download_question_metadata()
dl.download_pictures()
dl.download_photos()
dl.download_snippets()
dl.download_content()

# Build Everything:
bd.build_website()
bd.build_edition("N")
bd.build_assets()
