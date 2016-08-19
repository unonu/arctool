from contextlib import suppress
from .num2word import num2word
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime, QDate, QTime, QObject, QEvent
from types import MethodType
from arctool import ARCTool

class Profile():
	def __init__(self,path=None):
		if path:
			print("not ready yet")
			return

		self.name = "New Profile"

		# Section Titles map to indices in "sections"
		self.sectionTitles = {}
		self.sections = []
		self.context = None
		self.listWidget = None

	def __len__(self):
		return len(self.sections)

	# Assign the QListWidget to keep track of
	def setListWidget(self,widget):
		self.listWidget = widget
		self.listWidget.model().rowsMoved.connect(
			lambda: ARCTool.signalProfileChanged()
		)

	# Update section mappings in "sectionTitles"
	def setSectionTitle(self,oldTitle,title):
		if oldTitle == title: return

		index_ = self.sectionTitles[oldTitle]
		del(self.sectionTitles[oldTitle])

		# Assure no duplicates
		if title in self.sectionTitles:
			i = 1
			dup = ''
			while title+dup in self.sectionTitles:
				dup = ' ' + num2word(i).capitalize()
				i += 1
			title += dup
		self.sectionTitles[title] = index_

		self.sections[index_].setTitle(title)
		if self.listWidget is not None:
			self.listWidget.currentItem().setText(title)

		ARCTool.signalProfileChanged()

		return

	def getSectionCount(self):
		return len(self.sections)

	def getSections(self,copy=False):
		return copy[:] if copy else copy

	def getCurrentSection(self):
		if len(self.sections) == 0:
			return None
		return self.sections[
			self.sectionTitles[
			self.listWidget.currentItem().text()]]

	def removeSection(self):
		title = self.listWidget.currentItem().text()
		index_ = self.listWidget.currentIndex().row()

		self.sections.pop(self.sectionTitles[title])
		del(self.sectionTitles[title])
		for s in self.sectionTitles:
			self.sectionTitles[s] -= 1 if self.sectionTitles[s] > index_ else 0

		self.listWidget.takeItem(index_)
		ARCTool.signalProfileChanged()

	def moveSectionUp(self):
		item = self.listWidget.currentItem()
		row = self.listWidget.currentIndex().row()
		self.listWidget.insertItem(row - 1,self.listWidget.takeItem(row))
		self.listWidget.setCurrentItem(item)
		ARCTool.signalProfileChanged()
		return True

	def moveSectionDown(self):
		item = self.listWidget.currentItem()
		row = self.listWidget.currentIndex().row()
		self.listWidget.insertItem(row + 1,self.listWidget.takeItem(row))
		self.listWidget.setCurrentItem(item)
		ARCTool.signalProfileChanged()
		return True

	def moveSectionTo(self,src,dst):
		self.sections.insert(self.sections.pop(src),dst + 1)
		ARCTool.signalProfileChanged()

	def addSection(self,title="Untitled Section"):

		# Assure no duplicates
		if title in self.sectionTitles:
			i = 1
			dup = ''
			while title+dup in self.sectionTitles:
				dup = ' ' + num2word(i).capitalize()
				i += 1
			title += dup
		# Map section title to index in "sections"
		self.sectionTitles[title] = len(self.sections)

		# Add section to widget
		self.sections.append(Section(title))
		if self.listWidget is not None:
			self.listWidget.addItem(title)
		self.listWidget.setCurrentRow(len(self.sections)-1)

		ARCTool.signalProfileChanged()
		return self.sections[-1]

	def getName(self):
		return self.name

	def setName(self,name):
		self.name = name
		ARCTool.signalProfileChanged()

	def getTOC(self):
		toc = ''
		sections = []
		for i in range(len(self.sections)):
			title = self.listWidget.item(i).text()
			toc += '\t<section title="%s" pos=%d/>\n' %(title,i)
			sections.append(self.sections[self.sectionTitles[title]])
		toc = '<contents>\n%s</contents>\n' %(toc)
		return (toc, sections)

