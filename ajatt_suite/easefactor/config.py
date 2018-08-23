from aqt import mw
from aqt.qt import *


class EaseFactor:

    def __init__(self,mw,menu):
        submenu = menu.addMenu("Ease Factor")

        self.config_action = QAction("Configure", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.setup)
        submenu.addAction(self.config_action)

        self.run_action = QAction("Run", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.run)
        submenu.addAction(self.run_action)


    def setup(self):
        pass


    def run(self):
        pass
