import numpy as np
import matplotlib.pyplot as plt

# Generate input values
x = np.linspace(-10, 10, 400)

# Activation functions
def linear(x):
    return x

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)

def tanh(x):
    return np.tanh(x)

def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

def softmax(x):
    exp_x = np.exp(x - np.max(x))  # stability trick
    return exp_x / np.sum(exp_x)

# Create subplots (3 rows, 2 columns)
fig, axs = plt.subplots(3, 2, figsize=(10, 10))

axs[0, 0].plot(x, linear(x))
axs[0, 0].set_title("Linear")

axs[0, 1].plot(x, sigmoid(x))
axs[0, 1].set_title("Sigmoid")

axs[1, 0].plot(x, relu(x))
axs[1, 0].set_title("ReLU")

axs[1, 1].plot(x, tanh(x))
axs[1, 1].set_title("Tanh")

axs[2, 0].plot(x, softmax(x))
axs[2, 0].set_title("Softmax")

axs[2, 1].plot(x, leaky_relu(x))
axs[2, 1].set_title("Leaky ReLU")

for ax in axs.flat:
    ax.set_xlabel("Input")
    ax.set_ylabel("Output")
    ax.grid(True)

plt.tight_layout()
plt.show()
