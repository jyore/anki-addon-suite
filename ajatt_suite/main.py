from aqt import mw
from aqt.qt import *

from .repretire import config as repconf
from .easefactor import config as easeconf
from .kanjigrid import config as kanjiconf

menu = mw.form.menuTools.addMenu("AJATT Tool Suite")
repconf.RepRetire(mw,menu)
easeconf.EaseFactor(mw,menu)
kanjiconf.KanjiGrid(mw,menu)
