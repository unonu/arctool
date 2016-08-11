#!/usr/bin/python3

import sys
import re
import os
import tarfile
import tempfile
import importlib

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QStandardPaths, pyqtSignal
from ui.mainwindow import Ui_MainWindow

if __name__ == '__main__':
	import arc.arcclasses as ARCC
	import arc.arcdocument as ARCD
	import arc.arcgui as ARCG
	import arc.arcpreferences as ARCP

PANDOC = False
try:
	import pypandoc
	PANDOC = True
except ImportError:
	print("Couldn't import pypandoc. Make sure it's installed with `pip3"
		" install pypandoc`"
	)

class ARCTool(QMainWindow):
	contextChanged = pyqtSignal([str])
	profileChanged = pyqtSignal()

	def __init__(self,profile=None):
		super(ARCTool, self).__init__()

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.checkFileSystem()


		# Disable Plugin Tools
		self.ui.pluginToolsWidget.setEnabled(False)

		# Create Profile and Report
		self.profile = ARCC.Profile()
		self.profilePath = None
		self.execPath = os.path.dirname(__file__)
		self.document = None
		self.context = None
		self.loadContexts()
		self.profile.setListWidget(self.ui.sectionList)
		self.isSaved = True

		self.profileChanged.connect(lambda: self.setIsSaved(False))

		# Set up icons
		self.ui.saveProfile.setIcon(
			QIcon(os.path.join(self.execPath, "icons/document-save.png")))
		self.ui.openProfile.setIcon(
			QIcon(os.path.join(self.execPath, "icons/document-open.png")))
		self.ui.addSection.setIcon(
			QIcon(os.path.join(self.execPath, "icons/list-add.png")))
		self.ui.removeSection.setIcon(
			QIcon(os.path.join(self.execPath, "icons/list-remove.png")))
		self.ui.moveUp.setIcon(
			QIcon(os.path.join(self.execPath, "icons/go-up.png")))
		self.ui.moveDown.setIcon(
			QIcon(os.path.join(self.execPath, "icons/go-down.png")))

		# Export actions
		self.ui.actionPrint_PDF.triggered.connect(
			lambda: ARCD.pdfExport(self.document)
		)
		# self.ui.actionExport_ODF.triggered.connect(
		# 	lambda: ARCD.odfExport(self.document,self.profile.getName())
		# )
		self.ui.actionExport_HTML.triggered.connect(
			lambda: ARCD.htmlExport(self.document,self.profile.getName())
		)
		self.ui.actionExport_Plain_Text.triggered.connect(
			lambda: ARCD.textExport(self.document,self.profile.getName())
		)
		self.ui.actionExport_docx.setEnabled(PANDOC)
		self.ui.actionExport_docx.triggered.connect(
			lambda: ARCD.docxExport(self.document,self.profile.getName())
		)
		self.ui.actionExport_odt.setEnabled(PANDOC)
		self.ui.actionExport_odt.triggered.connect(
			lambda: ARCD.odtExport(self.document,self.profile.getName())
		)

		# Save As action
		self.ui.actionSave_Profile_As.triggered.connect(
			lambda: self.saveProfile(True)
		)

		# Add Contexts to combo
		for c in self.contexts:
			self.ui.contextBox.addItem(c.getName())

		self.ui.workspaceSplitter.setStretchFactor(1,1)

		# Remove Section dialog
		self.removeDialog = QMessageBox(self)
		self.removeDialog.setWindowTitle("Remove Section?")
		self.removeDialog.setStandardButtons(QMessageBox.Cancel
											 | QMessageBox.Yes
											)
		self.removeDialog.setText("This action cannot be undone. Are you sure"
								  "you want to remove this section?"
		 )
		self.removeDialog.buttonClicked.connect(self.removeSection)

		# Plugin Select dialog and packages
		self.packages = []
		self.plugins = {}
		self.packageNames = {}
		self.pluginDialog = ARCG.PluginSelectDialog(self)
		self.pluginDialog.accepted.connect(self.assignSectionPlugin)
		self.loadPackages()

		# Preference Dialog
		self.preferenceDialog = ARCP.PreferenceManager(self)
		self.ui.actionPreferences.triggered.connect(self.preferenceDialog.exec)

		# Import package file browser
		self.ui.actionImport_Package.triggered.connect(self.openPackageArchive)

		# Connect Profile/Report Tools signals
		self.ui.profileName.textChanged.connect(
			lambda: self.profile.setName(self.ui.profileName.text())
		)
		self.ui.profileName.textChanged.connect(self.updateTitle)
		self.profileChanged.connect(self.updateTitle)
		self.ui.profileName.setText(self.profile.getName())
		self.ui.actionNew_Profile.triggered.connect(self.newProfile)
		self.ui.saveProfile.clicked.connect(self.saveProfile)
		self.ui.openProfile.clicked.connect(self.openProfile)
		self.ui.contextBox.currentIndexChanged.connect(self.updateContext)
		self.ui.generateReport.clicked.connect(self.generateReport)
		self.ui.exportReport.setMenu(self.ui.menuExport_Report)

		# Connect Section Tools signals
		self.ui.addSection.clicked.connect(lambda: self.profile.addSection())
		self.ui.moveUp.clicked.connect(
			lambda: self.profile.moveSectionUp()
		)
		self.ui.moveDown.clicked.connect(
			lambda: self.profile.moveSectionDown()
		)
		self.ui.removeSection.clicked.connect(self.removeDialog.exec)

		# Connections to update Plugin Tool elements
		self.ui.sectionList.currentRowChanged.connect(self.updatePluginTools)
		self.ui.sectionTitle.textChanged.connect(self.updateSectionTitle)
		self.ui.pluginButton.clicked.connect(self.pluginDialog.exec)
		self.ui.showTitle.stateChanged.connect(
			lambda x: self.section.setShowTitle(x > 0)
		)

		self.updatePluginTools()

		# Everything worked!
		if profile:
			self.openProfile(profile)
		self.ui.statusBar.showMessage("Ready")
		self.show()

	def updatePluginTools(self):
		index_ = self.ui.sectionList.currentIndex().row()

		# Update Section Tools
		self.ui.removeSection.setEnabled(index_ > -1)
		self.ui.actionRemove_Section.setEnabled(index_ > -1)

		self.ui.moveUp.setEnabled(index_ > 0)
		self.ui.actionMove_Section_Up.setEnabled(index_ > 0)
		self.ui.moveDown.setEnabled(
			index_ < self.profile.getSectionCount() - 1
		)
		self.ui.actionMove_Section_Down.setEnabled(
			index_ < self.profile.getSectionCount() - 1
		)

		# Remove Widget no matter what
		if self.ui.pluginOptions.widget() is not None:
			self.ui.pluginOptions.setEnabled(False)
			self.ui.pluginOptions.takeWidget()

		# Update Plugin Tools
		if index_ > -1:
			title = self.ui.sectionList.currentItem().text()
			self.ui.pluginToolsWidget.setEnabled(True)
			self.ui.sectionTitle.setText(title)
			self.section = self.profile.getCurrentSection()
			if self.section is None:
				return

			# Insert Widget into container and misc UI actions
			if self.section.hasPlugin():
				self.ui.pluginButton.setText(self.section.plugin.getName())
				if self.section.plugin.hasWidget():
					self.ui.pluginOptions.setWidget(
						self.section.plugin.getWidget()
					)
					self.ui.pluginOptions.setEnabled(True)
				self.ui.pluginSettingsWidget.setEnabled(True)
				self.ui.showTitle.setChecked(self.section.showTitle)
			else:
				self.ui.pluginButton.setText("Set...")
				self.ui.showTitle.setChecked(True)
				self.ui.pluginSettingsWidget.setEnabled(False)
		else:
			self.ui.pluginToolsWidget.setEnabled(False)
			self.ui.sectionTitle.setText('')

		self.ui.generateReport.setEnabled(len(self.profile) > 0)
		self.ui.actionGenerate_Report.setEnabled(len(self.profile) > 0)
		self.ui.exportReport.setEnabled(self.document is not None)
		self.ui.menuExport_Report.setEnabled(self.document is not None)

	# For the following Section operations, there is an implicit "Current"
	# in front of "Section"
	def updateSectionTitle(self):
		if self.ui.sectionList.currentItem() is not None:
			self.profile.setSectionTitle(
				self.ui.sectionList.currentItem().text(),
				self.ui.sectionTitle.text()
			)

	def assignSectionPlugin(self,plugin=None):
		self.section.setPlugin(plugin if plugin is not None
							   else self.pluginDialog.getCurrentPlugin())
		self.updatePluginTools()
		self.setIsSaved(not self.section.hasPlugin())

	def removeSection(self,b):
		if self.removeDialog.buttonRole(b) == QMessageBox.YesRole:
			self.profile.removeSection()

	def setIsSaved(self,saved):
		self.isSaved = saved

	def newProfile(self):
		if not self.isSaved:
			mb = QMessageBox()
			mb.setText("The Profile has been modified")
			mb.setInformativeText("Changes made to this profile have yet to"
								  " be saved. Do you want to save?")
			mb.setStandardButtons(mb.Save | mb.Discard | mb.Cancel)
			mb.setDefaultButton(mb.Save)
			r = mb.exec()

			if r == mb.Save and self.saveProfile() < 0:
				return

			elif r == mb.Cancel:
				return

		self.ui.sectionList.clear()
		self.profile = ARCC.Profile()
		self.document = None
		self.setContext('None')
		self.profile.setListWidget(self.ui.sectionList)
		self.ui.profileName.setText(self.profile.getName())
		self.setIsSaved(True)
		self.updateTitle()
		self.updatePluginTools()

		return

	def openProfile(self,path=None):
		path = path or QFileDialog.getOpenFileName(
			self,"Open Profile",None,
			"Automatic Report Profile (*.arp)"
		)[0]
		
		if path is None or path[0] == '':
			return

		self.profilePath = path

		path = re.match("^([^.]+)(?:\..+)?$", path)
		path = path.group(1) + ".arp"
		print("openning from",path)
		try:
			file = open(path, 'r').read()
		except FileNotFoundError:
			print("Couldn't open profile " + path)
			return

		# Profile information
		profileHeader = re.search("<\s*profile(.+?)>", file)
		if profileHeader is None:
			print("Malformed profile.info")
			return

		# Profile name
		name = re.search("name\s*=\s*\"(.+)\"", profileHeader.group(1))
		if name is None:
			print("Profile name not found")
			return
		name = name.group(1)
		print("Profile named "+name)

		# Number of sections in this Profile
		numSections = re.search("sections\s*=\s*(\d+)", profileHeader.group(1))
		if numSections is None:
			print("Number of sections not found")
			return
		numSections = int(numSections.group(1))

		# Context
		context = re.search(
			"<\s*context(.+?)(?=\s*/?>)(/>)?(?(2)([^`]+?)<\s*/context\s*>|)",
			file
		)
		cname = re.search("name\s*=\s*([\w ]+)", context.group(1)).group(1)
		contextOptions = None
		if context.group(3):
			keys = re.findall("key\s*=\s*\"(\w+)",context.group(3))
			values = re.findall("value\s*=\s*\"(.+?)(?:(?<!\\\)\")",
								context.group(3)
			)
			properties = re.findall("property\s*=\s*\"(\w+)",context.group(3))
			contextOptions = dict(
				[
					(keys[x], (values[x], properties[x], types[x]))
					for x in range(len(keys))
				]
			)

		# Table of Contents
		toc = re.search("<contents>\s*(.*/>)\s*</contents>", file, re.DOTALL)
		if toc is None:
			print("couldn't find contents section")
			return
		toc = re.findall("<\s*section(.+)/>", toc.group(1))

		# Sections
		sections = []
		for s in toc:
			section = [re.search("title\s*=\s*\"(.+)\"", s).group(1),
						int(re.search("pos\s*=\s*(\d+)", s).group(1)),True]
			sections.append(section)
		sections.sort(key=lambda x : x[1])

		if len(sections) != numSections:
			print("Missing section details")
			return

		# As a matter of course, these indicies correspond to those in sections
		plugins = []
		for s in sections:
			section = re.search(
				"<section\s*.*?title\s*=\s*\"%s\"(.*?plugin.*?)/?>"
					%(re.escape(s[0])),
				file
			)
			showTitle = re.search(
				"showTitle\s*=\s*(\d)",section.group(1)
			).group(1)
			s[2] = showTitle == '1'

			# Plugin persistence
			mname = re.search(
				"plugin\s*=\s*\"(.+?)\"",section.group(1)
			).group(1)
			package = ''
			options = None
			extras = None
			if mname != "None":
				plugin = re.search(
					'''(?x)<section\s*.*?title\s*=\s*\"%s\".*?plugin[^/]+?>
						([^`]+?)</\s*section\s*>'''%(re.escape(s[0])),file
				)
				plugin = plugin.group(1)
				package = re.search(
					'''(?x)<plugin\s.*?package\s*=\s*\"(.+?)\".*?(?P<single>/)?
					>(?(single)|(?P<options>[^`]+)?</plugin>)''', plugin
				)
				options = package.group("options")
				package = package.group(1)
				# Construct a dictionary of key -> (value, prop, type)
				# or key -> value
				if options:
					# ummm should escap xml so this can't get tricked
					# print(options)
					numOpts = len(re.findall("<\s*opt",options))
					numExt = len(re.findall("<\s*extra",options))
					# print(numOpts, numExt)
					keys = re.findall("key\s*=\s*\"(\w+)",options)
					values = re.findall(
						"(?s)value\s*=\s*\"(.*?)(?:(?<!\\\)\")",options
					)
					properties = re.findall("property\s*=\s*\"(\w+)",options)
					types = re.findall("type\s*=\s*\"(\w+)",options)
					# print(keys, values)
					# Make sure to unescape quotes, BTW
					options = dict(
						[
							(keys[x],
								(values[x].replace('\\"','"'),
									properties[x], types[x]))
							for x in range(numOpts)
						]
					)
					extras = dict(
						[
							(keys[x+numOpts],
								values[x+numOpts].replace('\\"','"'))
							for x in range(numExt)
						]
					)
			plugins.append([mname,package,options,extras])

		# Construct Profile
		self.ui.sectionList.clear()
		self.profile = ARCC.Profile()
		self.profile.setListWidget(self.ui.sectionList)
		for x in range(len(sections)):
			s = self.profile.addSection(sections[x][0])
			s.setShowTitle(sections[x][2])
			# Get new plugin from package. key error if existing is None
			if plugins[x][0] != "None":
				m = self.packageNames[plugins[x][1]].newPlugin(plugins[x][0])
				if m is None:
					# Should disable section, but keep the plugin assossciation
					continue
				# print("Set %s to %s" %(sections[x][0],plugins[x][0]))
				# Options
				if plugins[x][2]:
					for k in plugins[x][2]:
						m.setOption(
							k,(plugins[x][2][k][0],plugins[x][2][k][1])
						)
					m.update()
				# Extras
				if plugins[x][3]:
					for k in plugins[x][3]:
						m.setExtra(k,plugins[x][3][k])
					m.update()

				s.setPlugin(m)
		self.profile.setName(name)
		self.setContext(cname)
		if contextOptions:
			self.context.setOptions(contextOptions)
		self.ui.profileName.setText(self.profile.getName())
		self.ui.sectionList.setCurrentRow(0)
		self.updatePluginTools()
		self.setIsSaved(True)
		self.updateTitle()

	def saveProfile(self,saveAs=False):
		name = self.profile.getName().replace(' ', '_') + ".arp"
		path = None
		if saveAs or self.profilePath is None:
			path = QFileDialog.getSaveFileName(
				self,"Save Profile",name,
				"Automatic Report Profile (*.arp)"
			)
			if path is None or path[0] == '':
				return -1
			self.profilePath = path = path[0]
		else:
			path = self.profilePath

		path = re.match("([^\.]+)\.?.+$", path)
		path = path.group(1) + ".arp"
		print("saving to",path)
		file = open(path, 'w')
		data = ''

		#Preserve order
		toc = self.profile.getTOC()
		data += toc[0]

		#Preserve data
		for s in toc[1]:
			data += s.serialise()

		#Preserve context
		data += "<context name=%s/>\n" %(self.context.getName())

		data = "<profile name=\"%s\" sections=%d>\n\t%s</profile>\n"\
			%(self.profile.getName(),len(toc[1]),data)
		file.write(data)
		self.setIsSaved(True)
		self.updateTitle()
		self.ui.statusBar.showMessage("Saved Profile as %s" %name)
		return 0

	def updateTitle(self):
		self.setWindowTitle("ARCTool"
							+ (" - %s"%(self.ui.profileName.text())
							  if self.ui.profileName.text() != ''
							  else '')
							+ ('' if self.isSaved else '*')
		)

	def loadContexts(self):
		self.contexts = []
		# TODO: look in packages for contexts
		# Default Contexts
		self.contexts.append(ARCC.Context())
		self.contexts.append(ARCC.DateContext())
		self.contexts.append(ARCC.TimeContext())
		self.contextNames = dict(
			[
				(self.contexts[x].getName(),x)
				for x in range(len(self.contexts))
			]
		)
		self.context = self.contexts[0]

	def updateContext(self):
		if self.context.hasWidget():
			self.context.getWidget().setParent(None)
			self.ui.contextWidgetContainer.removeWidget(
				self.context.getWidget()
			)
		self.context = self.contexts[self.ui.contextBox.currentIndex()]
		self.contextChanged.emit(self.context.getName())
		if self.context.hasWidget():
			self.ui.contextWidgetContainer.addWidget(self.context.getWidget())
			self.ui.contextWidgetContainer.update()

	def setContext(self,contextName):
		if contextName in self.contextNames:
			self.ui.contextBox.setCurrentIndex(self.contextNames[contextName])
		self.updateContext()

	def checkFileSystem(self):
		self.storagePath = QStandardPaths.standardLocations(
			QStandardPaths.AppDataLocation
		)[0]
		self.storagePath = os.path.join(self.storagePath, 'arctool')
		os.makedirs(self.storagePath, 0o777, True)
		os.makedirs(os.path.join(self.storagePath, "packages"), 0o777, True)
		open(os.path.join(self.storagePath, "config"), 'a').close()
		sys.path.append(os.path.dirname(__file__))
		# Add package directories so packages can include local Python plugins
		sys.path.append(os.path.join(self.storagePath, "packages"))
		sys.path.append(os.path.join(os.path.dirname(__file__), "packages"))


	def loadPackages(self):
		packagePaths = []

		# Scan directories for available packages
		for d in os.scandir(os.path.join(self.storagePath, "packages")):
			if d.is_dir():
				packagePaths.append(d.path)

		for d in os.scandir(os.path.join(os.path.dirname(__file__),
			"packages")):
			if d.is_dir():
				packagePaths.append(d.path)

		# TODO: add custom (user defined) package search directories

		# Create Packages and stage their plugins
		for p in packagePaths:
			package = ARCC.Package(p)
			if package.getName() not in self.packageNames:
				self.packageNames[package.getName()] = package
				self.packages.append(package)
				# Map plugin names to the package
				for m in package.getPluginNames():
					self.plugins[m] = package

		ARCG.PluginSelectDialog.updateModuleList()

	def generateReport(self):
		self.ui.statusBar.showMessage("Generating Report...")
		self.ui.exportReport.setEnabled(False)
		self.document = ARCD.Document()
		self.document.setTitle(self.profile.getName())
		
		toc = self.profile.getTOC()

		pb = QProgressBar()
		pb.setRange(0,len(toc))
		self.ui.statusBar.insertWidget(0,pb,1)

		i = 1
		for s in toc[1]:
			# s.updateContent()
			pb.setValue(i)
			if s.hasPlugin():
				r=0
				try:
					r = self.document.addSection(s)
				except BaseException as e:
					# e = sys.exc_info()[2]
					print('nope', e)
					r = -1
				# else:
				if r < 0:
					self.ui.statusBar.removeWidget(pb)
					self.ui.statusBar.showMessage(
						"Generation Failed At " + s.getTitle()
					)
					self.ui.sectionList.setCurrentRow(toc[1].index(s))
					return
			self.ui.statusBar.showMessage("Generating Report...")
			i += 1

		self.ui.statusBar.removeWidget(pb)

		self.updatePluginTools()
		self.ui.statusBar.showMessage("Finished Generating Report")

		return

	# def exportReport(self):
	# 	self.ui.statusBar.showMessage("Exporting Report")
	# 	ARCD.pdfExport(self.document)
	# 	self.ui.statusBar.showMessage("Finished Exporting Report")

	def openPackageArchive(self,path=None):
		path = path or QFileDialog.getOpenFileName(
			self,"Open Profile",None,
			"Package Archive (*.tar.gz)"
		)[0]
		self.installPackage(path)

	def installPackage(self,path):
		pkgName = os.path.basename(path).split('.',1)[0]
		msg = QMessageBox(self)
		msg.setWindowTitle('Install Package')
		msg.setStandardButtons(QMessageBox.Ok)
		with tarfile.open(path,'r:gz') as archive:
			path = os.path.join(self.storagePath, "packages", pkgName)

			try:
				os.mkdir(path)
			except FileExistsError:
				print("A package by this name already exists")
				msg.setText('A package by this name already exists.')
				self.ui.statusBar.showMessage(
					"A package by this name already exists.")
				msg.exec()
				# This should actually update the package instead...
				return

			names = archive.getnames()
			if ('__init__.py' not in names):

				os.rmdir(path)
				msg.setText('The package is malformed.')
				self.ui.statusBar.showMessage("The package is malformed.")
				msg.exec()
				return

			try:
				tmpDir = tempfile.mkdtemp()
				archive.extract('__init__.py',tmpDir,numeric_owner=True)
				with open(os.path.join(tmpDir,'__init__.py')) as init:
					all = re.search(r'(?s)__all__\s*=\s*\[(.)+?\](?<=\r)?\n',
						init.read()).group(1)
					for name in re.findall('\w+',all):
						if name not in names:
							print("Missing plugin")
				os.remove(os.path.join(tmpDir,'__init__.py'))
				os.rmdir(tmpDir)
			except:
				os.rmdir(path)
				try:
					os.remove(os.path.join(tmpDir,'__init__.py'))
				except:
					pass
				try:
					os.rmdir(tmpDir)
				except:
					pass
				msg.setText('The package could not be read.')
				self.ui.statusBar.showMessage("The package could not be read.")
				msg.exec()
				return

			for name in names:
				# Check for malicious intent? ;p
				if re.match(r'^((\.\.)|\.[/\\]|/|[A-Za-z]+:\\)', name):
					return
				archive.extract(name,path,numeric_owner=True)

		msg.setText('The package was succesfully installed')
		msg.exec()
		self.loadPackages()
		return

	@staticmethod
	def getContext():
		tlw = QApplication.topLevelWidgets()
		for w in tlw:
			if type(w).__name__ == "ARCTool":
				return w.context

	@staticmethod
	def getStatusBar():
		tlw = QApplication.topLevelWidgets()
		for w in tlw:
			if type(w).__name__ == "ARCTool":
				return w.ui.statusBar

	@staticmethod
	def signalProfileChanged():
		tlw = QApplication.topLevelWidgets()
		for w in tlw:
			if type(w).__name__ == "ARCTool":
				return w.profileChanged.emit()


	@staticmethod
	def getStoragePath():
		return os.path.join(QStandardPaths.standardLocations(
			QStandardPaths.AppDataLocation)[0],'arctool'
		)

if __name__ == '__main__':
	app = QApplication([''])
	arctool = ARCTool(sys.argv[1] if len(sys.argv) > 1 else None)
	sys.exit(app.exec_())
