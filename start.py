import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle("My App")
window.resize(300, 200)

button = QPushButton("Click Me", window)
button.move(100, 80)

window.show()
app.exec()
