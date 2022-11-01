"""This example demonstrates applying dark theme to PyQt2."""
import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton

import qdarktheme

app = QApplication(sys.argv)
main_win = QMainWindow()
push_button = QPushButton("PyQtDarkTheme!!")
main_win.setCentralWidget(push_button)

# Apply dark theme
app.setStyleSheet(qdarktheme.load_stylesheet())

main_win.show()

app.exec_()
