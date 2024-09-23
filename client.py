import socket
import threading
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
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
        self.game_active = True  # Игра активна для клиента
        #threading.Thread(target=self.handle_server, daemon=True).start()

    def button_client_clicked(self):
        if self.game_active:  # Если ход клиента и игра активна
            button = self.sender()

            # Отправляем информацию о кнопке на сервер
            button_info = f"{button.objectName()}"
            self.client_sock.sendall(button_info.encode('utf-8'))

            # Получаем путь к изображению от сервера и отображаем его
            data = self.client_sock.recv(1024)
            picture = data.decode('utf-8')
            print(picture)
            button.setIcon(QIcon(picture))
            button.setIconSize(QSize(button.width() - 8, button.height() - 8))

    def handle_server(self):
        try:
            while True:
                # Получаем информацию о нажатии кнопки от клиента
                data = self.client_sock.recv(1024)
                if not data:
                    break
                button_name = data.decode('utf-8')
                data = self.client_sock.recv(1024)
                if not data:
                    break
                picture = data.decode('utf-8')
                button = self.findChild(QPushButton, button_name)
                print(f"Button {button_name} pressed, displaying picture {picture}")

                button.setIcon(QIcon(picture))

                # Сервер также обновляет свою версию интерфейса
                #print(f"Button {button_name} pressed, displaying picture {picture}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.client_sock.close()  # Закрываем соединение

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow(0)  # 0 означает, что клиент ходит первым
    window.show()
    sys.exit(app.exec())
