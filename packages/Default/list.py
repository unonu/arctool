import arc.arcclasses as arcclasses
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextCursor
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import QUrl, Qt

class Plugin(arcclasses.Plugin):
	def __init__(self,package):
		super(Plugin,self).__init__(None,package)

		self.__name__ = "list"
		self.name = "List" # Required
		self.authors = ["unonu"] # Required
		self.version = (0,0,1) # Required
		self.description = "Creates a list of text items." # Required
		self.contexts = [] # Required
		self.fix = ('','')
		self.items = 0

	#needed
	def setupUi(self):
		self.widget.addItem.clicked.connect(lambda : self.addItem())
		self.widget.removeItem.clicked.connect(lambda : self.removeItem())
		self.widget.list.currentRowChanged.connect(self.updateSelection)
		# self.widget.list.itemDoubleClicked.connect(self.widget.list.editItem)
		self.widget.list.itemActivated.connect(self.widget.list.editItem)
		self.widget.prefix.textChanged.connect(self.updateFix)
		self.widget.suffix.textChanged.connect(self.updateFix)
		self.widget.styleBox.addItem("Bullet")
		self.widget.styleBox.addItem("Circle")
		self.widget.styleBox.addItem("Square")
		self.widget.styleBox.addItem("Number")
		self.widget.styleBox.addItem("Letter (Lower Case)")
		self.widget.styleBox.addItem("Letter (Upper Case)")
		self.widget.styleBox.addItem("Roman (Lower Case)")
		self.widget.styleBox.addItem("Roman (Upper Case)")
		self.widget.styleBox.currentIndexChanged.connect(self.styleChanged)
		#Label should look at the combobox

	#call super
	def update(self):
		super(Plugin,self).update()

		#updated from extras
		if "list" in self.extras:
			for entry in self.extras["list"].split('||'):
				self.addItem(entry.replace(' |','|'))

	#needed
	def storeOptions(self):
		self.options["prefix"] = (self.widget.prefix.text(), "text")
		self.options["suffix"] = (self.widget.suffix.text(), "text")
		self.options["styleBox"] = (self.widget.styleBox.currentIndex(),
									"currentIndex")
		# for i in range(self.items):
		self.extras["list"] = '||'.join(self.widget.list.item(i).text()
			.replace('|',' |') for i in range(self.items))

	#override
	def generate(self):
		doc = QTextDocument()
		cursor = QTextCursor(doc)

		# Formats
		listFormat = QTextListFormat()
		listFormat.setIndent(1)
		listFormat.setStyle(-1 - self.widget.styleBox.currentIndex())
		listFormat.setNumberPrefix(self.fix[0])
		listFormat.setNumberSuffix(self.fix[1])

		# Items
		list = cursor.insertList(listFormat)
		for i in range(self.items):
			cursor.insertText(self.widget.list.item(i).text())
			if i < self.items-1:
				cursor.insertBlock()

		return doc

	def addItem(self, value="New Item"):
		item = QListWidgetItem(value)
		item.setFlags(item.flags() | Qt.ItemIsEditable)
		self.widget.list.addItem(item)
		self.items += 1

	def removeItem(self):
		self.widget.list.takeItem(self.widget.list.currentIndex().row())
		self.items -= 1

	def updateSelection(self,index):
		self.widget.removeItem.setEnabled(index >= 0)

	def updateFix(self):
		self.fix = (self.widget.prefix.text(),self.widget.suffix.text())

	def styleChanged(self,index):
		self.widget.fixWidget.setEnabled(index > 2)
		s = ['...','1','a','A','i','I']
		self.widget.label.setText(
			s[max(self.widget.styleBox.currentIndex()-2,0)])