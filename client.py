import socket
import threading
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, QTimer
from PyQt6 import uic
import random
import time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('MainWindow.ui', self)
        self.setWindowTitle("Мемо - игра для вас и ваших друзей")
        self.setWindowIcon(QIcon('pictures/icon.png'))

        # Открываем сокет для приема и отправки сообщений
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect(('127.0.0.1', 53211))

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

        # Сейчас наш ход
        self.your_turn.setStyleSheet("""QPushButton{
                                        border: 5px solid #375;
                                        border-style: outset;
                                        background: rgb(60,150,90);
                                        color: rgb(250,250,255);
                                        }""")


        # Задаем условие выхода из потока для приема ходов противника
        self.stop_event = threading.Event()
        self.thread = None


    def button_client_clicked(self):
            button = self.sender()

            # Отправляем информацию о кнопке на сервер
            button_info = f"{button.objectName()}|?"
            self.client_sock.sendall(button_info.encode('utf-8'))

            data = self.client_sock.recv(1024)
            btn, picture = data.decode('utf-8').split('|')
            button.setIcon(QIcon(picture))
            # Если ход четный, то проверяемм условие выигрышности
            if self.press_count == 0:
                self.prev_image = picture
                self.prev_button = button
                self.press_count += 1
            else:
                if self.prev_image != picture:
                    for btn in self.buttons_list:
                        btn.setEnabled(False)
                    self.client_sock.sendall('end'.encode('utf-8'))
                    # Запускаем поток приема информации
                    self.start_tread()
                    # Закрываем карточки
                    QTimer.singleShot(1000, lambda: self.lock_pictures(self.prev_button, button))

                else:
                    self.my_score += 1
                    self.score.setText(str(self.my_score) + ":" + str(self.opponent_score))
                    self.prev_button.setStyleSheet("""QPushButton {
                                                            border: 5px solid #375;
                                                            border-style: outset;
                                                            color: black;
                                                            }""")
                    self.prev_button.disconnect()
                    button.setStyleSheet("""QPushButton {
                                                    border: 5px solid #375;
                                                    border-style: outset;
                                                    color: black;
                                                    }""")
                    button.disconnect()
                    if self.opponent_score + self.my_score == 15:
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
                #print(f"Button {button_name} pressed, displaying picture {picture}")
                button.setIcon(QIcon(picture))
                button.setStyleSheet("""QPushButton {
                                                    border: 5px solid #832;
                                                    border-style: outset;
                                                    color: black;
                                                    }""")
                if self.enemy_press_count == 0:
                    self.prev_enemy_button = button
                    self.prev_enemy_image = picture
                    self.enemy_press_count += 1
                else:
                    if self.prev_enemy_image != picture:
                        for btn in self.buttons_list:
                            btn.setEnabled(False)
                        time.sleep(1)
                        self.prev_enemy_button.setIcon(QIcon('pictures/back.jpg'))
                        self.prev_enemy_button.setStyleSheet("""QPushButton {
                                                                      border: 5px solid #357;
                                                                      border-style: outset;
                                                                      }""")
                        button.setIcon(QIcon('pictures/back.jpg'))
                        button.setStyleSheet("""QPushButton {
                                                                       border: 5px solid #357;
                                                                       border-style: outset;
                                                                       }""")
                    else:
                        self.opponent_score += 1
                        self.score.setText(str(self.my_score) + ":" + str(self.opponent_score))
                        self.prev_enemy_button.setStyleSheet("""QPushButton {
                                                                                border: 5px solid #832;
                                                                                border-style: outset;
                                                                                color: black;
                                                                                }""")
                        # После удачного хода кнопки не вызывают никакую функцию
                        self.prev_enemy_button.disconnect()
                        button.setStyleSheet("""QPushButton {
                                                                border: 5px solid #832;
                                                                border-style: outset;
                                                                color: black;
                                                                }""")
                        button.disconnect()
                        if self.opponent_score + self.my_score == 15:
                            self.i_lose()
                    self.enemy_press_count = 0


        except Exception as e:
            print(f"An error occurred: {e}")


    def lock_pictures(self, prev_button, current_button):
        prev_button.setIcon(QIcon('pictures/back.jpg'))
        current_button.setIcon(QIcon('pictures/back.jpg'))


    def start_tread(self):
        # Запускаем поток
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.handle_server, daemon=True)
            self.thread.start()
            self.enemys_turn.setStyleSheet("""QPushButton{
                                                    border: 5px solid #721;
                                                    border-style: outset;
                                                    background: rgb(180,50,40);
                                                    color: rgb(250,250,255);
                                                    }""")
            self.your_turn.setStyleSheet("""QPushButton {
                                                    border: 5px solid #375;
                                                    border-style: outset;
                                                    color: black;
                                                    }""")
            #print("Поток запущен.")


    def stop_tread(self):
        # Завершаем поток
        if self.thread is not None:
            self.stop_event.set()
            self.thread = None
            #print("Поток остановлен.")
            self.enemys_turn.setStyleSheet("""QPushButton {
                                                    border: 5px solid #832;
                                                    border-style: outset;
                                                    color: black;
                                                    }""")
            self.your_turn.setStyleSheet("""QPushButton{
                                                border: 5px solid #375;
                                                border-style: outset;
                                                background: rgb(60,150,90);
                                                color: rgb(250,250,255);
                                                }""")
            for btn in self.buttons_list:
                btn.setEnabled(True)

    def i_lose(self):
        self.label.setText("You lose")
        for button in self.buttons_list:
            #button.setText("You lose")
            button.setStyleSheet("""QPushButton {
                                                border: 5px solid #832;
                                                border-style: outset;
                                                color: black;
                                                }""")


    def i_win(self):
        self.label.setText("You lose")
        for button in self.buttons_list:
            #button.setText("You win")
            button.setStyleSheet("""QPushButton {
                                                border: 5px solid #375;
                                                border-style: outset;
                                                color: black;
                                                }""")


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
