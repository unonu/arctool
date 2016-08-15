from PyQt5.QtCore import QStandardPaths, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QFormLayout, QLineEdit, QSizePolicy,
	QCheckBox, QSpinBox, QComboBox, QDialog, QTreeWidgetItem)
from ui.preferencedialog import Ui_PreferenceDialog
from .arcgui import PluginSelectDialog as PSD
import arctool
import os

class PreferenceManager(QDialog):
	preferenceChanged = pyqtSignal([str,str])
	preferences = {}
	ui = Ui_PreferenceDialog()
	__init = False

	def __init__(self,parent):
		super(PreferenceManager,self).__init__(parent)
		if not PreferenceManager.__init:
			PreferenceManager.ui.setupUi(self)
			PreferenceManager.ui.buttonBox.accepted.connect(
				PreferenceManager.storeForm
			)
			PreferenceManager.ui.buttonBox.rejected.connect(
				lambda: (PreferenceManager.loadPreferences(),
					PreferenceManager.updateForm() )
			)
			PreferenceManager.ui.treeWidget.currentItemChanged.connect(
				PreferenceManager.updateForm
			)
			for k in sorted(PSD.getPackageNames()):
				PreferenceManager.preferences[k] = {
					'':PSD.getPackage(k).preferenceDict or {}
				}
				twi = QTreeWidgetItem()
				twi.setText(0,k)
				for m in sorted(PSD.getPluginNames(k)):
					PreferenceManager.preferences[k][m] =\
						PSD.getPluginInfo(k,m).getPreferenceDict()
					child = QTreeWidgetItem()
					child.setText(0,m)
					twi.addChild(child)

				PreferenceManager.ui.treeWidget.addTopLevelItem(twi)
			PreferenceManager.__init = True

		PreferenceManager.loadPreferences()
		PreferenceManager.ui.treeWidget.sortItems(0,0)
		PreferenceManager.ui.treeWidget.setCurrentItem(
			PreferenceManager.ui.treeWidget.itemAt(0,0)
		)
		PreferenceManager.updateForm()

	@staticmethod
	def getPreference(package,name,sub=''):
		if (package not in PreferenceManager.preferences or
			sub not in PreferenceManager.preferences[package] or
			name not in PreferenceManager.preferences[package][sub] or
			'value' not in PreferenceManager.preferences[package][sub][name]):
			return None
		return PreferenceManager.preferences[package][sub][name]['value'] \
			or None

	@staticmethod
	def setPreference(package,name,value,sub=''):
		if (package not in PreferenceManager.preferences or
			sub not in PreferenceManager.preferences[package] or
			name not in PreferenceManager.preferences[package][sub]):
			return
		PreferenceManager.preferences[package][sub][name] = value

	@staticmethod
	def updateForm():
		item = PreferenceManager.ui.treeWidget.currentItem()
		child = True if item.parent() else False
			
		package = None
		if child:	
			package = PreferenceManager.preferences[item.parent().text(0)]\
												   [item.text(0)]
		else:
			package = PreferenceManager.preferences[item.text(0)]['']
		# PreferenceManager.storeForm(False)
		PreferenceManager.ui.formWidget.setParent(None)
		PreferenceManager.ui.horizontalLayout.removeWidget(
			PreferenceManager.ui.formWidget
		)
		PreferenceManager.ui.formWidget = QWidget()
		PreferenceManager.ui.formWidget.setSizePolicy(
			QSizePolicy.Expanding,QSizePolicy.Expanding
		)
		form = QFormLayout()
		for k in sorted(package.keys()):
			params = package[k]
			w = None
			if params['type'] == 'string':
				w = QLineEdit()
				# print(params)
				w.setText(
					params['value'] if ('value' in params and params['value'])
					else params['default'] if 'default' in params 
					else ''
				)
				w.setPlaceholderText(
					params['placeholder'] if 'placeholder' in params 
					else ''
				)
				w.textEdited.connect(
					lambda: PreferenceManager.storeForm(False))
			elif params['type'] == 'check':
				w = QCheckBox()
				w.setChecked(
					bool(params['value'] if ('value' in params and
											 params['value']) 
					else params['default'] if 'default' in params 
					else False)
				)
				w.toggled.connect(lambda: PreferenceManager.storeForm(False))
			elif params['type'] == 'number':
				w = QSpinBox()
				w.setValue(
					int(params['value'] if ('value' in params and
											params['value']) 
					else params['default'] if 'default' in params 
					else 0)
				)
				w.valueChanged.connect(
					lambda: PreferenceManager.storeForm(False))
			elif params['type'] == 'choice':
				w = QComboBox()
				w.setItems(
					[
						x for x in (params['placeholder'].split(',') 
						if 'placeholder' in params else '--')
					]
				)
				w.setIndex(
					int(params['value'] if ('value' in params and
											params['value']) 
					else params['default'] if 'default' in params 
					else 0)
				)
				w.currentIndexChanged.connect(
					lambda: PreferenceManager.storeForm(False))

			w.setToolTip(params['tooltip'] if 'tooltip' in params else '')
			w.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum)
			params['widget'] = w
			form.addRow(params['label'],w)
		form.update()
		PreferenceManager.ui.formWidget.setLayout(form)
		PreferenceManager.ui.horizontalLayout.addWidget(
			PreferenceManager.ui.formWidget
		)
		PreferenceManager.ui.horizontalLayout.update()

	@staticmethod
	def storeForm(save=True):
		package = None
		item = PreferenceManager.ui.treeWidget.currentItem()
		child = True if item.parent() else False

		if child:	
			package = PreferenceManager.preferences[item.parent().text(0)]\
												   [item.text(0)]
		else:
			package = PreferenceManager.preferences[item.text(0)]['']

		# print(package)

		for k in sorted(package.keys()):
			# print(k)
			params = package[k]
			if 'widget' in params:
				params['value'] = {
					'string': lambda: params['widget'].text(),
					'check': lambda: params['widget'].isChecked(),
					'number': lambda: params['widget'].value(),
					'choice': lambda: params['widget'].currentText()
				}[params['type']]()
		# print(package)
		if save:
			PreferenceManager.savePreferences()

	@staticmethod
	def savePreferences():
		prefs = ''
		for p in PreferenceManager.preferences:
			for s in PreferenceManager.preferences[p]:
				for k in sorted(PreferenceManager.preferences[p][s].keys()):
					params = PreferenceManager.preferences[p][s][k]
					# print(params['type'])
					prefs += ('package=%s\xa0subpackage=%s\xa0name=%s\xa0label'
							 '=%s\xa0type=%s\xa0value=%s\xa0default=%s\xa0p'
							 'laceholder=%s\xa0tooltip=%s\n') %(
							 str(p),
							 str(s),
							 str(k),
							 str(params['label']),
							 str(params['type']),
							 str({
								'string': lambda: params['value'],
								'check': lambda: int(params['value']),
								'number': lambda: params['value'],
								'choice': lambda: params['value']
							 }[params['type']]())\
							 	if 'value' in params else '',
							 str(params['default'])\
							 	if 'default' in params else '',
							 str(params['placeholder'])\
							 	if 'placeholder' in params else '',
							 str(params['tooltip'])\
							 	if 'tooltip' in params else ''
					)

		path = arctool.ARCTool.getStoragePath()
		f = open(os.path.join(path,'config'),'w')
		f.write(prefs)
		f.close()

	@staticmethod
	def loadPreferences():
		path = arctool.ARCTool.getStoragePath()
		prefs = open(os.path.join(path,'config'),'r')
		for l in prefs:
			if '=' not in l:
				continue
			data = dict(
				[
					(x.split('=',1)[0], x.split('=',1)[1])\
					for x in l.strip().split('\xa0')
				]
			)
			PreferenceManager.preferences[data['package']]\
										 [data['subpackage']]\
										 [data['name']] = {
				'label': data['label'],
				'type': data['type'],
				'value': {
					'string': str,
					'check': lambda x: bool(int(x)),
					'number': int,
					'choice': int
				}[data['type']](data['value'])\
					if data['value'] != '' else None,
				'default': data['default']\
					if data['default'] != '' else None,
				'placeholder': data['placeholder']\
					if data['placeholder'] != '' else None,
				'tooltip': data['tooltip']\
					if data['tooltip'] != '' else None
			}