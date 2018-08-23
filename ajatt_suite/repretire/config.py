import json,os
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo,tooltip
from anki.lang import ngettext
from anki.utils import ids2str



conf = os.path.join(mw.pm.addonFolder(), 'ajatt_suite/repretire/config.json')
defaults = {
    "interval": "60",
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

        self.load()        


    def restore(self):
        self.options.update(defaults)
        self.populate_settings()

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

        self.load()
        self.populate_settings()

        if self.swin.exec_():
            mw.progress.start(immediate=True)
            self.update_settings()
            self.save()
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


            retired_card = False
            if self.options["action"] == 0:
                retired_card = self.suspend(nids)

            if self.options["action"] in [0,1]:
                retired_card = self.tag(nids)

            if self.options["action"] == 2:
                if self.options["delete_suspended"]:
                    ids.extend(i[0] for i in mw.col.db.all("select id from cards where queue = -1 and ivl >= ?", self.options["interval"]))

                retired_card = self.delete(ids)

            if retired_card:
                self.generate_tooltip(len(ids))



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



    def generate_tooltip(self,length):
        if length == 1:
            tooltip("Retired Card")
        elif length > 1:
            tooltip("Retired %d Cards" % length)
