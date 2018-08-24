from aqt import mw
from aqt.qt import *


from .repretire import repretire
from .reviewmanager import config as revconf

mw.form.menuTools.addSeparator()
menu = mw.form.menuTools.addMenu("Anki Tool Suite")
mw.form.menuTools.addSeparator()


mw.revconf = revconf.ReviewManager(mw,menu)
mw.repretire = repretire.RepRetire(mw,menu)
