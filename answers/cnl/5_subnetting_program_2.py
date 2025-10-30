# # EASY VERSION !!

ip = input("Enter IP address: ")
n = int(input("Enter number of subnets: "))

p = list(map(int, ip.split('.')))
print(p)

if len(p)!=4 or any(x<0 or x>255 for x in p):
    print("Invalid IP")
else:
    b=0
    while 2**b<n:
        b += 1
    
    if b>8:
        print("Too many Subnets")
    else:
        mask = 256 - 2**(8-b)
        print("Subnet mask:" + "255.255.255." + str(mask))
        print("Subnet Address:")
        for i in range(n):
            subnet_ip = str(p[0]) + "." + str(p[1]) + "." + str(p[2]) + "." + str(i*(256-mask))
            print(subnet_ip)
