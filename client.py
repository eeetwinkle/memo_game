import socket
import sys

from PyQt6.QtWidgets import QApplication
from UI import MainWindow
def client():
    # Создаем сокет
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('10.193.146.41', 53210))
    # ненадолго перевернуть картинки
    current_user = 0

    try:
        while True:
            match current_user:
                case 0:
                    # Запрашиваем ввод сообщения от пользователя
                    message1 = input("1 фото: ")
                    # Отправляем сообщение серверу
                    client_sock.sendall(message1.encode('utf-8'))
                    message2 = input("2 фото: ")
                    client_sock.sendall(message2.encode('utf-8'))
                    if message1.image != message2.image:
                       current_user = 1

                case 1:
                    # Получаем ответ от сервера
                    data = client_sock.recv(1024)
                    response1 = data.decode('utf-8')
                    print(response1)
                    data = client_sock.recv(1024)
                    response2 = data.decode('utf-8')
                    print(response2)
                    # if response1.image != response2.image:
                    #   current_user = 0


    except (KeyboardInterrupt, SystemExit):
        print("Прерывание программы.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        client_sock.close()


if __name__ == "__main__":
    client()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic
import random
import socket
import threading

class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Мемо - игра для вас и ваших друзей")
        self.setWindowIcon(QIcon('pictures/icon.png'))

        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect(('10.193.146.41', 53210))

        for button in self.buttons.buttons():
            button.setIcon(QIcon('pictures/back.jpg'))
            button.setText('')
            button.setIconSize(QSize(button.width() - 6, button.height() - 6))
            button.clicked.connect(self.button_client_clicked)

        self.current_user = current_user
        self.press_count = 0
        self.game_active = True  # Игра активна для клиента
        threading.Thread(target=self.listen_to_server, daemon=True).start()


    def listen_to_server(self):
        while True:
            data = self.client_sock.recv(1024)
            pic = data.decode('utf-8')
            button, pic1 = pic.split()
            print(pic1)
            button.setIcon(f'{pic1}')

            data = self.client_sock.recv(1024)
            pic = data.decode('utf-8')
            button, pic2 = pic.split()
            print(pic)
            button.setIcon(f'{pic2}')

            if pic1 != pic2:
                break
            else:
                continue
                # прописать про смену цветов рамки и блокировку выигранных карт


    def button_client_clicked(self, current_user):
        if self.current_user == 0 and self.press_count < 2 and self.game_active:
            button = self.sender()
            self.press_count += 1

            button_name = button.objectName()
            self.client_sock.sendall(button_name.encode('utf-8'))
            data = self.client_sock.recv(1024)
            pic = data.decode('utf-8')
            button.setIcon(QIcon(f'{pic}'))

            if self.press_count == 2:
                self.current_user = 0
                self.game_active = False
                self.press_count = 0

                self.listen_to_server()






if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow(0)
    window.show()
    sys.exit(app.exec())
