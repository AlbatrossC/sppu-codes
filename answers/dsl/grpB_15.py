def insertion_sort(arr):
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def shell_sort(arr):
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            key = arr[i]
            j = i
            while j >= gap and arr[j - gap] > key:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = key
        gap //= 2

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

print("Sorting using Insertion Sort...")
insertion_sort(student_percentages)
display_top_five(student_percentages)

print("\nSorting using Shell Sort...")
shell_sort(student_percentages)
display_top_five(student_percentages)
