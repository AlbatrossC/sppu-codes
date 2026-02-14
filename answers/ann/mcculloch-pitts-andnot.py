import numpy as np


def mp_neuron(inputs, weights, threshold):
    # Calculate weighted sum
    weighted_sum = np.dot(inputs, weights)

    # Apply step activation function
    if weighted_sum >= threshold:
        output = 1
    else:
        output = 0

    return output


def and_not(x1, x2):
    # Define weights for AND-NOT
    weights = np.array([1, -1])

    # Define threshold
    threshold = 1

    # Create input array
    inputs = np.array([x1, x2])

    # Get neuron output
    output = mp_neuron(inputs, weights, threshold)

    return output


# Test cases
print("A=0 B=0 ->", and_not(0, 0))
print("A=1 B=0 ->", and_not(1, 0))
print("A=0 B=1 ->", and_not(0, 1))
print("A=1 B=1 ->", and_not(1, 1))
