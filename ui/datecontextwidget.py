# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'datecontextwidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DateContextWidget(object):
	def setupUi(self, DateContextWidget):
		DateContextWidget.setObjectName("DateContextWidget")
		DateContextWidget.resize(379, 27)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(DateContextWidget.sizePolicy().hasHeightForWidth())
		DateContextWidget.setSizePolicy(sizePolicy)
		self.horizontalLayout = QtWidgets.QHBoxLayout(DateContextWidget)
		self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
		self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
		self.horizontalLayout.setSpacing(0)
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.checkBegin = QtWidgets.QCheckBox(DateContextWidget)
		self.checkBegin.setObjectName("checkBegin")
		self.horizontalLayout.addWidget(self.checkBegin)
		self.dateBegin = QtWidgets.QDateEdit(DateContextWidget)
		self.dateBegin.setCalendarPopup(True)
		self.dateBegin.setObjectName("dateBegin")
		self.horizontalLayout.addWidget(self.dateBegin)
		self.checkEnd = QtWidgets.QCheckBox(DateContextWidget)
		self.checkEnd.setObjectName("checkEnd")
		self.horizontalLayout.addWidget(self.checkEnd)
		self.dateEnd = QtWidgets.QDateEdit(DateContextWidget)
		self.dateEnd.setCalendarPopup(True)
		self.dateEnd.setObjectName("dateEnd")
		self.horizontalLayout.addWidget(self.dateEnd)

		self.retranslateUi(DateContextWidget)
		QtCore.QMetaObject.connectSlotsByName(DateContextWidget)

	def retranslateUi(self, DateContextWidget):
		_translate = QtCore.QCoreApplication.translate
		self.checkBegin.setText(_translate("DateContextWidget", "Beginning Date"))
		self.checkEnd.setText(_translate("DateContextWidget", "Ending Date"))

