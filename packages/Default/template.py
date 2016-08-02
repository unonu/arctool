import arc.arcclasses as arcclasses
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Plugin(arcclasses.Plugin):
	def __init__(self,package):
		super(Plugin,self).__init__(None,package)

		self.__name__ = "template"
		self.name = "Template"
		self.authors = ["John Doe"]
		self.version = (0,0,1)
		self.description = "Template plugin which does nothing"
		self.contexts = []

		self.preferenceDict = {
			'tag' : {
				'label':'Option #1',
				'placeholder':'placeholder value',
				'type':'string',
				'tooltip':'This option is shown in the preference manager'
			},
		}

	def setupUi(self):
		pass

	def update(self):
		super(Plugin,self).update()

	def storeOptions(self):
		pass

	def generate(self):
		doc = QTextDocument()
		cursor = QTextCursor(doc)

		return doc