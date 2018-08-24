from aqt import mw
from aqt.qt import *



from . import passfail

conf = os.path.join(mw.pm.addonFolder(), 'ajatt_suite/reviewmanager/config.json')
defaults = {
    "interval": "60",
    "trigger": True,
    "action": 0,
    "delete_suspended": False,
}

class ReviewManager:

    def __init__(self,mw,menu):
        submenu = menu.addMenu("Review Manager")

        mw.passfail = passfail.PassFail(mw,submenu)


