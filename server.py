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

        self.buttons_list = self.buttons.buttons()
        self.press_count = 0
        self.prev_image = ''
        self.prev_button = ''
        self.enemy_press_count = 0
        self.prev_enemy_image = ''
        self.prev_enemy_button = ''

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

                button.clicked.connect(self.button_server_clicked)
                button.setEnabled(False)


        self.enemys_turn.setStyleSheet("""QPushButton{
                                    border: 5px solid #721;
                                    border-style: outset;
                                    background: rgb(180,50,40);
                                    color: rgb(250,250,255);
                                    }""")


        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('', 53210))
        self.server_sock.listen(1)
        print('Server is running')

        self.client_sock, self.client_addr = self.server_sock.accept()
        print('Client connected', self.client_addr)

        self.stop_event = threading.Event()
        threading.Thread(target=self.handle_client, daemon=True).start()


    def handle_client(self):
        try:
            while not self.stop_event.is_set():

                data = self.client_sock.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                print(message)
                if message == 'end':
                    self.stop_tread()
                    break
                button_name, special_simbol = message.split('|')
                print(button_name, special_simbol)
                button = self.findChild(QPushButton, button_name)

                picture = button.property('picture')
                picture_info = f'{button_name}|{picture}'

                self.client_sock.sendall(picture_info.encode('utf-8'))

                print(f"Button {button_name} pressed, displaying picture {picture}")
                self.update_server_interface(button_name, picture)

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
                        button.setIcon(QIcon('pictures/back.jpg'))
                        #QTimer.singleShot(3000, lambda: self.lock_pictures(self.prev_enemy_button, button))
                        print("закрыто")
                    else:
                        self.prev_enemy_button.setStyleSheet("""QPushButton {
                                                                                border: 5px solid #832;
                                                                                border-style: outset;
                                                                                color: black;
                                                                                }""")
                        self.prev_enemy_button.disconnect()
                        button.setStyleSheet("""QPushButton {
                                                                border: 5px solid #832;
                                                                border-style: outset;
                                                                color: black;
                                                                }""")
                        button.disconnect()
                    self.enemy_press_count = 0

        except Exception as e:
            print(f"An error occurred: {e}")


    def start_tread(self):
        if self.thread is None or not self.thread.is_alive():
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.handle_client, daemon=True)
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
            print("Поток запущен.")

    def stop_tread(self):
        if self.thread is not None:
            self.stop_event.set()
            self.thread = None
            print("Поток остановлен.")
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

    def button_server_clicked(self):
        button = self.sender()
        picture = button.property('picture')

        button_info = f'{button.objectName()}|{picture}'
        self.client_sock.sendall(button_info.encode('utf-8'))

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
                self.client_sock.sendall('end'.encode('utf-8'))
                self.start_tread()
                QTimer.singleShot(1000, lambda: self.lock_pictures(self.prev_button, button))

            else:
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
            self.press_count = 0

    def lock_pictures(self, prev_button, current_button):
        prev_button.setIcon(QIcon('pictures/back.jpg'))
        current_button.setIcon(QIcon('pictures/back.jpg'))

    def update_server_interface(self, button_name, picture_path):
        button = self.findChild(QPushButton, button_name)
        button.setIcon(QIcon(picture_path))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


