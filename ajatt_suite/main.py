from aqt import mw
from aqt.qt import *
from aqt.reviewer import Reviewer
from anki.hooks import wrap

from .repretire import config as repconf
from .easefactor import config as easeconf
from .kanjigrid import config as kanjiconf

mw.form.menuTools.addSeparator()
menu = mw.form.menuTools.addMenu("AJATT Tool Suite")
mw.form.menuTools.addSeparator()


mw.repretire = repconf.RepRetire(mw,menu)
Reviewer._answerCard = wrap(Reviewer._answerCard, mw.repretire.run, "after")

easeconf.EaseFactor(mw,menu)
kanjiconf.KanjiGrid(mw,menu)
