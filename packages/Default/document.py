from arctool import ARCTool
from PyQt5.QtCore import QUrl, Qt, QStandardPaths
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from arc.arcpreferences import PreferenceManager as PM
import arc.arcclasses as arcclasses
import arc.arcgui as arcgui
import pypandoc

class Plugin(arcclasses.Plugin):

	def __init__(self,package):
		super(Plugin,self).__init__(None,package)

		self.__name__ = "document"
		# Required
		self.name = "Document"
		self.authors = ["unonu"]
		self.version = (0,0,1)
		self.description=("Inserts a document into the report. Supported file-"
			"types are docx, odt, html, rst, latex, epub and many types of "
			"markdown.")
		self.contexts = []

		self.path = ''
		self.preferenceDict = {
			'defaultpath' : {
				'label':'Default document path',
				'placeholder':QStandardPaths.standardLocations(
					QStandardPaths.DocumentsLocation)[0],
				'default':QStandardPaths.standardLocations(
					QStandardPaths.DocumentsLocation)[0],
				'type':'string',
				'tooltip':'Default path to document folder.'
			},
		}

	#needed
	def setupUi(self):
		self.widget.browseButton.clicked.connect(self.getPath)
		self.widget.lineEdit.textChanged.connect(self.setPath)

	#call super
	def update(self):
		super(Plugin,self).update()

		#updated from extras

	#needed
	def storeOptions(self):
		# self.options['logicBox'] =\
		# 	(self.widget.logicBox.text(),'text')
		pass


	#override
	def generate(self):
		doc = QTextDocument()
		cursor = QTextCursor(doc)
		if self.path != '':
			try:
				open(self.path).close()
			except:
				print("Couldn't open file at "+self.path)
				return None
		else:
			return None

		html = pypandoc.convert(self.path,'html',
								extra_args=['--email-obfuscation=none']
		)

		cursor.insertHtml(html)

		return doc

	def getPath(self):
		path = QFileDialog.getOpenFileName(
			None,"Choose Document",
			PM.getPreference('Default Package','defaultpath',self.__name__),
			("OpenDocument Text (*.odt);;OpenDocument XML (*.opml);;"
			+ "Microsoft Word Document 2007/2010/2013 (*.docx);;"
			+ "HTML (*.html);;LaTeX (*.latex);; EPUB (*.epub);;"
			+ "reStructuredText (*.rst);;Markdown (*.md)")
		)

		if path is not None:
			self.path = path[0]
			self.widget.lineEdit.setText(self.path)

	def setPath(self,text):
		self.path = text
