import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Морской бой')
        self.setGeometry(400, 200, 600, 400)
        self.setWindowIcon(QIcon('pictures\icon.jpg'))
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MyApp()
    main_window.show()
    sys.exit(app.exec())