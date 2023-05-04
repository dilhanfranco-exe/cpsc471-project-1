import socket
import sys
import os
import struct
from math import ceil

# # Initialise socket stuff
# TCP_IP = "127.0.0.1" # Only a local server
# TCP_PORT = 12345 # Just a random choice
# BUFFER_SIZE = 1024 # Standard chioce
# serverSocket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_input = input


# def conn():
# # Connect to the server
#     print ("Sending server request...")
# # try:
# #     serverSocket.connect((TCP_IP, TCP_PORT))
# #     print ("Connection successful")
# # except:
# #     print ("Connection unsucessful. Make sure the server is online.")


# def upld(file_name):
# # Upload a file
#     print ("\nUploading file: {}...").format(file_name)
#     try:
# # Check the file exists
#         content = open(file_name, "rb")
#     except:
#         print ("Couldn't open file. Make sure the file name was entered correctly.")

#     try:
# # Make upload request
#         serverSocket.send("UPLD")
#     except:
#         print ("Couldn't make server request. Make sure a connection has bene established.")

#     try:
# # Wait for server acknowledgement then send file details
# # Wait for server ok
#         serverSocket.recv(BUFFER_SIZE)
# # Send file name size and file name
#         serverSocket.send(struct.pack("h", sys.getsizeof(file_name)))
#         serverSocket.send(file_name)
# # Wait for server ok then send file size
#         serverSocket.recv(BUFFER_SIZE)
#         serverSocket.send(struct.pack("i", os.path.getsize(file_name)))
#     except:
#         print ("Error sending file details")
#     try:
# # Send the file in chunks defined by BUFFER_SIZE
# # Doing it this way allows for unlimited potential file sizes to be sent
#         l = content.read(BUFFER_SIZE)
#         print ("\nSending...")
#         while l:
#             serverSocket.send(l)
#             l = content.read(BUFFER_SIZE)
#             content.close()
# # Get upload performance details
#             upload_time = struct.unpack("f", serverSocket.recv(4))[0]
#             upload_size = struct.unpack("i", serverSocket.recv(4))[0]
#             print ("\nSent file: {}\nTime elapsed: {}s\nFile size: {}b").format(file_name, upload_time, upload_size)
#     except:
#         print ("Error sending file")


# def list_files():
# # List the files avaliable on the file server
# # Called list_files(), not list() (as in the format of the others) to avoid the standard python function list()
#     print ("Requesting files...\n")
#     try:
# # Send list request
#         serverSocket.send("LIST")
#     except:
#         print ("Couldn't make server request. Make sure a connection has been established.")

#     try:
# # First get the number of files in the directory
#         number_of_files = struct.unpack("i", serverSocket.recv(4))[0]
# # Then enter into a loop to recieve details of each, one by one
#         for i in range(int(number_of_files)):
# # Get the file name size first to slightly lessen amount transferred over socket
#             file_name_size = struct.unpack("i", serverSocket.recv(4))[0]
#             file_name = serverSocket.recv(file_name_size)
# # Also get the file size for each item in the server
#             file_size = struct.unpack("i", serverSocket.recv(4))[0]
#             print ("\t{} - {}b").format(file_name, file_size)
# # Make sure that the client and server are syncronised
#             serverSocket.send("1")
# # Get total size of directory
#             total_directory_size = struct.unpack("i", serverSocket.recv(4))[0]
#             print ("Total directory size: {}b").format(total_directory_size)
#     except:
#         print ("Couldn't retrieve listing")

# # try:
# # # Final check
# #     serverSocket.send("1")

# # except:
# #     print ("Couldn't get final server confirmation")


# def dwld(file_name):
# # Download given file
#     print ("Downloading file: {}").format(file_name)
#     try:
# # Send server request
#         serverSocket.send("DWLD")
#     except:
#         print ("Couldn't make server request. Make sure a connection has bene established.")
#         return
#     try:
# # Wait for server ok, then make sure file exists
#         serverSocket.recv(BUFFER_SIZE)
# # Send file name length, then name
#         serverSocket.send(struct.pack("h", sys.getsizeof(file_name)))
#         serverSocket.send(file_name)
# # Get file size (if exists)
#         file_size = struct.unpack("i", serverSocket.recv(4))[0]
#         if file_size == -1:
# # If file size is -1, the file does not exist
#             print ("File does not exist. Make sure the name was entered correctly")
#             return
#     except:
#         print ("Error checking file")
#     try:
# # Send ok to recieve file content
#         serverSocket.send("1")
# # Enter loop to recieve file
#         output_file = open(file_name, "wb")
#         bytes_recieved = 0
#         print ("\nDownloading...")
#         while bytes_recieved < file_size:
# # Again, file broken into chunks defined by the BUFFER_SIZE variable
#             l = serverSocket.recv(BUFFER_SIZE)
#             output_file.write(l)
#             bytes_recieved += BUFFER_SIZE
#             output_file.close()
#             print ("Successfully downloaded {}").format(file_name)
# # Tell the server that the client is ready to recieve the download performance details
#             serverSocket.send("1")
# # Get performance details
#             time_elapsed = struct.unpack("f", serverSocket.recv(4))[0]
#             print ("Time elapsed: {}s\nFile size: {}b").format(time_elapsed, file_size)
#     except:
#         print ("Error downloading file")
#         return


# def delf(file_name):
    
