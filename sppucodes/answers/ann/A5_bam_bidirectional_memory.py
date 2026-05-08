import numpy as np

def sign(v):
    if v >= 0:
        return 1
    else:
        return -1

input = np.array([[1, -1, 1], [-1, 1, -1]])
output = np.array([[1, 1], [-1, -1]])

weight = np.zeros((3, 2))

for i in range(len(input)):
    weight = weight + np.outer(input[i], output[i])

print("W:\n", weight)

print("\nFwd:")
for i in range(len(input)):
    res = np.dot(input[i], weight)
    pred = [sign(v) for v in res]
    print(input[i], "->", pred)

print("\nBwd:")
for i in range(len(output)):
    res = np.dot(output[i], weight.T)
    pred = [sign(v) for v in res]
    print(output[i], "->", pred)
