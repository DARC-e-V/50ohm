import sys

import mistletoe
from fifty_ohm_html_renderer import FiftyOhmHtmlRenderer

if __name__ == "__main__":
    with open(sys.argv[1]) as fin, open(sys.argv[2], "w") as fout:
        fout.write(mistletoe.markdown(fin, FiftyOhmHtmlRenderer))
