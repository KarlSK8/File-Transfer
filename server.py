import os
import socket
import time
import os.path
from os import path
import struct

while(True):
    #create socket 
    protsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #bind socket 
    protsock.bind(("",22222))
    #receiving the protocol from the client 
    protocol = protsock.recvfrom(256)
    #receiving the mode from the client 
    mode = protsock.recvfrom(256)


    print("Received request of type: " , protocol[0].decode(), " from: " ,protocol[1])
    #sending a confirmation msg to the client 

    protsock.sendto(str.encode("ok"),protocol[1])
    #close socket 
    protsock.close()
    #incase we are uploading, we need to check the protocol type 
    if(mode[0].decode() == "Upload"):
        #TCP 
        if(protocol[0].decode() == "TCP"):
            #create socket
            Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #bind 
            Socket.bind(("", 22222))
            #listen 
            Socket.listen(1)

            print("Connecting...")
            #address of the client 
            client, addr = Socket.accept()
            print("Done!")
            #receiving the file msg (if found or not)
            M = str(client.recv(1024).decode('utf-8'))
            #if not found, quit & close socket 
            if(M == "File not found."):
                print("Quitting...")
                #close socket 
                Socket.close()
            else:
                #receiving the file size & name 
                buffer = ""
                while "\n" not in buffer:
                    buffer += client.recv(1).decode()
                filename = str(buffer)
                filename = filename[0:len(filename)-1]
                unpacker = struct.Struct('i') 
                f = client.recv(unpacker.size)
                filesize = unpacker.unpack(f)
                print("Preparing to receive: ", filename,"(",filesize," bytes )")
                #open the file to write 
                file = open("./cloud/" + filename, "wb")
                i = 0
                print("")
                #write back to the file 
                while(i <= filesize[0]): #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                    data = client.recv(1024)
                    if not (data):
                        break
                    file.write(data)
                    i += len(data)
                file.close()
                
                print("Received!")
                #close socket 
                Socket.close()

        #incase we are using UDP protocol     
        if(protocol[0].decode() == "UDP"):
            #create socket 
            Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #bind 
            Socket.bind(("", 22222))
            #receive the file msg (if found or not)
            M = Socket.recvfrom(1024)[0].decode()
            #if not found 
            if(M == "File not found."):
                # quit and close socket 
                print("Quitting...")
                Socket.close()
            else:
                #if the file is found
                #receive the filename & size 
                filename = Socket.recvfrom(1024)[0].decode()
                filesize = int(Socket.recvfrom(1024)[0].decode())

                print("Preparing to receive: ", filename,"(",filesize," bytes )")
                #writing to the file 
                file = open("./cloud/" + filename, "wb")
                    
                i = 0

                while i < filesize: #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                    data = Socket.recvfrom(1024)
                    if not (data):
                        break
                    file.write(data[0])
                    i += len(data[0])
                    #since we are using UDP and we have to slow down the process of sending and receiving to avoid packet drops 
                    Socket.sendto("".encode(),data[1])
                file.close()
                #close the socket 
                print("Received!")
                Socket.close()
    #downloading
    if(mode[0].decode() == "Download"):
        #tcp protocol 
        if(protocol[0].decode() == "TCP"):
            #create socket
            
            Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #bind & listen (connection oriented)
            Socket.bind(("", 22222))
            Socket.listen(1)

            print("Connecting...")
            #client's address 
            client, addr = Socket.accept()
            print("Done!")
            #receive the file name & size 
            buffer = ""
            while "\n" not in buffer:
                buffer += client.recv(1).decode() #stopping at the seperator
            filename = str(buffer)
            filename = filename[0:len(filename)-1]
            E = path.exists("./cloud/" + filename) #taken from https://www.guru99.com/python-check-if-file-exists.html
            if(E == False):
                #if file not found send an error msg
                error = "File not found."
                print(error)
                client.send(str(error).encode())
                Socket.close()
                client.close()
            else:
                #if found, we need to send it to the client
                client.send(("File found.").encode())
                #get size of the file 
                filesize = os.path.getsize("./cloud/" + filename) #taken from https://www.geeksforgeeks.org/python-os-path-size-method/
                #send the size back
                packer = struct.Struct('i') #used https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/socket/binary.html for help in encoding
                packed_data = packer.pack(filesize)
                client.send(packed_data)
                print("Preparing to send: ", filename,"(",filesize," bytes )")
                    #read file 
                file = open("./cloud/" + filename, "rb")
                        
                i = 0
                #reading from file then closing it
                while i <= filesize: #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                    data = file.read(1024)
                    if not (data):
                        break
                    client.sendall(data)
                    i += len(data)
                file.close()
                    
                print("Sent!")
                    #close socket 
                Socket.close()
                client.close()
        #if UDP protocol 
        if(protocol[0].decode() == "UDP"):
                #create socket
            Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #bind 
            Socket.bind(("", 22222))
            #receive the file name and check if it is found 
            N = Socket.recvfrom(1024)
            filename = N[0].decode()
            E = path.exists("./cloud/" + filename) #taken from https://www.guru99.com/python-check-if-file-exists.html
            if( E == False):
                error = "File not found."
                #if file not found then send error msg to the client 
                print(error)
                Socket.sendto(str(error).encode(), N[1])
                Socket.close()
            else:
                #if found, send confirmation msg 
                Socket.sendto(("File found.").encode(), N[1])
                #get size of file 
                filesize = os.path.getsize("./cloud/" + filename) #taken from https://www.geeksforgeeks.org/python-os-path-size-method/
                
                Socket.sendto(str(filesize).encode(), N[1])
                print("Preparing to send: ", filename,"(",filesize," bytes )")
                    #read from file
                file = open("./cloud/" + filename, "rb")
                    
                i = 0

                while i <= filesize: #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                    data = file.read(1024)
                    if not (data):
                        break
                    Socket.sendto(data,N[1])
                    Socket.recvfrom(1)
                    i += len(data)
                file.close()
                
                print("Sent!")
                Socket.close()
