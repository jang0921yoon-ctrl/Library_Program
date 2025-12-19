#main.py
from PySide6.QtWidgets import QApplication
from widget import Widget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec())