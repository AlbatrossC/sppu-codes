def counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1

    for i in range(n):
        arr[i] = output[i]

def radix_sort(arr):
    max_num = max(arr)
    exp = 1
    while max_num // exp > 0:
        counting_sort(arr, exp)
        exp *= 10

def display_top_five(arr):
    top_five = arr[-5:][::-1]
    print("Top five scores are:")
    for score in top_five:
        print(score)

student_percentages = []
num_students = 10

print("Enter the percentage for 10 students:")
for i in range(num_students):
    percentage = float(input(f"Enter the percentage for student {i + 1}: "))
    student_percentages.append(percentage)

radix_sort(student_percentages)
display_top_five(student_percentages)
