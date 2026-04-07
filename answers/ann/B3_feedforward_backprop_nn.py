import numpy as np

def sig(x):
    return 1 / (1 + np.exp(-x))

def dsig(x):
    return x * (1 - x)

inp = np.array([[0,0],[0,1],[1,0],[1,1]])
out = np.array([[0],[1],[1],[0]])

w1 = np.random.rand(2, 3)
w2 = np.random.rand(3, 1)

lr = 0.5

for _ in range(10000):

    h = sig(np.dot(inp, w1))
    o = sig(np.dot(h, w2))

    err = out - o

    d2 = err * dsig(o)
    d1 = d2.dot(w2.T) * dsig(h)

    w2 = w2 + h.T.dot(d2) * lr
    w1 = w1 + inp.T.dot(d1) * lr

print("Output:")
print(o)
