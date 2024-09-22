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

        self.buttons_list = self.buttons.buttons()
        self.current_user = current_user  # 0 - клиент, 1 - сервер
        self.press_count = 0  # Количество нажатий

        # Присваиваем кнопкам случайные картинки
        pictures = [f'pictures/{i + 1}.jpg' for i in range(15)]
        self.buttons = self.buttons.buttons()
        random.shuffle(pictures)
        random.shuffle(self.buttons)
        for i in range(15):
            for k in range(2):
                button = self.buttons[i * 2 + k]
                button.setIcon(QIcon('pictures/back.jpg'))
                button.setText('')
                print(button.objectName(), pictures[i])
                button.setIconSize(QSize(button.width() - 8, button.height() - 8))
                button.setProperty('picture', pictures[i])
                # button.clicked.connect(self.button_clicked)
        self.enemys_turn.setStyleSheet("""QPushButton{
                                    border: 5px solid #721;
                                    border-style: outset;
                                    background: rgb(180,50,40);
                                    color: rgb(250,250,255);
                                    }""")

        # Подключение к серверу
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('', 53210))  # Укажите IP сервера, если нужно
        self.server_sock.listen(1)
        print('Server is running')

        self.client_sock, self.client_addr = self.server_sock.accept()
        print('Client connected', self.client_addr)

        self.game_active = True  # Игра активна для клиента
        threading.Thread(target=self.handle_client, daemon=True).start()

    def handle_client(self):
        try:
            while True:
                # Получаем информацию о нажатии кнопки от клиента
                data = self.client_sock.recv(1024)
                if not data:
                    break
                button_name = data.decode('utf-8')
                button = self.findChild(QPushButton, button_name)
                # Генерируем путь к изображению
                picture_path = button.property('picture')

                # Отправляем информацию клиенту для синхронного открытия
                self.client_sock.sendall(picture_path.encode('utf-8'))

                # Сервер также обновляет свою версию интерфейса
                print(f"Button {button_name} pressed, displaying picture {picture_path}")
                self.update_server_interface(button_name, picture_path)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.client_sock.close()  # Закрываем соединение

    def update_server_interface(self, button_name, picture_path):
        button = self.findChild(QPushButton, button_name)
        button.setIcon(QIcon(picture_path))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow(0)  # 0 означает, что клиент ходит первым
    window.show()
    sys.exit(app.exec())


