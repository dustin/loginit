#!/usr/bin/env python
"""

Copyright (c) 2004  Dustin Sallings <dustin@spy.net>
"""

from PyObjCTools import NibClassBuilder, AppHelper
import objc
from Foundation import NSNotificationCenter, NSTask, NSUserDefaults
from AppKit import NSApplication

NibClassBuilder.extractClasses("LogInit")

class Processes(NibClassBuilder.AutoBaseClass):

	def init(self):
		self.cmds=[]
		return self

	def numberOfRowsInTableView_(self, table):
		return len(self.cmds)

	def tableView_objectValueForTableColumn_row_(self, table, column, row):
		rv=self.cmds[row].valueForKey_(column.identifier())
		return(rv)

	def tableView_setObjectValue_forTableColumn_row_(self, table, v, col, row):
		rv=self.cmds[row].setValue_forKey_(v, col.identifier())

	def addItem(self, it):
		self.cmds.append(it)

	def delRow(self, row):
		del self.cmds[row]

	def __getitem__(self, which):
		return self.cmds[which]

	def toArray(self):
		return(map(lambda x: x.toDict(), self.cmds))

	def cmdFromDict(self, dict):
		rv=Command(dict['cmd'])
		rv.shouldRun=dict['shouldRun']
		return rv

	def loadArray(self, array):
		self.cmds=map(lambda x: self.cmdFromDict(x), array)

class Command:
	def __init__(self, cmd):
		self.cmd=cmd
		self.pid=-1
		self.shouldRun=False
		self.task=None

	def run(self):
		self.task=NSTask.launchedTaskWithLaunchPath_arguments_("/bin/sh",
			["-c", self.cmd])
		self.pid=self.task.processIdentifier()
		return self.pid

	def __str__(self):
		return "<Command:  " + self.cmd + ">"

	__repr__ = __str__

	def shouldBeRunning(self):
		return self.shouldRun

	def isRunning(self):
		rv=False
		if self.task is not None:
			rv=self.task.isRunning()
		return rv

	def stopRunning(self):
		if self.isRunning():
			self.task.terminate()

	def valueForKey_(self, k):
		return self.__dict__[k]

	def setValue_forKey_(self, v, k):
		# print "Setting", k, "to", v
		self.__dict__[k]=v
		# If it's run, send a notification
		if k == 'shouldRun':
			nc=NSNotificationCenter.defaultCenter()
			nc.postNotificationName_object_("RUN_CHECKED", self)

	def toDict(self):
		return({'shouldRun': self.shouldRun, 'cmd': self.cmd})

class Controller(NibClassBuilder.AutoBaseClass):

	def deadProcess_(self, notification):
		"""Called to let us know when a task completes"""
		task=notification.object()
		thepid=task.processIdentifier()
		# If this is one of our managed commands, clean it up
		if self.pids.has_key(thepid):
			cmd=self.pids[thepid]
			cmd.pid=-1
			del self.pids[thepid]
			self.table.reloadData()

			if cmd.shouldBeRunning():
				self.performSelector_withObject_afterDelay_('runCommand:',
					cmd, 5.0)

	def runChecked_(self, notification):
		"""Called when the run checkbox is checked or unchecked"""
		cmd=notification.object()
		if cmd.shouldBeRunning():
			if not cmd.isRunning():
				self.runCommand_(cmd)
		else:
			if cmd.isRunning():
				self.stopCommand_(cmd)

	def initDefaults(self):
		defaults=NSUserDefaults.standardUserDefaults()
		ob=defaults.objectForKey_("cmds")
		if ob is not None:
			ds=self.table.dataSource()
			ds.loadArray(ob)
			self.table.reloadData()

	def awakeFromNib(self):
		print "Awakened from NIB"
		NSApplication.sharedApplication().setDelegate_(self)
		self.pids={}
		nc=NSNotificationCenter.defaultCenter()
		nc.addObserver_selector_name_object_(self,
			'deadProcess:',
			"NSTaskDidTerminateNotification",
			None)
		nc.addObserver_selector_name_object_(self,
			'runChecked:',
			"RUN_CHECKED",
			None)

		self.initDefaults()

	def addCommand(self, cmd):
		ds=self.table.dataSource()
		ds.addItem(cmd)
		self.table.reloadData()

	def addEntry_(self, sender):
		self.addCommand(Command("do something"))

	def stopCommand_(self, cmd):
		# print "Stopping", cmd
		cmd.stopRunning()

	def runCommand_(self, cmd):
		# print "Starting", cmd
		pid=cmd.run()
		self.pids[pid]=cmd
		self.table.reloadData()

	def removeEntry_(self, sender):
		ds=self.table.dataSource()
		row=self.table.selectedRow()
		if row >= 0:
			ds.delRow(row)
			self.table.reloadData()

	def run_(self, sender):
		ds=self.table.dataSource()
		row=self.table.selectedRow()
		cmd=ds[row]
		self.runCommand_(cmd)

	def applicationWillTerminate_(self, notification):
		print "Application is terminating"
		ds=self.table.dataSource()
		defaults=NSUserDefaults.standardUserDefaults()
		defaults.setObject_forKey_(ds.toArray(), "cmds")
		for cmd in self.pids.values():
			print "Terminating", cmd
			cmd.stopRunning()

if __name__ == "__main__": 
	AppHelper.runEventLoop()
