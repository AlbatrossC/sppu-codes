import numpy as np

n = int(input("Enter a number: "))

binary = format(n, "08b")
print(binary)

inputs = []

for x in binary:
    inputs.append(int(x))

inputs = np.array(inputs)

weights = np.array([0, 0, 0, 0, 0, 0, 0, -1])

result = np.dot(inputs, weights)

if result == 0:
    print("Even")
else:
    print("Odd")