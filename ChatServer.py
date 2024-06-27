import os
import socket
import threading
import sys

listenPort = sys.argv[1] 

serversocket = socket.socket() 
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serversocket.bind(('localhost', int(listenPort))) 
clients = [] 
serversocket.listen(5) 

def recieve_message(sock1, clientlist):
    while True:
        return_msg= sock1.recv( 1024 ) 
        if return_msg:
            for (socky, socky2, un, ln) in clientlist:
                if socky != sock1:
                    socky.send(return_msg)
        else:
            sock1.close()
            os._exit(0)

def recieve_file(sock1, clientlist):

    recipfil = sock1.recv(1024).decode()
    sendr = recipfil.split(',')[0]
    filen = recipfil.split(',')[1]

    #send listen port of requester & file name to file sender
    listenpl = ""
    recipSocky = ""
    for (sockyl, socky2l, unl, lnl) in clientlist:
        if sock1 == socky2l:
            listenpl = lnl
        if sendr == unl:
            recipSocky = socky2l
    duple = listenpl + "," + filen
    recipSocky.send(duple.encode())

while True:
    sock, addr= serversocket.accept()
    listenNumber = sock.recv(1024).decode()
    sock2 = socket.socket()
    sock2.connect(('localhost', int(listenNumber)))
    username = sock.recv( 1024 ).decode()
    clients.append((sock, sock2, username, listenNumber))
    threading.Thread( target= recieve_message, args = (sock, clients) ).start()
    threading.Thread( target= recieve_file, args = (sock2, clients) ).start()