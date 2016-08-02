# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferencedialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PreferenceDialog(object):
	def setupUi(self, PreferenceDialog):
		PreferenceDialog.setObjectName("PreferenceDialog")
		PreferenceDialog.resize(400, 300)
		self.verticalLayout = QtWidgets.QVBoxLayout(PreferenceDialog)
		self.verticalLayout.setObjectName("verticalLayout")
		self.horizontalLayout = QtWidgets.QHBoxLayout()
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.treeWidget = QtWidgets.QTreeWidget(PreferenceDialog)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
		self.treeWidget.setSizePolicy(sizePolicy)
		self.treeWidget.setObjectName("treeWidget")
		self.treeWidget.header().setVisible(False)
		self.horizontalLayout.addWidget(self.treeWidget)
		self.formWidget = QtWidgets.QWidget(PreferenceDialog)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.formWidget.sizePolicy().hasHeightForWidth())
		self.formWidget.setSizePolicy(sizePolicy)
		self.formWidget.setObjectName("formWidget")
		self.formLayout = QtWidgets.QFormLayout(self.formWidget)
		self.formLayout.setContentsMargins(0, 0, 0, 0)
		self.formLayout.setObjectName("formLayout")
		self.horizontalLayout.addWidget(self.formWidget)
		self.horizontalLayout.setStretch(1, 2)
		self.verticalLayout.addLayout(self.horizontalLayout)
		self.buttonBox = QtWidgets.QDialogButtonBox(PreferenceDialog)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName("buttonBox")
		self.verticalLayout.addWidget(self.buttonBox)

		self.retranslateUi(PreferenceDialog)
		self.buttonBox.accepted.connect(PreferenceDialog.accept)
		self.buttonBox.rejected.connect(PreferenceDialog.reject)
		QtCore.QMetaObject.connectSlotsByName(PreferenceDialog)

	def retranslateUi(self, PreferenceDialog):
		_translate = QtCore.QCoreApplication.translate
		PreferenceDialog.setWindowTitle(_translate("PreferenceDialog", "Dialog"))
		self.treeWidget.setSortingEnabled(True)
		self.treeWidget.headerItem().setText(0, _translate("PreferenceDialog", "1"))

