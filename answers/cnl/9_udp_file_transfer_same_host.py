"""

 UDP File Transfer (Same Host)

⚠️ NOTE:
This script transfers files between processes 
on the SAME MACHINE (localhost, 127.0.0.1).

HOW TO RUN

1. Open one terminal → run as RECEIVER:
    On Windows:
        - Open Command Prompt and type: ipconfig
        - Look for "IPv4 Address" (e.g., 192.168.x.x)
        - Paste the server_ip in the cilent.py
    In terminanl: python receiver.py



2. Open another terminal → run as SENDER:
    Get the server_ip after typing ipconfig in terminal. Look for "IPv4"
        python cilent.py

"""

"""
============================
 receiver.py  (Server Side)
============================
"""
import socket
import os

def udp_file_receiver(bind_ip="0.0.0.0", bind_port=5001, buffer_size=4096, save_dir="received_files"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((bind_ip, bind_port))
    print(f"[+] UDP Server listening on {bind_ip}:{bind_port}")

    os.makedirs(save_dir, exist_ok=True)

    while True:
        data, addr = sock.recvfrom(buffer_size)
        filename = data.decode()
        print(f"Receiving file: {filename} from {addr}")

        filepath = os.path.join(save_dir, filename)
        with open(filepath, "wb") as f:
            while True:
                data, addr = sock.recvfrom(buffer_size)
                if data == b"EOF":
                    break
                f.write(data)

        print(f"File saved: {filepath}\n")

if __name__ == "__main__":
    udp_file_receiver()


"""
============================
 client.py  (Client Side)
============================
"""

import socket
import os

server_ip = "192.168.56.1"   # Change to server machine IP
server_port = 5001           # Change if needed
filepath = "ocr.py"          # File to send (script/text/audio/video)

#Send a file to a server over UDP sockets.
def udp_file_sender(server_ip, server_port, filepath, buffer_size=4096):
    if not os.path.isfile(filepath):
        print(f"[-] File '{filepath}' does not exist.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    filename = os.path.basename(filepath)
    sock.sendto(filename.encode(), (server_ip, server_port))

    # Send file data
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(buffer_size)
            if not chunk:
                break
            sock.sendto(chunk, (server_ip, server_port))

    # Indicate EOF
    sock.sendto(b"EOF", (server_ip, server_port))
    print(f"File '{filename}' sent successfully to {server_ip}:{server_port}")


if __name__ == "__main__":
    udp_file_sender(server_ip, server_port, filepath)
