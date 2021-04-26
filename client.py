import os
import os.path
from os import path
import socket
import time
import sys
from tqdm import tqdm
import struct

#take the ip address of host as input
host = input("Server adress: ")
C="N" #this is used to allow the user to send/receive multiple times
while(C=="N"):
    #we first created a socket to establish the connection between the client & server & to determine the protocol used
    #the protocol we used here to communicate between the client & server is UDP
    #take the protocol as input
    protocol = input("Choose the protocol(TCP/UDP): ")
    while(protocol!= "TCP" and protocol!="UDP"):
        print("Invalid protocol!")
        protocol = input("Choose the protocol(TCP/UDP): ")
        #as a second step here, decide on the action: to upload or download
    mode = input("Choose mode (Upload/Download): ")
    while(mode!= "Upload" and mode!="Download"):
        print("Invalid mode!")
        mode = input("Choose mode (Upload/Download): ")

    #create socket
    protsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #communicates used protocol
    #send the protocol type
    protsock.sendto(str.encode(protocol),(host,22222))
    #send the 'mode' type
    protsock.sendto(str.encode(mode),(host,22222))
    #receive response
    response = protsock.recvfrom(256)
    #close socket
    protsock.close()

    #after we have established the protocol & mode, the process of downloading/uploading begins:
    #we broke them into cases according the mode
    #first check if upload, then check if TCP or UDP
    if(mode == "Upload"):
        #check which protocol
        if(protocol == "TCP"):
            #create socket
            Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            print("Connecting...")
            #connect to server
            Socket.connect((host, 22222))
            print("Done!")
            #take the name of the file as input ex: test.pdf
            filename = input("Choose file path: ")
            #checking the file exists 
            E = path.exists(filename) #taken from https://www.guru99.com/python-check-if-file-exists.html
            if(E == False):
                #printing an error msg if the file is not found 
                error = "File not found."
                print(error)
                Socket.send(str(error).encode())
                #we need to close socket &stop 
                Socket.close()
            else:
                print("File Found!")
                Socket.send(("File Found!").encode())
                #compute the size of the file
                size = os.path.getsize(filename) #taken from https://www.geeksforgeeks.org/python-os-path-size-method/
                #send it to the server (size + filename)
                Socket.send((filename+"\n").encode()) # we need a seperator for the filename in this case "\n"
                packer = struct.Struct('i') #used https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/socket/binary.html for help in encoding
                packed_data = packer.pack(size)
                Socket.send(packed_data)
                print("Sending...")
                #reading from file
                file = open(filename, "rb")
                #printing the live bandwidth 
                start =time.time()
                for i in tqdm(range(0,size,1024)): #used this source https://towardsdatascience.com/a-complete-guide-to-using-progress-bars-in-python-aa7f4130cda8 to know how to implement the progress bar
                    #reading from the file 
                    data = file.read(1024) #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                    if not (data):
                        break
                    Socket.sendall(data)
                    
                end = time.time()
                #closing the file after we finish 
                file.close()
            
                duration = end - start
                #printing the average bandwidth
                print("Average Bandwidth: ", (int(size)*8)/duration, "bps")
                print("Sent!")
                Socket.close()

        if(protocol == "UDP"):
            #create socket
            Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #take the file name as input
            filename = input("Choose file path: ")
            E = path.exists(filename) #taken from https://www.guru99.com/python-check-if-file-exists.html
            if(E == False):
                error = "File not found."
                print(error)
                Socket.sendto(str(error).encode(),(host,22222))
                Socket.close()
            else:
                print("File Found!")
                Socket.sendto(("File Found!").encode(),(host,22222))
                #compute its size
                size = os.path.getsize(filename) #taken from https://www.geeksforgeeks.org/python-os-path-size-method/
                #send to server (size + filename)
                Socket.sendto(filename.encode(),(host,22222))
                Socket.sendto(str(size).encode(),(host,22222))

                print("Sending...")
                #read from file
                file = open(filename, "rb")
                i = 0
                start =time.time()
                # Starting the time capture.

                for i in tqdm(range(0,size,1024)): #used this source https://towardsdatascience.com/a-complete-guide-to-using-progress-bars-in-python-aa7f4130cda8 to know how to implement the progress bar
                    data = file.read(1024) #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                    if not (data):
                        break
                    #read & send the data to the client
                    Socket.sendto(data,(host,22222))
                    Socket.recvfrom(1)
                end = time.time()
                file.close()

                #Total duration needed to receive file
                duration = end - start
                #print the average bandwidth
                print("Average Bandwidth: ", (int(size)*8)/duration, "bps")
                print("Sent!")
                #close socket
                Socket.close()

            #MODE: DOWNLOAD
    if(mode == "Download"):
        if(protocol == "TCP"):
            #create socket
            Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Connecting...")
            #connect socket
            Socket.connect((host, 22222))
            print("Done!")
            #take the file name as input
            filename = input("Choose file path: ")
            #send it to the server
            Socket.send((filename+"\n").encode()) # we need a seperator for the filename in this case "\n"
            message = str(Socket.recv(1024).decode())
            #for the following lines of code We used the help of this reference: #source for file transfer: https://github.com/nikhilroxtomar/File-Transfer-using-TCP-Socket-in-Python3/blob/main/client.py to better get the idea of using TCP for downloading
            if(message == "File not found."):
                print("File is not on cloud.")
                #if file not found, then close socket
                Socket.close()
            else:
                unpacker = struct.Struct('i') 
                f = Socket.recv(unpacker.size)
                size = unpacker.unpack(f)
                print("Receiving...")
                file = open(filename, "wb")
                band=0
                si=time.time()
                Bandwidth = 0
                # Starting the time capture.
                with tqdm(range(0,size[0],1024)) as t: #used this source https://towardsdatascience.com/a-complete-guide-to-using-progress-bars-in-python-aa7f4130cda8 to know how to implement the progress bar
                    for i in range(0,size[0],1024): #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                        data = Socket.recv(1024)
                        if not (data):
                            break
                        file.write(data)
                        band+=len(data)
                        try:
                        #printing the live bandwidth in bps
                            Bandwidth = str(band*8/(time.time()-si))
                            B = Bandwidth + " bps"
                            t.set_postfix({"Bandwidth": B}) #used this reference https://tqdm.github.io/docs/tqdm/ to know how to modify the progress bar accordingly
                            t.update()
                        except:
                            Bandwidth =  "∞ bps"
                            t.set_postfix_str("Bandwidth: ∞ bps") #used this reference https://tqdm.github.io/docs/tqdm/ to know how to modify the progress bar accordingly
                            t.update()
                file.close()
                #Total duration needed to receive file
                print("Received!")
            
                #close socket
                Socket.close()

        if(protocol == "UDP"):
            #create socket
            Socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #take filename as input
            filename = input("Choose file path: ")
            Socket.sendto(filename.encode(),(host,22222))
            #receive confirmation msg / file itself
            message = (Socket.recvfrom(1024))[0].decode() #got insight from https://tutorialedge.net/python/udp-client-server-python/ for receieving error message
            if(message == "File not found."):
                print("File is not on cloud.")
                Socket.close()
            else:
                size = int(Socket.recvfrom(1024)[0].decode())
                print("Receiving...", end = "")
                #writing to the file
                file = open(filename, "wb")
                i = 0
                band=0
                si=time.time()
                # Starting the time capture.
                with tqdm(range(0,size,1024)) as t: #used this source https://towardsdatascience.com/a-complete-guide-to-using-progress-bars-in-python-aa7f4130cda8 to know how to implement the progress bar
                    for i in range(0,size,1024): #used https://www.thepythoncode.com/article/send-receive-files-using-sockets-python for writing and reading files
                        data = Socket.recvfrom(1024)
                        if not (data):
                            break
                        file.write(data[0])
                        band+=len(data[0])
                        try:
                        #printing the live bandwidth
                            Bandwidth = str(band*8/(time.time()-si))
                            B = Bandwidth + " bps"
                            t.set_postfix({"Bandwidth": B}) #used this reference https://tqdm.github.io/docs/tqdm/ to know how to modify the progress bar accordingly
                            t.update()
                        except:
                            Bandwidth =  "∞ bps"
                            t.set_postfix_str("Bandwidth: ∞ bps") #used this reference https://tqdm.github.io/docs/tqdm/ to know how to modify the progress bar accordingly
                            t.update()
                        Socket.sendto("".encode(),data[1])
                file.close()
                #Total duration needed to receive file
            
                print("Received!")

                
                Socket.close()
    
    C = input("Exit the program?(Y/N): ")
    #asks if we want to upload/download more files
    while(C!="Y" and C!="N"):
        C = input("Exit the program?(Y/N): ")
