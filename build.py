
import api.config as config
import api.directus as directus
import api.download as download

conf = config.Config()
api  = directus.DirectusAPI(conf)
dl   = download.Download(api)

# Download the text files:
dl.download_edition("N")

# Download additional files:
dl.download_question_metadata()
dl.download_photos()
dl.download_pictures()
