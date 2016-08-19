from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QStandardPaths, pyqtSignal, Qt
from ui.pluginselectdialog import Ui_PluginSelectDialog
from ui.logindialog import Ui_LoginDialog
from . import arcclasses as ARCC

class PluginSelectDialog(QDialog):
	# This is bad. If another object want's to be the parent, what will happen?
	# But at the same time, this needs to be relatively static due to it being
	# needed by different parts of the program. Maybe have instances tied to
	# the ARCTool and just have things find that? WHAT SHOULD I DO. Oh well, it
	# works for now, and this memo exists, so it can be taken care of later.
	parent = None
	ui = None
	# Holds package objects. Real name is p.name, nice name is p.getName()
	# Indices are numbers
	packageInfo = {}
	packageIndices = {}
	# Holds plugin objects. Real name is p.name, nice name is p.getName()
	# Indices are package real names -> plugin real names
	pluginInfo = {}
	__init = False

	def __init__(self,parent):
		super(PluginSelectDialog,self).__init__(parent)

		if not PluginSelectDialog.__init:
			PluginSelectDialog.ui = Ui_PluginSelectDialog()
			PluginSelectDialog.ui.setupUi(self)

			PluginSelectDialog.parent = parent
			PluginSelectDialog.ui.packageList.currentItemChanged.connect(
				PluginSelectDialog.updatePluginList
			)
			PluginSelectDialog.ui.pluginList.currentItemChanged.connect(
				PluginSelectDialog.updateDetails
			)
			self.setWindowTitle("Select Plugin")

			PluginSelectDialog.updatePackageList()
			PluginSelectDialog.updatePluginList()
			PluginSelectDialog.ui.packageList.setCurrentRow(0)
			PluginSelectDialog.__init = True

	# Update packageInfo with packages and add their nice names to the list
	# Also map the real names to the indices in the info list
	# Also create an entry in the pluginInfo list for each package's plugins
	@staticmethod
	def updatePackageList():
		PluginSelectDialog.packageInfo = sorted(
			PluginSelectDialog.parent.packages)
		PluginSelectDialog.ui.packageList.clear()
		PluginSelectDialog.packageIndices = {}
		for p in PluginSelectDialog.packageInfo:
			PluginSelectDialog.packageIndices[p.name] = len(
				PluginSelectDialog.packageIndices)
			PluginSelectDialog.pluginInfo[p.name] = {}
			PluginSelectDialog.ui.packageList.addItem(p.getName())

	# Load all plugins and store them according to their package
	@staticmethod
	def updatePluginInfo():
		for p in PluginSelectDialog.packageInfo:
			for m in p.getPluginNames():
				if not m in PluginSelectDialog.pluginInfo[p.name]:
					plugin = p.newPlugin(m,True)
					if plugin is not None:
						PluginSelectDialog.pluginInfo[p.name][m] = plugin
						(PluginSelectDialog.pluginInfo[p.name]
							[plugin.getName()]) = plugin


