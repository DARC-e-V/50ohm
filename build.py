import src.build as build
import src.config as config

conf = config.Config()

# Build Everything:
bd = build.Build(conf)
bd.build_website()
bd.build_edition("N")
bd.build_edition("E")
bd.build_edition("A")
bd.build_edition("NE")
bd.build_edition("EA")
bd.build_edition("NEA")
bd.build_assets()
bd.build_solutions()