class Section():
	def __init__(self,title="Untitled Section"):
		self.title = title
		self.plugin = None
		self.pluginName = "None"
		self.content = None
		self.showTitle = True

	def setTitle(self,title):
		self.title = title

	def getTitle(self):
		return self.title

	def setShowTitle(self,show):
		self.showTitle = show

	def updateContent(self):
		if self.plugin is None:
			return
		self.plugin.storeOptions()
		self.content = self.plugin.generate()

	def getContent(self):
		self.updateContent()
		return self.content

	def hasPlugin(self):
		return (self.plugin is not None)

	def setPlugin(self,plugin):
		self.plugin = plugin
		self.pluginName = self.plugin.getName()
		return self.plugin

	def serialise(self):
		if self.plugin is None:
			return ('<section title="%s" plugin="None" showTitle=%d/>\n'
				%(self.title,1 if self.showTitle else 0))
			
		return ('<section title="%s" plugin="%s" showTitle=%d>\n\t%s</sec'
				'tion>\n') %(self.title, self.plugin.__name__,
					1 if self.showTitle else 0, self.plugin.serialise())

class Package():
	def __init__(self,path):
		self.path = path
		import os, importlib.machinery
		self.plugins = []
		self.pluginNames = []
		self.date = None
		self.dependencies = []
		self.sources = []

		loader = importlib.machinery.SourceFileLoader(
			str(path.__hash__()),os.path.join(path,"__init__.py")
		)
		package = loader.load_module()
		self.pluginNames = package.__all__
		self.name = package.name
		self.version = package.version
		self.authors = package.authors
		self.preferenceDict = package.preferenceDict

	def __lt__(self,a):
		return self.name < a.name

	def addPlugin(self,plugin):
		self.pluginNames.append(plugin)

	def setVersion(self,version):
		self.version = [int(n) for n in version.split('.')]

	def setName(self,name):
		self.name = name

	def getName(self):
		return self.name

	def addAuthor(self,author):
		self.authors.append(author)

	def setDate(self,date):
		self.date = date

	def addDependency(self,dependancy):
		self.dependancies.append(dependancy)

	def addSource(self,source):
		self.sources.append(source)

	def getPluginNames(self):
		return self.pluginNames[:]

	def newPlugin(self,name,noUi=False):
		import os, importlib.machinery#, re
		path = os.path.join(self.path, name)

		loader = importlib.machinery.SourceFileLoader(
			name + "MOD_" + self.name,path + ".py"
		)
		# try:
		plugin = loader.load_module()

		m = plugin.Plugin(self)

		if not noUi:
			m.loadWidget(path + ".ui")
			if m.setupUi():
				m.setupUi()

		return m

class Plugin():
	def __init__(self,name="None",package=None):
		self.name = name
		self.package = package
		self.netReq = False
		self.subCount = 0
		self.contexts = []
		self.version = (0,0,0)
		self.widget = None #set from .ui file?
		self.authors = []
		self.description = "No Description"
		self.options = {} # ui_name : (value, property_name)
		self.extras = {} # key : "value"
		self.preferenceDict = None

	def setName(self,name):
		self.name = name

	def setVersion(self,version):
		self.version = [int(n) for n in version.split('.')]

	def addAuthor(self,author):
		self.authors.append(author)

	def addContext(self,context):
		self.contexts.append(context)

	def setDescription(self,description):
		self.description = description

	def getName(self):
		return self.name

	def getVersion(self):
		return "%d.%d.%d" %(self.version[0],self.version[1],self.version[2])

	def getAuthors(self):
		return ' '.join(self.authors)

	def getDescription(self):
		return self.description

	def getPreferenceDict(self):
		return self.preferenceDict or {}

	def loadWidget(self,path):
		from PyQt5 import uic 
		self.widget = uic.loadUi(path)

		# Attach signals to notify the Tool that the profile has changed.
		# If you want to use custom widgets that don't use these
		# signals, you'll have to hook this up yourself.
		sig = ARCTool.signalProfileChanged()
		for c in self.widget.__dict__.values():
			with suppress(Exception):
				c.stateChanged.connect(sig)
			with suppress(Exception):
				c.textChanged.connect(sig)
			with suppress(Exception):
				c.itemChanged.connect(sig)
			with suppress(Exception):
				c.indexChanged.connect(sig)
			with suppress(Exception):
				c.dateChanged.connect(sig)
			with suppress(Exception):
				c.valueChanged.connect(sig)
			with suppress(Exception):
				c.indexesMoved.connect(sig)

	def loadCode(self,path):
		import importlib
		importlib.import_module(path)

	def hasWidget(self):
		return self.widget is not None

	def getWidget(self):
		#should return QWidget
		return self.widget

	# Generate formatted text
	def generate(self):
		print("No overridden generate method")

	def setOption(self,key,value):
		self.options[key] = value

	def setExtra(self,key,value):
		# There are some type issues here
		self.extras[key] = value
		# print("set %s to %s" %(key, value))

	# Update user interface elements from options
	def update(self):
		if self.widget:
			for k in self.options:
				qw = self.widget.findChild(QObject,k)
				if qw:
					qw.setProperty(self.options[k][1], self.options[k][0])

	# Store the current options
	def serialise(self):
		# what if the plugin didn't load? should check somewhere
		self.storeOptions()
		return "<plugin name=\"%s\" package=\"%s\">\n\t%s%s</plugin>\n" \
			%(self.__name__, self.package.getName(),PackOptions(self.options),
				packExtras(self.extras))

