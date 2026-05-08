import socket

choice = input("Enter '1' for Domain to IP or '2' for IP to Domain: ")

if choice == '1':
    domain = input("Enter domain name: ")
    ip = socket.gethostbyname(domain)
    print("IP address of", domain, "is:", ip)

elif choice == '2':
    ip = input("Enter IP address: ")
    host = socket.gethostbyaddr(ip)
    print("Domain name of", ip, "is:", host[0])

else:
    print("Invalid choice.")