# # Delete specified file from file server
#     print ("Deleting file: {}...").format(file_name)
#     try:
# # Send resquest, then wait for go-ahead
#         serverSocket.send("DELF")
#         serverSocket.recv(BUFFER_SIZE)
#     except:
#         print ("Couldn't connect to server. Make sure a connection has been established.")
#         return
#     try:
# # Send file name length, then file name
#         serverSocket.send(struct.pack("h", sys.getsizeof(file_name)))
#         serverSocket.send(file_name)
#     except:
#         print ("Couldn't send file details")
#         return
#     try:
# # Get conformation that file does/doesn't exist
#         file_exists = struct.unpack("i", serverSocket.recv(4))[0]
#         if file_exists == -1:
#             print ("The file does not exist on server")
#             return
#     except:
#         print ("Couldn't determine file existance")

#         try:
# # Confirm user wants to delete file
#             confirm_delete = raw_input ("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
# # Make sure input is valid
# # Unfortunately python doesn't have a do while style loop, as that would have been better here
#             while confirm_delete != "Y" and confirm_delete != "N" and confirm_delete != "YES" and confirm_delete != "NO":
# # If user input is invalid
#                 print ("Command not recognised, try again")
#                 confirm_delete = raw_input ("Are you sure you want to delete {}? (Y/N)\n".format(file_name)).upper()
#         except:
#                 print ("Couldn't confirm deletion status")
#                 return
#     try:
# # Send conformation
#         if confirm_delete == "Y" or confirm_delete == "YES":
# # User wants to delete file
#             serverSocket.send("Y")
# # Wait for conformation file has been deleted
#             delete_status = struct.unpack("i", serverSocket.recv(4))[0]
#             if delete_status == 1:
#                 print ("File successfully deleted")
#             else:
# # Client will probably send -1 to get here, but an else is used as more of a catch-all
#                 print ("File failed to delete")
#         else:
#             serverSocket.send("N")
#             print ("Delete abandoned by user!")
#     except:
#         print ("Couldn't delete file")
#         return


# def quit():
#     serverSocket.send("QUIT")
# # Wait for server go-ahead
#     serverSocket.recv(BUFFER_SIZE)
#     serverSocket.close()
#     print ("Server connection ended")
#     return


# print ("\n\nWelcome to the FTP client.\n\nCall one of the following functions:\nCONN : Connect to server\nUPLD file_path : Upload file\nLIST : List files\nDWLD file_path : Download file\nDELF file_path : Delete file\nQUIT : Exit")

# while True:
# # Listen for a command
#     prompt = raw_input ("\nEnter a command: ")
#     if prompt[:4].upper() == "CONN":
#         conn()
#     elif prompt[:4].upper() == "UPLD":
#         upld(prompt[5:])
#     elif prompt[:4].upper() == "LIST":
#         list_files()
#     elif prompt[:4].upper() == "DWLD":
#         dwld(prompt[5:])
#     elif prompt[:4].upper() == "DELF":
#         delf(prompt[5:])
#     elif prompt[:4].upper() == "QUIT":
#         quit()
#         break
#     else:
#         print ("Command not recognised; please try again")

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

            ### INVALID COMMAND ###########################################
            case _:
                # Print error
                print(f"'{tokens[0]}' is not a recognized command\n")
                return
            
    def put(self, filename: str):
        '''
        Uploads file to the ftp server

        Parameters:
            filename (str): name of the file to be uploaded
        '''

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

        # Send upload request
        try:
            # Make upload request
            Client.send(self.c_sock, f'put,{filename}')
        except socket.error:
            print("Couldn't make server request. Make sure a connection has been established.\n")
            return

        try:
            # Recieve server message
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

            # Send encoded message over data connection
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

        # TODO Send a GET request to the server over the control connection, 
        # specifying the name and path of the file to be retrieved.

        # TODO Receive a response message from the server that includes the 
        # IP address and port number to be used for the data connection.

        # TODO Establish a data connection with the server on the IP address 
        # and port specified in the server response message.

        # TODO Receive the file from the server over the data connection.

        # TODO Close the data connection.

        # TODO Return the string

    def ls(self):
        '''Request and prints a list of the files in the ftp working directory'''

        # TODO Send an LS command to the server over the control connection.

        # TODO Receive a response message from the server that includes the 
        # IP address and port number to be used for the data connection.

        # TODO Establish a data connection with the server on the IP address 
        # and port specified in the server response message.

        # TODO Receive the directory listing from the server over the data 
        # connection.

        # TODO Close the data connection.

    def quit(self):
        '''Closes the control connection and terminates the client'''

        # Send a QUIT command to the server over the control connection.
        Client.send(self.c_sock, 'quit')

        # Receive a response message from the server indicating that the 
        # command has been received and the connection will be closed.
        m = Client.receive(self.c_sock, 1024)

        # Close connection if return code is 211
        if m == '211':

            # Close control connection
            self.c_sock.close()

            # Pause terminal until user input, then exit
            print('Press any key to exit . . .')
            os.system('pause>NUL')
            sys.exit()

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

    # try:
        sock.connect((ip, port_number))

    # commented out for debugging
    # except:
        # # Could not connect to server
        # print("Connection unsuccessful. Please make sure the connection is online.\nClosing 'cli.py'...\n")
        # print('Press any key to exit . . .')

        # # Pause terminal until user input, then exit
        # os.system('pause>NUL')
        # sys.exit()

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
    

if __name__ == '__main__':

    # print()
    
    # Ensure there are only 3 command line arguments
    if len(sys.argv) != 3:
        # Print error
        print(f"'cli.py' expects 2 arguments ({len(sys.argv)-1} given)")
        
    else:
        # TODO: parse inputs to ensure they are correct

        # Create Client Socket
        cli_sock = Client(sys.argv[1], int(sys.argv[2]))

        # Start Client Socket
        cli_sock.start()
