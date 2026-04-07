import numpy as np

number = int(input("Enter a Number (0-9): "))

def step_function(x):
    if x >= 0:
        return 1
    else:
        return 0

training_data = [
    {"input": [1, 1, 0, 0, 0, 0], "label": 1},
    {"input": [1, 1, 0, 0, 0, 1], "label": 0},
    {"input": [1, 1, 0, 0, 1, 0], "label": 1},
    {"input": [1, 1, 0, 1, 1, 1], "label": 0},
    {"input": [1, 1, 0, 1, 0, 0], "label": 1},
    {"input": [1, 1, 0, 1, 0, 1], "label": 0},
    {"input": [1, 1, 0, 1, 1, 0], "label": 1},
    {"input": [1, 1, 0, 1, 1, 1], "label": 0},
    {"input": [1, 1, 1, 0, 0, 0], "label": 1},
    {"input": [1, 1, 1, 0, 0, 1], "label": 0},
]

weights = np.array([0, 0, 0, 0, 0, 1])

for sample in training_data:
    inputs = np.array(sample["input"])
    label = sample["label"]

    result = np.dot(inputs, weights)
    output = step_function(result)

    error = label - output
    weights += inputs * error

binary_string = format(number, "06b")
binary_list = list(binary_string)
binary_numbers = [int(x) for x in binary_list]
binary_input = np.array(binary_numbers)

result = np.dot(binary_input, weights)
prediction = step_function(result)

if prediction == 0:
    answer = "odd"
else:
    answer = "even"

print(number, "is", answer)
