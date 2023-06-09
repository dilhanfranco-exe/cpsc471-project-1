import socket
import sys
import os
import struct
import ipaddress
import getpass

from pathlib import Path
from math import ceil

raw_input = input

class Client():
    '''
    A client class for ftp
    
    Attributes:
        ip (string): the IP address of the ftp server
        port (int): the port number for the ftp server
        buffer_size (int): the size of the client's buffer in bytes
        c_sock (socket): the control socket for communication with ftp server

    Methods:
        start()
            Starts ftp client

        get_input()
            Gets user input and calls appropriate command

        help()
            Display help information

        put(filename)
            Uploads file to the ftp server
        
        get(filename)
            Downloads file from the ftp server
        
        ls()
            Request and prints a list of the files in the ftp working directory

        quit()
            Closes the control connection and terminates the client


    Static Methods:
        tokenize_string(input_string)
            Tokenizes input string

        connect(sock, ip, port_number)
            Attempts to connect socket to the ftp server

        send(socket, msg)
            Send message over socket

        receive(socket, buffer_size)
            Receive message from socket

        close()
            Closes the program
    '''

    def __init__(self, serverip, port_number):
        '''
        
        Parameters:
            serverip (str): the server ip address
            port_number (int): the port number
        '''
        self.ip = serverip
        self.port = port_number
        self.buffer_size = 1024
        self.c_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect(self.c_sock, self.ip, self.port)

    def start(self):
        '''
        Starts ftp client
        
        Request user input in a loop until user quits
        '''

        # Print welcome message and help information
        print('##### WELCOME TO FTP! ############################################\n')
        self.help()

        while True:
            # Get user input as command
            self.get_input()

    def get_input(self):
        '''Gets user input and calls appropriate command'''

        try:
            # Get user input
            inStr = raw_input('ftp>')

        except EOFError:
            # Ctrl-z
            return
        except KeyboardInterrupt:
            # Ctrl-c
            print()
            return
        
        # Empty string
        if not inStr:
            return

        # Get tokens for user input
        tokens = Client.tokenize_string(inStr)

        match tokens[0]:
            ### GET COMMAND ###############################################
            case 'get':
                # Ensure only one parameter
                if len(tokens) != 2:
                    # Print error
                    print(f"'get' expected 1 argument ({len(tokens)-1} given)\n")
                    return

                self.get(tokens[1])

            ### PUT COMMAND ###############################################
            case 'put':
                # Ensure only one parameter
                if len(tokens) != 2:
                    # Print error
                    print(f"'put' expected 1 argument ({len(tokens)-1} given)\n")
                    return
                
                self.put(tokens[1])

            ### LS COMMAND ################################################
            case 'ls':
                # Ensure no parameters
                if len(tokens) != 1:
                    # Print error
                    print(f"'ls' expected 0 arguments ({len(tokens)-1} given)\n")
                    return
                
                self.ls()

            ### QUIT COMMAND ##############################################
            case 'quit':
                # Ensure no parameters
                if len(tokens) != 1:
                    # Print error
                    print(f"'get' expected 0 arguments ({len(tokens)-1} given)\n")
                    return

                self.quit()

            ### HELP COMMAND ##############################################
            case 'help':
                self.help()
                return

            ### INVALID COMMAND ###########################################
            case _:
                # Print error
                print(f"'{tokens[0]}' is not a recognized command\n")
                return
            
    def help(self):
        '''Display help information'''

        print(f'Current Directory: {os.getcwd()}\n\n'\
                       'GET - Download a file from the server\n'\
                       '\tUsage: get <filename>\n\n'\
                       'PUT - Upload a file to the server\n'\
                       '\t Usage: put <filename>\n\n'\
                       'LS - List file in server directory\n'\
                       '\tUsage: ls\n\n'\
                       'QUIT - Close connection with server\n'\
                       '\tUsage: quit\n\n'\
                       'HELP - Display help information\n'\
                       '\tUsage: help\n')
            
    def put(self, filename: str):
        '''
        Uploads file to the ftp server

        Parameters:
            filename (str): name of the file to be uploaded
        '''

        filepath = Path(filename)

        # Print message
        print(f'Uploading {filepath.name}...\n')

        # Check if attempting to upload cli.py
        if filepath.name == 'cli.py':
            print('Cannot send client program.\n')
            return

        # Open and read file
        try:
            # Open file
            with open(filepath, "r") as f:

                # Read file contents
                msg = f.read()

        except IOError:
            if '\\' in filename:
                print("Could'nt open file. Use forward slashes instead.\n")
            else:
                print("Couldn't open file. Make sure the file name was entered correctly.\n")
            return

        # Send upload request
        try:
            # Make upload request
            Client.send(self.c_sock, f'put,{filename}')
        except socket.error:
            print("Couldn't make server request. Make sure a connection has been established.\n")
            return

        try:

            # Receive server message indicating command will be executed succesfully
            m = Client.receive(self.c_sock, self.buffer_size)

            if m != '200':
                print('Bad Request.\n')
                return

            # Receive server message indicating ip and port of data connection
            m = Client.receive(self.c_sock, self.buffer_size)

            # Parse message
            ip, port = m.split(',')
            port = int(port)

        # Establish data connection on ip and port
        # specified in server response message m

            # Create data socket
            d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect data socket to server
            self.connect(d_sock, ip, port)

        # Send file to server over data connection

            # Send message over data connection
            Client.send(d_sock, msg)

            # Close data connection
            d_sock.close()

        except socket.error:
            print("Error sending file")
            return
        
    def get(self, filename: str) -> str:
        '''
        Downloads file from the ftp server

        Parameters:
            filename (str): name of file to be downloaded

        Returns:
            str: the downloaded file as a utf8 string
        '''

        # Check if client is attempting to download server.py
        if Path(filename).name == 'server.py':
            print('Cannot download server program.\n')
            return
    
        # Print getting message
        print(f'Downloading {Path(filename).name}...\n')

        # Send a GET request to the server over the control connection, 
        # specifying the name and path of the file to be retrieved.

        try:
            # Make upload request
            Client.send(self.c_sock, f'get,{filename}')
        except socket.error:
            print("Couldn't make server request. Make sure a connection has been established.\n")
            return
        
        # Receive response message from server indicating if file exist
        m = Client.receive(self.c_sock, self.buffer_size)

        if m == '550':
            print('File not found.\n')
            return
        elif m == '200':
            # File exist
            pass

        # Receive a response message from the server that includes the 
        # IP address and port number to be used for the data connection.

        try:
            # Receive server message
            m = Client.receive(self.c_sock, self.buffer_size)

            # Parse message
            ip, port = m.split(',')
            port = int(port)

        # Establish a data connection with the server on the IP address 
        # and port specified in the server response message.
        
            d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(d_sock, ip, port)

        # Receive the file from the server over the data connection.
            data = Client.receive(d_sock,self.buffer_size)
          
            with open(filename, 'w+') as f:
                    f.write(data)
            
        # Close the data connection.

            d_sock.close()
            
        # Return the string

        except socket.error:
            print("Error receiving file")
            return
        

    def ls(self):
        '''Request and prints a list of the files in the ftp working directory'''

        try:

            # Send LS command
            Client.send(self.c_sock, 'ls')

            # Receive server message indicating command will be executed succesfully
            m = Client.receive(self.c_sock, self.buffer_size)

            if m != '200':
                print('Bad Request.\n')
                return
            
            # Receive server message indiciating ip and port of data connection
            m = Client.receive(self.c_sock, 1024)

            # Parse server message
            ip, port = m.split(',')
            port = int(port)

            # Create and connect data socket
            d_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(d_sock, ip, port)

            # Receive data from server over data connection
            data = Client.receive(d_sock, self.buffer_size)

            # Print data to terminal
            print(data, end='\n\n')

            # Close data socket
            d_sock.close()

        except Exception as e:
            print(f'Error: {str(e)}')

    def quit(self):
        '''Closes the control connection and terminates the client'''

        # Send a QUIT command to the server over the control connection.
        # Client.send(c_sock, 'QUIT\r\n')
        Client.send(self.c_sock, 'quit')

        # Receive a response message from the server indicating that the 
        # command has been received and the connection will be closed.    
        m = Client.receive(self.c_sock, 1024)

        # Close connection if return code is 211
        if m == '211':

            # Print goodbye message
            print('Thanks for using ftp!\n')

            # Close control connection
            self.c_sock.close()

            # Terminate programs
            Client.close()

        # Connection could not be closed
        else:
            print('Could not close connection... Please try again.\n')
    
    @staticmethod
    def tokenize_string(input_string: str) -> list[str]:
        '''
        Tokenizes input string

        Parameters:
            input_string (str): string to tokenize

        Returns:
            list: list of string tokens
        '''

        # Remove extra spaces
        while '  ' in input_string:
            input_string.replace('  ', ' ')

        # Strip leading and trailing whitespace
        input_string = input_string.strip()
        
        # Return tokens
        return input_string.split(' ')
    
    @staticmethod
    def connect(sock: socket, ip: str, port_number: int):
        '''
        Attempts to connect socket to the ftp server
        
        If connection is unsuccessful this function will terminate the program

        Parameters:
            sock (socket): the socket to connect to the server
            ip (str): the ip address of the server socket
            port_number (int): port number of the server socket
        '''

        try:
            sock.connect((ip, port_number))

        except:
            # Could not connect to server
            print("Connection unsuccessful. Please check if port number and ip is correct or server is online.\nClosing 'cli.py'...\n")
            
            # Close the program
            Client.close()

    @staticmethod
    def send(socket: socket, msg: str):
        '''Send message over socket'''

        # print(f'Sending: {msg}')

        # Prepend 4-byte file size to encoded message
        e_msg = struct.pack('>I', len(msg)) + msg.encode()

        bytes_sent = 0
        # Keep sending bytes until all bytes are sent
        while bytes_sent != len(e_msg):
            # Send that string!
            bytes_sent += socket.send(e_msg[bytes_sent:])

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
        size = int.from_bytes(socket.recv(4), byteorder='big')

        data = b''
        for _ in range(ceil(size / buffer_size)):
            # Recieve buffer_size bytes and add to data
            data += socket.recv(buffer_size)

        # print(f'Received: {data.decode("utf8")}')

        return data.decode('utf8')
    
    @staticmethod 
    def close():
        '''Closes the program'''

        # Windows system
        if os.name == 'posix':
            print('Press Enter to exit . . .')
            # Wait for user input
            getpass.getpass(prompt='', stream=None)

            # Terminate program
            sys.exit()
        elif os.name == 'nt':
            print('Press any key to exit . . .')
            # Wait for user input
            os.system('pause>NUL')

            # Terminate program
            sys.exit()

            
if __name__ == '__main__':

    # print()
    
    # Ensure there are only 3 command line arguments
    if len(sys.argv) != 3:
        # Print error
        print(f"'cli.py' expects 2 arguments ({len(sys.argv)-1} given)")
        
    # Parse arguments
    else:
        try:
            int(sys.argv[2])
            ipaddress.ip_address(sys.argv[1])

        except ValueError:
            print('Invalid IP address or port number.\nPlease try again...\n')

            # Terminate program
            Client.close()
        

        # Create Client
        cli_sock = Client(sys.argv[1], int(sys.argv[2]))

        # Start Client
        cli_sock.start()
