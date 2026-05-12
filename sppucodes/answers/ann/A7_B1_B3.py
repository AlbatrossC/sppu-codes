# Forward and Back Propagation

import numpy as np

# Input and Output
X = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

Y = np.array([
    [0],
    [1],
    [1],
    [0]
])

# Weights
w1 = np.random.rand(2, 2)
w2 = np.random.rand(2, 1)

# Sigmoid Function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Derivative
def derivative(x):
    return x * (1 - x)

# Training
for i in range(5000):

    # Forward Propagation
    h_input = np.dot(X, w1)
    h_output = sigmoid(h_input)

    o_input = np.dot(h_output, w2)
    output = sigmoid(o_input)

    # Error
    error = Y - output

    # Back Propagation
    d_output = error * derivative(output)

    d_hidden = d_output.dot(w2.T) * derivative(h_output)

    # Update Weights
    w2 += h_output.T.dot(d_output)
    w1 += X.T.dot(d_hidden)

# Final Output
print("Output:")
print(np.round(output))