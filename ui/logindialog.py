# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logindialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoginDialog(object):
	def setupUi(self, LoginDialog):
		LoginDialog.setObjectName("LoginDialog")
		LoginDialog.resize(400, 133)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(LoginDialog.sizePolicy().hasHeightForWidth())
		LoginDialog.setSizePolicy(sizePolicy)
		LoginDialog.setModal(True)
		self.verticalLayout = QtWidgets.QVBoxLayout(LoginDialog)
		self.verticalLayout.setObjectName("verticalLayout")
		self.label = QtWidgets.QLabel(LoginDialog)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
		self.label.setSizePolicy(sizePolicy)
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		self.label.setObjectName("label")
		self.verticalLayout.addWidget(self.label)
		self.a = QtWidgets.QLineEdit(LoginDialog)
		self.a.setAlignment(QtCore.Qt.AlignCenter)
		self.a.setObjectName("a")
		self.verticalLayout.addWidget(self.a)
		self.b = QtWidgets.QLineEdit(LoginDialog)
		self.b.setEchoMode(QtWidgets.QLineEdit.Password)
		self.b.setAlignment(QtCore.Qt.AlignCenter)
		self.b.setObjectName("b")
		self.verticalLayout.addWidget(self.b)
		self.buttonBox = QtWidgets.QDialogButtonBox(LoginDialog)
		self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
		self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
		self.buttonBox.setObjectName("buttonBox")
		self.verticalLayout.addWidget(self.buttonBox)

		self.retranslateUi(LoginDialog)
		self.buttonBox.accepted.connect(LoginDialog.accept)
		self.buttonBox.rejected.connect(LoginDialog.reject)
		QtCore.QMetaObject.connectSlotsByName(LoginDialog)

	def retranslateUi(self, LoginDialog):
		_translate = QtCore.QCoreApplication.translate
		LoginDialog.setWindowTitle(_translate("LoginDialog", "Dialog"))
		self.label.setText(_translate("LoginDialog", "A Module needs your credentials in order to continue."))
		self.a.setPlaceholderText(_translate("LoginDialog", "Username"))
		self.b.setPlaceholderText(_translate("LoginDialog", "Password"))

