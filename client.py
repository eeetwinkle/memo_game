import socket


def client():
    # Создаем сокет
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('172.20.10.7', 53210))
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
                    # заблокировать все кнопки для нажатия, если неправильно
                    # картинки открыть если правильно и продолжать отсылать
                    # if message1.image != message2.image:
                    #   current_user = 1

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
