import socket
import sys
import time
import os
import struct

from math import ceil

# print ("\nWelcome to the FTP server.\n\nTo get started, connect a client.")

# # Initialise socket stuff
# TCP_IP = "127.0.0.1" # Only a local server
# TCP_PORT = 21 # Control connection port
# BUFFER_SIZE = 1024 # Standard size
# serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serverSocket.bind((TCP_IP, TCP_PORT))
# serverSocket.listen(1)
# conn, addr = serverSocket.accept()

# print ("\nConnected to by address: {}").format(addr)

# def put():
# # Send message once server is ready to recieve file details
#   conn.send("1")
# # Recieve file name length, then file name
# file_name_size = struct.unpack("h", conn.recv(2))[0]
# file_name = conn.recv(file_name_size)
# # Send message to let client know server is ready for document content
# conn.send("1")
# # Recieve file size
# file_size = struct.unpack("i", conn.recv(4))[0]
# # Initialise and enter loop to recive file content
# start_time = time.time()
# output_file = open(file_name, "wb")
# # This keeps track of how many bytes we have recieved, so we know when to stop the loop
# bytes_recieved = 0
# print ("\nRecieving...")
# while bytes_recieved < file_size:
#   l = conn.recv(BUFFER_SIZE)
#   output_file.write(l)
#   bytes_recieved += BUFFER_SIZE
#   output_file.close()
#   print ("\nRecieved file: {}").format(file_name)
# # Send upload performance details
#   conn.send(struct.pack("f", time.time() - start_time))
#   conn.send(struct.pack("i", file_size))

# def ls():
#   print ("Listing files...")
# # Get list of files in directory
#   listing = os.listdir(os.getcwd())
# # Send over the number of files, so the client knows what to expect (and avoid some errors)
#   conn.send(struct.pack("i", len(listing)))
#   total_directory_size = 0
# # Send over the file names and sizes whilst totaling the directory size
#   for i in listing:
# # File name size
#     conn.send(struct.pack("i", sys.getsizeof(i)))
# # File name
#     conn.send(i)
# # File content size
#     conn.send(struct.pack("i", os.path.getsize(i)))
#     total_directory_size += os.path.getsize(i)
# # Make sure that the client and server are syncronised
#     conn.recv(BUFFER_SIZE)
# # Sum of file sizes in directory
#     conn.send(struct.pack("i", total_directory_size))
# #Final check
#     conn.recv(BUFFER_SIZE)
#     print ("Successfully sent file listing")
#   return

# def get():
#   conn.send("1")
#   file_name_length = struct.unpack("h", conn.recv(2))[0]
#   print (file_name_length)
#   file_name = conn.recv(file_name_length)
#   print (file_name)
# if os.path.isfile(file_name):
# # Then the file exists, and send file size
#   conn.send(struct.pack("i", os.path.getsize(file_name)))
# else:
# # Then the file doesn't exist, and send error code
#   print ("File name not valid")
#   conn.send(struct.pack("i", -1))
# # Wait for ok to send file
# conn.recv(BUFFER_SIZE)
# # Enter loop to send file
# start_time = time.time()
# print ("Sending file...")
# content = open(file_name, "rb")
# # Again, break into chunks defined by BUFFER_SIZE
# l = content.read(BUFFER_SIZE)
# while l:
#   conn.send(l)
#   l = content.read(BUFFER_SIZE)
#   content.close()
# # Get client go-ahead, then send download details
#   conn.recv(BUFFER_SIZE)
#   conn.send(struct.pack("f", time.time() - start_time))

# def quit():
# # Send quit conformation
#     conn.send("1")
# # Close and restart the server
# conn.close()
# serverSocket.close()

class Server:
    '''
    A server class for ftp

    Attributes:
        ip (str): the ip address of the ftp server
        c_sock (socket): the control socket
    
    Methods:
        start()
            Start the ftp server

        quit()
            Closes the control connection and terminates the server

        
    '''

    def __init__(self, ip: str):
        '''

        Parameters:
            ip (str): the ip address of the ftp server
        '''

        self.ip = ip
        self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = 1024

        self.c_sock.bind((self.ip, 21))


    def start(self):
        '''Start the ftp server'''

        # Set number of allowed incoming connection requests
        self.c_sock.listen(1)
          
        # Wait for connection
        print('Waiting to connect...')
        conn, addr = self.c_sock.accept()
        print('Connected!')
    
        # Continually recieve message from control connection
        while True:
            # Recieve message
            msg = Server.receive(conn, 1024)

            # Parse message
            params = msg.split(',')

            match params[0]:
                case 'put':
                    self.put(conn, params[1])

                case 'quit':
                    self.quit(conn)

    def put(self, control_socket: socket, filename: str):
        '''
        Download file from client
        
        This method overwrites files if
        the file is already on the server

        Parameters:
            control_socket (socket): the control socket
            filename (str): the name of the file to download
        '''

        # Create data socket
        d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind data socket to ip and port
        d_sock.bind((self.ip, 20))

        # Create message with ip and port number for data connection
        msg = f'{self.ip},{20}'

        # Send msg over control connection
        Server.send(control_socket, msg)

        # Set max number of listeners for data connection
        d_sock.listen(1)

        # Accept connection
        conn, addr = d_sock.accept()

        print('connected')
        # Receive file from client
        data = Server.receive(conn, self.buffer_size)

        # Close data connection
        d_sock.close()
        conn.close()

        # Open and write data to file
        with open(filename, 'w+') as f:
            f.write(data)

    def get(self):
        pass

    def ls(self):
        pass

    def quit(self, socket: socket):
        '''
        Closes the control connection and terminates the server
        
        Parameters:
            socket: the control socket
        '''

        # Send acknowledgment to server
        Server.send(socket, '211')

        # Close control connection
        socket.close()

        # Pause terminal until user input, then exit
        print('Press any key to exit . . .')
        os.system('pause>NUL')
        sys.exit()

    @staticmethod
    def receive(socket: socket, buffer_size: int) -> str:
        '''
        Receive message from socket
        
        Parameters:
            socket (socket): the socket to recieve msg from
            buffer_size (int): the maximum buffer size

        Returns:
            str: the decoded string received from the socket
        '''

        # Get the size of the message
        size = int.from_bytes(socket.recv(4))

        data = b''
        for _ in range(ceil(size / buffer_size)):
            # Recieve buffer_size bytes and add to data
            data += socket.recv(buffer_size)

        print(f'Received: {data.decode("utf8")}')

        return data.decode('utf8')
    
    @staticmethod
    def send(socket: socket, msg: str):
        '''Send message over socket'''

        print(f'Sending: {msg}')

        # Prepend 4-byte file size to encoded message
        e_msg = struct.pack('>I', len(msg)) + msg.encode()

        bytes_sent = 0
        # Keep sending bytes until all bytes are sent
        while bytes_sent != len(e_msg):
            # Send that string!
            bytes_sent += socket.send(e_msg[bytes_sent:])

# os.execl(sys.executable, sys.executable, *sys.argv)

# while True:
# # Enter into a while loop to recieve commands from client
#   print ("\n\nWaiting for instruction")
#   data = conn.recv(BUFFER_SIZE)
#   print ("\nRecieved instruction: {}").format(data)
# # Check the command and respond correctly
#   if data == "PUT":
#     put()
#   elif data == "LS":
#     ls()
#   elif data == "GET":
#     get()
#   elif data == "QUIT":
#     quit()
# # Reset the data to loop
# data = None

if __name__ == '__main__':

    s = Server('127.0.0.1')

    s.start()