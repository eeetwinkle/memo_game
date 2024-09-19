import socket

def server():
    # Создаем сокет
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    serv_sock.bind(('', 53210))
    serv_sock.listen(10)

    try:
        while True:
            # Бесконечно обрабатываем входящие подключения
            client_sock, client_addr = serv_sock.accept()

            print('client connected', client_addr)
            # карточки ненадолго переворачиваются
            while True:
                # Пока клиент не отключился, читаем передаваемые
                # им данные и отправляем их обратно
                data = client_sock.recv(1024)
                if not data: # Клиент отключился
                    break
                # Декодируем данные из байтов в строку
                message1 = data.decode('utf-8')
                print(message1)
                data = client_sock.recv(1024)
                if not data:  # Клиент отключился
                    break
                # Декодируем данные из байтов в строку
                message2 = data.decode('utf-8')
                print(message2)
                response1 = input()
                client_sock.sendall(response1.encode('utf-8'))
                response2 = input()
                client_sock.sendall(response2.encode('utf-8'))

            client_sock.close()

    except (KeyboardInterrupt, SystemExit):
        print("Прерывание программы.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")



if __name__ == "__main__":
    server()