class Context():
	def __init__(self,name="None"):
		self.name = name
		self.callback = lambda x : True
		self.ui = None
		self.widget = None

	def inContext(self,content):
		return self.callback(content)

	def hasWidget(self):
		return self.widget is not None

	def getName(self):
		return self.name

	def setOptions(self,opts):
		if self.widget:
			for k in opts:
				qw = self.widget.findChild(QObject,k)
				if qw:
					qw.setProperty(
						opts[k][1],
						type(qw.getProperty(opts[k][1]))(opts[k][0])
					)


class DateContext(Context):
	def __init__(self):
		super(DateContext, self).__init__("Date")
		dateTime = QDateTime.currentDateTime()
		self.begin = dateTime.date()
		self.end = dateTime.date()
		self.hasBegin = False
		self.hasEnd = False
		# ISO dates are YYYY-MM-DD

		from ui.datecontextwidget import Ui_DateContextWidget
		self.ui = Ui_DateContextWidget()
		self.widget = QtWidgets.QWidget()
		self.ui.setupUi(self.widget)
		self.ui.dateBegin.setDate(self.begin)
		self.ui.dateEnd.setDate(self.end)
		self.ui.dateBegin.setEnabled(self.ui.checkBegin.isChecked())
		self.ui.dateEnd.setEnabled(self.ui.checkEnd.isChecked())
		self.ui.checkBegin.stateChanged.connect(self.updateBegin)
		self.ui.dateBegin.dateChanged.connect(self.updateBegin)
		self.ui.checkEnd.stateChanged.connect(self.updateEnd)
		self.ui.dateEnd.dateChanged.connect(self.updateEnd)

	def getWidget(self):
		return self.widget

	def setBegin(self,date):
		self.begin = date

	def setEnd(self,date):
		self.end = date

	def updateBegin(self):
		state = self.ui.checkBegin.isChecked()
		self.ui.dateBegin.setEnabled(state)
		self.hasBegin = state
		self.begin = self.ui.dateBegin.date()
		if state:
			self.ui.dateEnd.setMinimumDate(self.ui.dateBegin.date())
		else:
			self.ui.dateEnd.clearMinimumDate()

	def updateEnd(self):
		state = self.ui.checkEnd.isChecked()
		self.ui.dateEnd.setEnabled(state)
		self.hasEnd = state
		self.end = self.ui.dateEnd.date()
		if state:
			self.ui.dateBegin.setMaximumDate(self.ui.dateEnd.date())
		else:
			self.ui.dateBegin.clearMaximumDate()

	def callback(self,content):
		# If the content got this far, we'd better hope it meshes with this
		# context. Content in this Context should implement "getDate"
		# if content.getDate is None
		valid = True
		date = content.getDate()

		if self.hasBegin:
			valid = date >= self.begin and valid
		if self.hasEnd:
			valid = date <= self.end and valid

		return valid

	# Access
	def getBegin(self,format=None):
		if self.hasBegin:
			return self.begin if not format else self.begin.toString(format)

	def getEnd(self,format=None):
		if self.hasEnd:
			return self.end if not format else self.end.toString(format)

	def getMonth(self,format):
		cd = QDate.currentDate()
		return {
			"name" : cd.toString("MMMM"),
			"long" : cd.toString("MMMM"),
			"abbreviation" : cd.toString("MMM"),
			"short" : cd.toString("MMM"),
			"number" : cd.toString("M"),
		}[format.lower()]

	def getYear(self,format):
		cd = QDate.currentDate()
		return {
			"long" : cd.toString("yyyy"),
			"short" : cd.toString("yy"),
		}[format.lower()]

	def getDay(self,format):
		cd = QDate.currentDate()
		return {
			"name" : cd.toString("dddd"),
			"long" : cd.toString("dddd"),
			"abbreviation" : cd.toString("ddd"),
			"short" : cd.toString("ddd"),
			"number" : cd.toString("d"),
		}[format.lower()]

	def toString(self,format):
		return QDate.currentDate().toString(format)

