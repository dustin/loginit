#!/usr/bin/env python

from bundlebuilder import buildapp

buildapp(
	mainprogram = "LogInit.py",
	resources = ["LogInit.nib"],
	nibname = "LogInit",
)
