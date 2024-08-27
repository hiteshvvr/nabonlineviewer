from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
import pyqtgraph as pg
from mainwindow import MainWindow
from mdata import MData
from topdetector import TopDetector 
from bottomdetector import BottomDetector
from analysis import Analysis



class MainFrame(QWidget):
    def __init__(self, parent) -> None:
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        pg.setConfigOption('background', 'w')

        self.data = MData()

        self.tabs = QTabWidget()
        self.tab1 = MainWindow(self.data)
        self.tab2 = TopDetector(self.data)
        self.tab3 = BottomDetector(self.data)
        self.tab4 = Analysis(self.data)


        self.tabs.addTab(self.tab1, "Main Window")
        self.tabs.addTab(self.tab2, "Top Detector")
        self.tabs.addTab(self.tab3, "Bottom Detector")
        self.tabs.addTab(self.tab4, "Analysis")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

