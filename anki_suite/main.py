from aqt import mw
from aqt.qt import *


from .repretire import repretire
from .reviewmanager import easeassistant,passfail

mw.form.menuTools.addSeparator()
menu = mw.form.menuTools.addMenu("Anki Tool Suite")
mw.form.menuTools.addSeparator()


mw.easeassistant = easeassistant.EaseAssistant(mw,menu)
mw.passfail = passfail.PassFail(mw,menu)
mw.repretire = repretire.RepRetire(mw,menu)

