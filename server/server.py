import socket
import sys
import os
import struct
import getpass

from pathlib import Path
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

        put(control_socket, filename)
            Download file from client

        get(control_socket, filename)
            Upload the file to the client

        ls(sock)
            Print a list of files in the current directory

        quit(socket)
            Closes the control connection and terminates the server

    Static Methods:
        receive(socket, buffer_size)
            Receive message from socket

        send(socket, msg)
            Send message over socket

        close():
            Closes the program
    '''

    def __init__(self, ip: str, port: int):
        '''

        Parameters:
            ip (str): the ip address of the ftp server
            port (int): the port number of the control connection
        '''

        self.ip = ip
        self.port = port
        self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer_size = 1024

        self.c_sock.bind((self.ip, self.port))


    def start(self):
        '''Start the ftp server'''

        # Print starting message
        print(f'Starting server on port {self.c_sock.getsockname()[1]}')

        # Set number of allowed incoming connection requests
        self.c_sock.listen(1)
          
        # Wait for connection
        print('Waiting to connect')
        conn, addr = self.c_sock.accept()
        print("Connected to by address: {}".format(addr))
    
        # Continually recieve message from control connection
        while True:

            print()

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

        # Send ok message to client
        Server.send(control_socket, '200')

        # Create data socket
        d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind data socket to ip and port
        d_sock.bind((self.ip, 0))

        # Create message with ip and port number for data connection
        msg = f'{self.ip},{d_sock.getsockname()[1]}'

        # Send msg over control connection
        Server.send(control_socket, msg)

        # Set max number of listeners for data connection
        d_sock.listen(1)

        # Accept connection
        conn, addr = d_sock.accept()
        print("Connected to by address: {}".format(addr))

        # Receive file from client
        data = Server.receive(conn, self.buffer_size)

        # Close data connection
        d_sock.close()
        conn.close()
        print(f'Closing data connection')

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
        
        # Check if file exists
        if not Path(filename).exists():
            # Send file not found return code
            Server.send(control_socket, '550')
            return
        else:
            Server.send(control_socket, '200')
        
        # Create data socket
        d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Created data socket.')

        # Bind data socket to ip and port
        d_sock.bind((self.ip, 0))

        # Create message with ip and port number for data connection
        msg = f'{self.ip},{d_sock.getsockname()[1]}'

        # Send msg over control connection
        Server.send(control_socket, msg)

        # Set max number of listeners for data connection
        d_sock.listen(1)

        # Accept connection
        print('awaiting connection')
        conn, addr = d_sock.accept()
        print("\nConnected to by address: {}".format(addr))

        filepath = Path(filename)

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
        print('Closing data connection')


    def ls(self, sock: socket):
        '''
        Print a list of files in the current directory

        Parameters:
            sock (socket): the control connection
        '''

        # Send ok message to client
        Server.send(sock, '200')

        # Create data socket
        d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind data socket to ip and port
        d_sock.bind((self.ip, 0))

        # Create message with ip and port number for data connection
        msg = f'{self.ip},{d_sock.getsockname()[1]}'

        # Send msg over control connection
        Server.send(sock, msg)

        # Set max number of listeners for data connection
        d_sock.listen(1)

        # Accept connection
        conn, addr = d_sock.accept()
        print("Connected to by address: {}".format(addr))

        # Get a list of files in the current directory
        file_list = os.listdir('.')
        if 'server.py' in file_list:
            file_list.remove('server.py')

        # Join the file names into a string separated by commas characters
        response = ", ".join(file_list)

        # Send the directory listing to the client over the data connection
        Server.send(conn, response)

        # Close data connection
        d_sock.close()
        conn.close()
        print('Closing data connection')

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

        # Close program
        Server.close()

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

    @staticmethod 
    def close():
        '''Closes the program'''

        # Windows system
        if os.name == 'posix':
            print('Press any key to exit . . .')
            getpass.getpass(prompt='', stream=None)
            sys.exit()
        elif os.name == 'nt':
            print('Press any key to exit . . .')
            os.system('pause>NUL')
            sys.exit()


if __name__ == '__main__':

    # Ensure there is only 2 command line arguments
    if len(sys.argv) != 2:
        # Print error
        print(f"'server.py' expects 1 argument ({len(sys.argv)-1} given)")
        
    # Parse argument
    else:
        try:
            int(sys.argv[1])

        except ValueError:
            print('Invalid port number.\nPlease try again...\n')


            # Terminate program
            Server.close()

        # Create Server
        s = Server('127.0.0.1', int(sys.argv[1]))

        # Start Server
        s.start()
