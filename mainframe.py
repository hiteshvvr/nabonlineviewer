from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
import pyqtgraph as pg
from mainwindow import MainWindow
from monitorwindow import Monitor
from flippingratio import Flipper
from mdata import MData



class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')

        self.tabs = QTabWidget()
        self.data = MData()
        self.tab1 = MainWindow(self.data)
        self.tab2 = Monitor(self.data)
        self.tab3 = Monitor(self.data)
        self.tab4 = Flipper()

        self.tabs.addTab(self.tab1, "Main Window")
        self.tabs.addTab(self.tab2, "First Monitor")
        self.tabs.addTab(self.tab3, "Second Monitor")
        self.tabs.addTab(self.tab4, "Flipping Ratio")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

