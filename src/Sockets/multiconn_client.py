import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b'message 1', b'message 2'] #testing, each connection modifies this list

def start_connections(host, port, num_conn):
    server_addr = (host, port)
    for i in range(num_conn):
        conn_id = i+1
        print(f'starting connection {conn_id} to {server_addr}')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False) #accept input
        sock.connect_ex(server_addr) #doesn't interfere with connection in progress/throw BlockingIOError exception
        events = selectors.EVENT_READ | selectors.EVENT_WRITE #read and write from client
        data = types.SimpleNamespace(
            connid = conn_id,
            msg_total = sum(len(m) for m in messages),
            recv_total = 0,
            messages = messages.copy(),
            outb = b""
        )
        sel.register(sock, events, data)



