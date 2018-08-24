# -*- mode: Python ; coding: utf-8 -*-
from __future__ import unicode_literals

import json,os

from anki.hooks import wrap
from aqt import mw
from aqt.qt import *
from aqt.reviewer import Reviewer
from aqt.utils import showInfo,tooltip


from .. import config as cfg


path = os.path.join(mw.pm.addonFolder(), 'ajatt_suite/reviewmanager/passfail_config.json')
defaults = {
     "enabled": True
}
config = cfg.Config(path,defaults)
config.load()

default_map = {
  2: [None,1,2,2,2],
  3: [None,1,2,3,2],
  4: [None,1,2,3,4],
}

remap = {
  2: [None, 1, 2, 2, 2],
  3: [None, 1, 2, 2, 2],
  4: [None, 1, 3, 3, 3],
}

buttons = [
  '<b style="color:#c33">外れ</b>',
  '<b style="color:#3c3">当たり</b>'
]

full_width = '99%'
half_width = '48%'

show_answer_html = """
<div class="stat2" align="center" style="margin-top:2px;width:%s"><span class="stattxt">%s</span><br><button %s id="ansbut" style="display:inline-block;width:%s;%s" onclick="py.link('ans');">%s</button></div>
"""


def pass_fail_answer_card(obj, ease, _old=None):
    count = mw.col.sched.answerButtons(mw.reviewer.card)

    if config["enabled"]:
        try:
            ease = remap[count][ease]
        except (KeyError, IndexError):
            pass
    original(obj,ease)

original = Reviewer._answerCard


class PassFail:

    def __init__(self,mw,menu):
        sumbenu = menu.addMenu("PassFail")

        self.config_action = QAction("Configure", mw)
        mw.connect(self.config_action, SIGNAL("triggered()"), self.config)
        sumbenu.addAction(self.config_action)

        self.options = config
        self.options.load()

        Reviewer._showAnswerButton = wrap(Reviewer._showAnswerButton, self.show_answer_button, 'after')
        Reviewer._answerButtons = wrap(Reviewer._answerButtons, self.answer_buttons, 'after')
        Reviewer._answerCard = pass_fail_answer_card


    def restore(self):
        self.options.reset()
        self.populate_settings()


    def populate_settings(self):
        self.enabled.setChecked(self.options["enabled"])


    def update_settings(self):
        self.options["enabled"] = self.enabled.isChecked()


    def config(self):
        
        self.swin = QDialog(mw)
        layout = QVBoxLayout()
        layout.addWidget(self.create_layout())
        self.swin.setLayout(layout)

        config.load()
        self.populate_settings()

        if self.swin.exec_():
            mw.progress.start(immediate=True)
            self.update_settings()
            self.options.save()
            mw.progress.finish()
            


    def create_layout(self):
        hz_group_box = QGroupBox("Review Manager | PassFail Configuration")
        layout = QGridLayout()

        self.enabled = QCheckBox("Enabled")

        self.defaults = QPushButton("Restore Defaults")
        self.defaults.clicked.connect(self.restore)
        self.savebtn = QPushButton("Save")
        self.savebtn.connect(self.savebtn, SIGNAL("clicked()"), self.swin, SLOT("accept()"))
        self.cancel = QPushButton("Cancel")
        self.cancel.connect(self.cancel, SIGNAL("clicked()"), self.swin, SLOT("reject()"))


        # row 0
        layout.addWidget(self.enabled, 0, 0, 1, 12)


        # row 1
        layout.addWidget(QLabel(""), 1, 0, 1, 12)


        # row 2
        layout.addWidget(self.defaults, 2, 0, 1, 1)
        layout.addWidget(self.cancel, 2, 8, 1, 2)
        layout.addWidget(self.savebtn, 2, 10, 1, 2)


        hz_group_box.setLayout(layout)
        return hz_group_box



    def answer_buttons(self, obj, _old=None):
        default = obj._defaultEase()

        def btn(i, label, width):
            if i == default:
                extra = 'id="default"'
            else:
                extra = ''
            due = obj._buttonTime(i)
            return '''<td align="center" style="width:%s">%s<button %s %s onclick='py.link("ease%d");'>%s</button></td>''' % (
                width,
                due,
                extra,
                ' title="Shortcut Key: %d" ' % i,
                i,
                label
            )

        def def_btn(i, label):
            if i == default:
                extra = "id=default"
            else:
                extra = ""
            due = obj._buttonTime(i)
            return '''
<td align=center>%s<button %s title="%s" onclick='py.link("ease%d");'>\
%s</button></td>''' % (due, extra, _("Shortcut key: %s") % i, i, label)

        buf = '<table cellpadding="0" cellspacing="0" %s><tr>' % ('width="100%"' if self.options['enabled'] else "")
        if self.options["enabled"]:    
            for ease, label, width in self.answer_buttons_list(obj):
                buf = "%s%s" % (buf,btn(ease, label, width))

            style = "table tr td button { width:100%; }"
        else:
            for ease, label in obj._answerButtonList():
                buf = "%s%s" % (buf,def_btn(ease, label))
            style = ""

        return "%s%s" % (buf, '''</tr></table><style>%s</style><script>$(function () { $('#default').focus(); });</script>''' % style)




    def show_answer_button(self, obj, _old=None):
        if self.options["enabled"]:
            obj._bottomReady = True
            if not obj.typeCorrect:
                obj.bottom.web.setFocus()
            btn = show_answer_html % (
                full_width,
                obj._remaining(),
                ' title="%s: %s" ' % (_('Shortcut key'), _('Space')),
                full_width,
                'color:black',
                _('Show Answer')
            )

            mt = (obj.card.timeLimit()/1000) if obj.card.shouldShowTimer() else 0
            obj.bottom.web.eval('showQuestion(%s,%d);' % (json.dumps(btn), mt))
            return True


    def answer_buttons_list(self,obj,_old=None):
        again = ((1, '<span>%s</span>' % buttons[0],half_width),)

        cnt = obj.mw.col.sched.answerButtons(obj.card)
        if cnt in [2,3]:
            return again + ((2, '<span>%s</span>' % buttons[1], half_width),)
        elif cnt == 4:
            return again + ((3, '<span>%s</span>' % buttons[1], half_width),)

