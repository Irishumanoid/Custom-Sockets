import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b'message1', b'message2']

host, port, num_conns = sys.argv[1:4]

def start_connections(host, port, num_conn):
    server_addr = (host, port)
    for i in range(0, num_conn):
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


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print(f'received {recv_data!r} from {data.connid}')
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f'close the connection {data.connid}')
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"send {data.outb!r} to {data.connid}")
            sent = sock.send(data.outb) 
            data.outb = data.outb[sent:] 

if len(sys.argv) != 4:
    print(f'{sys.argv[0]} <host> <port> <number of connections>')
    sys.exit(1)

start_connections(host, int(port), int(num_conns))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("keyboard interrupt")
finally:
    sel.close()
