# Programming Assignment 1
CPSC471-02: Computer Communications

DUE: 6 May 2023 

## Group Members

- **Dilhan Franco** - dilhanfranco@csu.fullerton.edu
- **Omar Trejo** - trejo.omar562@csu.fullerton.edu
- **Jared Sevilla** - jgsevilla@csu.fullerton.edu
- **Anthony Tran**  - Tranthony_777@csu.fullerton.edu
- **Niccolo Chuidian** - niccolochuidian@csu.fullerton.edu
  
## Project Overview
In this assignment, you will implement (simplified) FTP server and FTP client. The client shall
connect to the server and support uploading and downloading of files to/from server

## Programming Language
Python 3.11.0

# How to Execute
Our client and server files are in two different folders with their respective names. Therefore, open two different terminals and cd into the Server and Client directories.

## How to start the Server
In the server, we specify the port number of the server's control connection:
```
python3 server.py 21
```

## How to start the Client
In the client, we specify the localhost server and the port we are connecting to:
```
python3 cli.py 127.0.0.1 21
```
## Running Client Commands
Once the Client and Server are successfully connected, you may run the following commands:

To list working directory contents:
```
ftp>ls
```

To download a file from the Server onto the Client:
```
ftp>get <filename>
```

To upload a file from the Client onto the Server:
```
ftp>put <filename>
```

To end the session:
```
ftp>quit
```

To display help information:
```
ftp> help
```

## Protocol

![Process Map](https://user-images.githubusercontent.com/54593489/236600347-1dc0d3d1-d4ff-4193-93ce-8ec8fb2c378e.jpeg)
```
