import arc.arcclasses as arcclasses
from arctool import ARCTool
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from Default.textedit import TextEditor

class Plugin(arcclasses.Plugin):	
	def __init__(self,package):
		super(Plugin,self).__init__(None,package)

		self.__name__ = "richtext"
		self.name = "Text" # Required
		self.authors = ["unonu"] # Required
		self.version = (0,0,1) # Required
		self.description = "Creates a portion of rich text." # Required
		self.contexts = [] # Required

	#needed
	def setupUi(self):
		self.widget = TextEditor()
		self.widget.textChanged.connect(ARCTool.signalProfileChanged)

	#call super
	def update(self):
		super(Plugin,self).update()
		if self.extras["document"]:
			self.widget.setHtml(self.extras["document"])

	#needed
	def storeOptions(self):
		self.extras["document"] = self.widget.toHtml()

	#override
	def generate(self):
		doc = QTextDocument()
		cursor = QTextCursor(doc)

		cursor.insertFragment(QTextDocumentFragment(self.widget.document()))
		
		return doc