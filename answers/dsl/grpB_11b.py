def binary_search(roll_numbers, target):
    left, right = 0, len(roll_numbers) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if roll_numbers[mid] == target:
            print(f"Roll number {target} attended the training program.")
            return
        elif roll_numbers[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    print(f"Roll number {target} did not attend the training program.")

def fibonacci_search(roll_numbers, target):
    fib_m2 = 0
    fib_m1 = 1
    fib_m = fib_m1 + fib_m2
    while fib_m < len(roll_numbers):
        fib_m2 = fib_m1
        fib_m1 = fib_m
        fib_m = fib_m1 + fib_m2
        
    offset = -1
    while fib_m > 1:
        i = min(offset + fib_m2, len(roll_numbers) - 1)
        if roll_numbers[i] < target:
            fib_m = fib_m1
            fib_m1 = fib_m2
            fib_m2 = fib_m - fib_m2
            offset = i
        elif roll_numbers[i] > target:
            fib_m = fib_m2
            fib_m1 -= fib_m2
            fib_m2 = fib_m1 - fib_m2
        else:
            print(f"Roll number {target} attended the training program.")
            return
            
    if fib_m1 and offset + 1 < len(roll_numbers) and roll_numbers[offset + 1] == target:
        print(f"Roll number {target} attended the training program.")
    else:
        print(f"Roll number {target} did not attend the training program.")

roll_numbers = []
num_students = int(input("Enter the number of students who attended the training program: "))
for _ in range(num_students):
    roll = int(input("Enter roll number: "))
    roll_numbers.append(roll)

roll_numbers.sort()
target_roll = int(input("Enter the roll number to search: "))
binary_search(roll_numbers, target_roll)
fibonacci_search(roll_numbers, target_roll)
