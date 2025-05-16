
import api.config as config
import api.directus as directus
import api.download as download

conf = config.Config()
api  = directus.DirectusAPI(conf)
dl   = download.Download(api)

dl.download_edition("N")
dl.download_question_metadata()
