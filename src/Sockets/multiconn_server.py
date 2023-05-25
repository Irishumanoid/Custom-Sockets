import socket
import sys
import selectors
import types

sel = selectors.DefaultSelector()

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None) #wait for data on multiple sockets


#get new socket object and register with selector
def accept_wrapper(sock:socket.socket(socket.AF_INET, socket.SOCK_STREAM)):
    conn, addr = sock.accept()
    print(f"accepted connection from {conn}")
    conn.setblocking(False) #sockets perform independent of each other
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"") #data carried with socket
    events = selectors.EVENT_READ | selectors.EVENT_WRITE #find out when client is ready to read or write
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj #socket object
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data #add received data outbound data through socket
        else:
            print(f"closing connection to {data.addr}")
            sel.unregister(sock) #socket is no longer monitored by .select()
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"echoing {data.outb} to {data.addr}")
            sent = sock.send(data.outb) #echo outbound data to client
            data.outb = data.outb[sent:] #remove bytes from buffer by taking array slice


try:
    while True:
        events = sel.select(timeout=None) #blocks until sockets are ready for io
        for key, mask in events: #key for association of file with file description, mask of available operations
            if key.data is None:
                accept_wrapper(key.fileobj)
            else: #previously accepted client socket, so connection may be serviced
                service_connection(key, mask)
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()



