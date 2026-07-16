import src.build as build
import src.config as config

conf = config.Config()

# Build Everything:
bd = build.Build(conf)
bd.build_website()
bd.build_edition("P")
bd.build_edition("A")
bd.build_assets()
bd.build_solutions()
bd.build_question_index()
bd.build_index()
bd.build_zip()
