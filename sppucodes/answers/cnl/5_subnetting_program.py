ip = input("Enter IP address (e.g. 192.168.1.0): ")
subnet_count = int(input("Enter number of required subnets: "))

def ip_to_binary(ip):
    return ''.join(f'{int(octet):08b}' for octet in ip.split('.'))

def binary_to_ip(bin_str):
    return '.'.join(str(int(bin_str[i:i+8], 2)) for i in range(0, 32, 8))

def calculate_subnet_mask(subnet_bits):
    mask = '1' * (24 + subnet_bits) + '0' * (8 - subnet_bits)
    return binary_to_ip(mask)

octets = ip.split('.')
if len(octets) != 4 or not all(o.isdigit() and 0 <= int(o) <= 255 for o in octets):
    print("Invalid IP address format.")

else:
    subnet_bits = 0
    while 2 ** subnet_bits < subnet_count:
        subnet_bits += 1

    if subnet_bits > 8:
        print("Too many subnets requested for a class C network.")

    else:
        subnet_mask = calculate_subnet_mask(subnet_bits)
        print(f"Subnet mask for {subnet_count} subnets is: {subnet_mask}")
        last_octet_mask = int(ip_to_binary(subnet_mask)[24:32], 2)
        block_size = 256 - last_octet_mask
        print("\nSubnet Addresses:")
        base_ip_parts = list(map(int, ip.split('.')))
        for i in range(subnet_count):
            subnet_ip = f"{base_ip_parts[0]}.{base_ip_parts[1]}.{base_ip_parts[2]}.{i * block_size}"
            print(subnet_ip)
            