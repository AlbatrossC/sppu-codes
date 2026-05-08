def power(base, exp, mod):
    if exp == 1:
        return base
    return pow(base, exp) % mod


P = int(input("Enter the prime number: "))
print("Value of P:", P)

G = int(input("Enter the primitive root for the above prime number: "))
print("Value of G:", G)

a = int(input("Enter the private key for A: "))
print("Private key of A:", a)

x = power(G, a, P)

b = int(input("Enter the private key for B: "))
print("Private key of B:", b)

y = power(G, b, P)

ka = power(y, a, P)
kb = power(x, b, P)

print("Secret key for A:", ka)
print("Secret key for B:", kb)