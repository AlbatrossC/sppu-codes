import numpy as np

def sign(x):
    return 1 if x >= 0 else -1

p = np.array([
    [1, -1, 1, -1],
    [-1, 1, -1, 1],
    [1, 1, -1, -1],
    [-1, -1, 1, 1]
])

n = p.shape[1]
w = np.zeros((n, n))

for i in range(len(p)):
    w = w + np.outer(p[i], p[i])

np.fill_diagonal(w, 0)

test = np.array([1, -1, 1, -1])

for _ in range(5):
    for i in range(n):
        val = np.dot(w[i], test)
        test[i] = sign(val)

print("Output:", test)
