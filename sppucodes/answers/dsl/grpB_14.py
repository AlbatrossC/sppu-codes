def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_index = i
        j = i + 1
        while j < n:
            if arr[j] < arr[min_index]:
                min_index = j
            j += 1
        temp = arr[i]
        arr[i] = arr[min_index]
        arr[min_index] = temp

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp

def display_top_five(arr):
    top_five = arr[-5:][::-1]
    print("Top five scores are:")
    for score in top_five:
        print(score)

student_percentages = []
num_students = int(input("Enter the number of students: "))

for i in range(num_students):
    percentage = float(input(f"Enter the percentage for student {i + 1}: "))
    student_percentages.append(percentage)

print("Sorting using Selection Sort...")
selection_sort(student_percentages)
display_top_five(student_percentages)

print("\nSorting using Bubble Sort...")
bubble_sort(student_percentages)
display_top_five(student_percentages)
