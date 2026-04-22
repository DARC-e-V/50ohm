import src.config as config
import src.latex_slides_build as build

conf = config.Config()

# Build Everything:
bd = build.LatexSlidesBuild(conf)
# bd.build_edition("N")
bd.build_edition("A")
