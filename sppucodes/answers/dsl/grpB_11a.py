def linear_search(roll_numbers, target):
    for roll in roll_numbers:
        if roll == target:
            print(f"Linear Search: Roll number {target} attended the training program.")
            return
    print(f"Linear Search: Roll number {target} did not attend the training program.")

def sentinel_search(roll_numbers, target):
    n = len(roll_numbers)
    last = roll_numbers[-1]
    roll_numbers[-1] = target
    i = 0
    while roll_numbers[i] != target:
        i += 1
    roll_numbers[-1] = last
    if i < n - 1 or roll_numbers[-1] == target:
        print(f"Sentinel Search: Roll number {target} attended the training program.")
    else:
        print(f"Sentinel Search: Roll number {target} did not attend the training program.")

roll_numbers = []
num_students = int(input("Enter the number of students who attended the training program: "))
for _ in range(num_students):
    roll = int(input("Enter roll number: "))
    roll_numbers.append(roll)

target_roll = int(input("Enter the roll number to search: "))
linear_search(roll_numbers, target_roll)
sentinel_search(roll_numbers, target_roll)