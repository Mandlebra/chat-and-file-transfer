import os
import socket
import threading
import sys
import getopt
import struct

# test command line arguments
argc= len( sys.argv )
if (argc < 3 or argc > 7) :
    sys.exit()	

# trim command line string and initialize variables
argv = sys.argv[1:]
try: 
    opts, args = getopt.getopt(argv, "l:s:p:") 
except: 
    print("Error fetching command line arguments") 

# parse command line arguments
for opt, arg in opts: 
    if opt in ['-l']:   # listen
        listenPort = arg 
        option1 = True
    elif opt in ['-s']: # address 
        serverAddress = arg 
        option2 = True
    elif opt in ['-p']: # port 
        portNumber = arg
        option3 = True

# get messenger socket as sock and file transfer socket as sock2 for both server and client
sock = socket.socket()
sock.connect(('localhost', int(portNumber)))

# sock2 as second listening socket for file transfer
serversocket = socket.socket() 
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serversocket.bind(('localhost', int(listenPort))) 
serversocket.listen(5) 
sock.send( listenPort.encode() )
sock2, addr= serversocket.accept() 

print("What is your name?")
Username= sys.stdin.readline()
sock.send( Username.rstrip('\n').encode() ) 

# function for recieve thread
def recieve_message(sock1):
    while True:
        return_msg= sock1.recv( 1024 ) 
        
        if return_msg:
            sys.stdout.write(return_msg.decode())
        else:
            sock1.close()
            os._exit(0)

def recieveFileThread (serversake):
    file_size_bytes= serversake.recv( 4 )
    if file_size_bytes:
        file_size= struct.unpack( '!L', file_size_bytes[:4] )[0]
        if file_size:
            # Receive the file lines returned from the server
            file = open(filename, 'wb')
            remaining = file_size
            while remaining > 0:
                file_bytes = serversake.recv(min(1024, remaining))
                if file_bytes:
                    file.write(file_bytes)
                    remaining -= len(file_bytes)
                else:
                    break
            # print("end recieving file in ChatClient")
            file.close()
        else:
            print( 'File does not exist or is empty' )
    else:
        print( 'File does not exist or is empty' )
    serversake.close()
    sys.exit()

def recieveFile():
    # recieve filename and listen port
    # create socket and connect to sender's server socket
    while True:
        sake, addr= serversocket.accept()
        threading.Thread( target= recieveFileThread, args = (sake,) ).start()
        


def send_file_thread(listenCode, file_name):
    newsock = socket.socket()
    newsock.connect(('localhost', int(listenCode)))
    try:
        file_stat= os.stat( file_name )
        if file_stat.st_size:
            file= open( file_name, 'rb' )
            print( 'File size is ' + str(file_stat.st_size) )
            file_size_bytes= struct.pack( '!L', file_stat.st_size )
            # send the number of bytes in the file
            newsock.send( file_size_bytes )
            # read the file and transmit its contents
            while True:
                file_bytes= file.read( 1024 )
                if file_bytes:
                    newsock.send( file_bytes )
                else:
                    break
            file.close(); 
        else:
            zero_bytes= struct.pack( '!L', 0 )
            newsock.send( zero_bytes )
    except OSError:
        zero_bytes= struct.pack( '!L', 0 )
        newsock.send( zero_bytes )
        newsock.close()
    newsock.close()
    sys.exit()


def send_file(sock1):
    # using sock2
    while True:
        # print(sock1) 
        file_name_duple = sock1.recv(1024)
        file_name_duple = file_name_duple.decode()
        file_name = file_name_duple.split(',')[1]
        # print("fileName : " + file_name)
        # listenCode = sock1.recv(1024)
        listenCode = file_name_duple.split(',')[0]
        # print("chatclient recieved filename listencode:" + file_name + listenCode)
        # newsock, addr = serversocket.accept()
        threading.Thread( target= send_file_thread, args = (listenCode, file_name) ).start()
        


# create new thread for recieving messages
threading.Thread( target= recieve_message, args = (sock,) ).start()

# create new thread for communicating with server
threading.Thread( target= send_file, args = (sock2,) ).start()

# create new thread for connecting with clients
threading.Thread( target= recieveFile).start()

# handle menu and sending messages
while True:
    print("Enter an option ('m', 'f', 'x'):")
    print(" (M)essage (send)")
    print(" (F)ile (request)")
    print("e(X)it")

    try:
        message= sys.stdin.readline().rstrip('\n')
        if message:
            if message == 'm':
                print("What is your message? ")
                message= sys.stdin.readline()
                message = Username.rstrip('\n') + ": " + message
                sock.send( message.encode() ) 
            if message == 'f':
                print("Who owns the file?")
                # read a file name from standard input
                recipient= sys.stdin.readline().rstrip( '\n' )
                print("Which file do you want?")
                # read a file name from standard input
                filename = sys.stdin.readline().rstrip( '\n' )
                # transmit the file name
                recipfil = recipient + "," + filename
                sock2.send(recipfil.encode())

            if message == 'x':
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
                sock2.shutdown(socket.SHUT_RDWR)
                sock2.close()
                serversocket.close()
                os._exit()

        else:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            sock2.close()
            serversocket.close()
            os._exit()
    except:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        sock2.close()
        serversocket.close()
        os._exit()
