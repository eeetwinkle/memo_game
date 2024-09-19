import socket

serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
serv_sock.bind(('', 53210))
serv_sock.listen(10)

while True:
    # Бесконечно обрабатываем входящие подключения
    client_sock, client_addr = serv_sock.accept()
    print('client connected')
    # запуск игры (открытие всех карточек)

    while True:
        # Пока клиент не отключился, читаем передаваемые
        # им данные и отправляем их обратно
        data = client_sock.recv(1024)
        if not data:
            # Клиент отключился
            break
        # Декодируем данные из байтов в строку
        message = data.decode('utf-8')
        print(message)  
        response = input()
        client_sock.sendall(response.encode('utf-8'))

    client_sock.close()