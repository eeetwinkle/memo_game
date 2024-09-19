from PyQt6.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Мемо - игра для вас и ваших друзей")
        self.setWindowIcon(QIcon('pictures/icon.png'))

        pictures = [f"pictures/{i + 1}.jpg" for i in range(15)]
        random.shuffle(pictures)

        new_buttons = self.buttons.buttons()
        print(new_buttons)
        random.shuffle(new_buttons)
        for i in range(15):
            for k in range(2):
                button = new_buttons[i * 2 + k]
                button.setIcon(QIcon('pictures/back.jpg'))
                button.setText('')
                button.setIconSize(QSize(button.width()-6, button.height()-6))
                button.setProperty('picture', pictures[i])
                button.clicked.connect(self.change_image)

        for button in self.buttons.buttons():
            print(f"Button {button.objectName()} has picture {button.property('picture')}")

    def change_image(self):
        button = self.sender()
        button.setIcon(QIcon(f"{button.property('picture')}"))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())