import api.directus as directus
import src.build as build
import src.config as config
import src.download as download

conf = config.Config()
content_api = directus.DirectusAPI(conf.content_base_url, conf.content_access_token)
dl = download.Download(content_api, conf)

# Download the content files:
dl.download_git_content()

# Download additional files:
dl.download_snippets()
dl.download_content()

## Build Everything:
bd = build.Build(conf)
# bd.build_website()
# bd.build_edition("N")
# bd.build_edition("E")
# bd.build_edition("A")
# bd.build_edition("NE")
# bd.build_edition("EA")
# bd.build_edition("NEA")
# bd.build_assets()
