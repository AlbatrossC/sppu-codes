import numpy as np

def sig(x):
    return 1 / (1 + np.exp(-x))

def dsig(x):
    return x * (1 - x)

inp = np.array([[0,0],[0,1],[1,0],[1,1]])
out = np.array([[0],[1],[1],[0]])

w1 = np.random.rand(2, 2)
b1 = np.zeros((1, 2))

w2 = np.random.rand(2, 1)
b2 = np.zeros((1, 1))

lr = 0.5

for _ in range(10000):

    h_in = np.dot(inp, w1) + b1
    h_out = sig(h_in)

    o_in = np.dot(h_out, w2) + b2
    o_out = sig(o_in)

    err = out - o_out

    d_out = err * dsig(o_out)

    d_hid = d_out.dot(w2.T) * dsig(h_out)

    w2 = w2 + h_out.T.dot(d_out) * lr
    b2 = b2 + np.sum(d_out, axis=0) * lr

    w1 = w1 + inp.T.dot(d_hid) * lr
    b1 = b1 + np.sum(d_hid, axis=0) * lr

print("Output:")
print(o_out)