import numpy as np


# Bipolar activation function
def sign(value):
    return 1 if value >= 0 else -1


# Input patterns
input_patterns = np.array([
    [1, -1, 1],
    [-1, 1, -1]
])

# Output patterns
output_patterns = np.array([
    [1, 1],
    [-1, -1]
])

# Initialize weights
weights = np.zeros((3, 2))

# Training
for i in range(len(input_patterns)):
    weights += np.outer(input_patterns[i], output_patterns[i])

print("Weight Matrix:")
print(weights)

# Forward propagation
print("\nForward Propagation:")

for pattern in input_patterns:
    result = np.dot(pattern, weights)
    prediction = [sign(v) for v in result]

    print(f"{pattern} -> {prediction}")

# Backward propagation
print("\nBackward Propagation:")

for pattern in output_patterns:
    result = np.dot(pattern, weights.T)
    prediction = [sign(v) for v in result]

    print(f"{pattern} -> {prediction}")

    