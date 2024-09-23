import socket
import threading
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QTimer
from PyQt6 import uic
import random

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Мемо - игра для вас и ваших друзей")
        self.setWindowIcon(QIcon('pictures/icon.png'))

        # Подключение к серверу
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect(('127.0.0.1', 53210))  # Укажите IP сервера

        self.buttons_list = self.buttons.buttons()
        self.current_user = current_user  # 0 - клиент, 1 - сервер
        self.press_count = 0  # Количество нажатий
        self.prev_image = ''
        self.prev_button = ''

        for button in self.buttons_list:
            button.setIcon(QIcon('pictures/back.jpg'))
            button.setText('')
            button.setIconSize(QSize(button.width() - 8, button.height() - 8))
            button.clicked.connect(self.button_client_clicked)

        self.your_turn.setStyleSheet("""QPushButton{
                                        border: 5px solid #375;
                                        border-style: outset;
                                        background: rgb(60,150,90);
                                        color: rgb(250,250,255);
                                        }""")

        #threading.Thread(target=self.listen_to_server, daemon=True).start()

    def button_client_clicked(self):
        button = self.sender()

        # Отправляем информацию о кнопке на сервер
        button_info = f"{button.objectName()}"
        self.client_sock.sendall(button_info.encode('utf-8'))

        # Получаем путь к изображению от сервера и отображаем его
        data = self.client_sock.recv(1024)
        picture = data.decode('utf-8')
        button.setIcon(QIcon(picture))
        button.setIconSize(QSize(button.width() - 8, button.height() - 8))
        if self.press_count == 0:
            self.prev_image = picture
            self.prev_button = button
            self.press_count += 1
        else:
            if self.prev_image != picture:
                for btn in self.buttons_list:
                    btn.setEnabled(False)
                QTimer.singleShot(3000, lambda: self.lock_pictures(self.prev_button, button))

            else:
                self.prev_button.setStyleSheet("""QPushButton {
                                                        border: 5px solid #375;
                                                        border-style: outset;
                                                        color: black;
                                                        }""")
                button.setStyleSheet("""QPushButton {
                                                border: 5px solid #375;
                                                border-style: outset;
                                                color: black;
                                                }""")
            self.press_count = 0

    def lock_pictures(self, prev_button, current_button):
        prev_button.setIcon(QIcon('pictures/back.jpg'))
        current_button.setIcon(QIcon('pictures/back.jpg'))




if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow(0)  # 0 означает, что клиент ходит первым
    window.show()
    sys.exit(app.exec())
