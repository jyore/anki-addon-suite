from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.hooks import addHook


# need?
from anki.js import jquery
from aqt.webview import AnkiWebView
from anki.utils import ids2str


import json,os

conf = os.path.join(mw.pm.addonFolder(), 'ajatt_suite/repretire/config.json')
defaults = {
    "interval": 60
}



class RepRetire:

    def __init__(self,mw,menu):
        submenu = menu.addMenu("Rep Retire")

        self.config_action = QAction("Configure", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.config)
        submenu.addAction(self.config_action)

        self.run_action = QAction("Run", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.run)
        submenu.addAction(self.run_action)

        self.load()


    def save(self):
        with open(conf,'w') as f:
            f.write(json.dumps(self.options))


    def load(self):
        self.options = defaults.copy()

        with open(conf,'r') as f:
            try:
                self.options.update(json.load(f))
            except Exception as e:
                pass


    def config(self):

        swin = QDialog(mw)
        vl   = QVBoxLayout()
        frm  = QGroupBox("Configre")
        vl.addWidget(frm)

        il = QVBoxLayout()
        il.addWidget(QLabel("Retire card after interval excedes:"))
        fl = QHBoxLayout()
        field = QLineEdit()
        field.setText(self.options["interval"])
        fl.addWidget(field)
        il.addLayout(fl)


        hl = QHBoxLayout()
        save = QPushButton("Save")
        save.connect(save, SIGNAL("clicked()"), swin, SLOT("accept()"))
        cancel = QPushButton("Cancel")
        cancel.connect(cancel, SIGNAL("clicked()"), swin, SLOT("reject()"))
        hl.addWidget(cancel)
        hl.addWidget(save)
        vl.addLayout(hl)

        frm.setLayout(il)
        swin.setLayout(vl)
        swin.resize(500, 400)


        if swin.exec_():
            mw.progress.start(immediate=True)
            self.options["interval"] = field.text()
            self.save()
            mw.progress.finish()



    def run(self):
        pass


## set this to the interval value in days to search for
##deathpoint = 150
##
##def get_cards_to_kill():
##    showInfo("\n".join(["%s" % i for i in mw.col.db.list("select id from cards where ivl > %s" % deathpoint)]))
##    
##
##action = QAction("DEATHPOINT", mw)
##action.triggered.connect(get_cards_to_kill)
##mw.form.menuTools.addAction(action)
#
#if __name__ != "__main__":
#    # Save a reference to the toolkit onto the mw, preventing garbage collection of PyQT objects
#    if mw: mw.deathpoint = DeathPoint(mw)
            #self.options.update(json.load(f))
