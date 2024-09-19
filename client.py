import socket


def client():
    # Создаем сокет
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(('172.20.10.7', 53210))

    try:
        while True:
            # Запрашиваем ввод сообщения от пользователя
            message = input("Введите сообщение (или 'exit' для выхода): ")

            # Проверяем условие выхода
            if message.lower() == 'exit':
                print("Выход из программы.")
                break

            # Отправляем сообщение серверу
            client_sock.sendall(message.encode())

            # Получаем ответ от сервера
            data = client_sock.recv(1024)
            print('Получено:', repr(data))

    except (KeyboardInterrupt, SystemExit):
        print("Прерывание программы.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        client_sock.close()


if __name__ == "__main__":
    main()
