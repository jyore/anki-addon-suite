from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo



from .. import config as cfg


path = os.path.join(mw.pm.addonFolder(), 'anki_suite/reviewmanager/easeassistant_config.json')
defaults = {
    "ease_factor": 250,
}



class EaseAssistant:

    def __init__(self,mw,menu):
        submenu = menu.addMenu("Ease Assistant")


        self.config_action = QAction("Configure", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.config)
        submenu.addAction(self.config_action)


        self.reset_action = QAction("Reset Ease Factor", mw)
        mw.connect(self.reset_action, SIGNAL("triggered()"), self.reset_ease)        
        submenu.addAction(self.reset_action)


        self.options = cfg.Config(path,defaults)
        self.options.load()



    def restore(self):
        self.options.reset()
        self.populate_settings()


    def populate_settings(self):
        self.easefactor.setText(str(self.options["ease_factor"]))


    def update_settings(self):
        self.options["ease_factor"] = int(self.easefactor.text())


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
        hz_group_box = QGroupBox("Ease Factor Settings")
        layout = QGridLayout()


        self.easefactor = QLineEdit()


        self.defaults = QPushButton("Restore Defaults")
        self.defaults.clicked.connect(self.restore)
        self.savebtn = QPushButton("Save")
        self.savebtn.connect(self.savebtn, SIGNAL("clicked()"), self.swin, SLOT("accept()"))
        self.cancel = QPushButton("Cancel")
        self.cancel.connect(self.cancel, SIGNAL("clicked()"), self.swin, SLOT("reject()"))


        # row 0
        layout.addWidget(QLabel("Ease Factor:"), 0, 0, 1, 12)


        # row 1
        layout.addWidget(self.easefactor, 1, 0, 1, 12)


        # row 6
        layout.addWidget(QLabel(""), 2, 0, 1, 12)  


        # row ?
        layout.addWidget(self.defaults, 3, 0, 1, 1)
        layout.addWidget(self.cancel, 3, 8, 1, 2)
        layout.addWidget(self.savebtn, 3, 10, 1, 2)

        hz_group_box.setLayout(layout)
        return hz_group_box
        


    def reset_ease(self):
        mw.col.db.execute("update cards set factor = ?", int(float(self.options["ease_factor"])*10))
        showInfo("Ease has been reset to %s%%" % self.options["ease_factor"])

