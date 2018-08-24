# -*- coding: utf-8 -*-
from __future__ import division
import time, random


from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from heapq import heappush
from anki.sched import Scheduler
from anki.utils import ids2str, intTime, fmtTimeSpan


from .. import config as cfg


path = os.path.join(mw.pm.addonFolder(), 'anki_suite/reviewmanager/easeassistant_config.json')
defaults = {
    "ease_factor": 250,
    "enabled": True,
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

        self.originals = {
            "rescheduleLapse": Scheduler._rescheduleLapse,
            "rescheduleRev":   Scheduler._rescheduleRev,
            "nextRevIvl":      Scheduler._nextRevIvl,
            "nextLapseIvl":    Scheduler._nextLapseIvl,
            "dynIvlBoost":     Scheduler._dynIvlBoost,
            "reschedCards":    Scheduler.reschedCards,
            "forgetCards":     Scheduler.forgetCards
        }



    def set_implementations(self):
        if self.options["enabled"]:
            Scheduler._rescheduleLapse = newRescheduleLapse
            Scheduler._rescheduleRev   = newRescheduleRev
            Scheduler._nextRevIvl      = nextRevIvl
            Scheduler._nextLapseIvl    = nextLapseIvl
            Scheduler._dynIvlBoost     = dynIvlBoost
            Scheduler.reschedCards     = newreschedCards
            Scheduler.forgetCards      = newforgetCards
        else:
            Scheduler._rescheduleLapse = self.originals["rescheduleLapse"]
            Scheduler._rescheduleRev   = self.originals["rescheduleRev"]
            Scheduler._nextRevIvl      = self.originals["nextRevIvl"]
            Scheduler._nextLapseIvl    = self.originals["nextLapseIvl"]
            Scheduler._dynIvlBoost     = self.originals["dynIvlBoost"]
            Scheduler.reschedCards     = self.originals["reschedCards"]
            Scheduler.forgetCards      = self.originals["forgetCards"]


    def restore(self):
        self.options.reset()
        self.populate_settings()


    def populate_settings(self):
        self.easefactor.setText(str(self.options["ease_factor"]))
        self.enabled.setChecked(self.options["enabled"])
        self.set_implementations()


    def update_settings(self):
        self.options["ease_factor"] = int(self.easefactor.text())
        self.options["enabled"] = self.enabled.isChecked()
        self.set_implementations()


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
        self.enabled    = QCheckBox("Enabled")

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


        # row 2
        layout.addWidget(QLabel(""), 2, 0, 1, 12)  


        # row 3
        layout.addWidget(QLabel("Low Stakes Anki (No Penalties or Boosting)"), 3, 0, 1, 12) 


        # row 4
        layout.addWidget(self.enabled, 4, 0, 1, 12)


        # row 5
        layout.addWidget(QLabel(""), 5, 0, 1, 12)  


        # row ?
        layout.addWidget(self.defaults, 6, 0, 1, 1)
        layout.addWidget(self.cancel, 6, 8, 1, 2)
        layout.addWidget(self.savebtn, 6, 10, 1, 2)

        hz_group_box.setLayout(layout)
        return hz_group_box
        


    def reset_ease(self):
        mw.col.db.execute("update cards set factor = ?", int(float(self.options["ease_factor"])*10))
        showInfo("Ease has been reset to %s%%" % self.options["ease_factor"])



# below taken from the: Low Stakes Anki No Penalties or Boosting New Interval Retained add-on

'''In the nextLapseIvl function below, I have now added my modification of Dmitry Mikheev's modification of Luminous Spice's <a href="https://ankiweb.net/shared/info/1481634779" rel="nofollow">Another Retreat</a> add-on. :) - This add-on actually manages to replicate the failed card handling that happens to be used in a research model by Xiong, Wang, and Beck. It resets the lapsed card interval to the previous successful interval. To use it, comment out line 117 and remove the triple quotes from lines 118 and 122.'''


def _answerLrnCard(self, card, ease): #commented out line 44 so that the interval for lapsed cards is unaffected
        # ease 1=no, 2=yes, 3=remove
        conf = self._lrnConf(card)
        if card.odid and not card.wasNew:
            type = 3
        elif card.type == 2:
            type = 2
        else:
            type = 0
        leaving = False
        # lrnCount was decremented once when card was fetched
        lastLeft = card.left
        # immediate graduate?
        if ease == 3:
            self._rescheduleAsRev(card, conf, True)
            leaving = True
        # graduation time?
        elif ease == 2 and (card.left%1000)-1 <= 0:
            self._rescheduleAsRev(card, conf, False)
            leaving = True
        else:
            # one step towards graduation
            if ease == 2:
                # decrement real left count and recalculate left today
                left = (card.left % 1000) - 1
                card.left = self._leftToday(conf['delays'], left)*1000 + left
            # failed
            else:
                card.left = self._startingLeft(card)
                resched = self._resched(card)
                if 'mult' in conf and resched:
                    # review that's lapsed
                    #card.ivl = max(1, conf['minInt'], card.ivl*conf['mult'])
					pass
					#card.ivl = nextLapseIvl(self, card, conf)
                else:
                    # new card; no ivl adjustment
                    pass
                if resched and card.odid:
                    card.odue = self.today + 1
            delay = self._delayForGrade(conf, card.left)
            if card.due < time.time():
                # not collapsed; add some randomness
                delay *= random.uniform(1, 1.25)
            card.due = int(time.time() + delay)
            # due today?
            if card.due < self.dayCutoff:
                self.lrnCount += card.left // 1000
                # if the queue is not empty and there's nothing else to do, make
                # sure we don't put it at the head of the queue and end up showing
                # it twice in a row
                card.queue = 1
                if self._lrnQueue and not self.revCount and not self.newCount:
                    smallestDue = self._lrnQueue[0][0]
                    card.due = max(card.due, smallestDue+1)
                heappush(self._lrnQueue, (card.due, card.id))
            else:
                # the card is due in one or more days, so we need to use the
                # day learn queue
                ahead = ((card.due - self.dayCutoff) // 86400) + 1
                card.due = self.today + ahead
                card.queue = 3
        self._logLrn(card, ease, conf, leaving, type, lastLeft)

	
def newRescheduleLapse(self, card): # no ease penalty, simply commented out line 16
	conf = self._lapseConf(card)
	card.lastIvl = card.ivl
	if self._resched(card):
		card.lapses += 1
		card.ivl = self._nextLapseIvl(card, conf)
		  # card.factor = max(1300, card.factor-200)
		card.due = self.today + card.ivl
		# if it's a filtered deck, update odue as well
		if card.odid:
			card.odue = card.due
	# if suspended as a leech, nothing to do
	delay = 0
	if self._checkLeech(card, conf) and card.queue == -1:
		return delay
	# if no relearning steps, nothing to do
	if not conf['delays']:
		return delay
	# record rev due date for later
	if not card.odue:
		card.odue = card.due
	delay = self._delayForGrade(conf, 0)
	card.due = int(delay + time.time())
	card.left = self._startingLeft(card)
	# queue 1
	if card.due < self.dayCutoff:
		self.lrnCount += card.left // 1000
		card.queue = 1
		heappush(self._lrnQueue, (card.due, card.id))
	else:
		# day learn queue
		ahead = ((card.due - self.dayCutoff) // 86400) + 1
		card.due = self.today + ahead
		card.queue = 3
	return delay
	
def nextLapseIvl(self, card, conf): # multiplier not honored, therefore card interval not reset or decreased - commented out and replaced line - to undo, just comment out line 48 and uncomment line 48
    #return max(conf['minInt'], int(card.ivl*conf['mult']))
    return max(conf['minInt'], conf['mult']*int(card.ivl))
    '''lastIvls = self.col.db.list("""select lastivl from revlog where cid = ? and lastivl < ? order by id desc LIMIT 1""", card.id, card.ivl)
    if lastIvls:
        return max( conf['minInt'], lastIvls[0])
    else:
        return max( conf['minInt'], int(card.ivl))'''

def newRescheduleRev(self, card, ease): # no ease boost or hard penalty - commented out line 55 so that card.factor not changed
	# update interval
	card.lastIvl = card.ivl
	if self._resched(card):
		self._updateRevIvl(card, ease)
		  # card.factor = max(1300, card.factor+[-150, 0, 150][ease-2])
		card.due = self.today + card.ivl
	else:
		card.due = card.odue
	if card.odid:
		card.did = card.odid
		card.odid = 0
		card.odue = 0
  
def nextRevIvl(self, card, ease): # only good interval - commented out 69 and 71
	"Ideal next interval for CARD, given EASE."
	delay = self._daysLate(card)
	conf = self._revConf(card)
	fct = card.factor / 1000
	# ivl2 = self._constrainedIvl((card.ivl + delay // 4) * 1.2, conf, card.ivl)
	ivl3 = self._constrainedIvl((card.ivl + delay // 2) * fct, conf, card.ivl) #card.ivl originally ivl2
	# ivl4 = self._constrainedIvl((card.ivl + delay) * fct * conf['ease4'], conf, ivl3)
	if ease == 2:
	    interval = ivl3
	elif ease == 3:
	    interval = ivl3
	elif ease == 4:
	    interval = ivl3
	# interval capped?
	return min(interval, conf['maxIvl'])
    
def dynIvlBoost(self, card): #replaced factor with fct
    assert card.odid and card.type == 2
    assert card.factor
    confL = self._lrnConf(card)
    elapsed = card.ivl - (card.odue - self.today)
    #factor = ((card.factor/1000)+1.2)/2
    fct = card.factor / 1000
    ivl = int(max(card.ivl, elapsed * fct, confL['minInt'])) #should maybe change 1 to minInt
    conf = self._revConf(card)
    return min(conf['maxIvl'], ivl)    

def newreschedCards(self, ids, imin, imax):
    "Put cards in review queue with a new interval in days (min, max)."
    d = []
    t = self.today
    mod = intTime()
    for id in ids:
        card = self.col.getCard(id)
        r = random.randint(imin, imax)
        d.append(dict(id=id, due=r+t, ivl=max(1, r), mod=mod,
                      usn=self.col.usn(), fact=card.factor))
    self.remFromDyn(ids)
    self.col.db.executemany("""
update cards set type=2,queue=2,ivl=:ivl,due=:due,odue=0,
usn=:usn,mod=:mod,factor=:fact where id=:id""",
                            d)
    self.col.log(ids)    

def newforgetCards(self, ids):
    "Put cards at the end of the new queue."
    d = []
    for id in ids:
        card = self.col.getCard(id)
        d.append(dict(id=id, fact=card.factor))
    self.remFromDyn(ids)        
    self.col.db.executemany("""
update cards set type=0,queue=0,ivl=0,due=0,odue=0,factor=:fact where id=:id""",
                            d)
    pmax = self.col.db.scalar(
        "select max(due) from cards where type=0") or 0
    # takes care of mod + usn
    self.sortCards(ids, start=pmax+1)
    self.col.log(ids)
