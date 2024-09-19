import socket


def client():
    # Создаем сокет
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('172.20.10.7', 53210))

    try:
        while True:
            # Запрашиваем ввод сообщения от пользователя
            message1 = input("1 фото: ")
            message2 = input("2 фото: ")

            # Отправляем сообщение серверу
            client_sock.sendall(message1.encode('utf-8'))
            client_sock.sendall(message2.encode('utf-8'))
            # Получаем ответ от сервера
            data = client_sock.recv(1024)
            response1 = data.decode('utf-8')
            print(response1)
            data = client_sock.recv(1024)
            response2 = data.decode('utf-8')
            print(response2)
            #условие для правильных картиной

    except (KeyboardInterrupt, SystemExit):
        print("Прерывание программы.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        client_sock.close()


if __name__ == "__main__":
    client()
