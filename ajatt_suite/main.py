from aqt import mw
from aqt.qt import *


from .repretire import repretire
from .reviewmanager import config as revconf
from .kanjigrid import config as kanjiconf

mw.form.menuTools.addSeparator()
menu = mw.form.menuTools.addMenu("AJATT Tool Suite")
mw.form.menuTools.addSeparator()


mw.revconf = revconf.ReviewManager(mw,menu)
mw.repretire = repretire.RepRetire(mw,menu)

kanjiconf.KanjiGrid(mw,menu)
