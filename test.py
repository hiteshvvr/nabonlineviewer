# import sys
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import QPalette

# if __name__ == "__main__":
#     app = QApplication([])
#     app.setStyle("Fusion")
    
#     qp = QPalette()
#     qp.setColor(QPalette.ButtonText, Qt.black)
#     qp.setColor(QPalette.Window, Qt.black)
#     qp.setColor(QPalette.Button, Qt.gray)
#     app.setPalette(qp)

#     w = QWidget()

#     grid = QGridLayout(w)
#     grid.addWidget(QPushButton("Button one"),0,0)
#     grid.addWidget(QPushButton("Button two"),0,1)
#     grid.addWidget(QPushButton("Button three"),1,0)
#     grid.addWidget(QPushButton("Button four"),1,1)


#     w.show()
#     sys.exit(app.exec_())
import numpy as np
aa = []
# aa = np.random.randint(0,100)
for i in range(99):
    aa.append(np.random.randint(997655))
aa = np.array(aa)
kk = np.array([5,8,12,23])
print(aa[[2,3,22]])
print(aa[kk])
# print(aa[2,3,4,12])