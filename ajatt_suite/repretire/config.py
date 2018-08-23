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
    "interval": "60",
    "trigger": True,
}



class RepRetire:

    def __init__(self,mw,menu):
        submenu = menu.addMenu("Rep Retire")

        self.config_action = QAction("Configure", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.config)
        submenu.addAction(self.config_action)

        self.run_action = QAction("Run", mw)
        mw.connect(self.run_action, SIGNAL("triggered()"), self.run)
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
        il.addWidget(QLabel("Retire card after intervale (in days):"))
        fl = QHBoxLayout()
        field = QLineEdit()
        field.setText(self.options["interval"])
        fl.addWidget(field)
        il.addLayout(fl)

        trigger = QCheckBox("Trigger Enabled")
        trigger.setChecked(self.options["trigger"])
        fl.addWidget(trigger)
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
            self.options["trigger"] = trigger.isChecked()
            self.save()
            mw.progress.finish()


    def run(self,reviewer=None,answer=None):

        if answer is None or (self.options["trigger"] and answer in [2,3,4]):
            if reviewer != None:
                # perform over just the answered card
                card = reviewer.lastCard()
                if card.ivl > int(self.options["interval"]):
                    mw.col.sched.suspendCards([card.id])
            else:
                # run over all cards
                mw.col.db.execute("update cards set queue = -1 where ivl > ?", self.options["interval"])

