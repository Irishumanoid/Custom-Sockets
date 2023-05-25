import socket

HOST = "127.0.0.1" #standard IPv4 address for loopback interface (only processes on host can connect to server)
#localhost doesn't require physical network interface, secure and isolated from external network
PORT = 65432 #TCP port


#different listening and communication sockets
#AF_INET is default address family, SOCK_STREAM socket type for TCP connection protocol
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT)) #associate socket with network interface and port number
    s.listen()
    conn, addr = s.accept() #get connection and client address, blocks execution to wait for incoming connection
    with conn: #closes socket automatically at end of block
        print(f"connected by {addr}")
        while True: #read and echo client data in loop
            data = conn.recv(1024) #receive data on port, 1024 is buffer size (max # receivable bytes)
            if not data:
                break
            conn.sendall(data) #send all received data to client
