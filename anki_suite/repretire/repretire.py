import os

from anki.lang import ngettext
from anki.utils import ids2str
from anki.hooks import wrap
from aqt import mw
from aqt.qt import *
from aqt.reviewer import Reviewer
from aqt.utils import tooltip


from .. import config as cfg


path = os.path.join(mw.pm.addonFolder(), 'anki_suite/repretire/config.json')
defaults = {
    "interval": "65",
    "trigger": True,
    "action": 0,
    "delete_suspended": False,
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

        self.options = cfg.Config(path,defaults)
        self.options.load()

        Reviewer._answerCard = wrap(Reviewer._answerCard, self.run, "after")
        


    def restore(self):
        self.options.reset()
        self.populate_settings()


    def populate_settings(self):
        self.interval.setText(self.options["interval"])
        self.trigger.setChecked(self.options["trigger"])
        self.action.setCurrentIndex(self.options["action"])
        self.delete_suspended.setChecked(self.options["delete_suspended"])

        self.warning_text()


    def warning_text(self):
        if self.action.currentIndex() == 2:
            self.warn.show()
            self.delete_suspended.show()
        else:
            self.warn.hide()
            self.delete_suspended.hide()


    def update_settings(self):
        self.options["interval"]         = self.interval.text()
        self.options["trigger"]          = self.trigger.isChecked()
        self.options["action"]           = self.action.currentIndex()
        self.options["delete_suspended"] = self.delete_suspended.isChecked()



    def config(self):

        self.swin = QDialog(mw)
        layout = QVBoxLayout()
        layout.addWidget(self.create_layout())
        self.swin.setLayout(layout)

        self.options.load()
        self.populate_settings()

        if self.swin.exec_():
            mw.progress.start(immediate=True)
            self.update_settings()
            self.options.save()
            mw.progress.finish()



    def create_layout(self):
        hz_group_box = QGroupBox("Rep Retire Configuration")
        layout = QGridLayout()


        self.interval = QLineEdit()
        self.trigger = QCheckBox("Enable Trigger")

        self.defaults = QPushButton("Restore Defaults")
        self.defaults.clicked.connect(self.restore)
        self.savebtn = QPushButton("Save")
        self.savebtn.connect(self.savebtn, SIGNAL("clicked()"), self.swin, SLOT("accept()"))
        self.cancel = QPushButton("Cancel")
        self.cancel.connect(self.cancel, SIGNAL("clicked()"), self.swin, SLOT("reject()"))

        self.action = QComboBox()
        self.action.addItems([
            "Suspend and Tag (recommended)",
            "Tag Only",
            "Delete Card"
        ])
        self.action.currentIndexChanged.connect(self.warning_text)

        self.warn = QLabel("Warning: Card deletion cannot be undone")
        self.warn.setStyleSheet('color: red; font-weight: bold;')

        self.delete_suspended = QCheckBox("Delete Suspended")

        # row 0
        layout.addWidget(QLabel("Retire card after interval (in days):"), 0, 0, 1, 12)


        # row 1
        layout.addWidget(self.interval, 1, 0, 1, 9)
        layout.addWidget(self.trigger, 1, 9, 1, 3)


        # row 2
        layout.addWidget(QLabel(""), 2, 0, 1, 12)


        # row 3
        layout.addWidget(QLabel("Action to take on retiring card:"), 3, 0, 1, 12)


        # row 4
        layout.addWidget(self.action,4,0,1,12)


        # row 5
        layout.addWidget(self.warn,5,0,1,6)
        layout.addWidget(self.delete_suspended,5,7,1,6)


        # row 6
        layout.addWidget(QLabel(""), 6, 0, 1, 12)        


        # row ?
        layout.addWidget(self.defaults, 7, 0, 1, 1)
        layout.addWidget(self.cancel, 7, 8, 1, 2)
        layout.addWidget(self.savebtn, 7, 10, 1, 2)


        hz_group_box.setLayout(layout)
        return hz_group_box



    def run(self,reviewer=None,answer=None):

        if answer is None or (self.options["trigger"] and answer in [2,3,4]):
            if reviewer != None:
                # perform over just the answered card
                card = reviewer.lastCard()
                if card.ivl > int(self.options["interval"]):
                    ids = [card.id]
                    nids = [card.nid]
                else:
                    ids = []
                    nids = []
                    message = None
            else:
                # run over all cards, greater than threshold, not suspended already
                ids_and_nids = mw.col.db.all("select id,nid from cards where queue != -1 and ivl >= ?", self.options["interval"])
                ids = [i[0] for i in ids_and_nids]
                nids = [i[1] for i in ids_and_nids]


            if self.options["action"] == 0:
                self.tag(nids)
                if self.suspend(nids):
                    tooltip(ngettext("Retired %d Card", "Retired %d Cards", len(ids)) % len(ids))


            elif self.options["action"] == 1:
                if self.tag(nids):
                    tooltip(ngettext("Retired %d Card", "Retired %d Cards", len(ids)) % len(ids))


            elif self.options["action"] == 2:
                if self.options["delete_suspended"]:
                    ids.extend(i[0] for i in mw.col.db.all("select id from cards where queue = -1 and ivl >= ?", self.options["interval"]))
                if self.delete(ids):
                    tooltip(ngettext("Deleted %d Card", "Deleted %d Cards", len(ids)) % len(ids))



    def suspend(self, ids):
        if ids is None or len(ids) <= 0:
            return False

        mw.col.db.execute("update cards set queue = -1 where nid in %s" % ids2str(ids))
        return True



    def tag(self, nids):
        if nids is None or len(nids) <= 0:
            return False
       
        mw.col.tags.bulkAdd(nids, _("retired"))
        return True
      


    def delete(self,ids):
        if ids is None or len(ids) <= 0:        
            return False

        mw.col.remCards(ids)
        return True
