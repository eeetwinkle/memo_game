import socket
import threading
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QTimer, pyqtSignal
from PyQt6 import QtWidgets, uic
import random
import time


class AwaitingWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('AwaitingWindow.ui', self)
        self.setWindowTitle('Мемо - игра для вас и ваших друзей')
        self.setWindowIcon(QIcon('pictures/back.jpg'))


class MainWindow(QMainWindow):
    # Сигнал для уведомления об успешном подключении
    connection_successful = pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle('Мемо - игра для вас и ваших друзей')
        self.setWindowIcon(QIcon('pictures/back.jpg'))

        self.buttons_list = self.buttons.buttons()
        # Счетчики для проверки выигрышных ходов
        self.press_count = 0
        self.prev_image = ''
        self.prev_button = ''
        self.enemy_press_count = 0
        self.prev_enemy_image = ''
        self.prev_enemy_button = ''
        self.my_score = 0
        self.opponent_score = 0

        # Присваиваем кнопкам случайные картинки
        pictures = [f'pictures/girls/{i + 1}.jpg' for i in range(15)]
        self.buttons = self.buttons.buttons()
        random.shuffle(pictures)
        random.shuffle(self.buttons)
        # Выставляем картинки парами
        for i in range(15):
            for k in range(2):
                button = self.buttons[i * 2 + k]
                button.setIcon(QIcon('pictures/back.jpg'))
                button.setText('')

                print(button.objectName(), pictures[i])
                button.setIconSize(QSize(button.width() - 8, button.height() - 8))
                button.setProperty('picture', pictures[i])

                button.clicked.connect(self.button_server_clicked)
                button.setEnabled(False)

        # Сейчас ход противника
        self.enemys_turn.setStyleSheet('''QPushButton{
                                    border: 5px solid #721;
                                    border-style: outset;
                                    background: rgb(180,50,40);
                                    color: rgb(250,250,255);
                                    }''')

        #self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server_sock.bind(('', 53211))
        #self.server_sock.listen(1)
        #print('Server is running')

        # Открываем сокет для отправки и приема
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('', 53210))
        self.server_sock.listen(1)
        self.client_sock = None
        # Запускаем трансляцию сообщения для всех пользователей локальной сети

        #self.start_server()
        self.connection_successful.connect(self.on_connection_successful)

        #self.client_sock, self.client_addr = self.server_sock.accept()
        #print('Client connected', self.client_addr)

        # Открываем поток для прослушивания ходов противника
        #self.stop_event = threading.Event()
        #threading.Thread(target=self.handle_client, daemon=True).start()


    def broadcast_ip(self):
        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Определяем IP сервера в локальной сети
        server_ip = socket.gethostbyname(socket.gethostname())
        broadcast_message = f'SERVER_IP:{server_ip}'.encode('utf-8')
        while not self.broadcast_event.is_set():
            broadcast_sock.sendto(broadcast_message, ('<broadcast>', 37021))
            print(f'Broadcasting server IP: {server_ip}')
            # Отправляем сообщение каждые 2 секунды
            self.broadcast_event.wait(1)


    def start_server(self):
        self.broadcast_event = threading.Event()
        awaiting_window.label.setText('Looking for the client...')
        print('Server is running, broadcasting IP for client discovery...')

        # Запуск широковещательной трансляции
        self.broadcast_thread = threading.Thread(target=self.broadcast_ip, daemon=True)
        self.broadcast_thread.start()

        # Ожидание подключения клиента
        self.client_sock, client_addr = self.server_sock.accept()
        awaiting_window.label.setText(f'Client connected from {client_addr}')
        print(f'Client connected from {client_addr}')
        time.sleep(1)

        # Остановка трансляции IP
        self.broadcast_event.set()
        if self.broadcast_thread.is_alive():
            self.broadcast_thread.join()

        print('Broadcasting stopped.')
        self.connection_successful.emit()


    def on_connection_successful(self):
        # Закрываем окно ожидания и показываем главное окно
        self.awaiting_window.close()
        self.show()

        # Логика для обработки клиента
        self.stop_event = threading.Event()
        # Запускаем поток приема ходов клиента
        threading.Thread(target=self.handle_client, daemon=True).start()


    def handle_client(self):
        try:
            # Принимаем данные от клиента до тех пор, пока не произойдет событие для выхода
            while not self.stop_event.is_set():
                data = self.client_sock.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                #print(message)

                if message == 'end':
                    self.stop_tread()
                    break

                button_name, special_simbol = message.split('|')
                # Смотрим картинку у кнопки из запроса клиента
                button = self.findChild(QPushButton, button_name)
                picture = button.property('picture')
                picture_info = f'{button_name}|{picture}'
                self.client_sock.sendall(picture_info.encode('utf-8'))

                self.update_server_interface(button, picture, 'r')

                # Проверяем ход противника на наличие выигрыша
                if self.enemy_press_count == 0:
                    button.setEnabled(False)
                    self.prev_enemy_button = button
                    self.prev_enemy_image = picture
                    self.enemy_press_count += 1
                else:
                    if self.prev_enemy_image != picture:
                        for btn in self.buttons_list:
                            btn.setEnabled(False)
                        time.sleep(1)

                        self.update_server_interface(self.prev_enemy_button, 'pictures/back.jpg', 'b')
                        self.update_server_interface(button, 'pictures/back.jpg', 'b')
                    else:
                        self.opponent_score += 1
                        self.score.setText(str(self.my_score) + ':' + str(self.opponent_score))

                        self.update_button_color(self.prev_enemy_button, 'r')
                        # После удачного хода кнопки не вызывают никакую функцию
                        self.prev_enemy_button.disconnect()
                        self.update_button_color(button, 'r')
                        button.disconnect()

                        if self.opponent_score + self.my_score == 15:
                            if self.opponent_score > self.my_score:
                                self.i_lose()
                            else:
                                self.i_win()

                    self.enemy_press_count = 0

        except Exception as e:
            print(f'An error occurred: {e}')


    def start_tread(self):
        # Запускаем поток
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.handle_client, daemon=True)
            self.thread.start()
            self.enemys_turn.setStyleSheet('''QPushButton{
                                                    border: 5px solid #721;
                                                    border-style: outset;
                                                    background: rgb(180,50,40);
                                                    color: rgb(250,250,255);
                                                    }''')
            self.your_turn.setStyleSheet('''QPushButton {
                                                    border: 5px solid #375;
                                                    border-style: outset;
                                                    color: black;
                                                    }''')
            #print('Поток запущен.')


    def stop_tread(self):
        # Завершаем поток
        if self.thread is not None:
            self.stop_event.set()
            self.thread = None
            #print('Поток остановлен.')
            self.enemys_turn.setStyleSheet('''QPushButton {
                                                    border: 5px solid #832;
                                                    border-style: outset;
                                                    color: black;
                                                    }''')
            self.your_turn.setStyleSheet('''QPushButton{
                                                border: 5px solid #375;
                                                border-style: outset;
                                                background: rgb(60,150,90);
                                                color: rgb(250,250,255);
                                                }''')
            for btn in self.buttons_list:
                btn.setEnabled(True)

    def button_server_clicked(self):
        button = self.sender()
        picture = button.property('picture')

        button_info = f'{button.objectName()}|{picture}'
        self.client_sock.sendall(button_info.encode('utf-8'))
        button.setIcon(QIcon(picture))

        # Если ход четный, то проверяемм условие выигрышности
        if self.press_count == 0:
            button.disconnect()
            self.prev_image = picture
            self.prev_button = button
            self.press_count += 1
        else:
            if self.prev_image != picture:
                self.prev_button.clicked.connect(self.button_server_clicked)
                for btn in self.buttons_list:
                    btn.setEnabled(False)
                self.client_sock.sendall('end'.encode('utf-8'))

                # Запускаем поток приема информации
                self.start_tread()
                # Закрываем карточки
                QTimer.singleShot(1000, lambda: self.lock_pictures(self.prev_button, button))

            else:
                self.my_score += 1
                self.score.setText(str(self.my_score) + ':' + str(self.opponent_score))

                self.update_button_color(self.prev_button, 'g')
                #self.prev_button.disconnect()
                self.update_button_color(button, 'g')
                #button.disconnect()

                if self.opponent_score + self.my_score == 15:
                    if self.opponent_score > self.my_score:
                        self.i_lose()
                    else:
                        self.i_win()

            self.press_count = 0


    def lock_pictures(self, prev_button, current_button):
        prev_button.setIcon(QIcon('pictures/back.jpg'))
        current_button.setIcon(QIcon('pictures/back.jpg'))


    def update_server_interface(self, button, picture_path, color):
        button.setIcon(QIcon(picture_path))
        self.update_button_color(button, color)

    def update_button_color(self, button, color):
        style = ''
        if color == 'r':
            style = '''QPushButton {
                                    border: 5px solid #832;
                                    border-style: outset;
                                    color: black;
                                    }'''
        elif color == 'g':
            style = '''QPushButton {
                                    border: 5px solid #375;
                                    border-style: outset;
                                    color: black;
                                    }'''

        else:
            style = '''QPushButton {
                                    border: 5px solid #357;
                                    border-style: outset;
                                    }'''

        button.setStyleSheet(style)


    def i_lose(self):
        self.label.setText('You lose')
        self.label.setStyleSheet('''font-size: 90px;
                                 color: rgb(255,0,0);''')
        for button in self.buttons_list:
            self.update_button_color(button, 'r')

    def i_win(self):
        self.label.setText('You win')
        self.label.setStyleSheet('''font-size: 90px;
                                 color: rgb(255,0,0);''')
        for button in self.buttons_list:
            self.update_button_color(button, 'g')

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    awaiting_window = AwaitingWindow()
    awaiting_window.show()
    main_window = MainWindow()
    # Передаем ссылку на окно ожидания
    main_window.awaiting_window = awaiting_window

    # Создаем поток для подключения к серверу
    connection_thread = threading.Thread(target=main_window.start_server)
    connection_thread.start()

    sys.exit(app.exec())