class TimeContext(Context):
	def __init__(self):
		super(TimeContext, self).__init__("Time")
		dateTime = QDateTime.currentDateTime()
		self.begin = dateTime.time()
		self.end = dateTime.time()
		self.hasBegin = False
		self.hasEnd = False

		from ui.timecontextwidget import Ui_TimeContextWidget
		self.ui = Ui_TimeContextWidget()
		self.widget = QtWidgets.QWidget()
		self.ui.setupUi(self.widget)
		self.ui.timeBegin.setTime(self.begin)
		self.ui.timeEnd.setTime(self.end)
		self.ui.timeBegin.setEnabled(self.ui.checkBegin.isChecked())
		self.ui.timeEnd.setEnabled(self.ui.checkEnd.isChecked())
		self.ui.checkBegin.stateChanged.connect(self.updateBegin)
		self.ui.timeBegin.timeChanged.connect(self.updateBegin)
		self.ui.checkEnd.stateChanged.connect(self.updateEnd)
		self.ui.timeEnd.timeChanged.connect(self.updateEnd)
		# self.updateBegin()
		# self.updateEnd()

	def getWidget(self):
		return self.widget

	def setBegin(self,time):
		self.begin = time

	def setEnd(self,time):
		self.end = time

	def updateBegin(self):
		state = self.ui.checkBegin.isChecked()
		self.ui.timeBegin.setEnabled(state)
		self.hasBegin = state
		if state:
			self.ui.timeEnd.setMinimumTime(self.ui.timeBegin.time())
		else:
			self.ui.timeEnd.setMinimumTime(QTime(0,0))

	def updateEnd(self):
		state = self.ui.checkEnd.isChecked()
		self.ui.timeEnd.setEnabled(state)
		self.hasEnd = state
		if state:
			self.ui.timeBegin.setMaximumTime(self.ui.timeEnd.time())
		else:
			self.ui.timeBegin.setMaximumTime(QTime(23,59,59,999))

	def callback(self,content):
		# If the content got this far, we'd better hope it meshes with this
		# context. Content in this Context should implement "getTime"
		# if content.getTime is None
		valid = True
		time = content.getTime()
		
		if self.hasBegin:
			valid = time >= self.begin and valid
		if self.hasEnd:
			valid = time <= self.end and valid

		return valid

	# Access
	def getBegin(self,format=None):
		if self.hasBegin:
			return self.begin if not format else self.begin.toString(format)

	def getEnd(self,format=None):
		if self.hasEnd:
			return self.end if not format else self.end.toString(format)

	def getMinute(self,format):
		ct = QTime.currentTime()
		return {
			"long" : ct.toString("mm"),
			"short" : ct.toString("m"),
		}[format.lower()]

	def getHour(self,format):
		ct = QTime.currentTime()
		return {
			"long" : ct.toString("hh"),
			"short" : ct.toString("h"),
		}[format.lower()]

	def getSecond(self,format):
		ct = QTime.currentTime()
		return {
			"long" : ct.toString("ss"),
			"short" : ct.toString("s"),
			"precise" : ct.toString("ss.zzz"),
		}[format.lower()]

	def toString(self,format):
		return QTime.currentTime().toString(format)

def PackOptions(opts):
	pack = ''
	for k in opts:
		pack += '<opt key="%s" value="%s" property="%s" type="%s"/>\n'\
			%(k,str(opts[k][0]).replace('"','\\"'),opts[k][1],
				type(opts[k][0]).__name__)
	return pack

def packExtras(extras):
	pack = ''
	for k in extras:
		pack += '<extra key="%s" value="%s"/>\n'\
			%(k,str(extras[k]).replace('"','\\"'))
	return pack