#HEY I JUST STARTED APPENDING PACKAGE NAMES TO PLUGINS IN PLUGIN INFO BUT THIS
#ISN"T THE BEST WAY< TAKE CARE OF IT.

	# Update the plugin list widget to contain the selected package's plugins
	@staticmethod
	def updatePluginList():
		if PluginSelectDialog.ui.packageList.currentItem() is None: return;
		index_ = PluginSelectDialog.ui.packageList.currentIndex().row()
		package = PluginSelectDialog.packageInfo[index_]

		PluginSelectDialog.updatePluginInfo()

		PluginSelectDialog.ui.pluginList.clear()
		PluginSelectDialog.ui.pluginList.addItems(
			[
				PluginSelectDialog.pluginInfo[package.name][m].getName()
				for m in package.getPluginNames()
				if m in PluginSelectDialog.pluginInfo[package.name]
			]
		)
		PluginSelectDialog.ui.pluginList.setCurrentRow(0)

	@staticmethod
	def updateDetails():
		if PluginSelectDialog.ui.pluginList.currentItem() is None: return;

		index_ = PluginSelectDialog.ui.packageList.currentIndex().row()
		package = PluginSelectDialog.packageInfo[index_]
		names = sorted(package.getPluginNames())
		name = names[PluginSelectDialog.ui.pluginList.currentIndex().row()]

		# Failsafe
		# plugin = None
		# if not name in PluginSelectDialog.pluginInfo:
		# 	plugin = PluginSelectDialog.packageInfo[index_].newPlugin(name,True)
		# 	PluginSelectDialog.pluginInfo[name] = plugin
		# else:
		if name not in PluginSelectDialog.pluginInfo[package.name]:
			return

		plugin = PluginSelectDialog.pluginInfo[package.name][name]

		PluginSelectDialog.ui.name.setText(plugin.getName())
		PluginSelectDialog.ui.version.setText(plugin.getVersion())
		PluginSelectDialog.ui.author.setText(plugin.getAuthors())
		PluginSelectDialog.ui.description.setText(plugin.getDescription())

		return

	# Return the nice name of the currently selected plugin
	def getCurrentPluginName(self):
		return self.ui.pluginList.currentItem().text()

	# Return the nice name of the currently selected package
	def getCurrentPackageName(self):
		return self.ui.packageList.currentItem().text()

	# Returns a full plugin object of the currently selected plugin
	def getCurrentPlugin(self):
		index_ = self.ui.packageList.currentIndex().row()
		package = self.packageInfo[index_]
		names = sorted(package.getPluginNames())
		name = names[self.ui.pluginList.currentIndex().row()]
		return package.newPlugin(name)

	# Returns a list of nice names for every package
	# Returns a list of real names for every package
	@staticmethod
	def getPackageNames(real=False):
		if real:
			return [p.name for p in PluginSelectDialog.packageInfo]
		else:
			return [p.getName() for p in PluginSelectDialog.packageInfo]

	# Returns a list of plugin nice names given a package nice or real name
	# If you want the real names, get them from a package object
	@staticmethod
	def getPluginNames(package,real=False):
		if real and package in PluginSelectDialog.packageIndices:
			return PluginSelectDialog.packageInfo[
				PluginSelectDialog.packageIndices[package]
			].getPluginNames()

		index_ = PluginSelectDialog.ui.packageList.findItems(
			package,Qt.MatchFixedString
		)
		if len(index_)  > 0:
			index_ = PluginSelectDialog.ui.packageList.row(index_[0])
			names = []
			for m in PluginSelectDialog.packageInfo[index_].getPluginNames():
				if m in PluginSelectDialog.pluginInfo:
					names.append(PluginSelectDialog.pluginInfo[m].getName())
			return names

	# Returns a package item given its nice or real name
	@staticmethod
	def getPackage(package,real=False):
		if real and package in PluginSelectDialog.packageIndices:
			return PluginSelectDialog.packageInfo[
				PluginSelectDialog.packageIndices[package]
			]
		index_ = PluginSelectDialog.ui.packageList.findItems(
			package,Qt.MatchFixedString
		)
		if len(index_) > 0:
			index_ = PluginSelectDialog.ui.packageList.row(index_[0])
		return PluginSelectDialog.packageInfo[index_]

	# Returns a plugin item by providing it's real package name and real name
	# The returned object has no ui widget
	@staticmethod
	def getPluginInfo(package,plugin):
		return PluginSelectDialog.pluginInfo[package][plugin]

class LoginDialog(QDialog):
	credentials = pyqtSignal([str, str])
	username = pyqtSignal([str])
	password = pyqtSignal([str])

	def __init__(self,parent):
		super(LoginDialog,self).__init__(parent)

		self.ui = Ui_LoginDialog()
		self.ui.setupUi(self)
		self.setWindowTitle("Provide Login Details")
		self.ui.buttonBox.accepted.connect(self.okay)
		self.ui.buttonBox.rejected.connect(self.cancel)

	def okay(self):
		self.credentials.emit(self.ui.a.text(),self.ui.b.text())
		self.username.emit(self.ui.a.text())
		self.password.emit(self.ui.b.text())
		self.ui.a.setText('')
		self.ui.b.setText('')

	def cancel(self):
		self.ui.a.setText('')
		self.ui.b.setText('')

	def setLabel(self,text):
		self.ui.label.setText(text)