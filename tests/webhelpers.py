# ------------------------------------------------------------------------------
# Tools to help with unittesting Coffee/web
# ------------------------------------------------------------------------------

from pathlib import Path
RootDir = Path(__file__).resolve().parents[1]
PhantomJSBin = str(RootDir / "node_modules/phantomjs/lib/phantom/bin/phantomjs")
