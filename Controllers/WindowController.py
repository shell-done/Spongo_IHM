from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

import Resources.Resources

from Models.Parameters import Parameters
from Controllers.MenuController import MenuController
from Controllers.ParametersController import ParametersController
from Controllers.AnalysisController import AnalysisController

class WindowController(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spongo")
        self.setFixedSize(1400, 750)
        self.setWindowIcon(QIcon(":/img/icon.png"))

        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.menu = MenuController()
        self.parameters = ParametersController()
        self.analysis = AnalysisController()

        self.stackedWidget.addWidget(self.menu)
        self.stackedWidget.addWidget(self.parameters)
        self.stackedWidget.addWidget(self.analysis)

        self.stackedWidget.setCurrentWidget(self.menu)

        self.menu.clickedChangeWidget.connect(self.changeWidget)
        self.parameters.clickedChangeWidget.connect(self.changeWidget)
        self.parameters.clickedChangeToAnalysisWidget.connect(self.changetoAnalysisWidget)
        self.analysis.clickedChangeWidget.connect(self.changeWidget)

        self.show()

    @pyqtSlot(Parameters, list)
    def changetoAnalysisWidget(self, parameters, images):
        current_widget = self.stackedWidget.currentWidget()
        current_widget.stop()

        self.stackedWidget.setCurrentWidget(self.analysis)
        self.analysis.start(parameters, images)

    @pyqtSlot(str)
    def changeWidget(self, nameWidget):
        next_widget = None
        if(nameWidget == "MENU"):
            next_widget = self.menu
        if(nameWidget == "PARAMETERS"):
            next_widget = self.parameters

        if next_widget is None:
            print("[WARNING] Unknown widget : %s" % str(next_widget))
            return
        
        current_widget = self.stackedWidget.currentWidget()
        current_widget.stop()

        self.stackedWidget.setCurrentWidget(next_widget)
        next_widget.start()

