from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6 import uic
import random
import socket
import threading

def server():
    # Создаем сокет
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    serv_sock.bind(('', 53210))
    serv_sock.listen(1)
    current_user = 0

    try:
        while True:
            # Бесконечно обрабатываем входящие подключения
            client_sock, client_addr = serv_sock.accept()

            print('client connected', client_addr)
            # карточки ненадолго переворачиваются
            while True:
                match current_user:
                    case 0:
                        # Получаем сообщение от клиента
                        data = client_sock.recv(1024)
                        if not data:  # Клиент отключился
                            break
                        message1 = data.decode('utf-8')
                        print(message1)

                        data = client_sock.recv(1024)
                        if not data:  # Клиент отключился
                            break
                        message2 = data.decode('utf-8')
                        print(message2)
                        # if message1.image != message2.image:
                        #   current_user = 1

                    case 1:
                        # Отправляем сообщение клиенту
                        response1 = input()
                        client_sock.sendall(response1.encode('utf-8'))
                        response2 = input()
                        client_sock.sendall(response2.encode('utf-8'))
                        # заблокировать все кнопки для нажатия, если неправильно
                        # картинки открыть если правильно и продолжать отсылать
                        # if response1.image != response2.image:
                        #   current_user = 0

            client_sock.close()

    except (KeyboardInterrupt, SystemExit):
        print('Прерывание программы.')

    except Exception as e:
        print(f'Произошла ошибка: {e}')



class MainWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        # Загрузить пользовательский интерфейс главного окна из файла .ui
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Мемо - игра для вас и ваших друзей")
        self.setWindowIcon(QIcon('pictures/icon.png'))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
        self.sock.bind(('', 55000))  # связываем сокет с портом, где он будет ожидать сообщения
        self.sock.listen(1)  # указываем сколько может сокет принимать соединений
        print('Server is running')

        pictures = [f'pictures/{i + 1}.jpg' for i in range(15)]
        random.shuffle(pictures)

        new_buttons = self.buttons.buttons()
        random.shuffle(new_buttons)
        self.slots = {}
        for i in range(15):
            for k in range(2):
                button = new_buttons[i * 2 + k]
                button.setIcon(QIcon('pictures/back.jpg'))
                button.setText('')
                button.setIconSize(QSize(button.width() - 6, button.height() - 6))
                button.setProperty('picture', pictures[i])
                button.clicked.connect(self.button_clicked)

        #for button in self.buttons.buttons():
        #    print(f"Button {button.objectName()} has picture {button.property('picture')}")

    def button_clicked(self, current_user):
        button = self.sender()
        button.setIcon(QIcon(f"{button.property('picture')}"))


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow(0)
    window.show()
    sys.exit(app.exec())
