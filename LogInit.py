#!/usr/bin/env python
"""

Copyright (c) 2004  Dustin Sallings <dustin@spy.net>
"""

from PyObjCTools import NibClassBuilder, AppHelper
from objc import getClassList, objc_object

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

class Command:
	def __init__(self, cmd):
		self.cmd=cmd
		self.pid=-1

	def setCmd_(self, to):
		self.cmd=to
		print "cmd is now", self.cmd

	def valueForKey_(self, k):
		return self.__dict__[k]

	def setValue_forKey_(self, v, k):
		self.__dict__[k]=v

class Controller(NibClassBuilder.AutoBaseClass):

	def awakeFromNib(self):
		print "Awakened from NIB"

	def addEntry_(self, sender):
		ds=self.table.dataSource()
		ds.addItem(Command("do something"))
		self.table.reloadData()

if __name__ == "__main__": 
	AppHelper.runEventLoop()
