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
		NSTask.launchedTaskWithLaunchPath_arguments_("/bin/sh",
			["-c", self.cmd])

	def valueForKey_(self, k):
		return self.__dict__[k]

	def setValue_forKey_(self, v, k):
		self.__dict__[k]=v

class Controller(NibClassBuilder.AutoBaseClass):

	def deadProcess_(self, notification):
		print "Got a notification", notification

	def awakeFromNib(self):
		print "Awakened from NIB"
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
		cmd.run()

if __name__ == "__main__": 
	AppHelper.runEventLoop()
