import socket
import sys
import time
import os
import struct

from math import ceil

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
        print("\nConnected to by address: {}".format(addr))
    
        # Continually recieve message from control connection
        while True:
            # Recieve message
            msg = Server.receive(conn, 1024)

            # Parse message
            params = msg.split(',')

            match params[0]:
                case 'put':
                    self.put(conn, params[1])
                case 'get':
                    self.get(conn,params[1])
                case 'ls':
                  self.ls(conn)

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

    def get(self, control_socket: socket, filename: str):
        '''
        
        Upload the file to the client

        Parameters:
            socket (socket): the control conneciton
            filename (str): the name of the file to upload
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

        filepath = os.getcwd() + '\\' + filename

        # Open and read file
        try:
            # Open file
            with open(filepath, "r") as f:

                # Read file contents
                msg = f.read()

        except IOError:
            print("Couldn't open file. Make sure the file name was entered correctly.\n")
            return
        
        Server.send(conn, msg)
        
        # Close data connection
        d_sock.close()
        conn.close()


    def ls(self, sock: socket):
        '''
        Return a list of files in the current directory

        Parameters:
            sock (socket): the control connection
        '''
        # Create data socket
        d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get a list of files in the current directory
        file_list = os.listdir('.')

        # Join the file names into a string separated by newline characters
        response = ", ".join(file_list)

        # Send the directory listing to the client over the data connection
        Server.send(sock, response)

        # Close data connection
        d_sock.close()

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

if __name__ == '__main__':

    s = Server('127.0.0.1')

    s.start()