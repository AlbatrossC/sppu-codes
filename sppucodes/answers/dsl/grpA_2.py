def marks():
    n = int(input("Enter Total no of Students: "))
    global marks
    global absent_count
    absent_count = 0
    marks = []
    for i in range(n):
        mark = input(f"Enter the marks of Student {i+1} (A if Absent): ")
        if mark.upper() == "A":
            absent_count += 1
        else:
            marks.append(int(mark))
    print("Marks of Students: ", marks)

def average():
    total = len(marks)
    total_sum = sum(marks)
    print("Average Score of the class: ", total_sum / total)

def highest_lowest():
    maximum = max(marks)
    minimum = min(marks)
    print("The Highest Score: ", maximum)
    print("The Lowest Score: ", minimum)

def count_absent():
    print("Number of students absent for the test: ", absent_count)

def highest_frequency_mark():
    frequency = {}
    for mark in marks:
        if mark in frequency:
            frequency[mark] += 1
        else:
            frequency[mark] = 1
    max_freq = max(frequency.values())
    most_frequent = [mark for mark, freq in frequency.items() if freq == max_freq]
    print("Mark(s) with the highest frequency: ", most_frequent)
    print("Frequency: ", max_freq)

# Function calls
marks()
average()
highest_lowest()
count_absent()
highest_frequency_mark()
