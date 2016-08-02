from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QStandardPaths, pyqtSignal, Qt
from ui.pluginselectdialog import Ui_PluginSelectDialog
from ui.logindialog import Ui_LoginDialog
from . import arcclasses as ARCC

class PluginSelectDialog(QDialog):
	ui = None
	packages = None
	pluginInfo = None
	__init = False

	def __init__(self,parent):
		super(PluginSelectDialog,self).__init__(parent)

		if not PluginSelectDialog.__init:
			PluginSelectDialog.packages = sorted(parent.packages)

			PluginSelectDialog.ui = Ui_PluginSelectDialog()
			PluginSelectDialog.ui.setupUi(self)
			PluginSelectDialog.ui.packageList.addItems(
				[p.getName() for p in PluginSelectDialog.packages]
			)
			PluginSelectDialog.ui.packageList.currentItemChanged.connect(
				PluginSelectDialog.updatePluginList
			)
			PluginSelectDialog.ui.pluginList.currentItemChanged.connect(
				PluginSelectDialog.updateDetails
			)
			self.setWindowTitle("Select Plugin")

			PluginSelectDialog.pluginInfo = {}
			PluginSelectDialog.updatePluginList()
			PluginSelectDialog.ui.packageList.setCurrentRow(0)
			PluginSelectDialog.__init = True

	@staticmethod
	def updatePluginInfo():
		for p in PluginSelectDialog.packages:
			for m in p.getPluginNames():
				if not m in PluginSelectDialog.pluginInfo:
					plugin = p.newPlugin(m,True)
					if plugin is not None:
						PluginSelectDialog.pluginInfo[m] = plugin
						PluginSelectDialog.pluginInfo[plugin.getName()] =plugin

	@staticmethod
	def updatePluginList():
		index_ = PluginSelectDialog.ui.packageList.currentIndex().row()

		PluginSelectDialog.updatePluginInfo()

		PluginSelectDialog.ui.pluginList.clear()
		PluginSelectDialog.ui.pluginList.addItems(
			[
				PluginSelectDialog.pluginInfo[m].getName()
				for m in PluginSelectDialog.packages[index_].getPluginNames()
				if m in PluginSelectDialog.pluginInfo
			]
		)
		PluginSelectDialog.ui.pluginList.setCurrentRow(0)

	@staticmethod
	def updateDetails():
		if PluginSelectDialog.ui.pluginList.currentItem() is None: return;

		index_ = PluginSelectDialog.ui.packageList.currentIndex().row()
		name = sorted(PluginSelectDialog.packages[index_].getPluginNames())
		name = name[PluginSelectDialog.ui.pluginList.currentIndex().row()]

		# Failsafe
		# plugin = None
		# if not name in PluginSelectDialog.pluginInfo:
		# 	plugin = PluginSelectDialog.packages[index_].newPlugin(name,True)
		# 	PluginSelectDialog.pluginInfo[name] = plugin
		# else:
		if name not in PluginSelectDialog.pluginInfo:
			return

		plugin = PluginSelectDialog.pluginInfo[name]

		PluginSelectDialog.ui.name.setText(plugin.getName())
		PluginSelectDialog.ui.version.setText(plugin.getVersion())
		PluginSelectDialog.ui.author.setText(plugin.getAuthors())
		PluginSelectDialog.ui.description.setText(plugin.getDescription())

		return

	def getCurrentPluginName(self):
		return self.ui.pluginList.currentItem().text()

	def getCurrentPackageName(self):
		return self.ui.packageList.currentItem().text()

	def getCurrentPlugin(self):
		index_ = self.ui.packageList.currentIndex().row()
		name = sorted(self.packages[index_].getPluginNames())
		name = name[self.ui.pluginList.currentIndex().row()]
		return self.packages[index_].newPlugin(name)

	@staticmethod
	def getPackageNames():
		return [p.getName() for p in PluginSelectDialog.packages]

	@staticmethod
	def getPluginNames(package):
		print(package)
		index_ = PluginSelectDialog.ui.packageList.findItems(
			package,Qt.MatchFixedString
		)
		if len(index_)  > 0:
			index_ = PluginSelectDialog.ui.packageList.row(index_[0])
			names = []
			for m in PluginSelectDialog.packages[index_].getPluginNames():
				if m in PluginSelectDialog.pluginInfo:
					names.append(PluginSelectDialog.pluginInfo[m].getName())
			return names

	@staticmethod
	def getPackage(package):
		index_ = PluginSelectDialog.ui.packageList.findItems(
			package,Qt.MatchFixedString
		)
		if len(index_) > 0:
			index_ = PluginSelectDialog.ui.packageList.row(index_[0])
		return PluginSelectDialog.packages[index_]

	@staticmethod
	def getPluginInfo(package,plugin):
		return PluginSelectDialog.pluginInfo[plugin]

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
		self.credentials.emit(None,None)
		self.username.emit(None)
		self.password.emit(None)
		self.ui.a.setText('')
		self.ui.b.setText('')

	def setLabel(self,text):
		self.ui.label.setText(text)