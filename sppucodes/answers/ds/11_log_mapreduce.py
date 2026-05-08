# MapReduce simulation in one file (log processing)

def main():
    # Sample log data (inside code)
    logs = [
        '192.168.1.1 - - [21/Apr/2026] "GET /home" 200',
        '192.168.1.2 - - [21/Apr/2026] "GET /about" 404',
        '192.168.1.1 - - [21/Apr/2026] "POST /login" 200',
        '192.168.1.3 - - [21/Apr/2026] "GET /home" 500',
        '192.168.1.1 - - [21/Apr/2026] "GET /home" 200'
    ]

    # Map phase
    mapped = []
    for line in logs:
        ip = line.split()[0]
        mapped.append((ip, 1))

    # Reduce phase
    result = {}
    for ip, value in mapped:
        result[ip] = result.get(ip, 0) + value

    # Output
    print("IP Count")
    for ip in result:
        print(ip, result[ip])


if __name__ == "__main__":
    main()