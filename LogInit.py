#!/usr/bin/env python
"""

Copyright (c) 2004  Dustin Sallings <dustin@spy.net>
"""

from PyObjCTools import NibClassBuilder, AppHelper
import objc
from Foundation import NSNotificationCenter, NSTask

NibClassBuilder.extractClasses("LogInit")

class Processes(NibClassBuilder.AutoBaseClass):

	def init(self):
		self.data=[]
		return self

	def numberOfRowsInTableView_(self, table):
		return len(self.data)

	def tableView_objectValueForTableColumn_row_(self, table, column, row):
		rv=self.data[row].valueForKey_(column.identifier())
		return(rv)

	def tableView_setObjectValue_forTableColumn_row_(self, table, v, col, row):
		rv=self.data[row].setValue_forKey_(v, col.identifier())

	def addItem(self, it):
		self.data.append(it)

	def __getitem__(self, which):
		return self.data[which]

class Command:
	def __init__(self, cmd):
		self.cmd=cmd
		self.pid=-1

	def run(self):
		task=NSTask.launchedTaskWithLaunchPath_arguments_("/bin/sh",
			["-c", self.cmd])
		self.pid=task.processIdentifier()
		return self.pid

	def __str__(self):
		return "<Command:  " + self.cmd + ">"

	__repr__ = __str__

	def valueForKey_(self, k):
		return self.__dict__[k]

	def setValue_forKey_(self, v, k):
		self.__dict__[k]=v

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

	def awakeFromNib(self):
		print "Awakened from NIB"
		self.pids={}
		nc=NSNotificationCenter.defaultCenter()
		nc.addObserver_selector_name_object_(self,
			'deadProcess:',
			"NSTaskDidTerminateNotification",
			None)

	def addEntry_(self, sender):
		ds=self.table.dataSource()
		ds.addItem(Command("do something"))
		self.table.reloadData()

	def run_(self, sender):
		ds=self.table.dataSource()
		row=self.table.selectedRow()
		cmd=ds[row]
		pid=cmd.run()
		self.pids[pid]=cmd
		self.table.reloadData()

if __name__ == "__main__": 
	AppHelper.runEventLoop()
