"""
 UDP File Transfer (Different Computers)

⚠️ NOTE:
This is for Transferring files on Different Computers
If you want to transfer files WITHIN THE SAME COMPUTER,
Check next code for same host.

HOW TO RUN

1. Start the SERVER (receiver) on one computer:
       python receiver.py

2. Start the CLIENT (sender) on another computer:
       python client.py <server_ip> <server_port> <file_path>

   Example:
       python client.py 192.168.1.5 5005 myfile.txt


On Windows:
   - Open Command Prompt and type: ipconfig
   - Look for "IPv4 Address" (e.g., 192.168.x.x)
   - Use port 5005 (default)
"""


"""
============================
 receiver.py  (Server Side)
============================
"""
import socket

def udp_file_receiver(ip='0.0.0.0', port=5005, buffer_size=4096):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    print(f"Listening on {ip}:{port}")

    # Receive filename first
    filename, addr = sock.recvfrom(buffer_size)
    filename = filename.decode()
    print(f"Receiving file: {filename} from {addr}")

    with open(filename, 'wb') as f:
        while True:
            data, addr = sock.recvfrom(buffer_size)
            if data == b'END':
                print("File transfer completed.")
                break
            f.write(data)
    sock.close()

if __name__ == "__main__":
    udp_file_receiver()

"""
============================
 client.py  (Client Side)
============================
"""

import socket
import os
import sys

def udp_file_sender(server_ip, server_port, filepath, buffer_size=4096):
    if not os.path.isfile(filepath):
        print("File does not exist.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    filename = os.path.basename(filepath)
    sock.sendto(filename.encode(), (server_ip, server_port))
    print("Sending file: {}".format(filename))

    with open(filepath, 'rb') as f:
        while True:
            bytes_read = f.read(buffer_size)
            if not bytes_read:
                break
            sock.sendto(bytes_read, (server_ip, server_port))

    sock.sendto(b'END', (server_ip, server_port))
    print("File sent successfully.")
    sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python udp_client.py <server_ip> <server_port> <file_path>")
        sys.exit(1)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    file_path = sys.argv[3]

    udp_file_sender(server_ip, server_port, file_path)
