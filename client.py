import socket
import threading
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QTimer, pyqtSignal
from PyQt6 import uic
import random
import time
import os

class AwaitingWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/AwaitingWindow.ui', self)
        self.setWindowTitle('Мемо - игра для вас и ваших друзей')
        self.setWindowIcon(QIcon('pictures/back.jpg'))


class MainWindow(QMainWindow):
    # Сигнал для уведомления об успешном подключении
    connection_successful = pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/MainWindow.ui', self)
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

        # Ставим начальные картинки на все кнопки
        for button in self.buttons_list:
            button.setIcon(QIcon('pictures/back.jpg'))
            button.setText('')
            button.setIconSize(QSize(button.width() - 8, button.height() - 8))
            button.clicked.connect(self.button_client_clicked)

        # Настраиваем стиль для хода игрока
        self.your_turn.setStyleSheet('''QPushButton{
                                                    border: 5px solid #375;
                                                    border-style: outset;
                                                    background: rgb(60,150,90);
                                                    color: rgb(250,250,255);
                                                    }''')

        # Инициализация сокета
        self.server_ip = None
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Привязываем сигнал успешного подключения
        self.connection_successful.connect(self.on_connection_successful)


    def connect_to_server(self):
        # Открываем юпд сокет для отловки сигнала трансляции
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.bind(('', 37021))

        awaiting_window.label.setText('Looking for the server...')
        print('Looking for the server...')

        while not self.server_ip:
            data, addr = udp_sock.recvfrom(1024)
            message = data.decode('utf-8')
            if message.startswith('SERVER_IP:'):
                self.server_ip = message.split(':')[1]
                awaiting_window.label.setText(f'Server IP found: {self.server_ip}')
                print(f'Server IP found: {self.server_ip}')
                time.sleep(1)

        if self.server_ip:
            self.client_sock.connect((self.server_ip, 53210))
            awaiting_window.label.setText('Connected to server')
            print('Connected to server')

            # Генерируем сигнал об успешном подключении
            self.connection_successful.emit()


    def on_connection_successful(self):
        # Закрываем окно ожидания и показываем главное окно
        self.awaiting_window.close()
        self.show()

        # Задаем условие выхода из потока для приема ходов противника
        self.stop_event = threading.Event()
        self.thread = None


    def button_client_clicked(self):
            button = self.sender()

            # Отправляем информацию о кнопке на сервер
            button_info = f'{button.objectName()}|?'
            self.client_sock.sendall(button_info.encode('utf-8'))

            data = self.client_sock.recv(1024)
            btn, picture = data.decode('utf-8').split('|')
            self.update_button(button, picture, 'b')

            # Если ход четный, то проверяемм условие выигрышности
            if self.press_count == 0:
                button.disconnect()
                self.prev_image = picture
                self.prev_button = button
                self.press_count += 1

            else:
                if self.prev_image != picture:
                    self.prev_button.clicked.connect(self.button_client_clicked)
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


    def handle_server(self):
        try:
            while not self.stop_event.is_set():
                # Получаем информацию о нажатии кнопки от клиента
                data = self.client_sock.recv(1024)
                message = data.decode('utf-8')
                #print(message)
                if message == 'end':
                    self.stop_tread()
                    break
                if not data:
                    break
                button_name, picture = message.split('|')
                button = self.findChild(QPushButton, button_name)
                #print(f'Button {button_name} pressed, displaying picture {picture}')
                self.update_button(button, picture, 'r')

                if self.enemy_press_count == 0:
                    self.prev_enemy_button = button
                    self.prev_enemy_image = picture
                    self.enemy_press_count += 1
                else:
                    if self.prev_enemy_image != picture:
                        for btn in self.buttons_list:
                            btn.setEnabled(False)
                        time.sleep(1)

                        self.update_button(self.prev_enemy_button, os.path.join(os.path.dirname(__file__), 'pictures/back.jpg'), 'b')
                        self.update_button(button, os.path.join(os.path.dirname(__file__), 'pictures/back.jpg'), 'b')
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


    def lock_pictures(self, prev_button, current_button):
        prev_button.setIcon(QIcon('pictures/back.jpg'))
        current_button.setIcon(QIcon('pictures/back.jpg'))


    def start_tread(self):
        # Запускаем поток
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.handle_server, daemon=True)
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

    
    def update_button(self, button, picture_path, color):
        button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), picture_path)))
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
    connection_thread = threading.Thread(target=main_window.connect_to_server, daemon=True)
    connection_thread.start()

    sys.exit(app.exec())