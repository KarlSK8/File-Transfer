# File-Transfer
This project allows sending and retrieving different types of files between a server and a client.


To start, you have to create a folder, named "cloud" on the server side in which the sent files will be found, and from which you'll br retrieving a file if needed.

After running the client, you will be asked to input:
1-The server's IP Adress.
2-Choose between 2 protocols, UDP or TCP.
3-Choose between sending and retriving files.
4-Write the file path you're intending to send or retrieve from the cloud.

The client side displays the average bandwidth exprienced throughout the whole process. It also displays a live bandwidth during the sending and recieving process.
A progress bar is implemented on the client side.
The client also shows the total time needed to send or retrieve the file. This duration is displayed next to the progress bar.

