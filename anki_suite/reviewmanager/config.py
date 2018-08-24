from aqt import mw
from aqt.qt import *



from . import passfail,easeassistant



class ReviewManager:

    def __init__(self,mw,menu):
        submenu = menu.addMenu("Review Manager")

        mw.passfail = passfail.PassFail(mw,submenu)
        mw.easeassistant = easeassistant.EaseAssistant(mw,submenu)


